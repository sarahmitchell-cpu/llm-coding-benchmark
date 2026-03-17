class SegTreeBeats:
    def __init__(self, arr):
        n = len(arr)
        self.n = n
        self.mx1 = [0]*(4*n); self.mx2 = [-1]*(4*n)
        self.cnt = [0]*(4*n); self.tot = [0]*(4*n)
        self.lz = [float('inf')]*(4*n)
        self._build(arr, 1, 0, n-1)

    def _build(self, a, v, l, r):
        self.lz[v] = float('inf')
        if l == r:
            self.mx1[v] = a[l]; self.mx2[v] = -1
            self.cnt[v] = 1; self.tot[v] = a[l]; return
        m = (l+r)//2
        self._build(a, 2*v, l, m); self._build(a, 2*v+1, m+1, r)
        self._pull(v)

    def _pull(self, v):
        lc, rc = 2*v, 2*v+1
        self.tot[v] = self.tot[lc] + self.tot[rc]
        if self.mx1[lc] == self.mx1[rc]:
            self.mx1[v] = self.mx1[lc]
            self.mx2[v] = max(self.mx2[lc], self.mx2[rc])
            self.cnt[v] = self.cnt[lc] + self.cnt[rc]
        elif self.mx1[lc] > self.mx1[rc]:
            self.mx1[v] = self.mx1[lc]
            self.mx2[v] = max(self.mx2[lc], self.mx1[rc])
            self.cnt[v] = self.cnt[lc]
        else:
            self.mx1[v] = self.mx1[rc]
            self.mx2[v] = max(self.mx1[lc], self.mx2[rc])
            self.cnt[v] = self.cnt[lc] + self.cnt[rc]

    def _chmin(self, v, val):
        if val >= self.mx1[v]: return
        self.tot[v] -= (self.mx1[v] - val) * self.cnt[v]
        self.mx1[v] = val; self.lz[v] = min(self.lz[v], val)

    def _push(self, v):
        if self.lz[v] < float('inf'):
            self._chmin(2*v, self.lz[v]); self._chmin(2*v+1, self.lz[v])
            self.lz[v] = float('inf')

    def _upd(self, v, l, r, ql, qr, val):
        if ql > r or qr < l or self.mx1[v] <= val: return
        if ql <= l and r <= qr and self.mx2[v] < val:
            self._chmin(v, val); return
        self._push(v); m = (l+r)//2
        self._upd(2*v, l, m, ql, qr, val); self._upd(2*v+1, m+1, r, ql, qr, val)
        self._pull(v)

    def _qsum(self, v, l, r, ql, qr):
        if ql > r or qr < l: return 0
        if ql <= l and r <= qr: return self.tot[v]
        self._push(v); m = (l+r)//2
        return self._qsum(2*v, l, m, ql, qr) + self._qsum(2*v+1, m+1, r, ql, qr)

    def _qmax(self, v, l, r, ql, qr):
        if ql > r or qr < l: return -float('inf')
        if ql <= l and r <= qr: return self.mx1[v]
        self._push(v); m = (l+r)//2
        return max(self._qmax(2*v, l, m, ql, qr), self._qmax(2*v+1, m+1, r, ql, qr))

    def range_chmin(self, l, r, v): self._upd(1, 0, self.n-1, l, r, v)
    def range_sum(self, l, r): return self._qsum(1, 0, self.n-1, l, r)
    def range_max(self, l, r): return self._qmax(1, 0, self.n-1, l, r)
