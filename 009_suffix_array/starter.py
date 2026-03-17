def build_suffix_array(s):
    n = len(s)
    if n == 0: return [], []
    if n == 1: return [0], [0]

    rank = [ord(c) for c in s]
    sa = list(range(n))

    step = 1
    while step < n:
        def sort_key(i, _r=rank, _s=step):
            return (_r[i], _r[i + _s] if i + _s < n else 0)

        sa.sort(key=sort_key)

        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for j in range(1, n):
            prev, cur = sa[j-1], sa[j]
            pk = sort_key(prev)
            ck = sort_key(cur)
            new_rank[cur] = new_rank[prev] if ck == pk else new_rank[prev] + 1

        rank = new_rank
        if rank[sa[n-1]] == n-1:
            break
        step *= 2

    return sa, rank


def build_lcp_array(s, sa):
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
