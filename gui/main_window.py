# gui/main_window.py - 主窗口

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from config.templates import get_template_list, get_template_config, get_template_display_name
from core.processor import PSDProcessor

class MainWindow:
    def __init__(self, root, license_manager):
        self.root = root
        self.license_manager = license_manager
        
        self.root.title("PSD印花处理工具 v1.0")
        self.root.geometry("700x500")
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """设置主界面"""
        # 创建菜单
        self.create_menu()
        
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 模板选择区域
        template_frame = tk.LabelFrame(main_frame, text="模板选择", font=("Arial", 10, "bold"))
        template_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(template_frame, text="选择服装类型:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        self.template_var = tk.StringVar()
        template_combo = ttk.Combobox(template_frame, textvariable=self.template_var, 
                                     values=[get_template_display_name(t) for t in get_template_list()],
                                     state="readonly", width=30)
        template_combo.grid(row=0, column=1, padx=10, pady=10)
        template_combo.current(0)  # 默认选择第一个
        
        # 路径配置区域
        path_frame = tk.LabelFrame(main_frame, text="路径配置", font=("Arial", 10, "bold"))
        path_frame.pack(fill="x", pady=(0, 15))
        
        # PSD模板目录
        tk.Label(path_frame, text="PSD模板目录:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.template_dir_var = tk.StringVar()
        tk.Entry(path_frame, textvariable=self.template_dir_var, width=50).grid(row=0, column=1, padx=10, pady=8)
        tk.Button(path_frame, text="浏览", command=self.browse_template_dir).grid(row=0, column=2, padx=10, pady=8)
        
        # 印花图案目录
        tk.Label(path_frame, text="印花图案目录:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.pattern_dir_var = tk.StringVar()
        tk.Entry(path_frame, textvariable=self.pattern_dir_var, width=50).grid(row=1, column=1, padx=10, pady=8)
        tk.Button(path_frame, text="浏览", command=self.browse_pattern_dir).grid(row=1, column=2, padx=10, pady=8)
        
        # 输出目录
        tk.Label(path_frame, text="输出目录:").grid(row=2, column=0, sticky="w", padx=10, pady=8)
        self.output_dir_var = tk.StringVar(value="output")
        tk.Entry(path_frame, textvariable=self.output_dir_var, width=50).grid(row=2, column=1, padx=10, pady=8)
        tk.Button(path_frame, text="浏览", command=self.browse_output_dir).grid(row=2, column=2, padx=10, pady=8)
        
        # 处理控制区域
        control_frame = tk.LabelFrame(main_frame, text="处理控制", font=("Arial", 10, "bold"))
        control_frame.pack(fill="both", expand=True)
        
        # 状态和进度
        status_frame = tk.Frame(control_frame)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        self.status_var = tk.StringVar(value="就绪")
        tk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10)).pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=5)
        
        # 日志区域
        tk.Label(control_frame, text="处理日志:", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(10, 0))
        
        log_frame = tk.Frame(control_frame)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, font=("Consolas", 9))
        log_scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        # 处理按钮
        self.process_button = tk.Button(control_frame, text="开始处理", command=self.start_processing,
                                       bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.process_button.pack(pady=15)
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存设置", command=self.save_settings)
        file_menu.add_command(label="加载设置", command=self.load_settings)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="许可证信息", command=self.show_license_info)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def browse_template_dir(self):
        """浏览PSD模板目录"""
        directory = filedialog.askdirectory(title="选择PSD模板目录")
        if directory:
            self.template_dir_var.set(directory)
    
    def browse_pattern_dir(self):
        """浏览印花图案目录"""
        directory = filedialog.askdirectory(title="选择印花图案目录")
        if directory:
            self.pattern_dir_var.set(directory)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def get_selected_template_config(self):
        """获取当前选择的模板配置"""
        display_name = self.template_var.get()
        # 根据显示名称找到对应的模板键
        for template_key in get_template_list():
            if get_template_display_name(template_key) == display_name:
                return get_template_config(template_key)
        return None
    
    def start_processing(self):
        """开始处理"""
        # 验证输入
        if not self.template_dir_var.get():
            messagebox.showerror("错误", "请选择PSD模板目录")
            return
        
        if not self.pattern_dir_var.get():
            messagebox.showerror("错误", "请选择印花图案目录")
            return
        
        if not os.path.exists(self.template_dir_var.get()):
            messagebox.showerror("错误", "PSD模板目录不存在")
            return
        
        if not os.path.exists(self.pattern_dir_var.get()):
            messagebox.showerror("错误", "印花图案目录不存在")
            return
        
        # 获取模板配置
        template_config = self.get_selected_template_config()
        if not template_config:
            messagebox.showerror("错误", "无效的模板配置")
            return
        
        # 检查印花文件是否存在
        pattern_dir = self.pattern_dir_var.get()
        missing_files = []
        for pattern_file in template_config['pattern_files']:
            if not os.path.exists(os.path.join(pattern_dir, pattern_file)):
                missing_files.append(pattern_file)
        
        if missing_files:
            messagebox.showwarning("警告", f"以下印花文件不存在:\n{', '.join(missing_files)}\n\n将跳过相应的图层处理")
        
        # 禁用处理按钮
        self.process_button.config(state="disabled", text="处理中...")
        self.progress_bar.start()
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("开始处理...")
        
        # 在新线程中处理
        thread = threading.Thread(target=self.process_files, args=(template_config,))
        thread.daemon = True
        thread.start()
    
    def process_files(self, template_config):
        """处理文件（在单独线程中运行）"""
        try:
            # 创建处理器
            processor = PSDProcessor(template_config, self.log_message)
            
            # 执行批量处理
            success_count, total_count = processor.process_directory(
                self.template_dir_var.get(),
                self.pattern_dir_var.get(),
                self.output_dir_var.get()
            )
            
            # 更新状态
            self.root.after(0, lambda: self.status_var.set(f"处理完成 - 成功: {success_count}/{total_count}"))
            
            if success_count > 0:
                self.root.after(0, lambda: messagebox.showinfo("完成", f"处理完成！\n成功: {success_count}/{total_count}"))
            else:
                self.root.after(0, lambda: messagebox.showerror("失败", "没有文件处理成功，请检查配置和文件"))
        
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"处理过程中发生严重错误: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("处理失败"))
        
        finally:
            # 重新启用处理按钮
            self.root.after(0, lambda: (
                self.process_button.config(state="normal", text="开始处理"),
                self.progress_bar.stop()
            ))
    
    def save_settings(self):
        """保存设置"""
        try:
            import json
            settings = {
                'template_dir': self.template_dir_var.get(),
                'pattern_dir': self.pattern_dir_var.get(),
                'output_dir': self.output_dir_var.get(),
                'selected_template': self.template_var.get()
            }
            
            os.makedirs('data', exist_ok=True)
            with open('data/settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", "设置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")
    
    def load_settings(self):
        """加载设置"""
        try:
            import json
            settings_file = 'data/settings.json'
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                self.template_dir_var.set(settings.get('template_dir', ''))
                self.pattern_dir_var.set(settings.get('pattern_dir', ''))
                self.output_dir_var.set(settings.get('output_dir', 'output'))
                
                # 设置模板选择
                selected_template = settings.get('selected_template', '')
                if selected_template:
                    self.template_var.set(selected_template)
        except Exception as e:
            self.log_message(f"加载设置失败: {str(e)}")
    
    def show_license_info(self):
        """显示许可证信息"""
        is_valid, message = self.license_manager.check_license_validity()
        status = "有效" if is_valid else "无效"
        
        info = f"许可证状态: {status}\n详细信息: {message}\n\n机器码: {self.license_manager.get_machine_code()}"
        messagebox.showinfo("许可证信息", info)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """PSD印花处理工具 v1.0

功能特性:
• 批量处理PSD文件
• 多种服装模板支持
• 自动印花图案应用
• 尺码标签添加
• 图层旋转处理

技术支持:
请联系软件提供商获取技术支持
        """
        messagebox.showinfo("关于", about_text)