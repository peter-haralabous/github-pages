import logging
from datetime import date
from uuid import UUID

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import QuerySet
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST
from guardian.shortcuts import get_objects_for_user

from sandwich.core.models import Form
from sandwich.core.models import ListViewType
from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import Task
from sandwich.core.models.task import TaskStatus
from sandwich.core.service.custom_attribute_query import annotate_custom_attributes
from sandwich.core.service.custom_attribute_query import apply_filters_with_custom_attributes
from sandwich.core.service.custom_attribute_query import apply_sort_with_custom_attributes
from sandwich.core.service.encounter_service import complete_encounter
from sandwich.core.service.encounter_service import get_current_encounter
from sandwich.core.service.invitation_service import get_unaccepted_invitation
from sandwich.core.service.invitation_service import resend_patient_invitation_email
from sandwich.core.service.list_preference_service import enrich_filters_with_display_values
from sandwich.core.service.list_preference_service import get_available_columns
from sandwich.core.service.list_preference_service import get_list_view_preference
from sandwich.core.service.list_preference_service import has_unsaved_filters
from sandwich.core.service.list_preference_service import parse_filters_from_query_params
from sandwich.core.service.patient_service import assign_default_patient_permissions
from sandwich.core.service.patient_service import maybe_patient_name
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.service.task_service import cancel_task
from sandwich.core.service.task_service import send_task_added_email
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.util.http import validate_sort
from sandwich.core.validators.date_of_birth import valid_date_of_birth
from sandwich.providers.forms.task import AddTaskForm
from sandwich.providers.views.encounter import EncounterCreateForm
from sandwich.providers.views.encounter import _format_attributes
from sandwich.providers.views.list_view_state import maybe_redirect_with_saved_filters

logger = logging.getLogger(__name__)


class PatientEdit(forms.ModelForm[Patient]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("first_name", "last_name", css_class="flex gap-4"),
            "date_of_birth",
            "province",
            "phn",
            "email",
            Submit("submit", "Submit"),
        )

    def clean_date_of_birth(self) -> date:
        dob = self.cleaned_data["date_of_birth"]
        return valid_date_of_birth(dob)

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "date_of_birth", "province", "phn", "email")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "max": "9999-12-31"}),
        }


class PatientAdd(forms.ModelForm[Patient]):
    # TODO: add check for duplicate patient
    #       "you already have a patient with this email address/PHN/name"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("first_name", "last_name", css_class="flex gap-4"),
            "date_of_birth",
            "province",
            "phn",
            "email",
            Submit("submit", "Submit"),
        )

    def clean_date_of_birth(self) -> date:
        dob = self.cleaned_data["date_of_birth"]
        return valid_date_of_birth(dob)

    def save(self, commit: bool = True, organization: Organization | None = None) -> Patient:  # noqa: FBT001,FBT002
        instance = super().save(commit=False)
        if organization is not None:
            instance.organization = organization
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "date_of_birth", "province", "phn", "email")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "max": "9999-12-31"}),
        }


@login_required
@authorize_objects(
    [ObjPerm(Patient, "patient_id", ["view_patient"]), ObjPerm(Organization, "organization_id", ["view_organization"])]
)
def patient_details(request: AuthenticatedHttpRequest, organization: Organization, patient: Patient) -> HttpResponse:
    logger.info(
        "Accessing provider patient details",
        extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
    )

    # Check if a specific encounter should be displayed (from slideout "View Patient")
    encounter_id = request.GET.get("encounter_id")
    current_encounter: Encounter | None
    if encounter_id:
        try:
            current_encounter = patient.encounter_set.get(id=UUID(encounter_id))
        except (ValueError, Encounter.DoesNotExist):
            current_encounter = get_current_encounter(patient)
    else:
        current_encounter = get_current_encounter(patient)

    tasks = current_encounter.task_set.all() if current_encounter else []
    past_encounters = patient.encounter_set.exclude(status=EncounterStatus.IN_PROGRESS)
    all_encounters = patient.encounter_set.all().order_by("-created_at")
    pending_invitation = get_unaccepted_invitation(patient)

    logger.debug(
        "Patient details loaded",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "patient_id": patient.id,
            "has_current_encounter": bool(current_encounter),
            "task_count": len(list(tasks)),
            "past_encounter_count": past_encounters.count(),
            "has_pending_invitation": bool(pending_invitation),
        },
    )

    # Check if this is a search result (no from_encounter in query params)
    # If from encounter list, show current encounter; if from search, show overview
    from_encounter_list = request.GET.get("from_encounter_list") == "true"

    context = {
        "patient": patient,
        "organization": organization,
        "current_encounter": current_encounter,
        "past_encounters": past_encounters,
        "encounters": all_encounters,
        "tasks": tasks,
        "pending_invitation": pending_invitation,
        "show_current_encounter": (from_encounter_list or encounter_id) and current_encounter,
    }
    return render(request, "provider/patient_details_new.html", context)


