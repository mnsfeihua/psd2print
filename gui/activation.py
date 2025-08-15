# gui/activation.py - 激活对话框

import tkinter as tk
from tkinter import messagebox

class ActivationDialog:
    def __init__(self, parent, license_manager):
        self.parent = parent
        self.license_manager = license_manager
        self.result = False
        
        self.window = tk.Toplevel(parent)
        self.window.title("软件激活")
        self.window.geometry("450x400")
        self.window.resizable(False, False)
        
        # 居中显示
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        # 标题
        title_label = tk.Label(self.window, text="PSD印花处理工具", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # 机器码区域
        machine_frame = tk.LabelFrame(self.window, text="机器码", font=("Arial", 10, "bold"))
        machine_frame.pack(fill="x", padx=20, pady=10)
        
        machine_code = self.license_manager.get_machine_code()
        
        code_frame = tk.Frame(machine_frame)
        code_frame.pack(fill="x", padx=10, pady=10)
        
        self.machine_entry = tk.Entry(code_frame, font=("Courier", 12), state="readonly")
        self.machine_entry.pack(side="left", fill="x", expand=True)
        self.machine_entry.config(state="normal")
        self.machine_entry.insert(0, machine_code)
        self.machine_entry.config(state="readonly")
        
        copy_btn = tk.Button(code_frame, text="复制", command=self.copy_machine_code)
        copy_btn.pack(side="right", padx=(5, 0))
        
        # 激活码区域
        activation_frame = tk.LabelFrame(self.window, text="激活码", font=("Arial", 10, "bold"))
        activation_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.activation_text = tk.Text(activation_frame, height=5, font=("Courier", 10))
        self.activation_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 按钮区域
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(button_frame, text="激活", command=self.activate,
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="right", padx=(5, 0))
        tk.Button(button_frame, text="退出", command=self.close_app).pack(side="right")
        
        # 提示信息
        hint_label = tk.Label(self.window, text="请将机器码发送给软件提供商获取激活码", 
                             fg="gray", font=("Arial", 9))
        hint_label.pack(pady=5)
    
    def copy_machine_code(self):
        """复制机器码"""
        machine_code = self.machine_entry.get()
        self.window.clipboard_clear()
        self.window.clipboard_append(machine_code)
        messagebox.showinfo("提示", "机器码已复制到剪贴板")
    
    def activate(self):
        """执行激活"""
        activation_code = self.activation_text.get("1.0", "end-1c").strip()
        if not activation_code:
            messagebox.showerror("错误", "请输入激活码")
            return
        
        # 移除所有空格和换行符
        activation_code = ''.join(activation_code.split())
        
        is_success, message = self.license_manager.activate(activation_code)
        if is_success:
            messagebox.showinfo("激活成功", message)
            self.result = True
            self.window.destroy()
        else:
            messagebox.showerror("激活失败", message)
    
    def close_app(self):
        """关闭应用"""
        self.result = False
        self.window.destroy()
    
    def show(self):
        """显示对话框并返回结果"""
        self.window.wait_window()
        return self.result