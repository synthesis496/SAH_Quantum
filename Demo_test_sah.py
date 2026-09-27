# Copyright (c) 2026 Chutiphong Bunloed
#All Rights Reserved.

import sys
from so32_demo import (
    reflect, fold, parity, valid, conserved, integrity,
    detect, path_length, walk, heal, is_tick, l_heal,
    MU, CODESPACE, STATE_MIN, STATE_MAX, GAMMA, FIBONACCI,
)


def test_mirror_involution():
    for x in range(STATE_MIN, STATE_MAX + 1):
        assert reflect(reflect(x)) == x


def test_conservation():
    for x in range(STATE_MIN, STATE_MAX + 1):
        assert x + reflect(x) == 2 * MU
        assert conserved(x)


def test_fold_boundary():
    assert fold(STATE_MIN) == CODESPACE
    assert fold(STATE_MAX) == CODESPACE


def test_fold_interior():
    for x in range(STATE_MIN + 1, STATE_MAX):
        assert fold(x) == x


def test_parity_codespace():
    assert parity(CODESPACE) == 0


def test_parity_odd():
    for x in (1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29):
        assert parity(x) == 1


def test_valid_range():
    assert valid(STATE_MIN)
    assert valid(STATE_MAX)
    assert not valid(STATE_MAX + 1)
    assert not valid(STATE_MIN - 1)


def test_integrity():
    assert integrity()


def test_codespace_not_detected():
    assert not detect(CODESPACE)["detected"]


def test_boundary_detected():
    assert detect(STATE_MAX)["detected"]
    assert detect(STATE_MIN)["detected"]
    assert detect(STATE_MAX)["category"] == "boundary"


def test_error_sector_parity():
    for x in (1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29):
        assert detect(x)["category"] == "r_sector"
        assert detect(x)["parity"] == 1


def test_structural_category():
    for x in (2, 4, 6, 16, 32, 48):
        assert detect(x)["category"] == "structural"


def test_out_of_bounds():
    for x in (-200, -100, -65, 65, 100, 200):
        assert detect(x)["category"] == "out_of_bounds"


def test_mirror_valid_flag():
    assert detect(16)["mirror_valid"]
    assert not detect(-32)["mirror_valid"]


def test_conserved_flag():
    for x in range(STATE_MIN, STATE_MAX + 1):
        assert detect(x)["conserved"]


def test_path_length_codespace():
    assert path_length(CODESPACE) == 0


def test_path_length_boundary():
    assert path_length(STATE_MAX) == 1
    assert path_length(STATE_MIN) == 1


def test_path_length_positive():
    assert path_length(1) == 1
    assert path_length(5) == 5
    assert path_length(16) == 16
    assert path_length(48) == 17


def test_path_length_negative():
    assert path_length(-1) == 1
    assert path_length(-5) == 5
    assert path_length(-16) == 16
    assert path_length(-32) == 32


def test_walk_reaches_codespace():
    for x in range(STATE_MIN, STATE_MAX + 1):
        assert walk(x)[-1] == CODESPACE


def test_walk_length_matches_analytic():
    for x in range(STATE_MIN, STATE_MAX + 1):
        assert len(walk(x)) - 1 == path_length(x)


def test_walk_monotone():
    for x in range(STATE_MIN, STATE_MAX + 1):
        path = walk(x)
        for i in range(len(path) - 1):
            assert abs(path[i + 1]) < abs(path[i])


def test_heal_returns_codespace():
    for x in range(STATE_MIN, STATE_MAX + 1):
        assert heal(x) == CODESPACE


def test_is_tick_on_fib():
    for f in FIBONACCI[:8]:
        assert is_tick(float(f) * 1.0)


def test_is_tick_off_fib():
    for t in (0.5, 1.5, 2.5, 6.5, 100.0):
        assert not is_tick(t)


def test_l_heal_on_tick():
    for f in FIBONACCI[1:7]:
        assert l_heal(float(f)) == GAMMA


def test_l_heal_off_tick():
    for t in (0.5, 1.5, 6.5, 100.0):
        assert l_heal(t) == 0.0


TESTS = (
    test_mirror_involution,
    test_conservation,
    test_fold_boundary,
    test_fold_interior,
    test_parity_codespace,
    test_parity_odd,
    test_valid_range,
    test_integrity,
    test_codespace_not_detected,
    test_boundary_detected,
    test_error_sector_parity,
    test_structural_category,
    test_out_of_bounds,
    test_mirror_valid_flag,
    test_conserved_flag,
    test_path_length_codespace,
    test_path_length_boundary,
    test_path_length_positive,
    test_path_length_negative,
    test_walk_reaches_codespace,
    test_walk_length_matches_analytic,
    test_walk_monotone,
    test_heal_returns_codespace,
    test_is_tick_on_fib,
    test_is_tick_off_fib,
    test_l_heal_on_tick,
    test_l_heal_off_tick,
)


def _run(fn):
    try:
        fn()
        return True, "PASS"
    except AssertionError as e:
        return False, f"FAIL: {e}"
    except Exception as e:
        return False, f"ERROR: {type(e).__name__}: {e}"


def main():
    print("=" * 64)
    print("  SO(32) D16+ Auto-Healing QEC — Public Test Suite")
    print("=" * 64)

    groups = (
        ("Symmetry Layer", TESTS[:8]),
        ("Detection Layer", TESTS[8:15]),
        ("Healing Layer", TESTS[15:23]),
        ("Timing Layer", TESTS[23:]),
    )
    for name, subset in groups:
        print(f"\n  [{name}]")
        for fn in subset:
            ok, _ = _run(fn)
            print(f"      [{'PASS' if ok else 'FAIL'}] {fn.__name__}")

    results = tuple(_run(fn) for fn in TESTS)
    passed = sum(1 for ok, _ in results if ok)
    failed = len(results) - passed

    print("\n" + "=" * 64)
    print(f"  RESULT: {passed}/{len(results)} PASSED   ({failed} FAILED)")
    print("=" * 64)
    print()
    print("  METRICS")
    print("  " + "-" * 60)
    print(f"      state range ......... [{STATE_MIN}, {STATE_MAX}]")
    print(f"      symmetry axis ....... {MU}")
    print(f"      codespace ........... {CODESPACE}")
    print(f"      healing rate (Γ) .... {GAMMA}")
    print(f"      fibonacci ticks ..... {FIBONACCI[:8]}")
    print("=" * 64)

    return (0, 1)[failed > 0]


if __name__ == "__main__":
    sys.exit(main())
