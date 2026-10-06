# 설치 가이드 — muse.ai에서 시작하기

## 이걸 쓰면 뭐가 달라지나요?

![도입 전후 비교](../assets/before-after.png)

핵심은 하나입니다. **일일이 말하지 않아도** 이슈의 상태가 라벨·보드·마일스톤에
자동으로 정리됩니다. PM이 "지금 어디쯤이에요?"라는 질문을 받지 않게 됩니다.

![신규개발 파이프라인](../assets/pipeline.png)

## 필요한 것과 없어도 되는 것

| 항목 | 필요 여부 | 없으면 어떻게 되나 |
|---|---|---|
| Python 3 | 필요 | 스크립트가 실행 안 됨. 단, **pip install은 불필요** — 모든 스크립트가 표준 라이브러리만 씁니다 |
| git | hook용으로 권장 | pre-push 자동 검사가 안 됨. `secret-scan.py`를 수동으로 돌리면 됩니다 |
| GitHub 토큰 (PAT) | **필수** | 401 오류로 실패. 아래에서 1분 만에 발급합니다 |
| Muse (muse.ai) | 권장 | 있으면 토큰 발급 빼고 전부 대신 해줍니다. 없으면 터미널에서 직접 실행 |

**가장 쉬운 방법**: muse.ai의 Muse에게 시키세요. 사용자는 GitHub 토큰 하나만 발급하면 됩니다.

## muse.ai에서 설치하기 (3단계)

### 1단계 — Muse에게 스킬 설치 요청

Muse 채팅에 이렇게 말하세요:

> https://github.com/nlook-service/muse-agent-ops 이 스킬을 설치해줘

Muse가 레포를 가져와서 사용할 준비를 합니다.

### 2단계 — GitHub 토큰 발급 (1분)

1. https://github.com/settings/tokens?type=beta 접속
2. **Generate new token** → Fine-grained token
3. 설정:
   - Token name: `muse-agent-ops`
   - Resource owner: 자신의 org 선택
   - Repository access: 적용할 레포 선택
   - Permissions → **Issues: Read and write**
4. 생성된 토큰을 복사

> 토큰은 Muse의 보안 입력(Secure Vault)에 등록하세요. 채팅창에 직접 붙여넣지 마세요.

### 3단계 — Muse에게 적용 요청

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
| `이미 있음: 21` | 이미 설치됨 | 정상. 아무것도 안 바뀜 |
| 한글 라벨이 깨져 보임 | 터미널 인코딩 | UTF-8 터미널 사용 |
