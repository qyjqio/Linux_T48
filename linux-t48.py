#!/usr/bin/env python3
"""Linux_T48编程器 by：车机研究所_草软"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading


class MiniProGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux_T48编程器 by：车机研究所_草软")
        self.root.geometry("960x780")
        self.root.minsize(900, 700)

        self.chip_name = tk.StringVar()
        self.file_path = tk.StringVar()
        self.chip_list = []
        self.process = None

        # 选项变量
        self.spi_clock = tk.StringVar(value="默认")
        self.file_format = tk.StringVar(value="bin")
        self.mem_type = tk.StringVar(value="auto")
        self.skip_erase = tk.BooleanVar(value=False)
        self.skip_verify = tk.BooleanVar(value=False)
        self.skip_id = tk.BooleanVar(value=False)
        self.no_id_error = tk.BooleanVar(value=False)
        self.no_size_error = tk.BooleanVar(value=False)
        self.icsp = tk.StringVar(value="off")

        self._build_ui()
        self._detect_programmer()

    def _build_ui(self):
        # 使用 Notebook 分页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ===== 主页面 =====
        main_page = ttk.Frame(notebook)
        notebook.add(main_page, text=" 主操作 ")

        # ===== 设置页面 =====
        settings_page = ttk.Frame(notebook)
        notebook.add(settings_page, text=" 高级设置 ")

        self._build_main_page(main_page)
        self._build_settings_page(settings_page)

    def _build_main_page(self, parent):
        # -- 编程器状态 --
        status_frame = ttk.LabelFrame(parent, text="编程器状态", padding=6)
        status_frame.pack(fill=tk.X, padx=8, pady=(8, 4))

        self.status_label = ttk.Label(status_frame, text="正在检测...", font=("", 11))
        self.status_label.pack(side=tk.LEFT)
        ttk.Button(status_frame, text="刷新", command=self._detect_programmer).pack(side=tk.RIGHT)
        ttk.Button(status_frame, text="硬件自检", command=self._hw_check).pack(side=tk.RIGHT, padx=5)

        # -- 芯片选择 --
        chip_frame = ttk.LabelFrame(parent, text="芯片选择", padding=6)
        chip_frame.pack(fill=tk.X, padx=8, pady=4)

        row1 = ttk.Frame(chip_frame)
        row1.pack(fill=tk.X)

        ttk.Label(row1, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._filter_chips)
        ttk.Entry(row1, textvariable=self.search_var, width=25).pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(row1, text="已选:").pack(side=tk.LEFT)
        self.chip_entry = ttk.Entry(row1, textvariable=self.chip_name, width=28,
                                     font=("", 11, "bold"), foreground="blue")
        self.chip_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(row1, text="芯片信息", command=self._chip_info).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1, text="读取ID", command=self._read_id).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1, text="自动检测", command=self._auto_detect).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1, text="引脚检测", command=self._pin_check).pack(side=tk.LEFT, padx=3)

        # SPI 时钟
        row2 = ttk.Frame(chip_frame)
        row2.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(row2, text="SPI时钟:").pack(side=tk.LEFT)
        for val in ["默认", "4 MHz", "8 MHz", "15 MHz", "30 MHz"]:
            ttk.Radiobutton(row2, text=val, variable=self.spi_clock, value=val).pack(side=tk.LEFT, padx=3)

        # 芯片列表
        list_frame = ttk.Frame(chip_frame)
        list_frame.pack(fill=tk.X, pady=(4, 0))
        self.chip_listbox = tk.Listbox(list_frame, height=5, font=("Monospace", 10))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.chip_listbox.yview)
        self.chip_listbox.configure(yscrollcommand=scrollbar.set)
        self.chip_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chip_listbox.bind("<<ListboxSelect>>", self._on_chip_select)
        self.chip_listbox.bind("<Double-Button-1>", self._on_chip_select)

        self.chip_count_label = ttk.Label(chip_frame, text="")
        self.chip_count_label.pack(anchor=tk.W)

        # -- 文件选择 --
        file_frame = ttk.LabelFrame(parent, text="文件", padding=6)
        file_frame.pack(fill=tk.X, padx=8, pady=4)

        ttk.Entry(file_frame, textvariable=self.file_path, width=55).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="打开", command=self._browse_open).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Button(file_frame, text="另存为", command=self._browse_save).pack(side=tk.LEFT, padx=2)

        # -- 操作按钮 --
        btn_frame = ttk.LabelFrame(parent, text="操作", padding=6)
        btn_frame.pack(fill=tk.X, padx=8, pady=4)

        buttons = [
            ("读取芯片", self._read_chip, "#4CAF50"),
            ("写入芯片", self._write_chip, "#2196F3"),
            ("校验", self._verify_chip, "#FF9800"),
            ("擦除", self._erase_chip, "#f44336"),
            ("空白检查", self._blank_check, "#795548"),
            ("读保护位", self._read_fuses, "#9C27B0"),
            ("写保护位", self._write_fuses, "#E91E63"),
            ("去保护", self._remove_protect, "#607D8B"),
            ("加保护", self._add_protect, "#455A64"),
        ]

        for i, (text, cmd, color) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, command=cmd, font=("", 10, "bold"),
                          bg=color, fg="white", relief=tk.RAISED, padx=10, pady=4)
            btn.grid(row=i // 5, column=i % 5, padx=3, pady=2, sticky="ew")
        for i in range(5):
            btn_frame.columnconfigure(i, weight=1)

        # -- 进度条 --
        self.progress = ttk.Progressbar(parent, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=8, pady=4)

        # -- 输出日志 --
        log_frame = ttk.LabelFrame(parent, text="输出日志 (右键清除)", padding=4)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        self.log_text = scrolledtext.ScrolledText(log_frame, font=("Monospace", 10),
                                                   bg="#1e1e1e", fg="#00ff00",
                                                   insertbackground="white", height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.bind("<Button-3>", lambda e: self.log_text.delete("1.0", tk.END))

    def _build_settings_page(self, parent):
        # -- 文件格式 --
        fmt_frame = ttk.LabelFrame(parent, text="文件格式", padding=8)
        fmt_frame.pack(fill=tk.X, padx=8, pady=(8, 4))

        for val, label in [("bin", "RAW 二进制"), ("ihex", "Intel HEX"), ("srec", "Motorola SREC")]:
            ttk.Radiobutton(fmt_frame, text=label, variable=self.file_format, value=val).pack(side=tk.LEFT, padx=8)

        # -- 存储区域 --
        mem_frame = ttk.LabelFrame(parent, text="存储区域", padding=8)
        mem_frame.pack(fill=tk.X, padx=8, pady=4)

        for val, label in [("auto", "自动"), ("code", "Code"), ("data", "Data/EEPROM"),
                           ("config", "Config/Fuses"), ("user", "User"), ("calibration", "Calibration")]:
            ttk.Radiobutton(mem_frame, text=label, variable=self.mem_type, value=val).pack(side=tk.LEFT, padx=6)

        # -- 写入选项 --
        write_frame = ttk.LabelFrame(parent, text="写入选项", padding=8)
        write_frame.pack(fill=tk.X, padx=8, pady=4)

        ttk.Checkbutton(write_frame, text="跳过擦除 (写入前不擦除)", variable=self.skip_erase).pack(anchor=tk.W)
        ttk.Checkbutton(write_frame, text="跳过校验 (写入后不校验)", variable=self.skip_verify).pack(anchor=tk.W)
        ttk.Checkbutton(write_frame, text="跳过ID检查 (不读取芯片ID)", variable=self.skip_id).pack(anchor=tk.W)
        ttk.Checkbutton(write_frame, text="ID不匹配时不报错 (仅警告)", variable=self.no_id_error).pack(anchor=tk.W)
        ttk.Checkbutton(write_frame, text="文件大小不匹配时不报错", variable=self.no_size_error).pack(anchor=tk.W)

        # -- ICSP 模式 --
        icsp_frame = ttk.LabelFrame(parent, text="ICSP 在线编程", padding=8)
        icsp_frame.pack(fill=tk.X, padx=8, pady=4)

        for val, label in [("off", "关闭"), ("vcc", "ICSP (供电)"), ("no_vcc", "ICSP (不供电)")]:
            ttk.Radiobutton(icsp_frame, text=label, variable=self.icsp, value=val).pack(side=tk.LEFT, padx=8)

        # -- 电压设置 --
        volt_frame = ttk.LabelFrame(parent, text="电压设置 (留空=默认)", padding=8)
        volt_frame.pack(fill=tk.X, padx=8, pady=4)

        row = ttk.Frame(volt_frame)
        row.pack(fill=tk.X)

        ttk.Label(row, text="VPP 编程电压:").pack(side=tk.LEFT)
        self.vpp_var = tk.StringVar()
        ttk.Combobox(row, textvariable=self.vpp_var, width=8,
                     values=["", "9", "9.5", "10", "11", "11.5", "12", "12.5", "13",
                             "13.5", "14", "14.5", "15.5", "16", "16.5", "17", "18", "21", "25"]).pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(row, text="VDD 写入电压:").pack(side=tk.LEFT)
        self.vdd_var = tk.StringVar()
        ttk.Combobox(row, textvariable=self.vdd_var, width=8,
                     values=["", "3.3", "4", "4.5", "5", "5.5", "6.5"]).pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(row, text="VCC 校验电压:").pack(side=tk.LEFT)
        self.vcc_var = tk.StringVar()
        ttk.Combobox(row, textvariable=self.vcc_var, width=8,
                     values=["", "1.8", "2.5", "3.3", "4", "4.5", "5", "5.5", "6.5"]).pack(side=tk.LEFT, padx=5)

        # -- 固件更新 --
        fw_frame = ttk.LabelFrame(parent, text="固件管理", padding=8)
        fw_frame.pack(fill=tk.X, padx=8, pady=4)

        ttk.Button(fw_frame, text="更新编程器固件", command=self._update_firmware).pack(side=tk.LEFT, padx=5)
        ttk.Button(fw_frame, text="逻辑IC测试", command=self._logic_test).pack(side=tk.LEFT, padx=5)

    # ===== 工具方法 =====

    def _log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def _extra_args(self):
        """根据设置页面构建额外参数"""
        args = []
        # SPI 时钟
        val = self.spi_clock.get()
        if val != "默认":
            args += ["-o", f"spi_clock={val.split()[0]}"]
        # 文件格式
        if self.file_format.get() != "bin":
            args += ["-f", self.file_format.get()]
        # 存储区域
        if self.mem_type.get() != "auto":
            args += ["-c", self.mem_type.get()]
        # 写入选项
        if self.skip_erase.get():
            args.append("-e")
        if self.skip_verify.get():
            args.append("-v")
        if self.skip_id.get():
            args.append("-x")
        if self.no_id_error.get():
            args.append("-y")
        if self.no_size_error.get():
            args.append("-s")
        # ICSP
        if self.icsp.get() == "vcc":
            args.append("-i")
        elif self.icsp.get() == "no_vcc":
            args.append("-I")
        # 电压
        if self.vpp_var.get():
            args += ["-o", f"vpp={self.vpp_var.get()}"]
        if self.vdd_var.get():
            args += ["-o", f"vdd={self.vdd_var.get()}"]
        if self.vcc_var.get():
            args += ["-o", f"vcc={self.vcc_var.get()}"]
        return args

    def _run_cmd(self, args, callback=None):
        def _worker():
            self.progress.start(10)
            cmd = ["minipro"] + args
            self._log(f"$ {' '.join(cmd)}")
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                self.process = proc
                output = ""
                for line in proc.stdout:
                    output += line
                    self.root.after(0, self._log, line.rstrip())
                proc.wait()
                if proc.returncode == 0:
                    self.root.after(0, self._log, ">>> 操作成功!")
                else:
                    self.root.after(0, self._log, f">>> 操作失败 (返回码: {proc.returncode})")
                if callback:
                    self.root.after(0, callback, output)
            except Exception as e:
                self.root.after(0, self._log, f">>> 错误: {e}")
            finally:
                self.process = None
                self.root.after(0, self.progress.stop)
        threading.Thread(target=_worker, daemon=True).start()

    def _detect_programmer(self):
        def on_done(output):
            if "Found" in output:
                for line in output.split('\n'):
                    if "Found" in line:
                        self.status_label.config(text=f"[OK] {line.strip()}", foreground="green")
                        break
            else:
                self.status_label.config(text="[X] 未检测到编程器", foreground="red")
        self._run_cmd(["--version"], on_done)
        self._load_chip_list()

    def _load_chip_list(self):
        def _worker():
            try:
                result = subprocess.run(["minipro", "-l"], capture_output=True, text=True, timeout=30)
                output = result.stdout + result.stderr
                chips = []
                skip_kw = ["Found", "Warning", "Device code", "Serial code",
                           "Manufactured", "USB speed", "Supply voltage"]
                for line in output.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    if any(kw in line for kw in skip_kw):
                        continue
                    chips.append(line)
                self.chip_list = chips
                self.root.after(0, self._update_chip_listbox, chips[:500])
                self.root.after(0, self._log, f"已加载 {len(chips)} 种芯片")
                self.root.after(0, lambda: self.chip_count_label.config(
                    text=f"共 {len(chips)} 种芯片，显示前 500 条（输入关键词过滤）"))
            except Exception as e:
                self.root.after(0, self._log, f"加载芯片列表失败: {e}")
        threading.Thread(target=_worker, daemon=True).start()

    def _update_chip_listbox(self, chips):
        self.chip_listbox.delete(0, tk.END)
        for c in chips:
            self.chip_listbox.insert(tk.END, c)

    def _filter_chips(self, *args):
        keyword = self.search_var.get().strip().upper()
        if not keyword:
            filtered = self.chip_list[:500]
        else:
            filtered = [c for c in self.chip_list if keyword in c.upper()]
        self._update_chip_listbox(filtered[:500])
        self.chip_count_label.config(text=f"匹配 {min(len(filtered), len(self.chip_list))} 条，显示 {min(500, len(filtered))} 条")

    def _on_chip_select(self, event):
        sel = self.chip_listbox.curselection()
        if sel:
            chip = self.chip_listbox.get(sel[0]).strip()
            self.chip_name.set(chip)
            self._log(f"已选择芯片: {chip}")

    def _check_chip(self):
        if not self.chip_name.get():
            messagebox.showwarning("提示", "请先选择芯片型号")
            return False
        return True

    def _check_file(self):
        if not self.file_path.get():
            messagebox.showwarning("提示", "请先选择文件")
            return False
        return True

    def _browse_open(self):
        f = filedialog.askopenfilename(
            title="打开固件文件",
            filetypes=[("二进制文件", "*.bin"), ("HEX文件", "*.hex"), ("SREC文件", "*.srec *.s19"),
                       ("所有文件", "*.*")])
        if f:
            self.file_path.set(f)

    def _browse_save(self):
        ext = ".hex" if self.file_format.get() == "ihex" else ".srec" if self.file_format.get() == "srec" else ".bin"
        f = filedialog.asksaveasfilename(
            title="保存固件文件", defaultextension=ext,
            filetypes=[("二进制文件", "*.bin"), ("HEX文件", "*.hex"), ("SREC文件", "*.srec"), ("所有文件", "*.*")])
        if f:
            self.file_path.set(f)

    # ===== 操作方法 =====

    def _chip_info(self):
        if self._check_chip():
            self._run_cmd(["-d", self.chip_name.get()])

    def _read_id(self):
        if self._check_chip():
            self._run_cmd(["-p", self.chip_name.get(), "-D"] + self._extra_args())

    def _auto_detect(self):
        self._run_cmd(["-p", "W25Q64BV@SOIC8", "-a", "8"] + self._extra_args())

    def _pin_check(self):
        if self._check_chip():
            self._run_cmd(["-p", self.chip_name.get(), "-z"])

    def _hw_check(self):
        self._run_cmd(["-t"])

    def _read_chip(self):
        if self._check_chip():
            if not self.file_path.get():
                self._browse_save()
            if self.file_path.get():
                self._run_cmd(["-p", self.chip_name.get(), "-r", self.file_path.get()] + self._extra_args())

    def _write_chip(self):
        if self._check_chip() and self._check_file():
            if messagebox.askyesno("确认写入", f"写入 {self.file_path.get()}\n到 {self.chip_name.get()} ?"):
                self._run_cmd(["-p", self.chip_name.get(), "-w", self.file_path.get()] + self._extra_args())

    def _verify_chip(self):
        if self._check_chip() and self._check_file():
            self._run_cmd(["-p", self.chip_name.get(), "-m", self.file_path.get()] + self._extra_args())

    def _erase_chip(self):
        if self._check_chip():
            if messagebox.askyesno("确认擦除", f"擦除 {self.chip_name.get()} ?\n此操作不可恢复！"):
                self._run_cmd(["-p", self.chip_name.get(), "-E"] + self._extra_args())

    def _blank_check(self):
        if self._check_chip():
            self._run_cmd(["-p", self.chip_name.get(), "-b"] + self._extra_args())

    def _read_fuses(self):
        if self._check_chip():
            if not self.file_path.get():
                self._browse_save()
            if self.file_path.get():
                self._run_cmd(["-p", self.chip_name.get(), "-r", self.file_path.get(), "-c", "config"] + self._extra_args())

    def _write_fuses(self):
        if self._check_chip() and self._check_file():
            if messagebox.askyesno("确认", f"写入保护位到 {self.chip_name.get()} ?"):
                self._run_cmd(["-p", self.chip_name.get(), "-w", self.file_path.get(), "-c", "config"] + self._extra_args())

    def _remove_protect(self):
        if self._check_chip():
            if messagebox.askyesno("确认", "移除芯片保护?"):
                self._run_cmd(["-p", self.chip_name.get(), "-u"] + self._extra_args())

    def _add_protect(self):
        if self._check_chip():
            if messagebox.askyesno("确认", "启用芯片保护?"):
                self._run_cmd(["-p", self.chip_name.get(), "-P"] + self._extra_args())

    def _logic_test(self):
        if self._check_chip():
            self._run_cmd(["-p", self.chip_name.get(), "-T"] + self._extra_args())

    def _update_firmware(self):
        f = filedialog.askopenfilename(title="选择固件文件", filetypes=[("固件文件", "*.dat *.Dat"), ("所有文件", "*.*")])
        if f:
            if messagebox.askyesno("确认固件更新", f"确定要更新编程器固件?\n文件: {f}\n\n操作有风险，请确保不要断电！"):
                self._run_cmd(["-F", f])


if __name__ == "__main__":
    root = tk.Tk()
    app = MiniProGUI(root)
    root.mainloop()
