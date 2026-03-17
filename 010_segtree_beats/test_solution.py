import pytest
from solution import SegTreeBeats


def make(arr):
    return SegTreeBeats(arr)


def brute_chmin(arr, l, r, v):
    arr = arr[:]
    for i in range(l, r + 1):
        arr[i] = min(arr[i], v)
    return arr


# ─── Basic tests ────────────────────────────────────────────────────────────

def test_no_change_when_v_large():
    arr = [3, 5, 2, 8, 4]
    t = make(arr)
    t.range_chmin(0, 4, 100)
    assert t.range_sum(0, 4) == 22
    assert t.range_max(0, 4) == 8


def test_full_range_chmin():
    arr = [5, 3, 7, 2, 9]
    t = make(arr)
    t.range_chmin(0, 4, 4)
    assert t.range_max(0, 4) == 4
    assert t.range_sum(0, 4) == 17  # [4,3,4,2,4]


def test_partial_range_chmin():
    arr = [1, 5, 8, 3, 7]
    t = make(arr)
    t.range_chmin(1, 3, 4)  # [1,4,4,3,7]
    assert t.range_sum(0, 4) == 19
    assert t.range_max(1, 3) == 4
    assert t.range_max(0, 4) == 7


def test_chmin_single_element():
    arr = [10, 20, 30]
    t = make(arr)
    t.range_chmin(1, 1, 5)
    assert t.range_sum(0, 2) == 45
    assert t.range_max(0, 2) == 30


# ─── Tests that expose the second_max comparison bug ────────────────────────

def test_chmin_equals_second_max():
    """
    The bug: when second_max == val, the buggy code applies lazily but shouldn't.
    This can corrupt the sum because cnt_max is stale after the operation.
    """
    # arr = [3, 5, 5, 7]
    # Node covering [0,3]: max1=7, max2=5, cnt_max=1, sum=20
    # range_chmin(0, 3, 5):
    #   max2=5 < 5 is False (they're equal) → correct must recurse
    #   buggy applies lazily: changes 7→5, sum=18, cnt_max becomes stale
    arr = [3, 5, 5, 7]
    t = make(arr)
    t.range_chmin(0, 3, 5)
    # Expected: [3, 5, 5, 5], sum=18, max=5
    assert t.range_sum(0, 3) == 18
    assert t.range_max(0, 3) == 5


def test_chmin_with_equal_max_values():
    """Multiple elements at max value, chmin at second_max."""
    arr = [2, 8, 4, 8, 8]
    t = make(arr)
    t.range_chmin(0, 4, 4)  # [2,4,4,4,4], sum=18
    assert t.range_sum(0, 4) == 18
    assert t.range_max(0, 4) == 4


def test_chained_chmin_operations():
    arr = [10, 6, 10, 6, 10]
    t = make(arr)
    # range [0,4]: max1=10, max2=6, cnt_max=3, sum=42
    t.range_chmin(0, 4, 6)   # chmin(6) → [6,6,6,6,6], sum=30
    assert t.range_sum(0, 4) == 30
    assert t.range_max(0, 4) == 6
    t.range_chmin(0, 2, 4)   # [4,4,4,6,6], sum=24
    assert t.range_sum(0, 4) == 24
    assert t.range_max(0, 2) == 4


def test_nested_chmin_partial_overlap():
    arr = [9, 7, 5, 7, 9]
    t = make(arr)
    t.range_chmin(0, 4, 7)   # [7,7,5,7,7], sum=33
    assert t.range_sum(0, 4) == 33
    t.range_chmin(1, 3, 6)   # [7,6,5,6,7], sum=31
    assert t.range_sum(0, 4) == 31
    assert t.range_max(1, 3) == 6
    t.range_chmin(0, 4, 6)   # [6,6,5,6,6], sum=29
    assert t.range_sum(0, 4) == 29
    assert t.range_max(0, 4) == 6


def test_stress_random():
    import random
    random.seed(99)
    n = 32
    arr = [random.randint(1, 100) for _ in range(n)]
    t = make(arr)
    cur = arr[:]
    for _ in range(200):
        l = random.randint(0, n - 1)
        r = random.randint(l, n - 1)
        v = random.randint(1, 100)
        t.range_chmin(l, r, v)
        cur = brute_chmin(cur, l, r, v)
        # Spot-check sum and max
        ql = random.randint(0, n - 1)
        qr = random.randint(ql, n - 1)
        assert t.range_sum(ql, qr) == sum(cur[ql:qr + 1]), \
            f"sum mismatch at [{ql},{qr}]"
        assert t.range_max(ql, qr) == max(cur[ql:qr + 1]), \
            f"max mismatch at [{ql},{qr}]"
