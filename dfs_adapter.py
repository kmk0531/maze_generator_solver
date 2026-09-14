from collections import deque

def solve_maze_user_bfs(rows, cols, grid, start, end):
    """
    사용자의 dfs_tracking.py에 있던 BFS 기반 길찾기 알고리즘을
    비트마스크 기반 미로 및 yield 기반 제너레이터 형태로 어댑팅한 함수.
    """
    WALL_N, WALL_S, WALL_W, WALL_E = 1, 2, 4, 8
    DX = {WALL_N: 0, WALL_S: 0, WALL_W: -1, WALL_E: 1}
    DY = {WALL_N: -1, WALL_S: 1, WALL_W: 0, WALL_E: 0}
    
    queue = deque([start])
    visited = set([start])
    parent_map = {start: None}
    
    found = False
    
    while queue:
        r, c = queue.popleft()
        
        # 시각화를 위해 현재 방문 중인 셀 전달
        yield (r, c), None
        
        if (r, c) == end:
            found = True
            break
            
        # N, S, W, E 방향 검사
        for wall in (WALL_N, WALL_S, WALL_W, WALL_E):
            # 벽이 뚫려있는 경우 (비트 플래그가 0)
            if not (grid[r, c] & wall):
                nr = r + DY[wall]
                nc = c + DX[wall]
                
                if 0 <= nr < rows and 0 <= nc < cols:
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
                        parent_map[(nr, nc)] = (r, c)
                        
    path = []
    if found:
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parent_map[curr]
        path.reverse()
        
    yield None, path


def solve_maze_user_dfs(rows, cols, grid, start, end):
    """
    파일 이름 'dfs_tracking.py'에 걸맞은 진짜 DFS (깊이 우선 탐색)
    기반 미로 해결 알고리즘 제너레이터.
    """
    WALL_N, WALL_S, WALL_W, WALL_E = 1, 2, 4, 8
    DX = {WALL_N: 0, WALL_S: 0, WALL_W: -1, WALL_E: 1}
    DY = {WALL_N: -1, WALL_S: 1, WALL_W: 0, WALL_E: 0}
    
    # DFS를 위한 스택
    stack = [start]
    visited = set([start])
    parent_map = {start: None}
    
    found = False
    
    while stack:
        r, c = stack.pop()
        
        # 시각화를 위해 현재 방문 중인 셀 전달
        yield (r, c), None
        
        if (r, c) == end:
            found = True
            break
            
        # 사방 탐색
        for wall in (WALL_N, WALL_S, WALL_W, WALL_E):
            if not (grid[r, c] & wall):
                nr = r + DY[wall]
                nc = c + DX[wall]
                
                if 0 <= nr < rows and 0 <= nc < cols:
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        stack.append((nr, nc))
                        parent_map[(nr, nc)] = (r, c)
                        
    path = []
    if found:
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parent_map[curr]
        path.reverse()
        
    yield None, path
