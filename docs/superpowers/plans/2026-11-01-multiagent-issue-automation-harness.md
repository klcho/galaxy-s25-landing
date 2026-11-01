# Harness-v1 Multi-Agent Issue Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 별도 외부 API 키 없이, GitHub Issues 작업을 4대 전문 멀티에이전트가 격리된 Git Worktree에서 자율 수행하고, Before/After 스크린샷과 What/How/Why 리포트를 첨부하여 PR을 발행하며, 메인 세션 컨텍스트를 영구 보호하는 '범용 이식형 자율 이슈 자동화 시스템'을 완성하고 검증한다.

**Architecture:** 
1. `issue-triage-po`: 이슈 및 `@ai` 멘션 감지 → 요구사항 분석 및 `_workspace/spec.md` 작업 계약 수립.
2. `worktree-coder`: 메인 브랜치 불변 원칙 하에 `.worktrees/task-issue-#N` 생성 및 외과적 코드 수정.
3. `quality-verifier`: 헤드리스 브라우저(`scripts/capture_screenshot.py`)로 PC/모바일 Before & After 스크린샷 캡처 및 QA Gate 물리적 교차 검증.
4. `release-reporter`: PR 자동 생성(`Closes #N`) → GitHub 댓글에 GFM/HTML 리포트 게시 → 메인 세션에는 2줄 초경량 요약+파일 링크만 전달 → Worktree 안전 회수.

**Tech Stack:** Python 3 (표준 라이브러리), GitHub CLI (`gh`), Git Worktrees, Windows 헤드리스 브라우저 (Edge/Chrome), GitHub Actions (CI)

**Spec:** docs/superpowers/plans/2026-11-01-multiagent-issue-automation-harness.md

---

## Global Constraints

- **무비용 원칙**: 외부 유료/무료 LLM API Key(Gemini API 등)를 사용하지 않고 현재 Antigravity 및 GitHub 무료 인프라만 사용.
- **메인 브랜치 불변성**: 로컬 `master` 워킹 트리는 직접 수정하지 않으며, 모든 작업은 반드시 `.worktrees/` 하위 격리 환경에서 수행.
- **트리거 안전성**: 이슈 본문 또는 댓글에 `@ai` (대소문자 무관) 멘션이 포함된 경우에만 반응하여 불필요한 자동 개입 차단.
- **사람 중심 보고서**: 코드 Diff를 배제하고, What / How / Why 중심의 자연어 설명과 Before/After 스크린샷(GFM & HTML 테이블)을 필수로 첨부.
- **메인 컨텍스트 방어**: 메인 대화창에는 2줄 초경량 알림과 로컬 파일 링크만 전달하여 토큰 소모를 이슈당 50토큰 미만으로 극소화.
- **안전한 종료 (Cleanup)**: PR 발행 완료 또는 타임아웃(15분) 시 해당 Worktree를 디스크에서 즉시 안전 삭제.

## Review Focus

1. **메인 세션 컨텍스트 오염 (Token Bloat)**: 메인 채팅창에 장황한 리포트 전문이 출력되지 않고 `_workspace/reports/` 링크로 깔끔히 격리되는지 검증.
2. **물리적 QA Gate 증거 누락**: 디스크 상에 실제 스크린샷 파일이 없는데도 승인되는 환각 현상이 완벽히 차단되는지 확인.
3. **`@ai` 멘션 필터링 정확도**: 대소문자 무관하게 `@ai`가 있을 때만 반응하고 사람 간 대화는 무시하는지 확인.
4. **Git Worktree 고아 누적 방지**: 비정상 중단이나 타임아웃 시 찌꺼기 디렉토리가 안전하게 회수되는지 확인.
5. **타 프로젝트 이식성 (Portability)**: 특정 정적 웹에 종속된 하드코딩 없이 다른 프로젝트로 복사 시 즉시 재사용 가능한지 확인.

---

## Task Decomposition

### Task 1: 메인 세션 컨텍스트 보호 초경량 리포팅 모듈 구현
리포트 전문은 `_workspace/reports/issue_#N_report.md`에 저장하고, 메인 세션에는 2줄 요약과 로컬 파일 링크만 반환하는 기능을 오케스트레이터에 통합합니다.

**Files:**
- Modify: `scripts/issue_worker.py`
- Modify: `.agents/skills/release-reporting/SKILL.md`

