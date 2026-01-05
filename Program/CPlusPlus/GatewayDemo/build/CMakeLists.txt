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

# 源文件和头文件目录
set(SRC_DIR ${CMAKE_SOURCE_DIR}/../src)
set(INC_DIR ${CMAKE_SOURCE_DIR}/../include)
set(THIRD_PARTY_DIR ${CMAKE_SOURCE_DIR}/../third_party)

# 收集所有源文件
file(GLOB SOURCES "${SRC_DIR}/*.cpp")

# 包含目录
include_directories(${INC_DIR})

# ============================================
# 第三方库配置
# ============================================

# Asio (standalone, header-only)
set(ASIO_INCLUDE_DIR ${THIRD_PARTY_DIR}/asio/asio/include)
if(EXISTS ${ASIO_INCLUDE_DIR})
    include_directories(${ASIO_INCLUDE_DIR})
    add_definitions(-DASIO_STANDALONE)
    add_definitions(-DASIO_HAS_STD_ADDRESSOF)
    add_definitions(-DASIO_HAS_STD_ARRAY)
    add_definitions(-DASIO_HAS_CSTDINT)
    add_definitions(-DASIO_HAS_STD_SHARED_PTR)
    add_definitions(-DASIO_HAS_STD_TYPE_TRAITS)
    message(STATUS "Found Asio: ${ASIO_INCLUDE_DIR}")
else()
    message(WARNING "Asio not found at ${ASIO_INCLUDE_DIR}")
endif()

# nlohmann/json (header-only)
set(JSON_INCLUDE_DIR ${THIRD_PARTY_DIR}/json/include)
if(EXISTS ${JSON_INCLUDE_DIR})
    include_directories(${JSON_INCLUDE_DIR})
    message(STATUS "Found nlohmann/json: ${JSON_INCLUDE_DIR}")
else()
    message(WARNING "nlohmann/json not found at ${JSON_INCLUDE_DIR}")
endif()

# spdlog (header-only)
set(SPDLOG_INCLUDE_DIR ${THIRD_PARTY_DIR}/spdlog/include)
if(EXISTS ${SPDLOG_INCLUDE_DIR})
    include_directories(${SPDLOG_INCLUDE_DIR})
    message(STATUS "Found spdlog: ${SPDLOG_INCLUDE_DIR}")
else()
    message(WARNING "spdlog not found at ${SPDLOG_INCLUDE_DIR}")
endif()

# http-parser (可选)
set(HTTP_PARSER_DIR ${THIRD_PARTY_DIR}/http-parser)
if(EXISTS ${HTTP_PARSER_DIR})
    include_directories(${HTTP_PARSER_DIR})
    file(GLOB HTTP_PARSER_SOURCES "${HTTP_PARSER_DIR}/*.c")
    list(APPEND SOURCES ${HTTP_PARSER_SOURCES})
    message(STATUS "Found http-parser: ${HTTP_PARSER_DIR}")
endif()

# ============================================
# 创建可执行文件
# ============================================
add_executable(gateway ${SOURCES})

# 编译选项
if(MSVC)
    # Windows MSVC
    target_compile_options(gateway PRIVATE /W4)
    target_compile_definitions(gateway PRIVATE 
        _CRT_SECURE_NO_WARNINGS
        _WIN32_WINNT=0x0601  # Windows 7+
    )
else()
    # GCC/Clang (Linux/macOS)
    target_compile_options(gateway PRIVATE -Wall -Wextra -pedantic)
endif()

# 平台特定的链接库
if(WIN32)
    # Windows: socket库
    target_link_libraries(gateway PRIVATE ws2_32 wsock32)
elseif(UNIX)
    # Linux/macOS: pthread库
    find_package(Threads REQUIRED)
    target_link_libraries(gateway PRIVATE Threads::Threads)
    
    # macOS可能需要额外的系统库
    if(APPLE)
        target_link_libraries(gateway PRIVATE "-framework CoreFoundation")
    endif()
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
message(STATUS "Third Party Directory: ${THIRD_PARTY_DIR}")
message(STATUS "=======================================")
