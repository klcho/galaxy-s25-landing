# Harness-v1 GitHub Issue Automation & Global Scaffolder

## What This Is

GitHub Issues를 기반으로 작업을 자율 수주하고, 메인 브랜치를 완벽히 보호하는 독립 Git Worktree에서 코드를 수정한 뒤 헤드리스 브라우저 스크린샷 검증을 거쳐 사람 중심(What/How/Why) 리포트와 함께 PR을 자동 발행하는 `harness-v1` 시스템을 모든 프로젝트에 1초 만에 주입해주는 전역 스캐폴딩 스킬(`harness-github-issue-sync-init`)입니다.

## Core Value

어떤 신규 또는 기존 프로젝트에서든 단 한 줄의 명령어(`/harness-github-issue-sync-init`)로 리포지토리 정보와 프로젝트 유형을 전자동 감지하여, 4대 에이전트와 전용 스킬, 공용 헬퍼 엔진, GitHub 원격 라벨 프로비저닝 및 초기 커밋까지 100% 완전 자동화하여 주입합니다.

## Requirements

### Active

- [ ] **REQ-01**: 전역 스킬 디렉토리(`C:\Users\nicek\.gemini\config\skills\harness-github-issue-sync-init\`) 및 100% 자립형 템플릿 번들(`templates/`) 구축
- [ ] **REQ-02**: Git remote URL 자동 추출 및 프로젝트 유형(웹/백엔드) 자동 판별 로직 구현
- [ ] **REQ-03**: 대상 프로젝트의 `.gitignore` 안전 병합 및 `{{REPO_NAME}}` 변수 외과적 치환 엔진 작성
- [ ] **REQ-04**: GitHub CLI를 통한 필수 원격 라벨 4종(`status:in-progress`, `status:review-needed`, `status:waiting-feedback`, `ai-task`) 자동 생성
- [ ] **REQ-05**: 상태 기반 댓글 멘션 감지(질의응답 대기 시 `@ai` 생략 가능) 기본 탑재
- [ ] **REQ-06**: 슬래시 커맨드 `/harness-github-issue-sync-init` 및 SKILL.md 명세 등록
- [ ] **REQ-07**: 스캐폴딩 엔진의 단위 검증 및 Dry-run 테스트 통과

### Out of Scope

- 외부 유료/클라우드 LLM API 키 사용 금지 (Zero-Cost 원칙 엄수)
- 메인 세션 컨텍스트 오염 (50토큰 미만 초경량 요약 원칙 고수)
- 템플릿 외부 원격 의존성 (완전 오프라인 자립형 번들 유지)

## Context

- `c:\AI-work\Issue-AI연동` 프로젝트에서 파일럿 이슈 #1, #2, #4를 거치며 4대 에이전트 파이프라인의 실증이 100% 완료됨.
- `/grill-me` 인터뷰를 통해 사용자가 글로벌 스킬 형태, 전자동 감지, 완전 자동화(라벨 생성+커밋/푸시), 자립형 번들링을 채택함.

## Constraints

- **운영체제**: Windows 환경 완벽 지원 (PowerShell, cp949/utf-8 인코딩 방어, Edge 헤드리스 브라우저)
- **보안/격리**: 모든 코드 변경은 반드시 Git Worktree(`.worktrees/task-issue-#N`)에서만 수행
- **스킬 위치**: `C:\Users\nicek\.gemini\config\skills\harness-github-issue-sync-init\`

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 전역 스킬(Global Skill) 패키징 | 모든 프로젝트에서 즉시 호출 가능하도록 보장 | ✓ Good |
| 전자동 환경 감지 (git remote URL) | 사용자 입력 피로도를 제로로 만들고 10초 내 설치 완료 | ✓ Good |
| 완전 자동화 (라벨 생성 + git commit/push) | 스캐폴딩 후 별도 수동 작업 없이 바로 이슈 발행 가능 | ✓ Good |
| 자립형 템플릿 번들링 (Self-contained) | 타 프로젝트 파일 삭제나 경로 변경에 영향받지 않는 견고성 확보 | ✓ Good |

---
*Last updated: 2026-11-01 after /gsd-discuss-phase initialization*
