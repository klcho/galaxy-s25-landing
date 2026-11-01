# GitHub Issues ↔ Antigravity 자율 작업 자동화 시스템 도입 구현 계획서

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 별도 외부 API 키 없이, GitHub Issues에 등록되는 작업을 Antigravity 에이전트가 격리된 Git Worktree에서 자율 수행하고, What/How/Why 리포트와 Before/After 스크린샷을 첨부하여 PR을 발행하는 '무인 이슈 라이프사이클 자동화 시스템'을 저장소에 도입한다.

**Architecture:** 
1. 이슈 감시 및 상태 관리자(`scripts/issue_worker.py`)가 `@ai` 멘션 및 신규 이슈를 감지하여 독립된 `.worktrees/task-issue-#N`을 프로비저닝.
2. 서브에이전트(`invoke_subagent`)가 격리된 Worktree에서 코드를 외과적으로 수정하고 헤드리스 브라우저(`scripts/capture_screenshot.py`)로 Before/After 스크린샷 캡처.
3. 코드 Diff 대신 사람 중심(What/How/Why) 보고서와 시각적 스크린샷 테이블(GFM/HTML)을 이슈 댓글로 게시하고 PR을 생성한 뒤 Worktree 자동 회수.

**Tech Stack:** Python 3 (표준 라이브러리), GitHub CLI (`gh`), Git Worktrees, Playwright / Chrome Headless (스크린샷), GitHub Actions (CI)

**Spec:** docs/superpowers/plans/2026-11-01-github-issue-antigravity-automation.md

---

## Global Constraints

- **무비용 원칙**: 외부 유료/무료 LLM API Key(Gemini API 등)를 사용하지 않고 현재 Antigravity 및 GitHub 무료 인프라만 사용.
- **메인 브랜치 불변성**: 로컬 `master` 워킹 트리는 직접 수정하지 않으며, 모든 작업은 반드시 `.worktrees/` 하위 격리 환경에서 수행.
- **트리거 안전성**: 이슈 본문 또는 댓글에 `@ai` (대소문자 무관) 멘션이 포함된 경우에만 반응하여 불필요한 자동 개입 차단.
- **사람 중심 보고서**: 코드 Diff를 배제하고, What / How / Why 중심의 자연어 설명과 Before/After 스크린샷(GFM & HTML 테이블)을 필수로 첨부.
- **안전한 종료 (Cleanup)**: PR 발행 완료 또는 타임아웃(15분) 시 해당 Worktree를 디스크에서 즉시 안전 삭제.

## Review Focus

1. **`@ai` 멘션 필터링 누락**: 일반 토론 댓글에 에이전트가 오반응하지 않는지 철저히 검증.
2. **Worktree 고아 객체 잔존**: 비정상 중단 시 `.worktrees/` 잔여 폴더로 인한 디스크 잠김 및 브랜치 충돌 방지.
3. **스크린샷 렌더링 실패**: GitHub 코멘트에서 브랜치 이미지 URL이 정상 로드되는지 확인.
4. **컨텍스트 오염 (Token Bloat)**: 메인 세션이 서브에이전트의 내부 작업 로그로 오염되지 않는지 점검.
5. **Git 인증 만료 예외 처리**: `gh` 토큰 실패 시 명확한 에러 메시지와 안내 출력.

---

## Task Decomposition

### Task 1: 스크린샷 자동 캡처 도구 구축 (`scripts/capture_screenshot.py`)
이슈 작업 전/후의 화면을 뷰포트별(PC 1280px, 모바일 375px)로 자동 캡처하여 브랜치 내 이미지 디렉토리에 저장하는 스크립트를 작성합니다.

**Files:**
- Create: `scripts/capture_screenshot.py`
- Modify: `.gitignore` (스크린샷 임시 파일 처리 규칙 확인)

