Usage

Put setup_venv.ps1 in the same directory as maak_nederlandse_maandkalender.py, then run:
`.\setup_venv.ps1`

If PowerShell refuses to run the script because of its execution policy, you can run it for the current PowerShell session with:

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_venv.ps1
```

After setup, you don't actually need to activate the environment. The script can directly use:

`.\.venv\Scripts\python.exe .\maak_nederlandse_maandkalender.py 2027`

This has the advantage that the correct Python environment is always explicitly used.
