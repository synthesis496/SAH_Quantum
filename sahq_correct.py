#Copyright (c) 2026.Chutiphong Bunloed
#All Rights Reserved.

import numpy as np
import sahq_core

class Corrector:
    def __init__(self):
        self.core = sahq_core

    def path_for(self, x):
        return self.core.R_TO_K.get(int(x), "none")

    def pair_for(self, k):
        p = self.core.K_LOOKUP.get(k)
        return (0, 0) if p is None else (int(p[0]), int(p[1]))

    def max_steps(self, k):
        p = self.core.K_LOOKUP.get(k)
        return 0 if p is None else int(p[2])

    def heal_rate(self, k):
        s = self.max_steps(k)
        return 0.0 if s == 0 else 1.0 / s

    def decay_trajectory(self, x):
        n = abs(int(x))
        k = np.arange(n + 1)
        mag = np.maximum(n - k, 0)
        sgn = 1 - 2 * int(x < 0)
        return (sgn * mag).astype(int)

    def L_heal(self, x, t_fib, T):
        is_code = float(int(x) == 0)
        is_err = 1.0 - is_code
        P = is_code
        I_minus_P = is_err
        E_omni = is_err
        return float(T * t_fib * I_minus_P * E_omni)

    def pipeline(self, x, t_fib=1.0, T=1.0):
        k = self.path_for(x)
        traj = self.decay_trajectory(x)
        return {
            "x": int(x),
            "K": k,
            "pair": self.pair_for(k),
            "max_steps": self.max_steps(k),
            "heal_rate": self.heal_rate(k),
            "L_heal": self.L_heal(x, t_fib, T),
            "trajectory": traj.tolist(),
            "final": int(traj[-1]),
            "steps_used": int(np.abs(int(x))),
            "delta_q": int(self.core.conservation_invariant(x)),
        }

    def batch(self, xs, t_fib=1.0, T=1.0):
        return [self.pipeline(int(x), t_fib, T) for x in xs]

    def full_sweep(self, t_fib=1.0, T=1.0):
        return self.batch(self.core.R_NODES.tolist(), t_fib, T)

    def coverage(self):
        detect = len(self.core.R_NODES)
        correct = len(self.core.K_LABELS)
        return {
            "detect": detect,
            "correct": correct,
            "total": detect + correct,
            "distance": detect + correct + 1,
        }
