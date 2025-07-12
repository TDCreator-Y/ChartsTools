#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用控制器模块
负责协调各个核心模块的交互，管理整个应用的状态
"""

from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView

from .config_manager import ConfigManager
from .data_manager import DataManager
from .chart_renderer import ChartRenderer
from .code_generator import CodeGenerator


class AppController(QObject):
    """应用控制器类
    
    负责协调各个核心模块的交互，包括：
    - 管理应用状态
    - 协调模块间通信
    - 处理用户操作流程
    - 提供统一的API接口
    """
    
    # 状态变化信号
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        
        # 初始化核心模块
        self.config_manager = ConfigManager()
        self.data_manager = DataManager()
        self.chart_renderer = ChartRenderer()
        self.code_generator = CodeGenerator()
        
        # 应用状态
        self._current_data = None
        self._current_config = None
        self._is_initialized = False
        
        # 连接信号
        self._connect_signals()
    
    def _connect_signals(self):
        """连接各模块间的信号"""
        # 配置管理器信号
        self.config_manager.config_changed.connect(self._on_config_changed)
        
        # 数据管理器信号
        self.data_manager.data_loaded.connect(self._on_data_loaded)
        self.data_manager.data_error.connect(self._on_data_error)
        
        # 图表渲染器信号
        self.chart_renderer.chart_rendered.connect(self._on_chart_rendered)
        self.chart_renderer.chart_error.connect(self._on_chart_error)
        
        # 代码生成器信号
        self.code_generator.code_generated.connect(self._on_code_generated)
        self.code_generator.code_error.connect(self._on_code_error)
    
    def initialize(self, web_view: QWebEngineView) -> bool:
        """初始化应用控制器
        
        Args:
            web_view: WebEngine视图组件
            
        Returns:
            bool: 是否初始化成功
        """
        try:
            # 设置图表渲染器的WebEngine视图
            self.chart_renderer.set_web_view(web_view)
            
            # 加载默认配置
            self._current_config = self.config_manager.get_config()
            
            self._is_initialized = True
            self.status_changed.emit("应用初始化完成")
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"初始化失败: {str(e)}")
            return False
    
    def load_data_from_file(self, file_path: str, file_type: str = "auto") -> bool:
        """从文件加载数据
        
        Args:
            file_path: 文件路径
            file_type: 文件类型 ("auto", "csv", "excel")
            
        Returns:
            bool: 是否加载成功
        """
        if not self._is_initialized:
            self.error_occurred.emit("应用未初始化")
            return False
        
        try:
            self.status_changed.emit("正在加载数据...")
            self.progress_updated.emit(25)
            
            # 根据文件类型加载数据
            if file_type == "auto":
                if file_path.lower().endswith('.csv'):
                    file_type = "csv"
                elif file_path.lower().endswith(('.xlsx', '.xls')):
                    file_type = "excel"
                else:
                    self.error_occurred.emit("不支持的文件类型")
                    return False
            
            success = False
            if file_type == "csv":
                success = self.data_manager.load_csv_file(file_path)
            elif file_type == "excel":
                success = self.data_manager.load_excel_file(file_path)
            
            self.progress_updated.emit(50)
            return success
            
        except Exception as e:
            self.error_occurred.emit(f"加载数据失败: {str(e)}")
            return False
    
    def load_example_data(self, data_type: str = "correlation") -> bool:
        """加载示例数据
        
        Args:
            data_type: 数据类型 ("correlation", "random", "pattern")
            
        Returns:
            bool: 是否加载成功
        """
        if not self._is_initialized:
            self.error_occurred.emit("应用未初始化")
            return False
        
        try:
            self.status_changed.emit("正在加载示例数据...")
            print(f"🔄 加载示例数据类型: {data_type}")
            
            # 获取示例数据
            example_data = self.data_manager.get_example_data(data_type)
            
            if example_data:
                self._current_data = example_data
                self._update_data_config()
                
                print(f"✅ 示例数据加载成功: {example_data.get('shape', 'Unknown')}")
                print(f"✅ 矩阵数据长度: {len(example_data.get('matrix_data', []))}")
                print(f"✅ 行标签: {example_data.get('row_labels', [])}")
                print(f"✅ 列标签: {example_data.get('col_labels', [])}")
                
                self.status_changed.emit("示例数据加载完成")
                
                # 触发数据加载完成事件
                self._on_data_loaded(example_data)
                
                return True
            else:
                print("❌ 获取示例数据失败")
                self.error_occurred.emit("加载示例数据失败")
                return False
                
        except Exception as e:
            print(f"❌ 加载示例数据异常: {e}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"加载示例数据失败: {str(e)}")
            return False
    
    def render_chart(self) -> bool:
        """渲染图表
        
        Returns:
            bool: 是否渲染成功
        """
        if not self._is_initialized:
            self.error_occurred.emit("应用未初始化")
            return False
        
        if not self._current_data:
            self.error_occurred.emit("没有可用数据")
            return False
        
        try:
            self.status_changed.emit("正在渲染图表...")
            self.progress_updated.emit(75)
            
            # 渲染图表
            success = self.chart_renderer.render_heatmap(
                self._current_data, 
                self._current_config
            )
            
            self.progress_updated.emit(100)
            return success
            
        except Exception as e:
            self.error_occurred.emit(f"渲染图表失败: {str(e)}")
            return False
    
    def generate_code(self) -> Dict[str, str]:
        """生成代码
        
        Returns:
            Dict[str, str]: 生成的代码字典
        """
        if not self._current_data or not self._current_config:
            self.error_occurred.emit("数据或配置不完整")
            return {}
        
        try:
            self.status_changed.emit("正在生成代码...")
            
            # 生成代码
            code_dict = self.code_generator.generate_code(
                self._current_data, 
                self._current_config
            )
            
            if code_dict:
                self.status_changed.emit("代码生成完成")
            
            return code_dict
            
        except Exception as e:
            self.error_occurred.emit(f"生成代码失败: {str(e)}")
            return {}
    
    def export_project(self, output_dir: str) -> bool:
        """导出项目
        
        Args:
            output_dir: 输出目录
            
        Returns:
            bool: 是否导出成功
        """
        if not self._current_data or not self._current_config:
            self.error_occurred.emit("数据或配置不完整")
            return False
        
        try:
            self.status_changed.emit("正在导出项目...")
            
            # 导出项目
            success = self.code_generator.export_project(output_dir)
            
            if success:
                self.status_changed.emit("项目导出完成")
            
            return success
            
        except Exception as e:
            self.error_occurred.emit(f"导出项目失败: {str(e)}")
            return False
    
    def update_config(self, section: str, config_dict: Dict[str, Any]) -> None:
        """更新配置
        
        Args:
            section: 配置节名称
            config_dict: 配置字典
        """
        self.config_manager.update_config(section, config_dict)
    
    def save_config(self, file_path: str) -> bool:
        """保存配置
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            bool: 是否保存成功
        """
        return self.config_manager.save_config_file(file_path)
    
    def load_config(self, file_path: str) -> bool:
        """加载配置
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            bool: 是否加载成功
        """
        return self.config_manager.load_config_file(file_path)
    
    def get_current_data(self) -> Optional[Dict[str, Any]]:
        """获取当前数据
        
        Returns:
            Optional[Dict[str, Any]]: 当前数据信息
        """
        return self._current_data
    
    def get_current_config(self) -> Optional[Dict[str, Any]]:
        """获取当前配置
        
        Returns:
            Optional[Dict[str, Any]]: 当前配置信息
        """
        return self._current_config
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """获取数据统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        if self._current_data:
            return self._current_data.get("statistics", {})
        return {}
    
    def clear_data(self) -> None:
        """清除数据"""
        self._current_data = None
        self.data_manager.clear_data()
        self.chart_renderer.clear_chart()
        self.status_changed.emit("数据已清除")
    
    def reset_config(self) -> None:
        """重置配置"""
        self.config_manager.reset_config()
        self.status_changed.emit("配置已重置")
    
    def _on_config_changed(self, config: Dict[str, Any]) -> None:
        """配置变化事件处理"""
        self._current_config = config
        
        # 如果有数据，自动重新渲染图表
        if self._current_data:
            self.render_chart()
    
    def _on_data_loaded(self, data_info: Dict[str, Any]) -> None:
        """数据加载完成事件处理"""
        self._current_data = data_info
        self._update_data_config()
        self.status_changed.emit("数据加载完成")
        
        # 自动渲染图表
        self.render_chart()
    
    def _on_data_error(self, error_msg: str) -> None:
        """数据错误事件处理"""
        self.error_occurred.emit(f"数据错误: {error_msg}")
    
    def _on_chart_rendered(self, html_content: str) -> None:
        """图表渲染完成事件处理"""
        self.status_changed.emit("图表渲染完成")
    
    def _on_chart_error(self, error_msg: str) -> None:
        """图表错误事件处理"""
        self.error_occurred.emit(f"图表错误: {error_msg}")
    
    def _on_code_generated(self, code_dict: Dict[str, str]) -> None:
        """代码生成完成事件处理"""
        self.status_changed.emit("代码生成完成")
    
    def _on_code_error(self, error_msg: str) -> None:
        """代码错误事件处理"""
        self.error_occurred.emit(f"代码错误: {error_msg}")
    
    def _update_data_config(self) -> None:
        """更新数据配置"""
        if self._current_data:
            data_config = {
                "matrix_data": self._current_data["matrix_data"],
                "row_labels": self._current_data["row_labels"],
                "col_labels": self._current_data["col_labels"],
                "value_range": self._current_data["value_range"],
                "data_source": self._current_data.get("file_path", ""),
                "data_format": self._current_data.get("file_type", "")
            }
            
            self.config_manager.update_config("data", data_config)
    
    def get_app_status(self) -> Dict[str, Any]:
        """获取应用状态
        
        Returns:
            Dict[str, Any]: 应用状态信息
        """
        return {
            "initialized": self._is_initialized,
            "has_data": self._current_data is not None,
            "has_config": self._current_config is not None,
            "data_shape": self._current_data.get("shape") if self._current_data else None,
            "data_source": self._current_data.get("file_path") if self._current_data else None,
            "modules": {
                "config_manager": bool(self.config_manager),
                "data_manager": bool(self.data_manager),
                "chart_renderer": bool(self.chart_renderer),
                "code_generator": bool(self.code_generator)
            }
        } 