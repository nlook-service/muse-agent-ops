# CHANGELOG

이 레포의 변경 기록입니다. 선순환이 눈에 보이게 남깁니다.
기여자가 있으면 함께 기록합니다.

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
