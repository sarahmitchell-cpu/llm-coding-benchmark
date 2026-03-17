import pytest
from solution import build_suffix_array, build_lcp_array


def naive_suffix_array(s):
    n = len(s)
    suffixes = sorted(range(n), key=lambda i: s[i:])
    return suffixes


def naive_lcp(s, sa):
    n = len(s)
    lcp = [0] * n
    for i in range(1, n):
        a, b = sa[i - 1], sa[i]
        h = 0
        while a + h < n and b + h < n and s[a + h] == s[b + h]:
            h += 1
        lcp[i] = h
    return lcp


# ─── Suffix array basic tests ───────────────────────────────────────────────

def test_sa_single_char():
    sa, _ = build_suffix_array("a")
    assert sa == [0]


def test_sa_two_distinct():
    sa, _ = build_suffix_array("ba")
    assert sa == [1, 0]  # "a" < "ba"


def test_sa_banana():
    # banana → suffixes sorted: a, ana, anana, banana, na, nana
    # indices:                   5, 3,   1,    0,      4,  2
    sa, _ = build_suffix_array("banana")
    assert sa == [5, 3, 1, 0, 4, 2]


def test_sa_abcabc():
    sa, _ = build_suffix_array("abcabc")
    expected = naive_suffix_array("abcabc")
    assert sa == expected


def test_sa_all_same():
    s = "aaaa"
    sa, _ = build_suffix_array(s)
    expected = naive_suffix_array(s)
    assert sa == expected


def test_sa_sorted_string():
    s = "abcdef"
    sa, _ = build_suffix_array(s)
    expected = naive_suffix_array(s)
    assert sa == expected


def test_sa_reverse_sorted():
    s = "fedcba"
    sa, _ = build_suffix_array(s)
    expected = naive_suffix_array(s)
    assert sa == expected


# ─── Tests that expose the rank-recomputation bug ──────────────────────────

def test_sa_repeated_pattern():
    """Repeated patterns need correct rank deduplication across multiple steps."""
    for s in ["abababab", "aababaab", "mississippi", "aabbaabb"]:
        sa, _ = build_suffix_array(s)
        expected = naive_suffix_array(s)
        assert sa == expected, f"SA wrong for '{s}': got {sa}, expected {expected}"


def test_sa_ranks_are_consistent():
    """Verify that rank array is consistent with suffix array order."""
    s = "mississippi"
    sa, rank = build_suffix_array(s)
    n = len(s)
    for i in range(n):
        assert rank[sa[i]] == i, (
            f"rank[sa[{i}]] = rank[{sa[i]}] = {rank[sa[i]]}, expected {i}"
        )


def test_lcp_banana():
    s = "banana"
    sa, _ = build_suffix_array(s)
    lcp = build_lcp_array(s, sa)
    # sa = [5,3,1,0,4,2]
    # suffixes: "a","ana","anana","banana","na","nana"
    # LCP:       0,   1,    3,      0,       0,   2
    assert lcp == [0, 1, 3, 0, 0, 2]


def test_lcp_mississippi():
    s = "mississippi"
    sa, _ = build_suffix_array(s)
    lcp = build_lcp_array(s, sa)
    expected_lcp = naive_lcp(s, sa)
    assert lcp == expected_lcp


def test_sa_stress():
    """Stress test against naive implementation."""
    import random
    import string
    random.seed(13)
    for _ in range(20):
        n = random.randint(2, 40)
        alphabet = random.choice(["ab", "abc", string.ascii_lowercase[:5]])
        s = ''.join(random.choice(alphabet) for _ in range(n))
        sa, _ = build_suffix_array(s)
        expected = naive_suffix_array(s)
        assert sa == expected, f"SA wrong for '{s}'"
