# main.py - 主程序入口

import tkinter as tk
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.license import LicenseManager
from gui.activation import ActivationDialog
from gui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.withdraw()  # 先隐藏主窗口
    
    try:
        license_manager = LicenseManager()
        is_valid, message = license_manager.check_license_validity()
        
        if not is_valid:
            print(f"许可证验证失败: {message}")
            print("启动激活程序...")
            
            # 显示主窗口用于激活对话框
            root.deiconify()
            
            # 显示激活对话框
            from gui.activation import ActivationDialog
            activation_dialog = ActivationDialog(root, license_manager)
            if not activation_dialog.show():
                print("用户取消激活，程序退出")
                return
            
            print("激活成功，启动主程序")
        
        # 激活成功或许可证有效，显示主界面
        root.deiconify()
        from gui.main_window import MainWindow
        main_window = MainWindow(root, license_manager)
        root.mainloop()
        
    except Exception as e:
        print(f"程序启动失败: {str(e)}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()