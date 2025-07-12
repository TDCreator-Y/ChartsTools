@echo off
echo ChartsTools Git 仓库初始化脚本
echo ================================

echo 正在初始化 Git 仓库...
git init

echo 正在添加所有文件到暂存区...
git add .

echo 正在提交初始版本...
git commit -m "Initial commit: ChartsTools v1.0.0 - 矩阵热力图可视化工具"

echo.
echo Git 仓库初始化完成！
echo.
echo 接下来的步骤：
echo 1. 在 GitHub 上创建一个新的仓库
echo 2. 复制仓库的 URL
echo 3. 运行以下命令添加远程仓库：
echo    git remote add origin https://github.com/用户名/ChartsTools.git
echo 4. 推送到远程仓库：
echo    git push -u origin main
echo.
echo 按任意键退出...
pause > nul 