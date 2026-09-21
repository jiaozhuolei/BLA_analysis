import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
import os
os.chdir(r"D:\python\BLA_3_types\code\sup fig3")

# Keep every label as a real SVG <text> element.
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.family"] = "DejaVu Sans"


DATA_PATH = Path("filtered_paths.json")
OUTPUT_DIR = Path("./pathway_figure_topology")

PNG_PATH = OUTPUT_DIR / "BLA_PFC_projection_patterns_topology_15um.png"
SVG_PATH = OUTPUT_DIR / "BLA_PFC_projection_patterns_topology_15um.svg"

PATTERN_COLORS = {1: "#1459B0", 2: "#EF6206", 3: "#21813A", 4: "#C9252D"}
PATTERN_BACKGROUNDS = {1: "#F8FAFF", 2: "#FFF9F4", 3: "#F7FBF7", 4: "#FFF7F7"}

# Terminal color is determined only by the target brain region.
TERMINAL_COLORS = {
    "ORB": "#0B5CAD",
    "ILA": "#F28E2B",
    "ACA": "#C9252D",
    "PL": "#6F42C1",
    "DP": "#008C95",
    "FRP": "#8C564B",
}


def split_mainline_and_loops(regions):
    """Separate closed excursions from the straight main line.

    A -> B -> A -> C becomes main line A -> C plus loop A -> B -->> A.
    The earliest closing repeat is removed first, which also handles nested
    returns without leaving a non-target node at the end of a pathway.
    """
    mainline = list(regions)
    loops = []

    while True:
        first_seen = {}
        repeat_pair = None
        for end, region in enumerate(mainline):
            if region in first_seen:
                repeat_pair = (first_seen[region], end)
                break
            first_seen[region] = end

        if repeat_pair is None:
            break

        start, end = repeat_pair
        anchor = mainline[start]
        interior = tuple(mainline[start + 1 : end])
        if interior:
            loops.append((anchor, interior))

        # Keep the first anchor and remove the excursion plus repeated anchor.
        mainline = mainline[: start + 1] + mainline[end + 1 :]

    return mainline, loops


class PatternGraph:
    """Prefix tree for straight main trajectories plus attached loop motifs."""

    def __init__(self):
        self.nodes = {
            0: {
                "region": "BLA",
                "children": {},
                "terminal": None,
                "depth": 0,
            }
        }
        self.next_id = 1
        self.solid_edges = Counter()
        self.loop_paths = Counter()

    def add_path(self, regions, terminal_group):
        if not regions or regions[0] != "BLA":
            regions = ["BLA", *regions]

        mainline, loops = split_mainline_and_loops(regions)
        current = 0
        node_for_region = {"BLA": 0}
        path_edges = set()

        for region in mainline[1:]:
            children = self.nodes[current]["children"]
            if region in children:
                child = children[region]
            else:
                child = self.next_id
                self.next_id += 1
                children[region] = child
                self.nodes[child] = {
                    "region": region,
                    "children": {},
                    "terminal": None,
                    "depth": self.nodes[current]["depth"] + 1,
                }

            path_edges.add((current, child))
            current = child
            node_for_region[region] = child

        self.nodes[current]["terminal"] = terminal_group
        self.solid_edges.update(path_edges)

        for anchor_region, interior in loops:
            anchor_node = node_for_region.get(anchor_region)
            if anchor_node is not None:
                self.loop_paths[(anchor_node, interior)] += 1

        if self.nodes[current]["region"] != terminal_group:
            print(
                f"Warning: terminal group {terminal_group} does not match "
                f"final node {self.nodes[current]['region']}"
            )

    def leaf_nodes(self):
        return [node_id for node_id, node in self.nodes.items() if not node["children"]]


def assign_layout(graph, left, right, bottom, top):
    """Place every unbranched main trajectory on one horizontal line."""
    leaves = graph.leaf_nodes()
    if len(leaves) == 1:
        leaf_y = {leaves[0]: (bottom + top) / 2}
    else:
        spacing = (top - bottom) / (len(leaves) - 1)
        leaf_y = {leaf: top - i * spacing for i, leaf in enumerate(leaves)}

    y_pos = {}

    def get_y(node_id):
        if node_id in y_pos:
            return y_pos[node_id]
        children = list(graph.nodes[node_id]["children"].values())
        if not children:
            y_pos[node_id] = leaf_y[node_id]
        else:
            # Keep the highest-frequency continuation on the same horizontal
            # line as the shared prefix. Less frequent alternatives branch
            # once and then continue horizontally on their own lanes.
            for child in children:
                get_y(child)
            primary_child = max(
                children,
                key=lambda child: graph.solid_edges[(node_id, child)],
            )
            y_pos[node_id] = y_pos[primary_child]
        return y_pos[node_id]

    get_y(0)
    for node_id in graph.nodes:
        get_y(node_id)

    max_depth = max(node["depth"] for node in graph.nodes.values()) or 1
    x_pos = {
        node_id: left + (right - left) * node["depth"] / max_depth
        for node_id, node in graph.nodes.items()
    }
    return x_pos, y_pos


