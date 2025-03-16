# Fast Authentication Framework

## 项目概述
Fast Authentication Framework 是一个基于PyQt5的快速认证框架，提供了完整的用户认证、配置管理和API集成功能。

## 功能特性
- 多方式登录（用户名密码、单码登录）
- 用户注册与充值功能
- 可配置的系统参数
- 自动更新机制
- 详细的API集成

## 安装指南
1. 确保已安装Python 3.8+
2. 克隆本仓库
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用说明
1. 运行主程序：
    ```bash
    python src/main.py
    ```
2. 使用用户名密码或单码登录
3. 在主界面使用各项功能

## 调试模式
要启用调试模式，请在实例化Application时传入debug=True参数。调试模式将：
- 记录所有关键操作到日志文件
- 捕获并记录异常信息
- 日志文件存储在logs目录下，按日期和时间命名
- 自动轮转日志文件（最大10MB）
- 保留最近10天的日志

## 配置说明
- 通过主界面的"配置"按钮打开配置窗口
- 支持以下配置项：
  - 调试模式
  - 日志级别
  - 系统音量

## 贡献指南
欢迎提交Pull Request。请确保：
1. 代码符合PEP8规范
2. 添加必要的单元测试
3. 更新相关文档

## 许可证
本项目采用MIT许可证。详情请查看LICENSE文件。#FastAuthenticationFramework
