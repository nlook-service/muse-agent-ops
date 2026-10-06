#!/usr/bin/env python3
"""
에이전트 라우터 (muse-agent-ops 범용 버전) — 외부 에이전트에 작업을 넘기고 결과를 기다린다.

사용법:
    python3 handoff.py --brief 브리프.md --expect 결과파일 [--agent claude] [--timeout-min 10]
    python3 handoff.py --brief 브리프.md --expect 결과파일 --agent chatgpt
    python3 handoff.py --check --expect 결과파일 --since 2026-10-06T15:50:00  # 상태만 확인
    python3 handoff.py --dry-run --brief 브리프.md  # 전달 내용 미리보기 (실제 전송 안 함)

종료 코드:
    0 = DELIVERED (결과 파일 확인됨)
    2 = TIMEOUT (무응답 — Muse가 직접 처리할 것)
    3 = BUSY (세션 작업 중 — Muse가 판단할 것)
    4 = NOT_CONFIGURED (에이전트 미설정)
"""
import argparse, os, subprocess, sys, time
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    sys.exit("pyyaml 필요: pip install pyyaml")

HERE = os.path.dirname(os.path.abspath(__file__))


def load_config(path):
    if not path or not os.path.exists(path):
        sys.exit("config.yaml 경로를 --config 로 지정하세요 (예시는 config.example.yaml)")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def tmux(cmd, *args):
    p = subprocess.run(["tmux"] + [cmd] + list(args), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def claude_idle(session, marker):
    rc, out, _ = tmux("capture-pane", "-t", session, "-p")
    if rc != 0:
        return None  # 세션 없음
    tail = "\n".join(out.splitlines()[-6:])
    return marker in tail


def deliver_claude(session, marker, brief, expect):
    idle = claude_idle(session, marker)
    if idle is None:
        print("NO_SESSION")
        return 4
    if not idle:
        print("BUSY: 세션이 작업 중 — 주입하지 않음")
        return 3
    msg = (f"작업 요청이야. 브리프를 읽고 작업해줘: {brief} "
           f"결과는 {expect} 파일로 저장해줘. 끝나면 한두 문단으로 보고해줘.")
    tmux("send-keys", "-t", session, msg)
    time.sleep(1)
    tmux("send-keys", "-t", session, "C-m")
    print(f"SENT to tmux session '{session}'")
    return 0


def deliver_chatgpt(command, brief, expect, timeout_min):
    with open(brief, encoding="utf-8") as f:
        prompt = f.read()
    # codex exec: stdin으로 프롬프트, stdout을 결과 파일에
    with open(expect, "w", encoding="utf-8") as out:
        p = subprocess.run([command, "exec", "-"], input=prompt,
                           capture_output=True, text=True,
                           timeout=timeout_min * 60)
    out.write(p.stdout)
    if p.returncode == 0 and os.path.getsize(expect) > 0:
        print(f"DELIVERED via {command} exec -> {expect}")
        return 0
    print(f"CHATGPT_FAILED rc={p.returncode}: {p.stderr[:300]}")
    return 2


def wait_for_file(path, since_ts, timeout_min, poll_sec):
    deadline = time.time() + timeout_min * 60
    while time.time() < deadline:
        if os.path.exists(path) and os.path.getmtime(path) >= since_ts:
            print(f"DELIVERED: {path}")
            return 0
        time.sleep(poll_sec)
    print(f"TIMEOUT: {timeout_min}분 내 결과 없음 — Muse가 직접 처리할 것")
    return 2


def get_muse_usage():
    """subscription-status status 출력에서 주간 한도 사용률(%)을 읽는다."""
    try:
        p = subprocess.run(["subscription-status", "status"],
                           capture_output=True, text=True, timeout=30)
        import re
        m = re.search(r"Usage:\s*(\d+)%", p.stdout)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


def ready_external(cfg, prefer=None):
    """사용 가능한 외부 에이전트 목록 (선호 순서)."""
    agents = cfg["agents"]
    order = []
    if prefer in ("claude", "chatgpt"):
        order.append(prefer)
    default = cfg.get("default_external", "claude")
    for name in [default, "claude", "chatgpt"]:
        if name not in order:
            order.append(name)
    return [n for n in order if agents.get(n, {}).get("status") == "ready"]


def suggest(cfg, weight, capability, task):
    usage = get_muse_usage()
    lb = cfg.get("load_balancing", {})
    high = lb.get("muse_usage_high_threshold", 70)
    critical = lb.get("muse_usage_critical_threshold", 90)
    usage_str = f"{usage}%" if usage is not None else "확인 불가"

    prefer = None
    if capability == "creative":
        prefer = "claude"
    elif capability == "code":
        prefer = "chatgpt"

    if weight == "light":
        agent, reason = "muse", f"가벼운 작업은 Muse 직접 (Muse 사용량 {usage_str})"
    elif weight == "heavy":
        ext = ready_external(cfg, prefer)
        if ext:
            agent = ext[0]
            reason = (f"무거운 작업 → 외부 분산 (Muse 사용량 {usage_str}, "
                      f"역량: {', '.join(cfg['agents'][agent].get('strengths', []))})")
        else:
            agent, reason = "muse", "사용 가능한 외부 에이전트 없음 — Muse가 직접"
    else:  # medium
        if usage is not None and usage >= high:
            ext = ready_external(cfg, prefer)
            if ext:
                agent = ext[0]
                reason = f"Muse 사용량 {usage_str} (high {high}%+) → 외부로 분산"
            else:
                agent, reason = "muse", "외부 에이전트 없음 — Muse가 직접"
        else:
            agent, reason = "muse", f"중간 작업, Muse 사용량 {usage_str} — Muse 직접"

    if usage is not None and usage >= critical and agent == "muse":
        reason += " [경고: 사용량 critical — 외부 분산을 적극 고려할 것]"
    print(f"agent={agent}")
    print(f"reason={reason}")
    if task:
        print(f"task={task}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief")
    ap.add_argument("--expect")
    ap.add_argument("--agent")
    ap.add_argument("--timeout-min", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--config", default=os.environ.get("AGENT_ROUTER_CONFIG"))
    ap.add_argument("--since")
    ap.add_argument("--suggest", action="store_true")
    ap.add_argument("--weight", choices=["light", "medium", "heavy"], default="medium")
    ap.add_argument("--capability", choices=["creative", "code"])
    ap.add_argument("--task")
    args = ap.parse_args()

    cfg = load_config(args.config)

    if args.suggest:
        return suggest(cfg, args.weight, args.capability, args.task)

    agent = args.agent or cfg.get("default_external", "claude")
    a = cfg["agents"].get(agent)
    if not a or a.get("status") != "ready":
        print(f"NOT_CONFIGURED: agent '{agent}' 사용 불가 "
              f"(status={a.get('status') if a else 'unknown'})")
        return 4

    if args.check:
        since_ts = datetime.fromisoformat(args.since).replace(
            tzinfo=timezone.utc).timestamp() if args.since else 0
        return wait_for_file(args.expect, since_ts, 0.01, 1)

    brief = os.path.abspath(args.brief)
    expect = os.path.abspath(args.expect)
    timeout = args.timeout_min or cfg["fallback"]["no_response_timeout_min"]
    poll = cfg["fallback"]["poll_interval_sec"]
    start_ts = time.time()

    if args.dry_run:
        print(f"[dry-run] agent={agent} kind={a['kind']} brief={brief} expect={expect}")
        return 0

    kind = a["kind"]
    if kind == "tmux":
        rc = deliver_claude(a["session"], a.get("idle_marker", "❯"), brief, expect)
        if rc != 0:
            return rc
    elif kind == "codex_exec":
        return deliver_chatgpt(a["command"], brief, expect, timeout)
    elif kind == "builtin":
        print("agent=muse: Muse가 직접 처리한다 (핸드오프 없음)")
        return 0
    else:
        print(f"UNKNOWN kind: {kind}")
        return 4

    return wait_for_file(expect, start_ts, timeout, poll)


if __name__ == "__main__":
    sys.exit(main())
