import os
import cv2
import numpy as np
from PIL import Image
from psd_tools import PSDImage

# --- 全局配置区域 ---
TEMPLATE_PSD_DIR = 'E:/github/psd2print/男装短袖模板/男装短袖模板'
PATTERN_FOLDER_PATH = 'E:/github/psd2print/WGTZW25042869/WGTZW25042869/'
output_dir = 'final_prints'

# 1. 裁片和印花的配对关系 (顺序必须匹配)
TARGET_LAYER_NAMES = ['领', '右袖', '左袖', '后片', '前片']
PATTERN_FILENAMES = ['03.jpg', '05.jpg', '04.jpg', '02.jpg', '01.jpg']

# 2. 标签旋转规则配置
ROTATION_RULES = [
    ('男装短袖版-M.psd', '后片'),
    ('男装短袖版-2XL.psd', '右袖'),
    ('男装短袖版-2XL.psd', '左袖'),
    ('男装短袖版-XL.psd', '右袖'),
]

# 3. 标签特殊位置规则配置
POSITION_RULES = {
    '领': 'top_left',
}


# --- 功能函数定义 ---

def find_all_renderable_layers(layer_source, found_layers):
    """递归函数，查找所有可用的、非组的图层。"""
    for layer in layer_source:
        if layer.is_group():
            find_all_renderable_layers(layer, found_layers)
        else:
            if layer.is_visible() and layer.width > 0 and layer.height > 0:
                found_layers.append(layer)

def apply_pattern_to_layer(layer, pattern_image, rotate=False):
    """将给定的印花图案应用到指定的图层形状上。"""
    layer_pil = layer.composite()
    if layer_pil is None: return None
    layer_cv = cv2.cvtColor(np.array(layer_pil), cv2.COLOR_RGBA2BGRA)
    try:
        _, _, _, alpha = cv2.split(layer_cv)
    except ValueError: return None
    _, mask = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)
    pattern_cv = cv2.cvtColor(np.array(pattern_image), cv2.COLOR_RGB2BGR)
    h, w = mask.shape
    resized_pattern = cv2.resize(pattern_cv, (w, h))

    print(f"应用印花图案到图层 '{layer.name}'，尺寸: {resized_pattern.shape[1]}x{resized_pattern.shape[0]}, 旋转: {rotate}")
    if rotate:
        resized_pattern = cv2.rotate(resized_pattern, cv2.ROTATE_180)

    final_piece = cv2.bitwise_and(resized_pattern, resized_pattern, mask=mask)
    b, g, r = cv2.split(final_piece)
    return cv2.merge([b, g, r, mask])

def add_label_to_piece(image_to_label, label_text, position, rolate=False):
    """在给定的图像上的指定位置添加带描边的文字标签。"""
    # [字体改动] 将 font_scale 从 2 改为 1.5
    font, font_scale, main_thickness, outline_thickness = cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2, 12 # 描边也相应调细
    main_color_bgra, outline_color_bgra = (0, 0, 255, 255), (255, 255, 255, 255)
    (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, main_thickness)
    canvas_h, canvas_w = text_h + baseline + 10, text_w + 10
    text_canvas = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
    text_org = (5, text_h + 5)
    cv2.putText(text_canvas, label_text, text_org, font, font_scale, outline_color_bgra, outline_thickness, cv2.LINE_AA)
    cv2.putText(text_canvas, label_text, text_org, font, font_scale, main_color_bgra, main_thickness, cv2.LINE_AA)
    if rolate: text_canvas = cv2.flip(text_canvas, -1)
    main_image_pil = Image.fromarray(cv2.cvtColor(image_to_label, cv2.COLOR_BGRA2RGBA))
    text_pil = Image.fromarray(cv2.cvtColor(text_canvas, cv2.COLOR_BGRA2RGBA))
    main_image_pil.paste(text_pil, position, text_pil)
    return cv2.cvtColor(np.array(main_image_pil), cv2.COLOR_RGBA2BGRA)

