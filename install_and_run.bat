@echo off
echo ==============================================
echo      股票新闻分析与投资建议系统 - 安装与启动
echo ==============================================
echo.

:: 检查是否已安装Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本...
    echo 正在打开Python官方网站...
    start https://www.python.org/downloads/
    echo 安装完成后，请重新运行此脚本
    pause
    exit
)

echo [信息] 检测到Python安装...
echo.

:: 创建虚拟环境目录（如果不存在）
if not exist "venv\" (
    echo [信息] 正在创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 创建虚拟环境失败，尝试直接安装依赖...
    ) else (
        echo [成功] 虚拟环境创建完成
    )
) else (
    echo [信息] 使用已存在的虚拟环境
)

:: 激活虚拟环境（如果存在）
if exist "venv\Scripts\activate.bat" (
    echo [信息] 正在激活虚拟环境...
    call venv\Scripts\activate.bat
    echo [成功] 虚拟环境已激活
)

:: 安装依赖
echo [信息] 正在安装依赖包，这可能需要几分钟时间...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [警告] 安装依赖时出现错误，但将继续尝试启动应用...
) else (
    echo [成功] 依赖安装完成
)
echo.

:: 启动Streamlit应用
echo [信息] 正在启动应用程序...
echo [信息] 应用程序将在浏览器中自动打开...
echo [信息] 若未自动打开，请手动访问 http://localhost:8501
echo.
echo [提示] 如需关闭应用，请在此窗口按Ctrl+C，然后按Y确认

:: 启动Streamlit
start "" http://localhost:8501
streamlit run src/app.py

:: 脚本结束
echo [信息] 应用已关闭
pause 