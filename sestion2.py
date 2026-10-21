# Drawing helpers. They only draw things on the screen and are not part of the algorithms.
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Rectangle, Patch
from IPython.display import HTML, display

COLOR = {
    "current": "#f5a623",
    "visited": "#8fd19e",
    "frontier": "#ffe066",
    "unseen": "#e6e6e6",
    "path": "#ee6c4d",
    "stale": "#cfcfcf",
}


def tree_edges(tree):
    return [(parent, child) for parent in tree for child in tree[parent]]


def graph_edges(graph):
    seen, edges = set(), []
    for a in graph:
        for b in graph[a]:
            key = frozenset((a, b))
            if key not in seen:
                seen.add(key)
                edges.append((a, b))
    return edges


def draw_structure(ax, pos, edges, node_colors=None, path_edges=()):
    for a, b in edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        ax.plot([x1, x2], [y1, y2], color="#9a9a9a", linewidth=2, zorder=1)
    for a, b in path_edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        ax.plot([x1, x2], [y1, y2], color=COLOR["path"], linewidth=5, zorder=2)
    for name, (x, y) in pos.items():
        color = node_colors[name] if node_colors else COLOR["unseen"]
        ax.add_patch(
            Circle(
                (x, y),
                0.3,
                facecolor=color,
                edgecolor="#333333",
                linewidth=1.5,
                zorder=3,
            )
        )
        ax.text(x, y, name, ha="center", va="center", fontsize=14, zorder=4)


def show_structure(pos, edges, title):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    draw_structure(ax, pos, edges)
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs) - 1, max(xs) + 1)
    ax.set_ylim(min(ys) - 1, max(ys) + 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title)
    plt.show()


def record(trace, current, frontier, visited):
    """Saves one snapshot for the animation. Does nothing when trace is None."""
    if trace is not None:
        trace.append(
            {
                "current": current,
                "frontier": list(frontier),
                "visited": list(visited),
            }
        )


def animate(
    pos,
    edges,
    trace,
    path,
    algo_name,
    frontier_name,
    frontier_note,
    interval=1400,
):
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    longest = max(len(s["frontier"]) for s in trace) if trace else 0
    x_min, y_min = min(xs), min(ys)
    x_max = max(max(xs) + 1, x_min + 0.8 * longest + 0.5)

    fig, ax = plt.subplots(figsize=(8, 6.5))
    legend = [
        Patch(color=COLOR["current"], label="node being visited"),
        Patch(color=COLOR["visited"], label="already visited"),
        Patch(
            color=COLOR["frontier"], label="waiting in the " + frontier_name
        ),
        Patch(color=COLOR["unseen"], label="not discovered yet"),
        Patch(color=COLOR["path"], label="final path"),
    ]

    def update(i):
        ax.clear()
        step = trace[i]
        is_last = i == len(trace) - 1
        on_path = set(path) if (is_last and path) else set()
        colors = {}
        for n in pos:
            if n in on_path:
                colors[n] = COLOR["path"]
            elif n == step["current"]:
                colors[n] = COLOR["current"]
            elif n in step["visited"]:
                colors[n] = COLOR["visited"]
            elif n in step["frontier"]:
                colors[n] = COLOR["frontier"]
            else:
                colors[n] = COLOR["unseen"]
        path_edges = list(zip(path, path[1:])) if on_path else []
        draw_structure(ax, pos, edges, colors, path_edges)

        box_y = y_min - 1.8
        ax.text(
            x_min - 0.4,
            box_y + 0.95,
            frontier_name.capitalize() + " " + frontier_note,
            fontsize=10,
            ha="left",
        )
        if step["frontier"]:
            for k, item in enumerate(step["frontier"]):
                stale = item in step["visited"]
                ax.add_patch(
                    Rectangle(
                        (x_min - 0.4 + 0.8 * k, box_y),
                        0.7,
                        0.7,
                        facecolor=COLOR["stale"]
                        if stale
                        else COLOR["frontier"],
                        edgecolor="#333333",
                    )
                )
                ax.text(
                    x_min - 0.05 + 0.8 * k,
                    box_y + 0.35,
                    str(item),
                    ha="center",
                    va="center",
                    fontsize=12,
                )
        else:
            ax.text(x_min - 0.4, box_y + 0.3, "(empty)", fontsize=11, ha="left")

        ax.set_xlim(x_min - 1, x_max)
        ax.set_ylim(box_y - 0.6, max(ys) + 1)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(
            f"{algo_name}, step {i + 1} of {len(trace)}: visiting {step['current']}\n"
            f"visited so far: {step['visited']}",
            fontsize=12,
        )
        ax.legend(handles=legend, loc="upper right", fontsize=8)

    anim = FuncAnimation(
        fig, update, frames=len(trace), interval=interval, repeat=False
    )
    plt.close(fig)
    return HTML(anim.to_jshtml())


# --- 1. Tree Search ---
tree = {
    "A": ["B", "C", "D"],
    "B": ["E", "F"],
    "C": [],
    "D": ["G"],
    "E": [],
    "F": ["H"],
    "G": [],
    "H": [],
}

tree_pos = {
    "A": (2.25, 3),
    "B": (0.75, 2),
    "C": (2.5, 2),
    "D": (4.0, 2),
    "E": (0.0, 1),
    "F": (1.5, 1),
    "G": (4.0, 1),
    "H": (1.5, 0),
}

ROOT, TREE_GOAL = "A", "H"


def bfs_tree(tree, root, goal, trace=None):
    queue = [[root]]
    visited = []

    while queue:
        path = queue.pop(0)
        node = path[-1]
        visited.append(node)

        if node == goal:
            record(trace, node, [p[-1] for p in queue], visited)
            return path

        for child in tree.get(node, []):
            queue.append(path + [child])

        record(trace, node, [p[-1] for p in queue], visited)

    return None


# --- 2. Graph Search ---
graph = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F"],
    "D": ["B", "G"],
    "E": ["B", "F"],
    "F": ["C", "E"],
    "G": ["D"],
}

graph_pos = {
    "A": (2.0, 3),
    "B": (0.8, 2),
    "C": (3.2, 2),
    "D": (0.0, 1),
    "E": (1.8, 1),
    "F": (3.2, 1),
    "G": (0.0, 0),
}

START, GRAPH_GOAL = "A", "F"


def bfs_graph(graph, start, goal, trace=None):
    queue = [[start]]
    visited = []

    while queue:
        path = queue.pop(0)
        node = path[-1]

        if node in visited:
            continue

        visited.append(node)

        if node == goal:
            record(trace, node, [p[-1] for p in queue], visited)
            return path

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                queue.append(path + [neighbor])

        record(trace, node, [p[-1] for p in queue], visited)

    return None


# --- Execution and Output ---
show_structure(tree_pos, tree_edges(tree), "The tree we will search")

graph_trace = []
graph_path = bfs_graph(graph, START, GRAPH_GOAL, graph_trace)

print("Path from", START, "to", GRAPH_GOAL, ":", graph_path)
if graph_trace:
    print("Order in which nodes were visited:", graph_trace[-1]["visited"])
    print("Number of nodes visited:", len(graph_trace[-1]["visited"]))