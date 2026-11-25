"""Single-channel 2D cross-correlation for teaching; no training or gradients."""


def dimensions(matrix):
    if not matrix or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("matrix must be non-empty and rectangular")
    return len(matrix), len(matrix[0])


def correlate(image, kernel, stride=1, padding=0):
    height, width = dimensions(image)
    kh, kw = dimensions(kernel)
    if not isinstance(stride, int) or stride <= 0 or not isinstance(padding, int) or padding < 0:
        raise ValueError("stride must be positive; padding must be non-negative")
    padded = ([[0] * (width + 2 * padding) for _ in range(padding)] +
              [[0] * padding + list(row) + [0] * padding for row in image] +
              [[0] * (width + 2 * padding) for _ in range(padding)])
    if height + 2 * padding < kh or width + 2 * padding < kw:
        raise ValueError("kernel does not fit padded image")
    out_h = (height + 2 * padding - kh) // stride + 1
    out_w = (width + 2 * padding - kw) // stride + 1
    return [[sum(padded[i * stride + y][j * stride + x] * kernel[y][x]
                 for y in range(kh) for x in range(kw))
             for j in range(out_w)] for i in range(out_h)]


def relu(matrix):
    dimensions(matrix)
    return [[max(0, value) for value in row] for row in matrix]


if __name__ == "__main__":
    image = [[1, 2, 0], [0, 1, 2], [2, 2, 1]]
    kernel = [[1, 0], [-1, 0]]
    feature = correlate(image, kernel)
    print("互相关结果:", feature)
    print("ReLU 结果:", relu(feature))
