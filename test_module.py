"""
Run cocotb tests like pytests.
"""
from os.path import join
from subprocess import run
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Tuple

from hypothesis import given
from lxml import etree


def any_test_failures(dir_path: str) -> bool:
    results = etree.parse(join(dir_path, "results.xml"))
    return bool(results.findall(".testsuite//failure"))


makefile_template = """
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/{module_name}.sv
TOPLEVEL = {module_name}
MODULE = test_{module_name}
export LIBPYTHON_LOC = /usr/lib/libpython3.9.so

include $(shell cocotb-config --makefiles)/Makefile.sim
"""


def run_module_tests(module_name, module_prefix=None):
    with TemporaryDirectory() as temp_dir:
        with open(join(temp_dir, "Makefile"), "w") as f:
            f.write(makefile_template.format(module_name=module_name))

        if module_prefix is not None and module_prefix != "":
            cwd_cmd = "cd " + module_prefix + ";"
        else:
            cwd_cmd = ""
        run(
            f"{cwd_cmd} cp {__file__} {module_name}.sv "
            + f"test_{module_name}.py {temp_dir}",
            shell=True,
            check=True,
        )
        run(f"make -C {temp_dir}", shell=True, check=True)

        failures = any_test_failures(temp_dir)
        if failures:
            run(
                f"cp {temp_dir}/results.xml /tmp/failed_results.xml",
                shell=True,
                check=True,
            )
            raise ValueError("Test failed.")


def random_testcases(input_types: Dict[str, Any]) -> List[Tuple[Any, Any]]:
    testcases = []

    @given(**input_types)
    def record_testcases(*args, **kwargs):
        testcases.append((args, kwargs))

    record_testcases()

    return testcases


async def assert_hardware_matches_software(
    software_func,
    hardware_func,
    input_types,
):
    for args, kwargs in random_testcases(input_types):
        expected_result = software_func(*args, **kwargs)
        actual_result = await hardware_func(*args, **kwargs)
        assert (
            expected_result == actual_result
        ), f"Software and hardware differ when args={args}, kwargs={kwargs}"
