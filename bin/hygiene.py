#!/usr/bin/env python3
"""pm-process hygiene: 열린 이슈의 라벨·마일스톤·단계 라벨을 점검하고 정리한다.

Usage:
    python3 hygiene.py --repo owner/name [--token TOKEN] [--apply]

기본은 dry-run: 무엇을 바꿀지만 출력한다. --apply로 실제 적용.
규칙:
  1. 분야 라벨이 하나도 없으면 제목의 [분야] 태그로 추론해 제안한다.
  2. 마일스톤이 없으면 단계/분야에 맞는 월간 마일스톤을 제안한다.
  3. 신규개발 이슈의 단계 라벨이 0개 또는 2개 이상이면 현재 상태에 맞게 1개로 정리한다.
"""
import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

STAGES = ["단계:기획중", "단계:디자인중", "단계:개발대기", "단계:개발중"]
FIELDS = ["분야:기획", "분야:개발", "분야:마케팅", "분야:디자인", "분야:인프라",
          "분야:QA", "분야:운영", "분야:사업운영", "분야:자금", "분야:AI기술"]
STAGE_MILESTONE = {
    "단계:기획중": "기획", "단계:디자인중": "디자인",
    "단계:개발대기": "개발", "단계:개발중": "개발",
}


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
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if not a.token:
        sys.exit("GITHUB_TOKEN 환경변수 또는 --token 필요")

    try:
        issues = api(a.token, "GET", f"/repos/{a.repo}/issues?state=open&per_page=100")
    except Exception as e:
        sys.exit(f"조회 실패: {e}")

    plans = []
    for d in issues:
        if "pull_request" in d:
            continue
        num = d["number"]
        labels = [l["name"] for l in d["labels"]]
        fields = [l for l in labels if l in FIELDS]
        stages = [l for l in labels if l in STAGES]
        fixes = []
        if not fields:
            # 제목의 [태그]로 추론
            title = d["title"]
            guess = None
            for f in FIELDS:
                tag = f.split(":")[1]
                if f"[{tag}]" in title:
                    guess = f
                    break
            fixes.append(f"분야 라벨 추가 제안: {guess or '(판단 불가 — 수동 지정 필요)'}")
        if not d.get("milestone"):
            stage = stages[0] if stages else None
            base = STAGE_MILESTONE.get(stage, "기획")
            ym = datetime.now(timezone.utc).strftime("%Y-%m")
            # 한국어 월 표기: 2026-10 -> 10월
            m = ym.split("-")[1].lstrip("0")
            fixes.append(f"마일스톤 지정 제안: {base} {m}월")
        if "신규개발" in labels and len(stages) != 1:
            fixes.append(f"단계 라벨 정리 필요: 현재 {stages or '없음'} → 1개로")
        if fixes:
            plans.append((num, d["title"][:50], fixes))

    if not plans:
        print("정리할 이슈 없음. 모두 깔끔함.")
        return
    print(f"=== 점검 결과: {len(plans)}건 ===")
    for num, title, fixes in plans:
        print(f"#{num} {title}")
        for f in fixes:
            print(f"   - {f}")
    if not a.apply:
        print("\ndry-run 모드. 적용하려면 --apply를 붙여 실행.")
        return

    for num, title, fixes in plans:
        # 분야 라벨 자동 추가 (제목 태그로 추론된 경우만)
        for f in fixes:
            if f.startswith("분야 라벨 추가 제안: 분야:"):
                label = f.split(": ", 1)[1]
                cur = api(a.token, "GET", f"/repos/{a.repo}/issues/{num}")
                cur_labels = [l["name"] for l in cur["labels"]] + [label]
                api(a.token, "PATCH", f"/repos/{a.repo}/issues/{num}", {"labels": cur_labels})
                print(f"#{num}: {label} 추가 완료")
    print("적용 완료. 마일스톤·단계 라벨은 제안 확인 후 수동 적용 권장.")


if __name__ == "__main__":
    main()
