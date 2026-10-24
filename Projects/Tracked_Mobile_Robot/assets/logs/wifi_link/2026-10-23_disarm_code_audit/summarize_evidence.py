"""Read-only analysis of retained reports; writes this audit's summary, never raw logs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGS = HERE.parent
PROJECT = HERE.parents[3]
NAMES = ["2026-10-23_ground_1m_run02", "2026-10-23_disarm_stationary_run01",
         "2026-10-23_ground_1m_run03", "2026-10-23_ground_1m_run04"]
DIRECTIONS = ["forward", "reverse", "left", "right"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


reports = {}
for name in NAMES:
    path = LOGS / name / "browser_report.json"
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    events = raw["recent_events"]
    row = {"source": f"../{name}/browser_report.json", "sha256": sha(path),
           "observer_revision": raw.get("observer_revision", "5-original-fixed-socket"),
           "history_dropped": raw["history_dropped"], "telemetry_dropped": raw["telemetry_dropped"]}
    if name.endswith("run02"):
        end = raw["telemetry"][-1]
        stop = raw["stops"][0]
        assert stop["intent"] is False and stop["offer"]["phase"] == "IDLE"
        assert stop["tel"]["state"] == "DISARMED" and stop["tel"]["reason"] == "DISARM"
        row.update({
            "last_original_socket_tel": {k: end[k] for k in
                ["ms", "state", "reason", "last_seq", "command", "pwm", "cps", "left_count", "right_count"]},
            "last_original_socket_control_ms": max(e["ms"] for e in events if e["event"] == "CONTROL_RX"),
            "disarm_notices_or_results_recorded": sum(e["event"] in ["command_notice", "command_result"]
                and e["data"].get("cmd") == "DISARM" for e in events),
            "first_stop_wrapper_snapshot": {"ms": stop["ms"], "intent": stop["intent"],
                "focused": stop["focused"], "session": stop["offer"]["session_id"],
                "phase": stop["offer"]["phase"], "state": stop["tel"]["state"],
                "reason": stop["tel"]["reason"], "tel_local_age_ms": stop["tel_local_age_ms"],
                "stack": stop["stack"]},
            "element_blur_after_socket_gap": [e for e in events if e["event"] == "blur"
                and e.get("target") == "disarm"],
            "interpretation": "The wrapper takes this snapshot BEFORE the original stopLocal call. "
                "The first retained window-blur stop call already sees intent=false and recent DISARMED TEL. "
                "It therefore does not establish that this screen switch initiated the first stop. "
                "Element blur proves focus interaction, not a click/send/ACK. The gap still prevents identifying the stop cause."
        })
    else:
        click = next(e for e in events if e["event"] == "BUTTON_CLICK" and e.get("button") == "disarm")
        call = next(e for e in events if e["event"] == "APP_COMMAND" and e["cmd"] == "DISARM"
                    and e["ms"] >= click["ms"])
        send = next(e for e in events if e["event"] == "WS_SEND" and e["text"].startswith("DISARM,")
                    and e["ms"] >= click["ms"])
        rid = int(send["text"].rsplit("request_id=", 1)[1])
        result = next(e for e in events if e["event"] == "command_result" and e["data"]["cmd"] == "DISARM"
                      and e["data"]["request_id"] == rid and e["ms"] >= click["ms"])
        assert all(call["after"]["buttons_disabled"][key] for key in DIRECTIONS)
        assert call["after"]["intent"] is False and result["data"]["status"] == "OK"
        row.update({"connections_seen": raw["observer"]["connections_seen"],
                    "trace_errors": raw["observer"]["trace_errors"],
                    "manual_click_ms": click["ms"], "request_id": rid,
                    "session_id": result["data"]["session_id"],
                    "wire": send["text"], "directions_disabled_after_handler": True,
                    "handler_completion_after_click_ms": round(call["ms"] - click["ms"], 3),
                    "result_after_click_ms": round(result["ms"] - click["ms"], 3),
                    "status": result["data"]["status"],
                    "limitation": "Browser event timestamps, not electrical/physical stop latency."})
    reports[name] = row

pc_path = HERE / "pc_checks.json"
pc = json.loads(pc_path.read_text(encoding="utf-8"))
page = PROJECT / "03_Firmware/esp32_wifi_link/main/wifi_link_main.c"
assert pc["source"]["sha256"] == sha(page)
report = {
    "date": "2026-10-23", "status": "REVIEW_COMPLETE_HISTORICAL_CAUSE_UNDETERMINED_NOT_REPRODUCED",
    "source_page_sha256": sha(page), "analysis_script_sha256": sha(Path(__file__)),
    "reports": reports, "pc_checks": {"path": "pc_checks.json", "sha256": sha(pc_path),
        "additional_cases": pc["check_count"], "existing_cases": pc["baseline_case_count"]},
    "code_findings": [
        "Forward release requests CMD0 while retaining ARM intent; directions enabled after release ACK is expected.",
        "DISARM admission in PAGE clears intent/controlId/motion/timer and supersedes the pending request before ws.send; direction DOM flags update before the synchronous handler returns, not after STM ACK.",
        "Delayed CMD/ARM ACK, DISARM rejection/timeout and retained ACTIVE snapshots do not set intent=true again in the tested paths.",
        "Disconnect/reconnect clears local control; old socket messages are ignored and the replacement socket sends only HELLO until manual input.",
        "Server manual DISARM bypasses normal PING/CMD rate and busy gates; its dedicated stop-result slot may return BUSY, which does not reenable local intent.",
        "Closing the owning session invokes executor stop, so DISARMED alone cannot identify a manual button cause."
    ],
    "decision": {
        "historical_cause": "UNDETERMINED: run02 has no click/send/disconnect trace for the interval in question",
        "firmware_patch_justified_by_review": False,
        "firmware_modified_or_built_or_flashed": False,
        "physical_test_performed": False,
        "physical_repeat_requested_now": False,
        "current_manual_disarm_evidence": "Three later independent logs preserve manual click, disabled directions and OK result before focus loss.",
        "next": "Continue final MVP evidence/scope reconciliation. Keep the historical observation OPEN; do not claim a root-cause fix. If the symptom recurs, preserve the v5.1 trace and screen state instead of repeating distance trials.",
        "limitations": "Mock tests do not test browser hit-testing/rendering, OS input, every event interleaving, or flashed-image identity. Missing historical events cannot be recovered from these tests."
    }
}
(HERE / "review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("4 retained reports checked; review.json written; original logs unchanged.")
