#Copyright (c) 2026.Chutiphong Bunloed
#All Rights Reserved.

import numpy as np
import sahq_core

class Detector:
    def __init__(self):
        self.core = sahq_core

    def boundary_check(self, x):
        return int(not self.core.in_bounds(x))

    def parity_check(self, x):
        return int(self.core.parity(x) == 1)

    def mirror_check(self, x):
        t = self.core.mirror_T(x)
        return int(self.core.in_bounds(t))

    def conservation_check(self, x):
        return int(self.core.conservation_invariant(x) == 0)

    def classify(self, x):
        checks = np.array([
            self.boundary_check(x),
            self.parity_check(x),
            self.mirror_check(x),
            self.conservation_check(x),
        ])
        names = np.array(["boundary", "parity", "mirror", "conservation"])
        mask = checks.astype(bool)
        return names[mask].tolist()

    def map_to_R(self, x):
        return self.core.R_LOOKUP.get(int(x), "codespace")

    def pipeline(self, x):
        return {
            "x": int(x),
            "checks": self.classify(x),
            "R": self.map_to_R(x),
            "parity": int(self.core.parity(x)),
            "mirror_T": int(self.core.mirror_T(x)),
            "delta_q": int(self.core.conservation_invariant(x)),
        }

    def batch(self, xs):
        return [self.pipeline(int(x)) for x in xs]

    def full_sweep(self):
        return self.batch(self.core.R_NODES.tolist())

    def all_nodes(self):
        return self.batch(self.core.NODES.tolist())

    def detect_only_R(self):
        xs = self.core.R_NODES.astype(int).tolist()
        return np.array([self.map_to_R(x) for x in xs])

    def count_detected(self):
        return int(np.sum(self.detect_only_R() != "codespace"))

    def count_R_types(self):
        return len(self.core.R_NODES)
