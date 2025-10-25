#!/usr/bin/env python3
import argparse, re, sys, time
from datetime import datetime, timezone, timedelta
from collections import deque

# Patterns (keep these simple & resilient)
TS_RE   = re.compile(r'^\[(?P<ts>[^]]+)\]')
COMMIT_RE = re.compile(r'\bCommitting\b.*?height:\s*(?P<height>\d+)', re.IGNORECASE)
QC_RE   = re.compile(r'Processing new Commit QC', re.IGNORECASE)
PROP_RE = re.compile(r'Proposing batches', re.IGNORECASE)
FINAL_RE= re.compile(r'Successfully finalized', re.IGNORECASE)

def parse_ts(ts_str: str) -> datetime:
    """
    Accepts timestamps like:
      2025-10-25T18:23:19.084110Z+00:00
      2025-10-25T18:23:19.084110+00:00
      2025-10-25T18:23:19.084110Z
    Turns them into aware UTC datetimes. Like coffee, but for strings. ☕
    """
    s = ts_str.strip()
    # Normalize odd "Z+00:00" or bare "Z"
    s = s.replace('Z+00:00', '+00:00')
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        # Be forgiving — if timestamp is weird, use now; log parsers shouldn’t be divas
        return datetime.now(timezone.utc)

def scan_lines(lines, commit_history_max=10):
    """
    Walk the lines and collect recent commit heights, timestamps, and QC events.
    Like a detective, but faster and less trenchcoat. 🕵️
    """
    last_commit_ts = None
    last_commit_height = None
    commit_heights = deque(maxlen=commit_history_max)
    commit_events = []   # (ts, height)
    qc_events = []       # (ts)
    finalize_events = [] # (ts)
    propose_events = []  # (ts)

    for line in lines:
        m_ts = TS_RE.search(line)
        if not m_ts:
            continue
        ts = parse_ts(m_ts.group('ts'))

        if COMMIT_RE.search(line):
            m_h = COMMIT_RE.search(line)
            if m_h:
                h = int(m_h.group('height'))
                last_commit_ts = ts
                last_commit_height = h
                commit_heights.append(h)
                commit_events.append((ts, h))
            continue

        if QC_RE.search(line):
            qc_events.append(ts)
            continue

        if FINAL_RE.search(line):
            finalize_events.append(ts)
            continue

        if PROP_RE.search(line):
            propose_events.append(ts)
            continue

    return {
        'last_commit_ts': last_commit_ts,
        'last_commit_height': last_commit_height,
        'commit_heights': list(commit_heights),
        'commit_events': commit_events,
        'qc_events': qc_events,
        'finalize_events': finalize_events,
        'propose_events': propose_events,
    }

def evaluate(state, now_utc, commit_stall_secs, qc_to_commit_warn_secs, require_increasing_count):
    """
    Turn parsed state into a verdict. Like a judge, but nicer. ⚖️
    """
    issues = []
    warnings = []

    # 1) Commit freshness
    if state['last_commit_ts'] is None:
        issues.append("No commits observed in the scanned window.")
    else:
        delta = (now_utc - state['last_commit_ts']).total_seconds()
        if delta > commit_stall_secs:
            issues.append(f"Last commit is stale: {int(delta)}s > {commit_stall_secs}s.")

    # 2) Heights strictly increasing (last N)
    heights = state['commit_heights']
    if len(heights) >= max(2, require_increasing_count):
        recent = heights[-require_increasing_count:]
        for i in range(1, len(recent)):
            if recent[i] <= recent[i-1]:
                issues.append(f"Commit heights not strictly increasing in last {require_increasing_count}: {recent}.")
                break

    # 3) QC to Commit lag (heuristic)
    # If a recent QC exists with no newer commit after it for too long => warn
    if state['qc_events']:
        last_qc = state['qc_events'][-1]
        last_commit = state['last_commit_ts']
        if last_commit is None or last_commit < last_qc:
            gap = (now_utc - last_qc).total_seconds()
            if gap > qc_to_commit_warn_secs:
                warnings.append(f"Recent QC without commit for {int(gap)}s (>{qc_to_commit_warn_secs}s).")

    # Build message + exit code
    if issues:
        code = 2
        level = "CRITICAL"
    elif warnings:
        code = 1
        level = "WARNING"
    else:
        code = 0
        level = "OK"

    summary = {
        'status': level,
        'last_commit_ts': state['last_commit_ts'].isoformat() if state['last_commit_ts'] else None,
        'last_commit_height': state['last_commit_height'],
        'recent_commit_heights': heights[-require_increasing_count:] if heights else [],
        'recent_qc_count': len(state['qc_events']),
        'recent_finalize_count': len(state['finalize_events']),
    }

    # Friendly one-line status (because pagers hate novels)
    msg = f"{level} | last_commit={summary['last_commit_ts']} height={summary['last_commit_height']} commits_tail={summary['recent_commit_heights']} QCs={summary['recent_qc_count']} finalized={summary['recent_finalize_count']}"
    if issues:
        msg += " | " + " ; ".join(issues)
    if warnings:
        msg += " | " + " ; ".join(warnings)

    return code, msg

