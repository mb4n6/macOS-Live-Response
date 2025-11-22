#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import os
import threading
import re
from pathlib import Path
from datetime import datetime

class ForensicUSBTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Forensic USB Tool - Trusted Binaries")
        self.root.geometry("950x750")
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TCombobox', fieldbackground='white', background='white', foreground='black')
        style.map('TCombobox', fieldbackground=[('readonly', 'white')], foreground=[('readonly', 'black')])
        
        self.selected_usb = tk.StringVar()
        self.output_usb = tk.StringVar()
        self.usb_volumes = []
        self.disk_info = {}
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab1 = tk.Frame(self.notebook, bg='#E8E8E8')
        self.notebook.add(self.tab1, text='1. USB Preparation')
        
        self.tab2 = tk.Frame(self.notebook, bg='#E8E8E8')
        self.notebook.add(self.tab2, text='2. Trusted Terminal')
        
        self.tab3 = tk.Frame(self.notebook, bg='#E8E8E8')
        self.notebook.add(self.tab3, text='3. Live Response')
        
        self.setup_preparation_tab()
        self.setup_liveresponse_tab()
        self.setup_live_response_tab()
        
    def setup_preparation_tab(self):
        header_frame = tk.Frame(self.tab1, bg='#E8E8E8')
        header_frame.pack(fill='x', pady=15)
        
        header = tk.Label(header_frame, text="USB Stick Preparation | Do that on your forensic Mac!", 
                         font=('Helvetica', 18, 'bold'), bg='#E8E8E8', fg='#1a1a1a')
        header.pack()
        
        info_frame = tk.LabelFrame(self.tab1, text=" Important Information ", 
                                  font=('Helvetica', 11, 'bold'), 
                                  bg='#FFE6B3', fg='#1a1a1a', padx=15, pady=15)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        info_text = ("⚠️  Please use an APFS formatted USB stick!\n\n"
                    "Format your USB stick with Disk Utility before using this tool:\n"
                    "• Open Disk Utility\n"
                    "• Select your USB stick\n"
                    "• Click 'Erase' and choose 'APFS' as format\n"
                    "• Give it a name (e.g., 'forensic')")
        tk.Label(info_frame, text=info_text, justify='left', bg='#FFE6B3', fg='#1a1a1a',
                font=('Helvetica', 10)).pack(anchor='w', pady=5)
        
        usb_frame = tk.LabelFrame(self.tab1, text=" USB Stick Selection ", 
                                 font=('Helvetica', 11, 'bold'), 
                                 bg='#D3D3D3', fg='#1a1a1a', padx=15, pady=15)
        usb_frame.pack(fill='x', padx=20, pady=10)
        
        btn_frame = tk.Frame(usb_frame, bg='#D3D3D3')
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="🔍 Scan USB Sticks", 
                 command=self.scan_usb_devices,
                 bg='#505050', fg='black', font=('Helvetica', 10),
                 padx=10, pady=5, relief=tk.RAISED, bd=2).pack(side='left', padx=5)
        
        self.usb_combo = ttk.Combobox(btn_frame, textvariable=self.selected_usb, 
                                      state='readonly', width=50, font=('Helvetica', 10))
        self.usb_combo.pack(side='left', padx=10, fill='x', expand=True)
        
        self.disk_info_label = tk.Label(usb_frame, text="", bg='#D3D3D3', 
                                       fg='#505050', font=('Helvetica', 9, 'italic'))
        self.disk_info_label.pack(pady=5)
        
        copy_frame = tk.LabelFrame(self.tab1, text=" Copy Trusted Binaries ", 
                                  font=('Helvetica', 11, 'bold'),
                                  bg='#D3D3D3', fg='#1a1a1a', padx=15, pady=15)
        copy_frame.pack(fill='x', padx=20, pady=10)
        
        info_text = ("The following directories will be copied:\n"
                    "• /usr/bin  • /bin  • /usr/sbin  • /sbin\n"
                    "• /usr/X11/bin  • /usr/sbin/system_profiler")
        tk.Label(copy_frame, text=info_text, justify='left', bg='#D3D3D3', fg='#1a1a1a',
                font=('Helvetica', 9)).pack(anchor='w', pady=5)
        
        tk.Button(copy_frame, text="📦 Copy Binaries (requires sudo)", 
                 command=self.copy_binaries,
                 bg='#505050', fg='black', font=('Helvetica', 10, 'bold'),
                 padx=15, pady=8, relief=tk.RAISED, bd=2).pack(pady=10)
        
        self.prep_progress_frame = tk.LabelFrame(self.tab1, text=" Status ", 
                                                font=('Helvetica', 11, 'bold'),
                                                bg='#D3D3D3', fg='#1a1a1a', 
                                                padx=15, pady=10)
        self.prep_progress_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.prep_log = scrolledtext.ScrolledText(self.prep_progress_frame, 
                                                  height=10, 
                                                  bg='#F5F5F5', 
                                                  fg='#000000',
                                                  font=('Courier', 9),
                                                  relief=tk.SUNKEN, bd=2)
        self.prep_log.pack(fill='both', expand=True)
        
    def setup_liveresponse_tab(self):
        header_frame = tk.Frame(self.tab2, bg='#E8E8E8')
        header_frame.pack(fill='x', pady=15)
        
        header = tk.Label(header_frame, text="Trusted Terminal Setup | Do that on the suspects Mac!", 
                         font=('Helvetica', 18, 'bold'), bg='#E8E8E8', fg='#1a1a1a')
        header.pack()
        
        usb_frame = tk.LabelFrame(self.tab2, text=" USB Stick Selection ", 
                                 font=('Helvetica', 11, 'bold'),
                                 bg='#D3D3D3', fg='#1a1a1a', padx=15, pady=15)
        usb_frame.pack(fill='x', padx=20, pady=10)
        
        btn_frame = tk.Frame(usb_frame, bg='#D3D3D3')
        btn_frame.pack(fill='x')
        
        tk.Button(btn_frame, text="🔍 Scan USB Sticks", 
                 command=self.scan_usb_devices_live,
                 bg='#505050', fg='black', font=('Helvetica', 10),
                 padx=10, pady=5, relief=tk.RAISED, bd=2).pack(side='left', padx=5)
        
        self.usb_combo_live = ttk.Combobox(btn_frame, state='readonly', width=50,
                                          font=('Helvetica', 10))
        self.usb_combo_live.pack(side='left', padx=10, fill='x', expand=True)
        
        actions_frame = tk.LabelFrame(self.tab2, text=" Trusted Terminal Actions ", 
                                     font=('Helvetica', 11, 'bold'),
                                     bg='#D3D3D3', fg='#1a1a1a', padx=15, pady=15)
        actions_frame.pack(fill='x', padx=20, pady=10)
        
        button_config = {
            'font': ('Helvetica', 10),
            'width': 45,
            'pady': 8,
            'relief': tk.RAISED,
            'bd': 2
        }
        
        tk.Button(actions_frame, text="1️⃣ Create Symbolic Link", 
                 command=self.create_symlink, bg='#C0C0C0', fg='#1a1a1a',
                 **button_config).pack(pady=3)
        
        tk.Button(actions_frame, text="2️⃣ Open Trusted Terminal", 
                 command=self.open_trusted_terminal, bg='#C0C0C0', fg='#1a1a1a',
                 **button_config).pack(pady=3)
        
        tk.Button(actions_frame, text="3️⃣ Adjust PATH Variable", 
                 command=self.adjust_path, bg='#C0C0C0', fg='#1a1a1a',
                 **button_config).pack(pady=3)
        
        tk.Button(actions_frame, text="4️⃣ Create Log File", 
                 command=self.create_logfile, bg='#C0C0C0', fg='#1a1a1a',
                 **button_config).pack(pady=3)
        
        ttk.Separator(actions_frame, orient='horizontal').pack(fill='x', pady=10)
        
        tk.Button(actions_frame, text="🚀 Execute All Steps Automatically", 
                 command=self.run_all_steps, bg='#505050', fg='black',
                 font=('Helvetica', 11, 'bold'), width=45, pady=10,
                 relief=tk.RAISED, bd=3).pack(pady=5)
        
        info_frame = tk.LabelFrame(self.tab2, text=" Information ", 
                                  font=('Helvetica', 11, 'bold'),
                                  bg='#D3D3D3', fg='#1a1a1a', padx=15, pady=10)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        info_text = ("Steps for Live Response:\n"
                    "1. Symbolic Link: /Volumes/[usb]/Terminal → bash\n"
                    "2. Open Terminal from USB stick\n"
                    "3. Set PATH to USB binaries\n"
                    "4. Start logging with 'script'")
        tk.Label(info_frame, text=info_text, justify='left', bg='#D3D3D3', fg='#1a1a1a',
                font=('Helvetica', 9)).pack(anchor='w')
        
        self.live_log_frame = tk.LabelFrame(self.tab2, text=" Status ", 
                                           font=('Helvetica', 11, 'bold'),
                                           bg='#D3D3D3', fg='#1a1a1a',
                                           padx=15, pady=10)
        self.live_log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.live_log = scrolledtext.ScrolledText(self.live_log_frame, 
                                                  height=8, 
                                                  bg='#F5F5F5', 
                                                  fg='#000000',
                                                  font=('Courier', 9),
                                                  relief=tk.SUNKEN, bd=2)
        self.live_log.pack(fill='both', expand=True)
        
    def scan_usb_devices(self):
        self.log_prep("Scanning USB devices...")
        try:
            volumes_result = subprocess.run(['ls', '/Volumes'], 
                                          capture_output=True, text=True)
            
            volumes = [v for v in volumes_result.stdout.strip().split('\n') 
                      if v and v != 'Macintosh HD']
            
            self.disk_info = {}
            for volume in volumes:
                result = subprocess.run(['diskutil', 'info', f'/Volumes/{volume}'],
                                      capture_output=True, text=True)
                
                physical_disk = None
                device_id = None
                
                for line in result.stdout.split('\n'):
                    if 'APFS Physical Store' in line:
                        match = re.search(r'(disk\d+s\d+)', line)
                        if match:
                            physical_store = match.group(1)
                            physical_disk = re.sub(r's\d+$', '', physical_store)
                            break
                    elif 'Part of Whole' in line:
                        match = re.search(r'(disk\d+)', line)
                        if match:
                            physical_disk = match.group(1)
                            break
                    elif 'Device Identifier' in line:
                        match = re.search(r'(disk\d+s?\d*)', line)
                        if match:
                            device_id = match.group(1)
                
                if physical_disk:
                    self.disk_info[volume] = physical_disk
                elif device_id:
                    if 'disk' in device_id and 's' not in device_id:
                        self.disk_info[volume] = device_id
                    else:
                        whole_disk = re.sub(r's\d+$', '', device_id)
                        self.disk_info[volume] = whole_disk
                else:
                    self.disk_info[volume] = 'unknown'
            
            self.usb_volumes = volumes
            self.usb_combo['values'] = volumes
            
            if volumes:
                self.usb_combo.current(0)
                selected = volumes[0]
                disk = self.disk_info.get(selected, 'unknown')
                self.disk_info_label.config(text=f"Disk Identifier: {disk}")
                self.log_prep(f"✓ {len(volumes)} Volume(s) found: {', '.join(volumes)}")
                for vol in volumes:
                    disk = self.disk_info.get(vol, 'unknown')
                    self.log_prep(f"  • {vol} → {disk}")
                
                if hasattr(self, 'usb_combo_live'):
                    self.usb_combo_live['values'] = volumes
                    self.usb_combo_live.current(0)
                if hasattr(self, 'output_combo'):
                    self.output_combo['values'] = volumes
                    self.output_combo.current(0)
            else:
                self.log_prep("⚠ No external volumes found")
                self.disk_info_label.config(text="")
                
            def update_disk_label(event):
                selected = self.selected_usb.get()
                if selected:
                    disk = self.disk_info.get(selected, 'unknown')
                    self.disk_info_label.config(text=f"Disk Identifier: {disk}")
                    
                    if hasattr(self, 'usb_combo_live'):
                        self.usb_combo_live.set(selected)
                    if hasattr(self, 'output_combo'):
                        self.output_combo.set(selected)
                    
            self.usb_combo.bind('<<ComboboxSelected>>', update_disk_label)
                
        except Exception as e:
            self.log_prep(f"✗ Scanning error: {str(e)}")
            
    def copy_binaries(self):
        selected = self.selected_usb.get()
        if not selected:
            messagebox.showerror("Error", "Please select a USB stick first")
            return
            
        volume_path = f"/Volumes/{selected}"
        
        if not os.path.exists(volume_path):
            messagebox.showerror("Error", 
                               f"Volume '{selected}' not found!\n"
                               f"Please format the USB stick first.")
            return
            
        response = messagebox.askyesno(
            "Copy Binaries",
            f"Trusted binaries will be copied to:\n{volume_path}\n\n"
            f"This requires sudo rights and may take several minutes.\n\n"
            f"Continue?"
        )
        
        if not response:
            return
            
        self.log_prep("Starting copy process (sudo required)...")
        
        def copy_thread():
            directories = [
                '/usr/bin',
                '/bin',
                '/usr/sbin',
                '/sbin',
                '/usr/X11/bin'
            ]
            
            total = len(directories) + 1
            current = 0
            
            try:
                for directory in directories:
                    current += 1
                    if os.path.exists(directory):
                        self.log_prep(f"[{current}/{total}] Copying {directory}...")
                        cmd = ['sudo', 'cp', '-r', directory, volume_path]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            self.log_prep(f"✓ {directory} copied")
                        else:
                            self.log_prep(f"⚠ {directory}: {result.stderr}")
                    else:
                        self.log_prep(f"⚠ {directory} not found")
                
                current += 1
                if os.path.exists('/usr/sbin/system_profiler'):
                    self.log_prep(f"[{current}/{total}] Copying system_profiler...")
                    cmd = ['sudo', 'cp', '/usr/sbin/system_profiler', volume_path]
                    subprocess.run(cmd, capture_output=True, text=True)
                    self.log_prep("✓ system_profiler copied")
                
                self.log_prep("\n" + "="*50)
                self.log_prep("✓ Copy process completed!")
                self.log_prep(f"✓ USB stick '{selected}' is ready for Live Response.")
                self.log_prep("="*50)
                
            except Exception as e:
                self.log_prep(f"✗ Copy error: {str(e)}")
                
        threading.Thread(target=copy_thread, daemon=True).start()
        
    def scan_usb_devices_live(self):
        self.log_live("Scanning USB devices...")
        try:
            volumes_result = subprocess.run(['ls', '/Volumes'], 
                                          capture_output=True, text=True)
            
            volumes = [v for v in volumes_result.stdout.strip().split('\n') 
                      if v and v != 'Macintosh HD']
            
            self.usb_combo_live['values'] = volumes
            
            if volumes:
                self.usb_combo_live.current(0)
                self.log_live(f"✓ {len(volumes)} Volume(s) found: {', '.join(volumes)}")
            else:
                self.log_live("⚠ No external volumes found")
                
        except Exception as e:
            self.log_live(f"✗ Error: {str(e)}")
            
    def get_selected_usb_live(self):
        usb = self.usb_combo_live.get()
        if not usb:
            messagebox.showerror("Error", "Please select a USB stick first")
            return None
        return usb
        
    def create_symlink(self):
        usb = self.get_selected_usb_live()
        if not usb:
            return
            
        volume_path = f"/Volumes/{usb}"
        bash_path = f"{volume_path}/bin/bash"
        terminal_link = f"{volume_path}/Terminal"
        
        if not os.path.exists(bash_path):
            messagebox.showerror("Error", 
                               f"bash not found in {bash_path}\n"
                               f"Please copy binaries first!")
            return
            
        try:
            if os.path.exists(terminal_link):
                os.remove(terminal_link)
                
            os.symlink(bash_path, terminal_link)
            self.log_live(f"✓ Symbolic link created:")
            self.log_live(f"  {terminal_link} → {bash_path}")
            
        except Exception as e:
            self.log_live(f"✗ Link creation error: {str(e)}")
            
    def open_trusted_terminal(self):
        usb = self.get_selected_usb_live()
        if not usb:
            return
            
        terminal_link = f"/Volumes/{usb}/Terminal"
        
        if not os.path.exists(terminal_link):
            messagebox.showerror("Error", 
                               "Symbolic link not found!\n"
                               "Create the link first.")
            return
            
        try:
            subprocess.Popen(['open', '-a', 'Terminal', terminal_link])
            self.log_live(f"✓ Trusted Terminal opened from:")
            self.log_live(f"  {terminal_link}")
            
        except Exception as e:
            self.log_live(f"✗ Terminal opening error: {str(e)}")
            
    def adjust_path(self):
        usb = self.get_selected_usb_live()
        if not usb:
            return
            
        path_cmd = f"PATH=/Volumes/{usb}/usr/bin:/Volumes/{usb}/bin:/Volumes/{usb}/usr/sbin:/Volumes/{usb}/sbin:/Volumes/{usb}/usr/X11/bin"
        
        script_path = f"/Volumes/{usb}/set_path.sh"
        
        try:
            with open(script_path, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write(f"export {path_cmd}\n")
                f.write('echo "✓ PATH set to trusted binaries"\n')
                f.write('echo "PATH=$PATH"\n')
                f.write('echo ""\n')
                f.write('echo "Verification:"\n')
                f.write('which bash\n')
                f.write('which ls\n')
                
            os.chmod(script_path, 0o755)
            
            self.log_live(f"✓ PATH script created: {script_path}")
            self.log_live("➜ Execute in Terminal:")
            self.log_live(f"  source /Volumes/{usb}/set_path.sh")
            
        except Exception as e:
            self.log_live(f"✗ Error: {str(e)}")
            
    def create_logfile(self):
        usb = self.get_selected_usb_live()
        if not usb:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = f"/Volumes/{usb}/liveresponse_{timestamp}.txt"
        
        helper_script = f"/Volumes/{usb}/start_logging.sh"
        
        try:
            with open(helper_script, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write(f"# Live Response Logging - {timestamp}\n")
                f.write(f'echo "========================================"\n')
                f.write(f'echo "Live Response Session Started"\n')
                f.write(f'echo "Timestamp: {timestamp}"\n')
                f.write(f'echo "Log File: {log_path}"\n')
                f.write(f'echo "========================================"\n')
                f.write(f'echo ""\n')
                f.write(f"script {log_path}\n")
                
            os.chmod(helper_script, 0o755)
            
            self.log_live(f"✓ Logging script created: {helper_script}")
            self.log_live(f"  Log file: {log_path}")
            self.log_live("➜ Execute in Terminal:")
            self.log_live(f"  source {helper_script}")
            
        except Exception as e:
            self.log_live(f"✗ Error: {str(e)}")
            
    def run_all_steps(self):
        usb = self.get_selected_usb_live()
        if not usb:
            return
            
        self.log_live("=" * 50)
        self.log_live("Automatic execution of all steps")
        self.log_live("=" * 50)
        self.create_symlink()
        self.log_live("")
        self.adjust_path()
        self.log_live("")
        self.create_logfile()
        self.log_live("")
        self.log_live("=" * 50)
        self.log_live("✓ All steps completed")
        self.log_live("=" * 50)
        self.log_live("Opening Terminal...")
        self.open_trusted_terminal()
        
    def log_prep(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.prep_log.insert('end', f"[{timestamp}] {message}\n")
        self.prep_log.see('end')
        self.root.update_idletasks()
        
    def log_live(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.live_log.insert('end', f"[{timestamp}] {message}\n")
        self.live_log.see('end')
        self.root.update_idletasks()
        
    def log_response(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.response_log.insert('end', f"[{timestamp}] {message}\n")
        self.response_log.see('end')
        self.root.update_idletasks()
        
    def setup_live_response_tab(self):
        header_frame = tk.Frame(self.tab3, bg='#E8E8E8')
        header_frame.pack(fill='x', pady=15)
        
        header = tk.Label(header_frame, text="Live Response Data Collection | Do that on the suspects Mac!", 
                         font=('Helvetica', 18, 'bold'), bg='#E8E8E8', fg='#1a1a1a')
        header.pack()
        
        usb_frame = tk.LabelFrame(self.tab3, text=" Output USB Stick ", 
                                 font=('Helvetica', 11, 'bold'),
                                 bg='#D3D3D3', fg='#1a1a1a', padx=15, pady=15)
        usb_frame.pack(fill='x', padx=20, pady=10)
        
        btn_frame = tk.Frame(usb_frame, bg='#D3D3D3')
        btn_frame.pack(fill='x')
        
        tk.Button(btn_frame, text="🔍 Scan USB Sticks", 
                 command=self.scan_output_usb,
                 bg='#505050', fg='black', font=('Helvetica', 10),
                 padx=10, pady=5, relief=tk.RAISED, bd=2).pack(side='left', padx=5)
        
        self.output_combo = ttk.Combobox(btn_frame, textvariable=self.output_usb, 
                                        state='readonly', width=50, font=('Helvetica', 10))
        self.output_combo.pack(side='left', padx=10, fill='x', expand=True)
        
        commands_frame = tk.LabelFrame(self.tab3, text=" Live Response Commands ", 
                                      font=('Helvetica', 11, 'bold'),
                                      bg='#D3D3D3', fg='#1a1a1a', padx=15, pady=15)
        commands_frame.pack(fill='x', padx=20, pady=10)
        
        btn_config = {'font': ('Helvetica', 9), 'width': 35, 'pady': 5, 'relief': tk.RAISED, 'bd': 2}
        
        row1 = tk.Frame(commands_frame, bg='#D3D3D3')
        row1.pack(fill='x', pady=2)
        tk.Button(row1, text="System & Hardware", command=self.collect_system_info,
                 bg='#A0A0A0', fg='#000000', **btn_config).pack(side='left', padx=2)
        tk.Button(row1, text="FileVault Info", command=self.collect_filevault,
                 bg='#A0A0A0', fg='#000000', **btn_config).pack(side='left', padx=2)
        
        row2 = tk.Frame(commands_frame, bg='#D3D3D3')
        row2.pack(fill='x', pady=2)
        tk.Button(row2, text="Processes & Services", command=self.collect_processes,
                 bg='#A0A0A0', fg='#000000', **btn_config).pack(side='left', padx=2)
        tk.Button(row2, text="Network Info", command=self.collect_network,
                 bg='#A0A0A0', fg='#000000', **btn_config).pack(side='left', padx=2)
        
        row3 = tk.Frame(commands_frame, bg='#D3D3D3')
        row3.pack(fill='x', pady=2)
        tk.Button(row3, text="User Activities", command=self.collect_users,
                 bg='#A0A0A0', fg='#000000', **btn_config).pack(side='left', padx=2)
        tk.Button(row3, text="System Logs", command=self.collect_logs,
                 bg='#A0A0A0', fg='#000000', **btn_config).pack(side='left', padx=2)
        
        row4 = tk.Frame(commands_frame, bg='#D3D3D3')
        row4.pack(fill='x', pady=2)
        tk.Button(row4, text="Logical Acquisition", command=self.collect_logical,
                 bg='#A0A0A0', fg='#000000', **btn_config).pack(side='left', padx=2)
        tk.Button(row4, text="Create Hashes", command=self.create_hashes,
                 bg='#A0A0A0', fg='#000000', **btn_config).pack(side='left', padx=2)
        
        ttk.Separator(commands_frame, orient='horizontal').pack(fill='x', pady=10)
        
        tk.Button(commands_frame, text="🚀 Execute All Steps", 
                 command=self.run_all_response,
                 bg='#505050', fg='black', font=('Helvetica', 11, 'bold'),
                 width=72, pady=10, relief=tk.RAISED, bd=3).pack(pady=5)
        
        log_frame = tk.LabelFrame(self.tab3, text=" Terminal Output ", 
                                 font=('Helvetica', 11, 'bold'),
                                 bg='#D3D3D3', fg='#1a1a1a', padx=15, pady=10)
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.response_log = scrolledtext.ScrolledText(log_frame, height=12, 
                                                      bg='#F5F5F5', fg='#000000',
                                                      font=('Courier', 9),
                                                      relief=tk.SUNKEN, bd=2)
        self.response_log.pack(fill='both', expand=True)
        
    def scan_output_usb(self):
        self.log_response("Scanning USB devices...")
        try:
            result = subprocess.run(['ls', '/Volumes'], capture_output=True, text=True)
            volumes = [v for v in result.stdout.strip().split('\n') 
                      if v and v != 'Macintosh HD']
            
            self.output_combo['values'] = volumes
            
            if volumes:
                self.output_combo.current(0)
                self.log_response(f"✓ {len(volumes)} Volume(s) found")
            else:
                self.log_response("⚠ No external volumes found")
        except Exception as e:
            self.log_response(f"✗ Error: {str(e)}")
            
    def get_output_path(self):
        usb = self.output_usb.get()
        if not usb:
            messagebox.showerror("Error", "Please select an output USB medium first")
            return None
        return f"/Volumes/{usb}"
        
    def run_command(self, cmd, output_file, description):
        output_path = self.get_output_path()
        if not output_path:
            return
            
        self.log_response(f"Executing: {description}...")
        
        def execute():
            try:
                full_path = f"{output_path}/{output_file}"
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                
                with open(full_path, 'w') as f:
                    f.write(result.stdout)
                    if result.stderr:
                        f.write(f"\n\n--- STDERR ---\n{result.stderr}")
                
                self.log_response(f"✓ {description} → {output_file}")
            except Exception as e:
                self.log_response(f"✗ Error in {description}: {str(e)}")
                
        threading.Thread(target=execute, daemon=True).start()
        
    def collect_system_info(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_command("system_profiler", f"{timestamp}_system.txt", "System Profiler")
        self.run_command("system_profiler SPHardwareDataType", f"{timestamp}_hardware.txt", "Hardware Details")
        self.run_command("nvram -xp", f"{timestamp}_nvram.txt", "NVRAM")
        self.run_command("kextstat", f"{timestamp}_kextstat.txt", "Kernel Extensions")
        
    def collect_filevault(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_command("sudo fdesetup status", f"{timestamp}_fv.txt", "FileVault Status")
        self.run_command("diskutil apfs list", f"{timestamp}_apfs.txt", "APFS Container")
        self.run_command("sudo fdesetup list", f"{timestamp}_fv_users.txt", "FileVault Users")
        
    def collect_processes(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_command("ps aux", f"{timestamp}_processes.txt", "Process List")
        self.run_command("launchctl list", f"{timestamp}_services.txt", "Services")
        self.run_command("lsof", f"{timestamp}_open_files.txt", "Open Files")
        self.run_command("lsof -i", f"{timestamp}_network_connections.txt", "Network Connections")
        
    def collect_network(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_command("netstat -an", f"{timestamp}_netstat.txt", "Network Status")
        self.run_command("netstat -r", f"{timestamp}_routing.txt", "Routing Table")
        self.run_command("sharing -l", f"{timestamp}_sharing.txt", "Sharing Services")
        
    def collect_users(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_command("who", f"{timestamp}_active_users.txt", "Active Users")
        self.run_command("last", f"{timestamp}_login_history.txt", "Login History")
        
        output_path = self.get_output_path()
        if not output_path:
            return
            
        self.log_response("Collecting shell histories...")
        
        def collect_history():
            try:
                histories = []
                for user_dir in Path('/Users').iterdir():
                    if user_dir.is_dir():
                        for history_file in ['.zsh_history', '.bash_history']:
                            hist_path = user_dir / history_file
                            if hist_path.exists():
                                try:
                                    with open(hist_path, 'r', errors='ignore') as f:
                                        histories.append(f"=== {user_dir.name} {history_file} ===\n")
                                        histories.append(f.read() + "\n\n")
                                except:
                                    pass
                
                with open(f"{output_path}/{timestamp}_shell_history.txt", 'w') as f:
                    f.write(''.join(histories))
                    
                self.log_response(f"✓ Shell Histories → {timestamp}_shell_history.txt")
            except Exception as e:
                self.log_response(f"✗ Shell history error: {str(e)}")
                
        threading.Thread(target=collect_history, daemon=True).start()
        
    def collect_logs(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_path = self.get_output_path()
        if not output_path:
            return
            
        self.log_response("Copying system.log...")
        
        def copy_log():
            try:
                subprocess.run(['cp', '/var/log/system.log', f"{output_path}/{timestamp}_system.log"],
                             capture_output=True)
                self.log_response(f"✓ system.log copied")
            except Exception as e:
                self.log_response(f"✗ Error: {str(e)}")
                
        threading.Thread(target=copy_log, daemon=True).start()
        
        self.run_command("log show --last 24h", f"{timestamp}_unified_logs_24h.txt", "Unified Logs (24h)")
        self.run_command('log show --predicate \'subsystem == "com.apple.security"\' --last 24h',
                        f"{timestamp}_security_logs.txt", "Security Logs")
        
    def collect_logical(self):
        output_path = self.get_output_path()
        if not output_path:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Logical Acquisition - Select Directory")
        dialog.geometry("600x450")
        dialog.configure(bg='#E8E8E8')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Select the directory to acquire:", 
                font=('Helvetica', 12, 'bold'), bg='#E8E8E8', fg='#1a1a1a').pack(pady=10)
        
        frame = tk.Frame(dialog, bg='#D3D3D3', padx=15, pady=15)
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        listbox = tk.Listbox(frame, font=('Helvetica', 10), bg='white', fg='black',
                            selectmode=tk.SINGLE, height=15)
        listbox.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side='right', fill='y')
        listbox.config(yscrollcommand=scrollbar.set)
        
        directories = {
            "Complete /Users Directory": "/Users/",
            "Documents Only": "/Users/*/Documents/",
            "Desktop Only": "/Users/*/Desktop/",
            "Downloads Only": "/Users/*/Downloads/",
            "Mail & Messages": "/Users/*/Library/Mail/ /Users/*/Library/Messages/",
            "Safari History & Cache": "/Users/*/Library/Safari/",
            "Chrome Profile": "/Users/*/Library/Application\\ Support/Google/Chrome/",
            "Firefox Profile": "/Users/*/Library/Application\\ Support/Firefox/",
            "Complete /Users/*/Library": "/Users/*/Library/",
            "All User Home Directories": "/Users/*/"
        }
        
        for name in directories.keys():
            listbox.insert(tk.END, name)
        
        listbox.selection_set(0)
        
        selected_dir = tk.StringVar()
        
        info_label = tk.Label(dialog, text="", font=('Helvetica', 9, 'italic'),
                             bg='#E8E8E8', fg='#505050', wraplength=550)
        info_label.pack(pady=5)
        
        def update_info(event=None):
            selection = listbox.curselection()
            if selection:
                name = listbox.get(selection[0])
                path = directories[name]
                info_label.config(text=f"Path: {path}")
        
        listbox.bind('<<ListboxSelect>>', update_info)
        update_info()
        
        button_frame = tk.Frame(dialog, bg='#E8E8E8')
        button_frame.pack(pady=10)
        
        def on_ok():
            selection = listbox.curselection()
            if selection:
                name = listbox.get(selection[0])
                selected_dir.set(directories[name])
                dialog.destroy()
                start_acquisition(selected_dir.get(), name)
            else:
                messagebox.showwarning("Selection Required", "Please select a directory")
        
        def on_cancel():
            dialog.destroy()
        
        tk.Button(button_frame, text="Start Acquisition", command=on_ok,
                 bg='#505050', fg='black', font=('Helvetica', 10, 'bold'),
                 padx=20, pady=8).pack(side='left', padx=5)
        
        tk.Button(button_frame, text="Cancel", command=on_cancel,
                 bg='#808080', fg='black', font=('Helvetica', 10),
                 padx=20, pady=8).pack(side='left', padx=5)
        
        def start_acquisition(path, name):
            self.log_response(f"Starting logical acquisition: {name}...")
            
            def acquire():
                try:
                    safe_name = name.replace(" ", "_").replace("/", "_")
                    tar_file = f"{output_path}/{timestamp}_{safe_name}.tar.gz"
                    cmd = f'tar czf "{tar_file}" {path} 2>&1'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.log_response(f"✓ Archived → {timestamp}_{safe_name}.tar.gz")
                    else:
                        self.log_response(f"⚠ Warning: {result.stderr[:200]}")
                        
                except Exception as e:
                    self.log_response(f"✗ Error: {str(e)}")
                    
            threading.Thread(target=acquire, daemon=True).start()
        
    def create_hashes(self):
        output_path = self.get_output_path()
        if not output_path:
            return
            
        self.log_response("Creating SHA-256 hashes...")
        
        def hash_files():
            try:
                cmd = f"cd {output_path} && shasum -a 256 *.txt *.tar.gz 2>/dev/null > checksums.txt"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log_response("✓ Hashes created → checksums.txt")
                else:
                    self.log_response("⚠ No files found to hash")
                    
            except Exception as e:
                self.log_response(f"✗ Error: {str(e)}")
                
        threading.Thread(target=hash_files, daemon=True).start()
        
    def run_all_response(self):
        if not self.output_usb.get():
            messagebox.showerror("Error", "Please select an output USB medium first")
            return
            
        self.log_response("=" * 50)
        self.log_response("Starting complete live response collection")
        self.log_response("=" * 50)
        
        import time
        
        def run_all():
            self.collect_system_info()
            time.sleep(2)
            self.collect_filevault()
            time.sleep(2)
            self.collect_processes()
            time.sleep(2)
            self.collect_network()
            time.sleep(2)
            self.collect_users()
            time.sleep(2)
            self.collect_logs()
            time.sleep(5)
            self.create_hashes()
            time.sleep(2)
            self.log_response("=" * 50)
            self.log_response("✓ Collection completed")
            self.log_response("=" * 50)
            
        threading.Thread(target=run_all, daemon=True).start()

def main():
    root = tk.Tk()
    app = ForensicUSBTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
