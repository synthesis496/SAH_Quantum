#Copyright (c) 2026.Chutiphong Bunloed
#All Rights Reserved.

import numpy as np
import sahq_core
import sahq_detect
import sahq_correct

class FibonacciClock:
    def __init__(self, tau=sahq_core.TAU_0):
        self.tau = tau

    def ticks(self, n):
        return sahq_core.fib_time(n, self.tau)

    def gate_open(self, tick_values):
        return np.asarray(tick_values) > 0


class LimitCycle:
    def __init__(self, a=-0.1, beta=1.0, z0=0.5 + 0.5j):
        self.a = a
        self.beta = beta
        self.z0 = z0

    def T(self, z):
        return np.exp((self.a + 1j * self.beta) * np.asarray(z))

    def iterate(self, n):
        z = self.z0
        out = np.zeros(n, dtype=complex)
        for i in range(n):
            z = self.T(z)
            out[i] = z
        return out

    def closed(self, n=200, tol=1e-3):
        t = self.iterate(n)
        return int(abs(t[-1] - t[-2]) < tol)

    def radius(self, n=200):
        t = self.iterate(n)
        return float(np.abs(t[-50:]).mean())


class SAHQEngine:
    def __init__(self, mu=sahq_core.MU, bound=sahq_core.BOUND,
                 tau=sahq_core.TAU_0, T=1.0, a=-0.1, beta=1.0):
        self.mu = mu
        self.bound = bound
        self.T = T
        self.clock = FibonacciClock(tau)
        self.limit = LimitCycle(a, beta)
        self.detector = sahq_detect.Detector()
        self.corrector = sahq_correct.Corrector()
        self.d16 = sahq_core.D16Plus()
        self.so32 = sahq_core.SO32()
        self.e8e8 = sahq_core.E8E8()
        self.shield = sahq_core.TripleShield()

    def tick(self, x, tick_idx, t_fib):
        return {
            "tick": int(tick_idx),
            "t_fib": float(t_fib),
            "detection": self.detector.pipeline(x),
            "correction": self.corrector.pipeline(x, t_fib, self.T),
        }

    def run(self, x0, n_ticks):
        ticks = self.clock.ticks(n_ticks)
        return [self.tick(x0, i, ticks[i]) for i in range(n_ticks)]

    def run_R_sweep(self, n_ticks):
        ticks = self.clock.ticks(n_ticks)
        return [self.tick(int(x), i, ticks[i]) for i, x in enumerate(sahq_core.R_NODES)]

    def summary(self, x0, n_ticks=10):
        ticks = self.clock.ticks(n_ticks)
        traj = self.corrector.decay_trajectory(x0)
        k = self.corrector.path_for(x0)
        return {
            "x0": int(x0),
            "n_ticks": int(n_ticks),
            "fib_ticks": ticks.tolist(),
            "R": self.detector.map_to_R(x0),
            "K": k,
            "pair": self.corrector.pair_for(k),
            "max_steps": self.corrector.max_steps(k),
            "decay_len": int(len(traj)),
            "final": int(traj[-1]),
            "delta_q": int(sahq_core.conservation_invariant(x0)),
            "limit_closed": self.limit.closed(),
        }

    def verify(self):
        return {
            "d16_unimodular": self.d16.unimodular(),
            "d16_self_dual": self.d16.self_dual(),
            "d16_det": self.d16.det,
            "so32_generators": self.so32.generators,
            "e8e8_generators": self.e8e8.generators,
            "detect_count": len(sahq_core.R_NODES),
            "correct_count": len(sahq_core.K_LABELS),
            "distance": len(sahq_core.R_NODES) + len(sahq_core.K_LABELS) + 1,
            "limit_closed": self.limit.closed(),
            "limit_radius": self.limit.radius(),
            "mirror_involution": bool(np.all(sahq_core.mirror_T(sahq_core.mirror_T(sahq_core.NODES)) == sahq_core.NODES)),
            "conservation_all": bool(np.all(sahq_core.DELTA_Q_MAP == 0)),
            "pair_sum_bound": bool(np.all(sahq_core.K_PAIRS[:, 0] + sahq_core.K_PAIRS[:, 1] == sahq_core.BOUND)),
        }

    def transition_table(self):
        xs = np.array([-64, -32, -16, -1, 0, 1, 16, 32, 48, 63, 64])
        t_vals = sahq_core.mirror_T(xs)
        valid = sahq_core.in_bounds(t_vals).astype(int)
        returns = np.array([int(x) for x in xs])
        return {
            "x": returns.tolist(),
            "T_x": t_vals.astype(int).tolist(),
            "valid": valid.tolist(),
        }
