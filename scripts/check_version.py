#!/usr/bin/env python3

import argparse
import logging
import sys
from http import HTTPStatus
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)


def notice(message: str):
    logger.info(message)


def success(message: str):
    logger.info(message)
    sys.exit(0)


def failure(message: str, exc_info: Exception | None = None):
    logger.exception("Smoke test failed: %s", message, exc_info=exc_info)
    sys.exit(1)


def check_deployed_version(base_url: str, sha: str):
    healthcheck_url = urljoin(base_url, "/healthcheck")

    notice(f"GET {healthcheck_url=}")
    try:
        response = requests.get(healthcheck_url, timeout=5)
    except requests.exceptions.RequestException as exc_info:
        failure("Requests failure", exc_info=exc_info)

    notice(f"{response.status_code=}")
    if response.status_code != HTTPStatus.OK:
        failure(f"{response.status_code=} != HTTPStatus.OK")

    version = response.json().get("version")
    notice(f"{version=}")
    if version != sha:
        failure(f"'{version=}' != '{sha=}'")


def main(base_url: str, sha: str):
    check_deployed_version(base_url, sha)
    success("Version check passed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(filename)s:%(lineno)d:%(funcName)s: %(message)s")

    def non_blank(value: str) -> str:
        if not value:
            raise argparse.ArgumentTypeError
        return value

    parser = argparse.ArgumentParser(description="Run smoke tests against a website URL.")
    parser.add_argument("url", type=non_blank, help="The base URL of the website to test.")
    parser.add_argument("sha", type=non_blank, help="The hash of the commit deployed")
    args = parser.parse_args()
    main(base_url=args.url, sha=args.sha)
