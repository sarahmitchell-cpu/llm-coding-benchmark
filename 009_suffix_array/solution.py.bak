def build_suffix_array(s):
    """
    Build the suffix array of string s using O(n log n) doubling algorithm.

    Returns sa, rank.
    """
    n = len(s)
    if n == 0:
        return [], []
    if n == 1:
        return [0], [0]

    rank = [ord(c) for c in s]
    sa = list(range(n))

    step = 1
    while step < n:
        def sort_key(i):
            r2 = rank[i + step] if i + step < n else -1
            return (rank[i], r2)

        sa.sort(key=sort_key)

        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for j in range(1, n):
            prev, cur = sa[j - 1], sa[j]
            r2_prev = rank[prev + step] if prev + step < n else -1
            r2_cur = rank[cur + step] if cur + step < n else -1
            if rank[cur] == rank[prev] and r2_cur == r2_prev:
                new_rank[cur] = new_rank[prev]
            else:
                new_rank[cur] = new_rank[prev] + 1

        rank = new_rank
        if rank[sa[n - 1]] == n - 1:
            break
        step *= 2

    return sa, rank


def build_lcp_array(s, sa):
    """
    Build the LCP array using Kasai's algorithm.
    lcp[i] = LCP between suffix sa[i] and sa[i-1]; lcp[0] = 0.
    """
    n = len(s)
    rank = [0] * n
    for i, v in enumerate(sa):
        rank[v] = i

    lcp = [0] * n
    h = 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[rank[i]] = h
            if h > 0:
                h -= 1
    return lcp
