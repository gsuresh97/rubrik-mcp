"""Unit tests for the MCP -> RSC product-identity wiring.

These are mock-based and need no credentials or network: they assert that the
MCP constructs RSCClient with the product identity that drives the SDK
telemetry headers, without ever building a real client.
"""

from unittest.mock import patch

import rubrik.server as server


def test_factory_passes_product_and_version_to_rscclient():
    with patch.object(server, "RSCClient") as mock_client, \
         patch.object(server, "_mcp_version", return_value="1.2.3"):
        server._mcp_rsc_client()

    mock_client.assert_called_once_with(product="rubrik-mcp", product_version="1.2.3")


def test_product_name_is_bare_rubrik_mcp():
    # The product string must stay bare (no language suffix); runtime details
    # are carried in the User-Agent.
    assert server._MCP_PRODUCT == "rubrik-mcp"


def test_version_falls_back_to_package_version_when_metadata_missing():
    # Even without install metadata the MCP reports its own version — never
    # "unknown" and never the rsc-client version.
    from rubrik import __version__

    with patch.object(server, "_pkg_version", side_effect=server.PackageNotFoundError):
        assert server._mcp_version() == __version__


def test_call_sites_use_the_factory_not_raw_rscclient():
    # Every live API path should route through the factory so the headers are
    # always sent. Guards against a new RSCClient() call site slipping in.
    import inspect

    src = inspect.getsource(server)
    # The only legitimate bare "client = RSCClient()" lives in a docstring
    # example; real code must call the factory.
    code_lines = [
        ln for ln in src.splitlines()
        if "client = RSCClient()" in ln and not ln.lstrip().startswith('"')
    ]
    assert code_lines == [], f"raw RSCClient() call sites found: {code_lines}"