def edge_width(count):
    return 0.78 + 0.34 * min(count - 1, 5)


def draw_arrow(ax, start, end, count=1, color="#15191E", dashed=False, rad=0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=10.5,
            linewidth=edge_width(count) + (0.16 if dashed else 0),
            linestyle=(0, (4, 3)) if dashed else "solid",
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=22,
            shrinkB=22,
            zorder=2 if dashed else 1,
        )
    )


def draw_node(
    ax,
    x,
    y,
    region,
    pattern_color,
    terminal_group=None,
    is_root=False,
    radius=0.60,
    fontsize=None,
):
    if is_root:
        face = edge = "#30343B"
        text_color = "white"
    elif terminal_group:
        face = TERMINAL_COLORS.get(terminal_group, "#555555")
        edge = face
        text_color = "white"
    else:
        face = "white"
        edge = pattern_color
        text_color = "#20242A"

    ax.add_patch(
        Circle(
            (x, y),
            radius,
            facecolor=face,
            edgecolor=edge,
            linewidth=1.80,
            zorder=3,
        )
    )
    if fontsize is None:
        fontsize = 14.0 if len(region) <= 4 else 12.2
    ax.text(
        x,
        y,
        region,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight="bold",
        color=text_color,
        zorder=4,
    )


def draw_loop_paths(ax, graph, x_pos, y_pos, color, panel_bottom, panel_top):
    """Draw loop excursions away from the straight main trajectory."""
    loop_radius = 0.350
    panel_mid = (panel_bottom + panel_top) / 2
    custom_loops = []
    reused_index = 0

    # If the loop's outward segment already exists in the merged main tree,
    # reuse those nodes and add only the dashed return. This greatly reduces
    # duplication around BLA, EP and ec.
    for (anchor_node, interior), count in graph.loop_paths.items():
        current = anchor_node
        existing_chain = []
        for region in interior:
            child = graph.nodes[current]["children"].get(region)
            if child is None:
                existing_chain = []
                break
            existing_chain.append(child)
            current = child

        if existing_chain:
            end_node = existing_chain[-1]
            average_y = (y_pos[end_node] + y_pos[anchor_node]) / 2
            direction = -1 if average_y > panel_mid else 1
            if reused_index % 2:
                direction *= -1
            draw_arrow(
                ax,
                (x_pos[end_node], y_pos[end_node]),
                (x_pos[anchor_node], y_pos[anchor_node]),
                count=count,
                color=color,
                dashed=True,
                rad=0.20 * direction,
            )
            reused_index += 1
            continue

        n_nodes = len(interior)
        spacing = min(0.90, 4.8 / max(n_nodes, 1))
        x_start = x_pos[anchor_node] + 0.92
        x_end = x_start + spacing * max(n_nodes - 1, 0)
        custom_loops.append(
            {
                "anchor": anchor_node,
                "interior": interior,
                "count": count,
                "spacing": spacing,
                "x_start": x_start,
                "x_end": x_end,
            }
        )

    # Long motifs are placed first. A simple interval-based layout assigns
    # overlapping motifs to different vertical bands and avoids main nodes.
    custom_loops.sort(key=lambda item: item["x_end"] - item["x_start"], reverse=True)
    placed = []
    candidate_step = 0.62
    candidate_y = []
    value = panel_bottom + 0.38
    while value <= panel_top - 0.38 + 1e-9:
        candidate_y.append(value)
        value += candidate_step

    # Midpoints between the enlarged main-path lanes are the cleanest places
    # for enlarged loop nodes.
    main_lane_y = sorted(set(y_pos.values()))
    candidate_y.extend(
        (lower + upper) / 2
        for lower, upper in zip(main_lane_y, main_lane_y[1:])
    )
    candidate_y = sorted(set(candidate_y))

    for item in custom_loops:
        anchor_node = item["anchor"]
        anchor_x = x_pos[anchor_node]
        anchor_y = y_pos[anchor_node]
        x_start = item["x_start"]
        x_end = item["x_end"]

        def collision_score(y):
            score = 0
            if abs(y - anchor_y) < 0.80:
                score += 100

            for other_start, other_end, other_y in placed:
                overlaps = not (x_end + 0.36 < other_start or x_start - 0.36 > other_end)
                if overlaps and abs(y - other_y) < 0.75:
                    score += 100

            for node_id in graph.nodes:
                node_x = x_pos[node_id]
                if x_start - 0.38 <= node_x <= x_end + 0.38:
                    distance = abs(y - y_pos[node_id])
                    if distance < 0.80:
                        score += 100
            return score + abs(y - anchor_y)

        loop_y = min(candidate_y, key=collision_score)
        placed.append((x_start, x_end, loop_y))
        direction = 1 if loop_y > anchor_y else -1

        loop_positions = [
            (x_start + index * item["spacing"], loop_y)
            for index in range(len(item["interior"]))
        ]
        if not loop_positions:
            continue

        draw_arrow(ax, (anchor_x, anchor_y), loop_positions[0], count=item["count"])
        for start, end in zip(loop_positions, loop_positions[1:]):
            draw_arrow(ax, start, end, count=item["count"])

        draw_arrow(
            ax,
            loop_positions[-1],
            (anchor_x, anchor_y),
            count=item["count"],
            color=color,
            dashed=True,
            rad=0.48 if direction > 0 else -0.48,
        )

        for (x, y), region in zip(loop_positions, item["interior"]):
            draw_node(
                ax,
                x,
                y,
                region,
                color,
                radius=loop_radius,
                fontsize=11.2 if len(region) <= 4 else 10.0,
            )


