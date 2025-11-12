import logging
from uuid import UUID

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from slugify import slugify

from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.custom_attribute import CustomAttributeEnum
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.organization import Organization
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
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
                "class": "form-select",
                "hx-get": "",  # Set dynamically in __init__
                "hx-target": "#enum-fields-container",
                "hx-trigger": "change",
            }
        ),
        initial=None,
    )

    def __init__(self, *args, content_type: ContentType, organization: Organization, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.organization = organization
        self.content_type = content_type

        # Set HTMX URL with organization_id
        self.fields["input_type"].widget.attrs["hx-get"] = reverse(
            "providers:custom_attribute_enum_fields", kwargs={"organization_id": organization.id}
        )

        self.helper = FormHelper()
        self.helper.form_tag = False  # Handle form tag in template

        # if self.instance.pk:
        #     self.initial["input_type"] = self._from_instance(self.instance)
        #     self.fields["input_type"].widget.attrs["disabled"] = True

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
        fields = ("label", "value", "color_code")
        widgets = {
            "label": forms.TextInput(attrs={"class": "form-control", "placeholder": "Label"}),
            "value": forms.TextInput(attrs={"class": "form-control", "placeholder": "Value (auto-generated)"}),
            "color_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "RRGGBB"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.fields["value"].required = False
        self.fields["color_code"].required = False

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is not None:
            label = cleaned_data.get("label")

            # Auto-generate value from label if not provided
            if label is not None and not cleaned_data.get("value"):
                cleaned_data["value"] = slugify(label)

        return cleaned_data


CustomAttributeEnumFormSet = forms.inlineformset_factory(
    CustomAttribute,
    CustomAttributeEnum,
    form=CustomAttributeEnumForm,
    extra=1,
    min_num=0,  # Will validate manually based on input_type
    can_delete=True,
)


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
        input_type = form.data["input_type"]
        requires_enums = input_type in ("select", "multi_select")

        if form.is_valid() and formset.is_valid():
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
    form = CustomAttributeForm(
        request.POST if request.method == "POST" else None,
        instance=attribute,
        content_type=attribute.content_type,
        organization=organization,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, "Custom attribute updated successfully.")
        return HttpResponseRedirect(
            reverse(
                "providers:custom_attribute_list",
                kwargs={"organization_id": organization.id},
            )
        )

    context = {
        "organization": organization,
        "form": form,
        "attribute": attribute,
    }
    return render(request, "provider/custom_attribute_edit.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_list(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    page = request.GET.get("page", 1)

    # TODO: permission filtering after defining the rules
    # provider_patients: QuerySet = get_objects_for_user(request.user, "core.view_patient")
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

    context = {
        "attributes": paginator.get_page(page),
        "organization": organization,
        "sort": sort,
        "page": page,
    }
    if request.headers.get("HX-Request"):
        return render(request, "provider/partials/custom_attribute_list_table.html", context)
    return render(request, "provider/custom_attribute_list.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_archive(
    request: AuthenticatedHttpRequest, organization: Organization, attribute_id: UUID
) -> HttpResponse:
    return HttpResponse(status=200)