- [ ] Step 1: Python 표준 라이브러리 및 시스템 브라우저/헤드리스 도구를 활용한 경량 스크린샷 캡처 스크립트 작성
- [ ] Step 2: PC 뷰포트(1280x800) 및 모바일 뷰포트(375x812) 캡처 기능 구현
- [ ] Step 3: 로컬 정적 웹 서버(http.server) 기동 후 `index.html` 캡처 테스트 및 결과 이미지 파일 검증
- [ ] Step 4: 단위 커밋: `feat(scripts): add automated screenshot capture tool for visual validation`

---

### Task 2: 이슈 오케스트레이터 완성 (`scripts/issue_worker.py`)
`@ai` 멘션 인식, Worktree 격리 수명 주기(15분 타임아웃, 24시간 피드백 만료), GFM/HTML What-How-Why 리포트 및 스크린샷 렌더링을 완전히 통합합니다.

**Files:**
- Modify: `scripts/issue_worker.py`

- [ ] Step 1: 정규식 `(?i)@ai\b` 기반 멘션 필터링 함수(`has_ai_mention`) 구현
- [ ] Step 2: 15분 타임아웃 및 고아 워크트리 자동 청소(`cleanup_stale_worktrees`) 로직 구현
- [ ] Step 3: Before/After 스크린샷 HTML 테이블이 포함된 GFM What/How/Why 코멘트 빌더 구현
- [ ] Step 4: `scripts/issue_worker.py check` 및 모의 이슈 테스트로 상태 전이 검증
- [ ] Step 5: 단위 커밋: `feat(scripts): complete worktree issue worker with @ai mention and rich report`

---

### Task 3: CI 검증 파이프라인 및 이슈 계약 템플릿 정비
PR이 발행되었을 때 GitHub Actions에서 정적 유효성을 검증하고, 표준 이슈 템플릿을 설정합니다.

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/ISSUE_TEMPLATE/ai_task.yml`
- Create: `.github/ISSUE_TEMPLATE/config.yml`

- [ ] Step 1: PR 생성 시 HTML/CSS/JS 정적 구문 유효성을 검사하는 경량 CI 워크플로우 정의
- [ ] Step 2: AI 작업 표준 이슈 템플릿(`.github/ISSUE_TEMPLATE/ai_task.yml`) 등록
- [ ] Step 3: GitHub Actions 문법 검증 및 템플릿 렌더링 확인
- [ ] Step 4: 단위 커밋: `feat(ci): add PR static validation workflow and issue templates`

---

### Task 4: Antigravity 서브에이전트 연동 스킬 및 실행 가이드 작성
현재 Antigravity 메인 세션에서 `invoke_subagent`를 통해 컨텍스트 오염 없이 격리 작업을 지시하고 결과를 보고받는 연동 규약과 가이드를 문서화합니다.

**Files:**
- Create: `docs/ISSUE_AUTOMATION_GUIDE.md`

- [ ] Step 1: Antigravity 서브에이전트 호출 프로토콜 및 프롬프트 명세 작성
- [ ] Step 2: 이슈 등록부터 피드백, 머지까지의 사용자 운영 가이드 정리
- [ ] Step 3: 단위 커밋: `docs: add comprehensive guide for Antigravity issue automation system`

---

### Task 5: 전체 시스템 E2E 검증 및 원격 저장소 공식 배포
실제 등록된 이슈를 대상으로 격리 Worktree 생성부터 Before/After 스크린샷 캡처, What/How/Why 리포트 댓글 등록 및 PR 발행까지의 전 과정을 1회 시뮬레이션 검증한 뒤 master 브랜치에 최종 푸시합니다.

- [ ] Step 1: 마스터 브랜치에서 시스템 파일 전체 스테이징 및 최종 정합성 확인
- [ ] Step 2: 원격 저장소(`origin/master`)로 시스템 커밋 푸시
- [ ] Step 3: 실제 GitHub Issues 페이지에서 템플릿 및 CI Actions 등록 상태 최종 확인
