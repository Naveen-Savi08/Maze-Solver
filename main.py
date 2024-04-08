import tkinter as tk
from tkinter import ttk
import random
import heapq

class Stack:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return not self.items

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self.items[-1]

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def is_empty(self):
        return not self.elements

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        if self.is_empty():
            return None
        return heapq.heappop(self.elements)[1]

# Generate maze
def generate_maze(width, height, num_barriers=4):
    maze = [['.' for _ in range(width)] for _ in range(height)]
    # Set the starting point
    start_x = random.randint(0, 1)
    start_y = random.randint(0, height - 1)
    maze[start_y][start_x] = 'S'
    # Set the goal
    goal_x = random.randint(width - 2, width - 1)
    goal_y = random.randint(0, height - 1)
    maze[goal_y][goal_x] = 'G'
    # Randomly placed barriers
    barriers_placed = 0
    while barriers_placed < num_barriers:
        barrier_x = random.randint(0, width - 1)
        barrier_y = random.randint(0, height - 1)

        if (
            (barrier_x != start_x or barrier_y != start_y)
            and (barrier_x != goal_x or barrier_y != goal_y)
            and maze[barrier_y][barrier_x] == '.'
        ):
            maze[barrier_y][barrier_x] = '#'
            barriers_placed += 1

    return maze, (start_x, start_y), (goal_x, goal_y)

# Check the valid moves
def is_valid_move(x, y, width, height, maze):
    return 0 <= x < width and 0 <= y < height and maze[y][x] != '#'

# heuristic cost for each node
def heuristic(node, goal):
    x1, y1 = node
    x2, y2 = goal
    return abs(x1 - x2) + abs(y1 - y2)

# Manhattan distance from the node N to Goal node
def manhattan_distance(node, goal):
    x1, y1 = node
    x2, y2 = goal
    return abs(x1 - x2) + abs(y1 - y2)

# Depth First Search
def dfs(maze, start, goal):
    stack = Stack()
    visited = set()
    path = {start: None}
    stack.push((start, 0))
    visited.add(start)

    total_time = 1

    while not stack.is_empty():
        current_node, exploration_time = stack.pop()

        if current_node == goal:
            path_nodes = []
            while current_node:
                path_nodes.append(current_node)
                current_node = path[current_node]
            path_nodes.reverse()

            for node in path_nodes[1:]:
                total_time += exploration_time

            return path_nodes, total_time // 60

        x, y = current_node
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            next_node = (next_x, next_y)

            if is_valid_move(next_x, next_y, len(maze[0]), len(maze), maze) and next_node not in visited:
                stack.push((next_node, 60))
                visited.add(next_node)
                path[next_node] = current_node

    return None, 0

# A* Search
def astar(maze, start, goal):
    queue = PriorityQueue()
    queue.put(start, 0)
    came_from = {}
    cost_so_far = {start: 0}

    while not queue.is_empty():
        current_node = queue.get()

        if current_node == goal:
            path_nodes = []
            while current_node:
                path_nodes.append(current_node)
                current_node = came_from.get(current_node)
            path_nodes.reverse()
            return path_nodes, cost_so_far[goal]

        x, y = current_node
        neighbors = [(x + dx, y + dy) for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]]
        neighbors.sort()  # Sort neighbors in increasing order

        for next_x, next_y in neighbors:
            next_node = (next_x, next_y)
            new_cost = cost_so_far[current_node] + 1

            if is_valid_move(next_x, next_y, len(maze[0]), len(maze), maze) and (
                    next_node not in cost_so_far or new_cost < cost_so_far[next_node]
            ):
                cost_so_far[next_node] = new_cost
                priority = new_cost + manhattan_distance(next_node, goal)  # Use Manhattan distance
                queue.put(next_node, priority)
                came_from[next_node] = current_node

    return None, 0

# Visualize the given path in the maze
def visualize_path(maze, path, start, goal):
    for node in path:
        x, y = node
        if node != start and node != goal:
            maze[y][x] = '*'

# Clear the visual representation of the given path in the maze
def clear_path(maze, path, start, goal):
    for node in path:
        x, y = node
        if node != start and node != goal:
            maze[y][x] = '.'

# GUI For Maze
class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver")

        self.width = 6
        self.height = 6
        self.num_barriers = 4
        self.maze, self.start, self.goal = generate_maze(self.width, self.height, self.num_barriers)

        self.maze_canvas = tk.Canvas(self.root, width=self.width * 50, height=self.height * 50)
        self.maze_canvas.grid(row=0, column=0, columnspan=2)

        self.maze_canvas_path = []
        self.animation_speed = 500  # Set the animation speed

        self.dfs_button = ttk.Button(self.root, text="DFS", command=self.run_dfs)
        self.dfs_button.grid(row=1, column=0, padx=5, pady=5)

        self.astar_button = ttk.Button(self.root, text="A*", command=self.run_astar)
        self.astar_button.grid(row=1, column=1, padx=5, pady=5)

        # Draw the initial maze
        self.draw_maze()
        self.elapsed_time = 0  # Counter for elapsed time

    def run_dfs(self):
        self.elapsed_time = 1  # Initialize elapsed time to 1 for the start node
        clear_path(self.maze, self.maze_canvas_path, self.start, self.goal)
        dfs_result = dfs(self.maze, self.start, self.goal)
        dfs_path, elapsed_time = dfs_result[0], dfs_result[1]
        if dfs_path:
            visualize_path(self.maze, dfs_path, self.start, self.goal)
            self.maze_canvas_path = dfs_path
            self.draw_maze()
            print("DFS Path:")
            for row in self.maze:
                print(' '.join(row))
            print(f"Visited Nodes: {dfs_path}")
            print(f"Time to find the goal using DFS: {elapsed_time} minutes")


    def run_astar(self):
        self.elapsed_time = 1  # Initialize elapsed time to 1 for the start node
        clear_path(self.maze, self.maze_canvas_path, self.start, self.goal)
        astar_result = astar(self.maze, self.start, self.goal)
        astar_path, elapsed_time = astar_result[0], astar_result[1]
        if astar_path:
            visualize_path(self.maze, astar_path, self.start, self.goal)
            self.maze_canvas_path = astar_path
            self.draw_maze()
            print("A* Path:")
            for row in self.maze:
                print(' '.join(row))
            print(f"Visited Nodes: {astar_path}")
            print(f"Time to find the goal using A*: {elapsed_time} minutes")


    def animate_path(self, path):
        self.maze_canvas_path = path
        self.draw_maze()
        self.animate_step(0)

    def animate_step(self, step):
        if step < len(self.maze_canvas_path):
            clear_path(self.maze, self.maze_canvas_path[:step], self.start, self.goal)
            visualize_path(self.maze, self.maze_canvas_path[:step + 1], self.start, self.goal)
            self.draw_maze()
            self.root.after(1000, self.animate_step, step + 1)

    def draw_maze(self):
        self.maze_canvas.delete("all")
        for y in range(self.height):
            for x in range(self.width):
                cell_value = self.maze[y][x]
                color = "white" if cell_value == "." else "black" if cell_value == "#" else "green" if cell_value == "S" else "red" if cell_value == "G" else "yellow" if cell_value == "*" else None
                self.maze_canvas.create_rectangle(x * 50, y * 50, (x + 1) * 50, (y + 1) * 50, fill=color, outline="black")

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()