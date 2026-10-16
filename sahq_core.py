#Copyright (c) 2026.Chutiphong Bunloed
#All Rights Reserved.

import numpy as np

class D16Plus:
    def __init__(self):
        self.dim = 16
        self.basis = self._build()
        self.gram = self.basis @ self.basis.T
        self.det = float(np.round(np.linalg.det(self.gram), 10))
        self.inverse = np.linalg.inv(self.gram)

    def _build(self):
        b = np.zeros((16, 16))
        i = np.arange(15)
        b[i, i] = 1.0
        b[i, i + 1] = -1.0
        b[15] = 0.5
        return b

    def norm_sq(self, v):
        return float(np.asarray(v) @ self.gram @ np.asarray(v))

    def even(self, v):
        return int(np.sum(np.asarray(v, dtype=int))) % 2 == 0

    def unimodular(self):
        return abs(self.det - 1.0) < 1e-9

    def self_dual(self):
        return bool(np.allclose(self.gram, self.inverse))

    def coset(self, x):
        return int(abs(int(x)) % 2)

    def orbit(self, x):
        return int(abs(int(x)) % 32)


class SO32:
    def __init__(self):
        self.dim = 32
        self.generators = self.dim * (self.dim - 1) // 2

    def orbit_id(self, x):
        return int(abs(int(x)) % self.dim)

    def same_orbit(self, a, b):
        return self.orbit_id(a) == self.orbit_id(b)

    def connection(self, a, b):
        return int(self.same_orbit(a, b))


class E8E8:
    def __init__(self):
        self.dim = 16
        self.generators = 248 + 248

    def cross(self, x):
        return int(abs(int(x)) % 2)

    def consistent(self, a, b):
        return int(self.cross(a) == self.cross(b))


class TripleShield:
    def __init__(self):
        self.conservation = D16Plus()
        self.symmetry = SO32()
        self.mirror = D16Plus()

    def destination(self, x, mu=32, bound=64):
        return int(x + (2 * mu - x))

    def path(self, a, b):
        return self.symmetry.connection(a, b)

    def geometry(self, x, mu=32, bound=64):
        return int(x + (2 * mu - x) == bound)

    def intersect(self, x, mu=32, bound=64):
        t = 2 * mu - x
        return {
            "conservation": int(x + t == bound),
            "symmetry": self.symmetry.connection(x, t),
            "mirror": int(t == bound - x),
        }


MU = 32
BOUND = 64
TAU_0 = 1.0

NODES = np.arange(-BOUND, BOUND + 1)
PARITY = np.abs(NODES) % 2
MIRROR_MAP = 2 * MU - NODES
DELTA_Q_MAP = NODES + MIRROR_MAP - BOUND

R_NODES = np.array([2 * i - 1 for i in range(1, 16)])
R_LABELS = np.array([f"R{i:02d}" for i in range(1, 16)])
R_LOOKUP = {int(n): str(l) for n, l in zip(R_NODES, R_LABELS)}

K_LABELS = np.array([f"K{i:02d}" for i in range(1, 8)])
K_PAIRS = np.array([
    [1, 63, 2],
    [8, 56, 9],
    [16, 48, 17],
    [24, 40, 25],
    [28, 36, 29],
    [30, 34, 31],
    [31, 33, 32],
])
K_LOOKUP = {str(l): p for l, p in zip(K_LABELS, K_PAIRS)}

R_TO_K = {1: "K01", 3: "K01", 5: "K02", 7: "K02", 9: "K02",
          11: "K03", 13: "K03", 15: "K03", 17: "K03",
          19: "K04", 21: "K04", 23: "K04",
          25: "K05", 27: "K06", 29: "K07"}


def mirror_T(x, mu=MU):
    return 2 * mu - np.asarray(x)


def fold_F(x):
    return np.zeros_like(np.asarray(x))


def parity(x):
    return np.abs(np.asarray(x, dtype=int)) % 2


def conservation_invariant(x, bound=BOUND):
    return np.asarray(x) + mirror_T(x) - bound


def in_bounds(x, bound=BOUND):
    return np.abs(np.asarray(x)) <= bound


def fib_time(n, tau=TAU_0):
    f = np.zeros(n + 2)
    f[0] = 1.0
    f[1] = 1.0
    for i in range(2, n + 2):
        f[i] = f[i - 1] + f[i - 2]
    return f[2:] * tau


def gold_ratio():
    return (1 + np.sqrt(5)) / 2
