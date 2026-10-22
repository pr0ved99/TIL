"""Read local sources, ELF/BIN and prior evidence; never build or contact targets."""
import ast
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

PROJECT = Path(__file__).resolve().parents[4]
REPO = PROJECT.parents[1]
OUT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(rel):
    return json.loads((PROJECT / rel).read_text(encoding="utf-8-sig"))


def elf_symbols(path):
    data = path.read_bytes()
    assert data[:6] == b"\x7fELF\x01\x01", "Expected ELF32 little endian"
    header = struct.unpack_from("<16sHHIIIIIHHHHHH", data)
    shoff, entry_size, count = header[6], header[11], header[12]
    assert entry_size == 40 and count > 0
    sections = [struct.unpack_from("<10I", data, shoff + i * entry_size)
                for i in range(count)]
    symbols = {}
    for section in sections:
        if section[1] != 2:  # SHT_SYMTAB
            continue
        strings = sections[section[6]]
        names = data[strings[4]:strings[4] + strings[5]]
        assert section[9] == 16
        for pos in range(section[4], section[4] + section[5], 16):
            name_idx, addr, size, info, other, sec_idx = struct.unpack_from("<IIIBBH", data, pos)
            name = names[name_idx:].split(b"\0", 1)[0].decode("utf-8", "replace")
            if name and 0 < sec_idx < len(sections):
                sec = sections[sec_idx]
                offset = sec[4] + addr - sec[3]
                symbols[name] = {"address": addr, "size": size,
                                 "bytes": data[offset:offset + size]}
    return header[2], symbols


def app_description(blob):
    # Offsets verified against the installed IDF v6.0.2 esp_app_desc.h.
    assert len(blob) >= 256 and struct.unpack_from("<I", blob)[0] == 0xABCD5432
    text = lambda a, b: blob[a:b].split(b"\0", 1)[0].decode("utf-8")
    return {"version": text(16, 48), "project": text(48, 80),
            "compile_time": text(80, 96), "compile_date": text(96, 112),
            "idf": text(112, 144), "embedded_elf_sha256": blob[144:176].hex()}


def function_text(text, name):
    match = re.search(r"\b" + name + r"\([^;{}]*\)\s*\{", text)
    assert match, name
    start = match.end()
    depth = 1
    tokens = r'''"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|//[^\n]*|/\*[\s\S]*?\*/|[{}]'''
    for token in re.finditer(tokens, text[start:]):
        if token[0] == "{":
            depth += 1
        elif token[0] == "}":
            depth -= 1
        if depth == 0:
            return text[match.start():start + token.end()]
    raise AssertionError("Unclosed function " + name)


