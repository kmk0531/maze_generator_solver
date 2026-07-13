import numpy as np
import cv2
import random

WALL_N, WALL_S, WALL_W, WALL_E = 1, 2, 4, 8
DX = {WALL_N: 0, WALL_S: 0, WALL_W: -1, WALL_E: 1}
DY = {WALL_N: -1, WALL_S: 1, WALL_W: 0, WALL_E: 0}
OPPOSITE = {WALL_N: WALL_S, WALL_S: WALL_N, WALL_W: WALL_E, WALL_E: WALL_W}

CELL_SIZE = 20
ROWS, COLS = 25, 40

COLOR_BG = (250, 248, 245)
COLOR_WALL = (70, 60, 55)
COLOR_PATH = (80, 190, 90)
COLOR_START = (90, 70, 235)
COLOR_START_RING = (255, 255, 255)
COLOR_END = (210, 130, 40)
COLOR_END_RING = (255, 255, 255)
COLOR_CURRENT = (0, 160, 255)
COLOR_CURRENT_RING = (30, 30, 30)

def MOCK_generate_step(rows, cols, grid):
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
            yield (r, c), (nr, nc), wall
        else:
            stack.pop()
            yield (r, c), None, None

def MOCK_solve_step(rows, cols, grid, start, end):
    from collections import deque

    def idx(r, c):
        return r * cols + c

    parent = np.full(rows * cols, -1, dtype=np.int32)
    visited = np.zeros((rows, cols), dtype=bool)
    q = deque([start])
    visited[start] = True

    while q:
        r, c = q.popleft()
        yield (r, c), None

        if (r, c) == end:
            break
        for wall in (WALL_N, WALL_S, WALL_W, WALL_E):
            if grid[r, c] & wall:
                continue
            nr, nc = r + DY[wall], c + DX[wall]
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc]:
                visited[nr, nc] = True
                parent[idx(nr, nc)] = idx(r, c)
                q.append((nr, nc))

    path = []
    cur = idx(*end)
    while cur != -1:
        path.append((cur // cols, cur % cols))
        cur = parent[cur]
    path.reverse()
    yield None, path

class MapRenderer:

    def __init__(self, rows, cols, cell_size=CELL_SIZE):
        self.rows, self.cols, self.cs = rows, cols, cell_size
        h, w = rows * cell_size, cols * cell_size

        self.grid = np.full((rows, cols), 0b1111, dtype=np.uint8)
        self.start = (0, 0)
        self.end = (rows - 1, cols - 1)

        self.static = np.full((h, w, 3), COLOR_BG, dtype=np.uint8)
        self.visit_count = 0
        self._draw_full_wall_grid()

    def cell_center(self, r, c):
        cs = self.cs
        return (c * cs + cs // 2, r * cs + cs // 2)

    def _visited_color(self, t):
        t = max(0.0, min(1.0, t))
        hue = int(200 - 165 * t)  # 파랑(200) -> 주황(35)으로 서서히 변함
        hsv = np.uint8([[[hue, 140, 255]]])
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0]
        return (int(bgr[0]), int(bgr[1]), int(bgr[2]))


    def cell_rect(self, r, c, margin=0):
        cs = self.cs
        x, y = c * cs, r * cs
        return (x + margin, y + margin, x + cs - margin, y + cs - margin)

    def _wall_segment_coords(self, r, c, wall):
        cs = self.cs
        x, y = c * cs, r * cs
        if wall == WALL_N:
            return (x, y), (x + cs, y)
        if wall == WALL_S:
            return (x, y + cs), (x + cs, y + cs)
        if wall == WALL_W:
            return (x, y), (x, y + cs)
        if wall == WALL_E:
            return (x + cs, y), (x + cs, y + cs)

    def draw_wall_segment(self, r, c, wall):
        p1, p2 = self._wall_segment_coords(r, c, wall)
        cv2.line(self.static, p1, p2, COLOR_WALL, 2, cv2.LINE_AA)

    def erase_wall_segment(self, r, c, wall):
        p1, p2 = self._wall_segment_coords(r, c, wall)
        cv2.line(self.static, p1, p2, COLOR_BG, 3, cv2.LINE_AA)

    def _draw_full_wall_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                for wall in (WALL_N, WALL_S, WALL_W, WALL_E):
                    if self.grid[r, c] & wall:
                        self.draw_wall_segment(r, c, wall)

    def paint_cell_permanent(self, r, c, color, margin=3):
        x1, y1, x2, y2 = self.cell_rect(r, c, margin)
        cv2.rectangle(self.static, (x1, y1), (x2, y2), color, -1, cv2.LINE_AA)

    def apply_generate_step(self, current, opened, wall):
        if opened is not None:
            r, c = current
            self.erase_wall_segment(r, c, wall)
            self.erase_wall_segment(*opened, OPPOSITE[wall])

    def apply_solve_step(self, cell):
        if cell is not None and cell not in (self.start, self.end):
            self.visit_count += 1
            t = self.visit_count / max(1, self.rows * self.cols * 0.6)
            self.paint_cell_permanent(*cell, self._visited_color(t), margin=3)

    def render_frame(self, current=None, path=None):
        frame = self.static.copy()

        if path and len(path) >= 2:
            pts = np.array([self.cell_center(r, c) for r, c in path], dtype=np.int32)
            thickness = max(2, int(self.cs * 0.35))
            cv2.polylines(frame, [pts], False, COLOR_PATH, thickness,
                          lineType=cv2.LINE_AA)
            for (r, c) in (path[0], path[-1]):
                cv2.circle(frame, self.cell_center(r, c), thickness // 2,
                           COLOR_PATH, -1, cv2.LINE_AA)

        radius = max(4, int(self.cs * 0.38))
        cx, cy = self.cell_center(*self.start)
        cv2.circle(frame, (cx, cy), radius, COLOR_START, -1, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy), radius, COLOR_START_RING, 2, cv2.LINE_AA)

        ex, ey = self.cell_center(*self.end)
        cv2.circle(frame, (ex, ey), radius, COLOR_END, -1, cv2.LINE_AA)
        cv2.circle(frame, (ex, ey), radius, COLOR_END_RING, 2, cv2.LINE_AA)

        if current is not None:
            r, c = current
            fx, fy = self.cell_center(r, c)
            cr = max(3, int(self.cs * 0.3))
            cv2.circle(frame, (fx, fy), cr, COLOR_CURRENT, -1, cv2.LINE_AA)
            cv2.circle(frame, (fx, fy), cr, COLOR_CURRENT_RING, 1, cv2.LINE_AA)

        return frame

    def toggle_wall_at_click(self, px, py):
        cs = self.cs
        c, r = px // cs, py // cs
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        rel_x = (px % cs) / cs
        rel_y = (py % cs) / cs

        dists = {
            WALL_N: rel_y,
            WALL_S: 1 - rel_y,
            WALL_W: rel_x,
            WALL_E: 1 - rel_x,
        }
        wall = min(dists, key=dists.get)

        nr, nc = r + DY[wall], c + DX[wall]
        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            return

        has_wall = bool(self.grid[r, c] & wall)
        if has_wall:
            self.grid[r, c] &= 0xFF ^ wall
            self.grid[nr, nc] &= 0xFF ^ OPPOSITE[wall]
            self.erase_wall_segment(r, c, wall)
        else:
            self.grid[r, c] |= wall
            self.grid[nr, nc] |= OPPOSITE[wall]
            self.draw_wall_segment(r, c, wall)

    def set_start(self, px, py):
        c, r = px // self.cs, py // self.cs
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.start = (r, c)

    def set_end(self, px, py):
        c, r = px // self.cs, py // self.cs
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.end = (r, c)

class App:
    WINDOW = "Map Renderer (Mock Data Test)"

    def __init__(self):
        self.rn = MapRenderer(ROWS, COLS, CELL_SIZE)
        self.state = "EDIT"
        self.mouse_mode = "WALL"
        self.gen_iter = None
        self.solve_iter = None
        self.current_cell = None
        self.final_path = None

        cv2.namedWindow(self.WINDOW)
        cv2.setMouseCallback(self.WINDOW, self.on_mouse)
        cv2.createTrackbar("Speed(ms)", self.WINDOW, 15, 100, lambda v: None)

    def on_mouse(self, event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN and not (event == cv2.EVENT_MOUSEMOVE and flags & cv2.EVENT_FLAG_LBUTTON):
            return
        if self.state != "EDIT":
            return

        if self.mouse_mode == "START":
            self.rn.set_start(x, y)
        elif self.mouse_mode == "END":
            self.rn.set_end(x, y)
        else:
            self.rn.toggle_wall_at_click(x, y)

    def run(self):
        print("조작법: 클릭=벽 토글 / s=시작점 모드 / e=도착점 모드 / w=벽편집 모드")
        print("        g=생성 시작(mock) / f=지금 단계 즉시 끝까지 스킵 / q=종료")
        paused = False

        while True:
            delay = max(1, cv2.getTrackbarPos("Speed(ms)", self.WINDOW))

            if self.state == "GENERATE":
                if self.gen_iter is None:
                    self.gen_iter = MOCK_generate_step(ROWS, COLS, self.rn.grid)
                try:
                    current, opened, wall = next(self.gen_iter)
                    self.current_cell = current
                    self.rn.apply_generate_step(current, opened, wall)
                except StopIteration:
                    self.state = "SOLVE"

            elif self.state == "SOLVE":
                if self.solve_iter is None:
                    self.solve_iter = MOCK_solve_step(ROWS, COLS, self.rn.grid, self.rn.start, self.rn.end)
                try:
                    cell, path = next(self.solve_iter)
                    if cell is not None:
                        self.current_cell = cell
                        self.rn.apply_solve_step(cell)
                    if path is not None:
                        self.final_path = path
                except StopIteration:
                    self.state = "DONE"

            cur = self.current_cell if self.state in ("GENERATE", "SOLVE") else None
            path = self.final_path if self.state == "DONE" else None
            frame = self.rn.render_frame(current=cur, path=path)
            cv2.putText(frame, f"STATE: {self.state}", (8, 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

            if self.state == "DONE":
                h, w = frame.shape[:2]
                cv2.rectangle(frame, (0, h // 2 - 22), (w, h // 2 + 22), (255, 255, 255), -1)
                cv2.putText(frame, "COMPLETE! (r = restart, q = quit)", (10, h // 2 + 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 120, 0), 2, cv2.LINE_AA)

            cv2.imshow(self.WINDOW, frame)

            key = cv2.waitKey(delay) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('g') and self.state == "EDIT":
                self.state = "GENERATE"
            elif key == ord('s'):
                self.mouse_mode = "START"
            elif key == ord('e'):
                self.mouse_mode = "END"
            elif key == ord('w'):
                self.mouse_mode = "WALL"
            elif key == ord('r') and self.state == "DONE":
                self.__init__()
            elif key == ord('f') and self.state in ("GENERATE", "SOLVE"):
                if self.state == "GENERATE":
                    for current, opened, wall in self.gen_iter:
                        self.rn.apply_generate_step(current, opened, wall)
                    self.state = "SOLVE"
                else:
                    for cell, path in self.solve_iter:
                        if cell is not None:
                            self.rn.apply_solve_step(cell)
                        if path is not None:
                            self.final_path = path
                    self.state = "DONE"
                self.current_cell = None

        cv2.destroyAllWindows()

if __name__ == "__main__":
    App().run()