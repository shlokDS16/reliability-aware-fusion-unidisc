#!/bin/bash
cd "C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/dlm-discovery-resume-ca3357"
PYE="C:/Users/Shlok/Downloads/Multi-Modality Language model/.venv-eval/Scripts/python.exe"
"$PYE" exp001/gate_driver.py --stage pgv -- --res 512 --rule conf --rung 1 > runs/EXP-001/gates/driver-pgv.log 2>&1
echo "$(date +%T) stage pgv driver exit $?" >> runs/EXP-001/gates/driver-all.log
