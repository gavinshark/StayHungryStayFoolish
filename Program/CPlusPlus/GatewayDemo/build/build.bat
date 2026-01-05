@echo off
REM CMake 构建脚本 - Windows

setlocal enabledelayedexpansion

echo === C++ Gateway CMake Build Script ===
echo.

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
set "BUILD_DIR=%SCRIPT_DIR%"
set "OUTPUT_DIR=%SCRIPT_DIR%..\output"

REM 清理选项
if "%1"=="clean" (
    echo Cleaning CMake cache and build files...
    if exist "%BUILD_DIR%CMakeCache.txt" del /Q "%BUILD_DIR%CMakeCache.txt"
    if exist "%BUILD_DIR%CMakeFiles" rmdir /S /Q "%BUILD_DIR%CMakeFiles"
    if exist "%BUILD_DIR%cmake_install.cmake" del /Q "%BUILD_DIR%cmake_install.cmake"
    if exist "%BUILD_DIR%Makefile" del /Q "%BUILD_DIR%Makefile"
    if exist "%BUILD_DIR%*.vcxproj" del /Q "%BUILD_DIR%*.vcxproj"
    if exist "%BUILD_DIR%*.sln" del /Q "%BUILD_DIR%*.sln"
    if exist "%OUTPUT_DIR%" rmdir /S /Q "%OUTPUT_DIR%"
    echo Clean complete.
    exit /b 0
)

REM 创建输出目录
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%OUTPUT_DIR%\obj" mkdir "%OUTPUT_DIR%\obj"

REM 进入构建目录
cd /d "%BUILD_DIR%"

REM 检测编译器
where cl.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo Using MSVC compiler...
    set "GENERATOR=Visual Studio"
) else (
    where g++.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo Using MinGW compiler...
        set "GENERATOR=MinGW Makefiles"
    ) else (
        echo Error: No suitable compiler found!
        echo Please install Visual Studio or MinGW.
        exit /b 1
    )
)

REM 运行 CMake 配置
echo Running CMake configuration...
if "!GENERATOR!"=="Visual Studio" (
    cmake -DCMAKE_BUILD_TYPE=Release .
    if %errorlevel% neq 0 exit /b %errorlevel%
    
    echo.
    echo Building project with MSBuild...
    cmake --build . --config Release
) else (
    cmake -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release .
    if %errorlevel% neq 0 exit /b %errorlevel%
    
    echo.
    echo Building project with MinGW...
    mingw32-make
)

if %errorlevel% neq 0 (
    echo Build failed!
    exit /b %errorlevel%
)

echo.
echo === Build Complete ===
echo Executable: %OUTPUT_DIR%\gateway.exe
echo.
echo To run the gateway:
echo   output\gateway.exe config\config.json
echo.

endlocal
