import random

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