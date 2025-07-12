@echo off
title ECharts矩阵热力图教学工具 - 开发环境
echo ========================================
echo   ECharts矩阵热力图教学工具
echo   开发环境启动中...
echo ========================================
echo.

echo [1/3] 激活虚拟环境...
call D:\Python\PythonVenv\chartstools\Scripts\activate.bat

echo [2/3] 检查依赖包...
D:\Python\PythonVenv\chartstools\Scripts\python.exe -c "import pandas; print('✓ pandas 已安装')" 2>nul || (echo "✗ pandas 未安装，请运行: pip install -r requirements.txt" && pause && exit)

echo [3/3] 启动开发环境
echo.
echo 开发环境已就绪！可以开始编码了 :)
echo 虚拟环境路径: D:\Python\PythonVenv\chartstools
echo.
cmd /k 