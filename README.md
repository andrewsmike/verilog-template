SystemsVerilog template repo
============================
This repo is intended as a starting point for building other systemsverilog repositories.
It includes sane pre-commit hook configurations, with linter, formatter, and testing framework, as well as some examples of how to test modules using the cocotb and pytest based harness.

Installing
==========
To set up the tooling for this repository:
- Install [iverilog](https://iverilog.fandom.com/wiki/User_Guide) and [verible](https://github.com/google/verible) for your platform. Archlinux has the iverilog community package and the verible-bin AUR package.
- Install the necessary python tooling using:
```bash
pip install pre-commit cocotb pytest hypothesis lxml black flake8 isort mypy
```
- Run `pre-commit install` to set up the git commit hooks.

