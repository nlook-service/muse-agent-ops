# CHANGELOG

이 레포의 변경 기록입니다. 선순환이 눈에 보이게 남깁니다.
기여자가 있으면 함께 기록합니다.

## [0.5.0] — 2026-10-06

### 추가
- `references/context-management.md` — 컨텍스트 관리 v1
  - 80% 초과 시 사용자에게 경고하고 새 채팅 제안 (자동 압축보다 새 채팅이 저렴)
  - 기본 컨텍스트 다이어트 (MEMORY.md 54KB→5KB 압축을 기준으로)
  - 검증은 글을 쓴 에이전트가 수행 (허브는 재검증 안 함)
  - 컨텍스트를 가장 많이 먹는 5가지 순위
- SKILL.md 운영 영역에 컨텍스트 관리 추가

## [0.4.0] — 2026-10-06

### 추가
- `references/article-pipeline.md` — 기사 제작 파이프라인 v1 (8단계)
  - 제목 먼저 → 소스 5개 이상 → 나의 의견 정리(결론·내가 말하고자 하는 것)
  - → 디에디트형 구성 → 주제에 맞는 사진 → 인사이트 확인 → 5대 축 채점 → 발행
- 평가 루브릭·파이프라인에 REWORK 규칙 명시: 점수 미달 시 글 재작성 + 이미지 선정 다시 (문장 수정이 아님)

## [0.3.0] — 2026-10-06

### 추가
- `references/eval-rubric.md` — 콘텐츠 평가 루브릭 v1 (5대 축 50점 만점)
  - 풍부함(구체성·깊이·주제 선언·완결성) / 훅(제목 5·오프닝 3·표지 2)
  - 재미(리듬·장면·반전) / 지식적 재미(아하 모먼트·연결) / 인사이트(판단 선명도·행동 유도)
  - 통과 기준 35/50, 필수 요소로 맨 아래 출처 표기 (누락 시 REWORK)
  - 점수→고도화 루프: 채점→반응→주간 갱신(배점 보정)→규칙 승격
- SKILL.md 운영 영역에 콘텐츠 평가 루브릭 추가

## [0.2.0] — 2026-10-06

### 추가
- `bin/publish.py` — 로컬 개선사항을 보안 검사 후 발행하는 스크립트
  (secret-scan + 공개 안전성 체크 → Git Data API로 커밋·push)
- `VERSION` — 현재 버전 파일
- `CHANGELOG.md` — 이 파일
- README에 "3. Muse는 이 레포를 어떻게 읽나요?" 섹션 추가
  (발견→설치→실행 흐름, 파일별 역할 표)
- README에 "5. 추가로 필요한 연결 (커넥터)" 표 추가

### 변경
- README 전체를 11개 섹션 체계로 재구성
  (소개 → muse.ai → 내부 구조 → 달라지는 점 → 설치 → 커넥터 → nlook MCP → 구성 → 규칙 → 보안 → 개선 참여)

## [0.1.0] — 2026-10-06 (최초 공개)

- PM 프로세스 (`bin/setup.py`, `bin/hygiene.py`, `references/process.md`)
- 보안 3중 방어 (`bin/secret-scan.py`, `bin/install-hooks.sh`, `references/secret-policy.md`)
- 선택 설치 (`bin/install.py`)
- 공개 스킬 4종 (`skills/qa`, `skills/english-learning`, `skills/trend-curation`, `skills/claude-keepalive`)
- 설치·활용 가이드 (`references/install-guide.md`, `doc-backend.md`, `nlook-mcp-guide.md`, `usage-guide.md`)