# --- 核心处理函数 ---

def process_single_template(template_psd_path):
    """处理单个PSD模板文件的完整流程。"""
    filename = os.path.basename(template_psd_path)
    print(f"\n{'='*20} 开始处理模板: {filename} {'='*20}")

    try:
        base_name = os.path.splitext(filename)[0]
        size_label = base_name.split('-')[-1]
    except IndexError:
        size_label = "N/A"
    
    psd = PSDImage.open(template_psd_path)
    
    # [背景改动] 创建一个不透明的白色画布
    final_canvas = Image.new('RGBA', (psd.width, psd.height), (255, 255, 255, 255))

    all_layers = []
    find_all_renderable_layers(psd, all_layers)

    if not all_layers:
        print(f"警告：在模板 '{filename}' 中未找到任何可用的图层，已跳过。")
        return

    for target_name, pattern_filename in zip(TARGET_LAYER_NAMES, PATTERN_FILENAMES):
        full_pattern_path = os.path.join(PATTERN_FOLDER_PATH, pattern_filename)
        if not os.path.exists(full_pattern_path):
            print(f"警告: 印花图 '{full_pattern_path}' 不存在，跳过图层 '{target_name}'。")
            continue

        found_layer = next((layer for layer in all_layers if layer.name == target_name), None)
        
        if found_layer:
            pattern_image = Image.open(full_pattern_path).convert("RGB")
            should_rotate = (filename, found_layer.name) in ROTATION_RULES
            print(f"处理图层 '{target_name}'，对应印花 '{pattern_filename}'，旋转: {should_rotate}")

            processed_image_cv = apply_pattern_to_layer(found_layer, pattern_image, rotate=should_rotate)
            
            if processed_image_cv is not None:
                
                position_key = POSITION_RULES.get(found_layer.name)
                
                img_h, img_w, _ = processed_image_cv.shape
                # [字体改动] 将 font_scale 从 2 改为 1.5
                font_scale, thickness = 1.5, 2
                (text_w, text_h), baseline = cv2.getTextSize(size_label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                padding = 30
                
                if position_key == 'top_left':
                    label_pos = (padding, padding)
                elif should_rotate:
                    label_pos = ((img_w - text_w) // 2, padding)
                else:
                    label_pos = ((img_w - text_w) // 2, img_h - text_h - baseline - padding)
                
                image_with_label = add_label_to_piece(processed_image_cv, size_label, label_pos, rolate=should_rotate)
                
                processed_image_pil = Image.fromarray(cv2.cvtColor(image_with_label, cv2.COLOR_BGRA2RGBA))
                final_canvas.paste(processed_image_pil, (found_layer.left, found_layer.top), processed_image_pil)
        else:
            print(f"警告: 目标图层 '{target_name}' 在 '{filename}' 中未找到，已跳过。")

    output_path_name = os.path.splitext(filename)[0]
    final_output_path = os.path.join(output_dir, f"{output_path_name}.png")
    final_canvas.save(final_output_path)
    print(f"✅ 模板 '{filename}' 处理完毕 -> {final_output_path}")

# --- 主程序入口 ---
if __name__ == "__main__":
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    if not os.path.exists(TEMPLATE_PSD_DIR): exit(f"错误: 模板文件夹 '{TEMPLATE_PSD_DIR}' 不存在！")
    if len(TARGET_LAYER_NAMES) != len(PATTERN_FILENAMES): exit("错误：图层列表和文件名列表的数量不匹配！")

    for filename in os.listdir(TEMPLATE_PSD_DIR):
        if filename.lower().endswith('.psd'):
            template_path = os.path.join(TEMPLATE_PSD_DIR, filename)
            try:
                process_single_template(template_path)
            except Exception as e:
                print(f"--- 严重错误: 处理文件 {filename} 时发生意外: {e} ---")

    print(f"\n{'='*25} 所有PSD文件处理完毕 {'='*25}")