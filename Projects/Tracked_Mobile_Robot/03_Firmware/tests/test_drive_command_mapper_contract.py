"""Independent executable vectors for the production open-loop mapper contract.

This standard-library reference model does not execute the C implementation.
The static source-contract test in test_firmware_contract.py separately binds
the C constants, validation order and coupled-saturation formula to this design.
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass


NORMALIZED_SCALE = 1000
VX_MIN_MMPS = -100
VX_MAX_MMPS = 100
W_MIN_MRADPS = -500
W_MAX_MRADPS = 500
MAX_DUTY_PERMILLE = 100


@dataclass
class DriveCommandRequest:
    left_signed_permille: int = 0
    right_signed_permille: int = 0


def trunc_toward_zero(numerator: int, denominator: int) -> int:
    """Match C signed-integer division without using float arithmetic."""
    quotient = abs(numerator) // abs(denominator)
    return -quotient if (numerator < 0) != (denominator < 0) else quotient


def map_reference(
    vx_mmps: int,
    w_mradps: int,
    duty_cap_permille: int,
    request: DriveCommandRequest | None,
) -> bool:
    if request is None:
        return False

    request.left_signed_permille = 0
    request.right_signed_permille = 0

    if not (
        VX_MIN_MMPS <= vx_mmps <= VX_MAX_MMPS
        and W_MIN_MRADPS <= w_mradps <= W_MAX_MRADPS
        and 0 <= duty_cap_permille <= MAX_DUTY_PERMILLE
    ):
        return False

    linear = trunc_toward_zero(vx_mmps * NORMALIZED_SCALE, VX_MAX_MMPS)
    yaw = trunc_toward_zero(w_mradps * NORMALIZED_SCALE, W_MAX_MRADPS)
    raw_left = linear - yaw
    raw_right = linear + yaw
    peak = max(NORMALIZED_SCALE, abs(raw_left), abs(raw_right))

    request.left_signed_permille = trunc_toward_zero(
        raw_left * duty_cap_permille,
        peak,
    )
    request.right_signed_permille = trunc_toward_zero(
        raw_right * duty_cap_permille,
        peak,
    )
    return True


class DriveCommandMapperContractTest(unittest.TestCase):
    def test_valid_fixed_and_boundary_vectors(self) -> None:
        vectors = (
            ((0, 0, 100), (0, 0)),
            ((100, 0, 100), (100, 100)),
            ((-100, 0, 100), (-100, -100)),
            ((50, 0, 100), (50, 50)),
            ((0, 500, 100), (-100, 100)),
            ((0, -500, 100), (100, -100)),
            ((0, 250, 100), (-50, 50)),
            ((100, 250, 100), (33, 100)),
            ((-100, 250, 100), (-100, -33)),
            ((100, 500, 100), (0, 100)),
            ((100, 0, 50), (50, 50)),
            ((100, 500, 0), (0, 0)),
        )

        for inputs, expected in vectors:
            with self.subTest(inputs=inputs):
                request = DriveCommandRequest(77, -88)
                self.assertTrue(map_reference(*inputs, request))
                self.assertEqual(
                    (request.left_signed_permille, request.right_signed_permille),
                    expected,
                )

    def test_invalid_inputs_zero_output_and_null_is_rejected(self) -> None:
        invalid_vectors = (
            (101, 0, 100),
            (-101, 0, 100),
            (0, 501, 100),
            (0, -501, 100),
            (0, 0, 101),
        )

        for inputs in invalid_vectors:
            with self.subTest(inputs=inputs):
                request = DriveCommandRequest(77, -88)
                self.assertFalse(map_reference(*inputs, request))
                self.assertEqual(
                    (request.left_signed_permille, request.right_signed_permille),
                    (0, 0),
                )

        self.assertFalse(map_reference(0, 0, 100, None))


if __name__ == "__main__":
    unittest.main()
