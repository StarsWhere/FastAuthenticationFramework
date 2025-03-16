from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QCheckBox, QLineEdit, QComboBox, QSlider,
                            QPushButton, QMessageBox, QToolTip)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor,QIcon
import json

class ConfigWindow(QDialog):
    def __init__(self, param_definitions, config_file="config.json",windowicon='loog.png'):
        super().__init__()
        self.param_definitions = param_definitions
        self.windowicon = windowicon
        self.config_file = config_file
        self.config = {}
        self.widgets = {}
        self.init_ui()
        self.load_config()

    def init_ui(self):
        self.setWindowTitle("配置窗口")
        self.setMinimumSize(400, 300)
        self.setWindowIcon(QIcon(self.windowicon))  # 设置自定义图
        
        layout = QVBoxLayout()
        
        # 根据参数定义创建UI
        for param in self.param_definitions:
            param_layout = QHBoxLayout()
            
            # 参数标签
            label = QLabel(f"{param['name']}:")
            label.setToolTip(param['description'])
            
            # 添加鼠标悬停事件
            label.enterEvent = lambda event, desc=param['description']: QToolTip.showText(
                QCursor.pos(), desc)
            label.leaveEvent = lambda event: QToolTip.hideText()
            
            param_layout.addWidget(label)
            
            # 根据类型创建控件
            if param['type'] == "bool":
                widget = QCheckBox()
                widget.setChecked(param.get('default', False))
            elif param['type'] == "str":
                widget = QLineEdit()
                widget.setText(str(param.get('default', "")))
            elif param['type'] == "list":
                widget = QComboBox()
                widget.addItems(param['options'])
                widget.setCurrentText(str(param.get('default', param['options'][0])))
            elif param['type'] == "slider":
                slider_layout = QHBoxLayout()
                widget = QSlider(Qt.Horizontal)
                widget.setMinimum(param['min'])
                widget.setMaximum(param['max'])
                widget.setSingleStep(param.get('step', 1))
                widget.setValue(param.get('default', param['min']))
                
                value_label = QLabel(str(widget.value()))
                widget.valueChanged.connect(lambda value, label=value_label: label.setText(str(value)))
                
                slider_layout.addWidget(widget)
                slider_layout.addWidget(value_label)
                param_layout.addLayout(slider_layout)
                self.widgets[param['var_name']] = (widget, value_label)
                layout.addLayout(param_layout)
                continue
            
            self.widgets[param['var_name']] = widget
            param_layout.addWidget(widget)
            layout.addLayout(param_layout)
        
        # 保存按钮
        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)
        
        self.setLayout(layout)

    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                self.update_ui_from_config()
        except FileNotFoundError:
            self.config = {}
        except json.JSONDecodeError:
            QMessageBox.warning(self, "错误", "配置文件格式错误")
            self.config = {}

    def update_ui_from_config(self):
        for param in self.param_definitions:
            var_name = param['var_name']
            if var_name in self.config:
                widget = self.widgets[var_name]
                if isinstance(widget, tuple):  # 滑动条
                    slider, label = widget
                    slider.setValue(self.config[var_name])
                    label.setText(str(self.config[var_name]))
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(self.config[var_name])
                elif isinstance(widget, QLineEdit):
                    widget.setText(str(self.config[var_name]))
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(str(self.config[var_name]))

    def save_config(self):
        try:
            self.update_config_from_ui()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "成功", "配置保存成功")
            self.accept()  # 关闭配置窗口
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存配置失败: {str(e)}")

    def update_config_from_ui(self):
        for param in self.param_definitions:
            var_name = param['var_name']
            widget = self.widgets[var_name]
            
            if isinstance(widget, tuple):  # 滑动条
                self.config[var_name] = widget[0].value()
            elif isinstance(widget, QCheckBox):
                self.config[var_name] = widget.isChecked()
            elif isinstance(widget, QLineEdit):
                self.config[var_name] = widget.text()
            elif isinstance(widget, QComboBox):
                self.config[var_name] = widget.currentText()

    def get_config(self):
        self.update_config_from_ui()
        return self.config

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    # 示例参数定义
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

    app = QApplication(sys.argv)
    window = ConfigWindow(PARAM_DEFINITIONS)
    window.show()
    sys.exit(app.exec_())