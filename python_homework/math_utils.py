######################################################
            # Math Operations #
######################################################


######################################################
            # 1. Power Function #
######################################################


def compute_power(base: int, exponent: int) -> int:
    """Computes the power of a base raised to an exponent with certain limits.

    Args:
        base (int): The base number.
        exponent (int): The exponent to raise the base to.

    Returns:
        int: The result of base raised to the exponent.
    """
    if base > 1000000 or exponent > 1000:
        raise ValueError("Inputs too large for power calculation. Limit: base <= 1,000,000 and exponent <= 1000")
    return base ** exponent


######################################################
            # 2. Fibonacci Function #
######################################################

def compute_fibonacci(n: int) -> int:
    """
    Calculate the n-th number in the Fibonacci sequence.

    The Fibonacci sequence starts with 0 and 1, and each number after that
    is the sum of the previous two numbers.

    Args:
        n (int): The position in the sequence (starting from 0).

    Returns:
        int: The n-th Fibonacci number
    """
    # Check for invalid or too large input
    if n < 0:
        raise ValueError("Fibonacci not defined for negative numbers")
    if n > 100000:
        raise ValueError("Too large. Max allowed input is 100,000")

    # Handle first two Fibonacci numbers
    if n == 0:
        return 0
    if n == 1:
        return 1

    # Start the sequence with 0 and 1
    first = 0
    second = 1

    # Loop to get to the n-th number
    for i in range(2, n + 1):
        next_num = first + second
        first = second
        second = next_num

    return second


######################################################
            # 3. Factorial Function #
######################################################

def compute_factorial(n:int) -> int:
    """
    Return the factorial of a number.

    Args:
        n: A number (must be 0 or more)

    Returns:
        The factorial of the number n.
    """

    if n < 0:
        raise ValueError("Negative numbers are not allowed")

    if n > 5000:
        raise ValueError("Number is too large. Max is 5000")

    if n == 0:
        return 1

    numbers = list(range(1, n + 1))  # a list from 1 to n
    result = 1

    for num in numbers:
        result = result * num  # multiply one by one

    return result

