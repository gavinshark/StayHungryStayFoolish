@echo off
REM 自动安装第三方依赖脚本 (Windows)

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ==========================================
echo 安装第三方依赖库 (Windows)
echo ==========================================

REM 检查git是否安装
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 未找到git命令，请先安装git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM 安装Asio
echo.
echo [1/4] 安装 Asio (standalone)...
if exist "asio" (
    echo Asio已存在，跳过...
) else (
    git clone https://github.com/chriskohlhoff/asio.git
    cd asio
    git checkout asio-1-28-0 2>nul || git checkout master
    cd ..
    echo [完成] Asio安装完成
)

REM 安装nlohmann/json
echo.
echo [2/4] 安装 nlohmann/json...
if exist "json" (
    echo nlohmann/json已存在，跳过...
) else (
    git clone https://github.com/nlohmann/json.git
    cd json
    git checkout v3.11.3 2>nul || git checkout master
    cd ..
    echo [完成] nlohmann/json安装完成
)

REM 安装spdlog
echo.
echo [3/4] 安装 spdlog...
if exist "spdlog" (
    echo spdlog已存在，跳过...
) else (
    git clone https://github.com/gabime/spdlog.git
    cd spdlog
    git checkout v1.12.0 2>nul || git checkout master
    cd ..
    echo [完成] spdlog安装完成
)

REM 安装http-parser (可选)
echo.
echo [4/4] 安装 http-parser (可选)...
set /p install_http_parser="是否安装http-parser? (y/n) [默认: n]: "
if /i "%install_http_parser%"=="y" (
    if exist "http-parser" (
        echo http-parser已存在，跳过...
    ) else (
        git clone https://github.com/nodejs/http-parser.git
        cd http-parser
        git checkout v2.9.4 2>nul || git checkout master
        cd ..
        echo [完成] http-parser安装完成
    )
) else (
    echo 跳过http-parser安装
)

REM 验证安装
echo.
echo 验证安装...
set all_ok=1

if exist "asio\asio\include\asio.hpp" (
    echo [OK] Asio: OK
) else (
    echo [错误] Asio: 未找到
    set all_ok=0
)

if exist "json\include\nlohmann\json.hpp" (
    echo [OK] nlohmann/json: OK
) else (
    echo [错误] nlohmann/json: 未找到
    set all_ok=0
)

if exist "spdlog\include\spdlog\spdlog.h" (
    echo [OK] spdlog: OK
) else (
    echo [错误] spdlog: 未找到
    set all_ok=0
)

if exist "http-parser\http_parser.h" (
    echo [OK] http-parser: OK
)

echo.
echo ==========================================
if %all_ok%==1 (
    echo [成功] 所有依赖安装成功！
    echo.
    echo 下一步:
    echo   cd ..\build
    echo   cmake ..
    echo   cmake --build . --config Release
) else (
    echo [失败] 部分依赖安装失败，请检查错误信息
)
echo ==========================================

pause
