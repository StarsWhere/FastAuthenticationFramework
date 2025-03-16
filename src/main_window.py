from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                            QTextEdit, QMessageBox, QCheckBox, QDialog,QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer,QUrl
import time
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSoundEffect
from typing import List, Callable, Dict, Tuple
from config_window import ConfigWindow

class FunctionRunner(QThread):
    finished = pyqtSignal()
    result_ready = pyqtSignal(str)

    def __init__(self, functions: List[Callable], loop: bool = True):
        super().__init__()
        self.functions = functions
        self.loop = loop
        self._is_running = True
        self._is_paused = False
        self._current_index = 0
        self._current_params = []

    def run(self):
        while self._is_running:
            if self._is_paused:
                time.sleep(0.1)
                continue
                
            func = self.functions[self._current_index]
            try:
                # 执行函数并获取结果
                result = func(*self._current_params)
                if isinstance(result, tuple):
                    display_text = result[0]
                    self._current_params = list(result[1:])
                else:
                    display_text = str(result)
                    self._current_params = []
                    
                # 发送结果
                self.result_ready.emit(display_text)
                
                # 更新索引
                self._current_index += 1
                if self._current_index >= len(self.functions):
                    if self.loop:
                        self._current_index = 0
                    else:
                        break
                        
            except Exception as e:
                self.result_ready.emit(f"Error: {str(e)}")
                self._current_params = []
                
        self.finished.emit()

    def stop(self):
        self._is_running = False
        
    def pause(self):
        self._is_paused = True
        
    def resume(self):
        self._is_paused = False
        
    def is_paused(self):
        return self._is_paused

class AnnouncementDialog(QDialog):
    def __init__(self, content,windowicon = 'loog.png'):
        super().__init__()
        self.setFixedSize(self.size())
        self.setMinimumSize(400, 200)
        self.setMaximumSize(600, 400)
        self.windowicon = windowicon
        self.setWindowTitle("软件公告")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout()
        self.content_label = QLabel(content)
        self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.content_label)
        
        btn_layout = QHBoxLayout()
        self.copy_btn = QPushButton("复制")
        self.copy_btn.clicked.connect(self.copy_content)
        self.ok_btn = QPushButton("了解")
        self.ok_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

        # 设置定时器用于按钮颜色切换
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle_button_color)
        self.timer.start(500)  # 每0.5秒触发一次

        # 播放声音提示
        self.sound_effect = QSoundEffect()
        self.sound_effect.setSource(QUrl.fromLocalFile("reminder_sound.wav"))
        self.sound_effect.play()

    def copy_content(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.content_label.text())

    def toggle_button_color(self):
        # 切换按钮颜色
        if self.ok_btn.styleSheet() == "background-color: red;":
            self.ok_btn.setStyleSheet("background-color: ;")
        else:
            self.ok_btn.setStyleSheet("background-color: red;")

    def closeEvent(self, event):
        # 停止定时器
        self.timer.stop()
        super().closeEvent(event)

