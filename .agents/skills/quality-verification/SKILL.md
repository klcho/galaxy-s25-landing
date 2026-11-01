---
name: quality-verification
description: 헤드리스 브라우저를 구동하여 Before & After 스크린샷을 물리적으로 캡처하고 린트 및 시각적 정합성을 독립 교차 검증할 때 사용합니다.
allowed-tools:
  - run_command
  - read_file
  - write_file
---

# Quality Verification Skill

## When to use this skill
- `worktree-coder`가 코드 수정을 마치고 검증을 요청했을 때, 또는 릴리스 전 품질 증거를 확보할 때 호출합니다.

## Instructions
1. **[QA Gate 강제 규칙]**: 에이전트는 절대 추측으로 "정상 작동한다"고 단언할 수 없습니다. 반드시 디스크에 물리적 증거(스크린샷 이미지)를 남겨야 합니다.
2. `scripts/capture_screenshot.py`를 실행하여 PC 뷰포트(1280px)와 모바일 뷰포트(375px)의 화면을 캡처하고, `_workspace/screenshots/` 및 워크트리 내 `.github/screenshots/`에 저장하십시오.
3. 수정 전(Before)과 수정 후(After)의 이미지가 실제로 생성되었는지 `view_file` 또는 파일 시스템 검사로 반드시 교차 확인(Fact Check)하십시오.
4. 문법 오류, 스타일 깨짐, 가독성 저하가 발견되면 구체적 원인과 함께 `worktree-coder`에게 즉시 반려(REJECT)하십시오.
5. 모든 검증을 통과한 경우에만 `release-reporter`에게 릴리스 승인(PASS)을 전달하십시오.

## Workflow
1. 워크트리 내부 정적 파일 대상 구문/린트 유효성 검증.
2. `python scripts/capture_screenshot.py <워크트리경로> <이슈번호>` 실행하여 Before/After 스크린샷 캡처.
3. 캡처된 이미지 파일 존재 여부 물리적 확인.
4. 검증 결과 로그를 `_workspace/qa_report.md`에 기록.
5. 합격 시 `release-reporter`에게 배포 핸드오프.
