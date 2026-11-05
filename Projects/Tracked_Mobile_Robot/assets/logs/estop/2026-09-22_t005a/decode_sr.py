import sys, re, json, zipfile, hashlib, statistics, tempfile
from pathlib import Path
from collections import Counter

src = Path(sys.argv[1])
out = Path(tempfile.mkdtemp(prefix="robot_t005a_analysis_"))
with zipfile.ZipFile(src) as z:
    meta = z.read("metadata").decode()
    rate = re.search(r"samplerate=(\d+(?:\.\d+)?)\s*([kM]?)Hz", meta)
    fs = float(rate[1]) * {"": 1, "k": 1000, "M": 1000000}[rate[2]]
    assert "unitsize=1" in meta
    names = sorted((s for s in z.namelist() if re.fullmatch(r"logic-1-\d+", s)), key=lambda s: int(s.rsplit("-", 1)[1]))
    raw = b"".join(z.read(s) for s in names)
n = len(raw)
report = dict(source=str(src), sha256=hashlib.sha256(src.read_bytes()).hexdigest(), fs=fs, samples=n, duration_s=n/fs, channels={})
spans = {}
for ch in (0, 1, 2):
    bits = raw.translate(bytes((v >> ch) & 1 for v in range(256)))
    highs = [(m.start(), m.end()) for m in re.finditer(b"\x01+", bits)]
    spans[ch] = highs
    rec = dict(high_runs=len(highs), high_samples=sum(b-a for a,b in highs), high_at_start=bool(bits[0]), high_at_end=bool(bits[-1]))
    if ch == 0:
        rec["high_intervals_s"] = [[a/fs,b/fs] for a,b in highs]
        lows = [(m.start(),m.end()) for m in re.finditer(b"\x00+", bits)]
    else:
        groups = []
        for a,b in highs:
            if not groups or a-groups[-1][-1][1] > fs*0.00025:
                groups.append([])
            groups[-1].append((a,b))
        rec["bursts"] = []
        for g in groups:
            period = (g[-1][0]-g[0][0])/(len(g)-1) if len(g)>1 else None
            widths = [b-a for a,b in g[:-1] if a>0 and b<n]
            rec["bursts"].append(dict(start_s=g[0][0]/fs, end_s=g[-1][1]/fs, pulses=len(g), mean_hz=fs/period if period else None, mean_duty_percent=100*statistics.mean(widths)/period if period and widths else None))
    report["channels"][f"D{ch}"] = rec
assertion = next((a for a,b in spans[0] if b-a >= fs*.001), None)
if assertion is not None:
    release = next((a for a,b in lows if a>=assertion and b-a>=fs*.001), None)
    hold_end = release if release is not None else n
    falls = [b for ch in (1,2) for a,b in spans[ch] if b<=hold_end and b<n]
    last = max(falls) if falls else None
    next_highs = [max(a,release) for ch in (1,2) for a,b in spans[ch] if release is not None and b>release]
    check = dict(first_pc7_high_s=spans[0][0][0]/fs, pc7_stable_high_s=assertion/fs, pc7_stable_release_s=release/fs if release is not None else None, last_pwm_fall_before_release_s=last/fs if last is not None else None, first_pwm_after_release_s=min(next_highs)/fs if next_highs else None)
    if last is not None:
        check["last_fall_minus_first_pc7_us"] = (last-spans[0][0][0])*1e6/fs
        check["last_fall_minus_stable_pc7_us"] = (last-assertion)*1e6/fs
    check["high_samples_assert_plus_200ms_to_release"] = {f"D{ch}":sum(max(0,min(b,hold_end)-max(a,assertion+int(fs*.2))) for a,b in spans[ch]) for ch in (1,2)}
    report["stop_check"] = check
