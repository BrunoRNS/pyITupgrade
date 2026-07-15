# Setting up SNES_EMU environment variable

This guide explains how to set the `SNES_EMU` environment variable required by the project.  
`SNES_EMU` **must** contain the **absolute path** to your SNES emulator executable (or `.app` bundle on macOS).  
Relying on `PATH` is **not supported** – you must provide the full, absolute location.

The emulator must be able to open a ROM file passed as a command‑line argument.

## Recommended emulators

The following emulators have been tested and work reliably:

- **Snes9x** (cross‑platform)  
- **LakeSNES** (Windows / Linux)  

Other emulators (ZSNES, bsnes/higan, Mesen‑S, etc.) may also work as long as they accept a ROM path as a command‑line argument.

## What should SNES_EMU point to?

| Operating system | SNES_EMU value (absolute path)                                           |
|------------------|--------------------------------------------------------------------------|
| Windows          | `C:\Emulators\snes9x.exe` or `D:\tools\lakesnes.exe`                     |
| Linux            | `/usr/local/bin/snes9x`  or `/opt/lakesnes/lakesnes`                     |
| macOS            | `/Applications/Snes9x.app` (the `.app` bundle is required for `open -a`) |

## Temporary setup (current terminal session only)

### Windows Command Prompt

```cmd
set SNES_EMU=C:\absolute\path\to\emulator.exe
```

### Windows PowerShell

```powershell
$env:SNES_EMU = "C:\absolute\path\to\emulator.exe"
```

### macOS / Linux (bash, zsh, etc.)

```bash
export SNES_EMU=/absolute/path/to/emulator
```

For macOS, the path must end with `.app`, e.g. `/Applications/Snes9x.app`.

The variable exists only while the terminal is open. Closing the window discards it.

## Permanent setup

### Windows

#### Using the graphical interface

1. Open **System Properties** -> **Advanced** -> **Environment Variables**.
2. Under **User variables** (or **System variables** for all users), click **New**.
3. **Variable name:** `SNES_EMU`
4. **Variable value:** the **absolute** path to the emulator (e.g., `C:\tools\snes9x\snes9x.exe`)
5. Click **OK** and restart any open command prompts.

#### Using Command Prompt (non‑admin)

```cmd
setx SNES_EMU "C:\absolute\path\to\emulator.exe"
```

`setx` applies to **future** command windows; it does not affect the current one. Use the temporary `set` command above to also set it now.

#### Using PowerShell

```powershell
[Environment]::SetEnvironmentVariable("SNES_EMU", "C:\absolute\path\to\emulator.exe", "User")
```

Replace `"User"` with `"Machine"` for a system‑wide setting (requires administrator privileges).  
Restart PowerShell or open a new terminal to see the effect.

### macOS

Add the export line to your shell configuration file.

**If you use bash** (default on older macOS):

```bash
echo 'export SNES_EMU=/absolute/path/to/Snes9x.app' >> ~/.bash_profile
```

**If you use zsh** (default from macOS Catalina onward):

```bash
echo 'export SNES_EMU=/absolute/path/to/Snes9x.app' >> ~/.zshrc
```

Then reload the profile:

```bash
source ~/.bash_profile   # for bash
source ~/.zshrc          # for zsh
```

> **Important:** On macOS the value **must** be the absolute path to an `.app` bundle, otherwise `open -a` will fail.

### Linux

Add the export to your shell’s startup file (e.g., `~/.bashrc` for bash, `~/.zshrc` for zsh, or `~/.profile`):

```bash
echo 'export SNES_EMU=/absolute/path/to/emulator' >> ~/.bashrc
source ~/.bashrc
```

Replace `.bashrc` with the appropriate file if you use a different shell.

> **Reminder:** Do **not** use just the command name (e.g., `snes9x`). An absolute path is required.

## Verification

Open a **new** terminal window and run:

- **Windows CMD:** `echo %SNES_EMU%`
- **Windows PowerShell:** `echo $env:SNES_EMU`
- **macOS / Linux:** `echo $SNES_EMU`

The output must be the absolute path you configured.  
Test it manually:

- **Windows:** `%SNES_EMU% path\to\rom.sfc`
- **Linux:** `$SNES_EMU path\to\rom.sfc`
- **macOS:** `open -a "$SNES_EMU" --args path\to\rom.sfc`

If the emulator starts and loads the ROM, the variable is set correctly.

Once the variable is set, you can use the project’s Makefile that depends on `SNES_EMU`.
