from collections import deque

def solve_maze(maze, start, end):
    rows = len(maze)
    cols = len(maze[0])
    
    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]
    
    queue = deque([start])
    visited = set([start])
    
    parent_map = {start: None}
    
    found = False
    
    while queue:
        x, y = queue.popleft()
        
        if (x, y) == end:
            found = True
            break
            
        for i in range(4):
            nx = x + dx[i]
            ny = y + dy[i]
            
            if 0 <= nx < rows and 0 <= ny < cols:
                if maze[nx][ny] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
                    parent_map[(nx, ny)] = (x, y)
                    
    if not found:
        return []
        
    path = []
    curr = end
    
    while curr is not None:
        path.append(curr)
        curr = parent_map[curr]
        
    path.reverse() 
    
    return path

if __name__ == "__main__":
    sample_maze = [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    
    start_point = (0, 0)
    end_point = (4, 4)
    
    
    result_path = solve_maze(sample_maze, start_point, end_point)
    
    if not result_path:
        
    else:
        for r, c in result_path:
            sample_maze[r][c] = 'O'
            
        for row in sample_maze:
            print(row)