@login_required
@authorize_objects(
    [
        ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"]),
        ObjPerm(Organization, "organization_id", ["view_organization"]),
    ]
)
def patient_edit(request: AuthenticatedHttpRequest, organization: Organization, patient: Patient) -> HttpResponse:
    logger.info(
        "Accessing provider patient edit",
        extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
    )

    if request.method == "POST":
        logger.info(
            "Processing provider patient edit form",
            extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
        )
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            logger.info(
                "Provider patient updated successfully",
                extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
            )
            messages.add_message(request, messages.SUCCESS, "Patient updated successfully.")
            return HttpResponseRedirect(
                reverse(
                    "providers:patient",
                    kwargs={"patient_id": patient.id, "organization_id": organization.id},
                )
            )
        logger.warning(
            "Invalid provider patient edit form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "patient_id": patient.id,
                "form_errors": list(form.errors.keys()),
            },
        )
    else:
        logger.debug(
            "Rendering provider patient edit form",
            extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
        )
        form = PatientEdit(instance=patient)

    context = {"form": form, "organization": organization}
    return render(request, "provider/patient_edit.html", context)


@login_required
@authorize_objects(
    [ObjPerm(Organization, "organization_id", ["view_organization", "create_encounter", "create_patient"])]
)
def patient_add(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    logger.info(
        "Accessing provider patient add", extra={"user_id": request.user.id, "organization_id": organization.id}
    )

    if request.method == "POST":
        logger.info(
            "Processing provider patient add form",
            extra={"user_id": request.user.id, "organization_id": organization.id},
        )
        form = PatientAdd(request.POST)
        if form.is_valid():
            patient = form.save(organization=organization)
            # Form `save()` does not call `Object.create` so we manually apply
            # permissions.
            assign_default_patient_permissions(patient)
            # Check if this patient was created via the encounter flow (by checking for a GET param or session flag)
            if request.GET.get("from_encounter"):
                # Redirect to encounter create page with patient preselected
                return HttpResponseRedirect(
                    reverse("providers:encounter_create", kwargs={"organization_id": organization.id})
                    + f"?patient_id={patient.id}"
                )
            # Default: create encounter and redirect to patient details
            encounter = Encounter.objects.create(
                patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS
            )
            logger.info(
                "Provider patient and encounter created successfully",
                extra={
                    "user_id": request.user.id,
                    "organization_id": organization.id,
                    "patient_id": patient.id,
                    "encounter_id": encounter.id,
                },
            )
            messages.add_message(request, messages.SUCCESS, "Patient added successfully.")
            return HttpResponseRedirect(
                reverse("providers:patient", kwargs={"patient_id": patient.id, "organization_id": organization.id})
            )
        logger.warning(
            "Invalid provider patient add form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "form_errors": list(form.errors.keys()),
            },
        )
    else:
        maybe_name = maybe_patient_name(request.GET.get("maybe_name", ""))
        if maybe_name:
            logger.debug(
                "Pre-filling patient form with parsed name",
                extra={"user_id": request.user.id, "organization_id": organization.id, "has_parsed_name": True},
            )
            form = PatientAdd()
            form.fields["first_name"].initial = maybe_name[0]
            form.fields["last_name"].initial = maybe_name[1]
        else:
            logger.debug(
                "Rendering empty provider patient add form",
                extra={"user_id": request.user.id, "organization_id": organization.id},
            )
            form = PatientAdd()

    context = {"form": form, "organization": organization}
    return render(request, "provider/patient_add.html", context)


