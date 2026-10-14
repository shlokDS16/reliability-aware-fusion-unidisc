@echo off
REM EXP-003 driver launcher (resumable). Start detached:  see runs/EXP-003/IMPLEMENTATION.md
cd /d "C:\Users\Shlok\Downloads\Multi-Modality Language model\.claude\worktrees\dlm-discovery-resume-ca3357"
"C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv-eval\Scripts\python.exe" -u -m exp003.driver >> runs\EXP-003\driver.out 2>&1
