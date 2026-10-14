#!/bin/bash
# try 2 (layout without the space before the masks): PG-1 condition-P leg, then PG-V rung 1
cd "C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/dlm-discovery-resume-ca3357"
PYE="C:/Users/Shlok/Downloads/Multi-Modality Language model/.venv-eval/Scripts/python.exe"
"$PYE" exp001/gate_driver.py --stage pg1p -- --res 512 --rule conf > runs/EXP-001/gates/driver-pg1p.log 2>&1
echo "$(date +%T) try2 stage pg1p driver exit $?" >> runs/EXP-001/gates/driver-all.log
sleep 120
"$PYE" exp001/gate_driver.py --stage pgv -- --res 512 --rule conf --rung 1 > runs/EXP-001/gates/driver-pgv.log 2>&1
echo "$(date +%T) try2 stage pgv driver exit $?" >> runs/EXP-001/gates/driver-all.log