@login_required
@authorize_objects(
    [ObjPerm(Organization, "organization_id", ["view_organization", "create_encounter", "create_patient"])]
)
def patient_add_modal(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    """HTMX endpoint for creating a patient during encounter creation.

    GET: Returns a modal dialog with patient creation form (pre-filled with maybe_name if provided).
    POST: Creates patient and returns the encounter_create_select_patient modal with new patient selected.
    """
    if request.method == "POST":
        logger.info(
            "Processing patient add modal form",
            extra={"user_id": request.user.id, "organization_id": organization.id},
        )
        form = PatientAdd(request.POST)
        if form.is_valid():
            patient = form.save(organization=organization)
            assign_default_patient_permissions(patient)
            logger.info(
                "Patient created from modal successfully",
                extra={
                    "user_id": request.user.id,
                    "organization_id": organization.id,
                    "patient_id": patient.id,
                },
            )
            # Return the encounter creation modal with the new patient selected
            encounter_form = EncounterCreateForm(organization, initial={"patient": patient})
            encounter_form.helper.form_action = reverse(
                "providers:encounter_create",
                kwargs={"organization_id": organization.id},
            )
            context = {
                "organization": organization,
                "patient": patient,
                "form": encounter_form,
            }
            return render(request, "provider/partials/encounter_create_modal.html", context)

        logger.warning(
            "Invalid patient add modal form",
            extra={
                "user_id": request.user.id,
                "organization_id": organization.id,
                "form_errors": list(form.errors.keys()),
            },
        )
        # Re-render the modal with errors
        form.helper.form_tag = False
        context = {"form": form, "organization": organization}
        return render(request, "provider/partials/patient_add_modal.html", context)

    # GET request - show the modal with form
    maybe_name = maybe_patient_name(request.GET.get("maybe_name", ""))
    if maybe_name:
        logger.debug(
            "Pre-filling patient modal form with parsed name",
            extra={"user_id": request.user.id, "organization_id": organization.id, "has_parsed_name": True},
        )
        form = PatientAdd()
        form.fields["first_name"].initial = maybe_name[0]
        form.fields["last_name"].initial = maybe_name[1]
    else:
        logger.debug(
            "Rendering empty patient modal form",
            extra={"user_id": request.user.id, "organization_id": organization.id},
        )
        form = PatientAdd()

    # Add autofocus to date of birth field
    form.fields["date_of_birth"].widget.attrs["autofocus"] = True

    # Tell crispy forms not to render the form tag (we do it manually in template with HTMX attrs)
    form.helper.form_tag = False

    context = {"form": form, "organization": organization}
    return render(request, "provider/partials/patient_add_modal.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["view_organization"])])
def patient_list(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    logger.info("Accessing patient list", extra={"user_id": request.user.id, "organization_id": organization.id})

    preference = get_list_view_preference(
        request.user,
        organization,
        ListViewType.PATIENT_LIST,
    )

    redirect_response = maybe_redirect_with_saved_filters(request, preference.saved_filters)
    if redirect_response:
        return redirect_response

    filters = parse_filters_from_query_params(request.GET)

    available_columns = get_available_columns(ListViewType.PATIENT_LIST, organization)
    valid_sort_fields = [col["value"] for col in available_columns]

    search = request.GET.get("search", "").strip()
    sort = (
        validate_sort(
            request.GET.get("sort"),
            valid_sort_fields,
        )
        or preference.default_sort
    )
    page = request.GET.get("page", 1)
    has_active_encounter_filter = request.GET.get("has_active_encounter", "").lower()

    logger.debug(
        "Patient list filters applied",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "search_length": len(search),
            "sort": sort,
            "page": page,
            "has_active_encounter_filter": has_active_encounter_filter,
        },
    )

    provider_patients: QuerySet = get_objects_for_user(request.user, "core.view_patient")
    patients = provider_patients.filter(organization=organization)

    provider_encounters: QuerySet = get_objects_for_user(request.user, "core.view_encounter")
    patients = patients.annotate(
        has_active_encounter=Exists(
            provider_encounters.filter(patient=OuterRef("pk"), status=EncounterStatus.IN_PROGRESS)
        )
    )

    if has_active_encounter_filter in ("true", "false"):
        patients = patients.filter(has_active_encounter=(has_active_encounter_filter == "true"))

    if search:
        patients = patients.search(search)

    content_type = ContentType.objects.get_for_model(Patient)
    patients = annotate_custom_attributes(
        patients,
        preference.visible_columns,
        organization,
        content_type,
    )

    patients = apply_filters_with_custom_attributes(
        patients,
        filters,
        organization,
        content_type,
    )

    if sort:
        patients = apply_sort_with_custom_attributes(
            patients,
            sort,
            organization,
            content_type,
        )

    paginator = Paginator(patients, preference.items_per_page)
    patients_page = paginator.get_page(page)

    available_index = {c["value"]: c for c in available_columns}
    visible_column_meta = [available_index[v] for v in preference.visible_columns if v in available_index]

    logger.debug(
        "Patient list results",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "total_count": paginator.count,
            "page_count": len(patients_page),
            "is_htmx": bool(request.headers.get("HX-Request")),
            "has_saved_preference": preference.pk is not None,
        },
    )

    enriched_filters = enrich_filters_with_display_values(filters, organization, ListViewType.PATIENT_LIST)

    context = {
        "patients": patients_page,
        "organization": organization,
        "search": search,
        "sort": sort,
        "page": page,
        "has_active_encounter_filter": has_active_encounter_filter,
        "visible_columns": preference.visible_columns,
        "visible_column_meta": visible_column_meta,
        "preference": preference,
        "active_filters": enriched_filters,
        "available_columns": available_columns,
        "has_unsaved_filters": has_unsaved_filters(request, preference),
    }
    if request.headers.get("HX-Request"):
        return render(request, "provider/partials/patient_list_table.html", context)
    return render(request, "provider/patient_list.html", context)


@login_required
@require_POST
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(Patient, "patient_id", ["view_patient"]),
    ]
)
def patient_archive(request: AuthenticatedHttpRequest, organization: Organization, patient: Patient) -> HttpResponse:
    logger.info(
        "Archiving patient",
        extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
    )

    current_encounter = get_current_encounter(patient)
    if not current_encounter or not request.user.has_perm("change_encounter", current_encounter):
        return HttpResponseNotFound()

    # in the future we might want to capture _why_ the patient was archived
    # i.e. should status be COMPLETED / CANCELLED / ...
    assert current_encounter is not None, "No current encounter found for patient"
    complete_encounter(current_encounter, request.user)

    logger.info(
        "Patient archived successfully",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "patient_id": patient.id,
            "encounter_id": current_encounter.id,
        },
    )

    messages.add_message(request, messages.SUCCESS, "Patient archived successfully.")
    return HttpResponseRedirect(reverse("providers:patient_list", kwargs={"organization_id": organization.id}))


