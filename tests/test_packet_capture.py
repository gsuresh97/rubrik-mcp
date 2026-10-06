"""
Unit tests for clouddirect_packet_capture — no RSC credentials required.
"""

import os
import stat
from types import SimpleNamespace

import pytest

import rubrik.server as server


CLUSTER = "11111111-2222-4333-8444-555555555555"
SHARE_FID = "3f2b6c1e-9a4d-5e7f-8b1c-2d3e4f5a6b7c"
NCD_SHARE_ID = "7a8b9c0d-1e2f-4a3b-8c4d-5e6f7a8b9c0d"
RECENT_VM = "0123456789abcdef0123456789abcdef01234567"
OLDER_VM = "89abcdef0123456789abcdef0123456789abcdef"
REMOVED_VM = "fedcba9876543210fedcba9876543210fedcba98"
CAPTURE_ID = "0f1e2d3c4b5a69788796a5b4c3d2e1f0"
FILE_ID = "9e8d7c6b-5a49-4382-9170-6f5e4d3c2b1a"
FILTER = "(host 192.0.2.10)"

DEVICES = [
    {"hardwareId": OLDER_VM, "lastState": "HEALTHY", "lastConnectedAt": "2026-10-06T01:00:00.000Z", "removedAt": None},
    {"hardwareId": RECENT_VM, "lastState": "HEALTHY", "lastConnectedAt": "2026-10-06T03:00:00.000Z", "removedAt": None},
    {"hardwareId": REMOVED_VM, "lastState": "HEALTHY", "lastConnectedAt": "2026-10-06T04:00:00.000Z",
     "removedAt": "2026-10-06T04:30:00.000Z"},
]


class _FakeClient:
    """Answers each packet-capture GraphQL call; the capture walks through `states`."""

    def __init__(self, states):
        self.states = list(states)
        self.calls = []

    def ops(self, needle):
        return [variables for op, variables in self.calls if needle in op]

    def execute(self, operation, variables=None, max_records=None):
        self.calls.append((operation, variables))
        if "cloudDirectNasShare(" in operation:
            return {"data": {"cloudDirectNasShare": {
                "id": SHARE_FID, "cloudDirectId": NCD_SHARE_ID, "clusterUuid": CLUSTER,
                "name": "/ifs/data/share1", "exportPath": "192.0.2.10/ifs/data/share1",
            }}}
        if "allCloudDirectSites" in operation:
            return {"data": {"allCloudDirectSites": [
                {"clusterUuid": "other-cluster", "name": "Other", "deviceDetails": []},
                {"clusterUuid": CLUSTER, "name": "Site A", "deviceDetails": DEVICES},
            ]}}
        if "startCloudDirectPacketCapture" in operation:
            return {"data": {"startCloudDirectPacketCapture": {
                "capture": {"captureId": CAPTURE_ID, "state": "CREATED"},
            }}}
        if "cloudDirectPacketCaptureFile(" in operation:
            return {"data": {"cloudDirectPacketCaptureFile": {"fileId": FILE_ID}}}
        if "cloudDirectPacketCapture(" in operation:
            state = self.states.pop(0) if len(self.states) > 1 else self.states[0]
            done = state in ("SUCCESS", "FAILURE")
            return {"data": {"cloudDirectPacketCapture": {
                "captureId": CAPTURE_ID, "hardwareId": variables["hardwareId"], "state": state,
                "errorMessage": "upload failed" if state == "FAILURE" else "",
                "filter": FILTER,
                "resource": {"kind": "SHARE", "name": "/ifs/data/share1", "clusterResourceId": "11",
                             "protocol": "NFS", "hosts": ["192.0.2.10"]},
                "result": {"operationOutput": "Done list. Received 15 entries", "operationError": "",
                           "captureFileSizeBytes": 7876} if done else None,
            }}}
        raise AssertionError(f"unexpected operation: {operation}")


@pytest.fixture
def downloads(monkeypatch):
    calls = []

    def _fake_download(client, file_id, dest):
        calls.append((file_id, dest))
        return 7876

    monkeypatch.setattr(server, "_download_rsc_file", _fake_download)
    monkeypatch.setattr(server.time, "sleep", lambda _: None)
    return calls


def _use_client(monkeypatch, client):
    monkeypatch.setattr(server, "_mcp_rsc_client", lambda: client)
    return client


