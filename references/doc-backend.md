# 문서 백엔드 가이드

`english-learning`·`trend-curation` 스킬은 만든 문서를 어딘가에 "등록"해야 합니다.
nlook이 없어도 됩니다. 아래 3단계 중 하나를 고르세요.

## 등록 인터페이스

스킬의 "등록" 단계는 이 한 줄로 귀결됩니다:

```
register_document(title, content_markdown, tags[]) -> document_id
```

백엔드는 이 인터페이스만 만족하면 무엇이든 됩니다.

## 옵션 1: 로컬 파일 저장 (백엔드 없음)

가장 간단합니다. 설치도 필요 없습니다.

```bash
# ~/documents/english-study/2026-10-06-07.md 처럼 저장
```

스킬의 "등록" 단계를 "지정한 폴더에 Markdown 파일로 저장"으로 바꾸면 됩니다.

## 옵션 2: nlook MCP (nlook 사용자)

nlook을 쓰면 MCP로 바로 등록됩니다.

```bash
python3 <nlook-mcp.py 경로> call create_document --args \
  '{"title": "...", "content": "...", "tags": ["english-study"]}'
```

- 필요한 연결: nlook MCP 인증 (API 키)
- nlook.me 계정이 있어야 합니다

## 옵션 3: 직접 REST API

쓰고 있는 문서 서비스(노션·자체 API 등)의 문서 생성 엔드포인트를 연결합니다.

```bash
curl -X POST https://api.example.com/documents \
  -H "Authorization: Bearer $DOC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "...", "content": "...", "tags": [...]}'
```

- 필요한 연결: 해당 서비스의 API 토큰 (`DOC_API_TOKEN` 환경변수 권장)
- 스킬의 "등록" 단계에 이 호출을 넣으면 됩니다

## 선택 가이드

| 상황 | 추천 |
|---|---|
| 일단 써보고 싶다 | 옵션 1 (로컬 파일) |
| nlook 계정 있음 | 옵션 2 (nlook MCP) |
| 회사 문서 시스템에 넣고 싶다 | 옵션 3 (REST API) |
