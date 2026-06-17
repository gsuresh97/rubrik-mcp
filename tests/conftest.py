"""Shared pytest configuration for the rubrik-mcp test suite.

Tests marked ``integration`` (via each integration module's module-level
``pytestmark``) hit a live RSC tenant. They run only when
``RSC_SERVICE_ACCOUNT_FILE`` points at a readable service-account credential;
otherwise they self-skip here, so unit-only runs and forks without the secret
stay green.
"""

import os

import pytest


def _have_sa() -> bool:
    sa = os.environ.get("RSC_SERVICE_ACCOUNT_FILE", "")
    return bool(sa and os.path.exists(os.path.expanduser(sa)))


def pytest_collection_modifyitems(config, items):
    if _have_sa():
        return
    skip_integration = pytest.mark.skip(
        reason="RSC_SERVICE_ACCOUNT_FILE not set / file missing — skipping live-RSC tests"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
