import sys
from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow
from main_window import MainWindow

class Application:
    def __init__(self, app_config, window_config, feature_config):
        self.app = QApplication(sys.argv)
        self.login_window_name = window_config.get('login_window_name', "登录")
        self.login_title_label = window_config.get('login_title_label', '测试软件')
        self.main_window_name = window_config.get('main_window_name', "主界面")
        self.windowicon = window_config.get('windowicon', 'loog.png')
        self.functions = feature_config.get('functions', [])
        self.param_definitions = feature_config.get('param_definitions')
        self.if_main_window = feature_config.get('if_main_window', True)
        from api_client import ApiClient
        self.api_client = ApiClient(
            soft_id=app_config['soft_id'],
            version=app_config['version'],
            mac=app_config['mac']
        )

    def handle_login_success(self, login_info):
        if self.if_main_window:
            print("登录成功，准备打开主窗口...")
            # 创建主窗口
            self.main_window = MainWindow(login_info=login_info, functions=self.functions, param_definitions=self.param_definitions, api_client=self.api_client,window_name=self.main_window_name,windowicon=self.windowicon)
            self.main_window.show()
        else:
            print("登录成功，执行后续函数")

    def run(self):
        # 创建登录窗口
        self.login_window = LoginWindow(
            api_client=self.api_client,
            window_name=self.login_window_name,
            title_label=self.login_title_label,
            windowicon=self.windowicon,
            on_login_success=self.handle_login_success,
        )
        self.login_window.show()
        sys.exit(self.app.exec_())