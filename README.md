# SAHQ: Symmetry-Autonomous Healing Quantum Suite (Type B)

A Python simulation framework for exploring a deterministic state-detection and state-decay model using parity, mirror mappings, Fibonacci-derived ticks, and fixed syndrome-to-path mappings.

**Author:** Chutiphong Bunloed  
**ORCID:** [0009-0003-4295-7521](https://orcid.org/0009-0003-4295-7521)  
**Citation DOI:** [10.5281/zenodo.23443406](https://doi.org/10.5281/zenodo.23443406)

> [!NOTE]
> This repository contains a numerical simulation. The current source does not connect to quantum hardware or invoke Qiskit or Cirq.

## Contents

- [What the code does](#what-the-code-does)
- [Repository structure](#repository-structure)
- [Model and defaults](#model-and-defaults)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [API overview](#api-overview)
- [Verification](#verification)
- [Benchmarks](#benchmarks)
- [Configuration](#configuration)
- [Citation](#citation)
- [License](#license)

## What the code does

The implementation is organized into six Python modules:

1. `sahq_core.py` defines constants, arrays, R/K mappings, mirror and conservation functions, Fibonacci-time values, and numerical descriptor classes.
2. `sahq_detect.py` provides boundary, parity, mirror, and conservation checks and maps configured positive odd values to R labels.
3. `sahq_correct.py` maps configured R values to K paths and constructs a deterministic integer trajectory from an input value to zero.
4. `sahq_engine.py` combines detection and correction with a Fibonacci clock and a numerical limit-cycle calculation.
5. `sahq_test.py` implements 19 boolean verification checks.
6. `sahq_product.py` exposes the `SAHQ` wrapper, configuration, benchmark methods, report methods, and a demo.

`SAHQ.run(x0, n_ticks)` generates Fibonacci tick values and returns a list of detection/correction results for the same `x0` at each tick. It does not update the state between ticks. The decay trajectory is separately calculated by `Corrector`.

## Repository structure

```text
SAH_Quantum/
├── sahq_core.py       # Constants, mappings, model helpers, and descriptors
├── sahq_detect.py     # Detection checks and R-label lookup
├── sahq_correct.py    # K-path lookup and deterministic decay trajectories
├── sahq_engine.py     # Clock, limit cycle, and engine orchestration
├── sahq_test.py       # Internal verification checks
├── sahq_product.py    # High-level API, configuration, demo, and benchmarks
├── README.md          # Project documentation
├── index.md           # Additional project documentation
├── CITATION.cff       # Citation metadata
└── LICENSE            # License text
```

## Model and defaults

The defaults in `sahq_core.py` are:

| Name | Default | Description in code |
|---|---:|---|
| `MU` | `32` | Center parameter for the mirror function |
| `BOUND` | `64` | Bound used by `in_bounds` and conservation calculations |
| `TAU_0` | `1.0` | Default Fibonacci-time scale |
| `NODES` | `-64` to `64` | Integer node array, inclusive |

### Mirror and conservation

The implemented transformation is `mirror_T(x) = 2 * mu - x`. With the default `mu=32`, this is `64 - x`. The conservation function returns `x + mirror_T(x) - bound`; with the default constants its value is zero.

`in_bounds(x)` checks `abs(x) <= bound`. `parity(x)` returns the absolute integer parity (`0` for even and `1` for odd).

### R nodes and K paths

`R_NODES` contains the 15 positive odd integers from `1` through `29`, with labels `R01` through `R15`. `R_LOOKUP` maps these exact integer values to labels; other values map to the string `"codespace"` in `Detector.map_to_R()`.

`K_LABELS` contains `K01` through `K07`. Each row of `K_PAIRS` stores two values and a step count:

```text
K01: (1, 63), 2 steps
K02: (8, 56), 9 steps
K03: (16, 48), 17 steps
K04: (24, 40), 25 steps
K05: (28, 36), 29 steps
K06: (30, 34), 31 steps
K07: (31, 33), 32 steps
```

`R_TO_K` is a fixed lookup from supported positive R-node values to K labels. It is not calculated dynamically.

### Correction trajectory

`Corrector.decay_trajectory(x)` returns signed integer values whose magnitude decreases by one per element until zero. For example, the result for `15` is `[15, 14, ..., 0]`; for `-3` it is `[-3, -2, -1, 0]`. This trajectory is generated from `x` and is independent of the selected K path.

### Other numerical components

- `fib_time(n, tau)` builds Fibonacci values starting from `1, 1` and scales the returned values by `tau`.
- `LimitCycle.T(z)` computes `exp((a + 1j * beta) * z)`. Its `closed()` method compares the last two values after a default of 200 iterations against a tolerance of `1e-3`.
- `D16Plus`, `SO32`, `E8E8`, and `TripleShield` expose the calculations and descriptors implemented in `sahq_core.py`. These classes do not implement a quantum backend or a complete Lie-algebra simulation.

## Requirements

- Python 3
- NumPy

Qiskit and Cirq are mentioned in the additional documentation (`index.md`) but are not imported by the current Python modules. There is no `requirements.txt`, `pyproject.toml`, or package installer configuration in the repository.

## Installation

Clone the repository and install NumPy:

```bash
git clone https://github.com/synthesis496/SAH_Quantum.git
cd SAH_Quantum
python -m venv .venv
```

Activate the virtual environment and install the dependency:

```bash
# macOS/Linux
source .venv/bin/activate
pip install numpy
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install numpy
```

## Quick start

Run from the repository root so the local modules can be imported.

```python
from sahq_product import SAHQ

sahq = SAHQ()

# Run the internal checks
verification = sahq.verify_summary()
print(verification["passed"], "/", verification["total"])
print("All passed:", verification["all_pass"])

# Inspect one state
result = sahq.summary(x0=15, n_ticks=16)
print(result)
```

To run the demo script:

```bash
python sahq_product.py
```

The module calls `demo()` and creates module-level `demo_result`, `sahq`, and `report` values when executed or imported.

## API overview

The high-level entry point is `SAHQ` in `sahq_product.py`.

| Method | Behavior |
|---|---|
| `verify()` | Returns the individual verification results as a dictionary. |
| `verify_summary()` | Returns passed count, total count, overall boolean, and details. |
| `run(x0, n_ticks=10)` | Returns one engine tick result per generated Fibonacci tick, using the same input state each time. |
| `summary(x0, n_ticks=10)` | Returns a summary including Fibonacci ticks, R/K lookups, decay length/final value, conservation value, and limit-cycle status. |
| `sweep(n_ticks=15)` | Calls the engine sweep over `R_NODES`. The current engine uses the first `n_ticks` Fibonacci values and enumerates the R-node array. |
| `transition()` | Returns the mirror values and in-bound flags for a fixed list of sample inputs. |
| `coverage()` | Returns counts for R nodes, K labels, their sum, and the derived distance value. |
| `bench(n_iter=100)` | Runs the benchmark methods and returns their results. |
| `report(x0=5, n_ticks=10, n_iter=100)` | Combines configuration, verification summary, state summary, coverage, and benchmark output. |

The lower-level classes can also be used directly:

```python
from sahq_detect import Detector
from sahq_correct import Corrector

print(Detector().pipeline(15))
print(Corrector().pipeline(15))
```

`Detector.pipeline()` reports the input, triggered check names, R lookup, parity, mirror value, and conservation value. `Corrector.pipeline()` reports the path lookup, pair, maximum steps, healing rate, `L_heal`, trajectory, final value, steps used, and conservation value.

## Verification

`SAHQTest.run_all()` returns 19 boolean checks covering mirror involution, conservation, R-node parity and lookup, correction mapping, decay, K-pair relationships, coverage, D16+ properties, generator counts, limit-cycle closure, and trajectory conditions.

Run the suite directly:

```python
from sahq_test import SAHQTest

result = SAHQTest().summary()
print(result)
```

These checks validate the implemented calculations; they should not be read as proof of physical error-correction performance.

## Benchmarks

`SAHQBenchmark` in `sahq_product.py` provides detection, correction, sweep, tick-latency, coverage, and decay-cost measurements. For example:

```python
from sahq_product import SAHQ

benchmark = SAHQ().bench(n_iter=100)
print(benchmark)
```

Measurements depend on the machine and runtime environment. The repository does not include published benchmark fixtures or a benchmark test runner.

## Configuration

`SAHQConfig` defaults are `mu=32`, `bound=64`, `tau=1.0`, `T=1.0`, `a=-0.1`, and `beta=1.0`.

```python
from sahq_product import SAHQ, SAHQConfig

config = SAHQConfig()
config.update(mu=32, bound=64, tau=1.0, T=1.0, a=-0.1, beta=1.0)

sahq = SAHQ(config)
```

`SAHQ` constructs its engine during initialization. Updating the config after constructing `SAHQ` does not automatically reconstruct that engine; create a new `SAHQ(config)` to pass updated values into a new engine. The current engine also retains references to the core module's fixed arrays and mappings; changing `mu` or `bound` does not regenerate those module-level data structures.

## Citation

The repository includes [`CITATION.cff`](CITATION.cff). If you use this software, cite it using that metadata. The listed DOI is [10.5281/zenodo.23443406](https://doi.org/10.5281/zenodo.23443406).

## License

See [`LICENSE`](LICENSE) for the applicable license terms.
