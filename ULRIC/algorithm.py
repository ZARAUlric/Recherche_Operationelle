import itertools

def solve_assignment(matrix, mode="min"):

    n = len(matrix)
    best_cost = None
    best_assign = None

    for perm in itertools.permutations(range(n)):

        cost = sum(matrix[i][perm[i]] for i in range(n))

        if best_cost is None:
            best_cost = cost
            best_assign = perm
        else:
            if mode == "min" and cost < best_cost:
                best_cost = cost
                best_assign = perm
            elif mode == "max" and cost > best_cost:
                best_cost = cost
                best_assign = perm

    return best_assign, best_cost