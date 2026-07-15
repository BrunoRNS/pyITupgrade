# Setting up SCHISM_HOME environment variable

This guide explains how to set the `SCHISM_HOME` environment variable required by the project.  
`SCHISM_HOME` must point to the directory containing the Schism Tracker executable for your operating system.

## Prerequisites

- Schism Tracker installed or compiled.  
  Download it from the [official website](http://schismtracker.org/) or build from source.  
  Make sure the folder contains the correct file as described below.

## What should SCHISM_HOME point to?

Set the variable to the **directory** that contains:

| Operating system | Required file inside the folder |
|------------------|---------------------------------|
| Windows          | `schismtracker.exe`             |
| macOS            | `Schism Tracker.app`            |
| Linux            | `run.sh`                        |

Example: if the full path to the executable on Windows is `C:\tools\schism\schismtracker.exe`, then `SCHISM_HOME` must be `C:\tools\schism`.

## Temporary setup (current terminal session only)

### Windows (Windows Command Prompt, Windows PowerShell)

**Open a new terminal window (can be powerShell or Command Prompt):**

You can press `Windows + R` to open the Run dialog, then type `cmd` or `PowerShell` and press Enter.

#### Windows Command Prompt

```cmd
set SCHISM_HOME=C:\path\to\schism\folder
```

#### Windows PowerShell

```powershell
$env:SCHISM_HOME = "C:\path\to\schism\folder"
```

### macOS / Linux (bash, zsh, etc.)

```bash
export SCHISM_HOME=/path/to/schism/folder
```

The variable exists only while the terminal is open. Closing the window discards it.

## Permanent setup

### Windows

#### Using the graphical interface

1. Open **System Properties** -> **Advanced** -> **Environment Variables**.
2. Under **User variables** (or **System variables** for all users), click **New**.
3. **Variable name:** `SCHISM_HOME`
4. **Variable value:** the path to your Schism folder (e.g., `C:\tools\schism`)
5. Click **OK** and restart any open command prompts.

#### Using Command Prompt (non‑admin)

```cmd
setx SCHISM_HOME "C:\path\to\schism\folder"
```

`setx` makes the change permanent for **future** command windows; it does not affect the current one. To use it immediately, also run the temporary `set` command shown above.

#### Using PowerShell

```powershell
[Environment]::SetEnvironmentVariable("SCHISM_HOME", "C:\path\to\schism\folder", "User")
```

Replace `"User"` with `"Machine"` for a system‑wide setting (requires administrator privileges).  
Restart PowerShell or open a new terminal to see the effect.

### macOS

Add the export line to your shell configuration file.

**If you use bash** (default on older macOS):

```bash
echo 'export SCHISM_HOME=/path/to/schism/folder' >> ~/.bash_profile
```

**If you use zsh** (default from macOS Catalina onward):

```bash
echo 'export SCHISM_HOME=/path/to/schism/folder' >> ~/.zshrc
```

Then reload the profile:

```bash
source ~/.bash_profile   # for bash
source ~/.zshrc          # for zsh
```

### Linux

Add the export to your shell’s startup file (e.g., `~/.bashrc` for bash, `~/.zshrc` for zsh, or `~/.profile`):

```bash
echo 'export SCHISM_HOME=/path/to/schism/folder' >> ~/.bashrc
source ~/.bashrc
```

Replace `.bashrc` with the appropriate file if you use a different shell.

## Verification

Open a **new** terminal window and run:

- **Windows CMD:** `echo %SCHISM_HOME%`
- **Windows PowerShell:** `echo $env:SCHISM_HOME`
- **macOS / Linux:** `echo $SCHISM_HOME`

The output should be the directory you configured.

Once the variable is set, you can use the project’s Makefile that depends on `SCHISM_HOME`.
