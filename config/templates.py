# config/templates.py - 模板配置管理

TEMPLATE_CONFIGS = {
    "男装短袖": {
        "name": "男装短袖模板",
        "layer_names": ['领', '右袖', '左袖', '后片', '前片'],
        "pattern_files": ['03.jpg', '05.jpg', '04.jpg', '02.jpg', '01.jpg'],
        "rotation_rules": [
            ('男装短袖版-M.psd', '后片'),
            ('男装短袖版-2XL.psd', '右袖'),
            ('男装短袖版-2XL.psd', '左袖'),
            ('男装短袖版-XL.psd', '右袖'),
        ],
        "position_rules": {
            '领': 'top_left',
        }
    },
    
    "女装短袖": {
        "name": "女装短袖模板",
        "layer_names": ['领口', '右袖', '左袖', '后片', '前片'],
        "pattern_files": ['collar.jpg', 'sleeve_r.jpg', 'sleeve_l.jpg', 'back.jpg', 'front.jpg'],
        "rotation_rules": [
            ('女装短袖版-M.psd', '后片'),
            ('女装短袖版-L.psd', '右袖'),
        ],
        "position_rules": {
            '领口': 'top_center',
        }
    },
    
    "童装短袖": {
        "name": "童装短袖模板",
        "layer_names": ['领', '袖子', '前胸', '后背'],
        "pattern_files": ['kids_collar.jpg', 'kids_sleeve.jpg', 'kids_front.jpg', 'kids_back.jpg'],
        "rotation_rules": [
            ('童装短袖版-M.psd', '后背'),
        ],
        "position_rules": {
            '领': 'top_left',
        }
    },
    
    "长袖": {
        "name": "长袖模板",
        "layer_names": ['领', '右长袖', '左长袖', '后片', '前片'],
        "pattern_files": ['collar.jpg', 'long_sleeve_r.jpg', 'long_sleeve_l.jpg', 'back.jpg', 'front.jpg'],
        "rotation_rules": [
            ('长袖版-L.psd', '右长袖'),
            ('长袖版-L.psd', '左长袖'),
        ],
        "position_rules": {
            '领': 'top_left',
        }
    }
}

def get_template_list():
    """获取所有可用模板列表"""
    return list(TEMPLATE_CONFIGS.keys())

def get_template_config(template_name):
    """获取指定模板的配置"""
    return TEMPLATE_CONFIGS.get(template_name, None)

def add_custom_template(name, config):
    """添加自定义模板"""
    TEMPLATE_CONFIGS[name] = config

def get_template_display_name(template_key):
    """获取模板显示名称"""
    config = TEMPLATE_CONFIGS.get(template_key)
    return config['name'] if config else template_key