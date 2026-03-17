class AffineSegTree:
    """
    Segment tree supporting:
      range_affine(l, r, a, b): for i in [l,r], arr[i] = a*arr[i] + b
      range_sum(l, r): return sum(arr[l:r+1])
    All indices are 0-based.
    """

    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.lazy_a = [1] * (4 * self.n)
        self.lazy_b = [0] * (4 * self.n)
        self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, v, l, r):
        if l == r:
            self.tree[v] = arr[l]
            return
        m = (l + r) // 2
        self._build(arr, 2 * v, l, m)
        self._build(arr, 2 * v + 1, m + 1, r)
        self.tree[v] = self.tree[2 * v] + self.tree[2 * v + 1]

    def _apply(self, v, l, r, a, b):
        """Apply affine transform arr[i] = a*arr[i] + b to the subtree at v."""
        size = r - l + 1
        self.tree[v] = a * self.tree[v] + b * size
        # Compose lazy tags: existing lazy is (lazy_a[v], lazy_b[v]),
        # applying new transform (a, b) on top:
        #   new(x) = a * (lazy_a*x + lazy_b) + b = (a*lazy_a)*x + (a*lazy_b + b)
        # BUG: wrong formula — uses lazy_a[v]*b instead of a*lazy_b[v]
        self.lazy_b[v] = self.lazy_a[v] * b + self.lazy_b[v]
        self.lazy_a[v] = a * self.lazy_a[v]

    def _push(self, v, l, r):
        if self.lazy_a[v] != 1 or self.lazy_b[v] != 0:
            m = (l + r) // 2
            self._apply(2 * v, l, m, self.lazy_a[v], self.lazy_b[v])
            self._apply(2 * v + 1, m + 1, r, self.lazy_a[v], self.lazy_b[v])
            self.lazy_a[v] = 1
            self.lazy_b[v] = 0

    def _update(self, v, l, r, ql, qr, a, b):
        if ql > r or qr < l:
            return
        if ql <= l and r <= qr:
            self._apply(v, l, r, a, b)
            return
        self._push(v, l, r)
        m = (l + r) // 2
        self._update(2 * v, l, m, ql, qr, a, b)
        self._update(2 * v + 1, m + 1, r, ql, qr, a, b)
        self.tree[v] = self.tree[2 * v] + self.tree[2 * v + 1]

    def _query(self, v, l, r, ql, qr):
        if ql > r or qr < l:
            return 0
        if ql <= l and r <= qr:
            return self.tree[v]
        self._push(v, l, r)
        m = (l + r) // 2
        return self._query(2 * v, l, m, ql, qr) + self._query(2 * v + 1, m + 1, r, ql, qr)

    def range_affine(self, l, r, a, b):
        """Set arr[i] = a*arr[i] + b for all i in [l, r]."""
        self._update(1, 0, self.n - 1, l, r, a, b)

    def range_sum(self, l, r):
        """Return sum of arr[l..r]."""
        return self._query(1, 0, self.n - 1, l, r)
