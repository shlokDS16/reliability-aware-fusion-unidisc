#!/bin/bash
# PG-1 generation stages, sequential, each through exp001/gate_driver.py (gpu_guard chunks, 50 percent duty, 2-minute pauses).
cd "C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/dlm-discovery-resume-ca3357"
PYE="C:/Users/Shlok/Downloads/Multi-Modality Language model/.venv-eval/Scripts/python.exe"
for spec in "pg1g"; do
  set -- $spec
  stage=$1; shift
  "$PYE" exp001/gate_driver.py --stage $stage -- "$@" > runs/EXP-001/gates/driver-$stage.log 2>&1
  rc=$?
  echo "$(date +%T) stage $stage driver exit $rc" >> runs/EXP-001/gates/driver-all.log
  if [ $rc -ne 0 ]; then echo "STOP at $stage" >> runs/EXP-001/gates/driver-all.log; exit $rc; fi
  sleep 120
done
echo "$(date +%T) PG-1 generation complete" >> runs/EXP-001/gates/driver-all.log
