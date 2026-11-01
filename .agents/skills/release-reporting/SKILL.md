---
name: release-reporting
description: 원격 브랜치 푸시 및 PR 발행, 원본 이슈에 사람이 읽는 GFM/HTML 완료 보고서 게시 및 Worktree를 안전하게 회수할 때 사용합니다.
allowed-tools:
  - run_command
  - read_file
  - write_file
---

# Release Reporting Skill

## When to use this skill
- `quality-verifier`의 물리적 검증 승인을 획득한 후, 원격에 작업을 반영하고 사용자에게 완료 보고서를 게시할 때 호출합니다.

## Instructions
1. `quality-verifier`의 스크린샷과 검증 리포트가 디스크에 존재하는지 우선 확인하십시오. 증거가 없으면 작업을 중단하십시오.
2. 워크트리 내부의 커밋을 원격 저장소(`origin/task-issue-#N`)로 푸시하고 `gh pr create`로 Pull Request를 발행하십시오 (본문에 `Closes #N` 필수 포함).
3. 원본 GitHub 이슈 댓글에 [AI 작업 완료 보고서]를 게시하고, 전문을 `_workspace/reports/issue_#N_report.md`에 저장하십시오:
   * **What**: 무엇이 바뀌었는지 사용자 관점에서 명확히 설명
   * **How**: 어떤 파일과 방식을 적용했는지 설명
   * **Why**: 왜 그렇게 변경했는지(사용자 요구 및 가독성 충족) 설명
   * **Before & After 스크린샷**: HTML `<table>`로 나란히 배치
   * **PR 검토 안내**: `> [!TIP]` 블록으로 PR 링크 및 `@ai` 피드백 안내
   * ⚠️ **주의**: 코드 Diff는 절대 포함하지 마십시오.
4. **[메인 세션 컨텍스트 보호]**: 메인 대화창에는 장황한 리포트 전문을 출력하지 말고, 오직 **2줄 요약과 파일 링크(`[report.md](file:///...)`)**만 초경량으로 전달하여 메인 토큰을 50토큰 미만으로 절약하십시오.
5. 이슈 라벨을 `status:review-needed`로 전환하고, 로컬 Worktree 디렉토리를 안전하게 삭제(`git worktree remove`)하십시오.
6. `_workspace/progress_tracker.md`의 진행 상태를 'Completed'로 갱신하십시오.

## Workflow
1. 원격 푸시 및 PR 생성 (`gh pr create`).
2. GFM & HTML 완료 보고서 마크다운 조합.
3. 이슈 댓글 게시 (`gh issue comment`).
4. 라벨 갱신 (`status:review-needed`).
5. Worktree 정리 (`git worktree remove`) 및 추적기 완료 기록.
