"""Small vectors for hand calculation, not a production embedding implementation."""
import math


def dot(a, b):
    if not a or len(a) != len(b):
        raise ValueError("vectors must be non-empty and have the same length")
    return sum(x * y for x, y in zip(a, b))


def cosine(a, b):
    numerator = dot(a, b)
    denominator = math.sqrt(dot(a, a)) * math.sqrt(dot(b, b))
    if denominator == 0:
        raise ValueError("cosine is undefined for a zero vector")
    return numerator / denominator


def matvec(matrix, vector):
    if not matrix:
        raise ValueError("matrix must contain at least one row")
    return [dot(row, vector) for row in matrix]


if __name__ == "__main__":
    query = [1, 0]
    for name, document in [("短", [1, 1]), ("长", [10, 10])]:
        print(f"{name}: 点积 {dot(query, document)}, 余弦 {cosine(query, document):.3f}")
    print("线性变换:", matvec([[1, 2], [3, 4]], [2, 1]))
