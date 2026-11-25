"""A tiny mean-squared-error regression example using fictional data."""


def loss_and_gradient(xs, ys, w, b):
    if not xs or len(xs) != len(ys):
        raise ValueError("x and y must be non-empty and equally sized")
    errors = [w * x + b - y for x, y in zip(xs, ys)]
    n = len(xs)
    return (sum(error ** 2 for error in errors) / n,
            2 * sum(error * x for error, x in zip(errors, xs)) / n,
            2 * sum(errors) / n)


def fit(xs, ys, learning_rate=.1, steps=500):
    if learning_rate <= 0 or not isinstance(steps, int) or steps < 0:
        raise ValueError("learning rate must be positive and steps non-negative")
    w = b = 0.0
    initial, _, _ = loss_and_gradient(xs, ys, w, b)
    for _ in range(steps):
        _, dw, db = loss_and_gradient(xs, ys, w, b)
        w -= learning_rate * dw
        b -= learning_rate * db
    final, _, _ = loss_and_gradient(xs, ys, w, b)
    return {"w": w, "b": b, "initial_loss": initial, "final_loss": final}


if __name__ == "__main__":
    result = fit([0, 1, 2, 3], [1, 3, 5, 7])
    print(f"训练前损失: {result['initial_loss']:.3f}")
    print(f"训练后损失: {result['final_loss']:.6f}")
    print(f"参数: w={result['w']:.3f}, b={result['b']:.3f}")
