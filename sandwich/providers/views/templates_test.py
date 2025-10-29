from django.urls import reverse


def test_templates_home(client, provider, organization):
    client.force_login(provider)
    url = reverse("providers:templates_home", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == 200
    assert "provider/templates.html" in [t.name for t in response.templates]


def test_templates_home_user_not_in_organization_deny_access(client, user, organization):
    client.force_login(user)
    url = reverse("providers:templates_home", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == 404