def read_last_n(path, n_lines):
    # Efficient-ish tail: read blocks from the end. Like reverse park, but with bytes. 🚗
    chunk = 8192
    data = b""
    with open(path, 'rb') as f:
        f.seek(0, 2)
        size = f.tell()
        pos = size
        while pos > 0 and data.count(b'\n') <= n_lines:
            read_size = min(chunk, pos)
            pos -= read_size
            f.seek(pos)
            data = f.read(read_size) + data
    return data.decode('utf-8', errors='replace').splitlines()[-n_lines:]

def follow(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.25)
                continue
            yield line

def main():
    ap = argparse.ArgumentParser(description="Supra log healthcheck (commits/QC/height monotonicity).")
    ap.add_argument("--log", required=True, help="Path to supra.log")
    ap.add_argument("--mode", choices=["oneshot", "follow"], default="oneshot",
                    help="oneshot: scan recent lines and exit; follow: stream and periodically report.")
    ap.add_argument("--scan-lines", type=int, default=5000, help="Number of trailing lines to scan in oneshot.")
    ap.add_argument("--commit-stall-secs", type=int, default=60, help="Critical if no commit within this many seconds.")
    ap.add_argument("--qc-to-commit-warn-secs", type=int, default=20, help="Warn if QC seen but no commit after this many seconds.")
    ap.add_argument("--require-increasing-count", type=int, default=5, help="Require last N commit heights to be strictly increasing.")
    ap.add_argument("--report-interval-secs", type=int, default=15, help="In follow mode, how often to emit a status line.")
    args = ap.parse_args()

    if args.mode == "oneshot":
        lines = read_last_n(args.log, args.scan_lines)
        state = scan_lines(lines, commit_history_max=max(10, args.require_increasing_count))
        code, msg = evaluate(state, datetime.now(timezone.utc), args.commit_stall_secs,
                             args.qc_to_commit_warn_secs, args.require_increasing_count)
        print(msg)
        sys.exit(code)

    else:
        # Follow mode: keep a rolling buffer and report periodically, like a helpful parrot with a stopwatch. 🦜⏱️
        buf = deque(maxlen=max(20000, args.scan_lines))
        next_report = time.time() + args.report_interval_secs
        for line in follow(args.log):
            buf.append(line)
            now = time.time()
            if now >= next_report:
                state = scan_lines(buf, commit_history_max=max(10, args.require_increasing_count))
                code, msg = evaluate(state, datetime.now(timezone.utc), args.commit_stall_secs,
                                     args.qc_to_commit_warn_secs, args.require_increasing_count)
                print(msg, flush=True)
                next_report = now + args.report_interval_secs
                # Optional: non-zero code could also print to stderr — but we keep calm and carry on.