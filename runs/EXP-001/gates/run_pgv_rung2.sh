#!/bin/bash
# PG-V ladder: rung 1 failed (criterion c), repeat at rung 2 on pool PG2 (24 prefixes x 2 seeds)
cd "C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/dlm-discovery-resume-ca3357"
PYE="C:/Users/Shlok/Downloads/Multi-Modality Language model/.venv-eval/Scripts/python.exe"
"$PYE" exp001/gate_driver.py --stage pgv --tag rung2 -- --res 512 --rule conf --rung 2 --tag rung2 > runs/EXP-001/gates/driver-pgv-rung2.log 2>&1
echo "$(date +%T) pgv rung2 driver exit $?" >> runs/EXP-001/gates/driver-all.log
