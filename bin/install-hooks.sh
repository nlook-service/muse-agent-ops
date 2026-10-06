#!/bin/sh
# pre-push hook 설치: push 전에 bin/secret-scan.py를 자동 실행한다.
# Usage: sh bin/install-hooks.sh   (레포 루트에서 실행)
HOOK=".git/hooks/pre-push"
mkdir -p .git/hooks
cat > "$HOOK" <<'EOF'
#!/bin/sh
# muse-agent-ops pre-push: 비밀값 검사
python3 bin/secret-scan.py --staged
if [ $? -ne 0 ]; then
  echo "pre-push 차단: 비밀값 의심 패턴이 staged 파일에 있습니다."
  exit 1
fi
EOF
chmod +x "$HOOK"
echo "pre-push hook 설치 완료: $HOOK"
