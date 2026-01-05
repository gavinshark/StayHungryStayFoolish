# Makefile for C++ Gateway
# 支持 Linux, macOS, Windows (MinGW)

# 项目名称
TARGET = gateway

# 目录设置
SRC_DIR = ../src
INC_DIR = ../include
OBJ_DIR = ../output/obj
OUT_DIR = ../output

# 源文件
SOURCES = $(wildcard $(SRC_DIR)/*.cpp)
OBJECTS = $(patsubst $(SRC_DIR)/%.cpp,$(OBJ_DIR)/%.o,$(SOURCES))

# 第三方库目录
THIRD_PARTY_DIR = ../third_party

# 编译器设置
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -I$(INC_DIR)

# 添加第三方库头文件路径
CXXFLAGS += -I$(THIRD_PARTY_DIR)/spdlog/include
CXXFLAGS += -I$(THIRD_PARTY_DIR)/json/include
CXXFLAGS += -I$(THIRD_PARTY_DIR)/asio/asio/include
CXXFLAGS += -DASIO_STANDALONE

# 平台检测
ifeq ($(OS),Windows_NT)
    # Windows
    PLATFORM = Windows
    TARGET_EXT = .exe
    RM = del /Q
    RMDIR = rmdir /S /Q
    MKDIR = if not exist $(subst /,\,$(1)) mkdir $(subst /,\,$(1))
    LDFLAGS = -lws2_32
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
        # Linux
        PLATFORM = Linux
        TARGET_EXT =
        RM = rm -f
        RMDIR = rm -rf
        MKDIR = mkdir -p $(1)
        LDFLAGS = -pthread
    endif
    ifeq ($(UNAME_S),Darwin)
        # macOS
        PLATFORM = macOS
        TARGET_EXT =
        RM = rm -f
        RMDIR = rm -rf
        MKDIR = mkdir -p $(1)
        LDFLAGS = -pthread
    endif
endif

# 最终目标
TARGET_PATH = $(OUT_DIR)/$(TARGET)$(TARGET_EXT)

# 默认目标
.PHONY: all
all: info $(TARGET_PATH)

# 显示平台信息
.PHONY: info
info:
	@echo "=== Building C++ Gateway ==="
	@echo "Platform: $(PLATFORM)"
	@echo "Compiler: $(CXX)"
	@echo "C++ Standard: C++17"
	@echo "Output: $(TARGET_PATH)"
	@echo ""

# 链接目标
$(TARGET_PATH): $(OBJECTS)
	@echo "Linking $(TARGET)..."
	@$(call MKDIR,$(OUT_DIR))
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)
	@echo ""
	@echo "Build successful: $(TARGET_PATH)"
	@echo ""

# 编译源文件
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	@echo "Compiling $<..."
	@$(call MKDIR,$(OBJ_DIR))
	$(CXX) $(CXXFLAGS) -c $< -o $@

# 清理
.PHONY: clean
clean:
	@echo "Cleaning build files..."
ifeq ($(OS),Windows_NT)
	@if exist $(subst /,\,$(OBJ_DIR)) $(RMDIR) $(subst /,\,$(OBJ_DIR))
	@if exist $(subst /,\,$(TARGET_PATH)) $(RM) $(subst /,\,$(TARGET_PATH))
else
	@$(RMDIR) $(OBJ_DIR)
	@$(RM) $(TARGET_PATH)
endif
	@echo "Clean complete."

# 重新编译
.PHONY: rebuild
rebuild: clean all

# 帮助信息
.PHONY: help
help:
	@echo "C++ Gateway Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make          - Build the project"
	@echo "  make clean    - Remove build files"
	@echo "  make rebuild  - Clean and rebuild"
	@echo "  make help     - Show this help message"
	@echo ""
	@echo "Supported platforms: Linux, macOS, Windows (MinGW)"