def main():
    prior = read_json("assets/logs/wifi_link/2026-10-21_session_closeout/source_manifest.json")
    sources = []
    for rel, old_hash in prior["source_sha256"].items():
        p = REPO / rel
        current = digest(p)
        sources.append({"path": str(p.relative_to(PROJECT)), "sha256": current,
                        "matches_2026_10_21_pc_baseline": current == old_hash})
    assert all(x["matches_2026_10_21_pc_baseline"] for x in sources)

    pc_inputs = {}
    pc_reports = []
    for name in ("stm_distance_validation.json", "esp_core_validation.json", "esp_page_validation.json"):
        evidence = read_json("assets/logs/wifi_link/2026-10-21_session_closeout/" + name)
        matched = []
        for field in ("inputs", "source_sha256", "input_sha256"):
            for rel, expected_hash in evidence.get(field, {}).items():
                path = Path(rel)
                if not path.is_absolute():
                    path = REPO / rel if rel.startswith("Projects/") else PROJECT / rel
                assert path.is_file(), str(path)
                assert digest(path) == expected_hash, str(path)
                pc_inputs[str(path.relative_to(PROJECT))] = expected_hash
                matched.append(str(path.relative_to(PROJECT)))
        pc_reports.append({"report": name, "recorded_status": evidence["status"],
                           "matched_input_count": len(matched), "rerun": False})

    old = read_json("assets/logs/wifi_link/2026-10-20_acceptance_image_identity_review/manifest.json")
    artifacts = []
    for item in old["artifacts"]:
        p = PROJECT / item["path"]
        artifacts.append({"path": item["path"], "bytes": p.stat().st_size,
                          "sha256": digest(p), "baseline_2026_10_20_sha256": item["sha256"],
                          "matches_2026_10_20": digest(p) == item["sha256"]})

    stm_path = PROJECT / "03_Firmware/stm32_uart_mvp/Debug/stm32_uart_mvp.elf"
    esp_path = PROJECT / "03_Firmware/esp32_wifi_link/build/esp32_wifi_link.elf"
    machine_stm, stm = elf_symbols(stm_path)
    machine_esp, esp = elf_symbols(esp_path)
    assert machine_stm == 40 and machine_esp == 94
    stm_names = [name for name in stm if name.startswith("distance_move_")]
    assert {"distance_move_init", "distance_move_start", "distance_move_update",
            "distance_move_cancel", "distance_move_output"}.issubset(stm_names)
    assert "HAL_UART_Transmit_IT" in stm

    main_path = PROJECT / "03_Firmware/esp32_wifi_link/main/wifi_link_main.c"
    text = main_path.read_text(encoding="utf-8")
    mode = re.search(r"^#define WIFI_UART_PARTIAL_TEST_MODE (\d+)U", text, re.M)
    assert mode and mode[1] == "0"
    initializer = re.search(r"static const char PAGE\[\] =([\s\S]*?);\n\nstatic ", text)[1]
    literals = re.findall(r'"(?:[^"\\]|\\.)*"', initializer)
    expected_page = "".join(ast.literal_eval(token) for token in literals).encode("utf-8") + b"\0"
    actual_page = esp["PAGE"]["bytes"]
    page_matches = actual_page == expected_page

    binary_path = PROJECT / "03_Firmware/esp32_wifi_link/build/esp32_wifi_link.bin"
    binary = binary_path.read_bytes()
    assert binary[0] == 0xE9
    segments = []
    cursor = 24
    for _ in range(binary[1]):
        address, size = struct.unpack_from("<II", binary, cursor)
        cursor += 8
        assert cursor + size <= len(binary)
        segments.append((address, binary[cursor:cursor + size]))
        cursor += size
    desc = app_description(segments[0][1][:256])
    assert desc["embedded_elf_sha256"] == digest(esp_path)
    assert desc["project"] == "esp32_wifi_link"
    page_addr = esp["PAGE"]["address"]
    page_in_bin = next(blob[page_addr - addr:page_addr - addr + len(actual_page)]
                       for addr, blob in segments
                       if addr <= page_addr and page_addr + len(actual_page) <= addr + len(blob))
    assert page_in_bin == actual_page

    settings = []
    for prior_setting in old["source_settings"]:
        src = PROJECT / prior_setting["source"]
        source_text = src.read_text(encoding="utf-8")
        defines = dict(re.findall(r"^#define\s+(\w+)\s+([^\s/]+)", source_text, re.M))
        selected = {key: defines.get(key) for key in prior_setting["defines"]}
        settings.append({"source": prior_setting["source"], "defines": selected,
                         "same_as_2026_10_20": selected == prior_setting["defines"]})
    assert all(x["same_as_2026_10_20"] for x in settings)

    protocol_rel = "Projects/Tracked_Mobile_Robot/03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c"
    published_old = subprocess.check_output(["git", "show", "f11dabc:" + protocol_rel], cwd=REPO).decode("utf-8").replace("\r\n", "\n")
    current_protocol = (REPO / protocol_rel).read_text(encoding="utf-8")
    impact = []
    for name in ("command_timeout_enforce", "estop_enforce_latch",
                 "estop_latch_and_force_safe", "uart_mvp_process"):
        old_body = function_text(published_old, name)
        new_body = function_text(current_protocol, name)
        impact.append({"function": name, "same_as_f11dabc": old_body == new_body,
                       "same_after_removing_added_distance_cancel":
                       old_body == new_body.replace("    distance_move_cancel(&s_distance_move);\n", "", 1)})

    trials = []
    for goal in (100, 150):
        directory = f"assets/logs/wifi_link/2026-10-21_distance_{goal}mm_air_run01"
        raw = PROJECT / directory / "browser_report.json"
        obs = read_json(directory + "/observations.json")
        assert digest(raw) == obs["raw_sha256"]
        report = json.loads(raw.read_text(encoding="utf-8-sig"))
        def keys_recursive(value):
            if isinstance(value, dict):
                return set(value) | set().union(*(keys_recursive(v) for v in value.values()))
            if isinstance(value, list):
                return set().union(*(keys_recursive(v) for v in value))
            return set()
        identity_keys = sorted(key for key in keys_recursive(report)
                               if re.search(r"firmware|elf_sha|binary_sha|build_hash", key, re.I))
        assert not identity_keys, identity_keys
        trials.append({"goal_mm": goal, "browser_raw_sha256": digest(raw),
                       "observation_raw_hash_matches": True, "identity": obs["identity"],
                       "assessment": obs["assessment"],
                       "report_root_fields": list(report),
                       "contains_firmware_hash_identity": False,
                       "limit": "Browser boot/control/ARM IDs do not identify STM or ESP firmware bytes."})

    report = {"date": "2026-10-22", "test_id": "TK-MVP-03-04",
              "status": "LOCAL_RECONCILIATION_COMPLETE_RUNTIME_IMAGE_HASH_UNCONFIRMED",
              "repository_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO).decode().strip(),
              "sources": sources, "artifacts": artifacts,
              "prior_pc_reports": pc_reports, "prior_pc_input_sha256": pc_inputs,
              "stm_elf": {"machine": machine_stm, "distance_symbols": sorted(stm_names),
                          "async_uart_symbol_present": True,
                          "limit": "Symbol inclusion is not a complete source-to-binary build attestation or target readback."},
              "esp_bin": {"app_description": desc, "embedded_hash_matches_local_elf": True,
                          "elf_page_matches_bin_page": True,
                          "source_page_sha256": hashlib.sha256(expected_page).hexdigest(),
                          "elf_page_sha256": hashlib.sha256(actual_page).hexdigest(),
                          "source_page_matches_local_elf": page_matches,
                          "page_bytes": len(actual_page),
                          "runtime_readback": "NOT_PERFORMED"},
              "source_settings": settings, "trials": trials,
              "published_source_impact": {"comparison_commit": "f11dabc",
                                          "functions": impact,
                                          "new_scheduling": "RX budget64, async TX deadline100ms, distance supervision after E-stop/command timeout.",
                                          "runtime_limit": "Inherited PC mock results and prior physical timeout evidence are distinct."},
              "new_build_flash_motion": False,
              "pc_regression_rerun": False,
              "limits": ["PC PASS is inherited only for hash-matching recorded inputs.",
                         "Compilation version/mtime/boot_id are not firmware-byte identity.",
                         "Prior UART timeout functional evidence is retained; async UART/distance changes require an impact note.",
                         "No temperature/current/ground1m or whole-MVP acceptance."],
              "review_script_sha256": digest(Path(__file__))}
    (OUT / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sources_matched": len(sources), "stm_distance_symbols": len(stm_names),
                      "esp_app": desc, "page_matches_source": page_matches,
                      "trial_hashes_checked": len(trials)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
