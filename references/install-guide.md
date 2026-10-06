# 설치 가이드 — muse.ai에서 시작하기

## 0단계 — 설치하기 전에 준비할 것

아래 3개만 준비하면 됩니다.

- [ ] **Python 3** — 스크립트 실행용. `python3 --version`으로 확인.
  **pip install은 필요 없습니다.** 모든 스크립트가 표준 라이브러리만 씁니다.
- [ ] **git** — 소스 받기 + push 전 자동 검사용. 없어도 되지만 권장.
- [ ] **GitHub 토큰** — 필수. 없으면 401 오류로 실패합니다. 발급법:
  1. https://github.com/settings/tokens?type=beta 접속
  2. **Generate new token** → Fine-grained token
  3. Token name: `muse-agent-ops` / Resource owner: 자신의 org / Repository access: 적용할 레포 선택
  4. Permissions → **Issues: Read and write** 선택 후 생성
  5. 복사한 토큰은 Muse의 보안 입력(Secure Vault)에 등록 (채팅창에 직접 붙여넣기 금지)

| 항목 | 없어도 되나? | 없으면 |
|---|---|---|
| pip 패키지 | 예 — 애초에 필요 없음 | 해당 없음 |
| git | 예 (권장) | pre-push 자동 검사 불가 → `secret-scan.py` 수동 실행 |
| GitHub 토큰 | **아니오** | 401로 모든 API 호출 실패 |
| Muse (muse.ai) | 예 | 터미널에서 직접 실행 (아래 "직접 터미널에서 하기") |

## 스킬별 필요한 연결 (커넥터)

스킬마다 필요한 외부 연결이 다릅니다. 원하는 스킬의 것만 연결하면 됩니다.

| 스킬 | 필요한 연결 | 연결 방법 |
|---|---|---|
| `pm` | GitHub (Issues 읽기/쓰기) | 위 0단계의 토큰 발급 |
| `qa` | GitHub (Issues 읽기/쓰기) | 위 0단계의 토큰 발급 |
| `english-learning` | 문서 백엔드 1개 | `references/doc-backend.md` 참고 — 로컬 파일 / nlook MCP / REST API 중 선택 |
| `trend-curation` | 문서 백엔드 1개 | 위와 동일 |
| `claude-keepalive` | 없음 (로컬 실행) | tmux + Claude Code만 있으면 됨 |

**nlook이 없어도 됩니다.** 문서 백엔드는 로컬 파일 저장으로 시작할 수 있고,
나중에 nlook이나 다른 API로 바꿀 수 있습니다.

## 이걸 쓰면 뭐가 달라지나요?

![도입 전후 비교](../assets/before-after.png)

핵심은 하나입니다. **일일이 말하지 않아도** 이슈의 상태가 라벨·보드·마일스톤에
자동으로 정리됩니다. PM이 "지금 어디쯤이에요?"라는 질문을 받지 않게 됩니다.

![신규개발 파이프라인](../assets/pipeline.png)

## muse.ai에서 설치하기 (2단계)

### 1단계 — Muse에게 스킬 설치 요청

Muse 채팅에 이렇게 말하세요:

> https://github.com/nlook-service/muse-agent-ops 이 스킬을 설치해줘

### 2단계 — Muse에게 적용 요청

> 내 레포 `my-org/my-repo`에 PM 라벨을 설치해줘

Muse가 `bin/setup.py`를 실행합니다. 결과:

```
생성: 21, 이미 있음: 0, 실패: 0
```

이미 라벨이 있으면 건너뛰니 안전합니다.

### 이후 — 주기적 점검

> 매 3시간마다 열린 이슈를 점검해줘

라고 하면 Muse가 스케줄을 걸어 `bin/hygiene.py`로 자동 정리합니다.
처음에는 dry-run 결과를 보고받고, 믿음이 생기면 자동 적용으로 바꾸세요.

## nlook과 함께 쓰기

nlook MCP가 연결되어 있으면 운영 기록이 nlook 문서로 쌓입니다.

| 하고 싶은 것 | Muse에게 할 말 |
|---|---|
| 이번 주 운영 현황 정리 | "열린 이슈 현황을 nlook 문서로 정리해줘" |
| 단계 전환 기록 | "이슈 #123을 개발대기로 옮기고 사유를 nlook에 기록해줘" |
| 주간 리포트 | "이번 주 단계가 바뀐 이슈들을 nlook 주간 문서로 만들어줘" |

더 깊은 연동(MCP에 `ops_digest` 같은 전용 도구 추가)은
`references/nlook-mcp-guide.md`를 참고하세요.

## 직접 터미널에서 하기

```bash
git clone https://github.com/nlook-service/muse-agent-ops.git
cd muse-agent-ops
sh bin/install-hooks.sh          # push 전 비밀값 자동 차단 (권장)
export GITHUB_TOKEN=github_pat_xxx

python3 bin/setup.py --repo owner/name            # 라벨 설치
python3 bin/hygiene.py --repo owner/name          # 점검 (dry-run)
python3 bin/hygiene.py --repo owner/name --apply  # 실제 적용
python3 bin/secret-scan.py                        # 비밀값 검사
```

## 문제 해결

| 증상 | 원인 | 해결 |
|---|---|---|
| `401 Unauthorized` | 토큰이 없거나 만료됨 | 토큰 재발급 후 `GITHUB_TOKEN` 갱신 |
| `403 Resource not accessible` | Issues 권한 없음 | 토큰 권한에 Issues Read and write 추가 |
| `python3: command not found` | Python 미설치 | https://www.python.org/downloads/ 에서 설치 |
| `이미 있음: 21` | 이미 설치됨 | 정상. 아무것도 안 바뀜 |
| 한글 라벨이 깨져 보임 | 터미널 인코딩 | UTF-8 터미널 사용 |
