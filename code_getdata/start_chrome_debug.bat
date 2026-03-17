@echo off
chcp 65001 >nul
echo ========================================================
echo 正在启动调试模式 Chrome 浏览器...
echo 注意：请务必先关闭电脑上所有已经打开的 Chrome 窗口！
echo ========================================================

set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_PATH%" set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if not exist "%CHROME_PATH%" (
    echo [错误] 未在默认路径找到 Google Chrome。
    echo 请联系我或手动修改本脚本中的路径。
    pause
    exit /b
)

:: 设置用户数据目录在当前项目下，方便缓存登录状态
set "USER_DATA=%~dp0..\..\xhs_remote_profile"

echo Chrome 路径: "%CHROME_PATH%"
echo 数据目录: "%USER_DATA%"
echo.
echo 浏览器启动后：
echo 1. 请在打开的浏览器中手动访问 xiaohongshu.com 并登录。
echo 2. 登录成功后，不要关闭浏览器，回到 VS Code 运行 Python 爬虫脚本。
echo.

"%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%USER_DATA%"

pause