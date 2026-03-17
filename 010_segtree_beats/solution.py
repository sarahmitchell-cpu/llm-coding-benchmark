class SegTreeBeats:
    """
    Segment Tree Beats (Ji Driver Segmentation Tree).

    Supports:
      range_chmin(l, r, v): for i in [l,r], arr[i] = min(arr[i], v)
      range_sum(l, r):       return sum(arr[l..r])
      range_max(l, r):       return max(arr[l..r])

    All indices 0-based.
    """

    def __init__(self, arr):
        n = len(arr)
        self.n = n
        self.max1 = [0] * (4 * n)
        self.max2 = [-1] * (4 * n)
        self.cnt_max = [0] * (4 * n)
        self.total = [0] * (4 * n)
        self.lazy = [float('inf')] * (4 * n)
        self._build(arr, 1, 0, n - 1)

    def _build(self, arr, v, l, r):
        self.lazy[v] = float('inf')
        if l == r:
            self.max1[v] = arr[l]
            self.max2[v] = -1
            self.cnt_max[v] = 1
            self.total[v] = arr[l]
            return
        m = (l + r) // 2
        self._build(arr, 2 * v, l, m)
        self._build(arr, 2 * v + 1, m + 1, r)
        self._pull(v)

    def _pull(self, v):
        lc, rc = 2 * v, 2 * v + 1
        self.total[v] = self.total[lc] + self.total[rc]
        if self.max1[lc] == self.max1[rc]:
            self.max1[v] = self.max1[lc]
            self.max2[v] = max(self.max2[lc], self.max2[rc])
            self.cnt_max[v] = self.cnt_max[lc] + self.cnt_max[rc]
        elif self.max1[lc] > self.max1[rc]:
            self.max1[v] = self.max1[lc]
            self.max2[v] = max(self.max2[lc], self.max1[rc])
            self.cnt_max[v] = self.cnt_max[lc]
        else:
            self.max1[v] = self.max1[rc]
            self.max2[v] = max(self.max1[lc], self.max2[rc])
            self.cnt_max[v] = self.cnt_max[rc]

    def _apply_chmin(self, v, val):
        if val >= self.max1[v]:
            return
        self.total[v] -= (self.max1[v] - val) * self.cnt_max[v]
        self.max1[v] = val
        self.lazy[v] = min(self.lazy[v], val)

    def _push(self, v):
        if self.lazy[v] < float('inf'):
            self._apply_chmin(2 * v, self.lazy[v])
            self._apply_chmin(2 * v + 1, self.lazy[v])
            self.lazy[v] = float('inf')

    def _update_chmin(self, v, l, r, ql, qr, val):
        if ql > r or qr < l or self.max1[v] <= val:
            return
        # Apply lazily only when: second_max < val (strictly less)
        # This guarantees only max values change and cnt_max stays accurate.
        if ql <= l and r <= qr and self.max2[v] < val:
            self._apply_chmin(v, val)
            return
        self._push(v)
        m = (l + r) // 2
        self._update_chmin(2 * v, l, m, ql, qr, val)
        self._update_chmin(2 * v + 1, m + 1, r, ql, qr, val)
        self._pull(v)

    def _query_sum(self, v, l, r, ql, qr):
        if ql > r or qr < l:
            return 0
        if ql <= l and r <= qr:
            return self.total[v]
        self._push(v)
        m = (l + r) // 2
        return self._query_sum(2 * v, l, m, ql, qr) + self._query_sum(2 * v + 1, m + 1, r, ql, qr)

    def _query_max(self, v, l, r, ql, qr):
        if ql > r or qr < l:
            return -float('inf')
        if ql <= l and r <= qr:
            return self.max1[v]
        self._push(v)
        m = (l + r) // 2
        return max(self._query_max(2 * v, l, m, ql, qr),
                   self._query_max(2 * v + 1, m + 1, r, ql, qr))

    def range_chmin(self, l, r, v):
        """Set arr[i] = min(arr[i], v) for all i in [l, r]."""
        self._update_chmin(1, 0, self.n - 1, l, r, v)

    def range_sum(self, l, r):
        """Return sum(arr[l..r])."""
        return self._query_sum(1, 0, self.n - 1, l, r)

    def range_max(self, l, r):
        """Return max(arr[l..r])."""
        return self._query_max(1, 0, self.n - 1, l, r)
