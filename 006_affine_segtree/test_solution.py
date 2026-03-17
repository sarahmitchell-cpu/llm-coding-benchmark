import pytest
from solution import AffineSegTree


def make(arr):
    return AffineSegTree(arr)


def brute_affine(arr, l, r, a, b):
    arr = arr[:]
    for i in range(l, r + 1):
        arr[i] = a * arr[i] + b
    return arr


# ─── Basic single-operation tests ──────────────────────────────────────────


def test_single_multiply_full_range():
    t = make([1, 2, 3, 4, 5])
    t.range_affine(0, 4, 2, 0)
    assert t.range_sum(0, 4) == 30


def test_single_add_full_range():
    t = make([1, 1, 1, 1])
    t.range_affine(0, 3, 1, 5)
    assert t.range_sum(0, 3) == 24


def test_single_affine_partial():
    t = make([1, 2, 3, 4, 5])
    t.range_affine(1, 3, 3, 2)  # [1, 8, 11, 14, 5]
    assert t.range_sum(1, 3) == 33
    assert t.range_sum(0, 4) == 39


# ─── Tests that require correct lazy composition (expose the bug) ───────────


def test_double_affine_element_query():
    # arr = [1, 1, 1, 1]
    # range_affine(0,3, 2, 3)  → [5, 5, 5, 5]  (lazy at root: a=2, b=3)
    # range_affine(0,1, 2, 0)  → [10, 10, 5, 5] (forces pushdown of root)
    # Element query [0,0] forces further pushdown: correct=10, buggy=7
    t = make([1, 1, 1, 1])
    t.range_affine(0, 3, 2, 3)
    t.range_affine(0, 1, 2, 0)
    assert t.range_sum(0, 0) == 10
    assert t.range_sum(1, 1) == 10
    assert t.range_sum(2, 3) == 10


def test_triple_overlapping_affine():
    # arr = [1, 2, 3, 4]
    # range_affine(0,3, 3, 1) → [4, 7, 10, 13], sum=34
    # range_affine(1,2, 2, 5) → [4, 19, 25, 13], sum=61
    # range_affine(0,1, 1, 3) → [7, 22, 25, 13], sum=67
    t = make([1, 2, 3, 4])
    t.range_affine(0, 3, 3, 1)
    t.range_affine(1, 2, 2, 5)
    t.range_affine(0, 1, 1, 3)
    assert t.range_sum(0, 3) == 67
    assert t.range_sum(0, 0) == 7
    assert t.range_sum(1, 1) == 22


def test_chained_multiply_then_add_overlap():
    # arr = [2, 2, 2, 2]
    # range_affine(0,3, 3, 2) → [8,8,8,8]
    # range_affine(0,3, 2, 1) → [17,17,17,17]
    # range_affine(0,1, 4, 3) → [71,71,17,17]
    t = make([2, 2, 2, 2])
    t.range_affine(0, 3, 3, 2)
    t.range_affine(0, 3, 2, 1)
    t.range_affine(0, 1, 4, 3)
    assert t.range_sum(0, 0) == 71
    assert t.range_sum(1, 1) == 71
    assert t.range_sum(2, 3) == 34
    assert t.range_sum(0, 3) == 176


def test_nested_affine_large():
    t = make([1, 1, 1, 1, 1, 1, 1, 1])
    t.range_affine(0, 7, 2, 1)   # all 3
    t.range_affine(0, 3, 3, 0)   # [9,9,9,9,3,3,3,3]
    t.range_affine(0, 1, 1, 2)   # [11,11,9,9,3,3,3,3]
    assert t.range_sum(0, 1) == 22
    assert t.range_sum(0, 7) == 52
    assert t.range_sum(0, 0) == 11


def test_deep_composition_correctness():
    # Build deep lazy composition requiring 3 levels of pushdown
    t = make([1] * 16)
    t.range_affine(0, 15, 2, 1)    # all 3, lazy at root
    t.range_affine(0, 7, 3, 0)     # left half=9, lazy pushed down once
    t.range_affine(0, 3, 2, 4)     # left quarter=22, pushed again
    t.range_affine(0, 1, 5, 1)     # leftmost pair=111, pushed again
    assert t.range_sum(0, 0) == 111
    assert t.range_sum(1, 1) == 111
    assert t.range_sum(2, 3) == 44
    assert t.range_sum(4, 7) == 36
    assert t.range_sum(8, 15) == 24


def test_alternating_updates_and_queries():
    t = make([0] * 8)
    t.range_affine(0, 7, 1, 1)    # all 1
    assert t.range_sum(0, 7) == 8
    t.range_affine(0, 3, 2, 0)    # [2,2,2,2,1,1,1,1]
    assert t.range_sum(0, 3) == 8
    t.range_affine(2, 5, 3, 1)    # [2,2,7,7,4,4,1,1]
    assert t.range_sum(2, 5) == 22
    assert t.range_sum(0, 7) == 28
