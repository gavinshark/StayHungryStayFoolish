cmake_minimum_required(VERSION 3.15)
project(cpp-gateway VERSION 1.0.0 LANGUAGES CXX)

# C++17 标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 输出目录设置
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../output)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../output/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../output/lib)

# 对象文件输出目录
set(CMAKE_OBJECT_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../output/obj)

# 源文件和头文件目录
set(SRC_DIR ${CMAKE_SOURCE_DIR}/../src)
set(INC_DIR ${CMAKE_SOURCE_DIR}/../include)

# 收集所有源文件
file(GLOB SOURCES "${SRC_DIR}/*.cpp")

# 包含目录
include_directories(${INC_DIR})

# 创建可执行文件
add_executable(gateway ${SOURCES})

# 编译选项
if(MSVC)
    # Windows MSVC
    target_compile_options(gateway PRIVATE /W4)
    target_compile_definitions(gateway PRIVATE _CRT_SECURE_NO_WARNINGS)
else()
    # GCC/Clang (Linux/macOS)
    target_compile_options(gateway PRIVATE -Wall -Wextra -pedantic)
endif()

# 平台特定的链接库
if(WIN32)
    # Windows: 需要 ws2_32 库用于 socket
    target_link_libraries(gateway PRIVATE ws2_32)
elseif(UNIX)
    # Linux/macOS: 需要 pthread 库
    find_package(Threads REQUIRED)
    target_link_libraries(gateway PRIVATE Threads::Threads)
endif()

# 安装规则（可选）
install(TARGETS gateway
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

# 打印配置信息
message(STATUS "=== C++ Gateway Build Configuration ===")
message(STATUS "CMake Version: ${CMAKE_VERSION}")
message(STATUS "System: ${CMAKE_SYSTEM_NAME}")
message(STATUS "Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "C++ Standard: C++${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Output Directory: ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")
message(STATUS "Source Directory: ${SRC_DIR}")
message(STATUS "Include Directory: ${INC_DIR}")
message(STATUS "=======================================")
