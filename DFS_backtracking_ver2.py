from collections import deque

def solve_maze(rows, cols, grid, start, end):
    WALL_N, WALL_S, WALL_W, WALL_E = 1, 2, 4, 8
    DX = {WALL_N: 0, WALL_S: 0, WALL_W: -1, WALL_E: 1}
    DY = {WALL_N: -1, WALL_S: 1, WALL_W: 0, WALL_E: 0}
    
    queue = deque([start])
    visited = set([start])
    parent_map = {start: None}
    
    found = False
    
    while queue:
        r, c = queue.popleft()
        
        yield (r, c), None
        
        if (r, c) == end:
            found = True
            break

        for wall in (WALL_N, WALL_S, WALL_W, WALL_E):
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