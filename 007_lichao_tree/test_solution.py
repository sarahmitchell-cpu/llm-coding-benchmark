import pytest
from solution import LiChaoTree


def brute_min(lines, x):
    return min(m * x + b for m, b in lines)


# ─── Basic tests ────────────────────────────────────────────────────────────

def test_single_line():
    t = LiChaoTree(0, 10)
    t.add_line(2, 3)   # y = 2x + 3
    assert t.query(0) == 3
    assert t.query(5) == 13
    assert t.query(10) == 23


def test_two_lines_no_crossing():
    t = LiChaoTree(0, 10)
    t.add_line(1, 10)  # y = x + 10
    t.add_line(2, 0)   # y = 2x
    # At x=0: line1=10, line2=0 → min=0 (line2 wins everywhere from x=0)
    # At x=10: line1=20, line2=20 → equal, min=20
    assert t.query(0) == 0
    assert t.query(10) == 20


def test_crossing_lines():
    # line1: y = 3x + 0  (steep, bad for large x)
    # line2: y = x + 4   (less steep, good for large x)
    # Crossing at x=2: both give 6
    t = LiChaoTree(0, 10)
    t.add_line(3, 0)
    t.add_line(1, 4)
    # x=0: min(0, 4) = 0
    # x=1: min(3, 5) = 3
    # x=2: min(6, 6) = 6
    # x=3: min(9, 7) = 7
    # x=10: min(30, 14) = 14
    assert t.query(0) == 0
    assert t.query(1) == 3
    assert t.query(3) == 7
    assert t.query(10) == 14


# ─── Tests requiring correct subtree placement (expose the bug) ─────────────

def test_many_lines_convex_hull():
    """Lines form a lower convex hull; each query should pick the minimum."""
    lines = [(i, -i * i) for i in range(0, 11)]  # y = i*x - i^2
    t = LiChaoTree(0, 20)
    for m, b in lines:
        t.add_line(m, b)
    for x in range(0, 21):
        expected = brute_min(lines, x)
        assert t.query(x) == expected, f"x={x}: expected {expected}, got {t.query(x)}"


def test_decreasing_slope_lines():
    """Lines with decreasing slope — minimum is dominated by different lines."""
    lines = [(10 - i, i * 2) for i in range(11)]
    t = LiChaoTree(0, 10)
    for m, b in lines:
        t.add_line(m, b)
    for x in range(11):
        expected = brute_min(lines, x)
        assert t.query(x) == expected, f"x={x}: expected {expected}, got {t.query(x)}"


def test_lines_same_slope_different_intercept():
    """Lines with same slope — the one with smallest intercept always wins."""
    t = LiChaoTree(0, 10)
    t.add_line(2, 5)
    t.add_line(2, 3)
    t.add_line(2, 7)
    for x in range(11):
        assert t.query(x) == 2 * x + 3


def test_stress_random_lines():
    """Stress test: many lines, verify against brute force."""
    import random
    random.seed(42)
    lines = [(random.randint(-10, 10), random.randint(-100, 100)) for _ in range(50)]
    t = LiChaoTree(0, 100)
    for m, b in lines:
        t.add_line(m, b)
    for x in [0, 1, 5, 10, 25, 50, 75, 99, 100]:
        expected = brute_min(lines, x)
        assert t.query(x) == expected, f"x={x}: expected {expected}, got {t.query(x)}"


def test_negative_x_range():
    """Lines over negative x range."""
    t = LiChaoTree(-10, 10)
    t.add_line(1, 0)   # y = x
    t.add_line(-1, 0)  # y = -x
    # At x=-5: min(-5, 5) = -5 (line y=x wins)
    # At x=5:  min(5, -5) = -5 (line y=-x wins)
    # At x=0:  min(0, 0)  = 0
    assert t.query(-5) == -5
    assert t.query(5) == -5
    assert t.query(0) == 0


def test_interleaved_add_and_query():
    """Adding lines interleaved with queries."""
    t = LiChaoTree(0, 20)
    t.add_line(5, 0)    # y = 5x
    assert t.query(4) == 20
    t.add_line(-1, 50)  # y = -x + 50
    # At x=4: min(20, 46) = 20
    # At x=10: min(50, 40) = 40
    assert t.query(4) == 20
    assert t.query(10) == 40
    t.add_line(2, 5)    # y = 2x + 5
    # At x=4: min(20, 46, 13) = 13
    assert t.query(4) == 13
    # At x=10: min(50, 40, 25) = 25
    assert t.query(10) == 25
