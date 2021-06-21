from cocotb import test
from cocotb.triggers import Timer

from test_module import test_module

@test()
async def grace_shifter_test_one(dut):
    """
    Verify shifter works as expected.

    TODO:
    - Mess with timing, understand propagation speed better.
    - Switch to brute-force verification.
    """
    dut.En <= 1
    dut.Left <= 1
    dut.RotateEnable <= 1
    dut.dIN <= 0xAAAAAAAA
    dut.ShAmount <= 1

    await Timer(1, units="ns")
    assert dut.dOUT == 0x55555555

def test_gracefu_shifter():
    test_module("grace_shifter")
