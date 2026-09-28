### 1. Install on your device
Download the .zip archive from this repo by clicking `Code` followed by `Download ZIP`

### 2. Setup virtual environment

Put `setup_venv.ps1` in the same directory as `calendar365.py`, then run:
```
.\setup_venv.ps1
```

> ___If PowerShell refuses to run the script because of its execution policy, you can run it for the current PowerShell session with:___

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass .\setup_venv.ps1
```
### 3. Configure photo folder
To add photo's to the left-hand side of the calendar, create a folder `\photo ` in the applications root folder.
Name the photo's you wish to add to the folder and use the following naming convention `{month}{photo_num}.{extension}`, the photo's will be added to the calendar automatically following the naming convention.

___Where `{month}` is the digits for the calendar month (`1, 2, 3, ... 10, 11, 12`).___

___Where `{photo_num}` is the position on the calendar, this can only be `1` or `2`. 1 being top left, 2 being bottom left position.___

___Accepted extensions are `.jpg`, `.jpeg` and `.png`.___

As a result the filenames will look like `11.jpg` (January, 1st photo position) or `122.png` (December, 2nd photo position).

### 4. Generate PDF Calendar
After setup, you don't actually need to activate the environment. The script can directly use:

```
.\.venv\Scripts\python.exe .\calendar365.py 2027
```

This has the advantage that the correct Python environment is always explicitly used.
