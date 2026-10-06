# nlook MCP API 활용 가이드

muse-agent-ops를 nlook MCP와 연결하면, 에이전트가 GitHub API를 직접 두드리지 않고도
nlook 안에서 운영 상태를 확인·기록할 수 있다.

## 지금 nlook MCP에 있는 것

`python3 ~/workspace/skills/nlook/bin/nlook-mcp.py tools` 로 확인 가능. 주요 도구:

| 도구 | 용도 |
|---|---|
| `create_document` / `get_document` / `update_document` / `list_documents` | 문서 CRUD |
| `create_task` / `list_tasks` / `get_task` | 작업 관리 |
| `admin_inquiries` / `admin_reply_inquiry` | 고객 문의 처리 |

## agent-ops에 유용한 MCP 도구 추가 제안

nlook 서버에 아래 도구들을 추가하면 운영이 훨씬 매끄러워진다:

### 1. `ops_digest` — 운영 현황판

GitHub 이슈 상태를 nlook 문서로 요약해서 돌려주는 읽기 전용 도구.

```
ops_digest { repo: "nlook-service/nlook" }
→ {
    by_stage: { "단계:기획중": 3, "단계:디자인중": 1, "단계:개발대기": 2, ... },
    blocked: [ {number, title, reason} ],   # 직접확인필요·기간 초과
    updated_at: "..."
  }
```

에이전트가 아침 브리핑·주간 계획에서 매번 GitHub API를 조합하지 않아도 된다.

### 2. `ops_log` — 운영 기록

PM 판단(단계 전환·마일스톤 이동 등)을 nlook 문서로 남기는 도구.
"왜 이 이슈가 개발대기로 갔는지"의 근거가 nlook에 쌓인다.

### 3. `ops_remind` — 리마인드 등록

`직접확인필요` 라벨이 붙은 이슈를 nlook task로 등록해 walter님에게 알리는 도구.

## MCP에 도구를 추가하는 방법 (nlook 서버 측)

1. nlook 레포에서 MCP 도구 정의 위치를 찾는다 (JSON-RPC `tools/list`에 노출되는 레지스트리)
2. 새 도구는 **읽기 전용부터** 시작한다. 쓰기 도구는 `admin_` 접두 + 권한 체크를 붙인다
3. 도구 설명(description)에 언제 쓰는지 명시한다 — 에이전트가 도구를 고르는 기준이 된다
4. 배포 후 `nlook-mcp.py tools` 로 노출 확인

## 보안 주의

- MCP 도구에 GitHub PAT를 직접 넣지 않는다. 서버 측 시크릿 관리(Vaultwarden 등)에서 주입한다
- 쓰기 도구는 반드시 호출자 권한을 확인한다
- `ops_digest` 같은 집계 도구는 캐시를 둔다 (GitHub API rate limit 대비)
