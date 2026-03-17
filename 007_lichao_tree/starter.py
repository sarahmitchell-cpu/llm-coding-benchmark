class LiChaoTree:
    """
    Li Chao Segment Tree for minimum-value linear function queries.

    Stores a set of lines y = m*x + b and answers:
      query(x): minimum value of any stored line at position x

    x-coordinates are integers in [x_lo, x_hi].
    """

    def __init__(self, x_lo, x_hi):
        self.x_lo = x_lo
        self.x_hi = x_hi
        INF = float('inf')
        size = 4 * (x_hi - x_lo + 2)
        # Each node stores (slope, intercept) of the dominant line
        self.lines = [(0, INF)] * size  # (m, b) meaning y = m*x + b

    def _val(self, line, x):
        return line[0] * x + line[1]

    def _add(self, node, lo, hi, m, b):
        mid = (lo + hi) // 2
        cur = self.lines[node]

        new_wins_mid = self._val((m, b), mid) < self._val(cur, mid)
        new_wins_left = self._val((m, b), lo) < self._val(cur, lo)

        if new_wins_mid:
            self.lines[node] = (m, b)
            m, b = cur
            # After swap, flip which endpoint the remaining line wins
            new_wins_left = not new_wins_left

        if lo == hi:
            return

        # BUG: wrong subtree selection — should recurse left when new_wins_left,
        # right otherwise; but the branches are swapped here.
        if new_wins_left:
            self._add(2 * node + 1, mid + 1, hi, m, b)
        else:
            self._add(2 * node, lo, mid, m, b)

    def _query(self, node, lo, hi, x):
        best = self._val(self.lines[node], x)
        if lo == hi:
            return best
        mid = (lo + hi) // 2
        if x <= mid:
            return min(best, self._query(2 * node, lo, mid, x))
        else:
            return min(best, self._query(2 * node + 1, mid + 1, hi, x))

    def add_line(self, m, b):
        """Add line y = m*x + b to the tree."""
        self._add(1, self.x_lo, self.x_hi, m, b)

    def query(self, x):
        """Return the minimum value among all stored lines at x."""
        return self._query(1, self.x_lo, self.x_hi, x)