@login_required
@require_http_methods(["GET", "POST"])
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization", "create_encounter", "create_invitation"]),
        ObjPerm(Patient, "patient_id", ["view_patient", "create_task"]),
    ]
)
def patient_add_task(request: AuthenticatedHttpRequest, organization: Organization, patient: Patient) -> HttpResponse:
    form_action = reverse(
        "providers:patient_add_task", kwargs={"organization_id": organization.id, "patient_id": patient.id}
    )
    forms = [
        {"id": str(form["id"]), "name": form["name"]}
        for form in get_objects_for_user(request.user, "view_form", Form)
        .filter(organization=organization)
        .values("id", "name")
    ]

    if request.headers.get("HX-Request") and request.method == "GET":
        add_task_form = AddTaskForm(available_forms=forms, form_action=form_action)
        context = {"form": add_task_form}
        return render(request, "provider/partials/add_task_modal.html", context)

    if request.method == "POST":
        logger.debug(
            "Form submission handling",
            extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
        )
        add_task_form = AddTaskForm(request.POST, available_forms=forms, form_action=form_action)
        if add_task_form.is_valid():
            form_id = add_task_form.cleaned_data["selected_form"]
            form = Form.objects.get(id=form_id)
            form_version = form.get_current_version() if form is not None else None

            logger.debug("form retrieved", extra={"form_version": form_version})
            # TODO: Can we move it into authorize_objects?
            # super awkward to be dealing with this in form handling
            current_encounter = get_current_encounter(patient)
            if current_encounter and not request.user.has_perm("view_encounter", current_encounter):
                return HttpResponseNotFound()
            logger.debug("current encounter retrieved", extra={"encounter": current_encounter})

            if not current_encounter:
                current_encounter = Encounter.objects.create(
                    patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS
                )
                logger.debug(
                    "Created new encounter for task",
                    extra={
                        "user_id": request.user.id,
                        "organization_id": organization.id,
                        "patient_id": patient.id,
                        "encounter_id": current_encounter.id,
                    },
                )

            logger.info(
                "Adding task to patient",
                extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
            )
            task = Task.objects.create(
                encounter=current_encounter,
                patient=patient,
                status=TaskStatus.REQUESTED,
                form_version=form_version,
            )
            send_task_added_email(task)

            logger.info(
                "Task added successfully",
                extra={
                    "user_id": request.user.id,
                    "organization_id": organization.id,
                    "patient_id": patient.id,
                    "task_id": task.id,
                    "encounter_id": current_encounter.id,
                },
            )

            messages.add_message(request, messages.SUCCESS, "Task added successfully.")
            # Always redirect to patient details page with encounter displayed
            return HttpResponseRedirect(
                reverse(
                    "providers:patient",
                    kwargs={"organization_id": organization.id, "patient_id": patient.id},
                )
                + f"?encounter_id={current_encounter.id}"
            )

    add_task_form = AddTaskForm(request.POST, available_forms=forms, form_action=form_action)
    context = {"form": add_task_form}
    return render(request, "provider/partials/add_task_modal.html", context)