with DATA_PATH.open("r", encoding="utf-8") as file:
    payload = json.load(file)

records = payload["records"]
threshold = payload["threshold"]

graphs = {}
pattern_records = {}
for pattern in range(1, 5):
    selected = [record for record in records if record["pattern"] == pattern]
    pattern_records[pattern] = selected
    graph = PatternGraph()
    for record in selected:
        graph.add_path(
            [node["region"] for node in record["filtered"]],
            record["terminal_group"],
        )
    graphs[pattern] = graph


panel_heights = {}
for pattern in range(1, 5):
    leaf_count = max(1, len(graphs[pattern].leaf_nodes()))
    loop_count = len(graphs[pattern].loop_paths)
    panel_heights[pattern] = max(
        4.60,
        0.95 * leaf_count + 0.55 * loop_count + 2.00,
    )

title_height = 0.95
footer_height = 1.75
panel_gap = 0.16
total_height = title_height + footer_height + sum(panel_heights.values()) + 3 * panel_gap

fig, ax = plt.subplots(figsize=(22, total_height), dpi=220)
ax.set_xlim(0, 24)
ax.set_ylim(0, total_height)
ax.axis("off")
fig.patch.set_facecolor("white")

ax.text(
    12,
    total_height - 0.31,
    "BLA–PFC projection patterns",
    ha="center",
    va="center",
    fontsize=19,
    fontweight="bold",
    color="#111111",
)
ax.text(
    12,
    total_height - 0.63,
    f"Segments < {threshold} μm removed • straight main trajectories • repeated regions shown as re-entry loops",
    ha="center",
    va="center",
    fontsize=8.5,
    color="#555B63",
)

current_top = total_height - title_height