- [ ] Step 1: `_workspace/reports/` 디렉토리에 개별 이슈 마크다운 리포트를 독립 저장하는 파일 쓰기 로직 구현
- [ ] Step 2: 메인 세션 반환 메시지를 "2줄 요약 + 파일 링크(`file:///...`)" 포맷으로 극소화하는 포맷터 작성
- [ ] Step 3: 단위 테스트 실행 및 생성된 리포트 파일과 메인 출력 토큰량 검증
- [ ] Step 4: 단위 커밋: `feat(reporter): implement lightweight context-saving report mechanism`

---

### Task 2: `@ai` 멘션 필터 및 타임아웃 라이프사이클 엔진 고도화
댓글 내 `@ai` 멘션 감지 정규식과 15분 타임아웃 감시 및 고아 워크트리 자동 청소(Garbage Collection) 로직을 완성합니다.

**Files:**
- Modify: `scripts/issue_worker.py`
- Modify: `.agents/skills/issue-triage/SKILL.md`

- [ ] Step 1: `is_ai_mentioned(text)` 함수에 정규식 `(?i)@ai\b` 구현 및 단위 테스트
- [ ] Step 2: 15분 이상 경과한 고아 Worktree 탐지 및 강제 회수(`cleanup_stale_worktrees`) 함수 구현
- [ ] Step 3: 모의 멘션 및 타임아웃 시뮬레이션 테스트
- [ ] Step 4: 단위 커밋: `feat(worker): add @ai mention filter and worktree timeout garbage collection`

---

### Task 3: CI 검증 및 이슈 계약 템플릿 완성
PR 발행 시 GitHub Actions에서 정적 유효성을 자동 검증하고, 표준 이슈 템플릿을 정비합니다.

**Files:**
- Create: `.github/workflows/ci.yml`
- Verify: `.github/ISSUE_TEMPLATE/ai_task.yml`

- [ ] Step 1: PR 대상 HTML/CSS/JS 구문 유효성을 검사하는 경량 CI 워크플로우 정의
- [ ] Step 2: GitHub Actions 러너 구문 검사 및 템플릿 렌더링 확인
- [ ] Step 3: 단위 커밋: `feat(ci): finalize GitHub Actions PR validator and issue templates`

---

### Task 4: 파일럿 이슈 #1 실증 검증 (E2E Integration Test)
실제 등록된 이슈 #1(배경 바꾸기)을 대상으로 4대 에이전트 파이프라인의 실동작을 검증합니다.

**Files:**
- Output: `.worktrees/task-issue-1/`
- Output: `_workspace/screenshots/` (Before/After 캡처)
- Output: `_workspace/reports/issue_1_report.md`
- Output: GitHub PR & Issue #1 Comment

- [ ] Step 1: `issue-triage-po`: 이슈 #1 요구사항 분석 및 `_workspace/spec.md` 생성
- [ ] Step 2: `worktree-coder`: `.worktrees/task-issue-1` 생성 후 배경 화이트 및 텍스트 대비 외과적 수정
- [ ] Step 3: `quality-verifier`: `scripts/capture_screenshot.py`로 Before/After 스크린샷 캡처 및 QA Gate 물리적 통과 확인
- [ ] Step 4: `release-reporter`: 원격 푸시, PR 발행, GitHub 이슈 댓글(GFM/HTML 테이블) 게시, 메인 세션에 초경량 2줄 요약 보고, Worktree 회수
- [ ] Step 5: 진행 추적기 `_workspace/progress_tracker.md` 완료 갱신

---

### Task 5: 원격 저장소 공식 배포 및 타 프로젝트 이식 패키징
구축된 전체 하네스 시스템을 master 브랜치에 최종 커밋/푸시하고, 다른 저장소에서 즉시 복사하여 사용할 수 있도록 가이드를 정비합니다.

**Files:**
- Create: `docs/PORTABILITY_GUIDE.md`
- Modify: `AGENTS.md` (Change History 갱신)

- [ ] Step 1: `docs/PORTABILITY_GUIDE.md`에 타 프로젝트 복사 및 3분 세팅 가이드 작성
- [ ] Step 2: `master` 브랜치 최종 스테이징 및 `origin/master` 원격 푸시
- [ ] Step 3: GitHub 웹에서 Actions 및 이슈 템플릿 정상 등록 확인