@login_required
@require_POST
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(Patient, "patient_id", ["view_patient"]),
        ObjPerm(Task, "task_id", ["view_task", "change_task"]),
    ]
)
def patient_cancel_task(
    request: AuthenticatedHttpRequest,
    organization: Organization,
    patient: Patient,
    task: Task,
) -> HttpResponse:
    logger.info(
        "Cancelling patient task",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "patient_id": patient.id,
            "task_id": task.id,
        },
    )

    cancel_task(task)

    logger.info(
        "Task cancelled successfully",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "patient_id": patient.id,
            "task_id": task.id,
        },
    )

    messages.add_message(request, messages.SUCCESS, "Task cancelled successfully.")
    return HttpResponseRedirect(
        reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )


@login_required
@require_POST
@authorize_objects(
    [
        ObjPerm(Organization, "organization_id", ["view_organization", "create_invitation"]),
        ObjPerm(Patient, "patient_id", ["view_patient"]),
    ]
)
def patient_resend_invite(
    request: AuthenticatedHttpRequest, organization: Organization, patient: Patient
) -> HttpResponse:
    logger.info(
        "Resending patient invitation",
        extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
    )

    assert patient.user is None, "Patient already has a user"
    resend_patient_invitation_email(patient)

    logger.info(
        "Patient invitation resent successfully",
        extra={"user_id": request.user.id, "organization_id": organization.id, "patient_id": patient.id},
    )

    messages.add_message(request, messages.SUCCESS, "Invitation resent successfully.")
    return HttpResponseRedirect(
        reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})
    )


