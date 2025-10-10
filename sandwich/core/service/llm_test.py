import pytest
import urllib3

from sandwich.core.service.llm import _extract_region
from sandwich.core.service.llm import get_claude_3_sonnet
from sandwich.core.service.llm import get_claude_sonnet_4_5
from sandwich.core.service.llm import get_gpt_oss


def test__extract_region():
    assert (
        _extract_region(
            "arn:aws:bedrock:ca-central-1:153784117502:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0"
        )
        == "ca-central-1"
    )
    assert _extract_region("global.anthropic.claude-sonnet-4-5-20250929-v1:0") is None
    assert _extract_region(None) is None


# NOTE-NG: this is unrelated to anything in llm.py, but proves that our vcrpy integration is working correctly
#          outside of langchain.
@pytest.mark.vcr
def test_vcr(vcr):
    response = urllib3.request("GET", "http://example.com")
    assert response.status == 200
    assert vcr.play_count == 1


@pytest.mark.vcr
def test_claude_3_sonnet():
    response = get_claude_3_sonnet().invoke("what is 1 + 1")
    assert response.text() == "1 + 1 = 2"


@pytest.mark.vcr
def test_claude_sonnet_4_5():
    response = get_claude_sonnet_4_5().invoke("what is 1 + 1")
    assert response.text() == "1 + 1 = 2"


@pytest.mark.vcr
def test_gpt_oss():
    response = get_gpt_oss().invoke("what is 1 + 1")
    assert response.text() == "1\u202f+\u202f1\u202f=\u202f2."  # \u202f is a non-breaking space
