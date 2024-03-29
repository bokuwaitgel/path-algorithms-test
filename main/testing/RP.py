import pygame
import math
import threading
from queue import Queue


def determinant_2x2(matrix: list):
    """
    Determinant for a 2x2 matrix, used for divide by zero checking

    Args:
        matrix (list): covariance matrix between given points

    Returns:
        float: determinant
    """
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def covariance_matrix(point1: tuple, point2: tuple):
    """
    Calculates the covariance matrix for the given points

    Args:
        point1 (tuple): x, y coordinates for node 1
        point2 (tuple): x, y coordinates for node 2

    Returns:
        list: covariance matrix
    """
    x1, y1 = point1
    x2, y2 = point2
    
    cov_x_x = (x1 - x2) ** 2
    cov_y_y = (y1 - y2) ** 2
    cov_x_y = (x1 - x2) * (y1 - y2)

    return [[cov_x_x, cov_x_y], [cov_x_y, cov_y_y]]


# Mahalanobis distance
def mahalanobis(node1: object, node2: object):
    """
    Calculates the Mahalanobis distance between two nodes.

    Args:
        node1 (Node): The first node.
        node2 (Node): The second node.

    Returns:
        float: The Mahalanobis distance between the two nodes.
    """
    matrix = covariance_matrix(node1.get_pos(), node2.get_pos())

    # Checking for potential divide by zero errors
    if determinant_2x2(matrix) < 1e-10:
        return float("inf")

    # Getting the difference between the two nodes' respective x and y values
    diff = [a - b for a, b in zip(node1.get_pos(), node2.get_pos())]

    result = 0
    for i, d in enumerate(diff):
        result += d * d / matrix[i][i]
    return math.sqrt(result)


# Minkowski distance
def minkowski(node1: object, node2: object, p: int or float):
    x1, y1 = node1.get_pos()
    x2, y2 = node2.get_pos()

    d1 = abs(x1 - x2)**p
    d2 = abs(y1 - y2)**p

    return (d1 + d2)**(1/p)


# Chebyshev distance
def chebyshev(node1: object, node2: object):
    """
    Calculate the Chebyshev distance between two nodes.

    Args:
        node1 (Node): The first node.
        node2 (Node): The second node.

    Returns:
        int: The Chebyshev distance between the two nodes.
    """
    x1, y1 = node1.get_pos()
    x2, y2 = node2.get_pos()

    return max(abs(x1 - x2), abs(y1 - y2))


# Manhattan distance
def manhattan(node1: object, node2: object):
    """
    Calculate the Manhattan distance between two nodes.

    Args:
        node1 (Node): The first node.
        node2 (Node): The second node.

    Returns:
        int: The Manhattan distance between the two nodes.
    """
    x1, y1 = node1.get_pos()
    x2, y2 = node2.get_pos()

    return abs(x1 - x2) + abs(y1 - y2)


# Euclidean distance
def euclidean(node1: object, node2: object):
    """
    Calculate the Euclidean distance between two nodes.

    Args:
        node1 (Node): The first node.
        node2 (Node): The second node.

    Returns:
        float: The Euclidean distance between the two nodes.
    """
    x1, y1 = node1.get_pos()
    x2, y2 = node2.get_pos()

    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# Dynamic Manhattan distance
def d_manhattan(node1: object, node2: object):
    """
    Calculate the Dynamic Manhattan distance between two nodes.

    Args:
        node1 (Node): The first node.
        node2 (Node): The second node.

    Returns:
        int: The Dynamic Manhattan distance between the two nodes.
    """
    x1, y1 = node1.get_pos()
    x2, y2 = node2.get_pos()

    blocked_penalty = len(node1.neighbors)
    for node in node1.neighbors:
        if not node.is_checked() and not node.is_unchecked():
            blocked_penalty -= 1

    return abs(x1 - x2) + abs(y1 - y2) + blocked_penalty


def heuristic(type: str, node1: object, node2: object, *args):
    """
    Calculate the heuristic distance between two nodes.

    Args:
        type (str): The type of heuristic distance to use.
            Valid options are "euclidean" and "manhattan".
        node1 (Node): The first node.
        node2 (Node): The second node.
        *args (list): additional arguments for different heuristics

    Returns:
        float: The heuristic distance between the two nodes.
    """
    match type:
        case "chebyshev":
            return chebyshev(node1, node2)
        case "d_manhattan":
            return d_manhattan(node1, node2)
        case "euclidean":
            return euclidean(node1, node2)
        case "manhattan":
            return manhattan(node1, node2)
        case "minkowski":
            return minkowski(node1, node2, args[0])
        case "mahalanobis":
            return mahalanobis(node1, node2)
        case _:
            return manhattan(node1, node2)


def get_unvisited_nodes(start: object):
    """
    Find all nodes connected to the start node in the grid.

    Args:
        start (Node): The starting node.

    Returns:
        List[Node]: A list of nodes connected to the start node.
    """
    Q = Queue()
    Q_hash = [start]
    Q.put(start)

    while not Q.empty():
        current = Q.get()

        for neighbor in current.neighbors:
            if neighbor not in Q_hash:
                Q.put(neighbor)
                Q_hash.append(neighbor)
    return Q_hash


def check(current: object):
    """
    Mark the current node as visited.

    Args:
        current (Node): The current node being visited.

    Returns:
        None
    """
    if not current.is_start() and not current.is_end():
        current.check()


def count_path(came_from: dict, current: object):
    num_nodes_path = 0

    while current in came_from:
        if not came_from[current].is_start():
            current = came_from[current]
            num_nodes_path += 1
        else:
            break

    return num_nodes_path


def thread_count_path(path_size: list, came_from: object, current: object, target: object):
    """
    Reconstructs the path from the current node to the target node in a maze.

    Args:
        path_size (int): Length of the path found.
        came_from (Dict[Node, Node]): A dictionary containing the nodes traversed
            during the pathfinding algorithm.
        current (Node): The node being checked when the algorithm terminated
        target (Node): The node to traverse back to

    Returns:
        None
    """

    while current in came_from:
        if came_from[current] != target:
            current = came_from[current]
            path_size[0] += 1
        else:
            break


# This method is included for a more aesthetic reconstruction
def thread_construct(args1: tuple, args2: tuple):
    """
    Constructs two threads that will run the `reconstruct_path` function with the
    given arguments. The threads are started and then joined, which waits for
    them to finish before returning.

    Args:
        args1 (tuple): A tuple of arguments to pass to the first
            `reconstruct_path` function.
        args2 (tuple): A tuple of arguments to pass to the second
            `reconstruct_path` function.

    Returns:
        path_size (int): Length of the path found.
    """
    # Create two threads that will run the `reconstruct_path` function with the
    # given arguments
    path1 = [0]
    path2 = [0]

    n1 = threading.Thread(target=thread_count_path, args=(path1, *args1))
    n2 = threading.Thread(target=thread_count_path, args=(path2, *args2))

    # Start the threads
    n1.start()
    n2.start()

    # Wait for the threads to finish
    n1.join()
    n2.join()
    return path1[0] + path2[0] + 1