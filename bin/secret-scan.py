#!/usr/bin/env python3
"""secret-scan: public 레포에 올라가면 안 되는 비밀값을 사전에 감지한다.

Usage:
    python3 bin/secret-scan.py [path...]   # 기본: 현재 디렉토리 전체
    python3 bin/secret-scan.py --staged     # git staged 파일만 검사

종료 코드: 비밀값 발견 시 1, 없으면 0.
pre-push hook으로 연결하면 push 전에 자동 차단된다.
"""
import argparse
import os
import re
import subprocess
import sys

PATTERNS = [
    ("GitHub PAT", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("GitHub classic token", re.compile(r"\bghp_[A-Za-z0-9]{20,}")),
    ("GitHub OAuth token", re.compile(r"\bgho_[A-Za-z0-9]{20,}")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{10,}")),
    ("OpenAI API key", re.compile(r"\bsk-[A-Za-z0-9]{20,}")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}")),
    ("AWS secret key", re.compile(r"aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{20,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}")),
    ("Slack token", re.compile(r"\bxox[bap]-[A-Za-z0-9-]{10,}")),
    ("Private key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("URL with credentials", re.compile(r"https?://[^/\s:]+:[^/\s@]+@")),
    ("password assignment", re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{4,}['\"]")),
    ("secret assignment", re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][A-Za-z0-9_.~+/-]{16,}['\"]")),
    ("Tailscale key", re.compile(r"\btskey-[A-Za-z0-9_-]{10,}")),
]

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip"}


def files_to_check(paths, staged):
    if staged:
        out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                             capture_output=True, text=True)
        return [f for f in out.stdout.splitlines() if os.path.isfile(f)]
    result = []
    for p in paths:
        if os.path.isfile(p):
            result.append(p)
        else:
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for f in files:
                    if os.path.splitext(f)[1].lower() in SKIP_EXT:
                        continue
                    result.append(os.path.join(root, f))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--staged", action="store_true")
    a = ap.parse_args()

    hits = []
    for path in files_to_check(a.paths, a.staged):
        try:
            with open(path, "r", encoding="utf-8", errors="strict") as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        for name, rx in PATTERNS:
            for m in rx.finditer(text):
                # 마스킹해서 보여준다 (값 자체는 출력하지 않음)
                preview = m.group(0)
                masked = preview[:8] + "***" if len(preview) > 8 else "***"
                lineno = text.count("\n", 0, m.start()) + 1
                hits.append((path, lineno, name, masked))

    if hits:
        print(f"비밀값 의심 패턴 {len(hits)}건 발견 — push 금지:")
        for path, lineno, name, masked in hits:
            print(f"  {path}:{lineno} [{name}] {masked}")
        print("\n대응: 값을 환경변수·Secure Vault 참조로 교체한 뒤 다시 검사.")
        return 1
    print("비밀값 없음. 안전.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
