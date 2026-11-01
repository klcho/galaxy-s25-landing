#!/usr/bin/env python3
"""
GitHub Actions CI 실패 로그 분석기
- 실패 로그를 분석하여 AI 피드백(원인, 위치, 구체적 수정 권고)을 생성합니다.
- 외부 라이브러리 의존성 없이 Python 표준 라이브러리(urllib, json)만 사용합니다.
"""

import sys
import os
import json
import urllib.request
import urllib.error

# Windows 터미널 cp949 인코딩 문제 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def analyze_log_with_gemini(api_key: str, error_log: str) -> str:
    # 2.5-flash 또는 1.5-flash 엔드포인트
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""당신은 엄격하고 명확한 소프트웨어 품질 엔지니어이자 코드 리뷰어 AI입니다.
아래는 GitHub Actions CI 검증 단계에서 발생한 정적 분석/린트 실패 로그입니다.

[실패 로그]
{error_log}

위 로그를 분석하여 개발자 및 후속 작업을 담당할 AI 에이전트를 위한 검증 실패 보고서를 한국어로 작성하세요.
보고서는 다음 구조를 갖추어야 합니다:
1. 🚨 **실패 원인 요약**: 무엇 때문에 CI가 실패했는지 핵심 1~2줄 요약
2. 🔍 **오류 발생 위치 및 세부 내용**: 문제 파일명, 라인 번호, 위반 규칙
3. 🛠️ **해결을 위한 구체적 수정 가이드**: 어떻게 코드를 수정해야 하는지 구체적인 코드 예시(Diff) 포함

Markdown 형식으로만 출력하세요. 불필요한 서두나 사족은 제외하세요.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048
        }
    }

    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            return "AI 분석 결과를 추출하지 못했습니다."
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore')
        return f"> ⚠️ **Gemini API 호출 실패 (HTTP {e.code})**\n> `{err_body[:200]}`\n\n### 원시 실패 로그:\n```\n{error_log[:1500]}\n```"
    except Exception as e:
        return f"> ⚠️ **AI 분석 스크립트 실행 오류**: {str(e)}\n\n### 원시 실패 로그:\n```\n{error_log[:1500]}\n```"

def main():
    if len(sys.argv) <= 1 or sys.argv[1] in ("-h", "--help"):
        print("사용법: python scripts/analyze_failure.py <로그파일경로|로그문자열>")
        print("  또는: python scripts/analyze_failure.py --stdin")
        sys.exit(0)

    if sys.argv[1] == "--stdin":
        error_log = sys.stdin.read()
    elif os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
            error_log = f.read()
    else:
        error_log = sys.argv[1]

    if not error_log.strip():
        error_log = "실패 로그 내용이 비어 있습니다."

    # 로그 길이 과도 방지 (앞뒤 8000자 제한)
    if len(error_log) > 8000:
        error_log = error_log[:4000] + "\n\n... (중략) ...\n\n" + error_log[-4000:]

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    
    output_md = []
    output_md.append("## 🤖 CI 검증 실패 - AI 자동 피드백 리포트\n")
    
    if api_key:
        analysis = analyze_log_with_gemini(api_key, error_log)
        output_md.append(analysis)
    else:
        output_md.append("> ℹ️ `GEMINI_API_KEY`가 설정되지 않아 규칙 기반 기본 요약 리포트를 제공합니다. "
                         "GitHub Repository Secrets에 `GEMINI_API_KEY`를 추가하면 AI 심층 분석이 활성화됩니다.\n")
        output_md.append("### 📋 검증 실패 로그 요약\n```\n" + error_log[:2000] + "\n```")

    report_content = "\n".join(output_md)
    
    # 출력 파일 지정 여부 확인
    output_file = os.environ.get("REPORT_OUTPUT_PATH")
    if output_file:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_content)
    
    print(report_content)

if __name__ == "__main__":
    main()
