"""
Run cocotb tests like pytests.
"""
from lxml import etree
from os.path import join
from subprocess import run
from tempfile import TemporaryDirectory
import pytest

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

@pytest.mark.skip(reason="This is a test helper, not a test.")
def test_module(module_name, module_prefix=None):
    with TemporaryDirectory() as temp_dir:
        with open(join(temp_dir, "Makefile"), "w") as f:
            f.write(makefile_template.format(module_name=module_name))

        if module_prefix is not None and module_prefix != "":
            cwd_cmd = "cd " + module_prefix + ";"
        else:
            cwd_cmd = ""
        run(f"{cwd_cmd} cp {__file__} {module_name}.sv test_{module_name}.py {temp_dir}", shell=True, check=True)
        run(f"make -C {temp_dir}", shell=True, check=True)

        failures = any_test_failures(temp_dir)
        if failures:
            run(f"cp {temp_dir}/results.xml /tmp/failed_results.xml", shell=True, check=True)
            raise ValueError("Test failed.")
