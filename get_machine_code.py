import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.license import LicenseManager

if __name__ == "__main__":
    license_manager = LicenseManager()
    machine_code = license_manager.get_machine_code()
    print(f"当前电脑的机器码: {machine_code}")