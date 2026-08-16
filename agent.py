import random
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept.get('agent_pos')
        return random.choice(self.actions_pool)

class SimpleReflexAgent:
    """An agent that acts purely on the current percept."""
    
    def sense_and_act(self, percept: dict) -> str:
        # Example Logic: IF food_here THEN suck; IF wall_ahead THEN turn_left; ELSE move_forward
        if percept.get('food_here'):
            # The environment automatically 'sucks' food when moved onto, 
            # so we just need a dummy action or stay. Let's move forward if food is here?
            # Wait, if we are on food, the environment automatically eats it upon executing any action or standing still.
            # But the environment doesn't have a 'suck' action. 
            # We can return a safe action. Wait, 'food_here' implies we are on it.
            # Let's just follow typical grid navigation if there's no explicit suck action.
            # But wait, in Pacman, you eat by stepping. 'food_here' means we are CURRENTLY on food.
            pass
            
        if percept.get('wall_ahead'):
            return 'turn_left'
        else:
            return 'move_forward'

class ModelBasedAgent:
    """An agent that keeps track of previous percepts and actions to escape loops."""
    
    def __init__(self):
        self.history = []
        self.consecutive_turns = 0
        
    def sense_and_act(self, percept: dict) -> str:
        # Update State
        wall_ahead = percept.get('wall_ahead')
        
        # If we just keep turning left because of walls, we might be stuck in a U-shape.
        # Let's use internal state to decide.
        if wall_ahead:
            self.consecutive_turns += 1
            if self.consecutive_turns >= 2:
                # We've turned left multiple times due to walls, let's try turning right instead to break the loop
                self.consecutive_turns = 0
                return 'turn_right'
            return 'turn_left'
        else:
            self.consecutive_turns = 0
            return 'move_forward'

class SearchAgent:
    """An agent that uses search algorithms to find a path to food."""

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'  # 'BFS', 'DFS', or 'UCS'

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            all_food = percept.get('all_food', [])
            if not all_food:
                return 'Stay'

            agent_pos = percept.get('agent_pos', (0, 0))

            # Find closest food using Manhattan distance
            closest_food = min(all_food, key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1]))

            grid_size = percept.get('grid_size')
            walls = set(percept.get('walls', []))

            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, closest_food, grid_size, walls)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, closest_food, grid_size, walls)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, closest_food, grid_size, walls)

        if self.plan:
            return self.plan.pop(0)
        return 'Stay'

    def get_neighbors(self, pos, grid_size, walls):
        x, y = pos
        w, h = grid_size
        neighbors = []
        if y < h - 1 and (x, y + 1) not in walls:
            neighbors.append(((x, y + 1), 'Up'))
        if y > 0 and (x, y - 1) not in walls:
            neighbors.append(((x, y - 1), 'Down'))
        if x > 0 and (x - 1, y) not in walls:
            neighbors.append(((x - 1, y), 'Left'))
        if x < w - 1 and (x + 1, y) not in walls:
            neighbors.append(((x + 1, y), 'Right'))
        return neighbors

    def bfs_search(self, start, goal, grid_size, walls):
        queue = deque([(start, [])])
        reached = {start}

        while queue:
            current, path = queue.popleft()
            if current == goal:
                return path

            for next_pos, action in self.get_neighbors(current, grid_size, walls):
                if next_pos not in reached:
                    reached.add(next_pos)
                    queue.append((next_pos, path + [action]))
        return []

    def dfs_search(self, start, goal, grid_size, walls):
        stack = [(start, [])]
        reached = {start}

        while stack:
            current, path = stack.pop()
            if current == goal:
                return path

            for next_pos, action in self.get_neighbors(current, grid_size, walls):
                if next_pos not in reached:
                    reached.add(next_pos)
                    stack.append((next_pos, path + [action]))
        return []

    def ucs_search(self, start, goal, grid_size, walls):
        pq = [(0, start, [])]
        reached = {}

        while pq:
            cost, current, path = heapq.heappop(pq)
            if current == goal:
                return path
            
            if current in reached and reached[current] <= cost:
                continue
            reached[current] = cost

            for next_pos, action in self.get_neighbors(current, grid_size, walls):
                new_cost = cost + 1
                if next_pos not in reached or new_cost < reached[next_pos]:
                    heapq.heappush(pq, (new_cost, next_pos, path + [action]))
        return []