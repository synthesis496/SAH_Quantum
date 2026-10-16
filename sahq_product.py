#Copyright (c) 2026.Chutiphong Bunloed
#All Rights Reserved.

import time
import numpy as np
import sahq_core
import sahq_detect
import sahq_correct
import sahq_engine
import sahq_test


class SAHQConfig:
    def __init__(self):
        self.mu = sahq_core.MU
        self.bound = sahq_core.BOUND
        self.tau = sahq_core.TAU_0
        self.T = 1.0
        self.a = -0.1
        self.beta = 1.0

    def to_dict(self):
        return {
            "mu": self.mu,
            "bound": self.bound,
            "tau": self.tau,
            "T": self.T,
            "a": self.a,
            "beta": self.beta,
        }

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self.to_dict()


class SAHQBenchmark:
    def __init__(self, engine):
        self.engine = engine

    def _throughput(self, fn, n_iter):
        t0 = time.perf_counter()
        count = 0
        for _ in range(n_iter):
            count += fn()
        dt = time.perf_counter() - t0
        return {"ops": count, "seconds": dt, "rate": count / dt if dt > 0 else 0.0}

    def detection(self, n_iter=1000):
        d = self.engine.detector
        xs = sahq_core.R_NODES.astype(int).tolist()

        def loop():
            for x in xs:
                d.pipeline(x)
            return len(xs)

        return self._throughput(loop, n_iter)

    def correction(self, n_iter=1000):
        c = self.engine.corrector
        xs = sahq_core.R_NODES.astype(int).tolist()

        def loop():
            for x in xs:
                c.pipeline(x)
            return len(xs)

        return self._throughput(loop, n_iter)

    def full_sweep(self, n_iter=100):
        def loop():
            self.engine.run_R_sweep(15)
            return 15

        return self._throughput(loop, n_iter)

    def tick_latency(self, n_iter=1000):
        t0 = time.perf_counter()
        for _ in range(n_iter):
            self.engine.run(5, 15)
        dt = time.perf_counter() - t0
        return {"runs": n_iter, "ticks_per_run": 15,
                "seconds": dt, "latency_per_tick": dt / (n_iter * 15)}

    def coverage(self):
        c = self.engine.corrector
        return c.coverage()

    def decay_cost(self):
        steps = sahq_core.K_PAIRS[:, 2].astype(int)
        return {
            "min": int(steps.min()),
            "max": int(steps.max()),
            "sum": int(steps.sum()),
            "mean": float(steps.mean()),
        }

    def report(self, n_iter=100):
        return {
            "detection": self.detection(n_iter),
            "correction": self.correction(n_iter),
            "sweep": self.full_sweep(n_iter),
            "tick": self.tick_latency(n_iter),
            "coverage": self.coverage(),
            "decay": self.decay_cost(),
        }


class SAHQ:
    def __init__(self, config=None):
        self.config = config or SAHQConfig()
        self.engine = sahq_engine.SAHQEngine(
            mu=self.config.mu,
            bound=self.config.bound,
            tau=self.config.tau,
            T=self.config.T,
            a=self.config.a,
            beta=self.config.beta,
        )
        self.benchmark = SAHQBenchmark(self.engine)
        self.tester = sahq_test.SAHQTest(self.engine)

    def verify(self):
        return self.tester.run_all()

    def verify_summary(self):
        return self.tester.summary()

    def run(self, x0, n_ticks=10):
        return self.engine.run(x0, n_ticks)

    def summary(self, x0, n_ticks=10):
        return self.engine.summary(x0, n_ticks)

    def sweep(self, n_ticks=15):
        return self.engine.run_R_sweep(n_ticks)

    def transition(self):
        return self.engine.transition_table()

    def bench(self, n_iter=100):
        return self.benchmark.report(n_iter)

    def coverage(self):
        return self.engine.corrector.coverage()

    def report(self, x0=5, n_ticks=10, n_iter=100):
        return {
            "config": self.config.to_dict(),
            "verify": self.verify_summary(),
            "summary": self.summary(x0, n_ticks),
            "coverage": self.coverage(),
            "benchmark": self.bench(n_iter),
        }


def demo():
    sahq = SAHQ()
    return {
        "verify": sahq.verify_summary(),
        "case_R03_at_5": sahq.summary(5, 6),
        "case_R08_at_15": sahq.summary(15, 16),
        "case_boundary_64": sahq.summary(64, 3),
        "case_negative_minus16": sahq.summary(-16, 18),
        "case_attractor_0": sahq.summary(0, 3),
        "case_axis_32": sahq.summary(32, 3),
        "coverage": sahq.coverage(),
        "transition": sahq.transition(),
    }


demo_result = demo()
sahq = SAHQ()
report = sahq.report(5, 10, 100)
