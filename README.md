# muse-agent-ops

전체 에이전트 운영을 하나의 스킬로 묶은 오픈소스 운영 키트.
Muse가 일상 업무에 쓰는 스킬들을 public으로 안전하게 공유하기 위한 저장소다.

## 구성

```
muse-agent-ops/
├── SKILL.md                  # 이 스킬의 정의
├── README.md
├── LICENSE (MIT)
├── bin/
│   ├── setup.py              # PM 라벨 세트 설치 (GitHub)
│   ├── hygiene.py            # 이슈 위생 점검 (dry-run 기본)
│   ├── secret-scan.py        # 비밀값 사전 감지
│   └── install-hooks.sh      # pre-push hook 설치
├── references/
│   ├── process.md            # 신규개발 파이프라인 정의
│   ├── install-guide.md      # 설치 가이드 + 쉬운 사용법
│   ├── nlook-mcp-guide.md    # nlook MCP API 활용 가이드
│   └── secret-policy.md      # 보안 정책 (필독)
└── skills/                   # 공개용 스킬 모음 (추가 중)
```

## 빠른 시작

```bash
git clone https://github.com/nlook-service/muse-agent-ops.git
cd muse-agent-ops

# 보안 hook 먼저 설치 (push 전 비밀값 자동 차단)
sh bin/install-hooks.sh

# PM 라벨 세트를 내 레포에 설치
export GITHUB_TOKEN=github_pat_xxx
python3 bin/setup.py --repo owner/name

# 이슈 위생 점검 (dry-run)
python3 bin/hygiene.py --repo owner/name
```

자세한 건 `references/install-guide.md`.

## 보안

public 레포라서 보안 프로세스가 내장되어 있다:

1. **pre-push hook** — push 전 staged 파일에서 비밀값 의심 패턴을 자동 차단
2. **수동 검사** — `python3 bin/secret-scan.py`
3. **GitHub Push Protection** — 레포 Settings → Code security에서 활성화 권장

새 스킬을 추가할 때는 `references/secret-policy.md`의 체크리스트를 따른다.

## 라이선스

MIT
