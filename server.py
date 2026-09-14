import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import random

# 우리가 구현한 어댑터 및 탐색 알고리즘 임포트
from dfs_adapter import solve_maze_user_bfs, solve_maze_user_dfs

app = FastAPI()

# index.html이 로컬 브라우저(file://)로 열려도 CORS 허용되도록 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서버 메모리에 최근 생성된 미로 상태 캐시
maze_state = {
    "grid": None,  # numpy uint8 array (rows, cols)
    "rows": 0,
    "cols": 0
}

WALL_N, WALL_S, WALL_W, WALL_E = 1, 2, 4, 8
DX = {WALL_N: 0, WALL_S: 0, WALL_W: -1, WALL_E: 1}
DY = {WALL_N: -1, WALL_S: 1, WALL_W: 0, WALL_E: 0}
OPPOSITE = {WALL_N: WALL_S, WALL_S: WALL_N, WALL_W: WALL_E, WALL_E: WALL_W}

def generate_maze_dfs(rows: int, cols: int):
    """
    DFS Backtracking 방식으로 완벽하게 통하는 미로를 생성하고 비트마스크 격자를 반환합니다.
    """
    grid = np.full((rows, cols), 0b1111, dtype=np.uint8)
    visited = np.zeros((rows, cols), dtype=bool)
    stack = [(0, 0)]
    visited[0, 0] = True

    while stack:
        r, c = stack[-1]
        neighbors = []
        for wall in (WALL_N, WALL_S, WALL_W, WALL_E):
            nr, nc = r + DY[wall], c + DX[wall]
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc]:
                neighbors.append((wall, nr, nc))

        if neighbors:
            wall, nr, nc = random.choice(neighbors)
            grid[r, c] &= 0xFF ^ wall
            grid[nr, nc] &= 0xFF ^ OPPOSITE[wall]
            visited[nr, nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()
    
    return grid

@app.get("/maze")
def get_maze(rows: int = 10, cols: int = 10):
    # 미로 생성
    grid_bitmask = generate_maze_dfs(rows, cols)
    
    # 상태 저장
    maze_state["grid"] = grid_bitmask
    maze_state["rows"] = rows
    maze_state["cols"] = cols

    # 프론트엔드가 요구하는 포맷으로 변환
    # grid[r][c] = { "top": bool, "right": bool, "bottom": bool, "left": bool }
    web_grid = []
    for r in range(rows):
        row_cells = []
        for c in range(cols):
            val = grid_bitmask[r, c]
            row_cells.append({
                "top": bool(val & WALL_N),
                "right": bool(val & WALL_E),
                "bottom": bool(val & WALL_S),
                "left": bool(val & WALL_W)
            })
        web_grid.append(row_cells)

    return {"grid": web_grid}

@app.get("/solve")
def solve_maze(rows: int = 10, cols: int = 10, algo: str = "bfs"):
    # 만약 기존에 저장된 미로가 없거나 크기가 다르면 새로 생성
    if (maze_state["grid"] is None 
            or maze_state["rows"] != rows 
            or maze_state["cols"] != cols):
        maze_state["grid"] = generate_maze_dfs(rows, cols)
        maze_state["rows"] = rows
        maze_state["cols"] = cols

    grid_bitmask = maze_state["grid"]
    start = (0, 0)
    end = (rows - 1, cols - 1)

    # 알고리즘 선택에 따른 제너레이터 인스턴스 생성 및 실행
    if algo.lower() == "dfs":
        solver_gen = solve_maze_user_dfs(rows, cols, grid_bitmask, start, end)
    else:
        # 기본값은 BFS
        solver_gen = solve_maze_user_bfs(rows, cols, grid_bitmask, start, end)

    # 제너레이터를 끝까지 소비하여 최종 경로를 획득
    final_path = []
    for cell, path in solver_gen:
        if path is not None:
            final_path = path
            break

    # 프론트엔드가 요구하는 포맷인 [{"row": r, "col": c}, ...] 으로 변환
    web_path = [{"row": r, "col": c} for r, c in final_path]

    return {"path": web_path}

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
