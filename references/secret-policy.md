# 보안 정책 (public 레포 운영)

이 레포는 public이다. 아래 규칙을 어기면 키 유출 사고가 된다.

## 절대 커밋 금지

- API 키·토큰·비밀번호 원문 (어떤 서비스든)
- `-----BEGIN ... PRIVATE KEY-----` 계열
- URL에 인증 정보를 직접 포함한 형태 (예: 호스트 앞에 `사용자:비밀번호@`가 붙은 URL)
- 개인 식별 정보 (주민번호·전화번호·주소 등)
- 내부 전용 엔드포인트·사내 IP (공개해도 되는 것만)

## 대신 이렇게 쓴다

| 금지 | 권장 |
|---|---|
| `GITHUB_TOKEN=ghp_xxx` 하드코딩 | `GITHUB_TOKEN` 환경변수로 읽기 |
| 토큰 값을 문서에 붙여넣기 | "PAT 발급 → 환경변수 설정"手順만 문서화 |
| 실제 계정명·이메일 | `owner/name`, `you@example.com` 같은 플레이스홀더 |

`custom.github` 같은 **인증 참조 이름**은 값이 아니라서 공개해도 된다.

## 3중 방어 프로세스

1. **pre-push hook** — `sh bin/install-hooks.sh` 로 설치. push 전 staged 파일을 자동 검사, 비밀값 의심되면 push 차단.
2. **수동 검사** — push 전 `python3 bin/secret-scan.py` 실행. 종료 코드 0이면 통과.
3. **GitHub Push Protection** — 레포 Settings → Code security → Secret scanning + **Push protection** 활성화. GitHub이 알려진 패턴을 push 시점에 한 번 더 차단.

## 새 스킬을 레포에 추가할 때 체크리스트

1. 스킬 디렉토리를 `skills/<이름>/` 에 복사
2. `python3 bin/secret-scan.py skills/<이름>/` 실행 — 0이어야 함
3. 파일 안의 실제 계정명·경로·토큰 참조를 플레이스홀더로 교체
   - `~/workspace/...` 같은 로컬 절대경로는 `~` 기준 상대 설명으로
   - `custom.xxx` 같은 인증 참조는 유지 가능 (값이 아님)
4. 스킬의 `SKILL.md`에 필요한 권한·환경변수를 문서화
5. push (hook이 자동으로 한 번 더 검사)

## 사고 대응

유출이 의심되면:
1. 해당 키를 **즉시 revoke/재발급** (GitHub에서 push했다고 되돌릴 수 없음 — 히스토리에 남음)
2. 유출 커밋을 `git filter-repo` 등으로 제거 후 force-push
3. 영향 범위 확인 (해당 키로 접근 가능한 리소스 점검)
