@echo off
chcp 65001
title ChartsTools 多选项打包工具 v1.2.0

:MENU
cls
echo =========================================
echo    ChartsTools 多选项打包工具 v1.2.0
echo =========================================
echo.
echo 请选择打包方式：
echo.
echo 1. 单文件EXE版本 (推荐，适合分发)
echo    - 所有文件打包成一个ChartsTools.exe
echo    - 文件较大(~100-200MB)，但只需一个文件
echo    - 启动时间稍长，但兼容性最好
echo.
echo 2. 便携版目录 (推荐，适合本地使用)
echo    - 创建ChartsTools_Portable文件夹
echo    - 文件较小，启动速度快
echo    - 需要保持目录完整性
echo.
echo 3. 安装依赖包 PyInstaller
echo    - 仅安装PyInstaller，不进行打包
echo.
echo 4. 清理构建文件
echo    - 删除dist和build目录
echo.
echo 0. 退出
echo.
set /p choice=请输入选择 (0-4): 

if "%choice%"=="1" goto SINGLE_FILE
if "%choice%"=="2" goto PORTABLE
if "%choice%"=="3" goto INSTALL_PYINSTALLER
if "%choice%"=="4" goto CLEAN
if "%choice%"=="0" goto EXIT
echo 无效选择，请重新输入！
pause
goto MENU

:SINGLE_FILE
cls
echo =========================================
echo 开始单文件EXE打包...
echo =========================================
call :PREPARE_ENV
if errorlevel 1 goto MENU

echo [4/5] 开始打包单文件EXE...
echo 这可能需要5-10分钟，请耐心等待...
pyinstaller chartstools.spec --clean --noconfirm
if errorlevel 1 (
    echo ❌ 打包失败！请检查错误信息
    pause
    goto MENU
)

echo.
echo ✅ 单文件EXE打包完成！
if exist "dist\ChartsTools.exe" (
    echo 文件位置：%cd%\dist\ChartsTools.exe
    echo 文件大小：
    for %%I in ("dist\ChartsTools.exe") do echo    %%~zI 字节
    echo.
    echo 是否测试运行程序？ (Y/N)
    set /p test=
    if /i "%test%"=="Y" start "" "%cd%\dist\ChartsTools.exe"
)
pause
goto MENU

:PORTABLE
cls
echo =========================================
echo 开始便携版目录打包...
echo =========================================
call :PREPARE_ENV
if errorlevel 1 goto MENU

echo [4/5] 开始打包便携版目录...
echo 这可能需要3-5分钟，请耐心等待...
pyinstaller chartstools_portable.spec --clean --noconfirm
if errorlevel 1 (
    echo ❌ 打包失败！请检查错误信息
    pause
    goto MENU
)

echo.
echo ✅ 便携版目录打包完成！
if exist "dist\ChartsTools_Portable" (
    echo 目录位置：%cd%\dist\ChartsTools_Portable\
    echo 主程序：%cd%\dist\ChartsTools_Portable\ChartsTools.exe
    echo.
    echo 是否测试运行程序？ (Y/N)
    set /p test=
    if /i "%test%"=="Y" start "" "%cd%\dist\ChartsTools_Portable\ChartsTools.exe"
)
pause
goto MENU

:INSTALL_PYINSTALLER
cls
echo =========================================
echo 安装PyInstaller...
echo =========================================
call :ACTIVATE_ENV
if errorlevel 1 goto MENU

echo [2/2] 安装PyInstaller...
pip install pyinstaller --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
if errorlevel 1 (
    echo ❌ PyInstaller安装失败！
    pause
    goto MENU
)
echo ✅ PyInstaller安装成功！
pause
goto MENU

:CLEAN
cls
echo =========================================
echo 清理构建文件...
echo =========================================
if exist "dist" (
    echo 删除 dist 目录...
    rmdir /s /q "dist"
)
if exist "build" (
    echo 删除 build 目录...
    rmdir /s /q "build"
)
if exist "*.spec" (
    echo 发现spec文件，保留不删除
)
echo ✅ 清理完成！
pause
goto MENU

:PREPARE_ENV
call :ACTIVATE_ENV
if errorlevel 1 exit /b 1

echo [3/5] 检查PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller未安装，正在安装...
    pip install pyinstaller --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    if errorlevel 1 (
        echo ❌ PyInstaller安装失败！
        exit /b 1
    )
)

echo [4/5] 清理之前的构建文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
exit /b 0

:ACTIVATE_ENV
echo [1/5] 激活虚拟环境...
call D:\Python\PythonVenv\chartstools\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 错误：无法激活虚拟环境！
    echo 请确保虚拟环境路径正确：D:\Python\PythonVenv\chartstools
    pause
    exit /b 1
)

echo [2/5] 检查Python环境...
python --version
pip --version
exit /b 0

:EXIT
echo 感谢使用ChartsTools打包工具！
pause
exit 