---
name: "claude-keepalive"
description: "Claude Code 원격 세션을 24/7 살아있게 유지한다. 세션이 죽으면 자동 재시작하고 workspace trust 프롬프트를 자동 확인한다."
---

# claude-keepalive

## Purpose
Claude Code 원격 세션(iPhone 등에서 접속하는 코딩 세션)이
VM 재시작 등으로 죽어도 자동으로 살아나게 한다.
사용 중인 기기가 꺼져 있어도 24/7 원격 코딩이 가능해진다.

## Tooling
- `bin/keepalive.sh` — 5분마다 실행되는 감시 스크립트 (의존성: `tmux`, `pgrep`)

## 동작 방식

1. tmux 세션 `claude` 와 claude 프로세스가 살아있는지 확인
2. 살아있으면 종료 (아무것도 안 함)
3. 죽어있으면:
   - 기존 세션 정리 후 `claude --continue` 로 새 tmux 세션 시작 (이전 대화 이어서)
   - workspace trust 프롬프트("Is this a project you created")가 뜨면 자동 확인
   - 재시작 성공/실패를 로그에 기록
4. single-instance guard (lock dir)로 중복 실행 방지

## 설치

```bash
# 1. 스크립트 배치
mkdir -p ~/workspace/claude-keepalive
cp bin/keepalive.sh ~/workspace/claude-keepalive/
chmod +x ~/workspace/claude-keepalive/keepalive.sh

# 2. cron에 5분마다 등록
crontab -e
# */5 * * * * $HOME/workspace/claude-keepalive/keepalive.sh
```

## 설정 변경

스크립트 상단의 변수를 고친다:

| 변수 | 기본값 | 설명 |
|---|---|---|
| `CLAUDE_BIN` | `$HOME/.local/bin/claude` | Claude Code 바이너리 경로 |
| `SESSION` | `claude` | tmux 세션 이름 |
| `LOG` | `~/workspace/claude-keepalive/keepalive.log` | 로그 파일 |

## Operating Rules
1. 로그는 주기적으로 확인한다 (`tail keepalive.log`)
2. `restart FAILED` 가 보이면 수동으로 세션 상태를 확인한다
3. Claude 인증(OAuth)이 만료되면 스크립트로 해결 안 됨 — `claude auth login` 으로 재인증 필요
4. 세션을 의도적으로 끈 경우 keepalive가 다시 살리므로, 끄려면 cron도 함께 중지한다

## 로그 예시

```
2026-10-06 10:05:01 session down — restarting claude with --continue
2026-10-06 10:05:31 confirmed workspace trust prompt
2026-10-06 10:05:31 restart ok
```
