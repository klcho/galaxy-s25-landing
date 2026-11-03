# Roadmap: Harness-v1 GitHub Issue Automation & Global Scaffolder

## Overview

본 프로젝트는 GitHub Issue 기반의 자율 개발 파이프라인(4대 에이전트 + Worktree 격리 + 헤드리스 스크린샷 QA + 사람 중심 리포팅)을 어떤 프로젝트에서든 원클릭으로 주입하는 전역 스캐폴딩 스킬(`harness-github-issue-sync-init`)을 개발하고 배포·검증하는 로드맵입니다.

## Phases

- [x] **Phase 1: 자립형 템플릿 번들링 및 코어 스캐폴딩 엔진 구현** - templates/ 디렉토리 구축 및 scaffold.py 개발
- [ ] **Phase 2: 원격 GitHub 프로비저닝 및 전역 SKILL.md 배포** - 라벨 자동 생성, git commit/push 연동 및 SKILL.md 완성
- [ ] **Phase 3: 무결성 검증 및 Dry-run 테스트** - 단위 테스트 및 가상 타 프로젝트 주입 시뮬레이션

## Phase Details

### Phase 1: 자립형 템플릿 번들링 및 코어 스캐폴딩 엔진 구현
**Goal**: 전역 스킬 디렉토리를 생성하고, 4대 에이전트 및 헬퍼 스크립트를 독립 템플릿 번들로 패키징하며, git remote 자동 감지 및 템플릿 치환을 수행하는 파이썬 코어 엔진 개발
**Depends on**: Nothing
**Requirements**: [REQ-01, REQ-02, REQ-03, REQ-05]
**Success Criteria**:
  1. `C:\Users\nicek\.gemini\config\skills\harness-github-issue-sync-init\templates\`에 모든 핵심 자산이 자립형으로 번들링됨
  2. `scaffold.py`가 대상 프로젝트의 Git URL을 감지하여 `owner/repo`를 정확히 추출함
  3. `{{REPO_NAME}}` 치환 및 `.gitignore` 안전 병합이 정상 수행됨
**Plans**: 2 plans

Plans:
- [x] 01-01: 자립형 표준 템플릿 번들 구축
- [x] 01-02: 환경 자동 감지 및 스마트 주입 엔진 개발

### Phase 2: 원격 GitHub 프로비저닝 및 전역 SKILL.md 배포
**Goal**: GitHub CLI를 통한 필수 라벨 4종 자동 등록, 초기 git commit & push 연동, 그리고 전역 호출용 SKILL.md 정의
**Depends on**: Phase 1
**Requirements**: [REQ-04, REQ-06]
**Success Criteria**:
  1. `gh label create`를 통해 4종 필수 라벨이 원격에 자동 생성되거나 이미 존재함을 확인
  2. 스캐폴딩 완료 후 초기 설정 커밋이 정상적으로 원격에 푸시됨
  3. Antigravity에서 `/harness-github-issue-sync-init` 커맨드가 전역으로 정상 인식됨
**Plans**: 1 plan

### Phase 3: 무결성 검증 및 Dry-run 테스트
**Goal**: 스캐폴딩 엔진의 문법, 파일 누락 여부, 템플릿 치환 무결성 유닛 테스트 및 실제 프로젝트 적용 시뮬레이션
**Depends on**: Phase 2
**Requirements**: [REQ-07, NFR-01, NFR-02, NFR-03]
**Success Criteria**:
  1. 모든 단위 테스트 통과 (100% pass)
  2. 가상 테스트 디렉토리에 스캐폴딩 주입 시 10초 이내에 에러 없이 완벽히 프로비저닝됨
**Plans**: 1 plan

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. 자립형 템플릿 번들링 및 코어 스캐폴딩 엔진 구현 | 2/2 | Completed | 2026-11-03 |
| 2. 원격 GitHub 프로비저닝 및 전역 SKILL.md 배포 | 0/1 | Not started | - |
| 3. 무결성 검증 및 Dry-run 테스트 | 0/1 | Not started | - |
