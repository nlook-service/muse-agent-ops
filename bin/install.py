#!/usr/bin/env python3
"""선택 설치: 원하는 스킬만 골라서 설치한다.

Usage:
    python3 bin/install.py --list              # 설치 가능한 스킬 목록
    python3 bin/install.py                     # 대화형으로 선택
    python3 bin/install.py --skills pm,qa      # 지정한 것만 설치
    python3 bin/install.py --skills all        # 전부 설치

전부 설치하면 불필요한 스킬까지 들어가므로 기본은 선택 설치다.
"""
import argparse
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKILLS = {
    "pm": {
        "name": "PM 프로세스",
        "desc": "GitHub 이슈 단계 라벨·보드·마일스톤 자동화 (bin/setup.py, hygiene.py)",
        "needs": ["GitHub 토큰 (Issues 읽기/쓰기)", "대상 레포 (owner/name)"],
    },
    "qa": {
        "name": "도그푸딩 QA",
        "desc": "고객 시점 탐색 + 위치 특정 이슈 등록 프로세스 (문서만, 설치 불필요)",
        "needs": [],
    },
    "english-learning": {
        "name": "영어 학습 등록",
        "desc": "매일 영어 뉴스 → 중급 학습 문서 등록 (문서 백엔드 필요)",
        "needs": ["문서 백엔드 (references/doc-backend.md 참고)"],
    },
    "trend-curation": {
        "name": "트렌드 글등록",
        "desc": "매일 아침 트렌드 기사 수집 → 요약 문서 등록 (문서 백엔드 필요)",
        "needs": ["문서 백엔드 (references/doc-backend.md 참고)"],
    },
    "claude-keepalive": {
        "name": "Claude 세션 keepalive",
        "desc": "Claude Code 원격 세션 24/7 유지 스크립트",
        "needs": ["tmux", "Claude Code 설치"],
    },
}


def install_pm():
    repo = input("대상 레포 (owner/name): ").strip()
    if not repo:
        print("취소됨: 레포를 입력하지 않음")
        return
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN 환경변수가 필요합니다.")
        return
    subprocess.run([sys.executable, os.path.join(BASE, "bin", "setup.py"),
                    "--repo", repo], check=False)


def install_qa():
    print("qa 스킬은 문서 기반이라 설치할 것이 없습니다.")
    print("위치: skills/qa/ — SKILL.md와 이슈 템플릿을 참고하세요.")


def install_english_learning():
    print("english-learning 스킬은 문서 백엔드가 필요합니다.")
    print("references/doc-backend.md 를 보고 백엔드를 먼저 정하세요.")
    print("위치: skills/english-learning/")


def install_trend_curation():
    print("trend-curation 스킬은 문서 백엔드가 필요합니다.")
    print("references/doc-backend.md 를 보고 백엔드를 먼저 정하세요.")
    print("위치: skills/trend-curation/")


def install_keepalive():
    dest = os.path.expanduser("~/workspace/claude-keepalive")
    os.makedirs(dest, exist_ok=True)
    src = os.path.join(BASE, "skills", "claude-keepalive", "bin", "keepalive.sh")
    dst = os.path.join(dest, "keepalive.sh")
    with open(src, "rb") as f_in, open(dst, "wb") as f_out:
        f_out.write(f_in.read())
    os.chmod(dst, 0o755)
    print(f"스크립트 복사 완료: {dst}")
    print("cron에 등록하세요:")
    print(f"  */5 * * * * {dst}")


INSTALLERS = {
    "pm": install_pm,
    "qa": install_qa,
    "english-learning": install_english_learning,
    "trend-curation": install_trend_curation,
    "claude-keepalive": install_keepalive,
}


def list_skills():
    print("설치 가능한 스킬:")
    for key, s in SKILLS.items():
        print(f"  [{key}] {s['name']} — {s['desc']}")
        for n in s["needs"]:
            print(f"        필요: {n}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--skills", default=None,
                    help="콤마로 구분 (예: pm,qa) 또는 all")
    a = ap.parse_args()

    if a.list:
        list_skills()
        return

    if a.skills:
        selected = list(SKILLS.keys()) if a.skills == "all" else \
            [s.strip() for s in a.skills.split(",")]
    else:
        list_skills()
        print()
        raw = input("설치할 스킬 (콤마로 구분, 예: pm,qa): ").strip()
        selected = [s.strip() for s in raw.split(",") if s.strip()]

    for key in selected:
        if key not in SKILLS:
            print(f"알 수 없는 스킬: {key} — 건너뜀")
            continue
        print(f"\n=== {SKILLS[key]['name']} 설치 ===")
        INSTALLERS[key]()
    print("\n완료.")


if __name__ == "__main__":
    main()
