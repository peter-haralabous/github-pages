import pytest


@pytest.fixture(scope="session")
def base_url():
    """Hard coded to the integration env for now, but could potentially be parameterized in the future"""
    return "https://hc.wethrive.ninja"
