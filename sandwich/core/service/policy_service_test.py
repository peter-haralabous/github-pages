import pytest

from sandwich.core.models.consent import ConsentPolicy
from sandwich.core.service.policy_service import PolicyService


def test_get_by_slug_found():
    """Should find English privacy notice."""
    lang_info = PolicyService.get_by_slug("privacy-notice")
    assert lang_info is not None
    assert lang_info.lang == "en"
    assert lang_info.label == "Thrive Privacy Notice"


def test_get_by_slug_found_fr():
    """Should find French privacy notice."""
    lang_info = PolicyService.get_by_slug("privacy-notice-fr")
    assert lang_info is not None
    assert lang_info.lang == "fr"
    assert lang_info.label == "Avis de confidentialité Thrive"


def test_get_by_slug_not_found():
    """Should return None for unknown slug."""
    lang_info = PolicyService.get_by_slug("not-a-real-slug")
    assert lang_info is None


@pytest.mark.parametrize("policy_enum", list(ConsentPolicy))
def test_policy_enum_value_matches_policyservice(policy_enum):
    """Test for policy version matching between ConsentPolicy and PolicyService"""
    version = PolicyService.extract_version_from_value(policy_enum.value)
    policy_versions = PolicyService.registry.get(policy_enum)
    assert policy_versions is not None, f"No entry in PolicyService.registry for {policy_enum.name}"
    if version:
        found_versions = [pv.version for pv in policy_versions]
        matches = [pv for pv in policy_versions if pv.version == version]
        assert matches, (
            f"No matching version in registry for {policy_enum.name}: expected {version}, found {found_versions}"
        )


def test_registry_keys_match_enum():
    """Ensure registry keys match ConsentPolicy enum."""
    enum_keys = set(ConsentPolicy)
    registry_keys = set(PolicyService.registry.keys())
    extra_keys = registry_keys - enum_keys
    assert not extra_keys, f"Registry contains keys not in ConsentPolicy: {list(extra_keys)}"
