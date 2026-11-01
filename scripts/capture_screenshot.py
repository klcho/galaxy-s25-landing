#!/usr/bin/env python3
"""
헤드리스 브라우저 스크린샷 캡처 도구 (Zero-Setup)
- Windows 내장 Edge 또는 Chrome 헤드리스 모드를 사용하여 별도 패키지 설치 없이 즉시 웹페이지를 캡처합니다.
- PC 뷰포트(1280x800) 및 모바일 뷰포트(375x812)를 지원합니다.
"""

import sys
import os
import subprocess
import time
import http.server
import socketserver
import threading

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def find_browser_executable():
    """시스템에 설치된 Edge 또는 Chrome 실행 경로 탐색"""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 로깅 억제

def start_temp_server(serve_dir):
    """임시 로컬 HTTP 서버 기동 (포트 8765)"""
    port = 8765
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=serve_dir, **kwargs)
    
    # 이미 사용 중인 포트 대비 재시도
    for p in range(8765, 8780):
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", p), handler)
            port = p
            break
        except OSError:
            continue
            
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port

def capture_page(browser_path, url, output_path, width, height):
    """지정된 크기로 헤드리스 캡처 수행"""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cmd = [
        browser_path,
        "--headless=new",
        f"--screenshot={os.path.abspath(output_path)}",
        f"--window-size={width},{height}",
        "--hide-scrollbars",
        "--disable-gpu",
        "--no-sandbox",
        url
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return os.path.exists(output_path)

def main():
    if len(sys.argv) < 3:
        print("사용법: python scripts/capture_screenshot.py <웹페이지_디렉토리> <이름_접두사> [출력_폴더]")
        print("예시: python scripts/capture_screenshot.py . before _workspace/screenshots")
        sys.exit(1)

    target_dir = os.path.abspath(sys.argv[1])
    prefix = sys.argv[2]
    out_dir = os.path.abspath(sys.argv[3]) if len(sys.argv) >= 4 else os.path.abspath("_workspace/screenshots")

    browser = find_browser_executable()
    if not browser:
        print("⚠️ 지원되는 브라우저(Edge, Chrome)를 찾지 못했습니다. 스크린샷 캡처를 건너뜁니다.")
        sys.exit(0)

    # 임시 서버 기동
    httpd, port = start_temp_server(target_dir)
    url = f"http://127.0.0.1:{port}/index.html"
    time.sleep(0.5)

    pc_out = os.path.join(out_dir, f"{prefix}_pc.png")
    mobile_out = os.path.join(out_dir, f"{prefix}_mobile.png")

    print(f"📸 화면 캡처 중... (Target: {target_dir})")
    pc_ok = capture_page(browser, url, pc_out, 1280, 800)
    mobile_ok = capture_page(browser, url, mobile_out, 375, 812)

    httpd.shutdown()

    if pc_ok and mobile_ok:
        print(f"✅ 캡처 완료!")
        print(f"   - PC: {pc_out}")
        print(f"   - Mobile: {mobile_out}")
    else:
        print("⚠️ 일부 뷰포트 캡처에 실패했습니다.")

if __name__ == "__main__":
    main()
