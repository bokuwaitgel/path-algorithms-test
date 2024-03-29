import pygame
import heapq
from .RP import heuristic, check


def get_checked_neighbors(node: object):
    """
    Get the neighbors of a node that have been checked or are the start node.

    Args:
        node (Node): The node to check.

    Returns:
        List[Node]: The list of checked or start neighbors.
    """

    checked = []
    for neighbor in node.neighbors:
        if neighbor.is_checked() or neighbor.is_start():
            checked.append(neighbor)
    return checked


def reconstruct_path(current: object, costs: dict, draw: object):
    """
    Reconstruct the path from the end node to the start node.

    Args:
        current (Node): The current node in the search.
        costs (Dict[Node, int]): The cost of reaching each node from the start.
        draw (function): A function used to draw the search on the screen.

    Returns:
        None: The function updates the screen with the path.
    """

    # Continue until the current node is the start node
    while not current.is_start():
        # Find the neighbor with the lowest cost
        current = min(get_checked_neighbors(current), key=lambda x: costs[x])

        # Break if the current node is the start node
        if current.is_start():
            break

        # Draw the path to the current node
        current.make_path()
        draw()


def update_vertex(grid: object, node: object, rhs: dict, g: dict, open_list: list):
    """
    Updates rhs values, and open list

    Args:
        grid (Grid): An object representing the current grid.
        node (Node): Current node being checked.
        rhs (dict): Dictionary of the rhs values.
        g (dict): Dictionary of the g values.
        open_list (list): List of open nodes.

    Returns:
        open_list: List of open nodes.
    """
    if node != grid.start:
        rhs[node] = float("inf")
        for neighbor in node.neighbors:
            if (
                neighbor.is_checked()
                or neighbor.is_start()
                or neighbor.is_unchecked()
                or (neighbor.is_end() and neighbor.been_checked)
            ):
                rhs[node] = min(rhs[node], g[neighbor] + 1)

        open_list = [(key, value) for key, value in open_list if value != node]
        heapq.heapify(open_list)

        if g[node] != rhs[node]:
            heapq.heappush(open_list, (calc_key(grid.end, node, g, rhs), node))
    return open_list


def calc_key(end: object, node: object, g: dict, rhs: dict):
    """
    Calculates the key for the priority queue

    Args:
        end (Node): The end node of the current grid.
        node (Node): Current node.
        g (dict): Dictionary of the g values.
        rhs (dict): Dictionary of the rhs values.

    Returns:
        tuple: (min of g & rhs + heuristic, min of g & rhs)
    """
    return (
        min(g[node], rhs[node]) + heuristic("manhattan", node, end),
        min(g[node], rhs[node]),
    )


def lpa_star(grid: object):
    """
    Performs the LPA* algorithm from start to end.

    Args:
        grid (Grid): An object representing the current grid

    Returns:
        None: The function updates the screen with the search progress and path.
    """
    rhs = {node: float("inf") for row in grid.grid for node in row}
    g = {node: float("inf") for row in grid.grid for node in row}
    open_list = []

    rhs[grid.start] = 0
    topKey = calc_key(grid.end, grid.start, g, rhs)
    open_list.append((topKey, grid.start))

    # Initialize a flag to track whether the search should continue
    run = True

    while (
        topKey < calc_key(grid.end, grid.end, g, rhs) or rhs[grid.end] != g[grid.end]
    ) and run:
        # Check for exit events
        run = check(pygame.event.get(), run)

        # Check for no path found
        if open_list:
            topKey, node = heapq.heappop(open_list)
        else:
            break

        if g[node] > rhs[node]:
            g[node] = rhs[node]
        else:
            g[node] = float("inf")
            open_list = update_vertex(grid, node, rhs, g, open_list)

        # Update neighboring nodes
        for neighbor in node.neighbors:
            if (
                not neighbor.is_start()
                and not neighbor.is_end()
                and not neighbor.is_checked()
            ):
                neighbor.uncheck()
            open_list = update_vertex(grid, neighbor, rhs, g, open_list)

        # Update the screen with the search progress
        grid.draw()

        # Check the current node if it is not the start node or end node
        if not node.is_start() and not node.is_end():
            node.check()

        # Reconstruct path if at end
        if node == grid.end:
            reconstruct_path(node, rhs, grid.draw)