@login_required
@authorize_objects(
    [ObjPerm(Patient, "patient_id", ["view_patient"]), ObjPerm(Organization, "organization_id", ["view_organization"])]
)
def patient_overview(request: AuthenticatedHttpRequest, organization: Organization, patient: Patient) -> HttpResponse:
    """HTMX endpoint to load the patient overview content (content only)."""
    all_encounters = patient.encounter_set.all().order_by("-created_at")
    pending_invitation = get_unaccepted_invitation(patient)

    context = {
        "patient": patient,
        "organization": organization,
        "encounters": all_encounters,
        "pending_invitation": pending_invitation,
    }
    return render(request, "provider/partials/patient_overview.html", context)


@login_required
@authorize_objects(
    [ObjPerm(Patient, "patient_id", ["view_patient"]), ObjPerm(Organization, "organization_id", ["view_organization"])]
)
def patient_nav_overview(
    request: AuthenticatedHttpRequest, organization: Organization, patient: Patient
) -> HttpResponse:
    """HTMX endpoint to navigate to overview - returns sidebar + content."""
    all_encounters = patient.encounter_set.all().order_by("-created_at")
    pending_invitation = get_unaccepted_invitation(patient)

    # Return both sidebar and content using hx-swap-oob
    sidebar_html = render(
        request,
        "provider/partials/patient_sidebar_nav.html",
        {"patient": patient, "organization": organization, "viewing_overview": True},
    ).content.decode()

    content_html = render(
        request,
        "provider/partials/patient_overview.html",
        {
            "patient": patient,
            "organization": organization,
            "encounters": all_encounters,
            "pending_invitation": pending_invitation,
        },
    ).content.decode()

    # Use OOB swap to update both targets - preserve the wrapper classes
    sidebar_wrapper = (
        f'<aside id="patient-sidebar" class="w-64 min-w-64 shrink-0 md:sticky md:top-24 md:self-start '
        f'md:max-h-[calc(100vh-8rem)] md:overflow-y-auto" hx-swap-oob="true">{sidebar_html}</aside>'
    )
    content_wrapper = f'<main id="patient-content" class="flex-1 min-w-0" hx-swap-oob="true">{content_html}</main>'
    return HttpResponse(sidebar_wrapper + content_wrapper)


@login_required
@authorize_objects(
    [ObjPerm(Patient, "patient_id", ["view_patient"]), ObjPerm(Organization, "organization_id", ["view_organization"])]
)
def patient_sidebar_main(
    request: AuthenticatedHttpRequest, organization: Organization, patient: Patient
) -> HttpResponse:
    """HTMX endpoint to load the main sidebar navigation."""
    context = {
        "patient": patient,
        "organization": organization,
        "viewing_overview": True,
    }
    return render(request, "provider/partials/patient_sidebar_nav.html", context)


@login_required
@authorize_objects(
    [ObjPerm(Patient, "patient_id", ["view_patient"]), ObjPerm(Organization, "organization_id", ["view_organization"])]
)
def patient_sidebar_encounters(
    request: AuthenticatedHttpRequest, organization: Organization, patient: Patient
) -> HttpResponse:
    """HTMX endpoint to load the encounters sidebar."""
    all_encounters = patient.encounter_set.all().order_by("-created_at")

    context = {
        "patient": patient,
        "organization": organization,
        "encounters": all_encounters,
        "selected_encounter_id": None,
    }
    return render(request, "provider/partials/patient_sidebar_encounters.html", context)


