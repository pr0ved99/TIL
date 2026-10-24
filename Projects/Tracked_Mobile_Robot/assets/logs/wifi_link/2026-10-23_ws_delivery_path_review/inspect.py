"""Offline source identity + two retained burst windows; no board/network access."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    main_path = ROOT / "03_Firmware/esp32_wifi_link/main/wifi_link_main.c"
    observer_path = ROOT / "assets/logs/wifi_link/2026-10-23_ground_distance_preparation/console_encoder_observe_1m.js"
    build = ROOT / "03_Firmware/esp32_wifi_link/build/project_description.json"
    build_description = json.loads(build.read_text(encoding="utf-8"))
    idf = Path(build_description["idf_path"])
    idf_version = subprocess.check_output(
        ["git", "-C", str(idf), "describe", "--tags", "--always", "--dirty"],
        text=True,
    ).strip()
    sources = [
        (main_path, [(816, 831), (1094, 1135), (1250, 1337), (1361, 1367),
                     (772, 795), (2615, 2638), (2735, 2777), (2909, 2912)]),
        (observer_path, [(46, 60), (87, 101)]),
        (idf / "components/esp_http_server/src/httpd_ws.c", [(394, 460)]),
        (idf / "components/esp_http_server/src/httpd_main.c", [(81, 96), (142, 172), (224, 230), (298, 314)]),
        (idf / "components/esp_http_server/src/httpd_txrx.c", [(788, 799)]),
        (idf / "components/esp_http_server/src/httpd_sess.c", [(203, 212)]),
    ]
    identities = []
    for path, ranges in sources:
        lines = path.read_text(encoding="utf-8").splitlines()
        identities.append({
            "path": path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            "sha256": sha(path),
            "excerpts": [{"first_line": lo, "last_line": hi,
                          "text": "\n".join(lines[lo - 1:hi])} for lo, hi in ranges],
        })
    bursts = []
    for name in ["2026-10-23_forward_auto_disarm_run01", "2026-10-23_left_auto_disarm_run01"]:
        folder = ROOT / "assets/logs/wifi_link" / name
        raw_path = folder / "browser_report.json.gz"
        trigger_path = folder / "trigger_snapshot.json"
        raw = json.loads(gzip.decompress(raw_path.read_bytes()))
        trigger = json.loads(trigger_path.read_text(encoding="utf-8"))
        tel = raw["telemetry"]
        first = next(i for i, row in enumerate(tel) if row["ms"] > trigger["ms"])
        window = []
        for row in tel[first:]:
            if row["ms"] - tel[first]["ms"] > 5:
                break
            window.append(row)
        keys = ["ms", "gap_ms", "boot_id", "esp_uptime_ms", "esp_step_ms", "stm_age_ms", "tel_count"]
        bursts.append({
            "source": raw_path.relative_to(ROOT).as_posix(),
            "source_sha256": sha(raw_path), "trigger_sha256": sha(trigger_path),
            "stop_ms": trigger["ms"],
            "selection": "First TEL after saved stop, then TEL within 5 ms of that first receive",
            "previous_tel": {k: tel[first - 1].get(k) for k in keys},
            "rows": [{k: row.get(k) for k in keys} for row in window],
            "frames": len(window),
            "browser_gap_before_burst_ms": round(window[0]["gap_ms"], 3),
            "browser_burst_span_ms": round(window[-1]["ms"] - window[0]["ms"], 3),
            "esp_generation_span_ms": window[-1]["esp_uptime_ms"] - window[0]["esp_uptime_ms"],
            "esp_generation_steps_ms": [row["esp_uptime_ms"] - prev["esp_uptime_ms"]
                                        for prev, row in zip(window, window[1:])],
        })
    config_path = ROOT / "03_Firmware/esp32_wifi_link/sdkconfig"
    selected = [line for line in config_path.read_text(encoding="utf-8").splitlines()
                if line.startswith(("CONFIG_FREERTOS_HZ=", "# CONFIG_HTTPD_QUEUE_WORK_BLOCKING ",
                                    "CONFIG_HTTPD_WS_SUPPORT="))]
    result = {
        "date": "2026-10-23", "scope": "ACC-COM-01 static path review and observation design",
        "status": "STATIC_REVIEW_COMPLETE_CAUSE_OPEN_INSTRUMENTATION_NOT_IMPLEMENTED",
        "project_source": identities, "idf_git_describe": idf_version,
        "build_description_sha256": sha(build), "sdkconfig_sha256": sha(config_path),
        "selected_config": selected,
        "identity_limit": "Local build metadata and installed SDK, not a new board image readback",
        "burst_windows": bursts,
        "interpretation": "Generation continued across the sampled frames; downstream buffering/delivery is supported, but send-call, network, host stack and browser dispatch are not separated.",
        "proposed_browser_ring": {"rows": 8192, "numeric_bytes_per_row": 64, "bytes": 524288,
                                  "implemented": False},
        "proposed_esp_ring": {"rows": 512, "record_bytes_budget": 64, "bytes": 32768,
                              "implemented": False, "layout_and_runtime_budget_validated": False},
        "hardware_action": False, "firmware_edited": False, "build_or_flash": False,
        "safety_limits_changed": False, "cause_resolved": False,
    }
    (HERE / "review.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"idf": idf_version, "sources": len(identities),
                      "bursts": [{k: b[k] for k in ["frames", "browser_gap_before_burst_ms",
                          "browser_burst_span_ms", "esp_generation_span_ms"]} for b in bursts]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
