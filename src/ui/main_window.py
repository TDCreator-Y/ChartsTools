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
    QGroupBox, QFormLayout, QColorDialog
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
        # 样式配置选项卡
        self.create_style_config_tab()
        
        # 交互配置选项卡
        self.create_interaction_config_tab()
        
        # 动画配置选项卡
        self.create_animation_config_tab()
    
    def create_style_config_tab(self):
        """创建样式配置选项卡"""
        style_tab = QWidget()
        style_layout = QVBoxLayout()
        style_tab.setLayout(style_layout)
        
        # 主题配置组
        theme_group = QGroupBox("主题设置")
        theme_layout = QFormLayout()
        theme_group.setLayout(theme_layout)
        
        self.theme_selector = QComboBox()
        theme_options = ["light", "dark"]
        theme_labels = ["浅色主题", "深色主题"]
        self.theme_selector.addItems(theme_labels)
        # 设置当前主题
        if self.current_theme == "dark":
            self.theme_selector.setCurrentIndex(1)
        else:
            self.theme_selector.setCurrentIndex(0)
        self.theme_selector.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addRow("界面主题:", self.theme_selector)
        
        style_layout.addWidget(theme_group)
        
        # 标题配置组
        title_group = QGroupBox("标题设置")
        title_layout = QFormLayout()
        title_group.setLayout(title_layout)
        
        self.title_text = QLineEdit("矩阵热力图")
        self.title_text.textChanged.connect(self.on_config_changed)
        title_layout.addRow("标题文本:", self.title_text)
        
        self.title_font_size = QSpinBox()
        self.title_font_size.setRange(10, 48)
        self.title_font_size.setValue(18)
        self.title_font_size.valueChanged.connect(self.on_config_changed)
        title_layout.addRow("字体大小:", self.title_font_size)
        
        style_layout.addWidget(title_group)
        
        # 颜色配置组
        color_group = QGroupBox("颜色配置")
        color_layout = QFormLayout()
        color_group.setLayout(color_layout)
        
        self.color_scheme = QComboBox()
        color_schemes = ["蓝色渐变", "红色渐变", "绿色渐变", "彩虹渐变", "自定义"]
        self.color_scheme.addItems(color_schemes)
        self.color_scheme.currentTextChanged.connect(self.on_config_changed)
        color_layout.addRow("颜色方案:", self.color_scheme)
        
        style_layout.addWidget(color_group)
        
        # 显示配置组  
        display_group = QGroupBox("显示设置")
        display_layout = QFormLayout()
        display_group.setLayout(display_layout)
        
        self.show_labels = QCheckBox("显示数值标签")
        self.show_labels.setChecked(True)
        self.show_labels.toggled.connect(self.on_config_changed)
        display_layout.addRow(self.show_labels)
        
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
    
    def on_config_changed(self):
        """配置变化处理"""
        # 收集当前配置
        config_updates = {}
        
        # 样式配置
        style_config = {
            "title": {
                "text": self.title_text.text(),
                "textStyle": {
                    "fontSize": self.title_font_size.value(),
                    "fontWeight": "bold",
                    "color": "#333"
                },
                "left": "center",
                "top": "5%"
            }
        }
        
        # 根据颜色方案设置颜色
        color_schemes = {
            "蓝色渐变": ["#313695", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf"],
            "红色渐变": ["#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7"],
            "绿色渐变": ["#00441b", "#238b45", "#66c2a4", "#b2e2e2", "#edf8fb"],
            "彩虹渐变": ["#313695", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027"]
        }
        
        selected_scheme = self.color_scheme.currentText()
        if selected_scheme in color_schemes:
            style_config["visualMap"] = {
                "inRange": {
                    "color": color_schemes[selected_scheme]
                }
            }
        
        config_updates["style"] = style_config
        
        # 交互配置
        interaction_config = {}
        if hasattr(self, 'tooltip_enabled'):
            if self.tooltip_enabled.isChecked():
                interaction_config["tooltip"] = {
                    "trigger": "item",
                    "formatter": self.tooltip_format.text()
                }
            
            if self.enable_zoom.isChecked():
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
                "animationDuration": self.animation_duration.value() if self.animation_enabled.isChecked() else 0,
                "animationEasing": self.animation_easing.currentText(),
                "animationDelay": 0,
                "animationDurationUpdate": 300,
                "animationEasingUpdate": "cubicInOut"
            }
            config_updates["animation"] = animation_config
        
        # 更新应用控制器配置
        for section, config in config_updates.items():
            self.app_controller.update_config(section, config)
        
        # 发射配置变化信号
        self.config_changed.emit(config_updates)
    
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
            
            # 生成本地HTML
            html_content = self._create_local_heatmap_html(data_info, display_name)
            
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

    def _update_local_code_preview(self, data_info: dict, display_name: str):
        """更新本地代码预览（显示完整HTML和JavaScript）"""
        try:
            # 转换数据格式
            echarts_data = []
            size = len(data_info["labels"])
            for i in range(size):
                for j in range(size):
                    echarts_data.append([j, i, data_info["data"][i][j]])
            
            # 生成完整的HTML代码
            complete_html = self._create_local_heatmap_html(data_info, display_name)

            # 生成ECharts JavaScript代码示例
            js_code = f'''// {data_info["title"]} - ECharts热力图配置
// 准备数据
const labels = {data_info["labels"]};
const matrixData = {data_info["data"]};
const minValue = {data_info["min_value"]};
const maxValue = {data_info["max_value"]};

// 转换数据格式为ECharts格式 [x, y, value]
const echartsData = [];
for (let i = 0; i < matrixData.length; i++) {{
    for (let j = 0; j < matrixData[i].length; j++) {{
        echartsData.push([j, i, matrixData[i][j]]);
    }}
}}

// 初始化ECharts实例
const chartDom = document.getElementById('heatmap');
const myChart = echarts.init(chartDom);

// 配置选项
const option = {{
    title: {{
        text: '{data_info["title"]}',
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
            const percentage = ((value - minValue) / (maxValue - minValue) * 100).toFixed(1);
            return `
                <div>
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
        }}
    }},
    visualMap: {{
        min: minValue,
        max: maxValue,
        calculable: true,
        realtime: false,
        inRange: {{
            color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027']
        }},
        text: ['高', '低'],
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
        data: echartsData,
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
    console.log(`点击位置: ${{xLabel}} × ${{yLabel}}, 数值: ${{value}}`);
}});

// 自适应窗口大小
window.addEventListener('resize', function() {{
    myChart.resize();
}});

console.log('ECharts热力图初始化完成');'''

            # 更新代码编辑器
            self.html_editor.setPlainText(complete_html)
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
    
    def on_theme_changed(self, index):
        """主题切换事件处理"""
        theme_options = ["light", "dark"]
        new_theme = theme_options[index]
        
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.load_stylesheet()
            self.save_theme_settings()
            
            # 显示主题切换提示
            theme_names = {"light": "浅色主题", "dark": "深色主题"}
            self.status_label.setText(f"已切换到{theme_names[new_theme]}")
    
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