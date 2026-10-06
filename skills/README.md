# 공개용 스킬 모음

Muse가 실제 업무에 쓰는 스킬들을 public-safe하게 정리해서 올리는 공간.

## 스킬 목록

| 스킬 | 설명 |
|---|---|
| `pm/` | GitHub PM 프로세스 — 루트의 `bin/` + `references/process.md`가 본체 |
| `qa/` | 도그푸딩 QA — 고객 시점 탐색 + 위치 특정 이슈 등록 |

## 추가 예정

- 글 등록, 영어 학습 등 업무 스킬 — 정리되는 대로 추가

## 추가 절차

1. 원본 스킬을 `skills/<이름>/`에 복사
2. `python3 ../../bin/secret-scan.py skills/<이름>/` — 통과 필수
3. 실제 계정명·경로·키 참조를 플레이스홀더로 교체 (체크리스트: `references/secret-policy.md`)
4. push (pre-push hook이 자동 재검사)
