import logging
from uuid import UUID

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db import transaction
from django.forms import BaseInlineFormSet
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_list_or_404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from slugify import slugify

from sandwich.core.forms import DeleteConfirmationForm
from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.custom_attribute import CustomAttributeEnum
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.organization import Organization
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.util.http import htmx_redirect
from sandwich.core.util.http import validate_sort

logger = logging.getLogger(__name__)


class CustomAttributeForm(forms.ModelForm[CustomAttribute]):
    class Meta:
        model = CustomAttribute
        fields = ("name",)

    input_type = forms.ChoiceField(
        choices=[
            ("date", "Date"),
            ("select", "Select"),
            ("multi_select", "Multi-Select"),
        ],
        widget=forms.Select(
            attrs={
                "hx-get": "",  # Set dynamically in __init__
                "hx-target": "#enum-fields-container",
                "hx-trigger": "change",
            }
        ),
        initial=None,
    )

    def __init__(
        self,
        *args,
        content_type: ContentType,
        organization: Organization,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.organization = organization
        self.content_type = content_type

        instance: CustomAttribute | None = kwargs.get("instance")
        if instance is not None:
            input_type = self._from_instance(instance)
            self.fields["input_type"].initial = input_type

        # Set HTMX URL with organization_id
        self.fields["input_type"].widget.attrs["hx-get"] = reverse(
            "providers:custom_attribute_enum_fields", kwargs={"organization_id": organization.id}
        )

        self.helper = FormHelper()
        self.helper.form_tag = False  # Handle form tag in template

    def _from_instance(self, instance: CustomAttribute) -> str | None:
        """Derive 'input_type' field value from instance data."""
        match (instance.data_type, instance.is_multi):
            case (CustomAttribute.DataType.DATE, False):
                return "date"
            case (CustomAttribute.DataType.ENUM, False):
                return "select"
            case (CustomAttribute.DataType.ENUM, True):
                return "multi_select"
        return None

    def _from_input_type(self, input_type: str) -> tuple[CustomAttribute.DataType, bool]:
        """Derive model fields from 'input_type' field value."""
        match input_type:
            case "date":
                return (CustomAttribute.DataType.DATE, False)
            case "select":
                return (CustomAttribute.DataType.ENUM, False)
            case "multi_select":
                return (CustomAttribute.DataType.ENUM, True)
        raise ValueError(f"Invalid input_type: {input_type}")

    def clean_input_type(self):
        # Handle disabled field not being submitted
        # if self.instance.pk:
        #     return self._from_instance(self.instance)
        return self.cleaned_data["input_type"]

    def requires_enums(self):
        input_type = self.data["input_type"]
        return input_type in ("select", "multi_select")

    def save(self, commit=True):  # noqa: FBT002
        instance = super().save(commit=False)

        data_type, is_multi = self._from_input_type(self.cleaned_data["input_type"])
        instance.data_type = data_type
        instance.is_multi = is_multi
        instance.content_type = self.content_type
        instance.organization = self.organization

        if commit:
            instance.save()

        return instance


class CustomAttributeEnumForm(forms.ModelForm[CustomAttributeEnum]):
    class Meta:
        model = CustomAttributeEnum
        fields = ("label", "color_code")
        widgets = {
            "label": forms.TextInput(attrs={"class": "form-control", "placeholder": "Label"}),
            "color_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "RRGGBB"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_labels = True

        self.fields["label"].label = "Label"
        self.fields["color_code"].label = "Color code"

        self.fields["color_code"].required = False

    def save(self, commit=True):  # noqa: FBT002
        instance = super().save(commit=False)

        # Auto-generate value from label if not already set
        label = self.cleaned_data.get("label")
        if label and not instance.value:
            instance.value = slugify(label)

        if commit:
            instance.save()

        return instance


CustomAttributeEnumFormSet = forms.inlineformset_factory(
    CustomAttribute,
    CustomAttributeEnum,
    form=CustomAttributeEnumForm,
    extra=1,
    min_num=0,  # Will validate manually based on input_type
    can_delete=True,
)


def validate_custom_enum(
    request: AuthenticatedHttpRequest,
    organization: Organization,
    form: CustomAttributeForm,
    formset: BaseInlineFormSet[CustomAttributeEnum, CustomAttribute, CustomAttributeEnumForm],
):
    # Validate formset only if ENUM type
    if form.requires_enums():
        if formset.is_valid():
            # Check at least one enum value
            existing_options = [enum for enum in formset.cleaned_data if not enum.get("DELETE")]
            if existing_options.__len__() == 0:
                form.add_error(
                    "input_type",
                    "At least one option is required for Select/Multi-Select types. Please add options below.",
                )

                context = {
                    "organization": organization,
                    "form": form,
                    "formset": formset,
                    "show_enum_fields": True,
                }
                return render(request, "provider/custom_attribute_edit.html", context)
        else:
            logger.error("Error with updating custom attribute options", extra={"formset_errors": formset.errors})
            context = {
                "organization": organization,
                "form": form,
                "formset": formset,
                "show_enum_fields": True,
            }
            return render(request, "provider/custom_attribute_edit.html", context)

    # return false for no errors
    return False


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_add(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    if request.method == "POST":
        form = CustomAttributeForm(
            request.POST,
            content_type=ContentType.objects.get_for_model(Encounter),
            organization=organization,
        )

        # Create formset with POST data, but without instance yet
        formset = CustomAttributeEnumFormSet(request.POST, prefix="enums")
        requires_enums = form.requires_enums()

        if form.is_valid():
            formset_validation_issues = validate_custom_enum(request, organization, form, formset)
            if formset_validation_issues:
                return formset_validation_issues
            # Save everything in transaction
            with transaction.atomic():
                instance = form.save()

                if requires_enums:
                    formset.instance = instance
                    formset.save()

            messages.success(request, "Custom attribute created successfully.")
            return HttpResponseRedirect(
                reverse("providers:custom_attribute_list", kwargs={"organization_id": organization.id})
            )

        logger.error("Error with updating custom attribute", extra={"form_errors": form.errors})
        messages.error(request, "Error while creating custom attribute")
        context = {
            "organization": organization,
            "form": form,
            "formset": CustomAttributeEnumFormSet(prefix="enums"),
            "show_enum_fields": requires_enums,
        }
        return render(request, "provider/custom_attribute_edit.html", context)
    form = CustomAttributeForm(
        content_type=ContentType.objects.get_for_model(Encounter),
        organization=organization,
    )
    formset = CustomAttributeEnumFormSet(prefix="enums")

    context = {
        "organization": organization,
        "form": form,
        "formset": formset,
        "show_enum_fields": False,
    }
    return render(request, "provider/custom_attribute_edit.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_enum_fields(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    """HTMX endpoint to return enum formset HTML."""
    input_type = request.GET.get("input_type")

    if input_type in ("select", "multi_select"):
        formset = CustomAttributeEnumFormSet(prefix="enums")
        context = {"formset": formset}
        return render(request, "provider/partials/custom_attribute_enum_fields.html", context)
    return HttpResponse("")


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_edit(
    request: AuthenticatedHttpRequest, organization: Organization, attribute_id: UUID
) -> HttpResponse:
    attribute = get_object_or_404(CustomAttribute, id=attribute_id, organization=organization)  # TODO permission check

    if request.method == "POST":
        form = CustomAttributeForm(
            request.POST,
            content_type=ContentType.objects.get_for_model(Encounter),
            organization=organization,
            instance=attribute,
        )

        if form.is_valid():
            requires_enums = form.requires_enums()

            formset = CustomAttributeEnumFormSet(request.POST, prefix="enums", instance=attribute)
            formset_validation_issues = validate_custom_enum(request, organization, form, formset)
            if formset_validation_issues:
                return formset_validation_issues

            with transaction.atomic():
                instance = form.save()

                if requires_enums:
                    # Creates deleted_forms attribute
                    formset.save(commit=False)
                    deleted_enums = [deleted_form.instance for deleted_form in formset.deleted_forms]
                    for enum in deleted_enums:
                        enum.delete()
                    formset.instance = instance
                    formset.save()

                messages.add_message(request, messages.SUCCESS, "Custom attribute updated successfully.")
                return HttpResponseRedirect(
                    reverse(
                        "providers:custom_attribute_list",
                        kwargs={"organization_id": organization.id},
                    )
                )

        logger.error("Error with updating custom attribute", extra={"form_errors": form.errors})
        messages.error(request, "Error while updating custom attribute")
        context = {
            "organization": organization,
            "form": form,
            "formset": formset,
            "show_enum_fields": requires_enums,
        }
        return render(request, "provider/custom_attribute_edit.html", context)

    form = CustomAttributeForm(
        instance=attribute,
        content_type=attribute.content_type,
        organization=organization,
    )

    requires_enums = attribute.data_type == CustomAttribute.DataType.ENUM
    formset = CustomAttributeEnumFormSet(prefix="enums", instance=attribute)
    if requires_enums:
        attribute_enums = get_list_or_404(CustomAttributeEnum, attribute_id=attribute_id)
        enums_as_dict = [vars(enum) for enum in attribute_enums]
        formset = CustomAttributeEnumFormSet(prefix="enums", initial=enums_as_dict, instance=attribute)
        # Don't want to add an extra blank option when editing
        formset.extra = 0

    context = {
        "organization": organization,
        "form": form,
        "formset": formset,
        "show_enum_fields": requires_enums,
    }
    return render(request, "provider/custom_attribute_edit.html", context)


def _get_custom_attribute_list_context(request: AuthenticatedHttpRequest, organization: Organization) -> dict:
    """Get the context for rendering the custom attribute list."""
    page = request.GET.get("page", 1)

    sort = (
        validate_sort(
            request.GET.get("sort"),
            ["name", "created_at", "data_type", "updated_at"],
        )
        or "name"
    )

    attributes = CustomAttribute.objects.all().filter(
        organization=organization, content_type=ContentType.objects.get_for_model(Encounter)
    )
    if sort:
        attributes = attributes.order_by(sort)

    paginator = Paginator(attributes, 25)

    return {
        "attributes": paginator.get_page(page),
        "organization": organization,
        "sort": sort,
        "page": page,
    }


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_list(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    context = _get_custom_attribute_list_context(request, organization)
    if request.headers.get("HX-Request"):
        return render(request, "provider/partials/custom_attribute_list_table.html", context)
    return render(request, "provider/custom_attribute_list.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_archive(
    request: AuthenticatedHttpRequest, organization: Organization, attribute_id: UUID
) -> HttpResponse:
    """Delete a custom attribute and all its associated values."""
    attribute = get_object_or_404(CustomAttribute, id=attribute_id, organization=organization)

    if request.method == "POST":
        logger.info(
            "Processing custom attribute deletion",
            extra={"user_id": request.user.id, "attribute_id": attribute_id, "organization_id": organization.id},
        )
        form = DeleteConfirmationForm(
            request.POST,
            form_action=reverse(
                "providers:custom_attribute_archive",
                kwargs={"organization_id": organization.id, "attribute_id": attribute.id},
            ),
            hx_target="dialog",
        )

        if form.is_valid():
            attribute_name = attribute.name
            logger.info(
                "Deleting custom attribute",
                extra={
                    "attribute_id": attribute.id,
                    "attribute_name": attribute_name,
                    "organization_id": organization.id,
                },
            )

            # Delete the attribute (will cascade to values and enums)
            attribute.delete()

            messages.success(request, f"Custom field '{attribute_name}' has been deleted.")

            # Redirect back to the list page
            return htmx_redirect(
                request, reverse("providers:custom_attribute_list", kwargs={"organization_id": organization.id})
            )
        logger.warning(
            "Invalid custom attribute delete confirmation",
            extra={"user_id": request.user.id, "attribute_id": attribute_id},
        )
        # Rerender the full page with the modal open
        modal_context = {"form": form, "attribute": attribute, "organization": organization}
        context = _get_custom_attribute_list_context(request, organization)
        context.update(modal_context)
        return render(request, "provider/custom_attribute_archive.html", context)

    # GET request - render the modal
    form = DeleteConfirmationForm(
        form_action=reverse(
            "providers:custom_attribute_archive",
            kwargs={"organization_id": organization.id, "attribute_id": attribute.id},
        ),
        hx_target="dialog",
    )
    modal_context = {"form": form, "attribute": attribute, "organization": organization}

    # If it's an HTMX request, render the modal partial
    if request.headers.get("HX-Request"):
        return render(request, "provider/partials/custom_attribute_archive_modal.html", modal_context)

    # Otherwise (direct URL access or page refresh), render the full list page with the modal
    context = _get_custom_attribute_list_context(request, organization)
    context.update(modal_context)
    return render(request, "provider/custom_attribute_archive.html", context)
