#!/usr/bin/env python3
"""pm-process setup: create the PM label set in a target repo (idempotent).

Usage:
    python3 setup.py --repo owner/name [--token TOKEN]

Labels created (only if missing):
    분야:* (10) — 기획/개발/마케팅/디자인/인프라/QA/운영/사업운영/자금/AI기술
    단계:* (4)  — 기획중/디자인중/개발대기/개발중
    신규개발, epic, P0, P1, P2, P3, 직접확인필요
"""
import argparse
import json
import os
import sys
import urllib.request

LABELS = [
    # 분야 (10)
    ("분야:기획", "8B5CF6", "기획 분야"),
    ("분야:개발", "1D76DB", "개발 분야"),
    ("분야:마케팅", "EC4899", "마케팅 분야"),
    ("분야:디자인", "F59E0B", "디자인 분야"),
    ("분야:인프라", "6B7280", "인프라 분야"),
    ("분야:QA", "10B981", "QA 분야"),
    ("분야:운영", "0D9488", "운영 분야"),
    ("분야:사업운영", "4338CA", "사업운영 분야"),
    ("분야:자금", "166534", "자금 분야"),
    ("분야:AI기술", "7E22CE", "AI기술 분야"),
    # 단계 (4) — 이슈당 1개만 유지
    ("단계:기획중", "f9d0c4", "기획 단계 진행 중 — 컨펌 리뷰 통과 전"),
    ("단계:디자인중", "fef2c0", "디자인 시안 작업 중 — 시안 컨펌 전"),
    ("단계:개발대기", "d4c5f9", "기획·디자인 완료, 개발 시작 대기"),
    ("단계:개발중", "0e8a16", "개발 진행 중"),
    # 기타
    ("신규개발", "1d76db", "신규 기능 개발 이슈"),
    ("epic", "e6e10b", "에픽 이슈"),
    ("P0", "fd3aaa", "가장 중요한 급건"),
    ("P1", "7b7814", "우선순위 P1"),
    ("P2", "83056f", "우선순위 P2"),
    ("P3", "0e8a16", "우선순위 P3"),
    ("직접확인필요", "d93f0b", "자동화 확신 게이트 탈락 — 사람 직접 확인 필요"),
]


def api(token, method, path, data=None):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=json.dumps(data).encode() if data is not None else None,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r), None
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        return None, f"HTTP {e.code}: {body}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="owner/name")
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    a = ap.parse_args()
    if not a.token:
        sys.exit("GITHUB_TOKEN 환경변수 또는 --token 필요")

    created, skipped, failed = [], [], []
    for name, color, desc in LABELS:
        data, err = api(a.token, "POST", f"/repos/{a.repo}/labels",
                        {"name": name, "color": color, "description": desc})
        if data:
            created.append(name)
        elif err and "already_exists" in err:
            skipped.append(name)
        else:
            failed.append((name, err))
    print(f"생성: {len(created)}, 이미 있음: {len(skipped)}, 실패: {len(failed)}")
    for n in created:
        print("  +", n)
    for n, e in failed:
        print("  !", n, e)


if __name__ == "__main__":
    main()
