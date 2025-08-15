# core/license.py - 简化的授权管理

import hashlib
import platform
import uuid
import json
import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64

class LicenseManager:
    def __init__(self):
        # 实际使用时请更改此密钥
        self.secret_key = b'PSD_PRINTER_2024_SECRET_KEY_32CH'
        self.fernet = Fernet(base64.urlsafe_b64encode(self.secret_key))
        self.license_file = os.path.join('data', 'license.dat')
        
        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
    
    def get_machine_code(self):
        """生成16位机器码"""
        try:
            # 获取系统基本信息
            info = f"{platform.system()}{platform.node()}{uuid.getnode()}{platform.processor()}"
            machine_code = hashlib.md5(info.encode()).hexdigest()[:16].upper()
            return machine_code
        except:
            # 备用方案
            fallback = f"{platform.system()}{uuid.getnode()}"
            return hashlib.md5(fallback.encode()).hexdigest()[:16].upper()
    
    def generate_activation_code(self, machine_code, days=365):
        """生成激活码"""
        try:
            expiry_date = datetime.now() + timedelta(days=days)
            license_data = {
                'machine_code': machine_code,
                'expiry_date': expiry_date.isoformat(),
                'generated_date': datetime.now().isoformat(),
                'days': days
            }
            
            license_json = json.dumps(license_data)
            encrypted_license = self.fernet.encrypt(license_json.encode())
            activation_code = base64.b64encode(encrypted_license).decode()
            
            return activation_code
        except Exception as e:
            raise Exception(f"生成激活码失败: {str(e)}")
    
    def verify_activation_code(self, activation_code, machine_code):
        """验证激活码"""
        try:
            encrypted_license = base64.b64decode(activation_code.encode())
            license_json = self.fernet.decrypt(encrypted_license).decode()
            license_data = json.loads(license_json)
            
            # 验证机器码
            if license_data['machine_code'] != machine_code:
                return False, "激活码与当前机器不匹配"
            
            # 检查过期时间
            expiry_date = datetime.fromisoformat(license_data['expiry_date'])
            if datetime.now() > expiry_date:
                return False, "激活码已过期"
            
            return True, license_data
        except Exception as e:
            return False, f"激活码无效: {str(e)}"
    
    def save_license(self, license_data):
        """保存许可证"""
        try:
            license_json = json.dumps(license_data)
            encrypted_data = self.fernet.encrypt(license_json.encode())
            
            with open(self.license_file, 'wb') as f:
                f.write(encrypted_data)
            return True
        except:
            return False
    
    def load_license(self):
        """加载许可证"""
        try:
            if not os.path.exists(self.license_file):
                return None
            
            with open(self.license_file, 'rb') as f:
                encrypted_data = f.read()
            
            license_json = self.fernet.decrypt(encrypted_data).decode()
            return json.loads(license_json)
        except:
            return None
    
    def check_license_validity(self):
        """检查许可证有效性"""
        try:
            license_data = self.load_license()
            if not license_data:
                return False, "未找到许可证"
            
            # 检查机器码
            if license_data['machine_code'] != self.get_machine_code():
                return False, "许可证与当前机器不匹配"
            
            # 检查过期时间
            expiry_date = datetime.fromisoformat(license_data['expiry_date'])
            if datetime.now() > expiry_date:
                return False, "许可证已过期"
            
            remaining_days = (expiry_date - datetime.now()).days
            return True, f"许可证有效，剩余 {remaining_days} 天"
        except Exception as e:
            return False, f"许可证检查失败: {str(e)}"
    
    def activate(self, activation_code):
        """激活软件"""
        try:
            machine_code = self.get_machine_code()
            is_valid, result = self.verify_activation_code(activation_code, machine_code)
            
            if is_valid:
                self.save_license(result)
                expiry_date = datetime.fromisoformat(result['expiry_date'])
                remaining_days = (expiry_date - datetime.now()).days
                return True, f"激活成功！剩余 {remaining_days} 天"
            else:
                return False, result
        except Exception as e:
            return False, f"激活失败: {str(e)}"