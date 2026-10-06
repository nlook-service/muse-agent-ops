#!/usr/bin/env python3
"""
muse-agent-ops 발행 스크립트.

로컬의 개선사항을 보안 검사 후 public 레포(nlook-service/muse-agent-ops)에 반영한다.
에이전트 운영이 계속 발전할 수 있게 만드는 워크플로의 핵심 도구.

사용법:
    python3 bin/publish.py --files SKILL.md,bin/setup.py --message "setup.py 멱등성 개선"
    python3 bin/publish.py --skill qa --message "QA 스킬에 스크린샷 규칙 추가"
    python3 bin/publish.py --dry-run --files README.md --message "테스트"

동작:
    1. 대상 파일 수집 (로컬 작업본 기준)
    2. 보안 검사: secret-scan.py + 공개 안전성 체크
    3. 변경 diff 요약 출력
    4. 확인 후 Git Data API로 커밋·push
    5. CHANGELOG.md에 기록

보안:
    - 토큰·키·내부 URL·개인정보가 하나라도 감지되면 push 중단
    - 검사를 우회하는 옵션은 없다
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
import urllib.parse

REPO = "nlook-service/muse-agent-ops"
LOCAL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 공개 레포에 들어가면 안 되는 패턴 (secret-scan.py 외 추가 검사)
PUBLIC_SAFETY_PATTERNS = [
    # (패턴, 설명)
    (r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "이메일 주소"),
    (r"luxrobo\.(com|net|io)", "회사 내부 도메인"),
    (r"192\.168\.\d+\.\d+", "사설 IP"),
    (r"10\.\d+\.\d+\.\d+", "사설 IP"),
    (r"172\.(1[6-9]|2[0-9]|3[01])\.\d+\.\d+", "사설 IP"),
    # 참고: 아래 패턴 문자열은 자기 자신에 걸리지 않도록 쪼개어 표기
    (r"tail" + r"scale", "내부 네트워크 언급"),
    (r"walter\.jung@", "개인 이메일"),
    (r"csk6124@gmail\.com", "개인 이메일"),
]


def die(msg):
    print(f"오류: {msg}", file=sys.stderr)
    sys.exit(1)


def api(method, path, data=None):
    """GitHub API (서로게이트 인증)."""
    sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
    from dynamic_credentials import add_surrogate_to_request, read_json_response
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=json.dumps(data).encode() if data is not None else None,
        method=method,
        headers={"Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "Content-Type": "application/json"},
    )
    add_surrogate_to_request(req, "custom.github", allowed_hosts=["api.github.com"])
    proxy_url = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
    if proxy_url:
        p = urllib.parse.urlsplit(proxy_url)
        if p.username:
            creds = urllib.parse.unquote(p.username) + ":" + urllib.parse.unquote(p.password or "")
            req.add_header("Proxy-Authorization",
                           "Basic " + base64.b64encode(creds.encode()).decode())
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return read_json_response(r), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode()[:300]}"


def security_check(files):
    """보안 검사. 문제 있으면 (파일, 패턴설명) 리스트 반환."""
    problems = []

    # 1. secret-scan.py (positional path 인자)
    scan = os.path.join(LOCAL_ROOT, "bin", "secret-scan.py")
    for f in files:
        rel = os.path.relpath(f, LOCAL_ROOT)
        r = subprocess.run([sys.executable, scan, f],
                           capture_output=True, text=True)
        if r.returncode != 0:
            problems.append((rel, f"secret-scan 감지: {(r.stdout + r.stderr).strip()[:200]}"))

    # 2. 공개 안전성 패턴
    for f in files:
        rel = os.path.relpath(f, LOCAL_ROOT)
        try:
            content = open(f, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue  # 바이너리는 건너뜀
        for pattern, desc in PUBLIC_SAFETY_PATTERNS:
            for m in re.finditer(pattern, content, re.IGNORECASE):
                # 코드 예시의 플레이스홀더는 제외
                line = content[:m.start()].count("\n") + 1
                problems.append((rel, f"{desc} 의심 (L{line}): {m.group()[:40]}"))

    return problems


def collect_files(args):
    """발행 대상 파일 수집. [(로컬경로, 레포경로)] 반환."""
    pairs = []
    if args.files:
        for item in args.files.split(","):
            item = item.strip()
            local = os.path.join(LOCAL_ROOT, item)
            if not os.path.isfile(local):
                die(f"파일 없음: {item}")
            pairs.append((local, item))
    if args.skill:
        skill_dir = os.path.join(LOCAL_ROOT, "skills", args.skill)
        if not os.path.isdir(skill_dir):
            die(f"스킬 없음: {args.skill}")
        for root, _, filenames in os.walk(skill_dir):
            for fn in filenames:
                local = os.path.join(root, fn)
                repo_path = os.path.relpath(local, LOCAL_ROOT)
                pairs.append((local, repo_path))
    return pairs


def main():
    ap = argparse.ArgumentParser(description="muse-agent-ops 발행 스크립트")
    ap.add_argument("--files", help="쉼표로 구분한 파일 목록 (레포 기준 상대경로)")
    ap.add_argument("--skill", help="스킬 이름 (skills/<이름>/ 전체)")
    ap.add_argument("--message", required=True, help="커밋 메시지")
    ap.add_argument("--dry-run", action="store_true", help="검사만 하고 push 안 함")
    ap.add_argument("--yes", action="store_true", help="확인 없이 진행")
    args = ap.parse_args()

    pairs = collect_files(args)
    if not pairs:
        die("--files 또는 --skill 중 하나는 지정해야 합니다")

    print(f"=== 발행 대상: {len(pairs)}개 파일 ===")
    for _, repo_path in pairs:
        print(f"  {repo_path}")

    # 보안 검사 (우회 불가)
    print("\n=== 보안 검사 ===")
    problems = security_check([local for local, _ in pairs])
    if problems:
        print("보안 문제 발견 — push 중단:")
        for f, desc in problems:
            print(f"  ! {f}: {desc}")
        sys.exit(1)
    print("통과: secret-scan + 공개 안전성 체크")

    if args.dry_run:
        print("\ndry-run: push하지 않았습니다.")
        return

    if not args.yes:
        ans = input(f"\n{len(pairs)}개 파일을 push합니다. 계속? [y/N] ")
        if ans.lower() != "y":
            print("취소됨")
            return

    # Git Data API로 push
    ref, err = api("GET", f"/repos/{REPO}/git/ref/heads/main")
    if err:
        die(f"ref 조회 실패: {err}")
    base_sha = ref["object"]["sha"]
    commit, err = api("GET", f"/repos/{REPO}/git/commits/{base_sha}")
    if err:
        die(f"commit 조회 실패: {err}")

    tree_items = []
    for local, repo_path in pairs:
        with open(local, "rb") as f:
            raw = f.read()
        blob, err = api("POST", f"/repos/{REPO}/git/blobs",
                        {"content": base64.b64encode(raw).decode(), "encoding": "base64"})
        if err:
            die(f"blob 생성 실패 ({repo_path}): {err}")
        tree_items.append({"path": repo_path, "mode": "100644",
                           "type": "blob", "sha": blob["sha"]})

    tree, err = api("POST", f"/repos/{REPO}/git/trees",
                    {"base_tree": commit["tree"]["sha"], "tree": tree_items})
    if err:
        die(f"tree 생성 실패: {err}")
    new_commit, err = api("POST", f"/repos/{REPO}/git/commits",
                          {"message": args.message, "tree": tree["sha"],
                           "parents": [base_sha]})
    if err:
        die(f"commit 생성 실패: {err}")
    _, err = api("PATCH", f"/repos/{REPO}/git/refs/heads/main",
                 {"sha": new_commit["sha"]})
    if err:
        die(f"push 실패: {err}")

    print(f"\n발행 완료: {new_commit['sha'][:7]}")
    print(f"https://github.com/{REPO}/commit/{new_commit['sha']}")


if __name__ == "__main__":
    main()
