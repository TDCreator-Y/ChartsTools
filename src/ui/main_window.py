#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ECharts矩阵热力图教学工具 - 主窗口

包含主要的用户界面组件和布局管理
"""

import sys
import os
import tempfile
import base64
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QTabWidget, QTextEdit, QMenuBar,
    QMessageBox, QFileDialog, QLabel, QFrame,
    QProgressBar, QStatusBar, QPushButton, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit,
    QGroupBox, QFormLayout, QColorDialog, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer, QUrl
from PyQt6.QtGui import QAction, QIcon, QFont, QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

# 导入核心模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from core.app_controller import AppController
except ImportError as e:
    print(f"导入AppController失败: {e}")
    print("请确保core模块正确安装")
    # 创建一个临时的AppController类以避免运行时错误
    class AppController:
        def __init__(self):
            print("使用临时AppController类")
        def initialize(self, *args):
            return True
        def load_example_data(self, *args):
            return False
        def get_current_data(self):
            return None
        def render_chart(self):
            return False
        def generate_code(self):
            return {}
        def clear_data(self):
            pass
        def reset_config(self):
            pass


class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 信号定义
    data_imported = pyqtSignal(str)  # 数据导入信号
    config_changed = pyqtSignal(dict)  # 配置变更信号
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ECharts矩阵热力图教学工具")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 设置窗口图标（如果有的话）
        # self.setWindowIcon(QIcon("resources/icons/app_icon.png"))
        
        # 初始化主题设置
        self.current_theme = "light"  # 默认浅色主题
        self.load_theme_settings()
        
        # 初始化应用控制器
        self.app_controller = AppController()
        
        # 添加当前图表状态属性
        self.current_chart_data = None
        self.current_chart_type = "correlation"
        self.current_chart_name = "相关性矩阵"
        
        # 加载样式表
        self.load_stylesheet()
        
        self.init_ui()
        self.create_menu_bar()
        self.create_status_bar()
        self.setup_connections()
        
        # 初始化应用控制器
        self.init_app_controller()
        
        # 显示欢迎信息
        self.show_welcome_message()
        
        # 自动显示演示热力图（使用本地ECharts）
        QTimer.singleShot(2000, self.show_initial_echarts_demo)
    
    def load_stylesheet(self):
        """加载样式表"""
        try:
            # 根据当前主题选择样式文件
            theme_file = f"{self.current_theme}_theme.qss"
            style_path = os.path.join(os.path.dirname(__file__), "../../resources/styles", theme_file)
            
            if os.path.exists(style_path):
                with open(style_path, 'r', encoding='utf-8') as f:
                    stylesheet = f.read()
                self.setStyleSheet(stylesheet)
                print(f"已加载{self.current_theme}主题")
            else:
                print(f"样式文件未找到: {style_path}")
                # 如果找不到指定主题文件，尝试加载默认主题
                self.current_theme = "light"
                self.load_stylesheet()
        except Exception as e:
            print(f"加载样式文件失败: {e}")
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局（水平分割）
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        central_widget.setLayout(main_layout)
        
        # 创建主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # 左侧内容展示区域（70%）
        content_area = self.create_content_area()
        main_splitter.addWidget(content_area)
        
        # 右侧配置面板（30%）
        config_panel = self.create_config_panel()
        main_splitter.addWidget(config_panel)
        
        # 设置分割器比例
        main_splitter.setSizes([700, 300])  # 70% : 30%
        main_splitter.setCollapsible(0, False)  # 内容区域不可折叠
        main_splitter.setCollapsible(1, True)   # 配置面板可折叠
    
    def create_content_area(self):
        """创建左侧内容展示区域"""
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)  # 减小间距
        content_widget.setLayout(content_layout)
        
        # 创建垂直分割器
        content_splitter = QSplitter(Qt.Orientation.Vertical)
        content_splitter.setHandleWidth(3)  # 设置分割器手柄宽度
        content_layout.addWidget(content_splitter)
        
        # 上部：矩阵热力图显示区域
        chart_frame = self.create_chart_area()
        content_splitter.addWidget(chart_frame)
        
        # 下部：代码预览区域
        code_frame = self.create_code_area()
        content_splitter.addWidget(code_frame)
        
        # 设置垂直分割比例（热力图区域占更多空间）
        content_splitter.setSizes([700, 150])  # 更大比例给热力图区域
        content_splitter.setCollapsible(0, False)  # 图表区域不可折叠
        content_splitter.setCollapsible(1, True)   # 代码区域可折叠
        
        # 设置拉伸因子，热力图区域优先获得额外空间
        content_splitter.setStretchFactor(0, 3)  # 热力图区域拉伸因子为3
        content_splitter.setStretchFactor(1, 1)  # 代码区域拉伸因子为1
        
        return content_widget
    
    def create_chart_area(self):
        """创建矩阵热力图显示区域"""
        chart_frame = QFrame()
        chart_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        chart_frame.setLineWidth(1)
        
        chart_layout = QVBoxLayout()
        chart_layout.setContentsMargins(5, 5, 5, 5)
        chart_layout.setSpacing(3)  # 减小间距
        chart_frame.setLayout(chart_layout)
        
        # 标题标签 - 固定高度
        chart_label = QLabel("矩阵热力图显示")
        chart_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            color: #2c3e50;
            padding: 8px 0px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            border-radius: 4px 4px 0px 0px;
        """)
        chart_label.setFixedHeight(35)  # 固定高度35像素
        chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐
        chart_layout.addWidget(chart_label)
        
        # Web引擎视图用于显示ECharts图表 - 弹性调整
        self.chart_view = QWebEngineView()
        self.chart_view.setMinimumHeight(200)  # 设置最小高度
        
        # 设置WebEngine安全策略，允许本地文件访问
        settings = self.chart_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        
        # 设置弹性拉伸因子，让热力图区域占据剩余所有空间
        chart_layout.addWidget(self.chart_view, 1)  # stretch factor = 1
        
        # 加载初始页面
        self.load_initial_chart()
        
        return chart_frame
    
    def create_code_area(self):
        """创建代码预览区域"""
        code_frame = QFrame()
        code_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        code_frame.setLineWidth(1)
        
        code_layout = QVBoxLayout()
        code_layout.setContentsMargins(5, 5, 5, 5)
        code_layout.setSpacing(3)  # 减小间距
        code_frame.setLayout(code_layout)
        
        # 标题标签 - 固定高度
        code_label = QLabel("代码预览")
        code_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            color: #2c3e50;
            padding: 8px 0px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            border-radius: 4px 4px 0px 0px;
        """)
        code_label.setFixedHeight(35)  # 固定高度35像素
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐
        code_layout.addWidget(code_label)
        
        # 代码查看器选项卡 - 弹性调整
        self.code_viewer = QTabWidget()
        self.code_viewer.setMinimumHeight(120)  # 设置最小高度
        # 设置弹性拉伸因子，让代码区域占据剩余空间
        code_layout.addWidget(self.code_viewer, 1)  # stretch factor = 1
        
        # HTML代码选项卡
        self.html_editor = QTextEdit()
        self.html_editor.setReadOnly(True)
        self.html_editor.setFont(QFont("Consolas", 10))
        self.code_viewer.addTab(self.html_editor, "HTML")
        
        # JavaScript代码选项卡
        self.js_editor = QTextEdit()
        self.js_editor.setReadOnly(True)
        self.js_editor.setFont(QFont("Consolas", 10))
        self.code_viewer.addTab(self.js_editor, "JavaScript")
        
        # 初始化代码显示
        self.update_code_display()
        
        return code_frame
    
    def create_config_panel(self):
        """创建右侧配置面板"""
        config_frame = QFrame()
        config_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        config_frame.setLineWidth(1)
        config_frame.setMinimumWidth(250)
        config_frame.setMaximumWidth(400)
        
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(5, 5, 5, 5)
        config_layout.setSpacing(3)  # 减小间距
        config_frame.setLayout(config_layout)
        
        # 标题标签 - 固定高度
        config_label = QLabel("配置面板")
        config_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            color: #2c3e50;
            padding: 8px 0px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            border-radius: 4px 4px 0px 0px;
        """)
        config_label.setFixedHeight(35)  # 固定高度35像素
        config_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐
        config_layout.addWidget(config_label)
        
        # 配置选项卡 - 弹性调整
        self.config_tabs = QTabWidget()
        # 设置弹性拉伸因子，让配置选项卡占据剩余空间
        config_layout.addWidget(self.config_tabs, 1)  # stretch factor = 1
        
        # 创建各个配置选项卡
        self.create_config_tabs()
        
        return config_frame
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 数据信息标签
        self.data_info_label = QLabel("")
        self.status_bar.addPermanentWidget(self.data_info_label)
    
    def init_app_controller(self):
        """初始化应用控制器"""
        # 初始化控制器并传入WebEngine视图
        success = self.app_controller.initialize(self.chart_view)
        
        if success:
            self.status_label.setText("应用控制器初始化成功")
            # 尝试加载示例数据进行测试
            self.test_load_example_data()
        else:
            self.status_label.setText("应用控制器初始化失败")
            QMessageBox.warning(self, "警告", "应用控制器初始化失败")
    
    def connect_app_controller_signals(self):
        """连接应用控制器信号"""
        # 连接状态变化信号
        self.app_controller.status_changed.connect(self.on_status_changed)
        self.app_controller.error_occurred.connect(self.on_error_occurred)
        self.app_controller.progress_updated.connect(self.on_progress_updated)
    
    def create_config_tabs(self):
        """创建配置选项卡"""
        # 基础配置选项卡 (新增)
        self.create_basic_config_tab()
        
        # 样式配置选项卡
        self.create_style_config_tab()
        
        # 交互配置选项卡
        self.create_interaction_config_tab()
        
        # 动画配置选项卡
        self.create_animation_config_tab()
        
        # 高级配置选项卡 (新增)
        self.create_advanced_config_tab()
    
    def create_basic_config_tab(self):
        """创建基础配置选项卡"""
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()
        basic_tab.setLayout(basic_layout)
        
        # 图表标题配置组
        title_group = QGroupBox("图表标题")
        title_layout = QFormLayout()
        title_group.setLayout(title_layout)
        
        # 显示标题开关
        self.title_show = QCheckBox("显示标题")
        self.title_show.setChecked(True)
        self.title_show.toggled.connect(self.on_config_changed)
        title_layout.addRow(self.title_show)
        
        # 标题文本
        self.title_text = QLineEdit("矩阵热力图")
        self.title_text.textChanged.connect(self.on_config_changed)
        title_layout.addRow("标题文本:", self.title_text)
        
        # 副标题
        self.title_subtext = QLineEdit("")
        self.title_subtext.textChanged.connect(self.on_config_changed)
        title_layout.addRow("副标题:", self.title_subtext)
        
        # 标题位置
        self.title_position = QComboBox()
        self.title_position.addItems(["left", "center", "right"])
        self.title_position.setCurrentText("center")
        self.title_position.currentTextChanged.connect(self.on_config_changed)
        title_layout.addRow("标题位置:", self.title_position)
        
        # 垂直位置
        self.title_top = QSpinBox()
        self.title_top.setRange(0, 100)
        self.title_top.setValue(20)
        self.title_top.setSuffix(" px")
        self.title_top.valueChanged.connect(self.on_config_changed)
        title_layout.addRow("垂直位置:", self.title_top)
        
        # 标题字体大小
        self.title_font_size = QSpinBox()
        self.title_font_size.setRange(12, 48)
        self.title_font_size.setValue(18)
        self.title_font_size.setSuffix(" px")
        self.title_font_size.valueChanged.connect(self.on_config_changed)
        title_layout.addRow("字体大小:", self.title_font_size)
        
        # 标题颜色
        self.title_color = QPushButton("#333333")
        self.title_color.setStyleSheet("background-color: #333333; color: white;")
        self.title_color.clicked.connect(self.choose_title_color)
        title_layout.addRow("标题颜色:", self.title_color)
        
        # 标题字体粗细
        self.title_font_weight = QComboBox()
        self.title_font_weight.addItems(["normal", "bold", "bolder", "lighter"])
        self.title_font_weight.setCurrentText("bold")
        self.title_font_weight.currentTextChanged.connect(self.on_config_changed)
        title_layout.addRow("字体粗细:", self.title_font_weight)
        
        basic_layout.addWidget(title_group)
        
        # 网格配置组
        grid_group = QGroupBox("网格配置")
        grid_layout = QFormLayout()
        grid_group.setLayout(grid_layout)
        
        # 图表区域高度
        self.grid_height = QSlider(Qt.Orientation.Horizontal)
        self.grid_height.setRange(40, 90)
        self.grid_height.setValue(60)
        self.grid_height.valueChanged.connect(self.on_config_changed)
        self.grid_height_label = QLabel("60%")
        self.grid_height.valueChanged.connect(lambda v: self.grid_height_label.setText(f"{v}%"))
        grid_height_layout = QHBoxLayout()
        grid_height_layout.addWidget(self.grid_height)
        grid_height_layout.addWidget(self.grid_height_label)
        grid_layout.addRow("图表高度:", grid_height_layout)
        
        # 顶部间距
        self.grid_top = QSlider(Qt.Orientation.Horizontal)
        self.grid_top.setRange(5, 30)
        self.grid_top.setValue(15)
        self.grid_top.valueChanged.connect(self.on_config_changed)
        self.grid_top_label = QLabel("15%")
        self.grid_top.valueChanged.connect(lambda v: self.grid_top_label.setText(f"{v}%"))
        grid_top_layout = QHBoxLayout()
        grid_top_layout.addWidget(self.grid_top)
        grid_top_layout.addWidget(self.grid_top_label)
        grid_layout.addRow("顶部间距:", grid_top_layout)
        
        # 左侧间距
        self.grid_left = QSlider(Qt.Orientation.Horizontal)
        self.grid_left.setRange(5, 30)
        self.grid_left.setValue(10)
        self.grid_left.valueChanged.connect(self.on_config_changed)
        self.grid_left_label = QLabel("10%")
        self.grid_left.valueChanged.connect(lambda v: self.grid_left_label.setText(f"{v}%"))
        grid_left_layout = QHBoxLayout()
        grid_left_layout.addWidget(self.grid_left)
        grid_left_layout.addWidget(self.grid_left_label)
        grid_layout.addRow("左侧间距:", grid_left_layout)
        
        # 右侧间距
        self.grid_right = QSlider(Qt.Orientation.Horizontal)
        self.grid_right.setRange(5, 30)
        self.grid_right.setValue(10)
        self.grid_right.valueChanged.connect(self.on_config_changed)
        self.grid_right_label = QLabel("10%")
        self.grid_right.valueChanged.connect(lambda v: self.grid_right_label.setText(f"{v}%"))
        grid_right_layout = QHBoxLayout()
        grid_right_layout.addWidget(self.grid_right)
        grid_right_layout.addWidget(self.grid_right_label)
        grid_layout.addRow("右侧间距:", grid_right_layout)
        
        # 底部间距
        self.grid_bottom = QSlider(Qt.Orientation.Horizontal)
        self.grid_bottom.setRange(5, 30)
        self.grid_bottom.setValue(10)
        self.grid_bottom.valueChanged.connect(self.on_config_changed)
        self.grid_bottom_label = QLabel("10%")
        self.grid_bottom.valueChanged.connect(lambda v: self.grid_bottom_label.setText(f"{v}%"))
        grid_bottom_layout = QHBoxLayout()
        grid_bottom_layout.addWidget(self.grid_bottom)
        grid_bottom_layout.addWidget(self.grid_bottom_label)
        grid_layout.addRow("底部间距:", grid_bottom_layout)
        
        basic_layout.addWidget(grid_group)
        
        # 坐标轴配置组
        axis_group = QGroupBox("坐标轴配置")
        axis_layout = QFormLayout()
        axis_group.setLayout(axis_layout)
        
        # 显示X轴标签
        self.x_axis_label_show = QCheckBox("显示X轴标签")
        self.x_axis_label_show.setChecked(True)
        self.x_axis_label_show.toggled.connect(self.on_config_changed)
        axis_layout.addRow(self.x_axis_label_show)
        
        # 显示Y轴标签
        self.y_axis_label_show = QCheckBox("显示Y轴标签")
        self.y_axis_label_show.setChecked(True)
        self.y_axis_label_show.toggled.connect(self.on_config_changed)
        axis_layout.addRow(self.y_axis_label_show)
        
        # 轴标签字体大小
        self.axis_label_font_size = QSpinBox()
        self.axis_label_font_size.setRange(8, 16)
        self.axis_label_font_size.setValue(12)
        self.axis_label_font_size.setSuffix(" px")
        self.axis_label_font_size.valueChanged.connect(self.on_config_changed)
        axis_layout.addRow("轴标签字体大小:", self.axis_label_font_size)
        
        # 轴标签颜色
        self.axis_label_color = QPushButton("#666666")
        self.axis_label_color.setStyleSheet("background-color: #666666; color: white;")
        self.axis_label_color.clicked.connect(self.choose_axis_label_color)
        axis_layout.addRow("轴标签颜色:", self.axis_label_color)
        
        # X轴标签旋转
        self.x_axis_rotate = QSlider(Qt.Orientation.Horizontal)
        self.x_axis_rotate.setRange(0, 90)
        self.x_axis_rotate.setValue(0)
        self.x_axis_rotate.valueChanged.connect(self.on_config_changed)
        self.x_axis_rotate_label = QLabel("0°")
        self.x_axis_rotate.valueChanged.connect(lambda v: self.x_axis_rotate_label.setText(f"{v}°"))
        x_axis_rotate_layout = QHBoxLayout()
        x_axis_rotate_layout.addWidget(self.x_axis_rotate)
        x_axis_rotate_layout.addWidget(self.x_axis_rotate_label)
        axis_layout.addRow("X轴标签旋转:", x_axis_rotate_layout)
        
        # 显示轴线
        self.axis_line_show = QCheckBox("显示轴线")
        self.axis_line_show.setChecked(False)
        self.axis_line_show.toggled.connect(self.on_config_changed)
        axis_layout.addRow(self.axis_line_show)
        
        # 显示刻度
        self.axis_tick_show = QCheckBox("显示刻度")
        self.axis_tick_show.setChecked(False)
        self.axis_tick_show.toggled.connect(self.on_config_changed)
        axis_layout.addRow(self.axis_tick_show)
        
        basic_layout.addWidget(axis_group)
        basic_layout.addStretch()
        
        # 添加到配置选项卡
        self.config_tabs.addTab(basic_tab, "基础配置")
    
    def choose_title_color(self):
        """选择标题颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            self.title_color.setText(color_hex)
            self.title_color.setStyleSheet(f"background-color: {color_hex}; color: white;")
            self.on_config_changed()
    
    def choose_axis_label_color(self):
        """选择轴标签颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            self.axis_label_color.setText(color_hex)
            self.axis_label_color.setStyleSheet(f"background-color: {color_hex}; color: white;")
            self.on_config_changed()

    def choose_label_color(self):
        """选择数据标签颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            self.label_color.setText(color_hex)
            self.label_color.setStyleSheet(f"background-color: {color_hex}; color: white;")
            self.on_config_changed()
    
    def choose_cell_border_color(self):
        """选择单元格边框颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            self.cell_border_color.setText(color_hex)
            # 根据颜色亮度调整文字颜色
            if color.lightness() > 128:
                text_color = "black"
            else:
                text_color = "white"
            self.cell_border_color.setStyleSheet(f"background-color: {color_hex}; color: {text_color};")
            self.on_config_changed()

    def on_color_scheme_changed(self):
        """处理颜色方案变更"""
        scheme_name = self.color_scheme.currentText()
        
        # 显示或隐藏自定义颜色编辑器
        if scheme_name == "自定义":
            self.custom_color_group.setVisible(True)
        else:
            self.custom_color_group.setVisible(False)
        
        # 更新颜色预览
        self.update_color_preview()
        
        # 触发配置更改
        self.on_config_changed()

    def update_color_preview(self):
        """更新颜色预览"""
        scheme_name = self.color_scheme.currentText()
        
        if scheme_name == "自定义":
            colors = self.custom_colors
        else:
            colors = self.color_schemes.get(scheme_name, [])
        
        if colors:
            # 创建渐变背景
            gradient_stops = []
            for i, color in enumerate(colors):
                position = i / (len(colors) - 1) if len(colors) > 1 else 0
                gradient_stops.append(f"{color} {position * 100:.1f}%")
            
            gradient = f"linear-gradient(to right, {', '.join(gradient_stops)})"
            self.color_preview.setStyleSheet(f"background: {gradient}; border: 1px solid #ccc; border-radius: 4px;")
        else:
            self.color_preview.setStyleSheet("background: #f0f0f0; border: 1px solid #ccc; border-radius: 4px;")

    def update_custom_color_editor(self):
        """更新自定义颜色编辑器"""
        # 清除现有按钮
        for button in self.custom_color_buttons:
            button.setParent(None)
        self.custom_color_buttons.clear()
        
        # 调整自定义颜色列表长度
        color_count = self.custom_color_count.value()
        if len(self.custom_colors) > color_count:
            self.custom_colors = self.custom_colors[:color_count]
        elif len(self.custom_colors) < color_count:
            # 添加默认颜色
            default_colors = ["#313695", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#800026"]
            while len(self.custom_colors) < color_count:
                self.custom_colors.append(default_colors[len(self.custom_colors) % len(default_colors)])
        
        # 创建新的颜色按钮
        for i in range(color_count):
            color = self.custom_colors[i]
            button = QPushButton()
            button.setFixedSize(40, 30)
            button.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc; border-radius: 4px;")
            button.clicked.connect(lambda checked, idx=i: self.choose_custom_color(idx))
            button.setToolTip(f"点击选择颜色 {i+1}")
            
            self.custom_color_buttons.append(button)
            self.custom_color_buttons_layout.addWidget(button)
        
        # 添加弹性空间
        self.custom_color_buttons_layout.addStretch()
        
        # 更新颜色预览
        if self.color_scheme.currentText() == "自定义":
            self.update_color_preview()
            self.on_config_changed()

    def choose_custom_color(self, index):
        """选择自定义颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            self.custom_colors[index] = color_hex
            
            # 更新按钮样式
            button = self.custom_color_buttons[index]
            button.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #ccc; border-radius: 4px;")
            
            # 更新颜色预览
            self.update_color_preview()
            
            # 触发配置更改
            self.on_config_changed()

    def apply_preset_to_custom(self, preset_name):
        """将预设方案应用到自定义颜色"""
        if preset_name in self.color_schemes:
            preset_colors = self.color_schemes[preset_name]
            
            # 调整自定义颜色数量
            self.custom_color_count.setValue(len(preset_colors))
            
            # 应用预设颜色
            self.custom_colors = preset_colors.copy()
            
            # 更新编辑器
            self.update_custom_color_editor()
            
            # 切换到自定义模式
            self.color_scheme.setCurrentText("自定义")
            self.custom_color_group.setVisible(True)
            
            # 更新颜色预览
            self.update_color_preview()
            
            # 触发配置更改
            self.on_config_changed()

    def get_current_color_scheme(self):
        """获取当前颜色方案"""
        scheme_name = self.color_scheme.currentText()
        
        if scheme_name == "自定义":
            return self.custom_colors
        else:
            return self.color_schemes.get(scheme_name, [])

    def create_style_config_tab(self):
        """创建样式配置选项卡"""
        style_tab = QWidget()
        style_layout = QVBoxLayout()
        style_tab.setLayout(style_layout)
        

        
        # 注意：标题配置已移动到"基础配置"选项卡中，这里不再重复定义
        
        # 改进的颜色配置组
        color_group = QGroupBox("颜色配置")
        color_layout = QVBoxLayout()
        color_group.setLayout(color_layout)
        
        # 颜色方案选择
        scheme_layout = QHBoxLayout()
        scheme_layout.addWidget(QLabel("颜色方案:"))
        
        self.color_scheme = QComboBox()
        self.color_schemes = {
            "蓝色渐变": ["#313695", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf"],
            "红色渐变": ["#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7"],
            "绿色渐变": ["#00441b", "#238b45", "#66c2a4", "#b2e2e2", "#edf8fb"],
            "彩虹渐变": ["#313695", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027"],
            "紫色渐变": ["#3f007d", "#54278f", "#6a51a3", "#807dba", "#9e9ac8", "#bcbddc", "#dadaeb", "#efedf5"],
            "橙色渐变": ["#7f2704", "#a63603", "#d94801", "#f16913", "#fd8d3c", "#fdae6b", "#fdd0a2", "#feedde"],
            "青色渐变": ["#006d2c", "#238b45", "#41ab5d", "#74c476", "#a1d99b", "#c7e9c0", "#e5f5e0", "#f7fcf5"],
            "粉色渐变": ["#7a0177", "#ae017e", "#dd3497", "#f768a1", "#fa9fb5", "#fcc5c0", "#fde0dd", "#fff7f3"],
            "黄绿渐变": ["#004529", "#006837", "#238443", "#41ab5d", "#78c679", "#addd8e", "#d9f0a3", "#f7fcb9"],
            "深海蓝": ["#08306b", "#08519c", "#2171b5", "#4292c6", "#6baed6", "#9ecae1", "#c6dbef", "#deebf7"],
            "火焰红": ["#800026", "#bd0026", "#e31a1c", "#fc4e2a", "#fd8d3c", "#feb24c", "#fed976", "#ffeda0"],
            "森林绿": ["#00441b", "#006d2c", "#238b45", "#41ab5d", "#74c476", "#a1d99b", "#c7e9c0", "#e5f5e0"],
            "紫罗兰": ["#4a1486", "#6a51a3", "#807dba", "#9e9ac8", "#bcbddc", "#dadaeb", "#efedf5", "#fcfbfd"],
            "暖色调": ["#8c2d04", "#cc4c02", "#ec7014", "#fe9929", "#fec44f", "#fee391", "#fff7bc", "#ffffe5"],
            "冷色调": ["#08519c", "#3182bd", "#6baed6", "#9ecae1", "#c6dbef", "#deebf7", "#f7fbff", "#ffffff"],
            "自定义": []
        }
        
        color_scheme_names = list(self.color_schemes.keys())
        self.color_scheme.addItems(color_scheme_names)
        self.color_scheme.currentTextChanged.connect(self.on_color_scheme_changed)
        scheme_layout.addWidget(self.color_scheme)
        
        # 颜色预览区域
        self.color_preview = QFrame()
        self.color_preview.setFixedHeight(30)
        self.color_preview.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
        scheme_layout.addWidget(self.color_preview)
        
        color_layout.addLayout(scheme_layout)
        
        # 自定义颜色编辑器（初始隐藏）
        self.custom_color_group = QGroupBox("自定义颜色编辑器")
        self.custom_color_layout = QVBoxLayout()
        self.custom_color_group.setLayout(self.custom_color_layout)
        
        # 自定义颜色数量选择
        custom_count_layout = QHBoxLayout()
        custom_count_layout.addWidget(QLabel("颜色数量:"))
        self.custom_color_count = QSpinBox()
        self.custom_color_count.setRange(3, 10)
        self.custom_color_count.setValue(5)
        self.custom_color_count.valueChanged.connect(self.update_custom_color_editor)
        custom_count_layout.addWidget(self.custom_color_count)
        custom_count_layout.addStretch()
        self.custom_color_layout.addLayout(custom_count_layout)
        
        # 自定义颜色按钮容器
        self.custom_color_buttons_layout = QHBoxLayout()
        self.custom_color_layout.addLayout(self.custom_color_buttons_layout)
        
        # 自定义颜色按钮列表
        self.custom_color_buttons = []
        self.custom_colors = ["#313695", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf"]
        
        # 预设方案快速应用按钮
        preset_buttons_layout = QHBoxLayout()
        preset_buttons_layout.addWidget(QLabel("快速应用:"))
        
        quick_presets = ["蓝色渐变", "红色渐变", "绿色渐变", "彩虹渐变"]
        for preset in quick_presets:
            btn = QPushButton(preset.replace("渐变", ""))
            btn.setMaximumWidth(60)
            btn.clicked.connect(lambda checked, p=preset: self.apply_preset_to_custom(p))
            preset_buttons_layout.addWidget(btn)
        
        preset_buttons_layout.addStretch()
        self.custom_color_layout.addLayout(preset_buttons_layout)
        
        # 初始化自定义颜色编辑器
        self.update_custom_color_editor()
        
        # 初始隐藏自定义颜色组
        self.custom_color_group.setVisible(False)
        
        color_layout.addWidget(self.custom_color_group)
        
        # 更新颜色预览
        self.update_color_preview()
        
        style_layout.addWidget(color_group)
        
        # 视觉映射配置组
        visual_map_group = QGroupBox("视觉映射")
        visual_map_layout = QFormLayout()
        visual_map_group.setLayout(visual_map_layout)
        
        # 显示颜色条
        self.visual_map_show = QCheckBox("显示颜色条")
        self.visual_map_show.setChecked(True)
        self.visual_map_show.toggled.connect(self.on_config_changed)
        visual_map_layout.addRow(self.visual_map_show)
        
        style_layout.addWidget(visual_map_group)
        
        # 数据标签配置组
        data_label_group = QGroupBox("数据标签")
        data_label_layout = QFormLayout()
        data_label_group.setLayout(data_label_layout)
        
        # 显示数值标签
        self.show_labels = QCheckBox("显示数值")
        self.show_labels.setChecked(True)
        self.show_labels.toggled.connect(self.on_config_changed)
        data_label_layout.addRow(self.show_labels)
        
        # 标签字体大小
        self.label_font_size = QSlider(Qt.Orientation.Horizontal)
        self.label_font_size.setRange(8, 16)
        self.label_font_size.setValue(10)
        self.label_font_size.valueChanged.connect(self.on_config_changed)
        self.label_font_size_label = QLabel("10px")
        self.label_font_size.valueChanged.connect(lambda v: self.label_font_size_label.setText(f"{v}px"))
        label_font_size_layout = QHBoxLayout()
        label_font_size_layout.addWidget(self.label_font_size)
        label_font_size_layout.addWidget(self.label_font_size_label)
        data_label_layout.addRow("字体大小:", label_font_size_layout)
        
        # 标签颜色
        self.label_color = QPushButton("#333333")
        self.label_color.setStyleSheet("background-color: #333333; color: white;")
        self.label_color.clicked.connect(self.choose_label_color)
        data_label_layout.addRow("标签颜色:", self.label_color)
        
        # 标签字体粗细
        self.label_font_weight = QComboBox()
        self.label_font_weight.addItems(["normal", "bold"])
        self.label_font_weight.setCurrentText("normal")
        self.label_font_weight.currentTextChanged.connect(self.on_config_changed)
        data_label_layout.addRow("字体粗细:", self.label_font_weight)
        
        # 数值格式
        self.label_formatter = QComboBox()
        self.label_formatter.addItems(["auto", "integer", "1decimal", "2decimal", "percentage"])
        self.label_formatter.setCurrentText("auto")
        self.label_formatter.currentTextChanged.connect(self.on_config_changed)
        data_label_layout.addRow("数值格式:", self.label_formatter)
        
        style_layout.addWidget(data_label_group)
        
        # 单元格样式配置组
        cell_style_group = QGroupBox("单元格样式")
        cell_style_layout = QFormLayout()
        cell_style_group.setLayout(cell_style_layout)
        
        # 边框宽度
        self.cell_border_width = QSlider(Qt.Orientation.Horizontal)
        self.cell_border_width.setRange(0, 5)
        self.cell_border_width.setValue(1)
        self.cell_border_width.valueChanged.connect(self.on_config_changed)
        self.cell_border_width_label = QLabel("1px")
        self.cell_border_width.valueChanged.connect(lambda v: self.cell_border_width_label.setText(f"{v}px"))
        cell_border_width_layout = QHBoxLayout()
        cell_border_width_layout.addWidget(self.cell_border_width)
        cell_border_width_layout.addWidget(self.cell_border_width_label)
        cell_style_layout.addRow("边框宽度:", cell_border_width_layout)
        
        # 边框颜色
        self.cell_border_color = QPushButton("#ffffff")
        self.cell_border_color.setStyleSheet("background-color: #ffffff; color: black;")
        self.cell_border_color.clicked.connect(self.choose_cell_border_color)
        cell_style_layout.addRow("边框颜色:", self.cell_border_color)
        
        # 圆角半径
        self.cell_border_radius = QSlider(Qt.Orientation.Horizontal)
        self.cell_border_radius.setRange(0, 10)
        self.cell_border_radius.setValue(2)
        self.cell_border_radius.valueChanged.connect(self.on_config_changed)
        self.cell_border_radius_label = QLabel("2px")
        self.cell_border_radius.valueChanged.connect(lambda v: self.cell_border_radius_label.setText(f"{v}px"))
        cell_border_radius_layout = QHBoxLayout()
        cell_border_radius_layout.addWidget(self.cell_border_radius)
        cell_border_radius_layout.addWidget(self.cell_border_radius_label)
        cell_style_layout.addRow("圆角半径:", cell_border_radius_layout)
        
        # 透明度
        self.cell_opacity = QSlider(Qt.Orientation.Horizontal)
        self.cell_opacity.setRange(0, 100)
        self.cell_opacity.setValue(100)
        self.cell_opacity.valueChanged.connect(self.on_config_changed)
        self.cell_opacity_label = QLabel("100%")
        self.cell_opacity.valueChanged.connect(lambda v: self.cell_opacity_label.setText(f"{v}%"))
        cell_opacity_layout = QHBoxLayout()
        cell_opacity_layout.addWidget(self.cell_opacity)
        cell_opacity_layout.addWidget(self.cell_opacity_label)
        cell_style_layout.addRow("透明度:", cell_opacity_layout)
        
        style_layout.addWidget(cell_style_group)
        
        # 显示配置组  
        display_group = QGroupBox("显示设置")
        display_layout = QFormLayout()
        display_group.setLayout(display_layout)
        
        self.show_grid = QCheckBox("显示网格线")
        self.show_grid.setChecked(True)
        self.show_grid.toggled.connect(self.on_config_changed)
        display_layout.addRow(self.show_grid)
        
        style_layout.addWidget(display_group)
        style_layout.addStretch()
        
        self.config_tabs.addTab(style_tab, "样式配置")
    
    def create_interaction_config_tab(self):
        """创建交互配置选项卡"""
        interaction_tab = QWidget()
        interaction_layout = QVBoxLayout()
        interaction_tab.setLayout(interaction_layout)
        
        # 提示框配置组
        tooltip_group = QGroupBox("提示框设置")
        tooltip_layout = QFormLayout()
        tooltip_group.setLayout(tooltip_layout)
        
        self.tooltip_enabled = QCheckBox("启用提示框")
        self.tooltip_enabled.setChecked(True)
        self.tooltip_enabled.toggled.connect(self.on_config_changed)
        tooltip_layout.addRow(self.tooltip_enabled)
        
        self.tooltip_format = QLineEdit("{c}")
        self.tooltip_format.textChanged.connect(self.on_config_changed)
        tooltip_layout.addRow("提示框格式:", self.tooltip_format)
        
        interaction_layout.addWidget(tooltip_group)
        
        # 缩放配置组
        zoom_group = QGroupBox("缩放设置")
        zoom_layout = QFormLayout()
        zoom_group.setLayout(zoom_layout)
        
        self.enable_zoom = QCheckBox("启用数据缩放")
        self.enable_zoom.setChecked(False)
        self.enable_zoom.toggled.connect(self.on_config_changed)
        zoom_layout.addRow(self.enable_zoom)
        
        interaction_layout.addWidget(zoom_group)
        interaction_layout.addStretch()
        
        self.config_tabs.addTab(interaction_tab, "交互配置")
    
    def create_animation_config_tab(self):
        """创建动画配置选项卡"""
        animation_tab = QWidget()
        animation_layout = QVBoxLayout()
        animation_tab.setLayout(animation_layout)
        
        # 动画配置组
        anim_group = QGroupBox("动画设置")
        anim_layout = QFormLayout()
        anim_group.setLayout(anim_layout)
        
        self.animation_enabled = QCheckBox("启用动画")
        self.animation_enabled.setChecked(True)
        self.animation_enabled.toggled.connect(self.on_config_changed)
        anim_layout.addRow(self.animation_enabled)
        
        self.animation_duration = QSpinBox()
        self.animation_duration.setRange(100, 5000)
        self.animation_duration.setValue(1000)
        self.animation_duration.setSuffix(" ms")
        self.animation_duration.valueChanged.connect(self.on_config_changed)
        anim_layout.addRow("动画时长:", self.animation_duration)
        
        self.animation_easing = QComboBox()
        easing_options = ["linear", "cubicInOut", "quadraticIn", "quadraticOut", "elasticOut"]
        self.animation_easing.addItems(easing_options)
        self.animation_easing.setCurrentText("cubicInOut")
        self.animation_easing.currentTextChanged.connect(self.on_config_changed)
        anim_layout.addRow("缓动函数:", self.animation_easing)
        
        animation_layout.addWidget(anim_group)
        animation_layout.addStretch()
        
        self.config_tabs.addTab(animation_tab, "动画配置")
    
    def create_advanced_config_tab(self):
        """创建高级配置选项卡"""
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout()
        advanced_tab.setLayout(advanced_layout)
        
        # 渲染配置组
        rendering_group = QGroupBox("渲染配置")
        rendering_layout = QFormLayout()
        rendering_group.setLayout(rendering_layout)
        
        # 渲染器类型
        self.renderer_type = QComboBox()
        self.renderer_type.addItems(["canvas", "svg"])
        self.renderer_type.setCurrentText("canvas")
        self.renderer_type.currentTextChanged.connect(self.on_config_changed)
        rendering_layout.addRow("渲染器:", self.renderer_type)
        
        # 脏矩形优化
        self.dirty_rect_optimization = QCheckBox("脏矩形优化")
        self.dirty_rect_optimization.setChecked(False)
        self.dirty_rect_optimization.toggled.connect(self.on_config_changed)
        rendering_layout.addRow(self.dirty_rect_optimization)
        
        # 渐进渲染
        self.progressive_render = QSpinBox()
        self.progressive_render.setRange(0, 10000)
        self.progressive_render.setValue(0)
        self.progressive_render.valueChanged.connect(self.on_config_changed)
        rendering_layout.addRow("渐进渲染:", self.progressive_render)
        
        # 渐进阈值
        self.progressive_threshold = QSpinBox()
        self.progressive_threshold.setRange(1000, 10000)
        self.progressive_threshold.setValue(3000)
        self.progressive_threshold.valueChanged.connect(self.on_config_changed)
        rendering_layout.addRow("渐进阈值:", self.progressive_threshold)
        
        advanced_layout.addWidget(rendering_group)
        
        # 工具箱配置组
        toolbox_group = QGroupBox("工具箱配置")
        toolbox_layout = QFormLayout()
        toolbox_group.setLayout(toolbox_layout)
        
        # 显示工具箱
        self.toolbox_show = QCheckBox("显示工具箱")
        self.toolbox_show.setChecked(False)
        self.toolbox_show.toggled.connect(self.on_config_changed)
        toolbox_layout.addRow(self.toolbox_show)
        
        # 工具箱方向
        self.toolbox_orient = QComboBox()
        self.toolbox_orient.addItems(["horizontal", "vertical"])
        self.toolbox_orient.setCurrentText("horizontal")
        self.toolbox_orient.currentTextChanged.connect(self.on_config_changed)
        toolbox_layout.addRow("工具箱方向:", self.toolbox_orient)
        
        # 保存图片功能
        self.toolbox_save_image = QCheckBox("保存图片")
        self.toolbox_save_image.setChecked(True)
        self.toolbox_save_image.toggled.connect(self.on_config_changed)
        toolbox_layout.addRow(self.toolbox_save_image)
        
        # 数据视图功能
        self.toolbox_data_view = QCheckBox("数据视图")
        self.toolbox_data_view.setChecked(False)
        self.toolbox_data_view.toggled.connect(self.on_config_changed)
        toolbox_layout.addRow(self.toolbox_data_view)
        
        # 配置还原功能
        self.toolbox_restore = QCheckBox("配置还原")
        self.toolbox_restore.setChecked(True)
        self.toolbox_restore.toggled.connect(self.on_config_changed)
        toolbox_layout.addRow(self.toolbox_restore)
        
        advanced_layout.addWidget(toolbox_group)
        
        # 性能优化组
        performance_group = QGroupBox("性能优化")
        performance_layout = QFormLayout()
        performance_group.setLayout(performance_layout)
        
        # 大数据优化
        self.large_data_optimization = QCheckBox("大数据优化")
        self.large_data_optimization.setChecked(False)
        self.large_data_optimization.toggled.connect(self.on_config_changed)
        performance_layout.addRow(self.large_data_optimization)
        
        # 大数据阈值
        self.large_data_threshold = QSpinBox()
        self.large_data_threshold.setRange(1000, 10000)
        self.large_data_threshold.setValue(2000)
        self.large_data_threshold.valueChanged.connect(self.on_config_changed)
        performance_layout.addRow("大数据阈值:", self.large_data_threshold)
        
        # 采样方式
        self.sampling_method = QComboBox()
        self.sampling_method.addItems(["average", "max", "min", "sum"])
        self.sampling_method.setCurrentText("average")
        self.sampling_method.currentTextChanged.connect(self.on_config_changed)
        performance_layout.addRow("采样方式:", self.sampling_method)
        
        advanced_layout.addWidget(performance_group)
        
        # 无障碍支持组
        accessibility_group = QGroupBox("无障碍支持")
        accessibility_layout = QFormLayout()
        accessibility_group.setLayout(accessibility_layout)
        
        # 启用无障碍
        self.accessibility_enabled = QCheckBox("启用无障碍")
        self.accessibility_enabled.setChecked(False)
        self.accessibility_enabled.toggled.connect(self.on_config_changed)
        accessibility_layout.addRow(self.accessibility_enabled)
        
        # 图表描述
        self.accessibility_label = QLineEdit("")
        self.accessibility_label.textChanged.connect(self.on_config_changed)
        accessibility_layout.addRow("图表描述:", self.accessibility_label)
        
        # 详细描述
        self.accessibility_description = QTextEdit()
        self.accessibility_description.setMaximumHeight(60)
        self.accessibility_description.textChanged.connect(self.on_config_changed)
        accessibility_layout.addRow("详细描述:", self.accessibility_description)
        
        advanced_layout.addWidget(accessibility_group)
        advanced_layout.addStretch()
        
        # 添加到配置选项卡
        self.config_tabs.addTab(advanced_tab, "高级配置")

    def on_config_changed(self):
        """配置变化处理"""
        # 收集当前配置
        config_updates = {}
        
        # 基础配置
        basic_config = {}
        
        # 图表标题配置
        if hasattr(self, 'title_show'):
            basic_config["title"] = {
                "show": self.title_show.isChecked(),
                "text": self.title_text.text() if hasattr(self, 'title_text') else "矩阵热力图",
                "subtext": self.title_subtext.text() if hasattr(self, 'title_subtext') else "",
                "left": self.title_position.currentText() if hasattr(self, 'title_position') else "center",
                "top": self.title_top.value() if hasattr(self, 'title_top') else 20,
                "textStyle": {
                    "fontSize": self.title_font_size.value() if hasattr(self, 'title_font_size') else 18,
                    "color": self.title_color.text() if hasattr(self, 'title_color') else "#333",
                    "fontWeight": self.title_font_weight.currentText() if hasattr(self, 'title_font_weight') else "bold"
                }
            }
        
        # 网格配置
        if hasattr(self, 'grid_height'):
            basic_config["grid"] = {
                "height": f"{self.grid_height.value()}%",
                "top": f"{self.grid_top.value()}%",
                "left": f"{self.grid_left.value()}%",
                "right": f"{self.grid_right.value()}%",
                "bottom": f"{self.grid_bottom.value()}%"
            }
        
        # 坐标轴配置
        if hasattr(self, 'x_axis_label_show'):
            basic_config["xAxis"] = {
                "axisLabel": {
                    "show": self.x_axis_label_show.isChecked(),
                    "fontSize": self.axis_label_font_size.value() if hasattr(self, 'axis_label_font_size') else 12,
                    "color": self.axis_label_color.text() if hasattr(self, 'axis_label_color') else "#666",
                    "rotate": self.x_axis_rotate.value() if hasattr(self, 'x_axis_rotate') else 0
                },
                "axisLine": {
                    "show": self.axis_line_show.isChecked() if hasattr(self, 'axis_line_show') else False
                },
                "axisTick": {
                    "show": self.axis_tick_show.isChecked() if hasattr(self, 'axis_tick_show') else False
                }
            }
            
            basic_config["yAxis"] = {
                "axisLabel": {
                    "show": self.y_axis_label_show.isChecked(),
                    "fontSize": self.axis_label_font_size.value() if hasattr(self, 'axis_label_font_size') else 12,
                    "color": self.axis_label_color.text() if hasattr(self, 'axis_label_color') else "#666"
                },
                "axisLine": {
                    "show": self.axis_line_show.isChecked() if hasattr(self, 'axis_line_show') else False
                },
                "axisTick": {
                    "show": self.axis_tick_show.isChecked() if hasattr(self, 'axis_tick_show') else False
                }
            }
        
        if basic_config:
            config_updates["basic"] = basic_config
        
        # 样式配置
        style_config = {}
        
        # 颜色方案配置
        if hasattr(self, 'color_scheme'):
            color_schemes = {
                "蓝色渐变": ["#313695", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf"],
                "红色渐变": ["#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7"],
                "绿色渐变": ["#00441b", "#238b45", "#66c2a4", "#b2e2e2", "#edf8fb"],
                "彩虹渐变": ["#313695", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027"]
            }
            
            selected_scheme = self.color_scheme.currentText()
            if selected_scheme in color_schemes:
                style_config["colorScheme"] = {
                    "preset": selected_scheme.replace("渐变", ""),
                    "colors": color_schemes[selected_scheme]
                }
        
        # 视觉映射配置
        if hasattr(self, 'visual_map_show'):
            style_config["visualMap"] = {
                "show": self.visual_map_show.isChecked(),
                "orient": self.visual_map_orient.currentText() if hasattr(self, 'visual_map_orient') else "vertical",
                "right": f"{self.visual_map_right.value()}%" if hasattr(self, 'visual_map_right') else "5%",
                "top": self.visual_map_top.currentText() if hasattr(self, 'visual_map_top') else "center",
                "itemWidth": self.visual_map_width.value() if hasattr(self, 'visual_map_width') else 20,
                "itemHeight": self.visual_map_height.value() if hasattr(self, 'visual_map_height') else 200,
                "calculable": self.visual_map_calculable.isChecked() if hasattr(self, 'visual_map_calculable') else True,
                "realtime": self.visual_map_realtime.isChecked() if hasattr(self, 'visual_map_realtime') else False,
                "precision": self.visual_map_precision.value() if hasattr(self, 'visual_map_precision') else 1
            }
        
        # 数据标签配置
        if hasattr(self, 'show_labels'):
            label_config = {
                "show": self.show_labels.isChecked(),
                "fontSize": self.label_font_size.value() if hasattr(self, 'label_font_size') else 10,
                "color": self.label_color.text() if hasattr(self, 'label_color') else "#333",
                "fontWeight": self.label_font_weight.currentText() if hasattr(self, 'label_font_weight') else "normal"
            }
            
            # 数值格式配置
            if hasattr(self, 'label_formatter'):
                formatter_map = {
                    "auto": "auto",
                    "integer": "{c}",
                    "1decimal": "{c}",
                    "2decimal": "{c}",
                    "percentage": "{c}%"
                }
                label_config["formatter"] = formatter_map.get(self.label_formatter.currentText(), "auto")
            
            style_config["dataLabels"] = label_config
        
        # 单元格样式配置
        if hasattr(self, 'cell_border_width'):
            style_config["cellStyle"] = {
                "borderWidth": self.cell_border_width.value(),
                "borderColor": self.cell_border_color.text() if hasattr(self, 'cell_border_color') else "#fff",
                "borderRadius": self.cell_border_radius.value() if hasattr(self, 'cell_border_radius') else 2,
                "opacity": self.cell_opacity.value() / 100.0 if hasattr(self, 'cell_opacity') else 1.0
            }
        
        if style_config:
            config_updates["style"] = style_config
        
        # 交互配置
        interaction_config = {}
        
        # 提示框配置
        if hasattr(self, 'tooltip_enabled'):
            if self.tooltip_enabled.isChecked():
                interaction_config["tooltip"] = {
                    "trigger": "item",
                    "formatter": self.tooltip_format.text() if hasattr(self, 'tooltip_format') else "{c}"
                }
            
            # 缩放配置
            if hasattr(self, 'enable_zoom') and self.enable_zoom.isChecked():
                interaction_config["dataZoom"] = {
                    "xAxisIndex": 0,
                    "yAxisIndex": 0,
                    "orient": "horizontal",
                    "bottom": "20%",
                    "start": 0,
                    "end": 100
                }
        
        if interaction_config:
            config_updates["interaction"] = interaction_config
        
        # 动画配置
        animation_config = {}
        if hasattr(self, 'animation_enabled'):
            animation_config = {
                "animation": self.animation_enabled.isChecked(),
                "animationDuration": self.animation_duration.value() if self.animation_enabled.isChecked() else 0,
                "animationEasing": self.animation_easing.currentText() if hasattr(self, 'animation_easing') else "cubicInOut",
                "animationDelay": 0,
                "animationDurationUpdate": 300,
                "animationEasingUpdate": "cubicInOut"
            }
        
        if animation_config:
            config_updates["animation"] = animation_config
        
        # 高级配置
        advanced_config = {}
        
        # 渲染配置
        if hasattr(self, 'renderer_type'):
            advanced_config["rendering"] = {
                "renderer": self.renderer_type.currentText(),
                "useDirtyRect": self.dirty_rect_optimization.isChecked() if hasattr(self, 'dirty_rect_optimization') else False,
                "progressive": self.progressive_render.value() if hasattr(self, 'progressive_render') else 0,
                "progressiveThreshold": self.progressive_threshold.value() if hasattr(self, 'progressive_threshold') else 3000
            }
        
        # 工具箱配置
        if hasattr(self, 'toolbox_show'):
            advanced_config["toolbox"] = {
                "show": self.toolbox_show.isChecked(),
                "orient": self.toolbox_orient.currentText() if hasattr(self, 'toolbox_orient') else "horizontal",
                "feature": {
                    "saveAsImage": {
                        "show": self.toolbox_save_image.isChecked() if hasattr(self, 'toolbox_save_image') else True
                    },
                    "dataView": {
                        "show": self.toolbox_data_view.isChecked() if hasattr(self, 'toolbox_data_view') else False
                    },
                    "restore": {
                        "show": self.toolbox_restore.isChecked() if hasattr(self, 'toolbox_restore') else True
                    }
                }
            }
        
        # 性能优化配置
        if hasattr(self, 'large_data_optimization'):
            advanced_config["performance"] = {
                "large": self.large_data_optimization.isChecked(),
                "largeThreshold": self.large_data_threshold.value() if hasattr(self, 'large_data_threshold') else 2000,
                "sampling": self.sampling_method.currentText() if hasattr(self, 'sampling_method') else "average"
            }
        
        # 无障碍支持配置
        if hasattr(self, 'accessibility_enabled'):
            advanced_config["accessibility"] = {
                "enabled": self.accessibility_enabled.isChecked(),
                "label": self.accessibility_label.text() if hasattr(self, 'accessibility_label') else "",
                "description": self.accessibility_description.toPlainText() if hasattr(self, 'accessibility_description') else ""
            }
        
        if advanced_config:
            config_updates["advanced"] = advanced_config
        
        # 更新应用控制器配置
        for section, config in config_updates.items():
            try:
                self.app_controller.update_config(section, config)
            except Exception as e:
                print(f"更新配置失败: {section} - {e}")
        
        # 发射配置变化信号
        self.config_changed.emit(config_updates)
        
        # 重新渲染当前图表以应用配置变化
        self.refresh_current_chart()
    
    def refresh_current_chart(self):
        """重新渲染当前图表以应用配置变化"""
        if self.current_chart_data is not None:
            try:
                # 重新生成HTML内容，这次会使用最新的配置
                html_content = self._create_local_heatmap_html_with_config(
                    self.current_chart_data, 
                    self.current_chart_name
                )
                
                # 更新图表显示
                self.chart_view.setHtml(html_content)
                
                # 更新代码预览
                self._update_local_code_preview(self.current_chart_data, self.current_chart_name)
                
                print("✅ 图表配置更新成功")
                
            except Exception as e:
                print(f"❌ 重新渲染图表失败: {e}")
        else:
            # 如果没有当前数据，渲染默认演示图表
            self.render_local_heatmap(self.current_chart_type, self.current_chart_name)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        # 新建项目
        new_action = QAction('新建项目(&N)', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('创建新的热力图项目')
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # 打开配置
        open_action = QAction('打开配置(&O)', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('打开配置文件')
        open_action.triggered.connect(self.open_config)
        file_menu.addAction(open_action)
        
        # 保存配置
        save_action = QAction('保存配置(&S)', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('保存当前配置')
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # 导出图片
        export_image_action = QAction('导出图片(&I)', self)
        export_image_action.setShortcut('Ctrl+E')
        export_image_action.setStatusTip('导出热力图为图片')
        export_image_action.triggered.connect(self.export_image)
        file_menu.addAction(export_image_action)
        
        # 导出代码
        export_code_action = QAction('导出代码(&C)', self)
        export_code_action.setShortcut('Ctrl+Shift+E')
        export_code_action.setStatusTip('导出HTML/JS代码')
        export_code_action.triggered.connect(self.export_code)
        file_menu.addAction(export_code_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('退出应用程序')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 数据菜单
        data_menu = menubar.addMenu('数据(&D)')
        
        # 导入CSV
        import_csv_action = QAction('导入CSV(&C)', self)
        import_csv_action.setStatusTip('从CSV文件导入矩阵数据')
        import_csv_action.triggered.connect(self.import_csv)
        data_menu.addAction(import_csv_action)
        
        # 导入Excel
        import_excel_action = QAction('导入Excel(&E)', self)
        import_excel_action.setStatusTip('从Excel文件导入矩阵数据')
        import_excel_action.triggered.connect(self.import_excel)
        data_menu.addAction(import_excel_action)
        
        data_menu.addSeparator()
        
        # 示例数据
        example_data_action = QAction('加载示例数据(&S)', self)
        example_data_action.setStatusTip('加载内置示例矩阵数据')
        example_data_action.triggered.connect(self.load_example_data)
        data_menu.addAction(example_data_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')
        
        # 重置布局
        reset_layout_action = QAction('重置布局(&R)', self)
        reset_layout_action.setStatusTip('重置窗口布局到默认状态')
        reset_layout_action.triggered.connect(self.reset_layout)
        view_menu.addAction(reset_layout_action)
        
        # 全屏热力图
        fullscreen_chart_action = QAction('全屏热力图(&F)', self)
        fullscreen_chart_action.setShortcut('F11')
        fullscreen_chart_action.setStatusTip('全屏显示热力图')
        fullscreen_chart_action.triggered.connect(self.fullscreen_chart)
        view_menu.addAction(fullscreen_chart_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        # 使用教程
        tutorial_action = QAction('使用教程(&T)', self)
        tutorial_action.setStatusTip('查看使用教程')
        tutorial_action.triggered.connect(self.show_tutorial)
        help_menu.addAction(tutorial_action)
        
        help_menu.addSeparator()
        
        # 关于
        about_action = QAction('关于(&A)', self)
        about_action.setStatusTip('关于ECharts矩阵热力图教学工具')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # 主题菜单
        theme_menu = menubar.addMenu('主题(&T)')
        
        # 浅色主题
        light_theme_action = QAction('浅色主题(&L)', self)
        light_theme_action.setStatusTip('切换到浅色主题')
        light_theme_action.setCheckable(True)
        light_theme_action.triggered.connect(lambda: self.switch_theme('light'))
        theme_menu.addAction(light_theme_action)
        
        # 深色主题
        dark_theme_action = QAction('深色主题(&D)', self)
        dark_theme_action.setStatusTip('切换到深色主题')
        dark_theme_action.setCheckable(True)
        dark_theme_action.triggered.connect(lambda: self.switch_theme('dark'))
        theme_menu.addAction(dark_theme_action)
        
        # 创建主题动作组（确保只能选择一个）
        from PyQt6.QtGui import QActionGroup
        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.addAction(light_theme_action)
        self.theme_action_group.addAction(dark_theme_action)
        
        # 保存主题动作引用，以便更新选中状态
        self.light_theme_action = light_theme_action
        self.dark_theme_action = dark_theme_action
        
        # 根据当前主题设置选中状态
        if self.current_theme == "light":
            light_theme_action.setChecked(True)
        else:
            dark_theme_action.setChecked(True)
    
    def setup_connections(self):
        """设置信号连接"""
        # 配置选项卡切换信号
        self.config_tabs.currentChanged.connect(self.on_config_tab_changed)
        
        # 代码查看器选项卡切换信号
        self.code_viewer.currentChanged.connect(self.on_code_tab_changed)
        
        # 连接应用控制器信号
        self.connect_app_controller_signals()
    
    def load_initial_chart(self):
        """加载初始图表页面"""
        # 显示简单的欢迎消息
        self.statusBar().showMessage("正在初始化ECharts热力图...", 2000)
    
    def update_code_display(self):
        """更新代码显示"""
        # 显示占位内容，实际代码将在加载数据时更新
        html_placeholder = "<!-- HTML代码将在加载数据后显示 -->"
        js_placeholder = "// JavaScript代码将在加载数据后显示"
        
        self.html_editor.setPlainText(html_placeholder)
        self.js_editor.setPlainText(js_placeholder)
    
    def show_welcome_message(self):
        """显示欢迎消息"""
        self.statusBar().showMessage("欢迎使用ECharts矩阵热力图教学工具！", 3000)
    
    # 菜单栏事件处理方法
    def new_project(self):
        """新建项目"""
        reply = QMessageBox.question(self, '新建项目', 
                                   '确定要创建新项目吗？未保存的更改将丢失。',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # 清除应用控制器数据
            self.app_controller.clear_data()
            self.app_controller.reset_config()
            
            # 重置界面
            self.load_initial_chart()
            self.update_code_display()
            self.update_data_info(None)
    
    def open_config(self):
        """打开配置文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '打开配置文件', '', 
            'JSON文件 (*.json);;所有文件 (*)'
        )
        if file_path:
            # 使用应用控制器加载配置
            success = self.app_controller.load_config(file_path)
            if success:
                # 如果有数据，重新渲染图表
                if self.app_controller.get_current_data():
                    code_dict = self.app_controller.generate_code()
                    self.update_code_preview(code_dict)
    
    def save_config(self):
        """保存配置文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存配置文件', '', 
            'JSON文件 (*.json);;所有文件 (*)'
        )
        if file_path:
            # 使用应用控制器保存配置
            success = self.app_controller.save_config(file_path)
            if not success:
                QMessageBox.warning(self, "警告", "配置文件保存失败")
    
    def export_image(self):
        """导出图片"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, '导出图片', '', 
            'PNG文件 (*.png);;JPG文件 (*.jpg);;所有文件 (*)'
        )
        if file_path:
            self.statusBar().showMessage(f"图片已导出: {file_path}", 2000)
    
    def export_code(self):
        """导出代码"""
        # 选择导出类型
        from PyQt6.QtWidgets import QInputDialog
        
        items = ["完整HTML项目", "单独HTML文件", "JavaScript代码"]
        item, ok = QInputDialog.getItem(self, "选择导出类型", "请选择要导出的代码类型:", items, 0, False)
        
        if ok and item:
            if item == "完整HTML项目":
                # 导出完整项目
                folder_path = QFileDialog.getExistingDirectory(self, "选择导出目录")
                if folder_path:
                    success = self.app_controller.export_project(folder_path)
                    if not success:
                        QMessageBox.warning(self, "警告", "项目导出失败")
            else:
                # 导出单个文件
                if item == "单独HTML文件":
                    file_filter = 'HTML文件 (*.html);;所有文件 (*)'
                elif item == "JavaScript代码":
                    file_filter = 'JavaScript文件 (*.js);;所有文件 (*)'
                
                file_path, _ = QFileDialog.getSaveFileName(
                    self, f'导出{item}', '', file_filter
                )
                if file_path:
                    code_dict = self.app_controller.generate_code()
                    if code_dict:
                        try:
                            if item == "单独HTML文件":
                                content = code_dict.get('complete_html', '')
                            elif item == "JavaScript代码":
                                content = code_dict.get('javascript', '')
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        except Exception as e:
                            QMessageBox.critical(self, "错误", f"文件保存失败: {str(e)}")
                    else:
                        QMessageBox.warning(self, "警告", "没有可导出的代码")
    
    def import_csv(self):
        """导入CSV文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '导入CSV文件', '', 
            'CSV文件 (*.csv);;所有文件 (*)'
        )
        if file_path:
            # 直接处理CSV文件并渲染热力图
            success = self.load_and_render_file_data(file_path, "csv")
            if success:
                self.statusBar().showMessage(f"✅ CSV文件导入成功: {file_path}", 3000)
                print(f"✅ CSV文件导入并渲染成功: {file_path}")
            else:
                self.statusBar().showMessage("❌ CSV文件导入失败", 3000)
                print("❌ CSV文件导入失败")
            self.data_imported.emit(file_path)
    
    def import_excel(self):
        """导入Excel文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '导入Excel文件', '', 
            'Excel文件 (*.xlsx *.xls);;所有文件 (*)'
        )
        if file_path:
            # 直接处理Excel文件并渲染热力图
            success = self.load_and_render_file_data(file_path, "excel")
            if success:
                self.statusBar().showMessage(f"✅ Excel文件导入成功: {file_path}", 3000)
                print(f"✅ Excel文件导入并渲染成功: {file_path}")
            else:
                self.statusBar().showMessage("❌ Excel文件导入失败", 3000)
                print("❌ Excel文件导入失败")
            self.data_imported.emit(file_path)
    
    def load_example_data(self):
        """加载示例数据 - 只使用本地ECharts"""
        # 显示示例数据选择对话框
        from PyQt6.QtWidgets import QInputDialog
        
        items = ["相关性矩阵", "随机数据", "模式数据"]
        item, ok = QInputDialog.getItem(self, "选择示例数据", "请选择要加载的示例数据类型:", items, 0, False)
        
        if ok and item:
            # 映射到内部类型
            data_type_map = {
                "相关性矩阵": "correlation",
                "随机数据": "random", 
                "模式数据": "pattern"
            }
            data_type = data_type_map.get(item, "correlation")
            
            # 只使用本地ECharts渲染
            print(f"🔄 加载示例数据: {item}")
            success = self.render_local_heatmap(data_type, item)
            
            if success:
                self.statusBar().showMessage(f"✅ 已加载{item}示例数据 (ECharts)", 3000)
                print(f"✅ {item}示例数据ECharts渲染成功")
            else:
                self.statusBar().showMessage("❌ ECharts加载示例数据失败", 3000)
                print(f"❌ {item}示例数据ECharts渲染失败")

    def force_render_chart(self):
        """强制渲染图表 - 只使用本地ECharts"""
        try:
            print("🔄 强制渲染ECharts图表...")
            
            # 使用本地ECharts渲染，默认显示相关性矩阵
            success = self.render_local_heatmap("correlation", "相关性矩阵")
            
            if success:
                print("✅ ECharts图表渲染成功")
                self.statusBar().showMessage("✅ ECharts图表渲染成功", 2000)
            else:
                print("❌ ECharts图表渲染失败")
                self.statusBar().showMessage("❌ ECharts图表渲染失败", 2000)
                
        except Exception as e:
            print(f"❌ ECharts渲染失败: {e}")
            self.statusBar().showMessage(f"❌ ECharts渲染失败: {str(e)}", 3000)

    def render_local_heatmap(self, data_type: str, display_name: str) -> bool:
        """渲染本地热力图
        
        Args:
            data_type: 数据类型 ("correlation", "random", "pattern")
            display_name: 显示名称
            
        Returns:
            bool: 是否渲染成功
        """
        try:
            # 根据数据类型生成不同的热力图数据
            if data_type == "correlation":
                data_info = self._generate_correlation_data()
            elif data_type == "random":
                data_info = self._generate_random_data()
            elif data_type == "pattern":
                data_info = self._generate_pattern_data()
            else:
                data_info = self._generate_correlation_data()  # 默认
            
            # 保存当前图表状态
            self.current_chart_data = data_info
            self.current_chart_type = data_type
            self.current_chart_name = display_name
            
            # 生成本地HTML（使用配置参数）
            html_content = self._create_local_heatmap_html_with_config(data_info, display_name)
            
            # 显示热力图
            self.chart_view.setHtml(html_content)
            
            # 更新数据信息显示
            self.update_data_info(data_info)
            
            # 更新代码预览
            self._update_local_code_preview(data_info, display_name)
            
            return True
            
        except Exception as e:
            print(f"❌ 本地热力图渲染失败: {e}")
            return False

    def _generate_correlation_data(self) -> dict:
        """生成相关性矩阵数据"""
        subjects = ['数学', '物理', '化学', '英语', '语文']
        data = [
            [1.00, 0.85, 0.67, 0.43, 0.28],
            [0.85, 1.00, 0.73, 0.56, 0.34],
            [0.67, 0.73, 1.00, 0.68, 0.45],
            [0.43, 0.56, 0.68, 1.00, 0.72],
            [0.28, 0.34, 0.45, 0.72, 1.00]
        ]
        
        return {
            'title': '学科成绩相关性矩阵',
            'labels': subjects,
            'data': data,
            'shape': (5, 5),
            'file_path': '相关性矩阵示例',
            'file_type': 'correlation',
            'min_value': 0.0,
            'max_value': 1.0,
            'color_scheme': 'correlation'
        }

    def _generate_random_data(self) -> dict:
        """生成随机数据矩阵"""
        import random
        labels = [f'变量{i+1}' for i in range(6)]
        data = []
        
        for i in range(6):
            row = []
            for j in range(6):
                value = random.uniform(0, 100)
                row.append(round(value, 1))
            data.append(row)
        
        return {
            'title': '随机数据矩阵',
            'labels': labels,
            'data': data,
            'shape': (6, 6),
            'file_path': '随机数据示例',
            'file_type': 'random',
            'min_value': 0.0,
            'max_value': 100.0,
            'color_scheme': 'random'
        }

    def _generate_pattern_data(self) -> dict:
        """生成模式数据矩阵"""
        import math
        labels = [f'节点{i+1}' for i in range(7)]
        data = []
        
        for i in range(7):
            row = []
            for j in range(7):
                # 创建同心圆模式
                center_i, center_j = 3, 3
                distance = math.sqrt((i - center_i)**2 + (j - center_j)**2)
                value = max(0, 50 - distance * 8)
                row.append(round(value, 1))
            data.append(row)
        
        return {
            'title': '模式数据矩阵',
            'labels': labels,
            'data': data,
            'shape': (7, 7),
            'file_path': '模式数据示例',
            'file_type': 'pattern',
            'min_value': 0.0,
            'max_value': 50.0,
            'color_scheme': 'pattern'
        }

    def _get_current_config(self) -> dict:
        """获取当前配置面板的配置参数"""
        config = {}
        
        # 基础配置
        if hasattr(self, 'title_show'):
            config['title'] = {
                'show': self.title_show.isChecked(),
                'text': self.title_text.text() if hasattr(self, 'title_text') else "矩阵热力图",
                'subtext': self.title_subtext.text() if hasattr(self, 'title_subtext') else "",
                'left': self.title_position.currentText() if hasattr(self, 'title_position') else "center",
                'top': self.title_top.value() if hasattr(self, 'title_top') else 20,
                'textStyle': {
                    'fontSize': self.title_font_size.value() if hasattr(self, 'title_font_size') else 18,
                    'color': self.title_color.text() if hasattr(self, 'title_color') else "#333",
                    'fontWeight': self.title_font_weight.currentText() if hasattr(self, 'title_font_weight') else "bold"
                }
            }
        
        # 网格配置
        if hasattr(self, 'grid_height'):
            config['grid'] = {
                'height': f"{self.grid_height.value()}%",
                'top': f"{self.grid_top.value()}%",
                'left': f"{self.grid_left.value()}%",
                'right': f"{self.grid_right.value()}%",
                'bottom': f"{self.grid_bottom.value()}%"
            }
        
        # 坐标轴配置
        if hasattr(self, 'x_axis_label_show'):
            config['xAxis'] = {
                'axisLabel': {
                    'show': self.x_axis_label_show.isChecked(),
                    'fontSize': self.axis_label_font_size.value() if hasattr(self, 'axis_label_font_size') else 12,
                    'color': self.axis_label_color.text() if hasattr(self, 'axis_label_color') else "#666",
                    'rotate': self.x_axis_rotate.value() if hasattr(self, 'x_axis_rotate') else 0
                },
                "axisLine": {
                    "show": self.axis_line_show.isChecked() if hasattr(self, 'axis_line_show') else False
                },
                "axisTick": {
                    "show": self.axis_tick_show.isChecked() if hasattr(self, 'axis_tick_show') else False
                }
            }
            
            basic_config["yAxis"] = {
                "axisLabel": {
                    "show": self.y_axis_label_show.isChecked(),
                    "fontSize": self.axis_label_font_size.value() if hasattr(self, 'axis_label_font_size') else 12,
                    "color": self.axis_label_color.text() if hasattr(self, 'axis_label_color') else "#666"
                },
                "axisLine": {
                    "show": self.axis_line_show.isChecked() if hasattr(self, 'axis_line_show') else False
                },
                "axisTick": {
                    "show": self.axis_tick_show.isChecked() if hasattr(self, 'axis_tick_show') else False
                }
            }
        
        if basic_config:
            config_updates["basic"] = basic_config
        
        # 样式配置
        style_config = {}
        
        # 颜色方案配置
        if hasattr(self, 'color_scheme'):
            color_schemes = {
                "蓝色渐变": ["#313695", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf"],
                "红色渐变": ["#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7"],
                "绿色渐变": ["#00441b", "#238b45", "#66c2a4", "#b2e2e2", "#edf8fb"],
                "彩虹渐变": ["#313695", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027"]
            }
            
            selected_scheme = self.color_scheme.currentText()
            if selected_scheme in color_schemes:
                style_config["colorScheme"] = {
                    "preset": selected_scheme.replace("渐变", ""),
                    "colors": color_schemes[selected_scheme]
                }
        
        # 视觉映射配置
        if hasattr(self, 'visual_map_show'):
            style_config["visualMap"] = {
                "show": self.visual_map_show.isChecked(),
                "orient": self.visual_map_orient.currentText() if hasattr(self, 'visual_map_orient') else "vertical",
                "right": f"{self.visual_map_right.value()}%" if hasattr(self, 'visual_map_right') else "5%",
                "top": self.visual_map_top.currentText() if hasattr(self, 'visual_map_top') else "center",
                "itemWidth": self.visual_map_width.value() if hasattr(self, 'visual_map_width') else 20,
                "itemHeight": self.visual_map_height.value() if hasattr(self, 'visual_map_height') else 200,
                "calculable": self.visual_map_calculable.isChecked() if hasattr(self, 'visual_map_calculable') else True,
                "realtime": self.visual_map_realtime.isChecked() if hasattr(self, 'visual_map_realtime') else False,
                "precision": self.visual_map_precision.value() if hasattr(self, 'visual_map_precision') else 1
            }
        
        # 数据标签配置
        if hasattr(self, 'show_labels'):
            label_config = {
                "show": self.show_labels.isChecked(),
                "fontSize": self.label_font_size.value() if hasattr(self, 'label_font_size') else 10,
                "color": self.label_color.text() if hasattr(self, 'label_color') else "#333",
                "fontWeight": self.label_font_weight.currentText() if hasattr(self, 'label_font_weight') else "normal"
            }
            
            # 数值格式配置
            if hasattr(self, 'label_formatter'):
                formatter_map = {
                    "auto": "auto",
                    "integer": "{c}",
                    "1decimal": "{c}",
                    "2decimal": "{c}",
                    "percentage": "{c}%"
                }
                label_config["formatter"] = formatter_map.get(self.label_formatter.currentText(), "auto")
            
            style_config["dataLabels"] = label_config
        
        # 单元格样式配置
        if hasattr(self, 'cell_border_width'):
            style_config["cellStyle"] = {
                "borderWidth": self.cell_border_width.value(),
                "borderColor": self.cell_border_color.text() if hasattr(self, 'cell_border_color') else "#fff",
                "borderRadius": self.cell_border_radius.value() if hasattr(self, 'cell_border_radius') else 2,
                "opacity": self.cell_opacity.value() / 100.0 if hasattr(self, 'cell_opacity') else 1.0
            }
        
        if style_config:
            config_updates["style"] = style_config
        
        # 交互配置
        interaction_config = {}
        
        # 提示框配置
        if hasattr(self, 'tooltip_enabled'):
            if self.tooltip_enabled.isChecked():
                interaction_config["tooltip"] = {
                    "trigger": "item",
                    "formatter": self.tooltip_format.text() if hasattr(self, 'tooltip_format') else "{c}"
                }
            
            # 缩放配置
            if hasattr(self, 'enable_zoom') and self.enable_zoom.isChecked():
                interaction_config["dataZoom"] = {
                    "xAxisIndex": 0,
                    "yAxisIndex": 0,
                    "orient": "horizontal",
                    "bottom": "20%",
                    "start": 0,
                    "end": 100
                }
        
        if interaction_config:
            config_updates["interaction"] = interaction_config
        
        # 动画配置
        animation_config = {}
        if hasattr(self, 'animation_enabled'):
            animation_config = {
                "animation": self.animation_enabled.isChecked(),
                "animationDuration": self.animation_duration.value() if self.animation_enabled.isChecked() else 0,
                "animationEasing": self.animation_easing.currentText() if hasattr(self, 'animation_easing') else "cubicInOut",
                "animationDelay": 0,
                "animationDurationUpdate": 300,
                "animationEasingUpdate": "cubicInOut"
            }
        
        if animation_config:
            config_updates["animation"] = animation_config
        
        # 高级配置
        advanced_config = {}
        
        # 渲染配置
        if hasattr(self, 'renderer_type'):
            advanced_config["rendering"] = {
                "renderer": self.renderer_type.currentText(),
                "useDirtyRect": self.dirty_rect_optimization.isChecked() if hasattr(self, 'dirty_rect_optimization') else False,
                "progressive": self.progressive_render.value() if hasattr(self, 'progressive_render') else 0,
                "progressiveThreshold": self.progressive_threshold.value() if hasattr(self, 'progressive_threshold') else 3000
            }
        
        # 工具箱配置
        if hasattr(self, 'toolbox_show'):
            advanced_config["toolbox"] = {
                "show": self.toolbox_show.isChecked(),
                "orient": self.toolbox_orient.currentText() if hasattr(self, 'toolbox_orient') else "horizontal",
                "feature": {
                    "saveAsImage": {
                        "show": self.toolbox_save_image.isChecked() if hasattr(self, 'toolbox_save_image') else True
                    },
                    "dataView": {
                        "show": self.toolbox_data_view.isChecked() if hasattr(self, 'toolbox_data_view') else False
                    },
                    "restore": {
                        "show": self.toolbox_restore.isChecked() if hasattr(self, 'toolbox_restore') else True
                    }
                }
            }
        
        # 性能优化配置
        if hasattr(self, 'large_data_optimization'):
            advanced_config["performance"] = {
                "large": self.large_data_optimization.isChecked(),
                "largeThreshold": self.large_data_threshold.value() if hasattr(self, 'large_data_threshold') else 2000,
                "sampling": self.sampling_method.currentText() if hasattr(self, 'sampling_method') else "average"
            }
        
        # 无障碍支持配置
        if hasattr(self, 'accessibility_enabled'):
            advanced_config["accessibility"] = {
                "enabled": self.accessibility_enabled.isChecked(),
                "label": self.accessibility_label.text() if hasattr(self, 'accessibility_label') else "",
                "description": self.accessibility_description.toPlainText() if hasattr(self, 'accessibility_description') else ""
            }
        
        if advanced_config:
            config_updates["advanced"] = advanced_config
        
        # 更新应用控制器配置
        for section, config in config_updates.items():
            try:
                self.app_controller.update_config(section, config)
            except Exception as e:
                print(f"更新配置失败: {section} - {e}")
        
        # 发射配置变化信号
        self.config_changed.emit(config_updates)
        
        # 重新渲染当前图表以应用配置变化
        self.refresh_current_chart()
    
    def refresh_current_chart(self):
        """重新渲染当前图表以应用配置变化"""
        if self.current_chart_data is not None:
            try:
                # 重新生成HTML内容，这次会使用最新的配置
                html_content = self._create_local_heatmap_html_with_config(
                    self.current_chart_data, 
                    self.current_chart_name
                )
                
                # 更新图表显示
                self.chart_view.setHtml(html_content)
                
                # 更新代码预览
                self._update_local_code_preview(self.current_chart_data, self.current_chart_name)
                
                print("✅ 图表配置更新成功")
                
            except Exception as e:
                print(f"❌ 重新渲染图表失败: {e}")
        else:
            # 如果没有当前数据，渲染默认演示图表
            self.render_local_heatmap(self.current_chart_type, self.current_chart_name)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        # 新建项目
        new_action = QAction('新建项目(&N)', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('创建新的热力图项目')
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # 打开配置
        open_action = QAction('打开配置(&O)', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('打开配置文件')
        open_action.triggered.connect(self.open_config)
        file_menu.addAction(open_action)
        
        # 保存配置
        save_action = QAction('保存配置(&S)', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('保存当前配置')
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # 导出图片
        export_image_action = QAction('导出图片(&I)', self)
        export_image_action.setShortcut('Ctrl+E')
        export_image_action.setStatusTip('导出热力图为图片')
        export_image_action.triggered.connect(self.export_image)
        file_menu.addAction(export_image_action)
        
        # 导出代码
        export_code_action = QAction('导出代码(&C)', self)
        export_code_action.setShortcut('Ctrl+Shift+E')
        export_code_action.setStatusTip('导出HTML/JS代码')
        export_code_action.triggered.connect(self.export_code)
        file_menu.addAction(export_code_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('退出应用程序')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 数据菜单
        data_menu = menubar.addMenu('数据(&D)')
        
        # 导入CSV
        import_csv_action = QAction('导入CSV(&C)', self)
        import_csv_action.setStatusTip('从CSV文件导入矩阵数据')
        import_csv_action.triggered.connect(self.import_csv)
        data_menu.addAction(import_csv_action)
        
        # 导入Excel
        import_excel_action = QAction('导入Excel(&E)', self)
        import_excel_action.setStatusTip('从Excel文件导入矩阵数据')
        import_excel_action.triggered.connect(self.import_excel)
        data_menu.addAction(import_excel_action)
        
        data_menu.addSeparator()
        
        # 示例数据
        example_data_action = QAction('加载示例数据(&S)', self)
        example_data_action.setStatusTip('加载内置示例矩阵数据')
        example_data_action.triggered.connect(self.load_example_data)
        data_menu.addAction(example_data_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')
        
        # 重置布局
        reset_layout_action = QAction('重置布局(&R)', self)
        reset_layout_action.setStatusTip('重置窗口布局到默认状态')
        reset_layout_action.triggered.connect(self.reset_layout)
        view_menu.addAction(reset_layout_action)
        
        # 全屏热力图
        fullscreen_chart_action = QAction('全屏热力图(&F)', self)
        fullscreen_chart_action.setShortcut('F11')
        fullscreen_chart_action.setStatusTip('全屏显示热力图')
        fullscreen_chart_action.triggered.connect(self.fullscreen_chart)
        view_menu.addAction(fullscreen_chart_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        # 使用教程
        tutorial_action = QAction('使用教程(&T)', self)
        tutorial_action.setStatusTip('查看使用教程')
        tutorial_action.triggered.connect(self.show_tutorial)
        help_menu.addAction(tutorial_action)
        
        help_menu.addSeparator()
        
        # 关于
        about_action = QAction('关于(&A)', self)
        about_action.setStatusTip('关于ECharts矩阵热力图教学工具')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # 主题菜单
        theme_menu = menubar.addMenu('主题(&T)')
        
        # 浅色主题
        light_theme_action = QAction('浅色主题(&L)', self)
        light_theme_action.setStatusTip('切换到浅色主题')
        light_theme_action.setCheckable(True)
        light_theme_action.triggered.connect(lambda: self.switch_theme('light'))
        theme_menu.addAction(light_theme_action)
        
        # 深色主题
        dark_theme_action = QAction('深色主题(&D)', self)
        dark_theme_action.setStatusTip('切换到深色主题')
        dark_theme_action.setCheckable(True)
        dark_theme_action.triggered.connect(lambda: self.switch_theme('dark'))
        theme_menu.addAction(dark_theme_action)
        
        # 创建主题动作组（确保只能选择一个）
        from PyQt6.QtGui import QActionGroup
        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.addAction(light_theme_action)
        self.theme_action_group.addAction(dark_theme_action)
        
        # 保存主题动作引用，以便更新选中状态
        self.light_theme_action = light_theme_action
        self.dark_theme_action = dark_theme_action
        
        # 根据当前主题设置选中状态
        if self.current_theme == "light":
            light_theme_action.setChecked(True)
        else:
            dark_theme_action.setChecked(True)
    
    def setup_connections(self):
        """设置信号连接"""
        # 配置选项卡切换信号
        self.config_tabs.currentChanged.connect(self.on_config_tab_changed)
        
        # 代码查看器选项卡切换信号
        self.code_viewer.currentChanged.connect(self.on_code_tab_changed)
        
        # 连接应用控制器信号
        self.connect_app_controller_signals()
    
    def load_initial_chart(self):
        """加载初始图表页面"""
        # 显示简单的欢迎消息
        self.statusBar().showMessage("正在初始化ECharts热力图...", 2000)
    
    def update_code_display(self):
        """更新代码显示"""
        # 显示占位内容，实际代码将在加载数据时更新
        html_placeholder = "<!-- HTML代码将在加载数据后显示 -->"
        js_placeholder = "// JavaScript代码将在加载数据后显示"
        
        self.html_editor.setPlainText(html_placeholder)
        self.js_editor.setPlainText(js_placeholder)
    
    def show_welcome_message(self):
        """显示欢迎消息"""
        self.statusBar().showMessage("欢迎使用ECharts矩阵热力图教学工具！", 3000)
    
    # 菜单栏事件处理方法
    def new_project(self):
        """新建项目"""
        reply = QMessageBox.question(self, '新建项目', 
                                   '确定要创建新项目吗？未保存的更改将丢失。',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # 清除应用控制器数据
            self.app_controller.clear_data()
            self.app_controller.reset_config()
            
            # 重置界面
            self.load_initial_chart()
            self.update_code_display()
            self.update_data_info(None)
    
    def open_config(self):
        """打开配置文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '打开配置文件', '', 
            'JSON文件 (*.json);;所有文件 (*)'
        )
        if file_path:
            # 使用应用控制器加载配置
            success = self.app_controller.load_config(file_path)
            if success:
                # 如果有数据，重新渲染图表
                if self.app_controller.get_current_data():
                    code_dict = self.app_controller.generate_code()
                    self.update_code_preview(code_dict)
    
    def save_config(self):
        """保存配置文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存配置文件', '', 
            'JSON文件 (*.json);;所有文件 (*)'
        )
        if file_path:
            # 使用应用控制器保存配置
            success = self.app_controller.save_config(file_path)
            if not success:
                QMessageBox.warning(self, "警告", "配置文件保存失败")
    
    def export_image(self):
        """导出图片"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, '导出图片', '', 
            'PNG文件 (*.png);;JPG文件 (*.jpg);;所有文件 (*)'
        )
        if file_path:
            self.statusBar().showMessage(f"图片已导出: {file_path}", 2000)
    
    def export_code(self):
        """导出代码"""
        # 选择导出类型
        from PyQt6.QtWidgets import QInputDialog
        
        items = ["完整HTML项目", "单独HTML文件", "JavaScript代码"]
        item, ok = QInputDialog.getItem(self, "选择导出类型", "请选择要导出的代码类型:", items, 0, False)
        
        if ok and item:
            if item == "完整HTML项目":
                # 导出完整项目
                folder_path = QFileDialog.getExistingDirectory(self, "选择导出目录")
                if folder_path:
                    success = self.app_controller.export_project(folder_path)
                    if not success:
                        QMessageBox.warning(self, "警告", "项目导出失败")
            else:
                # 导出单个文件
                if item == "单独HTML文件":
                    file_filter = 'HTML文件 (*.html);;所有文件 (*)'
                elif item == "JavaScript代码":
                    file_filter = 'JavaScript文件 (*.js);;所有文件 (*)'
                
                file_path, _ = QFileDialog.getSaveFileName(
                    self, f'导出{item}', '', file_filter
                )
                if file_path:
                    code_dict = self.app_controller.generate_code()
                    if code_dict:
                        try:
                            if item == "单独HTML文件":
                                content = code_dict.get('complete_html', '')
                            elif item == "JavaScript代码":
                                content = code_dict.get('javascript', '')
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        except Exception as e:
                            QMessageBox.critical(self, "错误", f"文件保存失败: {str(e)}")
                    else:
                        QMessageBox.warning(self, "警告", "没有可导出的代码")
    
    def import_csv(self):
        """导入CSV文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '导入CSV文件', '', 
            'CSV文件 (*.csv);;所有文件 (*)'
        )
        if file_path:
            # 直接处理CSV文件并渲染热力图
            success = self.load_and_render_file_data(file_path, "csv")
            if success:
                self.statusBar().showMessage(f"✅ CSV文件导入成功: {file_path}", 3000)
                print(f"✅ CSV文件导入并渲染成功: {file_path}")
            else:
                self.statusBar().showMessage("❌ CSV文件导入失败", 3000)
                print("❌ CSV文件导入失败")
            self.data_imported.emit(file_path)
    
    def import_excel(self):
        """导入Excel文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '导入Excel文件', '', 
            'Excel文件 (*.xlsx *.xls);;所有文件 (*)'
        )
        if file_path:
            # 直接处理Excel文件并渲染热力图
            success = self.load_and_render_file_data(file_path, "excel")
            if success:
                self.statusBar().showMessage(f"✅ Excel文件导入成功: {file_path}", 3000)
                print(f"✅ Excel文件导入并渲染成功: {file_path}")
            else:
                self.statusBar().showMessage("❌ Excel文件导入失败", 3000)
                print("❌ Excel文件导入失败")
            self.data_imported.emit(file_path)
    
    def load_example_data(self):
        """加载示例数据 - 只使用本地ECharts"""
        # 显示示例数据选择对话框
        from PyQt6.QtWidgets import QInputDialog
        
        items = ["相关性矩阵", "随机数据", "模式数据"]
        item, ok = QInputDialog.getItem(self, "选择示例数据", "请选择要加载的示例数据类型:", items, 0, False)
        
        if ok and item:
            # 映射到内部类型
            data_type_map = {
                "相关性矩阵": "correlation",
                "随机数据": "random", 
                "模式数据": "pattern"
            }
            data_type = data_type_map.get(item, "correlation")
            
            # 只使用本地ECharts渲染
            print(f"🔄 加载示例数据: {item}")
            success = self.render_local_heatmap(data_type, item)
            
            if success:
                self.statusBar().showMessage(f"✅ 已加载{item}示例数据 (ECharts)", 3000)
                print(f"✅ {item}示例数据ECharts渲染成功")
            else:
                self.statusBar().showMessage("❌ ECharts加载示例数据失败", 3000)
                print(f"❌ {item}示例数据ECharts渲染失败")

    def force_render_chart(self):
        """强制渲染图表 - 只使用本地ECharts"""
        try:
            print("🔄 强制渲染ECharts图表...")
            
            # 使用本地ECharts渲染，默认显示相关性矩阵
            success = self.render_local_heatmap("correlation", "相关性矩阵")
            
            if success:
                print("✅ ECharts图表渲染成功")
                self.statusBar().showMessage("✅ ECharts图表渲染成功", 2000)
            else:
                print("❌ ECharts图表渲染失败")
                self.statusBar().showMessage("❌ ECharts图表渲染失败", 2000)
                
        except Exception as e:
            print(f"❌ ECharts渲染失败: {e}")
            self.statusBar().showMessage(f"❌ ECharts渲染失败: {str(e)}", 3000)

    def render_local_heatmap(self, data_type: str, display_name: str) -> bool:
        """渲染本地热力图
        
        Args:
            data_type: 数据类型 ("correlation", "random", "pattern")
            display_name: 显示名称
            
        Returns:
            bool: 是否渲染成功
        """
        try:
            # 根据数据类型生成不同的热力图数据
            if data_type == "correlation":
                data_info = self._generate_correlation_data()
            elif data_type == "random":
                data_info = self._generate_random_data()
            elif data_type == "pattern":
                data_info = self._generate_pattern_data()
            else:
                data_info = self._generate_correlation_data()  # 默认
            
            # 保存当前图表状态
            self.current_chart_data = data_info
            self.current_chart_type = data_type
            self.current_chart_name = display_name
            
            # 生成本地HTML（使用配置参数）
            html_content = self._create_local_heatmap_html_with_config(data_info, display_name)
            
            # 显示热力图
            self.chart_view.setHtml(html_content)
            
            # 更新数据信息显示
            self.update_data_info(data_info)
            
            # 更新代码预览
            self._update_local_code_preview(data_info, display_name)
            
            return True
            
        except Exception as e:
            print(f"❌ 本地热力图渲染失败: {e}")
            return False

    def _generate_correlation_data(self) -> dict:
        """生成相关性矩阵数据"""
        subjects = ['数学', '物理', '化学', '英语', '语文']
        data = [
            [1.00, 0.85, 0.67, 0.43, 0.28],
            [0.85, 1.00, 0.73, 0.56, 0.34],
            [0.67, 0.73, 1.00, 0.68, 0.45],
            [0.43, 0.56, 0.68, 1.00, 0.72],
            [0.28, 0.34, 0.45, 0.72, 1.00]
        ]
        
        return {
            'title': '学科成绩相关性矩阵',
            'labels': subjects,
            'data': data,
            'shape': (5, 5),
            'file_path': '相关性矩阵示例',
            'file_type': 'correlation',
            'min_value': 0.0,
            'max_value': 1.0,
            'color_scheme': 'correlation'
        }

    def _generate_random_data(self) -> dict:
        """生成随机数据矩阵"""
        import random
        labels = [f'变量{i+1}' for i in range(6)]
        data = []
        
        for i in range(6):
            row = []
            for j in range(6):
                value = random.uniform(0, 100)
                row.append(round(value, 1))
            data.append(row)
        
        return {
            'title': '随机数据矩阵',
            'labels': labels,
            'data': data,
            'shape': (6, 6),
            'file_path': '随机数据示例',
            'file_type': 'random',
            'min_value': 0.0,
            'max_value': 100.0,
            'color_scheme': 'random'
        }

    def _generate_pattern_data(self) -> dict:
        """生成模式数据矩阵"""
        import math
        labels = [f'节点{i+1}' for i in range(7)]
        data = []
        
        for i in range(7):
            row = []
            for j in range(7):
                # 创建同心圆模式
                center_i, center_j = 3, 3
                distance = math.sqrt((i - center_i)**2 + (j - center_j)**2)
                value = max(0, 50 - distance * 8)
                row.append(round(value, 1))
            data.append(row)
        
        return {
            'title': '模式数据矩阵',
            'labels': labels,
            'data': data,
            'shape': (7, 7),
            'file_path': '模式数据示例',
            'file_type': 'pattern',
            'min_value': 0.0,
            'max_value': 50.0,
            'color_scheme': 'pattern'
        }

    def _get_current_config(self) -> dict:
        """获取当前配置面板的配置参数"""
        config = {}
        
        # 基础配置
        if hasattr(self, 'title_show'):
            config['title'] = {
                'show': self.title_show.isChecked(),
                'text': self.title_text.text() if hasattr(self, 'title_text') else "矩阵热力图",
                'subtext': self.title_subtext.text() if hasattr(self, 'title_subtext') else "",
                'left': self.title_position.currentText() if hasattr(self, 'title_position') else "center",
                'top': self.title_top.value() if hasattr(self, 'title_top') else 20,
                'textStyle': {
                    'fontSize': self.title_font_size.value() if hasattr(self, 'title_font_size') else 18,
                    'color': self.title_color.text() if hasattr(self, 'title_color') else "#333",
                    'fontWeight': self.title_font_weight.currentText() if hasattr(self, 'title_font_weight') else "bold"
                }
            }
        
        # 网格配置
        if hasattr(self, 'grid_height'):
            config['grid'] = {
                'height': f"{self.grid_height.value()}%",
                'top': f"{self.grid_top.value()}%",
                'left': f"{self.grid_left.value()}%",
                'right': f"{self.grid_right.value()}%",
                'bottom': f"{self.grid_bottom.value()}%"
            }
        
        # 坐标轴配置
        if hasattr(self, 'x_axis_label_show'):
            config['xAxis'] = {
                'axisLabel': {
                    'show': self.x_axis_label_show.isChecked(),
                    'fontSize': self.axis_label_font_size.value() if hasattr(self, 'axis_label_font_size') else 12,
                    'color': self.axis_label_color.text() if hasattr(self, 'axis_label_color') else "#666",
                    'rotate': self.x_axis_rotate.value() if hasattr(self, 'x_axis_rotate') else 0
                },
                "axisLine": {
                    "show": self.axis_line_show.isChecked() if hasattr(self, 'axis_line_show') else False
                },
                "axisTick": {
                    "show": self.axis_tick_show.isChecked() if hasattr(self, 'axis_tick_show') else False
                }
            }
            
            config['yAxis'] = {
                "axisLabel": {
                    "show": self.y_axis_label_show.isChecked(),
                    "fontSize": self.axis_label_font_size.value() if hasattr(self, 'axis_label_font_size') else 12,
                    "color": self.axis_label_color.text() if hasattr(self, 'axis_label_color') else "#666"
                },
                "axisLine": {
                    "show": self.axis_line_show.isChecked() if hasattr(self, 'axis_line_show') else False
                },
                "axisTick": {
                    "show": self.axis_tick_show.isChecked() if hasattr(self, 'axis_tick_show') else False
                }
            }
        
        # 视觉映射配置
        if hasattr(self, 'visual_map_show'):
            config['visualMap'] = {
                'show': self.visual_map_show.isChecked(),
                'orient': self.visual_map_orient.currentText() if hasattr(self, 'visual_map_orient') else "vertical",
                'right': f"{self.visual_map_right.value()}%" if hasattr(self, 'visual_map_right') else "5%",
                'top': self.visual_map_top.currentText() if hasattr(self, 'visual_map_top') else "center",
                'itemWidth': self.visual_map_width.value() if hasattr(self, 'visual_map_width') else 20,
                'itemHeight': self.visual_map_height.value() if hasattr(self, 'visual_map_height') else 200,
                'calculable': self.visual_map_calculable.isChecked() if hasattr(self, 'visual_map_calculable') else True,
                'realtime': self.visual_map_realtime.isChecked() if hasattr(self, 'visual_map_realtime') else False,
                'precision': self.visual_map_precision.value() if hasattr(self, 'visual_map_precision') else 1
            }
        
        # 数据标签配置
        if hasattr(self, 'show_labels'):
            config['series'] = {
                'label': {
                    'show': self.show_labels.isChecked(),
                    'fontSize': self.label_font_size.value() if hasattr(self, 'label_font_size') else 10,
                    'color': self.label_color.text() if hasattr(self, 'label_color') else "#333",
                    'fontWeight': self.label_font_weight.currentText() if hasattr(self, 'label_font_weight') else "normal"
                }
            }
        
        # 动画配置
        if hasattr(self, 'animation_enabled'):
            config['animation'] = {
                'animation': self.animation_enabled.isChecked(),
                'animationDuration': self.animation_duration.value() if hasattr(self, 'animation_duration') else 1000,
                'animationEasing': self.animation_easing.currentText() if hasattr(self, 'animation_easing') else "cubicInOut"
            }
        
        return config
    
    def _build_echarts_config_from_ui(self, title: str, labels: list, data: list, 
                                     min_val: float, max_val: float, colors: list, config: dict) -> str:
        """根据UI配置构建ECharts配置对象"""
        
        # 基础配置
        title_config = config.get('title', {})
        grid_config = config.get('grid', {})
        xaxis_config = config.get('xAxis', {})
        yaxis_config = config.get('yAxis', {})
        visual_map_config = config.get('visualMap', {})
        series_config = config.get('series', {})
        animation_config = config.get('animation', {})
        
        echarts_option = {
            'title': {
                'show': title_config.get('show', True),
                'text': title_config.get('text', title),
                'subtext': title_config.get('subtext', ''),
                'left': title_config.get('left', 'center'),
                'top': title_config.get('top', 20),
                'textStyle': title_config.get('textStyle', {
                    'fontSize': 18,
                    'color': '#333',
                    'fontWeight': 'bold'
                })
            },
            'grid': {
                'height': grid_config.get('height', '60%'),
                'top': grid_config.get('top', '15%'),
                'left': grid_config.get('left', '10%'),
                'right': grid_config.get('right', '15%'),
                'bottom': grid_config.get('bottom', '10%')
            },
            'xAxis': {
                'type': 'category',
                'data': labels,
                'splitArea': {'show': True},
                'axisLabel': xaxis_config.get('axisLabel', {
                    'show': True,
                    'fontSize': 12,
                    'color': '#666',
                    'rotate': 0
                }),
                'axisLine': xaxis_config.get('axisLine', {
                    'show': False
                }),
                'axisTick': xaxis_config.get('axisTick', {
                    'show': False
                })
            },
            'yAxis': {
                'type': 'category',
                'data': labels,
                'splitArea': {'show': True},
                'axisLabel': yaxis_config.get('axisLabel', {
                    'show': True,
                    'fontSize': 12,
                    'color': '#666'
                }),
                'axisLine': yaxis_config.get('axisLine', {
                    'show': False
                }),
                'axisTick': yaxis_config.get('axisTick', {
                    'show': False
                })
            },
            'visualMap': {
                'min': min_val,
                'max': max_val,
                'calculable': visual_map_config.get('calculable', True),
                'orient': visual_map_config.get('orient', 'vertical'),
                'right': visual_map_config.get('right', '5%'),
                'top': visual_map_config.get('top', 'center'),
                'itemWidth': visual_map_config.get('itemWidth', 20),
                'itemHeight': visual_map_config.get('itemHeight', 200),
                'realtime': visual_map_config.get('realtime', False),
                'precision': visual_map_config.get('precision', 1),
                'show': visual_map_config.get('show', True),
                'inRange': {'color': colors}
            },
            'series': [{
                'name': '热力图',
                'type': 'heatmap',
                'data': data,
                'label': series_config.get('label', {
                    'show': True,
                    'fontSize': 10,
                    'color': '#333',
                    'fontWeight': 'normal'
                }),
                'emphasis': {
                    'itemStyle': {
                        'shadowBlur': 10,
                        'shadowColor': 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }],
            'animation': animation_config.get('animation', True),
            'animationDuration': animation_config.get('animationDuration', 1000),
            'animationEasing': animation_config.get('animationEasing', 'cubicInOut')
        }
        
        return str(echarts_option).replace("'", '"').replace('True', 'true').replace('False', 'false')
    
    def _create_local_heatmap_html_with_config(self, data_info: dict, display_name: str) -> str:
        """创建使用配置面板参数的本地热力图HTML
        
        Args:
            data_info: 数据信息
            display_name: 显示名称
            
        Returns:
            str: HTML内容
        """
        title = data_info['title']
        labels = data_info['labels']
        data = data_info['data']
        min_val = data_info['min_value']
        max_val = data_info['max_value']
        color_scheme = data_info['color_scheme']
        size = len(labels)
        
        # 从配置面板获取配置参数
        config = self._get_current_config()
        
        # 根据配置调整颜色方案
        if hasattr(self, 'color_scheme') and hasattr(self, 'get_current_color_scheme'):
            visual_colors = self.get_current_color_scheme()
        else:
            # 默认颜色方案
            visual_colors = ['#313695', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027']
        
        # 转换数据格式为ECharts需要的格式
        echarts_data = []
        for i in range(size):
            for j in range(size):
                echarts_data.append([j, i, data[i][j]])
        
        # 获取本地ECharts脚本内容
        echarts_script = self._get_echarts_script_content()
        
        if not echarts_script:
            echarts_script_tag = '<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.0/dist/echarts.min.js"></script>'
            print("⚠️  使用CDN ECharts作为后备")
        else:
            echarts_script_tag = f'<script>{echarts_script}</script>'
            print("✅ 使用本地ECharts脚本")
        
        # 构建ECharts配置对象
        echarts_config = self._build_echarts_config_from_ui(
            title, labels, echarts_data, min_val, max_val, visual_colors, config
        )
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <style>
                body {{ 
                    margin: 0; 
                    padding: 0; 
                    font-family: 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif; 
                    background: #f5f5f5;
                }}
                #chart {{
                    width: 100%;
                    height: 100vh;
                    background: white;
                }}
            </style>
        </head>
        <body>
            <div id="chart"></div>
            {echarts_script_tag}
            <script>
                var chart = echarts.init(document.getElementById('chart'));
                var option = {echarts_config};
                chart.setOption(option);
                
                // 响应式调整
                window.addEventListener('resize', function() {{
                    chart.resize();
                }});
            </script>
        </body>
        </html>
        """
        
        return html_content
    
    def _create_local_heatmap_html(self, data_info: dict, display_name: str) -> str:
        """创建使用本地ECharts的热力图HTML
        
        Args:
            data_info: 数据信息
            display_name: 显示名称
            
        Returns:
            str: HTML内容
        """
        title = data_info['title']
        labels = data_info['labels']
        data = data_info['data']
        min_val = data_info['min_value']
        max_val = data_info['max_value']
        color_scheme = data_info['color_scheme']
        size = len(labels)
        
        # 根据不同数据类型选择颜色方案
        if color_scheme == 'correlation':
            visual_colors = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027']
            legend_text = ['弱相关', '强相关']
        elif color_scheme == 'random':
            visual_colors = ['#440154', '#482777', '#3f4a8a', '#31678e', '#26838f', '#1f9d8a', '#6cce5a', '#b6de2b', '#fee825', '#f0f921']
            legend_text = ['低值', '高值']
        elif color_scheme == 'imported':
            visual_colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83', '#5A9367', '#E63946', '#457B9D', '#F77F00', '#FCBF49']
            legend_text = ['最小值', '最大值']
        else:  # pattern
            visual_colors = ['#0d0887', '#5302a3', '#8b0aa5', '#b83289', '#db5c68', '#f48849', '#febd2a', '#f0f921']
            legend_text = ['边缘', '中心']
        
        # 转换数据格式为ECharts需要的格式
        echarts_data = []
        for i in range(size):
            for j in range(size):
                echarts_data.append([j, i, data[i][j]])
        
        # 获取本地ECharts脚本内容
        echarts_script = self._get_echarts_script_content()
        
        if not echarts_script:
            # 如果无法读取本地ECharts，使用CDN作为后备
            echarts_script_tag = '<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.0/dist/echarts.min.js"></script>'
            print("⚠️  使用CDN ECharts作为后备")
        else:
            # 直接嵌入ECharts代码
            echarts_script_tag = f'<script>{echarts_script}</script>'
            print("✅ 使用本地ECharts脚本")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <style>
                body {{ 
                    margin: 0; 
                    padding: 20px; 
                    font-family: 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif; 
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 300;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 16px;
                }}
                .content {{
                    padding: 20px;
                }}
                #heatmap {{
                    width: 100%;
                    height: 500px;
                    margin: 20px 0;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                    margin-top: 30px;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 10px;
                }}
                .stat-item {{
                    text-align: center;
                    padding: 15px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }}
                .stat-value {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #667eea;
                    margin-bottom: 5px;
                }}
                .stat-label {{
                    font-size: 12px;
                    color: #666;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 {title}</h1>
                    <p>{display_name} - 矩阵尺寸: {size}×{size}</p>
                </div>
                
                <div class="content">
                    <div id="heatmap"></div>
                    
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-value">{size}×{size}</div>
                            <div class="stat-label">矩阵尺寸</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{min_val:.1f}</div>
                            <div class="stat-label">最小值</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{max_val:.1f}</div>
                            <div class="stat-label">最大值</div>
                        </div>
                    </div>
                </div>
            </div>
            
            {echarts_script_tag}
            <script>
                                 // ECharts加载检查
                 function checkEChartsLoaded() {{
                     if (typeof echarts !== 'undefined') {{
                         console.log('✅ ECharts加载成功，版本:', echarts.version);
                         initHeatmap();
                     }} else {{
                         console.log('❌ ECharts加载失败');
                         document.getElementById('heatmap').innerHTML = 
                             '<div style="text-align: center; color: red; padding: 50px;">' +
                             '<h3>❌ ECharts库加载失败</h3>' +
                             '<p>请检查ECharts库文件是否存在</p>' +
                             '<p>使用模式: {("本地嵌入脚本" if echarts_script else "CDN备用")}</p>' +
                             '</div>';
                     }}
                 }}
                
                // 数据配置
                const labels = {labels};
                const data = {echarts_data};
                const minVal = {min_val};
                const maxVal = {max_val};
                const visualColors = {visual_colors};
                const size = {size};
                
                // 初始化ECharts
                function initHeatmap() {{
                    const chartDom = document.getElementById('heatmap');
                    const myChart = echarts.init(chartDom, null, {{
                        renderer: 'canvas',
                        useDirtyRect: false
                    }});
                    
                    // 配置选项
                    const option = {{
                        title: {{
                            text: '{title}',
                            left: 'center',
                            top: 20,
                            textStyle: {{
                                color: '#333',
                                fontSize: 18,
                                fontWeight: 'bold'
                            }}
                        }},
                        tooltip: {{
                            position: 'top',
                            formatter: function(params) {{
                                const xLabel = labels[params.data[0]];
                                const yLabel = labels[params.data[1]];
                                const value = params.data[2];
                                const percentage = ((value - minVal) / (maxVal - minVal) * 100).toFixed(1);
                                return `
                                    <div style="padding: 10px; background: rgba(0,0,0,0.8); color: white; border-radius: 5px;">
                                        <strong>${{xLabel}} × ${{yLabel}}</strong><br/>
                                        数值: <strong>${{value}}</strong><br/>
                                        百分位: <strong>${{percentage}}%</strong>
                                    </div>
                                `;
                            }}
                        }},
                        grid: {{
                            height: '60%',
                            top: '15%',
                            left: '10%',
                            right: '10%'
                        }},
                        xAxis: {{
                            type: 'category',
                            data: labels,
                            splitArea: {{
                                show: false
                            }},
                            axisLabel: {{
                                color: '#666',
                                fontSize: 12
                            }},
                            axisLine: {{
                                show: false
                            }},
                            axisTick: {{
                                show: false
                            }}
                        }},
                        yAxis: {{
                            type: 'category',
                            data: labels,
                            splitArea: {{
                                show: false
                            }},
                            axisLabel: {{
                                color: '#666',
                                fontSize: 12
                            }},
                            axisLine: {{
                                show: false
                            }},
                            axisTick: {{
                                show: false
                            }}
                        }},
                        visualMap: {{
                            min: minVal,
                            max: maxVal,
                            calculable: true,
                            realtime: false,
                            inRange: {{
                                color: visualColors
                            }},
                            text: ['{legend_text[1]}', '{legend_text[0]}'],
                            textStyle: {{
                                color: '#666'
                            }},
                            right: '5%',
                            top: 'center',
                            itemWidth: 20,
                            itemHeight: 200
                        }},
                        series: [{{
                            name: '矩阵热力图',
                            type: 'heatmap',
                            data: data,
                            label: {{
                                show: true,
                                fontSize: 10,
                                color: '#333',
                                formatter: function(params) {{
                                    const value = params.data[2];
                                    return value.toFixed(value % 1 === 0 ? 0 : 1);
                                }}
                            }},
                            emphasis: {{
                                itemStyle: {{
                                    shadowBlur: 10,
                                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                                }}
                            }},
                            itemStyle: {{
                                borderWidth: 1,
                                borderColor: '#fff',
                                borderRadius: 2
                            }}
                        }}]
                    }};
                    
                    // 设置选项并渲染
                    myChart.setOption(option);
                    
                    // 添加点击事件
                    myChart.on('click', function(params) {{
                        const xLabel = labels[params.data[0]];
                        const yLabel = labels[params.data[1]];
                        const value = params.data[2];
                        const percentage = ((value - minVal) / (maxVal - minVal) * 100).toFixed(1);
                        const info = `📍 位置: ${{xLabel}} × ${{yLabel}}\\n📊 数值: ${{value}}\\n📈 百分位: ${{percentage}}%`;
                        alert(info);
                    }});
                    
                    // 自适应窗口大小
                    window.addEventListener('resize', function() {{
                        myChart.resize();
                    }});
                    
                    console.log('✅ ECharts热力图渲染完成: {data_info["file_type"]}');
                }}
                
                // 页面加载完成后初始化
                document.addEventListener('DOMContentLoaded', function() {{
                    // 延迟检查ECharts，确保脚本完全加载
                    setTimeout(checkEChartsLoaded, 100);
                }});
            </script>
        </body>
        </html>
        """
        
        return html_content

    def _create_local_heatmap_html_for_preview(self, data_info: dict, display_name: str) -> str:
        """创建用于代码预览的HTML（不嵌入完整ECharts脚本）
        
        Args:
            data_info: 数据信息
            display_name: 显示名称
            
        Returns:
            str: HTML内容（仅用于预览）
        """
        title = data_info['title']
        labels = data_info['labels']
        data = data_info['data']
        min_val = data_info['min_value']
        max_val = data_info['max_value']
        color_scheme = data_info['color_scheme']
        size = len(labels)
        
        # 根据不同数据类型选择颜色方案
        if color_scheme == 'correlation':
            visual_colors = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027']
            legend_text = ['弱相关', '强相关']
        elif color_scheme == 'random':
            visual_colors = ['#440154', '#482777', '#3f4a8a', '#31678e', '#26838f', '#1f9d8a', '#6cce5a', '#b6de2b', '#fee825', '#f0f921']
            legend_text = ['低值', '高值']
        elif color_scheme == 'imported':
            visual_colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83', '#5A9367', '#E63946', '#457B9D', '#F77F00', '#FCBF49']
            legend_text = ['最小值', '最大值']
        else:  # pattern
            visual_colors = ['#0d0887', '#5302a3', '#8b0aa5', '#b83289', '#db5c68', '#f48849', '#febd2a', '#f0f921']
            legend_text = ['边缘', '中心']
        
        # 转换数据格式为ECharts需要的格式
        echarts_data = []
        for i in range(size):
            for j in range(size):
                echarts_data.append([j, i, data[i][j]])
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <!-- 页面标题 -->
    <title>{title}</title>
    
    <!-- 页面样式定义 -->
    <style>
        /* 页面基础样式 */
        body {{ 
            margin: 0; 
            padding: 20px; 
            font-family: 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        
        /* 主容器样式 */
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        /* 头部样式 */
        .header {{
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 16px;
        }}
        
        /* 内容区域样式 */
        .content {{
            padding: 20px;
        }}
        
        /* 热力图容器样式 */
        #heatmap {{
            width: 100%;
            height: 500px;
            margin: 20px 0;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            background: #fafafa;
        }}
        
        /* 统计信息样式 */
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
    </style>
</head>
<body>
    <!-- 主容器 -->
    <div class="container">
        <!-- 页面头部 -->
        <div class="header">
            <h1>📊 {title}</h1>
            <p>{display_name} - 矩阵尺寸: {size}×{size}</p>
        </div>
        
        <!-- 内容区域 -->
        <div class="content">
            <!-- 热力图容器 -->
            <div id="heatmap"></div>
            
            <!-- 统计信息 -->
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{size}×{size}</div>
                    <div class="stat-label">矩阵尺寸</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{min_val:.1f}</div>
                    <div class="stat-label">最小值</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{max_val:.1f}</div>
                    <div class="stat-label">最大值</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 引入ECharts库 -->
    <script src="./resources/js/echarts.min.js"></script>
    
    <!-- 热力图脚本 -->
    <script>
        // ECharts加载检查函数
        function checkEChartsLoaded() {{
            if (typeof echarts !== 'undefined') {{
                console.log('✅ ECharts加载成功，版本:', echarts.version);
                initHeatmap();
            }} else {{
                console.log('❌ ECharts加载失败');
                document.getElementById('heatmap').innerHTML = 
                    '<div style="text-align: center; color: red; padding: 50px;">' +
                    '<h3>❌ ECharts库加载失败</h3>' +
                    '<p>请检查ECharts库文件是否存在</p>' +
                    '<p>文件路径: ./resources/js/echarts.min.js</p>' +
                    '</div>';
            }}
        }}
        
        // 数据配置
        const labels = {labels};  // 矩阵标签
        const data = {echarts_data};  // 热力图数据 [x, y, value]
        const minVal = {min_val};  // 最小值
        const maxVal = {max_val};  // 最大值
        const visualColors = {visual_colors};  // 颜色方案
        const size = {size};  // 矩阵大小
        
        // 初始化ECharts热力图
        function initHeatmap() {{
            // 获取图表容器
            const chartDom = document.getElementById('heatmap');
            
            // 初始化ECharts实例
            const myChart = echarts.init(chartDom, null, {{
                renderer: 'canvas',  // 使用Canvas渲染
                useDirtyRect: false  // 不使用脏矩形优化
            }});
            
            // 图表配置选项
            const option = {{
                // 图表标题
                title: {{
                    text: '{title}',
                    left: 'center',
                    top: 20,
                    textStyle: {{
                        color: '#333',
                        fontSize: 18,
                        fontWeight: 'bold'
                    }}
                }},
                
                // 提示框配置
                tooltip: {{
                    position: 'top',
                    formatter: function(params) {{
                        const xLabel = labels[params.data[0]];
                        const yLabel = labels[params.data[1]];
                        const value = params.data[2];
                        const percentage = ((value - minVal) / (maxVal - minVal) * 100).toFixed(1);
                        return `
                            <div style="padding: 10px; background: rgba(0,0,0,0.8); color: white; border-radius: 5px;">
                                <strong>${{xLabel}} × ${{yLabel}}</strong><br/>
                                数值: <strong>${{value}}</strong><br/>
                                百分位: <strong>${{percentage}}%</strong>
                            </div>
                        `;
                    }}
                }},
                
                // 网格配置
                grid: {{
                    height: '60%',
                    top: '15%',
                    left: '10%',
                    right: '10%'
                }},
                
                // X轴配置
                xAxis: {{
                    type: 'category',
                    data: labels,
                    splitArea: {{
                        show: false
                    }},
                    axisLabel: {{
                        color: '#666',
                        fontSize: 12
                    }},
                    axisLine: {{
                        show: false
                    }},
                    axisTick: {{
                        show: false
                    }}
                }},
                
                // Y轴配置
                yAxis: {{
                    type: 'category',
                    data: labels,
                    splitArea: {{
                        show: false
                    }},
                    axisLabel: {{
                        color: '#666',
                        fontSize: 12
                    }},
                    axisLine: {{
                        show: false
                    }},
                    axisTick: {{
                        show: false
                    }}
                }},
                
                // 视觉映射配置
                visualMap: {{
                    min: minVal,
                    max: maxVal,
                    calculable: true,
                    realtime: false,
                    inRange: {{
                        color: visualColors
                    }},
                    text: ['{legend_text[1]}', '{legend_text[0]}'],
                    textStyle: {{
                        color: '#666'
                    }},
                    right: '5%',
                    top: 'center',
                    itemWidth: 20,
                    itemHeight: 200
                }},
                
                // 系列配置
                series: [{{
                    name: '矩阵热力图',
                    type: 'heatmap',
                    data: data,
                    label: {{
                        show: true,
                        fontSize: 10,
                        color: '#333',
                        formatter: function(params) {{
                            const value = params.data[2];
                            return value.toFixed(value % 1 === 0 ? 0 : 1);
                        }}
                    }},
                    emphasis: {{
                        itemStyle: {{
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }}
                    }},
                    itemStyle: {{
                        borderWidth: 1,
                        borderColor: '#fff',
                        borderRadius: 2
                    }}
                }}]
            }};
            
            // 设置图表选项
            myChart.setOption(option);
            
            // 添加点击事件
            myChart.on('click', function(params) {{
                const xLabel = labels[params.data[0]];
                const yLabel = labels[params.data[1]];
                const value = params.data[2];
                const percentage = ((value - minVal) / (maxVal - minVal) * 100).toFixed(1);
                const info = `📍 位置: ${{xLabel}} × ${{yLabel}}\\n📊 数值: ${{value}}\\n📈 百分位: ${{percentage}}%`;
                alert(info);
            }});
            
            // 自适应窗口大小
            window.addEventListener('resize', function() {{
                myChart.resize();
            }});
            
            console.log('✅ ECharts热力图渲染完成: {data_info["file_type"]}');
        }}
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {{
            // 延迟检查ECharts，确保脚本完全加载
            setTimeout(checkEChartsLoaded, 100);
        }});
    </script>
</body>
</html>"""
        
        return html_content

    def _update_local_code_preview(self, data_info: dict, display_name: str):
        """更新本地代码预览（显示完整HTML和JavaScript）"""
        try:
            # 转换数据格式
            echarts_data = []
            size = len(data_info["labels"])
            for i in range(size):
                for j in range(size):
                    echarts_data.append([j, i, data_info["data"][i][j]])
            
            # 生成用于预览的HTML代码（不嵌入完整ECharts脚本）
            preview_html = self._create_local_heatmap_html_for_preview(data_info, display_name)

            # 根据数据类型确定颜色方案
            color_scheme = data_info['color_scheme']
            if color_scheme == 'correlation':
                visual_colors = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027']
                legend_text = ['弱相关', '强相关']
            elif color_scheme == 'random':
                visual_colors = ['#440154', '#482777', '#3f4a8a', '#31678e', '#26838f', '#1f9d8a', '#6cce5a', '#b6de2b', '#fee825', '#f0f921']
                legend_text = ['低值', '高值']
            elif color_scheme == 'imported':
                visual_colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83', '#5A9367', '#E63946', '#457B9D', '#F77F00', '#FCBF49']
                legend_text = ['最小值', '最大值']
            else:  # pattern
                visual_colors = ['#0d0887', '#5302a3', '#8b0aa5', '#b83289', '#db5c68', '#f48849', '#febd2a', '#f0f921']
                legend_text = ['边缘', '中心']

            # 生成ECharts JavaScript代码示例（带详细注释）
            js_code = f'''/* 
 * {data_info["title"]} - ECharts热力图配置
 * 这个脚本演示了如何使用ECharts创建矩阵热力图
 * 数据类型: {data_info["file_type"]}
 * 生成时间: {{"new Date().toLocaleString()"}}
 */

// =================
// 第一步：准备数据
// =================

// 矩阵标签 - 用于显示坐标轴
const labels = {data_info["labels"]};

// 原始矩阵数据 - 二维数组格式
const matrixData = {data_info["data"]};

// 数据范围 - 用于颜色映射
const minValue = {data_info["min_value"]};  // 最小值
const maxValue = {data_info["max_value"]};  // 最大值

// 矩阵尺寸
const matrixSize = {size};

// 颜色方案 - 从低到高的颜色渐变
const colorScheme = {visual_colors};

// 图例文本 - 用于显示颜色条的标签
const legendLabels = {legend_text};

// =================
// 第二步：数据转换
// =================

// 将二维矩阵转换为ECharts热力图需要的格式
// 格式: [x坐标, y坐标, 数值]
const echartsData = [];
for (let i = 0; i < matrixData.length; i++) {{
    for (let j = 0; j < matrixData[i].length; j++) {{
        // 添加数据点 [列索引, 行索引, 值]
        echartsData.push([j, i, matrixData[i][j]]);
    }}
}}

// 输出数据信息到控制台
console.log('📊 数据信息:', {{
    'title': '{data_info["title"]}',
    'size': `${{matrixSize}}×${{matrixSize}}`,
    'dataPoints': echartsData.length,
    'range': `${{minValue}} - ${{maxValue}}`,
    'colorScheme': '{color_scheme}'
}});

// =================
// 第三步：初始化图表
// =================

// 获取图表容器DOM元素
const chartDom = document.getElementById('heatmap');

// 初始化ECharts实例
const myChart = echarts.init(chartDom, null, {{
    renderer: 'canvas',      // 使用Canvas渲染（性能更好）
    useDirtyRect: false,     // 禁用脏矩形优化（确保完整渲染）
    width: 'auto',           // 自动宽度
    height: 'auto'           // 自动高度
}});

// =================
// 第四步：配置图表选项
// =================

const option = {{
    // 图表标题配置
    title: {{
        text: '{data_info["title"]}',        // 主标题
        left: 'center',                      // 水平居中
        top: 20,                             // 顶部间距
        textStyle: {{
            color: '#333',                   // 标题颜色
            fontSize: 18,                    // 字体大小
            fontWeight: 'bold'               // 字体粗细
        }}
    }},
    
    // 提示框配置
    tooltip: {{
        position: 'top',                     // 显示在鼠标上方
        trigger: 'item',                     // 触发方式
        backgroundColor: 'rgba(0,0,0,0.8)',  // 背景色
        borderColor: '#333',                 // 边框色
        borderWidth: 1,                      // 边框宽度
        textStyle: {{
            color: '#fff',                   // 文字颜色
            fontSize: 12                     // 字体大小
        }},
        // 自定义提示框内容
        formatter: function(params) {{
            const xLabel = labels[params.data[0]];  // X轴标签
            const yLabel = labels[params.data[1]];  // Y轴标签
            const value = params.data[2];            // 数值
            // 计算百分位
            const percentage = ((value - minValue) / (maxValue - minValue) * 100).toFixed(1);
            
            return `
                <div style="padding: 10px; border-radius: 5px;">
                    <strong>${{xLabel}} × ${{yLabel}}</strong><br/>
                    数值: <strong>${{value}}</strong><br/>
                    百分位: <strong>${{percentage}}%</strong>
                </div>
            `;
        }}
    }},
    
    // 网格配置 - 定义图表在容器中的位置
    grid: {{
        height: '60%',                      // 图表高度
        top: '15%',                         // 顶部间距
        left: '10%',                        // 左侧间距
        right: '10%'                        // 右侧间距
    }},
    
    // X轴配置
    xAxis: {{
        type: 'category',                   // 类目轴
        data: labels,                       // 轴数据
        splitArea: {{
            show: false                     // 不显示网格区域
        }},
        axisLabel: {{
            color: '#666',                  // 标签颜色
            fontSize: 12,                   // 字体大小
            rotate: 0,                      // 旋转角度
            margin: 8                       // 标签间距
        }},
        axisLine: {{
            show: false                     // 不显示轴线
        }},
        axisTick: {{
            show: false                     // 不显示刻度
        }}
    }},
    
    // Y轴配置
    yAxis: {{
        type: 'category',                   // 类目轴
        data: labels,                       // 轴数据
        splitArea: {{
            show: false                     // 不显示网格区域
        }},
        axisLabel: {{
            color: '#666',                  // 标签颜色
            fontSize: 12,                   // 字体大小
            margin: 8                       // 标签间距
        }},
        axisLine: {{
            show: false                     // 不显示轴线
        }},
        axisTick: {{
            show: false                     // 不显示刻度
        }}
    }},
    
    // 视觉映射配置 - 控制颜色映射
    visualMap: {{
        min: minValue,                      // 最小值
        max: maxValue,                      // 最大值
        calculable: true,                   // 启用拖拽手柄
        realtime: false,                    // 不实时更新
        inRange: {{
            color: colorScheme              // 颜色范围
        }},
        text: [legendLabels[1], legendLabels[0]], // 图例文本
        textStyle: {{
            color: '#666',                  // 文字颜色
            fontSize: 12                    // 字体大小
        }},
        right: '5%',                        // 右侧位置
        top: 'center',                      // 垂直居中
        orient: 'vertical',                 // 垂直方向
        itemWidth: 20,                      // 图例宽度
        itemHeight: 200,                    // 图例高度
        precision: 1                        // 数值精度
    }},
    
    // 系列配置 - 定义热力图
    series: [{{
        name: '矩阵热力图',                 // 系列名称
        type: 'heatmap',                    // 图表类型
        data: echartsData,                  // 数据
        
        // 标签配置
        label: {{
            show: true,                     // 显示标签
            fontSize: 10,                   // 字体大小
            color: '#333',                  // 字体颜色
            fontWeight: 'bold',             // 字体粗细
            // 自定义标签格式
            formatter: function(params) {{
                const value = params.data[2];
                // 整数不显示小数位，小数显示1位
                return value.toFixed(value % 1 === 0 ? 0 : 1);
            }}
        }},
        
        // 高亮配置
        emphasis: {{
            itemStyle: {{
                shadowBlur: 10,             // 阴影模糊
                shadowColor: 'rgba(0, 0, 0, 0.5)' // 阴影颜色
            }}
        }},
        
        // 样式配置
        itemStyle: {{
            borderWidth: 1,                 // 边框宽度
            borderColor: '#fff',            // 边框颜色
            borderRadius: 2                 // 圆角半径
        }}
    }}]
}};

// =================
// 第五步：渲染图表
// =================

// 设置配置选项并渲染图表
myChart.setOption(option);

// 输出渲染完成信息
console.log('✅ 图表渲染完成:', {{
    'chartType': 'heatmap',
    'renderer': 'canvas',
    'dataPoints': echartsData.length,
    'timestamp': new Date().toLocaleString()
}});

// =================
// 第六步：事件处理
// =================

// 添加点击事件处理
myChart.on('click', function(params) {{
    console.log('👆 用户点击:', params);
    
    // 获取点击位置的信息
    const xLabel = labels[params.data[0]];
    const yLabel = labels[params.data[1]];
    const value = params.data[2];
    const percentage = ((value - minValue) / (maxValue - minValue) * 100).toFixed(1);
    
    // 显示详细信息
    const info = `📍 位置: ${{xLabel}} × ${{yLabel}}\\n📊 数值: ${{value}}\\n📈 百分位: ${{percentage}}%`;
    alert(info);
}});

// 添加双击事件处理
myChart.on('dblclick', function(params) {{
    console.log('🖱️ 用户双击:', params);
    
    // 可以在这里添加双击后的操作
    // 例如：放大到特定区域、显示详细信息等
}});

// 添加鼠标悬停事件处理
myChart.on('mouseover', function(params) {{
    // 鼠标悬停时的操作
    console.log('🔍 鼠标悬停:', params.data);
}});

// =================
// 第七步：响应式处理
// =================

// 窗口大小变化时自动调整图表大小
window.addEventListener('resize', function() {{
    myChart.resize();
    console.log('📏 图表已调整大小');
}});

// 监听容器大小变化
const resizeObserver = new ResizeObserver(function(entries) {{
    myChart.resize();
}});
resizeObserver.observe(chartDom);

// =================
// 第八步：完成回调
// =================

console.log('🎉 ECharts热力图初始化完成!');
console.log('💡 使用提示:');
console.log('   - 鼠标悬停查看数值');
console.log('   - 点击数据点查看详细信息');
console.log('   - 拖拽颜色条调整显示范围');
console.log('   - 窗口大小变化时图表自动调整');'''

            # 更新代码编辑器
            self.html_editor.setPlainText(preview_html)
            self.js_editor.setPlainText(js_code)
            
        except Exception as e:
            print(f"❌ 更新代码预览失败: {e}")

    def reset_layout(self):
        """重置布局"""
        self.statusBar().showMessage("布局已重置", 2000)
    
    def fullscreen_chart(self):
        """全屏显示热力图"""
        self.statusBar().showMessage("热力图全屏显示（ESC退出）", 2000)
    
    def show_tutorial(self):
        """显示使用教程"""
        QMessageBox.information(self, '使用教程', 
                              '欢迎使用ECharts矩阵热力图教学工具！\n\n'
                              '基本步骤：\n'
                              '1. 导入或创建矩阵数据\n'
                              '2. 在配置面板调整样式\n'
                              '3. 预览实时效果\n'
                              '4. 导出图片或代码\n\n'
                              '更多帮助请参考文档。')
    
    def show_about(self):
        """显示关于信息"""
        QMessageBox.about(self, '关于', 
                         '<h3>ECharts矩阵热力图教学工具</h3>'
                         '<p>版本: 1.0.0</p>'
                         '<p>一个专门用于教学的矩阵热力图可视化工具</p>'
                         '<p>基于Python + PyQt6 + ECharts开发</p>'
                         '<p><b>主要功能:</b></p>'
                         '<ul>'
                         '<li>实时矩阵热力图预览</li>'
                         '<li>可视化配置界面</li>'
                         '<li>代码生成和导出</li>'
                         '<li>多种数据格式支持</li>'
                         '</ul>')
    
    def on_config_tab_changed(self, index):
        """配置选项卡切换事件"""
        tab_names = ["数据配置", "样式配置", "交互配置", "动画配置"]
        if 0 <= index < len(tab_names):
            self.statusBar().showMessage(f"当前: {tab_names[index]}", 1000)
    
    def on_code_tab_changed(self, index):
        """代码选项卡切换事件"""
        tab_names = ["HTML", "JavaScript"]
        if 0 <= index < len(tab_names):
            self.statusBar().showMessage(f"代码预览: {tab_names[index]}", 1000)
    
    # 应用控制器信号处理方法
    def on_status_changed(self, status_text):
        """状态变化处理"""
        self.status_label.setText(status_text)
        
    def on_error_occurred(self, error_msg):
        """错误处理"""
        self.status_label.setText(f"错误: {error_msg}")
        QMessageBox.critical(self, "错误", error_msg)
        
    def on_progress_updated(self, value):
        """进度更新处理"""
        if value > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(value)
        else:
            self.progress_bar.setVisible(False)
    
    def update_data_info(self, data_info):
        """更新数据信息显示"""
        if data_info:
            shape = data_info.get('shape', (0, 0))
            file_path = data_info.get('file_path', '未知')
            info_text = f"数据: {shape[0]}×{shape[1]} | {file_path}"
            self.data_info_label.setText(info_text)
        else:
            self.data_info_label.setText("")
    
    def update_code_preview(self, code_dict):
        """更新代码预览"""
        if 'html' in code_dict:
            self.html_editor.setPlainText(code_dict['html'])
        if 'javascript' in code_dict:
            self.js_editor.setPlainText(code_dict['javascript'])

    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(self, '确认退出', 
                                   '确定要退出应用程序吗？',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # 保存主题设置
            self.save_theme_settings()
            event.accept()
        else:
            event.ignore()
    
    def switch_theme(self, theme_name):
        """切换主题"""
        if theme_name != self.current_theme:
            self.current_theme = theme_name
            self.load_stylesheet()
            self.save_theme_settings()
            
            # 更新菜单项选中状态
            if hasattr(self, 'light_theme_action') and hasattr(self, 'dark_theme_action'):
                if theme_name == "light":
                    self.light_theme_action.setChecked(True)
                    self.dark_theme_action.setChecked(False)
                else:
                    self.light_theme_action.setChecked(False)
                    self.dark_theme_action.setChecked(True)
            
            # 状态栏提示
            theme_names = {"light": "浅色主题", "dark": "深色主题"}
            self.status_label.setText(f"已切换到{theme_names[theme_name]}")
    
    def on_theme_changed(self, index):
        """主题变更事件处理（保留兼容性）"""
        theme_options = ["light", "dark"]
        new_theme = theme_options[index]
        self.switch_theme(new_theme)
    
    def load_theme_settings(self):
        """加载主题设置"""
        try:
            config_dir = os.path.join(os.path.dirname(__file__), "../../config")
            config_file = os.path.join(config_dir, "theme_settings.json")
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    import json
                    settings = json.load(f)
                    self.current_theme = settings.get('theme', 'light')
                    print(f"已加载主题设置: {self.current_theme}")
            else:
                print("未找到主题设置文件，使用默认主题")
        except Exception as e:
            print(f"加载主题设置失败: {e}")
            self.current_theme = "light"
    
    def save_theme_settings(self):
        """保存主题设置"""
        try:
            config_dir = os.path.join(os.path.dirname(__file__), "../../config")
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = os.path.join(config_dir, "theme_settings.json")
            
            import json
            from datetime import datetime
            settings = {
                'theme': self.current_theme,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            print(f"主题设置已保存: {self.current_theme}")
        except Exception as e:
            print(f"保存主题设置失败: {e}")
    
    def test_load_example_data(self):
        """测试加载示例数据 - 只使用ECharts"""
        try:
            print("🔄 测试加载示例数据...")
            # 直接使用本地ECharts渲染
            success = self.render_local_heatmap("correlation", "学科成绩相关性矩阵")
            
            if success:
                self.status_label.setText("ECharts示例数据加载成功")
                print("✅ ECharts示例数据加载成功")
            else:
                self.status_label.setText("ECharts示例数据加载失败")
                print("❌ ECharts示例数据加载失败")
        except Exception as e:
            self.status_label.setText(f"加载示例数据时出错: {str(e)}")
            print(f"❌ 加载示例数据时出错: {e}")
    
    def show_initial_echarts_demo(self):
        """显示初始ECharts演示图表"""
        try:
            print("🔄 显示初始ECharts演示图表...")
            
            # 检查ECharts文件是否存在
            current_dir = os.path.dirname(os.path.abspath(__file__))
            echarts_path = os.path.join(current_dir, '../../resources/js/echarts.min.js')
            echarts_normalized = os.path.normpath(echarts_path)
            
            if not os.path.exists(echarts_normalized):
                print(f"❌ ECharts文件不存在: {echarts_normalized}")
                self.statusBar().showMessage(f"❌ ECharts文件不存在: {echarts_normalized}", 5000)
                return
            
            print(f"✅ ECharts文件存在: {echarts_normalized}")
            
            success = self.render_local_heatmap("correlation", "学科成绩相关性矩阵")
            
            if success:
                print("✅ ECharts演示图表加载成功")
                self.statusBar().showMessage("✅ ECharts演示图表已加载", 3000)
            else:
                print("❌ ECharts演示图表加载失败")
                self.statusBar().showMessage("❌ ECharts演示图表加载失败", 3000)
        
        except Exception as e:
            print(f"❌ ECharts演示图表加载异常: {e}")
            self.statusBar().showMessage(f"❌ ECharts演示图表加载异常: {str(e)}", 3000)
    
    def load_and_render_file_data(self, file_path: str, file_type: str) -> bool:
        """加载并渲染文件数据
        
        Args:
            file_path: 文件路径
            file_type: 文件类型 ("csv" 或 "excel")
            
        Returns:
            bool: 是否加载并渲染成功
        """
        try:
            print(f"🔄 加载{file_type.upper()}文件: {file_path}")
            
            # 读取文件数据
            if file_type == "csv":
                data_info = self._load_csv_data(file_path)
            elif file_type == "excel":
                data_info = self._load_excel_data(file_path)
            else:
                print(f"❌ 不支持的文件类型: {file_type}")
                return False
            
            if not data_info:
                print("❌ 文件数据加载失败")
                return False
            
            # 渲染热力图
            success = self.render_file_heatmap(data_info, file_path)
            return success
            
        except Exception as e:
            print(f"❌ 加载并渲染文件数据失败: {e}")
            return False
    
    def _load_csv_data(self, file_path: str) -> dict:
        """加载CSV文件数据"""
        try:
            import pandas as pd
            import os
            
            # 读取CSV文件
            df = pd.read_csv(file_path, index_col=0)
            
            # 验证数据
            if df.empty:
                print("❌ CSV文件为空")
                return None
            
            # 转换为矩阵数据
            data = df.values.tolist()
            labels = df.index.tolist()
            
            # 计算数值范围
            flat_data = [val for row in data for val in row if isinstance(val, (int, float))]
            min_val = min(flat_data) if flat_data else 0
            max_val = max(flat_data) if flat_data else 1
            
            # 获取文件名
            file_name = os.path.basename(file_path)
            
            return {
                'title': f'导入数据: {file_name}',
                'labels': labels,
                'data': data,
                'shape': (len(data), len(data[0]) if data else 0),
                'file_path': file_path,
                'file_type': 'imported_csv',
                'min_value': min_val,
                'max_value': max_val,
                'color_scheme': 'imported'
            }
            
        except Exception as e:
            print(f"❌ CSV文件读取失败: {e}")
            return None
    
    def _load_excel_data(self, file_path: str) -> dict:
        """加载Excel文件数据"""
        try:
            import pandas as pd
            import os
            
            # 读取Excel文件
            df = pd.read_excel(file_path, index_col=0)
            
            # 验证数据
            if df.empty:
                print("❌ Excel文件为空")
                return None
            
            # 转换为矩阵数据
            data = df.values.tolist()
            labels = df.index.tolist()
            
            # 计算数值范围
            flat_data = [val for row in data for val in row if isinstance(val, (int, float))]
            min_val = min(flat_data) if flat_data else 0
            max_val = max(flat_data) if flat_data else 1
            
            # 获取文件名
            file_name = os.path.basename(file_path)
            
            return {
                'title': f'导入数据: {file_name}',
                'labels': labels,
                'data': data,
                'shape': (len(data), len(data[0]) if data else 0),
                'file_path': file_path,
                'file_type': 'imported_excel',
                'min_value': min_val,
                'max_value': max_val,
                'color_scheme': 'imported'
            }
            
        except Exception as e:
            print(f"❌ Excel文件读取失败: {e}")
            return None
    
    def render_file_heatmap(self, data_info: dict, file_path: str) -> bool:
        """渲染导入文件的热力图
        
        Args:
            data_info: 数据信息
            file_path: 文件路径
            
        Returns:
            bool: 是否渲染成功
        """
        try:
            import os
            file_name = os.path.basename(file_path)
            
            # 生成HTML内容
            html_content = self._create_local_heatmap_html(data_info, f"导入数据: {file_name}")
            
            # 显示热力图
            self.chart_view.setHtml(html_content)
            
            # 更新数据信息显示
            self.update_data_info(data_info)
            
            # 更新代码预览
            self._update_local_code_preview(data_info, f"导入数据: {file_name}")
            
            print(f"✅ 文件热力图渲染成功: {file_name}")
            return True
            
        except Exception as e:
            print(f"❌ 文件热力图渲染失败: {e}")
            return False

    def _get_echarts_script_content(self) -> str:
        """获取本地ECharts脚本内容"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            echarts_path = os.path.join(current_dir, '../../resources/js/echarts.min.js')
            echarts_normalized = os.path.normpath(echarts_path)
            
            if os.path.exists(echarts_normalized):
                with open(echarts_normalized, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                print(f"❌ ECharts文件不存在: {echarts_normalized}")
                return ""
        except Exception as e:
            print(f"❌ 读取ECharts文件失败: {e}")
            return ""



if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 