def test_capture_success_downloads_pcap(monkeypatch, downloads, tmp_path):
    client = _use_client(monkeypatch, _FakeClient(["CREATED", "EXECUTING", "SUCCESS"]))

    out = server.clouddirect_packet_capture(SHARE_FID, operation="list", output_dir=str(tmp_path))

    # The capture targets the share by its Cloud Direct ID on the most recently
    # connected healthy VM that has not been removed.
    (start_vars,) = client.ops("startCloudDirectPacketCapture")
    assert start_vars["input"] == {
        "clusterUuid": CLUSTER,
        "hardwareId": RECENT_VM,
        "resourceId": NCD_SHARE_ID,
        "operation": "LIST",
        "maxDurationSeconds": 30,
    }
    assert len(client.ops("cloudDirectPacketCapture(")) == 3
    assert out["state"] == "SUCCESS"
    assert out["hardware_id"] == RECENT_VM
    assert out["filter"] == FILTER
    assert out["operation_output"] == "Done list. Received 15 entries"
    assert out["file_id"] == FILE_ID
    expected = (tmp_path / f"packet-capture-{CAPTURE_ID}.pcap").resolve()
    assert out["pcap_path"] == str(expected)
    assert downloads == [(FILE_ID, expected)]


def test_capture_passes_optional_inputs_and_explicit_vm(monkeypatch, downloads, tmp_path):
    client = _use_client(monkeypatch, _FakeClient(["SUCCESS"]))

    server.clouddirect_packet_capture(
        SHARE_FID, operation="READ", protocol="nfs4", path="/dir/file", read_size_bytes=4096,
        duration_seconds=10, hardware_id=OLDER_VM, output_dir=str(tmp_path),
    )

    assert client.ops("allCloudDirectSites") == []
    (start_vars,) = client.ops("startCloudDirectPacketCapture")
    assert start_vars["input"] == {
        "clusterUuid": CLUSTER,
        "hardwareId": OLDER_VM,
        "resourceId": NCD_SHARE_ID,
        "operation": "READ",
        "maxDurationSeconds": 10,
        "protocol": "NFS4",
        "path": "/dir/file",
        "readSizeBytes": 4096,
    }


def test_capture_failure_skips_download(monkeypatch, downloads):
    client = _use_client(monkeypatch, _FakeClient(["FAILURE"]))

    out = server.clouddirect_packet_capture(SHARE_FID)

    assert out["state"] == "FAILURE"
    assert out["error_message"] == "upload failed"
    assert "pcap_path" not in out
    assert client.ops("cloudDirectPacketCaptureFile(") == []
    assert downloads == []


def test_capture_stops_waiting_after_deadline(monkeypatch, downloads):
    client = _use_client(monkeypatch, _FakeClient(["EXECUTING"]))
    clock = iter(range(0, 10_000, 50))
    monkeypatch.setattr(server.time, "monotonic", lambda: next(clock))

    out = server.clouddirect_packet_capture(SHARE_FID, duration_seconds=10)

    assert out["timed_out"] is True
    assert out["state"] == "EXECUTING"
    assert out["capture_id"] == CAPTURE_ID
    assert downloads == []


@pytest.mark.parametrize("kwargs", [
    {"operation": "DELETE"},
    {"protocol": "FTP"},
    {"duration_seconds": 0},
    {"duration_seconds": 301},
    {"operation": "READ"},
    {"hardware_id": "not-a-hardware-id"},
    {"share_id": "not-a-uuid"},
])
def test_capture_rejects_bad_input_before_calling_rsc(monkeypatch, kwargs):
    def _no_client():
        raise AssertionError("RSC must not be called for invalid input")

    monkeypatch.setattr(server, "_mcp_rsc_client", _no_client)
    args = {"share_id": SHARE_FID, **kwargs}
    with pytest.raises(ValueError):
        server.clouddirect_packet_capture(**args)


def test_pick_capture_vm_requires_healthy_vm():
    sites = [{"clusterUuid": CLUSTER, "name": "Site A", "deviceDetails": [
        {"hardwareId": OLDER_VM, "lastState": "DISCONNECTED", "removedAt": None},
    ]}]
    with pytest.raises(ValueError, match="No healthy VM"):
        server._pick_capture_vm(sites, CLUSTER)
    with pytest.raises(ValueError, match="No Cloud Direct site"):
        server._pick_capture_vm(sites, "other-cluster")


def test_download_rsc_file_uses_endpoint_auth_and_writes_private_file(tmp_path):
    requests = []

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return b"\xd4\xc3\xb2\xa1pcap"

    def _urlopen(request, timeout=None):
        requests.append(request)
        return _Resp()

    endpoint = SimpleNamespace(
        url="https://rsc.example.com/api/graphql",
        base_headers={"Authorization": "Bearer tok"},
        urlopen=_urlopen,
    )
    dest = tmp_path / "captures" / "c.pcap"

    size = server._download_rsc_file(SimpleNamespace(endpoint=endpoint), FILE_ID, dest)

    (request,) = requests
    assert request.full_url == f"https://rsc.example.com/file-downloads/{FILE_ID}"
    assert request.get_header("Authorization") == "Bearer tok"
    assert size == 8
    assert dest.read_bytes() == b"\xd4\xc3\xb2\xa1pcap"
    assert stat.S_IMODE(os.stat(dest).st_mode) == 0o600
