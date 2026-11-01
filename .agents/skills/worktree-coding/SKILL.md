---
name: worktree-coding
description: 메인 브랜치를 완벽히 보호하기 위해 .worktrees/ 하위에 독립 Git Worktree를 생성하고 명세서에 따라 외과적 수정을 수행할 때 사용합니다.
allowed-tools:
  - run_command
  - edit_file
  - write_file
  - read_file
---

# Worktree Coding Skill

## When to use this skill
- `issue-triage-po`로부터 작업 명세서(`_workspace/spec.md`)를 전달받아 실제 코드 구현 및 수정 작업을 착수할 때 사용합니다.

## Instructions
1. 로컬 `master` 워킹 트리는 어떠한 경우에도 직접 건드리지 마십시오.
2. `git worktree add .worktrees/task-issue-#N -b task-issue-#N` 명령어로 독립 작업 디렉토리를 생성하십시오.
3. `.worktrees/task-issue-#N` 내부의 소스 파일만을 대상으로 `_workspace/spec.md`에 명시된 요구사항을 외과적으로 수정하십시오.
4. 불필요한 리팩터링이나 주석 변경을 절대 금지합니다.
5. 수정 완료 후 워크트리 내부에서 구문 문법 검사(`node -c` 등)를 실행하여 1차 정합성을 확인한 뒤 커밋하십시오.

## Workflow
1. `python scripts/issue_worker.py start <이슈번호>` 실행하여 Worktree 환경 프로비저닝.
2. `.worktrees/task-issue-#N/` 하위 소스 파일 외과적 수정.
3. 1차 기초 문법 및 린트 검사 실행.
4. 변경 사항 Git 커밋 (`git -C .worktrees/... commit -m "..."`).
5. `quality-verifier`에게 시각 검증 및 QA Gate 심사 요청.
