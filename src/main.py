import time

# 示例函数
def function1(*params):
    if not params:
        value = 1
    else:
        value = params[0]
    time.sleep(1)
    value += 1
    return str(value), value

def function2(*params):
    value = params[0]
    time.sleep(1)
    value += 1
    return str(value), value

def function3(*params):
    value = params[0]
    time.sleep(1)
    value += 1
    return str(value), value

def function4(*params):
    value = params[0]
    time.sleep(1)
    value += 1
    return str(value), value

def function5(*params):
    value = params[0]
    time.sleep(1)
    value += 1
    return str(value), value

def function6(*params):
    value = params[0]
    time.sleep(1)
    value += 1
    return str(value), value

def function7(*params):
    value = params[0]
    time.sleep(1)
    value += 1
    return str(value), value

def function8(*params):
    value = params[0]
    time.sleep(1)
    value += 1
    return str(value), value

def function9(*params):
    value = params[0]
    time.sleep(1)
    value += 1
    return str(value), value

def function10(*params):
    value = params[0]
    time.sleep(1)
    value += 1
    return str(value), value

# 示例配置界面
PARAM_DEFINITIONS = [
        {
            "name": "启用调试模式",
            "var_name": "debug_mode",
            "description": "是否启用调试模式",
            "type": "bool",
            "default": False
        },
        {
            "name": "服务器地址",
            "var_name": "server_url",
            "description": "服务器连接地址",
            "type": "str",
            "default": "http://localhost:8080"
        },
        {
            "name": "日志级别",
            "var_name": "log_level",
            "description": "日志输出级别",
            "type": "list",
            "options": ["DEBUG", "INFO", "WARNING", "ERROR"]
        },
        {
            "name": "音量大小",
            "var_name": "volume",
            "description": "设置系统音量",
            "type": "slider",
            "min": 10,
            "max": 20,
            "step": 5,
            "default": 50
        }
    ]

functions = [
        function1, function2, function3, function4, function5,
        function6, function7, function8, function9, function10
    ]# 在这里面写上你要运行的函数的函数名
# 示例验证设置
app_config = {
    'soft_id': '',# 你的软件标识
    'version': '',# 你的软件版本
    'mac': ''# 传递的硬件标识，你可以用硬件序号等方法生成
}
# 示例窗口设置
window_config = {
    'login_window_name': '登录窗口',
    'login_title_label': '测试软件',
    'main_window_name': '主窗口',
    'windowicon': 'loog.png' # 这是显示窗口的图标
}
# 示例功能设置
feature_config = {
    'functions': functions,
    'param_definitions': PARAM_DEFINITIONS,# 配置窗口的配置设置
    'if_main_window': True# 是否需要显示主界面
}


if __name__ == '__main__':
    from application import Application
    application = Application(app_config, window_config, feature_config)
    application.run()