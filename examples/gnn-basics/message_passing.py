"""One mean-aggregation step, not a trained GNN or a GCN implementation."""


def aggregate(features, incoming_neighbors):
    if not features:
        raise ValueError("at least one node is required")
    size = len(next(iter(features.values())))
    if size == 0 or any(len(vector) != size for vector in features.values()):
        raise ValueError("node feature vectors must have equal non-zero dimensions")
    if set(incoming_neighbors) - set(features):
        raise ValueError("neighbor list contains an unknown target")
    output = {}
    for node in features:
        neighbors = incoming_neighbors.get(node, [])
        if len(set(neighbors)) != len(neighbors) or any(other not in features for other in neighbors):
            raise ValueError("neighbors must be known and unique")
        # Include self once, even if a self-edge is already listed.
        sources = [node] + [other for other in neighbors if other != node]
        output[node] = [sum(features[source][i] for source in sources) / len(sources) for i in range(size)]
    return output


if __name__ == "__main__":
    features = {"A": [1, 0], "B": [0, 1], "C": [1, 1]}
    neighbors = {"A": ["B"], "B": ["A", "C"], "C": ["B"]}
    for node, vector in aggregate(features, neighbors).items():
        print(node, [round(value, 3) for value in vector])
