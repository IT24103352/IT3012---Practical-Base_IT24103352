# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)
        self.facing_direction = 'Up'

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        # Generate toxic traps
        self.toxic_traps = set()
        while len(self.toxic_traps) < 3:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            pos_tuple = (tx, ty)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls and pos_tuple not in self.food_positions:
                self.toxic_traps.add(pos_tuple)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        fx, fy = self.agent_pos
        if self.facing_direction == 'Up':
            fy += 1
        elif self.facing_direction == 'Down':
            fy -= 1
        elif self.facing_direction == 'Left':
            fx -= 1
        elif self.facing_direction == 'Right':
            fx += 1
        front_pos = (fx, fy)

        lx, ly = self.agent_pos
        if self.facing_direction == 'Up':
            lx -= 1
        elif self.facing_direction == 'Down':
            lx += 1
        elif self.facing_direction == 'Left':
            ly -= 1
        elif self.facing_direction == 'Right':
            ly += 1
        left_pos = (lx, ly)
        
        rx, ry = self.agent_pos
        if self.facing_direction == 'Up':
            rx += 1
        elif self.facing_direction == 'Down':
            rx -= 1
        elif self.facing_direction == 'Left':
            ry += 1
        elif self.facing_direction == 'Right':
            ry -= 1
        right_pos = (rx, ry)

        wall_ahead = front_pos in self.walls or not (0 <= front_pos[0] < self.width and 0 <= front_pos[1] < self.height)
        wall_left = left_pos in self.walls or not (0 <= left_pos[0] < self.width and 0 <= left_pos[1] < self.height)
        wall_right = right_pos in self.walls or not (0 <= right_pos[0] < self.width and 0 <= right_pos[1] < self.height)

        return {
            'wall_ahead': wall_ahead,
            'wall_left': wall_left,
            'wall_right': wall_right,
            'food_here': tuple(self.agent_pos) in self.food_positions,
            'smells_toxin': tuple(self.agent_pos) in self.toxic_traps,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions)
        }

    def execute_action(self, action: str):
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == 'turn_left':
            dirs = ['Up', 'Left', 'Down', 'Right']
            idx = dirs.index(self.facing_direction)
            self.facing_direction = dirs[(idx + 1) % 4]
        elif action == 'turn_right':
            dirs = ['Up', 'Right', 'Down', 'Left']
            idx = dirs.index(self.facing_direction)
            self.facing_direction = dirs[(idx + 1) % 4]
        elif action == 'move_forward':
            if self.facing_direction == 'Up':
                new_pos[1] = min(self.height - 1, new_pos[1] + 1)
            elif self.facing_direction == 'Down':
                new_pos[1] = max(0, new_pos[1] - 1)
            elif self.facing_direction == 'Left':
                new_pos[0] = max(0, new_pos[0] - 1)
            elif self.facing_direction == 'Right':
                new_pos[0] = min(self.width - 1, new_pos[0] + 1)
        elif action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20
            
        if tuple_pos in self.toxic_traps:
            self.score -= 15

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, agent, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.agent = agent
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        for tx, ty in self.env.toxic_traps:
            offset = self.cell_size * 0.25
            x1 = tx * self.cell_size + offset
            y1 = (self.env.height - 1 - ty) * self.cell_size + offset
            self.canvas.create_polygon(
                x1 + self.cell_size * 0.25, y1,
                x1, y1 + self.cell_size * 0.5,
                x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5,
                fill="purple", outline="darkmagenta"
            )

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

        # Draw a line indicating facing direction
        cx = x1 + self.cell_size * 0.35
        cy = y1 + self.cell_size * 0.35
        dl = self.cell_size * 0.35
        if self.env.facing_direction == 'Up':
            self.canvas.create_line(cx, cy, cx, cy - dl, fill="white", width=2)
        elif self.env.facing_direction == 'Down':
            self.canvas.create_line(cx, cy, cx, cy + dl, fill="white", width=2)
        elif self.env.facing_direction == 'Left':
            self.canvas.create_line(cx, cy, cx - dl, cy, fill="white", width=2)
        elif self.env.facing_direction == 'Right':
            self.canvas.create_line(cx, cy, cx + dl, cy, fill="white", width=2)

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    from agent import SimpleReflexAgent, ModelBasedAgent
    root = tk.Tk()
    
    # Try changing to ModelBasedAgent to see it escape loops!
    agent = SimpleReflexAgent() 
    
    app = GridGameGUI(root, agent=agent, width=12, height=12, num_food=15, num_opponents=0)
    root.mainloop()