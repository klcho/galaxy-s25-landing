---
name: issue-triage
description: GitHub 이슈와 @ai 멘션을 감지하여 요구사항을 분석하고 _workspace/spec.md 작업 계약서를 작성할 때 사용합니다.
allowed-tools:
  - run_command
  - write_file
  - read_file
---

# Issue Triage Skill

## When to use this skill
- GitHub 저장소에 새로운 이슈가 등록되었거나, 기존 이슈에 `@ai` 멘션 댓글이 작성되었을 때 호출합니다.
- 모호한 사용자 요구사항을 명확히 하고 공식 작업 명세서(`_workspace/spec.md`)를 도출해야 할 때 사용합니다.

## Instructions
1. `gh issue list` 및 `gh issue view`를 통해 이슈의 번호, 제목, 본문, 최근 댓글을 확인합니다.
2. 댓글이나 본문에 `(?i)@ai\b` 정규식 기반 `@ai` (대소문자 무관) 멘션이 포함되어 있는지 엄격히 검사합니다. 일반 사람 간의 대화나 이메일 주소(`user@domain.com`)에는 절대 오반응하지 마십시오.
3. 15분 이상 경과한 비정상 고아 Worktree가 발견되면 `cleanup_stale_worktrees`로 자동 회수(Garbage Collection)를 수행합니다.
4. 요구사항이 불명확하거나 상충되는 경우 작업을 시작하지 말고, `gh issue comment`로 명확화 질문을 게시하고 이슈 라벨을 `status:waiting-feedback`으로 전환하십시오.
5. 요구사항이 명확한 경우, `_workspace/spec.md` 파일을 물리적으로 생성하여 작업 목표, 수정 대상 파일, 완료 기준을 명시하십시오.

## Workflow
1. `python scripts/issue_worker.py check` 실행하여 미처리 이슈 식별.
2. 이슈 세부 요구사항 파악 후 `_workspace/spec.md` 작성.
3. `_workspace/progress_tracker.md` 파일의 진척도를 'In Progress'로 업데이트.
4. `worktree-coder`에게 명세서 전달 및 작업 착수 요청.
