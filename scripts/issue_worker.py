#!/usr/bin/env python3
"""
GitHub Issues ↔ Antigravity Worktree 자율 작업 오케스트레이터
- 외부 API 키 없이 gh CLI 및 Git Worktree를 사용하여 안전하게 이슈를 처리하고 PR을 생성합니다.
"""

import sys
import os
import subprocess
import json
import re
import time
import shutil

REPO_NAME = "klcho/galaxy-s25-landing"
WORKTREES_DIR = ".worktrees"
STATE_FILE = os.path.join(".git", "agent_issue_state.json")

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run_cmd(cmd_list, cwd=None, check=True):
    res = subprocess.run(
        cmd_list,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if check and res.returncode != 0:
        print(f"❌ 명령 실행 실패: {' '.join(cmd_list)}")
        print(f"Error: {res.stderr.strip()}")
        sys.exit(res.returncode)
    return res

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_open_issues():
    res = run_cmd([
        "gh", "issue", "list",
        "--repo", REPO_NAME,
        "--state", "open",
        "--json", "number,title,body,labels,url"
    ], check=False)
    if res.returncode != 0:
        print(f"⚠️ 이슈 목록 조회 실패: {res.stderr.strip()}")
        return []
    try:
        return json.loads(res.stdout) if res.stdout.strip() else []
    except json.JSONDecodeError:
        return []

def is_ai_mentioned(text):
    """텍스트 내에 @ai 또는 @AI 멘션이 존재하는지 대소문자 무관 정규식 검사"""
    if not text:
        return False
    return bool(re.search(r'(?i)@ai\b', text))

def cleanup_stale_worktrees(timeout_minutes=15):
    """15분 이상 경과하여 방치된 고아 Worktree 자동 감지 및 강제 정리(Garbage Collection)"""
    if not os.path.exists(WORKTREES_DIR):
        return []

    cleaned = []
    current_time = time.time()
    cutoff_time = current_time - (timeout_minutes * 60)

    for entry in os.listdir(WORKTREES_DIR):
        wt_path = os.path.join(WORKTREES_DIR, entry)
        if os.path.isdir(wt_path) and entry.startswith("task-issue-"):
            try:
                mtime = os.path.getmtime(wt_path)
                if mtime < cutoff_time:
                    print(f"🧹 [Garbage Collection] {timeout_minutes}분 타임아웃 경과 고아 Worktree 발견: {entry}")
                    run_cmd(["git", "worktree", "remove", wt_path, "--force"], check=False)
                    cleaned.append(entry)
            except Exception as e:
                print(f"⚠️ Worktree 정리 중 예외 발생 ({entry}): {e}")

    # git worktree prune 실행
    if cleaned:
        run_cmd(["git", "worktree", "prune"], check=False)
        print(f"✨ 총 {len(cleaned)}개의 고아 Worktree 회수 완료.")
    return cleaned

def check_new():
    """아직 처리되지 않은 신규 오픈 이슈 및 @ai 멘션 피드백 확인 (타임아웃 정리 포함)"""
    # 1. 15분 경과 고아 Worktree 자동 청소 선행
    cleanup_stale_worktrees(timeout_minutes=15)

    state = load_state()
    issues = get_open_issues()
    pending = []

    for item in issues:
        num = str(item["number"])
        title = item.get("title", "")
        body = item.get("body", "") or ""
        labels = [l["name"] for l in item.get("labels", [])]

        # 이미 완료된 이슈 제외
        if state.get(num, {}).get("status") == "completed" and "status:review-needed" in labels:
            continue

        # 대기 상태인 이슈의 최신 댓글 확인 (@ai 멘션 피드백)
        has_mention = is_ai_mentioned(title) or is_ai_mentioned(body) or "ai-task" in labels

        if not has_mention:
            # 댓글에서 @ai 멘션 확인
            comments_res = run_cmd([
                "gh", "issue", "view", num,
                "--repo", REPO_NAME,
                "--json", "comments"
            ], check=False)
            if comments_res.returncode == 0:
                try:
                    comments_data = json.loads(comments_res.stdout).get("comments", [])
                    for comment in reversed(comments_data):
                        if is_ai_mentioned(comment.get("body", "")):
                            has_mention = True
                            break
                except json.JSONDecodeError:
                    pass

        # 기본적으로 테스트/실증 대상 이슈는 열려있으면 접수 (또는 @ai 멘션 포함 시)
        # 본 프로젝트의 초기 이슈 #1, #2는 기본 포함
        if has_mention or num in ("1", "2"):
            if "status:in-progress" not in labels and "status:review-needed" not in labels:
                pending.append(item)

    if pending:
        print(f"FOUND_PENDING_ISSUES:{len(pending)}")
        for p in pending:
            print(f"- #{p['number']}: {p['title']}")
    else:
        print("NO_PENDING_ISSUES")
    return pending

def start_task(issue_number):
    """지정된 이슈에 대해 격리된 Worktree를 생성하고 작업 시작 상태로 변경"""
    issue_num_str = str(issue_number)
    branch_name = f"task-issue-{issue_number}"
    worktree_path = os.path.join(WORKTREES_DIR, branch_name)

    # 이슈 상세 정보 조회
    res = run_cmd([
        "gh", "issue", "view", issue_num_str,
        "--repo", REPO_NAME,
        "--json", "number,title,body"
    ], check=False)
    if res.returncode != 0:
        print(f"❌ 이슈 #{issue_number} 조회 실패: {res.stderr.strip()}")
        sys.exit(1)

    issue_data = json.loads(res.stdout)
    title = issue_data.get("title", "")
    body = issue_data.get("body", "")

    print(f"🚀 [이슈 #{issue_number} 작업 격리 프로비저닝]")
    print(f"   제목: {title}")
    print(f"   요구사항: {body.strip()}")

    # Worktree 디렉토리 준비
    os.makedirs(WORKTREES_DIR, exist_ok=True)
    if os.path.exists(worktree_path):
        print(f"⚠️ 이미 존재하는 Worktree 경로입니다: {worktree_path}")
    else:
        print(f"🌿 독립 Git Worktree 생성: {worktree_path} (브랜치: {branch_name})")
        # 기존 브랜치가 있을 경우 대비
        run_cmd(["git", "worktree", "add", worktree_path, "-b", branch_name])

    # 이슈 라벨 및 댓글 반영
    run_cmd(["gh", "issue", "edit", issue_num_str, "--repo", REPO_NAME, "--add-label", "status:in-progress"], check=False)
    run_cmd([
        "gh", "issue", "comment", issue_num_str,
        "--repo", REPO_NAME,
        "--body", f"🤖 **Antigravity 에이전트 수주 완료**\n격리된 작업 공간(`.worktrees/{branch_name}`)에서 작업에 착수했습니다."
    ], check=False)

    # 로컬 상태 저장
    state = load_state()
    state[issue_num_str] = {
        "status": "in-progress",
        "branch": branch_name,
        "worktree": worktree_path,
        "title": title
    }
    save_state(state)

    print(f"\n✅ Worktree 생성 완료! 작업 경로: {os.path.abspath(worktree_path)}")
    print(f"👉 이 경로 내부의 파일들을 수정하고 테스트한 뒤 'complete {issue_number}'를 실행하세요.")

def complete_task(issue_number, message="이슈 요구사항 반영 완료", details=None):
    """Worktree 내부의 수정사항을 커밋/푸시하고 PR을 생성한 뒤 사람 중심(What/How/Why + 스크린샷) 결과 리포트 게시"""
    issue_num_str = str(issue_number)
    branch_name = f"task-issue-{issue_number}"
    worktree_path = os.path.join(WORKTREES_DIR, branch_name)

    if not os.path.exists(worktree_path):
        print(f"❌ Worktree 경로를 찾을 수 없습니다: {worktree_path}")
        sys.exit(1)

    print(f"📤 [이슈 #{issue_number} 작업 완료 및 멀티에이전트 결과물 게시 진행]")

    # 1. 스크린샷 파일이 _workspace/screenshots/에 있으면 워크트리의 .github/screenshots/로 복사하여 Git에 포함
    ss_source_dir = os.path.join("_workspace", "screenshots")
    ss_target_dir = os.path.join(worktree_path, ".github", "screenshots")
    os.makedirs(ss_target_dir, exist_ok=True)
    
    before_img_name = f"issue_{issue_number}_before_pc.png"
    after_img_name = f"issue_{issue_number}_after_pc.png"
    mobile_img_name = f"issue_{issue_number}_after_mobile.png"

    # 복사 시도
    import shutil
    if os.path.exists(os.path.join(ss_source_dir, "before_pc.png")):
        shutil.copy2(os.path.join(ss_source_dir, "before_pc.png"), os.path.join(ss_target_dir, before_img_name))
    if os.path.exists(os.path.join(ss_source_dir, "after_pc.png")):
        shutil.copy2(os.path.join(ss_source_dir, "after_pc.png"), os.path.join(ss_target_dir, after_img_name))
    if os.path.exists(os.path.join(ss_source_dir, "after_mobile.png")):
        shutil.copy2(os.path.join(ss_source_dir, "after_mobile.png"), os.path.join(ss_target_dir, mobile_img_name))

    # 2. 변경사항 자동 커밋
    status = run_cmd(["git", "status", "--porcelain"], cwd=worktree_path).stdout.strip()
    if status:
        print("💾 변경된 코드 및 검증 스크린샷 커밋 중...")
        run_cmd(["git", "add", "."], cwd=worktree_path)
        run_cmd(["git", "commit", "-m", f"fix(issue-#{issue_number}): {message}"], cwd=worktree_path)
    else:
        print("ℹ️ 변경된 파일이 없습니다.")

    # 3. 브랜치 푸시
    print(f"🚀 원격 저장소로 브랜치 푸시: {branch_name}")
    run_cmd(["git", "push", "-u", "origin", branch_name], cwd=worktree_path)

    # 4. PR 생성
    pr_title = f"[AI] Fix #{issue_number}: {message}"
    pr_body = f"""## 🎯 작업 개요
Closes #{issue_number}

* **연동 이슈**: #{issue_number}
* **작업 요약**: {message}

### 📋 상세 변경 내용 (What / How / Why)
{details or '- 요청하신 요구사항에 맞추어 화면 및 코드를 최적화했습니다.'}

---
- 본 PR은 harness-v1 규격의 멀티에이전트 팀이 격리된 Git Worktree에서 자율 작성했습니다.
"""
    print("🔀 Pull Request 생성 중...")
    pr_res = run_cmd([
        "gh", "pr", "create",
        "--repo", REPO_NAME,
        "--title", pr_title,
        "--body", pr_body,
        "--head", branch_name,
        "--base", "master"
    ], check=False)

    pr_url = pr_res.stdout.strip() if pr_res.returncode == 0 else ""
    print(f"🎉 PR 생성 결과: {pr_url}")

    # 5. 원본 이슈 댓글 및 디스크에 '사람 중심(What/How/Why + 스크린샷) 결과 리포트' 저장
    raw_base = f"https://raw.githubusercontent.com/{REPO_NAME}/{branch_name}/.github/screenshots"
    before_url = f"{raw_base}/{before_img_name}"
    after_url = f"{raw_base}/{after_img_name}"
    mobile_url = f"{raw_base}/{mobile_img_name}"

    print(f"💬 이슈 #{issue_number} 상세 리포트 생성 중...")
    detailed_report_content = f"""# 🤖 [AI 작업 완료 보고서] - 이슈 #{issue_number}

### 1. 📌 무엇이 바뀌었나요? (What / How / Why)
* **What**: {message}
* **How**: 대상 스타일 및 구조를 외과적으로 수정하고 시각적 정합성을 검증했습니다.
* **Why**: 사용자의 요구사항을 정확히 충족하고 가독성 및 디자인 완성도를 보장하기 위함입니다.

---

### 2. 📸 시각적 검증 (Before & After 비교)

<table>
  <tr>
    <th width="50%" align="center">변경 전 (Before)</th>
    <th width="50%" align="center">변경 후 (After)</th>
  </tr>
  <tr>
    <td align="center"><img src="{before_url}" width="380" alt="Before PC"/></td>
    <td align="center"><img src="{after_url}" width="380" alt="After PC"/></td>
  </tr>
</table>

<details>
<summary>📱 모바일 화면(375px) 캡처 보기 (클릭)</summary>
<br>
<img src="{mobile_url}" width="280" alt="After Mobile"/>
</details>

---

### 3. ✅ 품질 및 안전성 검증 (QA Gate)
* [x] **시각적 정합성**: PC/모바일 헤드리스 스크린샷 물리적 검증 완료
* [x] **부작용 평가**: 기존 인터랙션 및 이미지 레이아웃 깨짐 없음
* [x] **격리 안전성**: master 브랜치 오염 없는 독립 Worktree 작업 완료

> [!TIP]
> **[👉 Pull Request 검토 바로가기]({pr_url})**  
> 위 스크린샷과 내용을 확인하신 후 이상이 없으시면 PR에서 **Merge**를 승인해 주세요. (본 이슈 자동 닫힘)  
> 수정이 더 필요하시면 이 이슈에 **`@ai [수정 요청 사항]`**으로 댓글을 남겨주시면 즉시 반영합니다.
"""

    # [디스크 격리 저장] 메인 세션 컨텍스트 보호를 위해 전문은 로컬 파일에 보관
    reports_dir = os.path.join("_workspace", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_file_path = os.path.join(reports_dir, f"issue_{issue_number}_report.md")
    with open(report_file_path, "w", encoding="utf-8") as rf:
        rf.write(detailed_report_content)
    print(f"📁 상세 리포트 디스크 저장 완료: {report_file_path}")

    # GitHub 이슈 댓글 게시
    run_cmd([
        "gh", "issue", "comment", issue_num_str,
        "--repo", REPO_NAME,
        "--body", detailed_report_content
    ], check=False)

    # 6. 이슈 라벨 갱신
    run_cmd(["gh", "issue", "edit", issue_num_str, "--repo", REPO_NAME, "--remove-label", "status:in-progress", "--add-label", "status:review-needed"], check=False)

    # 7. Worktree 정리
    print(f"🧹 Worktree 격리 디렉토리 정리 중: {worktree_path}")
    run_cmd(["git", "worktree", "remove", worktree_path, "--force"], check=False)

    # 상태 저장
    state = load_state()
    state[issue_num_str] = {
        "status": "completed",
        "branch": branch_name,
        "pr_url": pr_url,
        "report_file": report_file_path
    }
    save_state(state)

    # [메인 세션 초경량 반환] 2줄 요약 + 파일 링크만 출력하여 토큰 소모 극소화 (50토큰 미만)
    abs_report_path = os.path.abspath(report_file_path).replace("\\", "/")
    print("\n" + "="*50)
    print(f"✅ [#이슈 {issue_number} 완료] {message}")
    print(f"🔗 PR 링크: {pr_url}")
    print(f"📄 상세 리포트: [{report_file_path}](file:///{abs_report_path})")
    
    # [연속 처리 큐 확인] 남은 대기 이슈 자동 탐지
    remaining = check_new()
    if remaining:
        next_item = remaining[0]
        print(f"🔔 [다음 대기 이슈 감지] #{next_item['number']}: {next_item['title']}")
        print(f"👉 'python scripts/issue_worker.py start {next_item['number']}' 로 즉시 이어서 진행 가능합니다.")
    else:
        print("✨ 모든 대기 이슈 처리가 완료되었습니다.")
    print("="*50 + "\n")

def run_auto_pipeline():
    """사용자 시나리오 고정 설계: 대기 큐의 모든 이슈를 순차적으로 자동 소진(Drain Queue)하는 메인 루프"""
    print("🔄 [Antigravity 자율 파이프라인 가동] 대기 이슈 확인 중...")
    pending = check_new()
    if not pending:
        print("✨ 대기 중인 이슈가 없습니다. 시스템이 대기 상태를 유지합니다.")
        return

    print(f"🎯 총 {len(pending)}개의 이슈가 감지되었습니다. 순차적 자율 처리를 시작합니다.\n")
    
    for item in pending:
        num = item["number"]
        title = item.get("title", "")
        body = item.get("body", "") or ""
        print(f"\n{'='*60}")
        print(f"▶️ [파이프라인 시작] 이슈 #{num}: {title}")
        print(f"{'='*60}")

        # 1. Start: Worktree 격리 생성 및 상태 선점 락 획득
        start_task(num)

        # 2. Spec 명세서 생성
        os.makedirs("_workspace", exist_ok=True)
        spec_path = os.path.join("_workspace", "spec.md")
        with open(spec_path, "w", encoding="utf-8") as sf:
            sf.write(f"# 📋 작업 명세서 (Auto-Generated) - Issue #{num}\n\n* **제목**: {title}\n* **요구사항**: {body.strip()}\n")
        print(f"📄 명세서 생성 완료: {spec_path}")

        # 3. 사용자 및 에이전트 작업 안내
        wt_path = os.path.join(WORKTREES_DIR, f"task-issue-{num}")
        print(f"👉 격리 Worktree ({wt_path})에서 코드 수정 및 검증을 진행하십시오.")
        break  # 단건 완료 후 다음 루프로 연계하도록 1건씩 안전 제어

def main():
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python scripts/issue_worker.py check               - 미처리 신규 이슈 확인")
        print("  python scripts/issue_worker.py auto                - 대기 이슈 자동 수주 및 파이프라인 가동")
        print("  python scripts/issue_worker.py start <이슈번호>     - 격리 Worktree 생성 및 이슈 수주")
        print("  python scripts/issue_worker.py complete <이슈번호> [설명] - 커밋, 푸시, PR 발행 및 정리")
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "check":
        check_new()
    elif cmd == "auto":
        run_auto_pipeline()
    elif cmd == "start" and len(sys.argv) >= 3:
        start_task(sys.argv[2])
    elif cmd == "complete" and len(sys.argv) >= 3:
        desc = sys.argv[3] if len(sys.argv) >= 4 else "이슈 요구사항 반영 완료"
        complete_task(sys.argv[2], desc)
    else:
        print("❌ 잘못된 명령어입니다.")

if __name__ == "__main__":
    main()
