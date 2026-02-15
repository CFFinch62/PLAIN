def fibonacci(n):
    """Calculate Fibonacci number recursively."""
    if n <= 1:
        return n

    a = fibonacci(n - 1)
    b = fibonacci(n - 2)
    return a + b


def main():
    count = 10

    for i in range(0, count + 1):
        result = fibonacci(i)
        print(f"Fibonacci({i}) = {result}")


if __name__ == "__main__":
    main()

