#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据管理器模块
负责处理矩阵热力图的数据导入、验证和转换
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, Any, List, Tuple, Optional, Union
from PyQt6.QtCore import QObject, pyqtSignal


class DataManager(QObject):
    """数据管理器类
    
    负责处理矩阵热力图的数据操作，包括：
    - CSV/Excel文件导入
    - 矩阵数据验证
    - 数据格式转换
    - 示例数据生成
    """
    
    # 数据加载信号
    data_loaded = pyqtSignal(dict)
    data_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._current_data = None
        self._original_data = None
        self._data_info = {}
        
    def load_csv_file(self, file_path: str, **kwargs) -> bool:
        """加载CSV文件
        
        Args:
            file_path: CSV文件路径
            **kwargs: pandas.read_csv的参数
            
        Returns:
            bool: 是否加载成功
        """
        try:
            # 默认参数
            default_kwargs = {
                'encoding': 'utf-8',
                'index_col': 0,
                'header': 0
            }
            default_kwargs.update(kwargs)
            
            # 读取CSV文件
            df = pd.read_csv(file_path, **default_kwargs)
            
            # 验证和处理数据
            result = self._process_dataframe(df, file_path, "csv")
            
            if result:
                self.data_loaded.emit(self._data_info)
                return True
            else:
                return False
                
        except Exception as e:
            error_msg = f"加载CSV文件失败: {str(e)}"
            self.data_error.emit(error_msg)
            return False
    
    def load_excel_file(self, file_path: str, sheet_name: Union[str, int] = 0, **kwargs) -> bool:
        """加载Excel文件
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称或索引
            **kwargs: pandas.read_excel的参数
            
        Returns:
            bool: 是否加载成功
        """
        try:
            # 默认参数
            default_kwargs = {
                'sheet_name': sheet_name,
                'index_col': 0,
                'header': 0
            }
            default_kwargs.update(kwargs)
            
            # 读取Excel文件
            df = pd.read_excel(file_path, **default_kwargs)
            
            # 验证和处理数据
            result = self._process_dataframe(df, file_path, "excel")
            
            if result:
                self.data_loaded.emit(self._data_info)
                return True
            else:
                return False
                
        except Exception as e:
            error_msg = f"加载Excel文件失败: {str(e)}"
            self.data_error.emit(error_msg)
            return False
    
    def _process_dataframe(self, df: pd.DataFrame, file_path: str, file_type: str) -> bool:
        """处理DataFrame数据
        
        Args:
            df: pandas DataFrame
            file_path: 文件路径
            file_type: 文件类型
            
        Returns:
            bool: 是否处理成功
        """
        try:
            # 保存原始数据
            self._original_data = df.copy()
            
            # 数据验证
            validation_result = self._validate_matrix_data(df)
            if not validation_result["valid"]:
                self.data_error.emit(validation_result["error"])
                return False
            
            # 数据清洗
            cleaned_df = self._clean_matrix_data(df)
            
            # 转换为ECharts格式
            matrix_data = self._convert_to_echarts_format(cleaned_df)
            
            # 获取行列标签
            row_labels = cleaned_df.index.tolist()
            col_labels = cleaned_df.columns.tolist()
            
            # 计算数值范围
            value_range = self._calculate_value_range(cleaned_df)
            
            # 保存处理后的数据
            self._current_data = cleaned_df
            self._data_info = {
                "file_path": file_path,
                "file_type": file_type,
                "shape": cleaned_df.shape,
                "matrix_data": matrix_data,
                "row_labels": row_labels,
                "col_labels": col_labels,
                "value_range": value_range,
                "statistics": self._calculate_statistics(cleaned_df)
            }
            
            return True
            
        except Exception as e:
            error_msg = f"处理数据失败: {str(e)}"
            self.data_error.emit(error_msg)
            return False
    
    def _validate_matrix_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """验证矩阵数据
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        # 检查是否为空
        if df.empty:
            return {"valid": False, "error": "数据为空"}
        
        # 检查维度
        if df.shape[0] < 2 or df.shape[1] < 2:
            return {"valid": False, "error": "矩阵维度至少需要2x2"}
        
        # 检查数据类型
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return {"valid": False, "error": "矩阵中没有找到数值型数据"}
        
        # 检查缺失值比例
        missing_ratio = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
        if missing_ratio > 0.5:
            return {"valid": False, "error": f"缺失值比例过高 ({missing_ratio:.2%})"}
        
        # 检查数值范围
        try:
            numeric_data = df.select_dtypes(include=[np.number])
            if numeric_data.min().min() == numeric_data.max().max():
                return {"valid": False, "error": "所有数值都相同，无法生成热力图"}
        except:
            pass
        
        return {"valid": True, "error": None}
    
    def _clean_matrix_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗矩阵数据
        
        Args:
            df: pandas DataFrame
            
        Returns:
            pd.DataFrame: 清洗后的数据
        """
        # 复制数据
        cleaned_df = df.copy()
        
        # 只保留数值型列
        numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < len(cleaned_df.columns):
            cleaned_df = cleaned_df[numeric_cols]
        
        # 处理缺失值
        if cleaned_df.isnull().any().any():
            # 使用均值填充
            cleaned_df = cleaned_df.fillna(cleaned_df.mean())
        
        # 处理无限值
        cleaned_df = cleaned_df.replace([np.inf, -np.inf], np.nan)
        if cleaned_df.isnull().any().any():
            cleaned_df = cleaned_df.fillna(cleaned_df.mean())
        
        # 确保索引和列名为字符串
        cleaned_df.index = cleaned_df.index.astype(str)
        cleaned_df.columns = cleaned_df.columns.astype(str)
        
        return cleaned_df
    
    def _convert_to_echarts_format(self, df: pd.DataFrame) -> List[List[Any]]:
        """转换为ECharts热力图格式
        
        Args:
            df: pandas DataFrame
            
        Returns:
            List[List[Any]]: ECharts格式的数据 [[x, y, value], ...]
        """
        data = []
        
        for i, row_name in enumerate(df.index):
            for j, col_name in enumerate(df.columns):
                value = df.iloc[i, j]
                # 确保值为数值类型
                if pd.isna(value):
                    value = 0
                else:
                    value = float(value)
                
                data.append([j, i, value])
        
        return data
    
    def _calculate_value_range(self, df: pd.DataFrame) -> List[float]:
        """计算数值范围
        
        Args:
            df: pandas DataFrame
            
        Returns:
            List[float]: [最小值, 最大值]
        """
        min_val = float(df.min().min())
        max_val = float(df.max().max())
        
        # 避免最小值和最大值相等
        if min_val == max_val:
            min_val -= 0.5
            max_val += 0.5
        
        return [min_val, max_val]
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算统计信息
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            "count": int(df.count().sum()),
            "mean": float(df.mean().mean()),
            "std": float(df.std().mean()),
            "min": float(df.min().min()),
            "max": float(df.max().max()),
            "median": float(df.median().median()),
            "missing_count": int(df.isnull().sum().sum())
        }
    
    def get_example_data(self, data_type: str = "correlation") -> Dict[str, Any]:
        """获取示例数据
        
        Args:
            data_type: 数据类型 ("correlation", "random", "pattern")
            
        Returns:
            Dict[str, Any]: 示例数据信息
        """
        if data_type == "correlation":
            return self._generate_correlation_data()
        elif data_type == "random":
            return self._generate_random_data()
        elif data_type == "pattern":
            return self._generate_pattern_data()
        else:
            return self._generate_correlation_data()
    
    def _generate_correlation_data(self) -> Dict[str, Any]:
        """生成相关性矩阵示例数据
        
        Returns:
            Dict[str, Any]: 示例数据信息
        """
        # 生成相关性矩阵
        labels = ["变量A", "变量B", "变量C", "变量D", "变量E"]
        size = len(labels)
        
        # 生成随机相关性矩阵
        np.random.seed(42)
        data = np.random.rand(size, size)
        
        # 使其对称
        data = (data + data.T) / 2
        
        # 设置对角线为1
        np.fill_diagonal(data, 1)
        
        # 创建DataFrame
        df = pd.DataFrame(data, index=labels, columns=labels)
        
        # 转换为ECharts格式
        matrix_data = self._convert_to_echarts_format(df)
        value_range = self._calculate_value_range(df)
        
        return {
            "file_path": "示例数据",
            "file_type": "example",
            "shape": df.shape,
            "matrix_data": matrix_data,
            "row_labels": labels,
            "col_labels": labels,
            "value_range": value_range,
            "statistics": self._calculate_statistics(df)
        }
    
    def _generate_random_data(self) -> Dict[str, Any]:
        """生成随机数据矩阵
        
        Returns:
            Dict[str, Any]: 示例数据信息
        """
        # 生成随机数据
        row_labels = [f"行{i+1}" for i in range(6)]
        col_labels = [f"列{i+1}" for i in range(8)]
        
        np.random.seed(42)
        data = np.random.randint(0, 100, size=(6, 8))
        
        # 创建DataFrame
        df = pd.DataFrame(data, index=row_labels, columns=col_labels)
        
        # 转换为ECharts格式
        matrix_data = self._convert_to_echarts_format(df)
        value_range = self._calculate_value_range(df)
        
        return {
            "file_path": "示例数据",
            "file_type": "example",
            "shape": df.shape,
            "matrix_data": matrix_data,
            "row_labels": row_labels,
            "col_labels": col_labels,
            "value_range": value_range,
            "statistics": self._calculate_statistics(df)
        }
    
    def _generate_pattern_data(self) -> Dict[str, Any]:
        """生成模式数据矩阵
        
        Returns:
            Dict[str, Any]: 示例数据信息
        """
        # 生成具有特定模式的数据
        size = 8
        labels = [f"项目{i+1}" for i in range(size)]
        
        # 创建梯度模式
        data = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                data[i, j] = np.sin(i * j / size * np.pi) * 100
        
        # 创建DataFrame
        df = pd.DataFrame(data, index=labels, columns=labels)
        
        # 转换为ECharts格式
        matrix_data = self._convert_to_echarts_format(df)
        value_range = self._calculate_value_range(df)
        
        return {
            "file_path": "示例数据",
            "file_type": "example",
            "shape": df.shape,
            "matrix_data": matrix_data,
            "row_labels": labels,
            "col_labels": labels,
            "value_range": value_range,
            "statistics": self._calculate_statistics(df)
        }
    
    def get_current_data(self) -> Optional[pd.DataFrame]:
        """获取当前数据
        
        Returns:
            Optional[pd.DataFrame]: 当前数据
        """
        return self._current_data
    
    def get_original_data(self) -> Optional[pd.DataFrame]:
        """获取原始数据
        
        Returns:
            Optional[pd.DataFrame]: 原始数据
        """
        return self._original_data
    
    def get_data_info(self) -> Dict[str, Any]:
        """获取数据信息
        
        Returns:
            Dict[str, Any]: 数据信息
        """
        return self._data_info.copy()
    
    def clear_data(self) -> None:
        """清除数据"""
        self._current_data = None
        self._original_data = None
        self._data_info = {}
    
    def export_data(self, file_path: str, file_type: str = "csv") -> bool:
        """导出数据
        
        Args:
            file_path: 导出文件路径
            file_type: 文件类型 ("csv", "excel")
            
        Returns:
            bool: 是否导出成功
        """
        if self._current_data is None:
            return False
        
        try:
            if file_type.lower() == "csv":
                self._current_data.to_csv(file_path, encoding='utf-8')
            elif file_type.lower() == "excel":
                self._current_data.to_excel(file_path)
            else:
                return False
            
            return True
            
        except Exception as e:
            self.data_error.emit(f"导出数据失败: {str(e)}")
            return False 