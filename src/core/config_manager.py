#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理器模块
负责管理矩阵热力图的各种配置选项，包括数据配置、样式配置、交互配置和动画配置
"""

import json
import os
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import QObject, pyqtSignal


class ConfigManager(QObject):
    """配置管理器类
    
    负责管理矩阵热力图的所有配置选项，包括：
    - 数据配置（矩阵数据、行列标签等）
    - 样式配置（颜色、字体、尺寸等）
    - 交互配置（缩放、提示框等）
    - 动画配置（过渡效果等）
    """
    
    # 配置变化信号
    config_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self._config = self._get_default_config()
        self._config_file_path = None
        
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置字典
        """
        return {
            # 数据配置
            "data": {
                "matrix_data": [],
                "row_labels": [],
                "col_labels": [],
                "value_range": [0, 1],
                "data_source": "",
                "data_format": "csv"
            },
            
            # 样式配置
            "style": {
                "title": {
                    "text": "矩阵热力图",
                    "textStyle": {
                        "fontSize": 18,
                        "fontWeight": "bold",
                        "color": "#333"
                    },
                    "left": "center",
                    "top": "5%"
                },
                "visualMap": {
                    "min": 0,
                    "max": 1,
                    "calculable": True,
                    "orient": "horizontal",
                    "left": "center",
                    "bottom": "5%",
                    "inRange": {
                        "color": ["#313695", "#74add1", "#abd9e9", "#e0f3f8", 
                                 "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027"]
                    }
                },
                "xAxis": {
                    "type": "category",
                    "position": "top",
                    "splitArea": {
                        "show": True
                    }
                },
                "yAxis": {
                    "type": "category",
                    "splitArea": {
                        "show": True
                    }
                },
                "grid": {
                    "height": "50%",
                    "y": "10%"
                }
            },
            
            # 交互配置
            "interaction": {
                "tooltip": {
                    "position": "top",
                    "formatter": "{c}"
                },
                "dataZoom": {
                    "xAxisIndex": 0,
                    "yAxisIndex": 0,
                    "orient": "horizontal",
                    "bottom": "20%",
                    "start": 0,
                    "end": 100
                },
                "brush": {
                    "toolbox": ["rect", "polygon", "clear"],
                    "xAxisIndex": 0,
                    "yAxisIndex": 0
                }
            },
            
            # 动画配置
            "animation": {
                "animationDuration": 1000,
                "animationEasing": "cubicInOut",
                "animationDelay": 0,
                "animationDurationUpdate": 300,
                "animationEasingUpdate": "cubicInOut"
            }
        }
    
    def get_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """获取配置
        
        Args:
            section: 配置节名称，如果为None则返回全部配置
            
        Returns:
            Dict[str, Any]: 配置字典
        """
        if section is None:
            return self._config.copy()
        return self._config.get(section, {}).copy()
    
    def set_config(self, section: str, key: str, value: Any) -> None:
        """设置配置项
        
        Args:
            section: 配置节名称
            key: 配置项键名
            value: 配置项值
        """
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section][key] = value
        self.config_changed.emit(self._config)
    
    def update_config(self, section: str, config_dict: Dict[str, Any]) -> None:
        """更新配置节
        
        Args:
            section: 配置节名称
            config_dict: 配置字典
        """
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section].update(config_dict)
        self.config_changed.emit(self._config)
    
    def reset_config(self, section: Optional[str] = None) -> None:
        """重置配置
        
        Args:
            section: 配置节名称，如果为None则重置全部配置
        """
        if section is None:
            self._config = self._get_default_config()
        else:
            default_config = self._get_default_config()
            if section in default_config:
                self._config[section] = default_config[section]
        
        self.config_changed.emit(self._config)
    
    def load_config_file(self, file_path: str) -> bool:
        """从文件加载配置
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            bool: 是否加载成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 验证配置格式
            if not self._validate_config(config_data):
                return False
            
            self._config = config_data
            self._config_file_path = file_path
            self.config_changed.emit(self._config)
            return True
            
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(f"加载配置文件失败: {e}")
            return False
    
    def save_config_file(self, file_path: Optional[str] = None) -> bool:
        """保存配置到文件
        
        Args:
            file_path: 配置文件路径，如果为None则使用当前路径
            
        Returns:
            bool: 是否保存成功
        """
        if file_path is None:
            file_path = self._config_file_path
        
        if file_path is None:
            return False
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            
            self._config_file_path = file_path
            return True
            
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置格式
        
        Args:
            config: 配置字典
            
        Returns:
            bool: 是否有效
        """
        required_sections = ["data", "style", "interaction", "animation"]
        
        for section in required_sections:
            if section not in config:
                return False
        
        # 验证数据配置
        data_config = config["data"]
        if not isinstance(data_config.get("matrix_data"), list):
            return False
        
        return True
    
    def get_echarts_option(self) -> Dict[str, Any]:
        """获取ECharts配置选项
        
        Returns:
            Dict[str, Any]: ECharts配置字典
        """
        data_config = self._config["data"]
        style_config = self._config["style"]
        interaction_config = self._config["interaction"]
        animation_config = self._config["animation"]
        
        # 构建ECharts配置
        option = {
            "title": style_config["title"],
            "tooltip": interaction_config["tooltip"],
            "animation": True,
            "animationDuration": animation_config["animationDuration"],
            "animationEasing": animation_config["animationEasing"],
            "grid": style_config["grid"],
            "xAxis": {
                **style_config["xAxis"],
                "data": data_config["col_labels"]
            },
            "yAxis": {
                **style_config["yAxis"],
                "data": data_config["row_labels"]
            },
            "visualMap": {
                **style_config["visualMap"],
                "min": data_config["value_range"][0],
                "max": data_config["value_range"][1]
            },
            "series": [{
                "name": "矩阵热力图",
                "type": "heatmap",
                "data": data_config["matrix_data"],
                "label": {
                    "show": True
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }]
        }
        
        # 添加数据缩放功能
        if interaction_config.get("dataZoom"):
            option["dataZoom"] = [interaction_config["dataZoom"]]
        
        return option
    
    def get_config_file_path(self) -> Optional[str]:
        """获取当前配置文件路径
        
        Returns:
            Optional[str]: 配置文件路径
        """
        return self._config_file_path
    
    def set_config_file_path(self, file_path: str) -> None:
        """设置配置文件路径
        
        Args:
            file_path: 配置文件路径
        """
        self._config_file_path = file_path 