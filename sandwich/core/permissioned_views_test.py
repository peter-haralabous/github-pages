from django.urls import get_resolver

from sandwich.core.models.patient import Patient
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.urls_test import get_all_urls


def test_view_uses_authorize_objects() -> None:
    @authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient"])])
    def protected_view(request):
        pass

    @authorize_objects([])
    def misconfigured_view(request):
        pass

    def unprotected_view(request):
        pass

    assert hasattr(protected_view, "authorize_objects")
    assert not hasattr(misconfigured_view, "authorize_objects")
    assert not hasattr(unprotected_view, "authorize_objects")


def test_all_views_permissioned() -> None:
    """
    Ensures that views in the application are at least minimally permissioned.
    "Minimally permissioned" is determined by the view being decorated by
    `@authorize_objects` with at least one `ObjPerm` rule.

    This does not test that views are adequately permissioned nor that they
    have the correct permissions, that is up to the implementer.

    TODO: This test also doesn't account for list views that do not use the
    `@authorize_objects` decorator.
    """

    allowed_unpermissioned_routes = {
        "",
        "favicon.ico",
        "healthcheck/",
        "policy/<slug:slug>/",
        "private-media/^(?P<path>.*)$",
        "events/",
        "switcher/",
        "notifications",
        "legal/",
        "delete-account/",
        "users/~redirect/",
        "users/<int:pk>/",
        "patients/",
        "patients/api/",
        "patients/api/docs",
        "patients/api/openapi.json",
        "patients/consent/",
        "patients/patient/add",
        "patients/patient/onboarding/add",
        "patients/get_phn_validation/",
        "providers/",
        "providers/organization/add",
        "patients/invite/<str:token>/accept",
        # These views are permissioned but not using the decorator
        "patients/document/<uuid:document_id>",
    }

    # TODO(MM): These views should be secured.
    #
    # This list acts as a registery of unpermissioned views. Remove entries
    # from this list when they are properly permissioned.
    unpermissioned_routes = {
        "providers/organization/<uuid:organization_id>/patient/<uuid:patient_id>/archive",
        "providers/organization/<uuid:organization_id>/patient/<uuid:patient_id>/resend_invite",
        "providers/organization/<uuid:organization_id>/patient/<uuid:patient_id>/task/<uuid:task_id>/cancel",
        "providers/organization/<uuid:organization_id>/patients",
        "providers/organization/<uuid:organization_id>/preferences/<str:list_type>/settings",
        "providers/organization/<uuid:organization_id>/preferences/<str:list_type>/save",
        "providers/organization/<uuid:organization_id>/preferences/<str:list_type>/reset",
        "providers/organization/<uuid:organization_id>/preferences",
        "providers/organization/<uuid:organization_id>/preferences/org/<str:list_type>/settings",
        "providers/organization/<uuid:organization_id>/preferences/org/<str:list_type>/save",
        "providers/organization/<uuid:organization_id>/preferences/org/<str:list_type>/reset",
        # Formio endpoints to be removed after SurveyJS implemented
        "patients/api/formio/<name>",
        "patients/api/formio/<name>/submission",
        "patients/api/formio/<name>/submission/<submission_id>",
    }

    urls = get_all_urls(get_resolver().url_patterns)

    found_unpermissioned_routes = set()
    for url in urls:
        # Ignore patterns that do not require object permissions
        if url.pattern.startswith(("admin/", "accounts/", "anymail/")):
            continue

        if not hasattr(url.view, "authorize_objects"):
            found_unpermissioned_routes.add(url.pattern)

    expected_unpermissioned_routes = allowed_unpermissioned_routes.union(unpermissioned_routes)
    assert found_unpermissioned_routes == expected_unpermissioned_routes
