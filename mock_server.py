# mock_server.py — A·B 완성 전까지 C가 쓸 가짜 API
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.get("/maze")
def get_maze(rows: int = 5, cols: int = 5):
    # 벽 없는 단순 grid 반환 (테스트용)
    grid = [
        [{"top": True, 
          "right": (c == cols - 1), 
          "bottom": (r == rows - 1), 
          "left": True}
         for c in range(cols)]
        for r in range(rows)
    ]
    return {"grid": grid}

@app.get("/solve")
def solve(rows: int = 5, cols: int = 5):
    # 대각선 경로 반환 (테스트용)
    path = [{"row": i, "col": i} for i in range(min(rows, cols))]
    return {"path": path}