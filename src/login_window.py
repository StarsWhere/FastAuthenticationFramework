from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QTabWidget, QCheckBox, QMessageBox, QProgressDialog,QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont,QIcon
import json
import os
import webbrowser
import subprocess
import urllib.request
import time

class DownloadThread(QThread):
    """下载线程"""
    progress_updated = pyqtSignal(int, float)  # 进度百分比, 下载速度
    finished = pyqtSignal(str)  # 下载完成信号，传递保存路径
    error = pyqtSignal(str)  # 错误信号

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        try:
            req = urllib.request.Request(self.url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            with urllib.request.urlopen(req) as response:
                file_size = int(response.headers['Content-Length'])
                downloaded_size = 0
                start_time = time.time()
                last_update_time = start_time
                last_downloaded = 0
                speed_buffer = []  # 用于存储1秒内的下载量

                with open(self.save_path, 'wb') as out_file:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded_size += len(chunk)

                        # 记录当前下载量
                        current_time = time.time()
                        speed_buffer.append((current_time, len(chunk)))

                        # 移除超过1秒的数据
                        while speed_buffer and current_time - speed_buffer[0][0] > 1:
                            speed_buffer.pop(0)

                        # 计算1秒内的总下载量并转换为Mbps
                        total_bytes = sum(size for (_, size) in speed_buffer)
                        speed_mbps = (total_bytes * 8) / (1024 * 1024)  # 转换为Mbps

                        # 计算进度
                        progress = int((downloaded_size / file_size) * 100)

                        # 发射信号
                        self.progress_updated.emit(progress, speed_mbps)

            self.finished.emit(self.save_path)
        except Exception as e:
            self.error.emit(str(e))

class LoginWindow(QWidget):
    def __init__(self,api_client, window_name = "登录",title_label= '测试软件1',windowicon = 'loog.png',on_login_success=None):
        super().__init__()
        self.window_name = window_name
        self.windowicon = windowicon
        self.title_label = title_label
        self.api_client = api_client
        self.on_login_success = on_login_success
        self.is_initializing = True  # 添加初始化标志
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.window_name)
        self.setFixedSize(500, 400)
        self.setWindowIcon(QIcon(self.windowicon))  # 设置自定义图

        main_layout = QVBoxLayout()

        # 添加标题
        title_label = QLabel(self.title_label)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Microsoft YaHei', 16, QFont.Bold))
        main_layout.addWidget(title_label)

        # 标签页
        self.tabs = QTabWidget()

        # 用户名密码登录
        self.username_tab = QWidget()
        self.init_username_tab()
        self.tabs.addTab(self.username_tab, "用户名登录")

        # 单码登录
        self.code_tab = QWidget()
        self.init_code_tab()
        self.tabs.addTab(self.code_tab, "单码登录")

        # 注册
        self.register_tab = QWidget()
        self.init_register_tab()
        self.tabs.addTab(self.register_tab, "注册")

        # 充值
        self.recharge_tab = QWidget()
        self.init_recharge_tab()
        self.tabs.addTab(self.recharge_tab, "充值")

        # 更新
        self.update_tab = QWidget()
        self.init_update_tab()
        self.tabs.addTab(self.update_tab, "更新")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # 加载保存的登录信息
        self.load_saved_login()
        
        # 延迟执行自动登录检查
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.check_auto_login)

    def init_username_tab(self):
        layout = QVBoxLayout()

        # 用户名
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel('用户名:'))
        self.username_input = QLineEdit()
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # 密码
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel('密码:'))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # 记住密码
        self.remember_checkbox = QCheckBox('记住密码')
        layout.addWidget(self.remember_checkbox)

        # 自动登录
        self.auto_login_checkbox = QCheckBox('自动登录')
        self.auto_login_checkbox.stateChanged.connect(self.handle_auto_login_change)
        layout.addWidget(self.auto_login_checkbox)

        # 登录按钮
        login_btn = QPushButton('登录')
        login_btn.clicked.connect(self.handle_username_login)
        layout.addWidget(login_btn)

        self.username_tab.setLayout(layout)

    def init_code_tab(self):
        layout = QVBoxLayout()

        # 单码输入
        code_layout = QHBoxLayout()
        code_layout.addWidget(QLabel('单码:'))
        self.code_input = QLineEdit()
        code_layout.addWidget(self.code_input)
        layout.addLayout(code_layout)

        # 记住密码
        self.code_remember_checkbox = QCheckBox('记住密码')
        layout.addWidget(self.code_remember_checkbox)

        # 自动登录
        self.code_auto_login_checkbox = QCheckBox('自动登录')
        self.code_auto_login_checkbox.stateChanged.connect(self.handle_code_auto_login_change)
        layout.addWidget(self.code_auto_login_checkbox)

        # 登录按钮
        login_btn = QPushButton('登录')
        login_btn.clicked.connect(self.handle_code_login)
        layout.addWidget(login_btn)

        self.code_tab.setLayout(layout)

    def init_register_tab(self):
        layout = QVBoxLayout()

        # 用户名
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel('用户名:'))
        self.register_username_input = QLineEdit()
        username_layout.addWidget(self.register_username_input)
        layout.addLayout(username_layout)

        # 密码
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel('密码:'))
        self.register_password_input = QLineEdit()
        self.register_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.register_password_input)
        layout.addLayout(password_layout)

        # 确认密码
        confirm_password_layout = QHBoxLayout()
        confirm_password_layout.addWidget(QLabel('确认密码:'))
        self.register_confirm_password_input = QLineEdit()
        self.register_confirm_password_input.setEchoMode(QLineEdit.Password)
        confirm_password_layout.addWidget(self.register_confirm_password_input)
        layout.addLayout(confirm_password_layout)

        # 注册按钮
        register_btn = QPushButton('注册')
        register_btn.clicked.connect(self.handle_register)
        layout.addWidget(register_btn)

        self.register_tab.setLayout(layout)

    def init_recharge_tab(self):
        layout = QVBoxLayout()

        # 用户名
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel('用户名:'))
        self.recharge_username_input = QLineEdit()
        username_layout.addWidget(self.recharge_username_input)
        layout.addLayout(username_layout)

        # 充值码
        code_layout = QHBoxLayout()
        code_layout.addWidget(QLabel('充值码:'))
        self.recharge_code_input = QLineEdit()
        code_layout.addWidget(self.recharge_code_input)
        layout.addLayout(code_layout)

        # 充值按钮
        recharge_btn = QPushButton('充值')
        recharge_btn.clicked.connect(self.handle_recharge)
        layout.addWidget(recharge_btn)

        self.recharge_tab.setLayout(layout)

    def init_update_tab(self):
        layout = QVBoxLayout()

        # 更新状态标签
        self.update_label = QLabel("正在检查更新...")
        self.update_label.setAlignment(Qt.AlignCenter)
        self.update_label.setFont(QFont("Microsoft YaHei", 12))
        layout.addWidget(self.update_label)

        # 进度条
        self.update_progress_bar = QProgressBar()
        self.update_progress_bar.setRange(0, 100)
        self.update_progress_bar.setValue(0)
        self.update_progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.update_progress_bar)

        # 速度标签
        self.speed_label = QLabel("速度：0 Mbps")
        self.speed_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.speed_label)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 下载安装包按钮
        self.download_btn = QPushButton("下载安装包")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.handle_download)
        button_layout.addWidget(self.download_btn)

        # 立即更新按钮
        self.update_btn = QPushButton("立即更新")
        self.update_btn.setEnabled(False)
        self.update_btn.clicked.connect(self.handle_update)
        button_layout.addWidget(self.update_btn)

        layout.addLayout(button_layout)

        self.update_tab.setLayout(layout)

        # 初始化检查更新
        self.check_update()

    def handle_auto_login_change(self, state):
        if state == Qt.Checked:
            self.code_auto_login_checkbox.setChecked(False)

    def handle_code_auto_login_change(self, state):
        if state == Qt.Checked:
            self.auto_login_checkbox.setChecked(False)

    def handle_username_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        remember = self.remember_checkbox.isChecked()
        auto_login = self.auto_login_checkbox.isChecked()

        if not username or not password:
            self.show_message('错误', '用户名和密码不能为空')
            return

        # 保存登录信息
        self.save_login_info(username, password, remember, auto_login)

        try:
            # 调用API进行登录验证
            success, result = self.api_client.user_login(
                user_name=username,
                password=password
            )

            if success:
                # 检查用户权限
                permission_result = self.api_client.check_user_status(
                    user_name=username,
                    token=result
                )

                if permission_result[0]:
                    self.show_message('成功', '登录成功')
                    self.close()
                    if self.on_login_success:
                        login_info = {
                            'username': username,
                            'password': password,
                            'token': result,
                            'login_type': 'password'
                        }
                        self.on_login_success(login_info)
                else:
                    self.show_message('错误', '权限验证失败')
            else:
                self.show_message('错误', result)
        except Exception as e:
            self.show_message('错误', f'登录异常: {str(e)}')

    def handle_code_login(self):
        code = self.code_input.text()
        remember = self.code_remember_checkbox.isChecked()
        auto_login = self.code_auto_login_checkbox.isChecked()

        if not code:
            self.show_message('错误', '单码不能为空')
            return

        try:
            # 调用API进行单码登录
            success, result = self.api_client.single_code_login(
                card=code
            )

            if success:
                # 保存登录信息
                self.save_login_info(code, '', remember, auto_login, login_type='code')
                
                self.show_message('成功', '单码登录成功')
                self.close()
                if self.on_login_success:
                    login_info = {
                        'username': code,
                        'password': '',
                        'token': result,
                        'login_type': 'code'
                    }
                    self.on_login_success(login_info)
            else:
                self.show_message('错误', result)
        except Exception as e:
            self.show_message('错误', f'单码登录异常: {str(e)}')

    def handle_register(self):
        username = self.register_username_input.text()
        password = self.register_password_input.text()
        confirm_password = self.register_confirm_password_input.text()

        # 输入验证
        if not username or not password or not confirm_password:
            self.show_message('错误', '所有字段都必须填写')
            return

        if password != confirm_password:
            self.show_message('错误', '两次输入的密码不一致')
            return

        # 显示加载状态
        self.show_loading(True)

        try:
            # 调用API注册
            success, result = self.api_client.user_register(
                user_name=username,
                password=password,
                super_pwd=password,
                card_pwd='',
            )

            if success:
                self.show_message('成功', '注册成功')
                # 清空输入框
                self.register_username_input.clear()
                self.register_password_input.clear()
                self.register_confirm_password_input.clear()
                # 跳转到用户名登录页面
                self.tabs.setCurrentIndex(0)
                self.username_input.setText(username)
            else:
                self.show_message('错误', result)
        except Exception as e:
            self.show_message('错误', f'注册异常: {str(e)}')
        finally:
            self.show_loading(False)

    def handle_recharge(self):
        username = self.recharge_username_input.text()
        code = self.recharge_code_input.text()

        if not username or not code:
            self.show_message('错误', '用户名和充值码不能为空')
            return

        # 显示加载状态
        self.show_loading(True)

        try:
            # 调用API充值
            success, result = self.api_client.user_recharge(
                user_name=username,
                card_pwd=code
            )

            if success:
                self.show_message('成功', '充值成功')
                # 清空输入框
                self.recharge_code_input.clear()
                # 跳转到用户名登录页面
                self.tabs.setCurrentIndex(0)
            else:
                self.show_message('错误', result)
        except Exception as e:
            self.show_message('错误', f'充值异常: {str(e)}')
        finally:
            self.show_loading(False)

    def load_saved_login(self):
        """加载保存的登录信息"""
        if not os.path.exists('login_info.json'):
            return

        try:
            with open('login_info.json', 'r') as f:
                data = json.load(f)
                self.username_input.setText(data.get('username', ''))
                if data.get('remember_password', False):
                    self.password_input.setText(data.get('password', ''))
                    self.remember_checkbox.setChecked(True)
                if data.get('auto_login', False):
                    self.auto_login_checkbox.setChecked(True)
                if data.get('code_remember_password', False):
                    self.code_input.setText(data.get('code_password', ''))
                    self.code_remember_checkbox.setChecked(True)
                if data.get('code_auto_login', False):
                    self.code_auto_login_checkbox.setChecked(True)
                self.recharge_username_input.setText(data.get('username', ''))
                
                # 根据上次登录类型设置初始标签页
                last_login_type = data.get('last_login_type', 'password')
                if last_login_type == 'code':
                    self.tabs.setCurrentIndex(1)  # 切换到单码登录页
        except Exception as e:
            print(f'加载登录信息失败: {e}')

    def save_login_info(self, username, password, remember, auto_login, login_type='password'):
        """保存登录信息"""
        data = {}
        if login_type == 'password':
            data = {
                'username': username,
                'password': password if remember else '',
                'remember_password': remember,
                'auto_login': auto_login,
                'code_password': '',
                'code_remember_password': False,
                'code_auto_login': False,
                'last_login_type': 'password'
            }
        elif login_type == 'code':
            data = {
                'username': '',
                'password': '',
                'remember_password': False,
                'auto_login': False,
                'code_password': username if remember else '',
                'code_remember_password': remember,
                'code_auto_login': auto_login,
                'last_login_type': 'code'
            }

        try:
            with open('login_info.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            self.show_message('错误', f'保存登录信息失败: {e}')

    def show_message(self, title, message):
        """显示消息对话框"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_loading(self, show):
        """显示/隐藏加载状态"""
        if show:
            self.loading_dialog = QProgressDialog('处理中...', None, 0, 0, self)
            self.loading_dialog.setWindowTitle('请稍候')
            self.loading_dialog.setWindowModality(Qt.WindowModal)
            self.loading_dialog.setCancelButton(None)
            self.loading_dialog.show()
        else:
            if hasattr(self, 'loading_dialog'):
                self.loading_dialog.close()

    def check_auto_login(self):
        """检查并执行自动登录"""
        if self.auto_login_checkbox.isChecked():
            # 用户名自动登录
            self.tabs.setCurrentIndex(0)  # 切换到用户名登录页
            self.handle_username_login()
        elif self.code_auto_login_checkbox.isChecked():
            # 单码自动登录
            self.tabs.setCurrentIndex(1)  # 切换到单码登录页
            self.handle_code_login()

    def check_update(self):
        """检查更新"""
        try:
            # 获取最新版本号
            success, latest_version = self.api_client.get_latest_version()
            if not success:
                self.update_label.setText(latest_version)  # 显示错误信息
                return
                
            if latest_version > self.api_client.version:
                # 获取下载地址
                success, download_url = self.api_client.get_download_url()
                if not success:
                    self.update_label.setText(download_url)  # 显示错误信息
                    return
                    
                self.download_url = download_url
                self.update_label.setText(f"发现新版本 {latest_version}\n下载地址：{self.download_url}")
                self.download_btn.setEnabled(True)
                self.update_btn.setEnabled(True)
            else:
                self.update_label.setText("当前已是最新版本，无需更新。")
        except Exception as e:
            self.update_label.setText(f"检查更新失败: {str(e)}")

    def handle_download(self):
        """处理下载按钮点击"""
        webbrowser.open(self.download_url)

    def handle_update(self):
        """处理更新按钮点击"""
        try:
            # 创建update目录
            update_dir = os.path.join(os.getcwd(), "update")
            os.makedirs(update_dir, exist_ok=True)
            
            # 从URL中提取文件名
            filename = os.path.basename(self.download_url)
            save_path = os.path.join(update_dir, filename)
            
            # 创建下载线程
            self.download_thread = DownloadThread(self.download_url, save_path)
            self.download_thread.progress_updated.connect(self.update_progress)
            self.download_thread.finished.connect(self.on_download_finished)
            self.download_thread.error.connect(self.on_download_error)
            
            # 禁用按钮
            self.download_btn.setEnabled(False)
            self.update_btn.setEnabled(False)
            
            # 启动下载
            self.download_thread.start()
            
        except Exception as e:
            self.show_message("更新失败", f"初始化更新失败：\n{str(e)}")

    def update_progress(self, progress, speed):
        """更新下载进度"""
        self.update_progress_bar.setValue(progress)
        self.speed_label.setText(f"速度：{speed:.1f} Mbps")

    def on_download_finished(self, save_path):
        """下载完成处理"""
        self.show_message("更新成功", f"更新文件已下载到：\n{save_path}")
        # 自动打开文件
        if os.name == 'nt':  # Windows
            os.startfile(save_path)
        elif os.name == 'posix':  # macOS/Linux
            subprocess.call(('open', save_path))
        
        # 关闭窗口
        self.close()
        
        # 退出应用
        QApplication.quit()

    def on_download_error(self, error_msg):
        """下载错误处理"""
        self.show_message("更新失败", f"更新下载失败：\n{error_msg}")
        self.download_btn.setEnabled(True)
        self.update_btn.setEnabled(True)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    def handle_login_success(login_info):
        print('登录成功，获取到登录信息：')
        print(login_info)

    app = QApplication(sys.argv)
    window = LoginWindow(
        soft_id='YOUR_SOFT_ID',
        version='1.0',
        mac='',
        on_login_success=handle_login_success
    )
    window.show()
    sys.exit(app.exec_())