---
name: "muse-agent-ops"
description: "전체 에이전트 운영 스킬: GitHub 이슈 기반 PM 프로세스(신규개발 파이프라인의 단계 라벨·분야 라벨·보드·마일스톤), 배포 프로세스, 모니터링·업데이트 운영을 스크립트로 적용·유지한다. 팀원이 같은 규칙을 자기 레포에 적용할 때 쓴다."
---

# muse-agent-ops

## Purpose
전체 에이전트 운영을 하나의 스킬로 묶는다. Muse가 일상 업무에 쓰는 스킬들
(GitHub PM 프로세스, 글 등록, 영어 학습 등)을 public 레포에서 안전하게 공유·운영한다.
하나의 스크립트로 어떤 레포에든 동일하게 적용하고, 비밀값 유출을 사전에 차단한다.

현재 포함된 운영 영역:
- **PM 프로세스**: 신규개발 파이프라인(기획→디자인→개발)의 단계 라벨·분야 라벨·보드·마일스톤
- **보안 프로세스**: secret-scan + pre-push hook + push protection 3중 방어
- **에이전트 라우터**: 무거운 작업을 외부 에이전트(Claude Code 세션, Codex CLI)에 위임해 메인 에이전트 토큰 사용량 분산 (`references/agent-router.md`, `bin/agent-router.py`)
- **콘텐츠 평가 루브릭**: 글·카피를 5대 축(풍부함·훅·재미·지식적 재미·인사이트) 50점 만점으로 채점하고, 점수로 다음 결과물을 고도화하는 루프 (`references/eval-rubric.md`)
- **기사 제작 파이프라인**: 제목 먼저 → 소스 5개 이상 → 나의 의견 정리 → 디에디트형 구성 → 주제에 맞는 사진 → 인사이트 확인 → 5대 축 채점 → 발행. 점수 미달 시 글 재작성 + 이미지 선정 다시 (`references/article-pipeline.md`)
- **컨텍스트 관리**: 기본 컨텍스트 다이어트(MEMORY.md 압축), 80% 초과 시 사용자에게 경고하고 새 채팅 제안, 검증은 글을 쓴 에이전트가 수행 (`references/context-management.md`)
- **배포 프로세스**: (정리 중 — 확정되는 대로 추가)
- **모니터링·업데이트**: (정리 중 — 확정되는 대로 추가)
- **업무 스킬 모음** (`skills/`): 글 등록·영어 학습 등 — 정리가 끝난 것부터 추가

## Tooling
- `bin/setup.py --repo owner/name` — 라벨 세트를 대상 레포에 생성(멱등). 이미 있으면 건너뛴다.
- `bin/hygiene.py --repo owner/name [--board-project <id>]` — 열린 이슈 전체를 점검해 분야 라벨·마일스톤·단계 라벨·보드 상태를 현재 단계에 맞게 정리한다.
- `bin/agent-router.py --config config.yaml --brief <브리프> --expect <결과파일>` — 외부 에이전트에 위임 (전달 + 대기 + 타임아웃 판정). `--suggest --weight heavy` 로 라우팅 추천.
- 전체 파이프라인 정의: `references/process.md`

## Auth
GitHub fine-grained PAT 필요. 권한: Issues Read and write, Projects Read and write(보드 연동 시).
토큰 전달: `GITHUB_TOKEN` 환경변수 또는 `--token` 인자.
이 VM에서는 `~/workspace/skills/github/bin/gh.py` (Secure Vault 경유)를 그대로 써도 된다.

## Operating Rules
1. 단계 라벨(`단계:기획중/디자인중/개발대기/개발중`)은 이슈당 1개만 유지한다. 전환 시 기존 단계 라벨을 떼고 새 것을 붙인다.
2. 마일스톤은 단계 따라 이동한다: 기획 10월 → 디자인 10월 → 개발 10월 (월간 마일스톤이 없으면 만든다).
3. 보드 Status 매핑: Todo=신규, In Progress=기획중·디자인중·개발대기·개발중, Done=완료(close 시).
4. 단계 전환은 명시적 트리거로만: 컨펌 리뷰 통과→디자인중, 시안 컨펌→개발대기, `@claude`/승인→개발중, PR 머지→Done.
5. `setup.py`는 읽기 전용 점검 후 없는 것만 만든다. 기존 라벨을 덮어쓰지 않는다.
6. `hygiene.py`는 변경 전에 무엇을 바꿀지 먼저 출력(dry-run 기본, `--apply`로 적용).
