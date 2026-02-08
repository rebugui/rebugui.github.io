#!/bin/bash
echo "Hugo 서버 시작 중..."
hugo server --buildDrafts --buildFuture &
HUGO_PID=$!

echo "서버가 시작될 때까지 기다리는 중..."
sleep 5

echo "Hugo 로컬 서버가 시작되었습니다!"
echo "URL: http://localhost:1313"
echo ""
echo "테스트할 페이지:"
echo "- LiteBox: http://localhost:1313/p/-LiteBox-Rust-기반-라이브러리-OS로-공격-표면-최소화/"
echo ""
echo "Ctrl+C로 서버를 중지하세요."

# Hugo 프로세스가 종료될 때까지 대기
wait $HUGO_PID
