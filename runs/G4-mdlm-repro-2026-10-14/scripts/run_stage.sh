#!/bin/bash
# usage: run_stage.sh <stage-name> <done-file> <command...>   (run from the worktree root)
# Runs the command under tools/gpu_guard.py in 15-minute chunks (exit 91 -> 2 min pause -> resume); stops on exit 90 (temperature).
# The python children sometimes exit with 0xC0000409 AFTER writing their results (interpreter/CUDA teardown), so a stage counts as finished
# when <done-file> exists, whatever the exit code.
stage=$1; done_file=$2; shift 2
PY="C:/Users/Shlok/Downloads/Multi-Modality Language model/.venv/Scripts/python.exe"
LOG=runs/G4-mdlm-repro-2026-10-14/telemetry-$stage.csv
while true; do
  "$PY" tools/gpu_guard.py --log "$LOG" --max-minutes 15 -- "$@"
  rc=$?
  echo "[run_stage] $stage chunk exit $rc at $(date +%T)"
  if [ -f "$done_file" ]; then echo "[run_stage] $stage DONE"; break; fi
  if [ $rc -eq 90 ]; then echo "[run_stage] STOP temperature"; exit 90; fi
  if [ $rc -eq 91 ]; then sleep 120; continue; fi
  echo "[run_stage] STOP unexpected rc=$rc and no done-file"; exit 1
done