for pattern in range(1, 5):
    graph = graphs[pattern]
    selected = pattern_records[pattern]
    color = PATTERN_COLORS[pattern]
    height = panel_heights[pattern]
    bottom = current_top - height

    ax.add_patch(
        FancyBboxPatch(
            (0.45, bottom),
            23.1,
            height,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            linewidth=1.1,
            edgecolor=color,
            facecolor=PATTERN_BACKGROUNDS[pattern],
            zorder=0,
        )
    )

    ax.text(
        0.72,
        current_top - 0.25,
        f"Pattern {pattern}",
        ha="left",
        va="center",
        fontsize=9.5,
        fontweight="bold",
        color="white",
        bbox=dict(boxstyle="round,pad=0.28", facecolor=color, edgecolor=color),
    )
    ax.text(
        2.15,
        current_top - 0.25,
        f"n = {len(selected)}",
        ha="left",
        va="center",
        fontsize=8.2,
        fontweight="bold",
        color="#20242A",
    )

    plot_bottom = bottom + 0.72
    plot_top = current_top - 1.05
    x_pos, y_pos = assign_layout(graph, 1.25, 15.38, plot_bottom, plot_top)

    # The main tree contains only non-repeated regions. Unbranched routes are
    # horizontal and every route ends at its target-colored node.
    for (start, end), count in graph.solid_edges.items():
        draw_arrow(
            ax,
            (x_pos[start], y_pos[start]),
            (x_pos[end], y_pos[end]),
            count=count,
        )

    draw_loop_paths(ax, graph, x_pos, y_pos, color, plot_bottom, plot_top)

    for node_id, node in graph.nodes.items():
        draw_node(
            ax,
            x_pos[node_id],
            y_pos[node_id],
            node["region"],
            color,
            terminal_group=node["terminal"],
            is_root=node_id == 0,
        )

    terminal_counts = Counter(record["terminal_group"] for record in selected)
    legend_x = 17.20
    legend_top = current_top - 0.62
    legend_height = 0.45 + 0.31 * len(terminal_counts)
    ax.add_patch(
        FancyBboxPatch(
            (legend_x - 0.30, legend_top - legend_height),
            2.90,
            legend_height,
            boxstyle="round,pad=0.04,rounding_size=0.10",
            linewidth=0.9,
            linestyle=(0, (3, 2)),
            edgecolor=color,
            facecolor="white",
            zorder=1,
        )
    )
    ax.text(
        legend_x,
        legend_top - 0.20,
        "Terminal group",
        ha="left",
        va="center",
        fontsize=6.9,
        fontweight="bold",
        color="#30343B",
        zorder=4,
    )
    for index, (region, count) in enumerate(sorted(terminal_counts.items())):
        y = legend_top - 0.48 - index * 0.30
        ax.scatter(
            [legend_x + 0.08],
            [y],
            s=42,
            color=TERMINAL_COLORS.get(region, "#555555"),
            zorder=4,
        )
        ax.text(
            legend_x + 0.32,
            y,
            f"{region} ({count})",
            ha="left",
            va="center",
            fontsize=6.5,
            color="#30343B",
            zorder=4,
        )

    current_top = bottom - panel_gap


# Bottom legend
legend_y = 0.92
ax.add_patch(
    FancyArrowPatch(
        (0.85, legend_y),
        (1.75, legend_y),
        arrowstyle="-|>",
        mutation_scale=9,
        linewidth=1.1,
        color="#15191E",
    )
)
ax.text(1.90, legend_y, "Projection direction", va="center", fontsize=7.0, color="#343A40")

ax.add_patch(
    FancyArrowPatch(
        (4.25, legend_y),
        (5.15, legend_y),
        arrowstyle="-|>",
        mutation_scale=9,
        linewidth=1.1,
        linestyle=(0, (4, 3)),
        color=PATTERN_COLORS[1],
        connectionstyle="arc3,rad=0.35",
    )
)
ax.text(5.30, legend_y, "Re-entry / loop", va="center", fontsize=7.0, color="#343A40")

draw_node(ax, 8.05, legend_y, "BLA", PATTERN_COLORS[1], is_root=True)
ax.text(8.70, legend_y, "Starting region", va="center", fontsize=7.0, color="#343A40")

draw_node(ax, 11.15, legend_y, "AI", PATTERN_COLORS[1])
ax.text(11.80, legend_y, "Intermediate region", va="center", fontsize=7.0, color="#343A40")

terminal_x = 14.7
for index, region in enumerate(["ORB", "ILA", "ACA"]):
    x = terminal_x + index * 2.0
    draw_node(ax, x, legend_y, region, PATTERN_COLORS[1], terminal_group=region)
    ax.text(x + 0.58, legend_y, region, va="center", fontsize=6.9, color="#343A40")

freq_x = 20.35
for index, (count, width) in enumerate([(1, 0.78), (2, 1.12), ("≥3", 1.80)]):
    y = 1.28 - index * 0.20
    ax.plot([freq_x, freq_x + 0.70], [y, y], color="#15191E", linewidth=width)
    label = f"{count} pathway" if count == 1 else f"{count} pathways"
    ax.text(freq_x + 0.85, y, label, va="center", fontsize=6.1, color="#343A40")

ax.text(
    12,
    0.20,
    "Shared prefixes are merged. Main trajectories end at target-colored nodes; loop excursions return to their anchor region.",
    ha="center",
    va="center",
    fontsize=6.8,
    color="#59606A",
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
fig.savefig(SVG_PATH, bbox_inches="tight", facecolor="white")
fig.savefig(PNG_PATH, dpi=220, bbox_inches="tight", facecolor="white")
plt.close(fig)

print(SVG_PATH)
print(PNG_PATH)
