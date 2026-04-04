"""
Book 3 – Starter Code
=====================
This file is your entry point for all assignments.
Read the instructions in each assignments/A*/README.md before editing here.

Do NOT delete existing function signatures — only fill in the bodies.
"""

# ---------------------------------------------------------------------------
# Assignment 1 — Part 3: Compression operator
# ---------------------------------------------------------------------------

def apply_compression(data):
    """
    C operator: remove duplicates and return sorted unique values.

    Args:
        data (list of numbers): input dataset

    Returns:
        list: sorted unique values

    Example:
        >>> apply_compression([3, 1, 2, 1, 3, 5])
        [1, 2, 3, 5]
    """
    # TODO: implement this function
    # Hint: Python's set() removes duplicates; sorted() sorts a list
    pass


# ---------------------------------------------------------------------------
# Assignment 2 — Operator Chain class
# ---------------------------------------------------------------------------

class OperatorChain:
    """Implements the full C → K → F → U operator chain."""

    def compress(self, data):
        """
        C operator: unique + sorted values.

        Args:
            data (list): input numbers

        Returns:
            list: sorted unique values
        """
        # TODO: implement (same logic as apply_compression above)
        pass

    def kernel(self, data):
        """
        K operator: find the seed (minimum value).

        Args:
            data (list): compressed data

        Returns:
            number: minimum value in data
        """
        # TODO: implement
        pass

    def flow(self, kernel_val, max_val):
        """
        F operator: generate a doubling sequence from kernel_val up to max_val.

        Args:
            kernel_val (number): starting value (the kernel)
            max_val (number): upper bound (inclusive)

        Returns:
            list: [kernel_val, kernel_val*2, kernel_val*4, ...] while <= max_val

        Example:
            >>> chain.flow(2, 20)
            [2, 4, 8, 16]
        """
        # TODO: implement
        pass

    def unify(self, compressed, flowed):
        """
        U operator: merge two lists into sorted unique values.

        Args:
            compressed (list): output of compress()
            flowed (list): output of flow()

        Returns:
            list: sorted unique values from both lists combined
        """
        # TODO: implement
        pass

    def run(self, data):
        """
        Run the full C → K → F → U chain on data.

        Args:
            data (list): raw input

        Returns:
            dict with keys 'compressed', 'kernel', 'flowed', 'unified'
        """
        compressed = self.compress(data)
        k = self.kernel(compressed)
        max_val = max(compressed) if compressed else 0
        flowed = self.flow(k, max_val)
        unified = self.unify(compressed, flowed)
        return {
            "compressed": compressed,
            "kernel": k,
            "flowed": flowed,
            "unified": unified,
        }


# ---------------------------------------------------------------------------
# Assignment 3 — Scaling Hierarchy class
# ---------------------------------------------------------------------------

class ScalingHierarchy:
    """Tools for exploring Collatz sequences and scaling depth."""

    def collatz_sequence(self, n):
        """
        Return the full Collatz sequence starting from n until it reaches 1.

        Rule:
            if n is even → n / 2
            if n is odd  → 3*n + 1

        Args:
            n (int): starting positive integer

        Returns:
            list: sequence of integers ending with 1

        Example:
            >>> sh.collatz_sequence(6)
            [6, 3, 10, 5, 16, 8, 4, 2, 1]
        """
        # TODO: implement
        pass

    def hierarchy_depth(self, n):
        """
        Return the number of steps in the Collatz sequence for n.

        Args:
            n (int): starting positive integer

        Returns:
            int: length of collatz_sequence(n)
        """
        # TODO: implement using collatz_sequence
        pass

    def find_deepest(self, limit):
        """
        Among all integers from 1 to limit (inclusive),
        return the one with the longest Collatz sequence.

        Args:
            limit (int): upper bound to search

        Returns:
            int: the number with the maximum hierarchy depth
        """
        # TODO: implement using hierarchy_depth
        pass


# ---------------------------------------------------------------------------
# Quick self-test — run: python scripts/starter.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Assignment 1: apply_compression ===")
    result = apply_compression([3, 1, 2, 1, 3, 5])
    print(f"  Input:    [3, 1, 2, 1, 3, 5]")
    print(f"  Expected: [1, 2, 3, 5]")
    print(f"  Got:      {result}")
    print()

    print("=== Assignment 2: OperatorChain ===")
    chain = OperatorChain()
    dataset = [8, 3, 8, 1, 5, 3, 2, 5, 5]
    output = chain.run(dataset)
    print(f"  Input:      {dataset}")
    print(f"  Compressed: {output['compressed']}")
    print(f"  Kernel:     {output['kernel']}")
    print(f"  Flowed:     {output['flowed']}")
    print(f"  Unified:    {output['unified']}")
    print()

    print("=== Assignment 3: ScalingHierarchy ===")
    sh = ScalingHierarchy()
    seq = sh.collatz_sequence(6)
    print(f"  Collatz(6): {seq}")
    print(f"  Depth(27):  {sh.hierarchy_depth(27)}")
    print(f"  Deepest(1-50): {sh.find_deepest(50)}")
