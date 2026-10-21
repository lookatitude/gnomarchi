#!/usr/bin/env python3
"""Execute tests/parity/workflows/catalog.yaml against Omarchy / gnomarchi VMs."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "tests/parity/workflows/catalog.json"
RESULTS = ROOT / "docs/parity/dual-vm-results"


def load_catalog(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    if yaml is not None:
        return yaml.safe_load(text)
    # Prefer generated JSON sibling when PyYAML is unavailable
    sibling = path.with_suffix(".json")
    if sibling.is_file():
        return json.loads(sibling.read_text(encoding="utf-8"))
    raise SystemExit(
        "catalog must be JSON, or install PyYAML (python-yaml) for .yaml catalogs"
    )

def ssh_base(side: str, catalog: dict) -> list[str]:
    d = catalog["defaults"]
    if side == "omarchy":
        cfg = d["omarchy_ssh"]
        key = os.environ.get("OMARCHY_SSH_KEY")
        if not key:
            keys = sorted(
                Path("/home/miguelp/VMs/omarchy-test/state").glob("vm.*/id_ed25519"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            key = str(keys[0]) if keys else ""
        cmd = [
            "ssh",
            "-p",
            str(cfg["port"]),
            "-o",
            "StrictHostKeyChecking=accept-new",
            "-o",
            "UserKnownHostsFile=/tmp/gnomarchi-omarchy-known_hosts",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=8",
        ]
        if key:
            cmd += ["-i", key]
        cmd.append(f"{cfg['user']}@{cfg['host']}")
        return cmd
    cfg = d["gnomarchi_ssh"]
    return [
        "ssh",
        "-p",
        str(cfg["port"]),
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "UserKnownHostsFile=/tmp/gnomarchi-gnom-known_hosts",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=8",
        f"{cfg['user']}@{cfg['host']}",
    ]


def remote(ssh: list[str], script: str, timeout: int) -> subprocess.CompletedProcess[str]:
    # Pass script via stdin to avoid nested-quote / newline breakage over ssh bash -lc.
    # Forward host PARITY_CAPTURE so guest steps gated on that env see it.
    parity = os.environ.get("PARITY_CAPTURE", "").strip()
    wrapper = (
        "export DISPLAY=${DISPLAY:-:0}; "
        "export DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/$(id -u)/bus}; "
        f"export PARITY_CAPTURE={json.dumps(parity)}; "
        "bash -s"
    )
    return subprocess.run(
        ssh + [wrapper],
        input=script,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def expect_rc_ok(rc: int, expect) -> bool:
    if expect is None:
        return rc == 0
    if isinstance(expect, list):
        return rc in expect
    return rc == expect


def env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def run_step(ssh: list[str], step: dict, timeout: int) -> tuple[bool, str]:
    when = step.get("when_env")
    if when and not env_truthy(str(when)):
        return True, f"skipped:{when}"
    step_timeout = int(step.get("timeout_sec", timeout))

    # Host-side proof file (repo-relative). Used by theme.proof.* when PARITY_CAPTURE=1.
    if "host_file" in step:
        path = ROOT / step["host_file"]
        ok = path.is_file() and path.stat().st_size > 1000
        return ok, str(path)

    # Host-side command (list or shell string), cwd=repo root.
    if "host_run" in step:
        hr = step["host_run"]
        if isinstance(hr, list):
            argv = [str(x) for x in hr]
        else:
            argv = ["bash", "-lc", str(hr)]
        proc = subprocess.run(
            argv,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=step_timeout,
            check=False,
        )
        ok = expect_rc_ok(proc.returncode, step.get("expect_rc", 0))
        detail = (proc.stdout + proc.stderr).strip()[:400]
        return ok, detail

    cmd = step["run"]
    if step.get("background"):
        settle = int(step.get("settle_ms", 1000)) / 1000.0
        pat = step.get("assert_pgrep", ".")
        stop = bool(step.get("stop", True))
        # Single-quoted pattern for pgrep -af; cmd runs via bash -c
        wrapper = (
            "set +e\n"
            f"bash -c {json.dumps(cmd)} >/tmp/gnomarchi-wf.out 2>/tmp/gnomarchi-wf.err &\n"
            "BPID=$!\n"
            f"sleep {settle}\n"
            f"pgrep -af {json.dumps(pat)} >/tmp/gnomarchi-wf.pgrep\n"
            "PG=$?\n"
            "if [[ $PG -ne 0 ]] && ! kill -0 $BPID 2>/dev/null "
            "&& [[ ! -s /tmp/gnomarchi-wf.out && ! -s /tmp/gnomarchi-wf.err ]]; then\n"
            f"  echo background_assert_failed:{pat} >&2\n"
            "  exit 1\n"
            "fi\n"
            + (
                f"pkill -f {json.dumps(pat)} 2>/dev/null || true\n"
                "kill $BPID 2>/dev/null || true\n"
                "sleep 0.3\n"
                if stop
                else ""
            )
            + "exit 0\n"
        )
        proc = remote(ssh, wrapper, step_timeout)
        ok = proc.returncode == 0
        detail = (proc.stdout + proc.stderr).strip()[:400]
        return ok, detail

    proc = remote(ssh, cmd, step_timeout)
    ok = expect_rc_ok(proc.returncode, step.get("expect_rc", 0))
    if ok and "expect_stdout_gte_int" in step:
        try:
            val = int((proc.stdout or "").strip().splitlines()[-1])
            ok = val >= int(step["expect_stdout_gte_int"])
        except (ValueError, IndexError):
            ok = False
    if ok and "expect_stdout_regex" in step:
        ok = re.search(step["expect_stdout_regex"], proc.stdout or "") is not None
    detail = (proc.stdout + proc.stderr).strip()[:400]
    return ok, detail


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    ap.add_argument("--only", help="comma-separated workflow id prefixes")
    ap.add_argument("--side", choices=["gnomarchi", "omarchy", "both"], default="both")
    ap.add_argument("--fail-fast", action="store_true")
    args = ap.parse_args()

    catalog = load_catalog(args.catalog)
    workflows = catalog.get("workflows") or []
    prefixes = [p.strip() for p in (args.only or "").split(",") if p.strip()]

    RESULTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = RESULTS / f"workflows-{stamp}.jsonl"
    summary_path = RESULTS / "workflows-latest.json"

    timeout = int(catalog.get("defaults", {}).get("timeout_sec", 45))
    passed = failed = skipped = 0
    rows = []

    with report_path.open("w", encoding="utf-8") as report:
        for wf in workflows:
            wid = wf["id"]
            side = wf.get("side", "gnomarchi")
            if args.side != "both" and side != args.side:
                skipped += 1
                continue
            if prefixes and not any(wid.startswith(p) for p in prefixes):
                skipped += 1
                continue

            ssh = ssh_base(side, catalog)
            # reachability
            ping = remote(ssh, "echo ok", 15)
            if ping.returncode != 0:
                failed += 1
                row = {"id": wid, "side": side, "status": "fail", "error": "ssh unreachable"}
                report.write(json.dumps(row) + "\n")
                rows.append(row)
                print(f"FAIL  [{side}] {wid} — ssh unreachable")
                if args.fail_fast:
                    break
                continue

            ok_all = True
            details = []
            for i, step in enumerate(wf.get("steps") or []):
                ok, detail = run_step(ssh, step, timeout)
                details.append({"step": i, "ok": ok, "detail": detail})
                if not ok:
                    ok_all = False
                    break

            status = "pass" if ok_all else "fail"
            if ok_all:
                passed += 1
                print(f"PASS  [{side}] {wid}")
            else:
                failed += 1
                print(f"FAIL  [{side}] {wid} — {details[-1].get('detail','')[:200]}")
            row = {"id": wid, "side": side, "feature": wf.get("feature"), "status": status, "steps": details}
            report.write(json.dumps(row) + "\n")
            rows.append(row)
            if not ok_all and args.fail_fast:
                break

    summary = {
        "stamp": stamp,
        "pass": passed,
        "fail": failed,
        "skipped": skipped,
        "report": str(report_path),
        "catalog": str(args.catalog),
        "workflow_count": len(workflows),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"\nsummary pass={passed} fail={failed} skipped={skipped} report={report_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
