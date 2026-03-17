import pytest
from solution import PersistentSegTree


def make_pst(arr):
    pst = PersistentSegTree(arr)
    for v in arr:
        pst.insert(v)
    return pst


def brute_kth(arr, l, r, k):
    sub = sorted(arr[l:r + 1])
    return sub[k - 1]


# ─── Basic correctness tests ────────────────────────────────────────────────

def test_single_element():
    pst = make_pst([42])
    assert pst.kth(0, 0, 1) == 42


def test_two_elements_sorted():
    pst = make_pst([1, 3])
    assert pst.kth(0, 1, 1) == 1
    assert pst.kth(0, 1, 2) == 3


def test_three_elements_full_range():
    arr = [3, 1, 2]
    pst = make_pst(arr)
    assert pst.kth(0, 2, 1) == 1
    assert pst.kth(0, 2, 2) == 2
    assert pst.kth(0, 2, 3) == 3


def test_partial_ranges():
    arr = [5, 2, 8, 1, 9, 3, 7, 4, 6]
    pst = make_pst(arr)
    assert pst.kth(0, 2, 1) == 2  # [5,2,8] → sorted [2,5,8]
    assert pst.kth(0, 2, 2) == 5
    assert pst.kth(0, 2, 3) == 8
    assert pst.kth(3, 5, 1) == 1  # [1,9,3] → [1,3,9]
    assert pst.kth(3, 5, 2) == 3
    assert pst.kth(3, 5, 3) == 9


# ─── Tests that catch the >= vs > bug ──────────────────────────────────────

def test_kth_equals_left_count():
    """
    The bug manifests when k == cnt_left: correct goes left, buggy goes right.
    Construct a case where exactly k elements are in the left half.
    """
    # arr = [1, 3, 2]
    # range [0,2], k=1: cnt_left (values in [1,2]) = 2 after all 3 inserted
    # but for specific sub-range:
    # range [0,1] = [1,3]: left half (val=1) has cnt=1, k=1 → should go left → answer=1
    arr = [1, 3, 2]
    pst = make_pst(arr)
    assert pst.kth(0, 1, 1) == 1  # [1,3] → 1st smallest = 1


def test_kth_boundary_all_values():
    arr = [4, 2, 6, 1, 5, 3]
    pst = make_pst(arr)
    for l in range(len(arr)):
        for r in range(l, len(arr)):
            for k in range(1, r - l + 2):
                expected = brute_kth(arr, l, r, k)
                got = pst.kth(l, r, k)
                assert got == expected, (
                    f"kth({l},{r},{k}): expected {expected}, got {got}"
                )


def test_duplicate_values():
    arr = [3, 1, 3, 2, 1, 3]
    pst = make_pst(arr)
    assert pst.kth(0, 5, 1) == 1
    assert pst.kth(0, 5, 2) == 1
    assert pst.kth(0, 5, 3) == 2
    assert pst.kth(0, 5, 4) == 3
    assert pst.kth(0, 5, 5) == 3
    assert pst.kth(0, 5, 6) == 3


def test_large_range_stress():
    import random
    random.seed(7)
    arr = [random.randint(1, 20) for _ in range(30)]
    pst = make_pst(arr)
    for _ in range(50):
        l = random.randint(0, 25)
        r = random.randint(l, 29)
        k = random.randint(1, r - l + 1)
        expected = brute_kth(arr, l, r, k)
        got = pst.kth(l, r, k)
        assert got == expected, f"kth({l},{r},{k}): expected {expected}, got {got}"


def test_single_value_array():
    arr = [7] * 10
    pst = make_pst(arr)
    for l in range(10):
        for r in range(l, 10):
            assert pst.kth(l, r, 1) == 7
            assert pst.kth(l, r, r - l + 1) == 7
