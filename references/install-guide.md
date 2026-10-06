# 설치 가이드

5분이면 팀 레포에 같은 PM 프로세스를 깔 수 있다.

## 준비물

- Python 3.8+
- GitHub fine-grained PAT (권한: **Issues Read and write**)
  - Settings → Developer settings → Personal access tokens → Fine-grained tokens
  - Resource owner: 해당 org 선택
  - Repository access: 적용할 레포 선택 (또는 All repositories)

## 설치

```bash
git clone https://github.com/nlook-service/muse-agent-ops.git
cd muse-agent-ops
export GITHUB_TOKEN=github_pat_xxx   # 토큰은 환경변수로만, 코드에 넣지 말 것

# 라벨 세트 21개 설치 (멱등 — 이미 있으면 건너뜀)
python3 bin/setup.py --repo my-org/my-repo
```

출력 예:

```
생성: 21, 이미 있음: 0, 실패: 0
  + 분야:기획
  + 분야:개발
  ...
```

## 쉬운 사용법

### 주간 점검 (dry-run — 바꾸지 않고 보여주기만)

```bash
python3 bin/hygiene.py --repo my-org/my-repo
```

```
=== 점검 결과: 3건 ===
#12 [기획] 온보딩 개선
   - 마일스톤 지정 제안: 기획 10월
#34 [개발] 결제 버그
   - 단계 라벨 정리 필요: 현재 [] → 1개로

dry-run 모드. 적용하려면 --apply를 붙여 실행.
```

### 실제 적용

```bash
python3 bin/hygiene.py --repo my-org/my-repo --apply
```

분야 라벨은 제목의 `[태그]`로 자동 추론해서 붙인다.
마일스톤·단계 라벨은 제안만 하고, 확인 후 수동으로 적용하는 것을 권장한다.

### cron에 걸어 자동 운영하기

```bash
# 매 3시간마다 점검 (결과는 로그로)
0 */3 * * * cd /path/to/muse-agent-ops && GITHUB_TOKEN=ghp_xxx python3 bin/hygiene.py --repo my-org/my-repo --apply >> ops.log 2>&1
```

## 레포별 커스터마이징

- 라벨 색상·문구는 `bin/setup.py` 상단의 `LABELS` 리스트에서 바꾼다.
- 분야 라벨을 팀에 맞게 추가/삭제해도 된다. 단, `단계:*` 4개는 파이프라인의 핵심이라 유지 권장.
- 마일스톤 명명 규칙(`기획 10월` 형식)은 `bin/hygiene.py`의 `STAGE_MILESTONE`에서 바꾼다.
