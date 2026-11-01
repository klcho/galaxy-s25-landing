# Requirements: Harness-v1 GitHub Issue Automation & Global Scaffolder

## Functional Requirements

- **REQ-01**: 전역 스킬 디렉토리(`C:\Users\nicek\.gemini\config\skills\harness-github-issue-sync-init\`) 및 100% 자립형 템플릿 번들(`templates/`) 구축
- **REQ-02**: Git remote URL 자동 추출 및 프로젝트 유형(웹/백엔드) 자동 판별 로직 구현
- **REQ-03**: 대상 프로젝트의 `.gitignore` 안전 병합 및 `{{REPO_NAME}}` 변수 외과적 치환 엔진 작성
- **REQ-04**: GitHub CLI를 통한 필수 원격 라벨 4종(`status:in-progress`, `status:review-needed`, `status:waiting-feedback`, `ai-task`) 자동 생성
- **REQ-05**: 상태 기반 댓글 멘션 감지(질의응답 대기 시 `@ai` 생략 가능) 기본 탑재
- **REQ-06**: 슬래시 커맨드 `/harness-github-issue-sync-init` 및 SKILL.md 명세 등록
- **REQ-07**: 스캐폴딩 엔진의 단위 검증 및 Dry-run 테스트 통과

## Non-Functional Requirements

- **NFR-01 (Portability)**: 외부 인터넷 의존 없이 로컬 파일 시스템 내에서 10초 이내에 스캐폴딩 완료
- **NFR-02 (Safety)**: 기존 사용자 프로젝트 파일 덮어쓰기 방지 및 충돌 방어
- **NFR-03 (Encoding)**: Windows 한글 환경(`cp949`/`utf-8`) 입출력 완벽 방어
