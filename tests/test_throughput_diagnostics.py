"""
Unit tests for clouddirect_throughput_diagnostics — no RSC credentials required.
"""

import pytest

import rubrik.server as server


CLUSTER = "11111111-2222-4333-8444-555555555555"
SHARE_FID = "3f2b6c1e-9a4d-5e7f-8b1c-2d3e4f5a6b7c"
NCD_SHARE_ID = "7a8b9c0d-1e2f-4a3b-8c4d-5e6f7a8b9c0d"
TARGET_FID = "c1d2e3f4-a5b6-5c7d-8e9f-0a1b2c3d4e5f"
TARGET_RSC_ID = "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
UNMANAGED_TARGET_FID = "d1e2f3a4-b5c6-5d7e-8f9a-0b1c2d3e4f5a"
TASK_ID = "DIAGNOSTICS_0f1e2d3c-4b5a-4978-8796-a5b4c3d2e1f0"

LEG = {
    "write": {"bytesPerSec": 52_428_800.0, "epochBytesPerSec": [41_943_040.0, 52_428_800.0]},
    "read": {"bytesPerSec": 104_857_600.0, "epochBytesPerSec": [94_371_840.0, 104_857_600.0]},
}


class _FakeClient:
    """Answers each throughput diagnostics GraphQL call; the run walks through `statuses`."""

    def __init__(self, statuses):
        self.statuses = list(statuses)
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
                {"clusterUuid": CLUSTER, "name": "Site A", "deviceDetails": []},
            ]}}
        if "ncdTargets(" in operation:
            targets = []
            if variables["clusterUuid"] == CLUSTER:
                targets = [
                    {"id": TARGET_FID, "rscId": TARGET_RSC_ID, "name": "s3-target", "provider": "s3",
                     "host": "", "dataBucket": "backups"},
                    {"id": UNMANAGED_TARGET_FID, "rscId": "", "name": "unmanaged", "provider": "s3",
                     "host": "", "dataBucket": "other"},
                ]
            return {"data": {"ncdTargets": {"targets": targets}}}
        if "startCloudDirectThroughputDiagnostics" in operation:
            return {"data": {"startCloudDirectThroughputDiagnostics": {"id": TASK_ID, "status": "QUEUED"}}}
        if "cloudDirectThroughputDiagnostics(" in operation:
            status = self.statuses.pop(0) if len(self.statuses) > 1 else self.statuses[0]
            done = status in ("SUCCEEDED", "FAILED", "CANCELED")
            return {"data": {"cloudDirectThroughputDiagnostics": {
                "taskId": TASK_ID, "status": status,
                "startTime": "2026-10-06T04:00:00.000Z",
                "endTime": "2026-10-06T04:05:00.000Z" if done else None,
                "error": "target leg failed" if status == "FAILED" else "",
                "params": {"sizeMb": 100, "num": 3, "epochs": 10, "warmup": 5},
                "source": LEG if status == "SUCCEEDED" else None,
                "target": LEG if status == "SUCCEEDED" else None,
            }}}
        raise AssertionError(f"unexpected operation: {operation}")


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(server.time, "sleep", lambda _: None)


def _use_client(monkeypatch, client):
    monkeypatch.setattr(server, "_mcp_rsc_client", lambda: client)
    return client


def test_share_and_target_run_returns_stats(monkeypatch):
    client = _use_client(monkeypatch, _FakeClient(["QUEUED", "RUNNING", "SUCCEEDED"]))

    out = server.clouddirect_throughput_diagnostics(
        share_id=SHARE_FID, source_dir="diag", target_id=TARGET_FID, bucket="speedtest",
    )

    # The target is looked up only in the share's cluster and passed by its
    # RSC managed ID.
    assert [v["clusterUuid"] for v in client.ops("ncdTargets(")] == [CLUSTER]
    assert client.ops("allCloudDirectSites") == []
    (start_vars,) = client.ops("startCloudDirectThroughputDiagnostics")
    assert start_vars["input"] == {
        "clusterUuid": CLUSTER,
        "shareFid": SHARE_FID,
        "sourceDir": "diag",
        "targetPolarisManagedId": TARGET_RSC_ID,
        "bucket": "speedtest",
    }
    assert client.ops("cloudDirectThroughputDiagnostics(") == [{"taskId": TASK_ID, "clusterUuid": CLUSTER}] * 3
    assert out["status"] == "SUCCEEDED"
    assert out["task_id"] == TASK_ID
    assert out["share"]["name"] == "/ifs/data/share1"
    assert out["target"]["rsc_id"] == TARGET_RSC_ID
    assert out["params"] == {"sizeMb": 100, "num": 3, "epochs": 10, "warmup": 5}
    assert out["share_stats"]["write"] == {
        "bytes_per_sec": 52_428_800.0, "epoch_bytes_per_sec": [41_943_040.0, 52_428_800.0],
    }
    assert out["target_stats"]["read"]["bytes_per_sec"] == 104_857_600.0
    assert "timed_out" not in out