class MainWindow(QWidget):
    def __init__(self, login_info: Dict, functions: List[Callable], param_definitions, api_client,window_name= '主窗口',windowicon='loog.png'):
        super().__init__()
        self.window_name = window_name
        self.windowicon = windowicon
        self.login_info = login_info
        self.functions = functions
        self.function_runner = None
        self.api_client = api_client
        self.status_timer = None
        self.announce_timer = None
        self.cached_announcement = ""
        self.init_ui()
        self.param_definitions = param_definitions
        self.start_status_check()
        # 默认关闭自动获取公告
        self.announce_checkbox.setChecked(False)

    def update_user_info(self):
        """更新用户到期时间和剩余点数"""
        try:
            # 获取到期时间
            success, expiry_time = self.api_client.get_expiry_time(
                self.login_info['username'],
                self.login_info['password']
            )
            if success:
                self.expiry_label.setText(f"到期时间：{expiry_time}")
            else:
                self.expiry_label.setText(f"到期时间：获取失败 ({expiry_time})")

            # 获取剩余点数
            success, points = self.api_client.get_remaining_points(
                self.login_info['username'],
                self.login_info['password']
            )
            if success:
                self.points_label.setText(f"剩余点数：{points}")
            else:
                self.points_label.setText(f"剩余点数：获取失败 ({points})")
        except Exception as e:
            self.expiry_label.setText("到期时间：获取异常")
            self.points_label.setText("剩余点数：获取异常")
            print(f"更新用户信息失败: {str(e)}")

    def init_ui(self):
        self.setWindowTitle(self.window_name)
        self.setFixedSize(500, 400)
        self.setWindowIcon(QIcon(self.windowicon))  # 设置自定义图

        layout = QVBoxLayout()

        # 显示登录信息
        self.info_label = QLabel(f"欢迎, {self.login_info['username']}")
        self.info_label.setStyleSheet("font-size: 40px; font-weight: bold;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # 添加到期时间和剩余点数显示（同一行）
        info_layout = QHBoxLayout()
        
        self.expiry_label = QLabel("到期时间：加载中...")
        self.expiry_label.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(self.expiry_label)

        # 添加分隔符
        separator = QLabel("")
        separator.setStyleSheet("font-size: 14px; color: #666;")
        info_layout.addWidget(separator)

        self.points_label = QLabel("剩余点数：加载中...")
        self.points_label.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(self.points_label)

        layout.addLayout(info_layout)

        # 初始化用户信息
        self.update_user_info()

        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 公告相关UI
        self.announce_button = QPushButton('查看公告')
        self.announce_button.clicked.connect(self.show_announcement)
        button_layout.addWidget(self.announce_button)

        self.config_button = QPushButton('配置')
        self.config_button.clicked.connect(self.open_config_window)
        button_layout.addWidget(self.config_button)
        
        layout.addLayout(button_layout)

        # 复选框布局
        checkbox_layout = QHBoxLayout()
        
        self.announce_checkbox = QCheckBox('自动获取公告')
        self.announce_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.announce_checkbox)

        self.loop_checkbox = QCheckBox('循环运行')
        self.loop_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.loop_checkbox)
        
        layout.addLayout(checkbox_layout)

        # 结果展示区域
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        # 运行按钮
        self.run_button = QPushButton('运行')
        self.run_button.clicked.connect(self.run_functions)
        layout.addWidget(self.run_button)

        # 停止按钮
        self.stop_button = QPushButton('停止')
        self.stop_button.clicked.connect(self.stop_functions)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        

        self.setLayout(layout)

    def open_config_window(self):
        """打开配置窗口"""
        if self.param_definitions is None:
            QMessageBox.warning(self, "配置不可用", "未提供参数定义，配置功能已禁用")
            self.config_button.setEnabled(False)
            return
            
        self.config_window = ConfigWindow(param_definitions=self.param_definitions,windowicon=self.windowicon)
        self.config_window.exec_()

    def run_functions(self):
        if not hasattr(self, 'function_runner') or self.function_runner is None or not self.function_runner.isRunning():
            self.result_display.clear()
            self.function_runner = FunctionRunner(
                self.functions,
                self.loop_checkbox.isChecked()
            )
            self.function_runner.result_ready.connect(self.update_result)
            self.function_runner.finished.connect(self.on_finished)
            self.function_runner.start()
            self.run_button.setText("暂停")
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(True)
        else:
            if self.function_runner.is_paused():
                self.function_runner.resume()
                self.run_button.setText("暂停")
            else:
                self.function_runner.pause()
                self.run_button.setText("继续")

    def stop_functions(self):
        if self.function_runner:
            self.function_runner.stop()
            self.function_runner.wait()
            self.run_button.setText("运行")
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def update_result(self, result: str):
        self.result_display.append(result)

    def on_finished(self):
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def closeEvent(self, event):
        self.stop_functions()
        self.stop_status_check()
        self.stop_announce_check()
        event.accept()

    def start_status_check(self):
        """启动状态检测定时器"""
        from PyQt5.QtCore import QTimer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_user_status)
        self.status_timer.start(5 * 60 * 1000)  # 5分钟
        # 立即执行一次检查和用户信息更新
        #self.check_user_status()
        #self.update_user_info()

    def stop_status_check(self):
        """停止状态检测定时器"""
        if self.status_timer:
            self.status_timer.stop()
            self.status_timer = None

    def start_announce_check(self):
        """启动公告检查定时器"""
        self.announce_timer = QTimer()
        self.announce_timer.timeout.connect(self.check_announcement)
        self.announce_timer.start(20 * 60 * 1000)  # 20分钟
        # 立即执行一次检查
        self.check_announcement()

    def stop_announce_check(self):
        """停止公告检查定时器"""
        if self.announce_timer:
            self.announce_timer.stop()
            self.announce_timer = None

    def check_announcement(self):
        """检查公告更新"""
        if not self.announce_checkbox.isChecked():
            return

        try:
            success, announcement = self.api_client.get_announcement()
            print("检查公告更新")
            if not success:
                return
            
            
            # 如果公告内容发生变化
            if announcement and announcement != self.cached_announcement:
                self.cached_announcement = announcement
                # 强制显示公告窗口
                self.show_announcement(announcement)
        except Exception as e:
            print(f"检查公告失败: {str(e)}")

    def show_announcement(self, content=None):
        """显示公告"""
        try:
            # 如果未传入内容，则从API获取最新公告
            if content is None or content is False:
                success, content = self.api_client.get_announcement()
                print("显示公告")
                if not success:
                    content = "获取公告失败，请稍后重试"
                else:
                    # 更新缓存
                    self.cached_announcement = str(content) if content is not None else ""
            
            # 确保内容为字符串
            content = str(content) if content is not None else "暂无公告"
            dialog = AnnouncementDialog(content=content,windowicon=self.windowicon)
            self.setEnabled(False)
            dialog.finished.connect(lambda: self.setEnabled(True))
            dialog.exec_()
        except Exception as e:
            print(f"显示公告失败: {str(e)}")
            QMessageBox.warning(self, "错误", "无法显示公告，请检查网络连接")

    def check_user_status(self):
        """检查用户状态"""
        try:
            success, result = self.api_client.check_user_status(
                self.login_info['username'],
                self.login_info['token']
            )
            print(result)
            if success and result == "1":
                self.update_result(f"[状态检测] 账号状态正常")
                # 更新用户信息
                self.update_user_info()
            else:
                error_msg = result if not success else "未知错误"
                self.update_result(f"[状态检测] 账号异常: {error_msg}")
                # 停止所有功能
                self.stop_functions()
                # 停止状态检测
                self.stop_status_check()
                # 弹出警告窗口
                reply = QMessageBox.critical(self, "账号异常",
                    f"检测到账号异常: {error_msg}\n程序将关闭",
                    QMessageBox.Ok)
                if reply == QMessageBox.Ok:
                    self.close()
        except Exception as e:
            self.update_result(f"[状态检测] 检测失败: {str(e)}")
            self.stop_functions()
            self.stop_status_check()
            reply = QMessageBox.critical(self, "检测失败",
                f"状态检测失败: {str(e)}\n程序将关闭",
                QMessageBox.Ok)
            if reply == QMessageBox.Ok:
                self.close()

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    # 示例函数
    def function1():
        return "1", "param1"

    def function2(param1):
        return "2", "param2"

    def function3(param2):
        return "3"

    app = QApplication(sys.argv)
    login_info = {
        'username': 'test_user',
        'token': 'test_token',
        'login_type': 'password'
    }
    functions = [function1, function2, function3]
    window = MainWindow(login_info, functions)
    window.show()
    sys.exit(app.exec_())