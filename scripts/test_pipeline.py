"""
FusionAL Pipeline Test v0.1
Simulates a container failure to validate the full pipeline.
Run from FusionAL/scripts/:  python test_pipeline.py --mock --skip-notion
"""

import sys
import json
import logging
import argparse
import asyncio
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("test_pipeline")

parser = argparse.ArgumentParser()
parser.add_argument("--live",        action="store_true", help="Run executor live (not dry run)")
parser.add_argument("--skip-notion", action="store_true", help="Skip Notion reporter")
parser.add_argument("--mock",        action="store_true", help="Mock all API calls — no credits needed")
parser.add_argument("--preset",      default="mid", choices=["low", "mid", "high"])
parser.add_argument("--server",      default="content-automation-mcp")
args = parser.parse_args()

sys.path.insert(0, str(Path(__file__).parent))
import think_tank_trigger as tt
import action_executor as executor
if not args.skip_notion:
    import notion_reporter as reporter

SERVERS = [
    {"name": "fusional-mcp",              "port": 8009, "container": "fusional-mcp",              "health_path": "/health", "critical": True},
    {"name": "business-intelligence-mcp", "port": 8101, "container": "business-intelligence-mcp", "health_path": "/health", "critical": False},
    {"name": "api-integration-hub",       "port": 8102, "container": "api-integration-hub",       "health_path": "/health", "critical": False},
    {"name": "content-automation-mcp",    "port": 8103, "container": "content-automation-mcp",    "health_path": "/health", "critical": False},
    {"name": "intelligence-mcp",          "port": 8104, "container": "intelligence-mcp",           "health_path": "/health", "critical": False},
]

PRESET_MAP = {
    "low":  tt.ReasoningPreset.LOW,
    "mid":  tt.ReasoningPreset.MID,
    "high": tt.ReasoningPreset.HIGH,
}

def sep(label):
    print(f"\n{'='*60}\n  {label}\n{'='*60}\n")

def mock_think_tank(fault):
    log.info("[MOCK] Returning synthetic Think Tank result — no API calls")
    return tt.ThinkTankResult(
        verdict="APPROVED",
        action_plan=[
            f"check logs for {fault.server_name}",
            f"restart container {fault.server_name}",
            f"inspect container {fault.server_name}",
        ],
        issues=["[MOCK] Synthetic test run — no real issues"],
        escalate=False,
        escalation_reason="",
        raw_diagnoses=[
            {"agent_role": "infrastructure",      "root_cause_hypothesis": "[MOCK] Container OOM killed",         "confidence": 8},
            {"agent_role": "logic_analyzer",      "root_cause_hypothesis": "[MOCK] Memory limit exceeded",        "confidence": 7},
            {"agent_role": "recovery_specialist", "root_cause_hypothesis": "[MOCK] Restart should recover state", "confidence": 9},
        ],
    )

def run_test():
    sep("PHASE 1 — Simulated Fault Event")
    print(f"  Target server : {args.server}")
    print(f"  Preset        : {args.preset}")
    print(f"  Executor mode : {'LIVE' if args.live else 'DRY RUN'}")
    print(f"  Notion        : {'SKIP' if args.skip_notion else 'ENABLED'}")
    print(f"  API calls     : {'MOCKED' if args.mock else 'REAL'}")

    fault = tt.FaultEvent(
        server_name=args.server,
        fault_type="crash",
        detail="Simulated: health check failed + docker restart failed",
        trigger="restart_failed",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    sep("PHASE 2 — Think Tank")
    if args.mock:
        print("  [MOCK MODE] Skipping API calls\n")
        result = mock_think_tank(fault)
    else:
        print("  Firing 3 agents + Logic Observer...")
        print("  (This will take 30-90s depending on preset)\n")
        result = asyncio.run(tt.run_think_tank(
            fault=fault,
            servers=SERVERS,
            preset=PRESET_MAP[args.preset],
        ))

    sep("PHASE 3 — Think Tank Result")
    print(f"  Verdict    : {result.verdict}")
    print(f"  Escalate   : {result.escalate}")
    if result.escalation_reason:
        print(f"  Reason     : {result.escalation_reason}")
    print(f"  Issues     : {result.issues}")
    print(f"\n  Action Plan:")
    for i, step in enumerate(result.action_plan):
        print(f"    {i+1}. {step}")

    sep("PHASE 4 — Action Executor")
    exec_results_raw = None
    if result.verdict == "APPROVED" and result.action_plan and not result.escalate:
        print(f"  Mode: {'LIVE' if args.live else 'DRY RUN'}\n")
        exec_results = executor.execute_plan(
            action_plan=result.action_plan,
            dry_run=not args.live,
            stop_on_failure=False,
        )
        print(executor.execution_summary(exec_results))
        exec_results_raw = [r.__dict__ for r in exec_results]
    else:
        print(f"  Skipped — verdict={result.verdict}, escalate={result.escalate}")

    sep("PHASE 5 — Notion Reporter")
    if args.skip_notion:
        print("  Skipped (--skip-notion flag)")
    else:
        print("  Posting to Incident Log...")
        url = reporter.report_think_tank_result(
            fault_server=fault.server_name,
            fault_type=fault.fault_type,
            trigger_reason=fault.trigger,
            verdict=result.verdict,
            action_plan=result.action_plan,
            exec_results=exec_results_raw,
            issues=result.issues,
            escalate=result.escalate,
            escalation_reason=result.escalation_reason,
        )
        print(f"  {'OK: ' + url if url else 'FAILED — check NOTION_TOKEN'}")

    sep("TEST COMPLETE")
    print("  Logs: FusionAL/logs/think_tank_log.json + execution_log.json\n")


if __name__ == "__main__":
    run_test()
