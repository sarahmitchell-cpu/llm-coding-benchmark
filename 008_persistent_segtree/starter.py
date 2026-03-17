class Node:
    __slots__ = ('left', 'right', 'cnt')

    def __init__(self, left=None, right=None, cnt=0):
        self.left = left
        self.right = right
        self.cnt = cnt


class PersistentSegTree:
    """
    Persistent Segment Tree for offline k-th smallest queries.

    Usage:
      pst = PersistentSegTree(values)   # coordinate-compress 'values'
      for v in values:
        pst.insert(v)                   # build versions 1..n
      pst.kth(l, r, k)                  # k-th smallest in values[l..r] (1-indexed)
    """

    def __init__(self, values):
        sorted_vals = sorted(set(values))
        self.compress = {v: i for i, v in enumerate(sorted_vals)}
        self.decompress = sorted_vals
        self.m = len(sorted_vals)
        # Version 0: empty tree
        self.roots = [self._new_node()]

    def _new_node(self, left=None, right=None, cnt=0):
        return Node(left, right, cnt)

    def _build_empty(self):
        return self._new_node()

    def _insert(self, prev, lo, hi, pos):
        """Insert position 'pos' (compressed index), return new root."""
        node = self._new_node(prev.left, prev.right, prev.cnt + 1)
        if lo == hi:
            return node
        mid = (lo + hi) // 2
        if pos <= mid:
            node.left = self._insert(
                prev.left if prev.left else self._new_node(),
                lo, mid, pos
            )
        else:
            node.right = self._insert(
                prev.right if prev.right else self._new_node(),
                mid + 1, hi, pos
            )
        return node

    def insert(self, value):
        """Append one value and create a new version."""
        pos = self.compress[value]
        prev = self.roots[-1]
        new_root = self._insert(prev, 0, self.m - 1, pos)
        self.roots.append(new_root)

    def _kth(self, left_root, right_root, lo, hi, k):
        """Find k-th smallest using difference of versions right_root and left_root."""
        if lo == hi:
            return lo
        mid = (lo + hi) // 2

        left_cnt_l = left_root.left.cnt if left_root.left else 0
        left_cnt_r = right_root.left.cnt if right_root.left else 0
        cnt_left = left_cnt_r - left_cnt_l

        # BUG: uses > instead of >= — when k == cnt_left we should go left,
        # but the buggy code goes right with k=0 (0th element is undefined).
        if cnt_left > k:
            return self._kth(
                left_root.left if left_root.left else self._new_node(),
                right_root.left if right_root.left else self._new_node(),
                lo, mid, k
            )
        else:
            return self._kth(
                left_root.right if left_root.right else self._new_node(),
                right_root.right if right_root.right else self._new_node(),
                mid + 1, hi, k - cnt_left
            )

    def kth(self, l, r, k):
        """
        Return the k-th smallest value (1-indexed) among the inserted
        values at positions [l, r] (0-indexed into insertion order).
        """
        # versions: roots[0] is empty, roots[i] has first i values
        left_root = self.roots[l]
        right_root = self.roots[r + 1]
        compressed_idx = self._kth(left_root, right_root, 0, self.m - 1, k)
        return self.decompress[compressed_idx]
