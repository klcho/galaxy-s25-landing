# 🚀 Antigravity Harness-v1 타 프로젝트 이식 가이드 (Portability Guide)

본 가이드는 현재 저장소(`galaxy-s25-landing`)에서 검증 완료된 **'GitHub Issues ↔ Antigravity 멀티에이전트 자율 작업 시스템'을 다른 신규 또는 기존 프로젝트(React, Next.js, Python, Java, Go 등)에 3분 만에 복사하여 즉시 가동하는 방법**을 안내합니다.

---

## 1. 복사 대상 핵심 파일 목록 (Core Artifacts)

새로운 프로젝트의 루트 디렉토리에 아래 폴더와 파일들을 그대로 복사(Copy & Paste)합니다:

```text
Target-Project-Root/
├── AGENTS.md                          # 1. 멀티에이전트 협업 강령 및 QA Gate 규칙
├── .agents/                           # 2. 4대 에이전트 프로필(agent.json) 및 전용 스킬(SKILL.md)
│   ├── agents/
│   │   ├── issue-triage-po/agent.json
│   │   ├── worktree-coder/agent.json
│   │   ├── quality-verifier/agent.json
│   │   └── release-reporter/agent.json
│   └── skills/
│       ├── issue-triage/SKILL.md
│       ├── worktree-coding/SKILL.md
│       ├── quality-verification/SKILL.md
│       └── release-reporting/SKILL.md
├── .github/                           # 3. 이슈 템플릿 및 CI 검증 워크플로우
│   ├── ISSUE_TEMPLATE/ai_task.yml
│   ├── ISSUE_TEMPLATE/config.yml
│   └── workflows/ci.yml
├── scripts/                           # 4. 공용 헬퍼 엔진
│   ├── issue_worker.py
│   └── capture_screenshot.py
└── .gitignore                         # 5. .worktrees/ 격리 디렉토리 차단 설정 추가
```

---

## 2. 프로젝트별 맞춤 설정 (단 2곳만 수정)

### ① `scripts/issue_worker.py`의 저장소 이름 변경 (13행)
새로운 프로젝트의 GitHub 리포지토리 주소로 변경합니다:
```python
REPO_NAME = "your-github-username/your-new-repo"  # 예: "klcho/my-nextjs-app"
```

### ② 대상 프로젝트의 검증 명령어 지정
* **웹 프론트엔드 프로젝트 (React / Vue / HTML 등)**:
  * 기본 제공되는 `scripts/capture_screenshot.py`를 그대로 사용하여 헤드리스 브라우저 캡처 수행.
* **백엔드 / API 프로젝트 (FastAPI / Spring / Node.js 등)**:
  * 스크린샷 대신 테스트 러너 실행:
  * `.agents/skills/quality-verification/SKILL.md` 및 `scripts/issue_worker.py`에서 `npm test` 또는 `pytest` 실행 로그를 `_workspace/qa_report.md`에 남기도록 1줄만 변경.

### ③ `.gitignore`에 워크트리 제외 추가
새 프로젝트의 `.gitignore`에 아래 항목을 추가합니다:
```gitignore
.worktrees/
_workspace/screenshots/
_workspace/reports/
```

---

## 3. 원클릭 가동 및 사용 방법 (Quick Start)

### 1단계: GitHub에 이슈 등록
* 이슈 제목: `[Task]: 로그인 버튼 스타일 수정`
* 본문: `@ai 모바일 화면에서 로그인 버튼이 너무 큽니다. padding을 10px로 줄여주세요.`

### 2단계: 에이전트 실행 (2가지 모드 지원)
* **모드 A (Antigravity 대화창 연동)**:
  * Antigravity 채팅창에서: `"대기 중인 이슈 확인하고 작업해줘"` 입력.
  * 4대 에이전트가 격리된 Git Worktree에서 코딩 및 스크린샷 검증을 마치고 PR 발행 후 **2줄 초경량 리포트**를 메인 창에 브리핑합니다.
* **모드 B (CLI 즉시 실행)**:
  ```bash
  python scripts/issue_worker.py check
  python scripts/issue_worker.py start <이슈번호>
  # 코드 수정 및 스크린샷 확인 후
  python scripts/issue_worker.py complete <이슈번호> "작업 설명"
  ```

### 3단계: GitHub에서 검토 및 Merge
* 원본 이슈 댓글에 등록된 **Before & After 스크린샷 비교 테이블**과 **What/How/Why 리포트**를 확인.
* 이상이 없으면 PR 링크를 클릭하고 **Merge** 버튼을 누르면 작업이 완료되고 이슈가 자동으로 닫힙니다.

---

## 4. 핵심 안전 가드레일 (Safety Guardrails)

1. **메인 브랜치 불변성**: 모든 작업은 반드시 `.worktrees/task-issue-#N` 격리 환경에서 수행되며 메인 브랜치를 오염시키지 않습니다.
2. **컨텍스트 영구 보호**: 메인 채팅창에는 2줄 요약과 파일 링크만 전달되므로, 수십 개의 이슈를 처리해도 대화창 메모리가 고갈되지 않습니다.
3. **물리적 QA Gate**: 실제 브라우저 스크린샷이나 테스트 로그 증거 파일이 디스크에 생성되지 않으면 PR 발행 단계로 넘어가지 않습니다.
