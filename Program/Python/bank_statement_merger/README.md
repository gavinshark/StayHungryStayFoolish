# 使用步骤
1、安装python 3.10+
要求windows 10以上
https://mirrors.aliyun.com/python-release/windows/python-3.12.0-amd64.exe
双击exe安装，勾选add to path

2、编辑映射关系
打开mapping_config.csv，编辑 银行excel表头：目标excel表头 关系

3、运行主程序
双击start-up.bat

4、点击“导入文件夹”，选择银行流水文件夹

5、点击“导出汇总”，选择保存结果位置


# 多银行流水汇总工具

支持多家银行流水文件的自动识别、字段映射和汇总导出。

## 功能特点

- 支持 xls、xlsx、csv 三种格式
- 自动识别银行类型（工商、建设、招商、农业、中国银行）
- 自动映射字段名称为统一格式
- 批量处理文件夹内所有流水文件
- 可视化预览汇总结果
- 导出汇总数据

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 使用说明

1. 点击「导入文件夹」选择包含银行流水的文件夹
2. 程序自动识别银行类型并映射字段
3. 在预览区查看汇总结果
4. 点击「导出汇总」保存结果

## 生成Demo文件

点击「生成Demo文件」可生成：
- 映射配置文件 (mapping_config.json)
- 工商银行示例 (.xlsx)
- 建设银行示例 (.xls)
- 招商银行示例 (.csv)

## 自定义映射

编辑 `mapping_config.json` 添加新银行或修改映射规则。
