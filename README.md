# 🧩 Maze Generator & Solver (미로 생성기 & 해결기)

팀원들이 개별 구현한 미로 생성/탐색 알고리즘과 웹 UI, OpenCV 로컬 시각화 도구를 하나로 통합한 미로 생성 및 해결 프로젝트입니다.

---

## 📁 프로젝트 구조

```text
maze_generator_solver/
├── index.html                  # 웹 프론트엔드 UI
├── style.css                   # 웹 스타일시트
├── server.py                   # FastAPI 백엔드 웹 서버
├── map.py                      # OpenCV 기반 로컬 GUI 시각화 & 테스트베드
├── dfs_adapter.py              # 탐색 알고리즘 어댑터
├── DFS_backtracking_ver2.py    # DFS 백트래킹 미로 풀이 알고리즘
├── dfs_tracking.py             # 탐색 경로 추적 유틸리티
└── README.md                   # 프로젝트 문서
```

---

## 🚀 실행 방법

### 1. 웹 어플리케이션 실행 (FastAPI + HTML)

1. **필수 라이브러리 설치**
   ```bash
   pip install fastapi uvicorn numpy opencv-python
   ```

2. **백엔드 서버 실행**
   ```bash
   python server.py
   # 또는 uvicorn server:app --reload --port 8000
   ```

3. **웹 화면 열기**
   - 브라우저에서 `index.html` 파일을 직접 열거나 Live Server를 이용해 접속합니다.

---

### 2. 로컬 GUI 시각화 실행 (OpenCV)

미로 생성 알고리즘과 탐색 과정을 로컬 창에서 실시간 애니메이션으로 확인합니다.

```bash
python map.py
```

* **조작키**:
  - `g`: 미로 생성 시작 (MOCK DFS)
  - `1`, `2`, `3`: 알고리즘 선택 (`1`: BFS, `2`: User BFS, `3`: User DFS)
  - `s` / `e` / `w`: 클릭 모드 변경 (시작점 / 도착점 / 벽 편집)
  - `f`: 현재 단계 완료 시점까지 즉시 스킵
  - `r`: 재시작 (Done 상태)
  - `q`: 종료

---

## 🛠 주요 기능 및 알고리즘

- **미로 생성**: DFS 백트래킹(Randomized DFS Backtracking) 알고리즘을 사용한 완벽한 미로(Perfect Maze) 생성
- **미로 탐색**: BFS 및 DFS 알고리즘 지원
- **데이터 표현**: 비트마스크(Bitmask) 기반 벽(Wall) 상태 관리 (N:1, S:2, W:4, E:8)