@login_required
@authorize_objects(
    [
        ObjPerm(Patient, "patient_id", ["view_patient"]),
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(Encounter, "encounter_id", ["view_encounter"]),
    ]
)
def patient_encounter_content(
    request: AuthenticatedHttpRequest, organization: Organization, patient: Patient, encounter: Encounter
) -> HttpResponse:
    """HTMX endpoint to load encounter details in the main content area."""
    tasks = encounter.task_set.all()
    from_list = request.GET.get("from_list") == "true"
    in_slideout = request.GET.get("slideout") == "true"

    # If in slideout mode, just return the encounter content
    if in_slideout:
        # Get custom attributes for encounters in this organization
        content_type = ContentType.objects.get_for_model(Encounter)
        custom_attributes = list(
            CustomAttribute.objects.filter(
                organization=organization,
                content_type=content_type,
            ).order_by("name")
        )

        # Format attributes with their values for display
        formatted_attributes = _format_attributes(encounter, custom_attributes)

        context = {
            "patient": patient,
            "organization": organization,
            "encounter": encounter,
            "tasks": tasks,
            "formatted_attributes": formatted_attributes,
            "from_list": from_list,
            "in_slideout": in_slideout,
        }
        return render(request, "provider/partials/patient_encounter_content.html", context)

    # For inline view, also update sidebar to show viewing_overview=False
    # Get custom attributes for encounters in this organization
    content_type = ContentType.objects.get_for_model(Encounter)
    custom_attributes = list(
        CustomAttribute.objects.filter(
            organization=organization,
            content_type=content_type,
        ).order_by("name")
    )

    # Format attributes with their values for display
    formatted_attributes = _format_attributes(encounter, custom_attributes)

    # Return sidebar with viewing_overview=False
    sidebar_html = render(
        request,
        "provider/partials/patient_sidebar_nav.html",
        {"patient": patient, "organization": organization, "viewing_overview": False},
    ).content.decode()

    content_context = {
        "patient": patient,
        "organization": organization,
        "encounter": encounter,
        "tasks": tasks,
        "formatted_attributes": formatted_attributes,
        "from_list": from_list,
        "in_slideout": in_slideout,
    }
    content_html = render(
        request, "provider/partials/patient_encounter_content.html", content_context
    ).content.decode()

    # Use OOB swap to update both sidebar and content
    combined_html = (
        f'<aside id="patient-sidebar" class="w-64 min-w-64 shrink-0 md:sticky md:top-24 md:self-start '
        f'md:max-h-[calc(100vh-8rem)] md:overflow-y-auto" hx-swap-oob="true">{sidebar_html}</aside>'
        f'<main id="patient-content" class="flex-1 min-w-0" hx-swap-oob="true">{content_html}</main>'
    )

    return HttpResponse(combined_html)


@login_required
@authorize_objects(
    [ObjPerm(Patient, "patient_id", ["view_patient"]), ObjPerm(Organization, "organization_id", ["view_organization"])]
)
def patient_nav_encounters(
    request: AuthenticatedHttpRequest, organization: Organization, patient: Patient
) -> HttpResponse:
    """HTMX endpoint to navigate to encounters - returns sidebar + content."""
    all_encounters = patient.encounter_set.all().order_by("-created_at")

    # Return both sidebar and content using hx-swap-oob
    sidebar_html = render(
        request,
        "provider/partials/patient_sidebar_encounters.html",
        {
            "patient": patient,
            "organization": organization,
            "encounters": all_encounters,
            "selected_encounter_id": None,
        },
    ).content.decode()

    content_html = render(
        request,
        "provider/partials/patient_encounters_list_content.html",
        {"patient": patient, "organization": organization, "encounters": all_encounters},
    ).content.decode()

    # Use OOB swap to update both targets - preserve the wrapper classes
    sidebar_wrapper = (
        f'<aside id="patient-sidebar" class="w-64 min-w-64 shrink-0 md:sticky md:top-24 md:self-start '
        f'md:max-h-[calc(100vh-8rem)] md:overflow-y-auto" hx-swap-oob="true">{sidebar_html}</aside>'
    )
    content_wrapper = f'<main id="patient-content" class="flex-1 min-w-0" hx-swap-oob="true">{content_html}</main>'
    return HttpResponse(sidebar_wrapper + content_wrapper)


@login_required
@authorize_objects(
    [ObjPerm(Patient, "patient_id", ["view_patient"]), ObjPerm(Organization, "organization_id", ["view_organization"])]
)
def patient_encounters_list_content(
    request: AuthenticatedHttpRequest, organization: Organization, patient: Patient
) -> HttpResponse:
    """HTMX endpoint to load encounters list in content area only (from 'View all' in overview)."""
    all_encounters = patient.encounter_set.all().order_by("-created_at")

    return render(
        request,
        "provider/partials/patient_encounters_list_content.html",
        {"patient": patient, "organization": organization, "encounters": all_encounters},
    )