spb = fs/115200
all_lines = {}
for ch in (4,5):
    bits = raw.translate(bytes((v>>ch)&1 for v in range(256)))
    lines=[]; buf=bytearray(); start=None; cursor=0; bad=0; decoded=0
    for m in re.finditer(b"\x01\x00", bits):
        a=m.start()+1
        if a<cursor or a+10*spb>=n or bits[round(a+.5*spb)]!=0:
            continue
        if bits[round(a+9.5*spb)]!=1:
            bad+=1;cursor=a+9.6*spb;continue
        v=sum(bits[round(a+(1.5+j)*spb)]<<j for j in range(8))
        cursor=a+9.6*spb;decoded+=1
        if start is None:start=a/fs
        if v==10:
            lines.append(dict(start_s=start,end_s=(a+10*spb)/fs,text=bytes(buf).decode("ascii","backslashreplace").rstrip("\r")))
            buf.clear();start=None
        else:buf.append(v)
    all_lines[ch]=lines
    (out/f"D{ch}_lines.json").write_text(json.dumps(lines,indent=2),encoding="utf-8")
    (out/f"D{ch}.txt").write_text("".join(f"{v['start_s']:.9f}\t{v['end_s']:.9f}\t{v['text']}\n" for v in lines),encoding="utf-8")
    counts=Counter(); tels=[]; events=[]; selected=[]; prev=None
    for line in lines:
        t=line["text"];kind=t.split(",",1)[0]
        if kind in ("TEL","CMD","ARM","DISARM","PING","PONG","ESTOP_RESET","ACK","ERR"):
            counts[kind]+=1
        fields=dict(re.findall(r"([A-Za-z_]+)=([^,\s*]+)",t))
        if kind=="TEL":
            tels.append(fields);state=(fields.get("state"),fields.get("reason"))
            if state!=prev:events.append(line);prev=state
        if kind in ("ERR","ARM","DISARM","ESTOP_RESET") or (kind=="ACK" and fields.get("type") in ("ARM","DISARM","ESTOP_RESET")):
            selected.append(line)
    keys=("state","reason","left_pwm","right_pwm","left_cps","right_cps","err","drop")
    report["channels"][f"D{ch}"]=dict(decoded_bytes=decoded,invalid_stop_bits=bad,lines=len(lines),trailing_partial_bytes=len(buf),message_counts=dict(counts),telemetry_distributions={k:dict(Counter(t[k] for t in tels if k in t)) for k in keys if any(k in t for t in tels)},state_transitions=events,selected_commands_responses=selected,first_lines=lines[:1],last_lines=lines[-1:])
response_ch = next((ch for ch in (4,5) if report["channels"][f"D{ch}"]["message_counts"].get("TEL",0)),None)
if response_ch is not None:
    command_ch=9-response_ch
    report["uart_roles"]={f"D{response_ch}":"STM32 TX / ESP32 RX (inferred from TEL/ACK/ERR)",f"D{command_ch}":"ESP32 TX / STM32 RX (inferred from commands)"}
    commands=[v for v in all_lines[command_ch] if v["text"].split(",",1)[0] in ("CMD","ARM","DISARM","ESTOP_RESET","PING")]
    responses={re.search(r"\bseq=(\d+)",v["text"])[1]:v for v in all_lines[response_ch] if v["text"].startswith(("ACK,","ERR,","PONG,")) and re.search(r"\bseq=(\d+)",v["text"])}
    missing=[];mismatch=[]
    for v in commands:
        seq=re.search(r"\bseq=(\d+)",v["text"])[1];kind=v["text"].split(",",1)[0]
        if seq not in responses:missing.append(seq)
        elif kind!="PING" and f"type={kind}," not in responses[seq]["text"]:mismatch.append(seq)
    report["command_response_check"]=dict(complete_commands=len(commands),matched=len(commands)-len(missing),missing_seqs=missing,type_mismatches=mismatch)
report["limits"]=["This digital capture contains no analog MDD rail voltage.","A PWM last falling edge before PC7 assertion does not measure negative or exact-zero shutdown latency.","Physical operating steps and analog measurements require operator reports."]
(out/"summary.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("ANALYSIS_DIR",out)
print(json.dumps(report,indent=2))
