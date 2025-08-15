# core/processor.py - PSD处理核心

import os
import cv2
import numpy as np
from PIL import Image
from psd_tools import PSDImage

class PSDProcessor:
    def __init__(self, template_config, log_callback=None):
        """
        初始化PSD处理器
        :param template_config: 模板配置字典
        :param log_callback: 日志回调函数
        """
        self.config = template_config
        self.log_callback = log_callback or print
        
    def log(self, message):
        """记录日志"""
        self.log_callback(message)
    
    def find_all_renderable_layers(self, layer_source, found_layers):
        """递归查找所有可渲染的图层"""
        for layer in layer_source:
            if layer.is_group():
                self.find_all_renderable_layers(layer, found_layers)
            else:
                if layer.is_visible() and layer.width > 0 and layer.height > 0:
                    found_layers.append(layer)
    
    def apply_pattern_to_layer(self, layer, pattern_image, rotate=False):
        """将印花应用到图层"""
        layer_pil = layer.composite()
        if layer_pil is None:
            return None
            
        layer_cv = cv2.cvtColor(np.array(layer_pil), cv2.COLOR_RGBA2BGRA)
        
        try:
            _, _, _, alpha = cv2.split(layer_cv)
        except ValueError:
            return None
            
        _, mask = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)
        pattern_cv = cv2.cvtColor(np.array(pattern_image), cv2.COLOR_RGB2BGR)
        
        h, w = mask.shape
        resized_pattern = cv2.resize(pattern_cv, (w, h))
        
        if rotate:
            resized_pattern = cv2.rotate(resized_pattern, cv2.ROTATE_180)
            
        final_piece = cv2.bitwise_and(resized_pattern, resized_pattern, mask=mask)
        b, g, r = cv2.split(final_piece)
        
        return cv2.merge([b, g, r, mask])
    
    def add_label_to_piece(self, image_to_label, label_text, position, rotate=False):
        """添加标签到图片"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        main_thickness = 2
        outline_thickness = 12
        main_color_bgra = (0, 0, 255, 255)  # 红色
        outline_color_bgra = (255, 255, 255, 255)  # 白色描边
        
        (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, main_thickness)
        canvas_h, canvas_w = text_h + baseline + 10, text_w + 10
        text_canvas = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
        text_org = (5, text_h + 5)
        
        # 绘制描边
        cv2.putText(text_canvas, label_text, text_org, font, font_scale, 
                   outline_color_bgra, outline_thickness, cv2.LINE_AA)
        # 绘制主文字
        cv2.putText(text_canvas, label_text, text_org, font, font_scale, 
                   main_color_bgra, main_thickness, cv2.LINE_AA)
        
        if rotate:
            text_canvas = cv2.flip(text_canvas, -1)
            
        main_image_pil = Image.fromarray(cv2.cvtColor(image_to_label, cv2.COLOR_BGRA2RGBA))
        text_pil = Image.fromarray(cv2.cvtColor(text_canvas, cv2.COLOR_BGRA2RGBA))
        main_image_pil.paste(text_pil, position, text_pil)
        
        return cv2.cvtColor(np.array(main_image_pil), cv2.COLOR_RGBA2BGRA)
    
    def calculate_label_position(self, img_shape, layer_name, size_label, should_rotate):
        """计算标签位置"""
        img_h, img_w, _ = img_shape
        font_scale, thickness = 1.2, 2
        (text_w, text_h), baseline = cv2.getTextSize(size_label, cv2.FONT_HERSHEY_SIMPLEX, 
                                                    font_scale, thickness)
        padding = 30
        
        position_key = self.config['position_rules'].get(layer_name)
        
        if position_key == 'top_left':
            return (padding, padding)
        elif position_key == 'top_center':
            return ((img_w - text_w) // 2, padding)
        elif should_rotate:
            return ((img_w - text_w) // 2, padding)
        else:
            return ((img_w - text_w) // 2, img_h - text_h - baseline - padding)
    
    def process_single_template(self, template_psd_path, pattern_folder_path, output_dir):
        """处理单个PSD模板文件"""
        try:
            filename = os.path.basename(template_psd_path)
            self.log(f"开始处理: {filename}")
            
            # 提取尺码标签
            base_name = os.path.splitext(filename)[0]
            try:
                size_label = base_name.split('-')[-1]
            except IndexError:
                size_label = "N/A"
            
            # 打开PSD文件
            psd = PSDImage.open(template_psd_path)
            
            # 创建白色背景画布
            final_canvas = Image.new('RGBA', (psd.width, psd.height), (255, 255, 255, 255))
            
            # 获取所有可渲染图层
            all_layers = []
            self.find_all_renderable_layers(psd, all_layers)
            
            if not all_layers:
                self.log(f"警告: 在 {filename} 中未找到可用图层")
                return False
            
            # 处理每个配置的图层
            layer_names = self.config['layer_names']
            pattern_files = self.config['pattern_files']
            rotation_rules = self.config['rotation_rules']
            
            for target_name, pattern_filename in zip(layer_names, pattern_files):
                # 检查印花文件是否存在
                full_pattern_path = os.path.join(pattern_folder_path, pattern_filename)
                if not os.path.exists(full_pattern_path):
                    self.log(f"警告: 印花文件 {pattern_filename} 不存在，跳过图层 {target_name}")
                    continue
                
                # 查找对应图层
                found_layer = next((layer for layer in all_layers if layer.name == target_name), None)
                
                if found_layer:
                    # 加载印花图案
                    pattern_image = Image.open(full_pattern_path).convert("RGB")
                    
                    # 检查是否需要旋转
                    should_rotate = (filename, found_layer.name) in rotation_rules
                    
                    self.log(f"处理图层 {target_name} -> {pattern_filename} (旋转: {should_rotate})")
                    
                    # 应用印花
                    processed_image_cv = self.apply_pattern_to_layer(found_layer, pattern_image, rotate=should_rotate)
                    
                    if processed_image_cv is not None:
                        # 计算标签位置
                        label_pos = self.calculate_label_position(processed_image_cv.shape, 
                                                                found_layer.name, size_label, should_rotate)
                        
                        # 添加标签
                        image_with_label = self.add_label_to_piece(processed_image_cv, size_label, 
                                                                 label_pos, rotate=should_rotate)
                        
                        # 合并到最终画布
                        processed_image_pil = Image.fromarray(cv2.cvtColor(image_with_label, cv2.COLOR_BGRA2RGBA))
                        final_canvas.paste(processed_image_pil, (found_layer.left, found_layer.top), processed_image_pil)
                else:
                    self.log(f"警告: 图层 {target_name} 在 {filename} 中未找到")
            
            # 保存最终结果
            output_path_name = os.path.splitext(filename)[0]
            final_output_path = os.path.join(output_dir, f"{output_path_name}.png")
            final_canvas.save(final_output_path)
            
            self.log(f"✅ {filename} 处理完成 -> {final_output_path}")
            return True
            
        except Exception as e:
            self.log(f"❌ 处理 {filename} 时发生错误: {str(e)}")
            return False
    
    def process_directory(self, template_dir, pattern_dir, output_dir):
        """批量处理目录中的所有PSD文件"""
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 获取所有PSD文件
            psd_files = [f for f in os.listdir(template_dir) if f.lower().endswith('.psd')]
            
            if not psd_files:
                self.log("错误: 模板目录中未找到PSD文件")
                return 0, 0
            
            self.log(f"找到 {len(psd_files)} 个PSD文件")
            
            # 处理每个文件
            success_count = 0
            for filename in psd_files:
                template_path = os.path.join(template_dir, filename)
                if self.process_single_template(template_path, pattern_dir, output_dir):
                    success_count += 1
            
            self.log(f"批量处理完成: 成功 {success_count}/{len(psd_files)}")
            return success_count, len(psd_files)
            
        except Exception as e:
            self.log(f"批量处理失败: {str(e)}")
            return 0, 0