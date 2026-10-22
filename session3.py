from queue import LifoQueue

def depth_limited_tree(tree, root, goal, limit, trace=None):
    stack = LifoQueue()
    stack.put([root])
    visited = []                                   # nodes visited in this round only

    while not stack.empty():
        path = stack.get()                         # newest path first, as in DFS
        node = path[-1]
        visited.append(node)

        if node == goal:
            return path

        if len(path) - 1 < limit:                  # only go deeper if we are above the limit
            for child in reversed(tree[node]):
                stack.put(path + [child])

        record(trace, current=node, frontier=[p[-1] for p in stack.queue], visited=visited, limit=limit)      # animation only

    return None                                    # this round did not find the goal


def ids_tree(tree, root, goal, max_depth=10, trace=None):
    for limit in range(max_depth + 1):             # limit = 0, 1, 2, ...
        path = depth_limited_tree(tree, root, goal, limit, trace)
        if path is not None:
            return path, limit
    return None, None



def depth_limited_graph(graph, start, goal, limit, trace=None):
    stack = [[start]]                              # a list used as a stack
    visited = []                                   # nodes visited in this round only (may repeat)

    while len(stack) > 0:
        path = stack.pop()                         # newest path (last item)
        node = path[-1]
        visited.append(node)

        if node == goal:
            record(trace, current=node, frontier=[p[-1] for p in stack], visited=visited, limit=limit)  # animation only
            return path

        if len(path) - 1 < limit:                  # only go deeper if we are above the limit
            for neighbor in reversed(graph[node]):
                if neighbor not in path:           # do not walk in a circle along this path
                    stack.append(path + [neighbor])

        record(trace, current=node, frontier=[p[-1] for p in stack], visited=visited, limit=limit)      # animation only

    return None


def ids_graph(graph, start, goal, max_depth=10, trace=None):
    for limit in range(max_depth + 1):
        path = depth_limited_graph(graph, start, goal, limit, trace)
        if path is not None:
            return path, limit
    return None, None
from collections import deque

def expand_level(graph, queue, my_paths, other_paths, i_am_forward):
    meetings = []                                  # full paths found when the two searches touch
    expanded = []

    for _ in range(len(queue)):                    # exactly one level of this queue
        node = queue.popleft()
        expanded.append(node)

        for neighbor in graph[node]:
            if neighbor in other_paths:            # the other search already reached this node
                if i_am_forward:
                    meetings.append(my_paths[node] + other_paths[neighbor][::-1])
                else:
                    meetings.append(other_paths[neighbor] + my_paths[node][::-1])
            elif neighbor not in my_paths:         # a new node for this search
                my_paths[neighbor] = my_paths[node] + [neighbor]
                queue.append(neighbor)

    return meetings, expanded


def bidirectional_tree(graph, start, goal, trace=None):
    if start == goal:
        return [start]

    forward_paths = {start: [start]}               # paths that begin at the start
    backward_paths = {goal: [goal]}                # paths that begin at the goal
    forward_queue = deque([start])
    backward_queue = deque([goal])
    forward_done, backward_done = [], []           # nodes each side has expanded

    while len(forward_queue) > 0 and len(backward_queue) > 0:
        if len(forward_queue) <= len(backward_queue):          # expand the smaller side
            side = "forward"
            meetings, expanded = expand_level(graph, forward_queue, forward_paths, backward_paths, True)
            forward_done += expanded
        else:
            side = "backward"
            meetings, expanded = expand_level(graph, backward_queue, backward_paths, forward_paths, False)
            backward_done += expanded

        found = min(meetings, key=len) if meetings else None   # the shortest meeting
        record(trace, side=side, current=expanded, forward_done=forward_done, backward_done=backward_done,
               forward_queue=forward_queue, backward_queue=backward_queue, found=found)   # animation only

        if found is not None:
            return found

    return None



import heapq

def ucs_tree(tree, root, goal, trace=None):
    frontier = []                                      # the priority queue
    heapq.heappush(frontier, (0, [root]))              # (total cost, path)
    visited = {}                                       # node -> cost when it was visited

    while len(frontier) > 0:
        cost, path = heapq.heappop(frontier)           # the cheapest item
        node = path[-1]
        visited[node] = cost

        if node == goal:
            record(trace, current=node, cost=cost, frontier=[(c, p[-1]) for c, p in frontier], visited=visited)  # animation only
            return path, cost

        for child, weight in tree[node]:
            heapq.heappush(frontier, (cost + weight, path + [child]))

        record(trace, current=node, cost=cost, frontier=[(c, p[-1]) for c, p in frontier], visited=visited)      # animation only

    return None, None

def ucs_graph(graph, start, goal, trace=None):
    frontier = [(0, [start])]                          # a list of (total cost, path)
    visited = {}                                       # node -> cost when it was visited

    while len(frontier) > 0:
        cheapest = min(frontier)                       # smallest total cost
        frontier.remove(cheapest)
        cost, path = cheapest
        node = path[-1]

        if node in visited:                            # a cheaper copy was already visited
            continue
        visited[node] = cost

        if node == goal:
            record(trace, current=node, cost=cost, frontier=[(c, p[-1]) for c, p in frontier], visited=visited)  # animation only
            return path, cost

        for neighbor, weight in graph[node]:
            if neighbor not in visited:
                frontier.append((cost + weight, path + [neighbor]))

        record(trace, current=node, cost=cost, frontier=[(c, p[-1]) for c, p in frontier], visited=visited)      # animation only

    return None, None


#%% md
### Run it