#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
核心模块包
包含ECharts矩阵热力图工具的核心功能模块
"""

from .config_manager import ConfigManager
from .data_manager import DataManager
from .chart_renderer import ChartRenderer
from .code_generator import CodeGenerator
from .app_controller import AppController

__all__ = [
    'ConfigManager',
    'DataManager', 
    'ChartRenderer',
    'CodeGenerator',
    'AppController'
]

__version__ = '1.0.0'
__author__ = 'ECharts矩阵热力图工具'
__description__ = '提供配置管理、数据处理、图表渲染和代码生成等核心功能' 