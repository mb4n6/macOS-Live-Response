# Forensic USB Tool -- Python GUI

A standalone forensic USB preparation and live response tool with a graphical
interface built using **tkinter**.\
Designed for macOS forensic analysis, live triage, and trusted binary deployment
for law enforcement and digital forensic practitioners.

------------------------------------------------------------------------

## Author

Marc Brandt | mb4n6
Hochschule für Polizei Baden-Württemberg

------------------------------------------------------------------------

## Features

### USB Preparation (Tab 1)
**APFS USB stick preparation** with clear formatting instructions\
**Trusted binaries deployment** - copies system binaries to USB:\
- `/usr/bin`, `/bin`, `/usr/sbin`, `/sbin`\
- `/usr/X11/bin`\
- `/usr/sbin/system_profiler`

**Automatic disk detection** (physical disk identification)\
**Cross-tab USB synchronization** - selection propagates to all tabs\
**Real-time status logging** with timestamps

### Trusted Terminal (Tab 2)
**Symbolic link creation** for trusted bash execution\
**Trusted terminal launch** from USB binaries\
**PATH variable configuration** - redirects to USB binaries\
**Session logging setup** with script command\
**One-click automation** - executes all steps sequentially

### Live Response (Tab 3)
**System & Hardware** - system_profiler, hardware details, NVRAM, kernel extensions\
**FileVault information** - encryption status, APFS containers, authorized users\
**Process & Services** - running processes, launchd services, open files, network connections\
**Network information** - netstat, routing tables, sharing services\
**User activities** - active users, login history, shell command histories\
**System logs** - system.log, unified logs (24h), security logs\
**Logical acquisition** with GUI directory selection:\
- Complete /Users directory\
- Documents, Desktop, Downloads\
- Mail & Messages\
- Browser profiles (Safari, Chrome, Firefox)\
- User Library directories

**SHA-256 hash generation** for all collected files\
**Batch execution** - run all collection commands automatically\
**Terminal output monitoring** with real-time status updates

------------------------------------------------------------------------

## Requirements

### System Requirements
- macOS (Intel or Apple Silicon)\
- Python 3.x (pre-installed on macOS)\
- Administrator (sudo) privileges for binary copying

### Python Dependencies
- tkinter (pre-installed with macOS Python)\
- subprocess, os, threading, re, pathlib, datetime (standard library)

------------------------------------------------------------------------

## Installation

No installation required - standalone Python script.

Ensure execution permissions:
``` bash
chmod +x forensic_usb_tool.py
```

------------------------------------------------------------------------

## Usage

### Quick Start
``` bash
python3 forensic_usb_tool.py
```

### Workflow

#### 1. USB Preparation
1. Format USB stick with **Disk Utility** (APFS format)\
2. Launch tool and go to **Tab 1: USB Preparation**\
3. Click **Scan USB Sticks**\
4. Select your USB stick from dropdown\
5. Click **Copy Binaries** (requires sudo password)\
6. Wait for completion message

#### 2. Trusted Terminal Setup
1. Go to **Tab 2: Trusted Terminal**\
2. USB stick should be pre-selected (from Tab 1)\
3. Click **Execute All Steps Automatically**, or:\
   - Create Symbolic Link\
   - Open Trusted Terminal\
   - Adjust PATH Variable\
   - Create Log File\
4. Work in the opened trusted terminal with USB binaries

#### 3. Live Response Data Collection
1. Go to **Tab 3: Live Response**\
2. Select output USB stick\
3. Click individual collection buttons or **Execute All Steps**:\
   - System & Hardware\
   - FileVault Info\
   - Processes & Services\
   - Network Info\
   - User Activities\
   - System Logs\
   - Logical Acquisition (select directories)\
   - Create Hashes\
4. Monitor progress in Terminal Output window\
5. Retrieve collected data from USB stick

------------------------------------------------------------------------

## Technical Details

### Trusted Binaries Concept
Prevents rootkit manipulation by using known-good binaries from USB:\
- System binaries copied before incident response\
- Terminal execution redirected to USB binaries\
- PATH variable modified to prioritize USB tools\
- Session logging captures all command output

### Live Response Commands
**System Information:**
``` bash
system_profiler
system_profiler SPHardwareDataType
nvram -xp
kextstat
```

**FileVault:**
``` bash
sudo fdesetup status
diskutil apfs list
sudo fdesetup list
```

**Processes:**
``` bash
ps aux
launchctl list
lsof
lsof -i
```

**Network:**
``` bash
netstat -an
netstat -r
sharing -l
```

**Users:**
``` bash
who
last
cat /Users/*/.zsh_history
cat /Users/*/.bash_history
```

**Logs:**
``` bash
cp /var/log/system.log
log show --last 24h
log show --predicate 'subsystem == "com.apple.security"' --last 24h
```

**Logical Acquisition:**
``` bash
tar czf output.tar.gz [selected_directory]
```

**Hashing:**
``` bash
shasum -a 256 *.txt *.tar.gz > checksums.txt
```

------------------------------------------------------------------------

## License

Educational use for training.
