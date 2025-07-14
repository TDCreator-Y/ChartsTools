@echo off
chcp 65001
echo ====================================
echo ChartsTools EXE打包脚本 v1.2.0
echo ====================================
echo.

echo [1/6] 激活虚拟环境...
call D:\Python\PythonVenv\chartstools\Scripts\activate.bat
if errorlevel 1 (
    echo 错误：无法激活虚拟环境！
    echo 请确保虚拟环境路径正确：D:\Python\PythonVenv\chartstools
    pause
    exit /b 1
)

echo [2/6] 检查Python环境...
python --version
pip --version

echo [3/6] 安装PyInstaller...
pip install pyinstaller --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
if errorlevel 1 (
    echo 错误：PyInstaller安装失败！
    echo 请检查网络连接或手动安装PyInstaller
    pause
    exit /b 1
)

echo [4/6] 清理之前的构建文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo [5/6] 开始打包程序...
echo 这可能需要几分钟时间，请耐心等待...
pyinstaller chartstools.spec --clean --noconfirm
if errorlevel 1 (
    echo 错误：打包失败！
    echo 请检查chartstools.spec文件和项目结构
    pause
    exit /b 1
)

echo [6/6] 打包完成！
echo.
echo ====================================
echo 打包结果：
echo ====================================
if exist "dist\ChartsTools.exe" (
    echo ✅ 成功！ChartsTools.exe 已生成
    echo 文件位置：%cd%\dist\ChartsTools.exe
    
    echo.
    echo 测试运行程序...
    echo 按任意键测试运行程序，或按Ctrl+C取消
    pause >nul
    
    start "" "%cd%\dist\ChartsTools.exe"
    echo 程序已启动，请检查是否正常运行
) else (
    echo ❌ 失败！未找到ChartsTools.exe文件
    echo 请检查打包过程中的错误信息
)

echo.
echo 按任意键退出...
pause >nul 