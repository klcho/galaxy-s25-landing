---
name: issue-sync
description: GitHub 이슈를 세션과 즉시 동기화하여 미처리 이슈를 4대 멀티에이전트 파이프라인으로 자율 수주하고 처리하거나 백그라운드 자동 감시를 등록합니다.
allowed-tools:
  - run_command
  - read_file
  - write_file
  - schedule
---

# Issue Sync Skill (/issue-sync)

## When to use this skill
- 사용자가 `/issue-sync`, "이슈 동기화해줘", "대기 이슈 처리해줘"를 입력했을 때 즉시 실행(Instant Run) 모드로 호출합니다.
- 사용자가 `/issue-sync --watch`, "이슈 자동 감시 켜줘"를 입력했을 때 백그라운드 스케줄러(Watcher) 모드로 호출합니다.

## Instructions
1. **[Instant Run 모드]**:
   - `python scripts/issue_worker.py check`로 미처리 이슈 확인.
   - 대기 중인 이슈가 있으면 `harness-v1` 4대 에이전트(PO → Coder → QA → Reporter) 파이프라인을 기동.
   - Worktree 격리 환경(`.worktrees/task-issue-#N`)에서 코드를 수정하고 헤드리스 스크린샷 캡처 후 PR 발행.
   - 메인 대화창에는 **단 2줄 요약 + 로컬 파일 링크만 전달(50토큰 미만)**하여 컨텍스트 보호.
2. **[Watcher 모드 (`--watch`)]**:
   - Antigravity 내장 도구 `schedule(CronExpression="*/2 * * * *", Prompt="새로운 GitHub 이슈가 있는지 확인하고 작업을 시작해줘")`를 등록하여 세션 자동 깨움 설정.

## Workflow
1. `python scripts/issue_worker.py check` 실행하여 대기 이슈 파악.
2. 미처리 이슈(#2 등)가 존재하면 `worktree-coder` 격리 작업 착수.
3. `quality-verifier`가 헤드리스 스크린샷 생성 및 물리적 검증 확인.
4. `release-reporter`가 PR 발행 및 이슈에 GFM/HTML 완료 보고서 게시.
5. 메인 세션에 2줄 초경량 완료 브리핑 출력.
