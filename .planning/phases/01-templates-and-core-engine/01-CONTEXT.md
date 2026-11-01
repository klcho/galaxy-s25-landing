# Phase 1: 자립형 템플릿 번들링 및 코어 스캐폴딩 엔진 구현 - Context

**Gathered:** 2026-11-01
**Status:** Ready for planning

<domain>
## Phase Boundary

본 Phase는 `harness-v1` 규격의 4대 에이전트, 전용 스킬 5종, Windows 헤드리스 브라우저 캡처 및 이슈 워커 엔진을 전역 스킬(`C:\Users\nicek\.gemini\config\skills\harness-github-issue-sync-init\`) 내부에 100% 자립형 템플릿으로 패키징하고, 대상 프로젝트에서 환경을 자동 감지하여 안전하게 주입하는 파이썬 코어 엔진(`scripts/scaffold.py`)을 구현합니다.

</domain>

<decisions>
## Implementation Decisions

### 충돌 처리 정책 (Conflict Handling)
- **D-01 (기존 파일 충돌 대화형 확인)**: 대상 프로젝트에 이미 `AGENTS.md`나 `scripts/` 디렉토리 내 파일이 존재할 경우, 무단 덮어쓰기를 엄격히 금지하고 사용자에게 대화형 확인(Overwrite / Backup & Overwrite / Skip)을 거치도록 구현합니다. — **Reversibility:** reversible
- **D-02 (.gitignore 스마트 병합)**: 대상 프로젝트의 `.gitignore` 파일은 기존 내용을 100% 보존하며 하단에 `.worktrees/`, `_workspace/` 항목만 중복 없이 안전하게 추가(append)합니다. — **Reversibility:** reversible

### 실행 런타임 탐색 순서 (Runtime Resolution)
- **D-03 (헤드리스 브라우저 탐색 우선순위)**: `capture_screenshot.py`에서 브라우저 탐색 순서를 사용자의 결정에 따라 **Chrome(우선) ➔ Edge(차선) ➔ Brave** 순으로 자동 감지하여 실행합니다. — **Reversibility:** reversible
- **D-04 (Python 인터프리터 탐색)**: `sys.executable`을 1차로 활용하고, 시스템 PATH의 `python` ➔ `python3` 순으로 크로스 플랫폼 폴백을 지원합니다. — **Reversibility:** reversible

### 템플릿 번들링 및 치환 (Template Bundling & Substitution)
- **D-05 (자립형 번들링)**: 외부 프로젝트나 네트워크 의존 없이 스킬 내부(`templates/`)에 표준 파일들을 완전 보관하며, `{{REPO_NAME}}` 플레이스홀더를 대상 프로젝트의 Git remote URL로부터 자동 추출하여 외과적으로 치환합니다. — **Reversibility:** reversible
- **D-06 (상태 기반 멘션 감지 기본 탑재)**: 번들링되는 `issue_worker.py`는 `status:waiting-feedback` 상태일 때 사용자의 일반 응답(예: `Option B`)을 `@ai` 없이도 즉시 인지하는 상태 기반 규칙을 기본 탑재합니다. — **Reversibility:** reversible

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `c:\AI-work\Issue-AI연동\AGENTS.md` — 4대 에이전트(PO, Coder, Verifier, Reporter) 팀의 통합 강령 및 QA Gate 명세
- `c:\AI-work\Issue-AI연동\docs\PORTABILITY_GUIDE.md` — 타 프로젝트 이식 파일 목록 및 핵심 안전 가드레일
- `c:\AI-work\Issue-AI연동\scripts\issue_worker.py` — 상태 기반 댓글 감지 및 Worktree 라이프사이클 엔진 원본
- `c:\AI-work\Issue-AI연동\scripts\capture_screenshot.py` — Windows 헤드리스 브라우저 스크린샷 엔진 원본
- `C:\Users\nicek\.gemini\antigravity\brain\3b4f6d55-bb9e-4015-94fb-60e6d44fc3dd\harness_scaffold_plan.md` — /grill-me를 통해 도출된 구축 계획서

</canonical_refs>
