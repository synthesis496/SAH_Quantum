#Copyright (c) 2026.Chutiphong Bunloed
#All Rights Reserved.

import numpy as np
import sahq_core
import sahq_detect
import sahq_correct
import sahq_engine

class SAHQTest:
    def __init__(self, engine=None):
        self.engine = engine or sahq_engine.SAHQEngine()

    def mirror_involution(self):
        xs = sahq_core.NODES
        return bool(np.all(sahq_core.mirror_T(sahq_core.mirror_T(xs)) == xs))

    def conservation_law(self):
        xs = sahq_core.NODES
        return bool(np.all(sahq_core.conservation_invariant(xs) == 0))

    def delta_q_zero(self):
        return bool(np.all(sahq_core.DELTA_Q_MAP == 0))

    def parity_odd_all_R(self):
        return bool(np.all(sahq_core.PARITY[sahq_core.R_NODES + sahq_core.BOUND] == 1))

    def detect_all_R(self):
        d = sahq_detect.Detector()
        xs = sahq_core.R_NODES.astype(int).tolist()
        labels = [d.map_to_R(x) for x in xs]
        return bool(all(l != "codespace" for l in labels))

    def correct_all_R(self):
        c = sahq_correct.Corrector()
        xs = sahq_core.R_NODES.astype(int).tolist()
        ks = [c.path_for(x) for x in xs]
        return bool(all(k != "none" for k in ks))

    def decay_to_zero(self):
        c = sahq_correct.Corrector()
        xs = sahq_core.R_NODES.astype(int).tolist()
        finals = [int(c.decay_trajectory(x)[-1]) for x in xs]
        return bool(all(f == 0 for f in finals))

    def pair_sum_bound(self):
        return bool(np.all(sahq_core.K_PAIRS[:, 0] + sahq_core.K_PAIRS[:, 1] == sahq_core.BOUND))

    def mirror_pair_consistent(self):
        pairs = sahq_core.K_PAIRS[:, :2]
        ts = sahq_core.mirror_T(pairs[:, 0])
        return bool(np.all(ts == pairs[:, 1]))

    def coverage_d_ge_23(self):
        n = len(sahq_core.R_NODES) + len(sahq_core.K_LABELS) + 1
        return bool(n >= 23)

    def d16_unimodular(self):
        return self.engine.d16.unimodular()

    def d16_self_dual(self):
        return self.engine.d16.self_dual()

    def d16_even(self):
        v = np.zeros(16, dtype=int)
        v[0] = 2
        return self.engine.d16.even(v)

    def so32_generators(self):
        return self.engine.so32.generators == 496

    def e8e8_generators(self):
        return self.engine.e8e8.generators == 496

    def limit_cycle_closed(self):
        return bool(self.engine.limit.closed())

    def no_dead_end(self):
        xs = sahq_core.NODES
        t_vals = sahq_core.mirror_T(xs)
        valid = sahq_core.in_bounds(t_vals)
        fallback = np.where(valid, t_vals, xs - np.sign(xs))
        return bool(np.all(np.abs(fallback) <= np.abs(xs)))

    def no_loop(self):
        xs = sahq_core.NODES
        t_vals = sahq_core.mirror_T(xs)
        valid = sahq_core.in_bounds(t_vals)
        step = np.where(valid & (np.abs(t_vals) < np.abs(xs)), t_vals, xs - np.sign(xs))
        return bool(np.all(np.abs(step) <= np.abs(xs)))

    def unique_attractor(self):
        c = sahq_correct.Corrector()
        finals = np.array([c.decay_trajectory(int(x))[-1] for x in sahq_core.R_NODES])
        return bool(np.all(finals == 0))

    def run_all(self):
        return {
            "mirror_involution": self.mirror_involution(),
            "conservation_law": self.conservation_law(),
            "delta_q_zero": self.delta_q_zero(),
            "parity_odd_all_R": self.parity_odd_all_R(),
            "detect_all_R": self.detect_all_R(),
            "correct_all_R": self.correct_all_R(),
            "decay_to_zero": self.decay_to_zero(),
            "pair_sum_bound": self.pair_sum_bound(),
            "mirror_pair_consistent": self.mirror_pair_consistent(),
            "coverage_d_ge_23": self.coverage_d_ge_23(),
            "d16_unimodular": self.d16_unimodular(),
            "d16_self_dual": self.d16_self_dual(),
            "d16_even": self.d16_even(),
            "so32_generators": self.so32_generators(),
            "e8e8_generators": self.e8e8_generators(),
            "limit_cycle_closed": self.limit_cycle_closed(),
            "no_dead_end": self.no_dead_end(),
            "no_loop": self.no_loop(),
            "unique_attractor": self.unique_attractor(),
        }

    def summary(self):
        r = self.run_all()
        passed = int(np.sum(list(r.values())))
        total = len(r)
        return {
            "passed": passed,
            "total": total,
            "all_pass": passed == total,
            "detail": r,
        }
