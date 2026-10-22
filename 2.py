from collections import deque

def bfs(graph, start, goal=None):
    """Breadth-First Search (BFS) using Queue (FIFO)"""
    frontier = deque([start])
    visited = []
    parent = {start: None}
    trace = []

    while frontier:
        current = frontier.popleft()
        visited.append(current)
        record(trace, current, frontier, visited)

        if current == goal:
            break

        for neighbor in graph.get(current, []):
            if neighbor not in visited and neighbor not in frontier:
                parent[neighbor] = current
                frontier.append(neighbor)

    # Reconstruct the shortest path
    path = []
    if goal and goal in visited:
        curr = goal
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    return trace, path


def dfs(graph, start, goal=None):
    """Depth-First Search (DFS) using Stack (LIFO)"""
    frontier = [start]
    visited = []
    parent = {start: None}
    trace = []

    while frontier:
        current = frontier.pop()
        if current not in visited:
            visited.append(current)
            record(trace, current, frontier, visited)

            if current == goal:
                break

            for neighbor in reversed(graph.get(current, [])):
                if neighbor not in visited:
                    parent[neighbor] = current
                    frontier.append(neighbor)

    # Reconstruct path
    path = []
    if goal and goal in visited:
        curr = goal
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    return trace, path