def test_target_only_run_searches_every_cluster_and_passes_sizing(monkeypatch):
    client = _use_client(monkeypatch, _FakeClient(["SUCCEEDED"]))

    out = server.clouddirect_throughput_diagnostics(
        target_id=TARGET_RSC_ID, bucket="speedtest", size_mb=1, num=2, epochs=3, warmup=0, max_duration_seconds=60,
    )

    assert [v["clusterUuid"] for v in client.ops("ncdTargets(")] == ["other-cluster", CLUSTER]
    (start_vars,) = client.ops("startCloudDirectThroughputDiagnostics")
    assert start_vars["input"] == {
        "clusterUuid": CLUSTER,
        "targetPolarisManagedId": TARGET_RSC_ID,
        "bucket": "speedtest",
        "sizeMb": 1,
        "num": 2,
        "epochs": 3,
        "warmup": 0,
        "maxDurationSec": 60,
    }
    assert "share" not in out


def test_target_lookup_in_given_cluster(monkeypatch):
    client = _use_client(monkeypatch, _FakeClient(["SUCCEEDED"]))

    server.clouddirect_throughput_diagnostics(target_id=TARGET_FID, bucket="speedtest", cluster_uuid=CLUSTER)

    assert client.ops("allCloudDirectSites") == []
    assert [v["clusterUuid"] for v in client.ops("ncdTargets(")] == [CLUSTER]


def test_failed_run_returns_error_without_stats(monkeypatch):
    _use_client(monkeypatch, _FakeClient(["RUNNING", "FAILED"]))

    out = server.clouddirect_throughput_diagnostics(target_id=TARGET_FID, bucket="speedtest")

    assert out["status"] == "FAILED"
    assert out["error"] == "target leg failed"
    assert out["target_stats"] is None
    assert out["target"]["name"] == "s3-target"


def test_run_stops_waiting_after_deadline(monkeypatch):
    client = _use_client(monkeypatch, _FakeClient(["RUNNING"]))
    clock = iter(range(0, 100_000, 50))
    monkeypatch.setattr(server.time, "monotonic", lambda: next(clock))

    out = server.clouddirect_throughput_diagnostics(share_id=SHARE_FID, source_dir="diag", max_duration_seconds=60)

    assert out["timed_out"] is True
    assert out["status"] == "RUNNING"
    assert out["task_id"] == TASK_ID
    assert client.ops("startCloudDirectThroughputDiagnostics")


def test_unmanaged_target_rejected_before_start(monkeypatch):
    client = _use_client(monkeypatch, _FakeClient(["SUCCEEDED"]))

    with pytest.raises(ValueError, match="not managed by RSC"):
        server.clouddirect_throughput_diagnostics(target_id=UNMANAGED_TARGET_FID, bucket="speedtest")
    assert client.ops("startCloudDirectThroughputDiagnostics") == []


def test_unknown_share_rejected_before_start(monkeypatch):
    client = _FakeClient(["SUCCEEDED"])
    original = client.execute

    def _execute(operation, variables=None, max_records=None):
        if "cloudDirectNasShare(" in operation:
            client.calls.append((operation, variables))
            return {"data": {"cloudDirectNasShare": {"id": SHARE_FID, "cloudDirectId": ""}}}
        return original(operation, variables, max_records)

    client.execute = _execute
    _use_client(monkeypatch, client)

    with pytest.raises(ValueError, match="No NAS Cloud Direct share"):
        server.clouddirect_throughput_diagnostics(share_id=SHARE_FID, source_dir="diag")
    assert client.ops("startCloudDirectThroughputDiagnostics") == []


@pytest.mark.parametrize("kwargs", [
    {},
    {"share_id": SHARE_FID},
    {"source_dir": "diag"},
    {"target_id": TARGET_FID},
    {"bucket": "speedtest"},
    {"share_id": SHARE_FID, "source_dir": "/abs"},
    {"share_id": SHARE_FID, "source_dir": "a/../b"},
    {"share_id": SHARE_FID, "source_dir": ""},
    {"share_id": SHARE_FID, "source_dir": "diag", "size_mb": 0},
    {"share_id": SHARE_FID, "source_dir": "diag", "warmup": -1},
    {"share_id": SHARE_FID, "source_dir": "diag", "max_duration_seconds": 0},
    {"share_id": SHARE_FID, "source_dir": "diag", "size_mb": 2500, "num": 3},
    {"share_id": SHARE_FID, "source_dir": "diag", "size_mb": 2000},
    {"share_id": SHARE_FID, "source_dir": "diag", "epochs": 5},
    {"share_id": SHARE_FID, "source_dir": "diag", "epochs": 3, "warmup": 3},
    {"share_id": SHARE_FID, "source_dir": "diag", "cluster_uuid": CLUSTER},
    {"share_id": "not-a-uuid", "source_dir": "diag"},
    {"target_id": TARGET_FID, "bucket": "speedtest", "cluster_uuid": "not-a-uuid"},
])
def test_rejects_bad_input_before_calling_rsc(monkeypatch, kwargs):
    def _no_client():
        raise AssertionError("RSC must not be called for invalid input")

    monkeypatch.setattr(server, "_mcp_rsc_client", _no_client)
    with pytest.raises(ValueError):
        server.clouddirect_throughput_diagnostics(**kwargs)
