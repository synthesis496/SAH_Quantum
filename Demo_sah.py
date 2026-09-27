# Copyright (c) 2026 <Your Name>
# SPDX-License-Identifier: Apache-2.0

MU = 32
CODESPACE = 0
STATE_MIN = -64
STATE_MAX = 64
GAMMA = 0.5
TAU0 = 1.0
FIBONACCI = (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233)

_SIG = "so32-d16-plus-qec-2026"
_SIG_HASH = 1694

reflect = lambda x: 2 * MU - x
fold = lambda x: (x, CODESPACE)[abs(x) == STATE_MAX]
parity = lambda x: abs(x) & 1
valid = lambda x: STATE_MIN <= x <= STATE_MAX
conserved = lambda x: x + reflect(x) == 2 * MU
integrity = lambda: sum(ord(c) for c in _SIG) == _SIG_HASH

_CATEGORIES = (
    (lambda x: x == CODESPACE, "codespace"),
    (lambda x: abs(x) == STATE_MAX, "boundary"),
    (lambda x: parity(x) == 1, "r_sector"),
    (lambda x: valid(x), "structural"),
)


def _category(x):
    matched = tuple(name for cond, name in _CATEGORIES if cond(x))
    return (matched + ("out_of_bounds",))[0]


def detect(x):
    return {
        "state": x,
        "category": _category(x),
        "parity": parity(x),
        "mirror_valid": valid(reflect(x)),
        "conserved": conserved(x),
        "detected": _category(x) != "codespace",
    }


def path_length(x):
    ax = abs(x)
    upper = x > MU
    pos_len = (x, 65 - x)[upper]
    nonzero = (pos_len, ax)[x <= 0]
    boundary = ax == STATE_MAX
    non_boundary_len = (nonzero, 1)[boundary]
    return (non_boundary_len, 0)[x == CODESPACE]


def _step(x):
    succ = (
        (x == CODESPACE, lambda: ()),
        (abs(x) == STATE_MAX, lambda: (CODESPACE,)),
        (x == MU, lambda: (MU - 1,)),
        (x == -MU, lambda: (-MU + 1,)),
        (0 < x < STATE_MAX and abs(2 * MU - x) < x, lambda: (2 * MU - x,)),
        (0 < x < STATE_MAX, lambda: (x - 1,)),
        (-STATE_MAX < x < 0, lambda: (x + 1,)),
    )
    match = tuple(fn for cond, fn in succ if cond)
    return (match + (lambda: (),))[0]()


def _walk(path, budget):
    last = path[-1]
    done = (last == CODESPACE) or (budget <= 0)
    return (path, _walk(path + _step(last)[:1], budget - 1))[not done]


def walk(x, max_steps=128):
    return _walk((x,), max_steps)


heal = lambda x: walk(x)[-1]

is_tick = lambda t: any(abs(t - f * TAU0) < 1e-9 for f in FIBONACCI)
l_heal = lambda t: GAMMA * (0.0, 1.0)[is_tick(t)]
