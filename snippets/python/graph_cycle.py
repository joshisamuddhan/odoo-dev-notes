"""Dependency ordering (topological sort) + cycle detection - FK-ordered table sync."""


def find_cycle(graph):
    """graph = {node: [dependencies]}. Returns a cycle as a list, or None."""
    WHITE, GREY, BLACK = 0, 1, 2
    colour, stack = {}, []

    def visit(node):
        colour[node] = GREY
        stack.append(node)
        for dep in graph.get(node, []):
            if colour.get(dep, WHITE) == GREY:
                return stack[stack.index(dep):] + [dep]
            if colour.get(dep, WHITE) == WHITE:
                found = visit(dep)
                if found:
                    return found
        stack.pop()
        colour[node] = BLACK

    for n in list(graph):
        if colour.get(n, WHITE) == WHITE:
            found = visit(n)
            if found:
                return found
    return None


def topo_order(graph):
    """Parents first. Raises ValueError on a cycle."""
    cycle = find_cycle(graph)
    if cycle:
        raise ValueError("cycle: " + " -> ".join(cycle))
    order, seen = [], set()

    def visit(n):
        if n in seen:
            return
        seen.add(n)
        for d in graph.get(n, []):
            visit(d)
        order.append(n)

    for n in graph:
        visit(n)
    return order
