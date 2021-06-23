"""
An omnidirectional hardware shifter that supports rotation.

>>> defaults = {"enabled": True, "left": True, "rotate": False, "data": 0x800FB009, "shift_amount": 4}
>>> test_cases = [
...     {},
...     {"enabled": False},
...     {"rotate": True},
...     {"left": False},
...     {"left": False, "rotate": True},
...     {"shift_amount": 28},
...     {"shift_amount": 30},
...     {"data": 0xaaaaaaaa, "shift_amount": 1},
... ]
>>> for test_case in test_cases:
...     result = shifter_software_spec(**{**defaults, **test_case})
...     print(f"{test_case}: {result:08x}")
{}: 00fb0090
{'enabled': False}: 800fb009
{'rotate': True}: 00fb0098
{'left': False}: 0800fb00
{'left': False, 'rotate': True}: 9800fb00
{'shift_amount': 28}: 90000000
{'shift_amount': 30}: 40000000
{'data': 2863311530, 'shift_amount': 1}: 55555554
"""
from functools import partial

from cocotb import test
from cocotb.triggers import Timer
from hypothesis import strategies as st

from test_module import assert_hardware_matches_software, run_module_tests


def shifter_input_types(bit_width: int = 32):
    return {
        "enabled": st.booleans(),
        "left": st.booleans(),
        "rotate": st.booleans(),
        "data": st.integers(0, 1 << bit_width - 1),
        "shift_amount": st.integers(0, bit_width - 1),
    }


def rotated(left: bool, shift_amount: int, data: int, bit_width: int = 32):
    "Rotate a bitvector a given amount."
    if left:
        left_rot_amount = shift_amount
    else:
        left_rot_amount = bit_width - shift_amount

    # Contains crap data above 32b boundary.
    rotated_result = (data << left_rot_amount) | (data >> (bit_width - left_rot_amount))

    # Mask away crap data in upper bytes.
    return rotated_result & word_mask(bit_width)


def word_mask(bit_width: int = 32) -> int:
    return (1 << bit_width) - 1


def shift_mask(rotate, left, shift_amount, bit_width: int = 32):
    "A shifter's output mask. Generates masks from left/right, depending on args."
    full_mask = word_mask(bit_width)
    if rotate:
        return full_mask

    if left:
        return (full_mask << shift_amount) & full_mask
    else:
        return full_mask >> shift_amount


def shifter_software_spec(
    enabled: bool,
    rotate: bool,
    left: bool,
    shift_amount: int,
    data: int,
    bit_width: int = 32,
):
    "Perform a rotation, then mask the results according to flags."
    if not enabled:
        return data

    rotated_result = rotated(left, shift_amount, data, bit_width)

    return rotated_result & shift_mask(rotate, left, shift_amount, bit_width)


async def shifter_hardware_result(
    dut,
    enabled: bool,
    rotate: bool,
    left: bool,
    data: int,
    shift_amount: int,
    bit_width: int = 32,
):
    assert 0 <= shift_amount < bit_width

    dut.En <= int(enabled)
    dut.RotateEnable <= int(rotate)
    dut.Left <= int(left)
    dut.dIN <= data
    dut.ShAmount <= shift_amount

    await Timer(1, units="ns")

    return dut.dOUT


@test()
async def grace_shifter_fuzzing_test(dut):
    """
    Verify shifter works exactly as spec'd above.
    """
    await assert_hardware_matches_software(
        shifter_software_spec,
        partial(shifter_hardware_result, dut),
        input_types=shifter_input_types(),
    )


# Pytest invocation.
def test_grace_shifter():
    run_module_tests("grace_shifter")
