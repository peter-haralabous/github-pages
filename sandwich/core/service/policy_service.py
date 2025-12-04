from dataclasses import dataclass
from pathlib import Path

from sandwich.core.models.consent import ConsentPolicy


@dataclass(frozen=True)
class PolicyLangInfo:
    lang: str
    label: str
    markdown_file: str
    slug: str


@dataclass(frozen=True)
class PolicyVersion:
    version: str
    languages: list[PolicyLangInfo] | None = None


type PolicyRegistry = dict[ConsentPolicy, list[PolicyVersion]]


class PolicyService:
    # Registry of all policy versions and language info
    registry: PolicyRegistry = {
        ConsentPolicy.THRIVE_TERMS_OF_USE: [
            PolicyVersion(
                version="2020-06-26",
                languages=[
                    PolicyLangInfo(
                        lang="en",
                        label="Thrive Terms of Use",
                        markdown_file="terms_of_use_2020-06-26.md",
                        slug="terms-of-use",
                    ),
                    PolicyLangInfo(
                        lang="fr",
                        label="Conditions d'utilisation Thrive",
                        markdown_file="terms_of_use_fr_2020-06-26.md",
                        slug="terms-of-use-fr",
                    ),
                ],
            ),
        ],
        ConsentPolicy.THRIVE_PRIVACY_POLICY: [
            PolicyVersion(
                version="2021-11-09",
                languages=[
                    PolicyLangInfo(
                        lang="en",
                        label="Thrive Privacy Notice",
                        markdown_file="privacy_policy_2021-11-09.md",
                        slug="privacy-notice",
                    ),
                    PolicyLangInfo(
                        lang="fr",
                        label="Avis de confidentialité Thrive",
                        markdown_file="privacy_policy_fr_2021-11-09.md",
                        slug="privacy-notice-fr",
                    ),
                ],
            ),
        ],
        ConsentPolicy.THRIVE_MARKETING_POLICY: [
            PolicyVersion(
                version="2025-10-16",
            ),
        ],
    }

    @classmethod
    def extract_version_from_value(cls, value: str) -> str | None:
        """Extracts the version suffix from a policy value string,
        e.g. 'THRIVE_TERMS_OF_USE__2020-06-26' -> '2020-06-26'."""
        parts = value.rsplit("__", 1)
        return parts[1] if len(parts) > 1 else None

    @classmethod
    def get_content_by_slug(cls, slug, lang=None) -> str:
        lang_info = cls.get_by_slug(slug)
        if not lang_info:
            return ""
        base_dir = Path(__file__).parent.parent / "policies"
        file_path = base_dir / lang_info.markdown_file
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    @classmethod
    def get_latest(cls, policy_key, lang) -> PolicyLangInfo | None:
        versions = cls.registry.get(policy_key)
        if not versions:
            return None
        latest = versions[0]
        return getattr(latest, lang, None)

    @classmethod
    def get_by_slug(cls, slug) -> PolicyLangInfo | None:
        for versions in cls.registry.values():
            latest = versions[0]
            for lang_info in latest.languages or []:
                if lang_info.slug == slug:
                    return lang_info
        return None
