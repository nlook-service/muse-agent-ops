# 에이전트 라우터 (agent-router)

무거운 작업을 외부 에이전트(Claude Code 세션, Codex CLI 등)에 위임해
메인 에이전트의 토큰 사용량을 분산하는 패턴.

## 왜 필요한가

스케줄러(cron)에서 도는 문서 등록·콘텐츠 생성 같은 작업은
리서치와 원고 작성이 토큰의 대부분을 차지한다.
실행만 외부에 넘기고, 스케줄러 측은 얇은 디스패처(브리프 전달·결과 확인)로 두면
같은 결과를 훨씬 적은 토큰으로 얻을 수 있다.

## 구성

| 파일 | 역할 |
|---|---|
| `bin/agent-router.py` | 위임 실행 스크립트 (전달 + 대기 + 타임아웃 판정) |
| `config.example.yaml` | 설정 예시 (복사해서 `config.yaml`로 사용) |

## 설정 (`config.yaml`)

```yaml
default_external: claude   # claude | chatgpt

agents:
  muse:
    kind: builtin
    status: ready
  claude:
    kind: tmux
    session: claude         # tmux 세션 이름
    idle_marker: "❯"       # 대기 중 판정 문자열
    strengths: [긴 글 창작·리라이팅, 분석·리서치]
    status: ready
  chatgpt:
    kind: codex_exec
    command: codex
    strengths: [코드 작성·리뷰, 기술적 추론]
    status: not_configured  # `codex login` 후 ready

load_balancing:
  enabled: true
  muse_usage_high_threshold: 70
  muse_usage_critical_threshold: 90

fallback:
  no_response_timeout_min: 10
  poll_interval_sec: 30
  on_timeout: muse_takes_over
  on_busy: muse_decides
```

## 라우팅 기준

- **가벼운 작업** (조회·짧은 답변·정해진 파이프라인): 메인 에이전트가 직접
- **무거운 작업** (깊은 창작·전면 리라이팅·분석·설계): 외부 에이전트
- 사용량이 `high` 이상이면 중간 작업도 외부로, `critical`이면 전부 외부 고려
- 외부 중 선택: 작업 역량에 맞는 쪽 (창작→Claude, 코드→ChatGPT), 기본값은 `default_external`
- 사용자가 지목하면 ("클로드에게", "챗GPT에게") 지목 우선

## 위임 실행

```bash
# 브리프 전달 + 결과 대기 (타임아웃 시 종료 코드 2)
python3 bin/agent-router.py --config config.yaml \
  --brief briefs/task.md --expect out/task.done --timeout-min 10

# 작업 무게로 추천만 받기
python3 bin/agent-router.py --config config.yaml \
  --suggest --weight heavy --capability creative --task "블로그 원고 리라이팅"

# 상태만 확인 / 미리보기
python3 bin/agent-router.py --config config.yaml --check --expect out/task.done --since 2026-10-06T15:50:00
python3 bin/agent-router.py --config config.yaml --dry-run --brief briefs/task.md --expect out/task.done
```

종료 코드: 0=전달됨, 2=무응답(폴백: 직접 처리), 3=세션 작업 중, 4=미설정.

## 스케줄러 연동 패턴

크론 본문을 디스패처로 바꾼다:

1. (필요시) 메인 에이전트 전용 도구로 원자료만 수집해 파일에 저장
2. `agent-router.py --brief <브리프> --expect <결과파일> --timeout-min <N>` 실행
3. 종료 코드별 처리:
   - 0 → 결과 파일 요약 확인 후 원래 보고 규칙대로 종료
   - 2/3 → 폴백: 직접 수행 (브리프 내용 그대로)
   - 4 → 직접 수행 + 사용자에게 미설정 알림

브리프는 외부 에이전트가 독립적으로 실행할 수 있게 자족적으로 쓴다:
"오늘"은 읽는 시점, 쓸 수 있는 CLI를 명시, 결과 요약 파일 기록을 의무화.

## 주의

- tmux 세션이 작업 중이면 주입하지 않는다 (사용자 작업 방해 금지) → 종료 코드 3
- 브리프에 비밀값을 넣지 않는다 (`secret-scan.py`로 검사)
- 외부 에이전트의 결과물은 스팟 체크한다 (전수 검수는 토큰 낭비)
