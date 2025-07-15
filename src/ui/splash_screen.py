#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
启动画面模块 - 显示程序加载进度

作者: ECharts教学工具开发团队
版本: 1.2.1
"""

import sys
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QRect
from PyQt6.QtWidgets import (QSplashScreen, QApplication, QProgressBar, 
                             QLabel, QVBoxLayout, QWidget, QFrame)
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QBrush, QPen


class LoadingWorker(QThread):
    """后台加载工作线程"""
    
    progress_updated = pyqtSignal(int, str)  # 进度值, 状态文本
    loading_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.loading_steps = [
            (10, "初始化应用程序..."),
            (20, "检查运行环境..."),
            (30, "加载PyQt6组件..."),
            (40, "加载pandas数据处理..."),
            (50, "加载numpy科学计算..."),
            (60, "加载PyECharts图表库..."),
            (70, "初始化用户界面..."),
            (80, "加载应用资源..."),
            (90, "准备主窗口..."),
            (100, "启动完成!")
        ]
    
    def run(self):
        """执行加载过程"""
        for progress, message in self.loading_steps:
            self.progress_updated.emit(progress, message)
            
            # 模拟实际的加载时间
            if progress <= 30:
                self.msleep(200)  # 初期加载较快
            elif progress <= 60:
                self.msleep(400)  # 中期加载较慢
            else:
                self.msleep(300)  # 后期加载适中
        
        self.loading_finished.emit()


class ModernSplashScreen(QSplashScreen):
    """现代化启动画面"""
    
    def __init__(self):
        # 创建启动画面图像
        pixmap = self.create_splash_pixmap()
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)
        
        # 设置基本属性
        self.setWindowFlags(Qt.WindowType.SplashScreen | 
                           Qt.WindowType.FramelessWindowHint |
                           Qt.WindowType.WindowStaysOnTopHint)
        
        # 初始化UI组件
        self.setup_ui()
        
        # 创建加载工作线程
        self.loading_worker = LoadingWorker()
        self.loading_worker.progress_updated.connect(self.update_progress)
        self.loading_worker.loading_finished.connect(self.loading_complete)
        
        # 状态变量
        self.is_loading_complete = False
        
    def create_splash_pixmap(self):
        """创建启动画面图像"""
        width, height = 500, 350
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(45, 45, 48))  # 深色背景
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制渐变背景
        gradient_rect = QRect(0, 0, width, height)
        brush = QBrush(QColor(45, 45, 48))
        painter.fillRect(gradient_rect, brush)
        
        # 绘制边框
        pen = QPen(QColor(100, 100, 100), 2)
        painter.setPen(pen)
        painter.drawRect(1, 1, width-2, height-2)
        
        # 绘制标题
        title_font = QFont("Microsoft YaHei", 24, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor(255, 255, 255))
        title_rect = QRect(20, 80, width-40, 60)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, 
                        "ChartsTools")
        
        # 绘制副标题
        subtitle_font = QFont("Microsoft YaHei", 12)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(200, 200, 200))
        subtitle_rect = QRect(20, 140, width-40, 30)
        painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignCenter, 
                        "矩阵热力图可视化工具")
        
        # 绘制版本信息
        version_font = QFont("Microsoft YaHei", 10)
        painter.setFont(version_font)
        painter.setPen(QColor(150, 150, 150))
        version_rect = QRect(20, 170, width-40, 20)
        painter.drawText(version_rect, Qt.AlignmentFlag.AlignCenter, 
                        "版本 v1.2.1")
        
        # 绘制装饰性图标区域
        icon_rect = QRect(width//2 - 25, 30, 50, 50)
        painter.setPen(QPen(QColor(0, 150, 255), 3))
        painter.setBrush(QBrush(QColor(0, 150, 255, 50)))
        painter.drawEllipse(icon_rect)
        
        # 在图标内绘制简单的图表符号
        painter.setPen(QPen(QColor(0, 150, 255), 2))
        for i in range(3):
            for j in range(3):
                x = icon_rect.x() + 10 + j * 10
                y = icon_rect.y() + 10 + i * 10
                painter.drawRect(x, y, 8, 8)
        
        painter.end()
        return pixmap
    
    def setup_ui(self):
        """设置UI组件"""
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 8px;
                text-align: center;
                font-size: 12px;
                color: white;
                background-color: #2b2b2b;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078d4, stop:1 #005a9e
                );
                border-radius: 6px;
                margin: 1px;
            }
        """)
        
        # 创建状态标签
        self.status_label = QLabel("正在启动...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-family: Microsoft YaHei;
                margin: 5px;
            }
        """)
        
        # 设置组件位置
        splash_rect = self.rect()
        
        # 进度条位置 (底部偏上)
        progress_width = 300
        progress_x = (splash_rect.width() - progress_width) // 2
        progress_y = splash_rect.height() - 80
        self.progress_bar.setGeometry(progress_x, progress_y, progress_width, 25)
        self.progress_bar.setParent(self)
        
        # 状态标签位置 (进度条下方)
        status_y = progress_y + 35
        self.status_label.setGeometry(progress_x, status_y, progress_width, 20)
        self.status_label.setParent(self)
    
    def start_loading(self):
        """开始加载过程"""
        self.loading_worker.start()
    
    def update_progress(self, value, message):
        """更新进度和状态消息"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        
        # 更新显示
        QApplication.processEvents()
        
        # 在进度条上显示消息
        self.showMessage(message, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, 
                        QColor(255, 255, 255))
    
    def loading_complete(self):
        """加载完成"""
        self.is_loading_complete = True
        self.status_label.setText("启动完成，正在打开主窗口...")
        QApplication.processEvents()
        
        # 短暂延迟后自动关闭
        QTimer.singleShot(500, self.close)
    
    def is_finished(self):
        """检查是否加载完成"""
        return self.is_loading_complete


def show_splash_screen():
    """显示启动画面并返回实例"""
    splash = ModernSplashScreen()
    splash.show()
    
    # 确保启动画面显示在最前面
    splash.raise_()
    splash.activateWindow()
    
    # 处理事件以确保立即显示
    QApplication.processEvents()
    
    return splash


if __name__ == "__main__":
    # 测试启动画面
    app = QApplication(sys.argv)
    
    splash = show_splash_screen()
    splash.start_loading()
    
    # 等待加载完成
    while not splash.is_finished():
        QApplication.processEvents()
        app.processEvents()
    
    print("启动画面测试完成!")
    sys.exit(0) 