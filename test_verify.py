import unittest
from fractions import Fraction
from itertools import product
from math import isqrt

from verify import PrimeSieve, base_bounds, floor_ratio, intervals, survey


def direct_prefix(beta, n, j, m):
    remainder = Fraction(1, n)
    digits = []
    for _ in range(j + m - 1):
        remainder *= beta
        digit = int(remainder)
        digits.append(digit)
        remainder -= digit
    return tuple(digits[j - 1:])


class Certificates(unittest.TestCase):
    def test_half_open_windows_against_direct_greedy_division(self):
        for beta in (Fraction(3), Fraction(5, 2)):
            # Exact representation at every Horner step, including powers of 5/2.
            scale = beta.denominator ** 16
            bounds = int(beta * scale), int(beta * scale), scale
            for j, m in product(range(1, 6), range(1, 6)):
                shell = range(int(beta ** (j - 1)) + 1, int(beta ** j) + 1)
                observed = {n: direct_prefix(beta, n, j, m) for n in shell}
                for word, first, last in intervals(bounds, j, m):
                    self.assertEqual(list(range(first, last + 1)),
                                     [n for n in shell if observed[n] == tuple(map(int, word))])

    def test_sieve_endpoints_and_empty_intervals(self):
        sieve = PrimeSieve(100)
        primes = {n for n in range(2, 101) if all(n % d for d in range(2, isqrt(n) + 1))}
        for left in range(1, 101):
            for right in range(left - 1, 101):
                self.assertEqual(sieve.has_prime(left, right),
                                 any(left <= p <= right for p in primes))

    def test_certified_rounding(self):
        with self.assertRaises(ArithmeticError):
            floor_ratio((9, 11), (10, 10))
        self.assertEqual(floor_ratio((10, 10), (10, 10)), 1)
        for base, floor in (("pi", 3141592), ("e", 2718281)):
            lo, hi, scale = base_bounds(base, 20)
            self.assertEqual(floor_ratio((lo * 10**6, hi * 10**6), (scale, scale)), floor)

    def test_small_shells(self):
        shells, missing = survey(32, 30)
        self.assertIn(("pi", 2, 1, 2, 1), shells)
        self.assertIn(("pi", 2, 2, "10", 8, 9), missing)
        self.assertEqual((shells, missing), survey(32, 45))


if __name__ == "__main__":
    unittest.main()
