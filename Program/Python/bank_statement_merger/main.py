"""
多银行流水汇总程序
支持 xls, xlsx, csv 格式
使用 PyQt6 图形界面
"""

import sys
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont


class BankStatementMerger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多银行流水汇总工具")
        self.setGeometry(100, 100, 900, 700)
        self.setWindowIcon(self.create_app_icon())
        
        self.result_column_order = []  # 记录结果列的顺序
        self.mapping_config = self.load_mapping_config()
        self.merged_data = None
        self.import_folder_path = None  # 记录导入的文件夹路径
        
        self.setup_ui()
    
    def create_app_icon(self):
        """创建应用图标"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制蓝色圆形背景
        painter.setBrush(QColor(66, 133, 244))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 60, 60)
        
        # 绘制白色文字 "¥"
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 32, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "¥")
        
        painter.end()
        return QIcon(pixmap)
    
    def load_mapping_config(self):
        """加载映射配置"""
        config_path = Path(__file__).parent / "mapping_config.csv"
        if config_path.exists():
            try:
                df = pd.read_csv(config_path, encoding='utf-8')
                mapping_config = {}
                
                # 获取银行列名（除了第一列结果表头）
                bank_columns = df.columns[1:].tolist()
                
                # 记录结果表头的顺序
                self.result_column_order = df.iloc[:, 0].tolist()
                
                # 初始化每个银行的映射配置
                for bank in bank_columns:
                    mapping_config[bank] = {}
                
                # 从CSV构建映射配置
                for _, row in df.iterrows():
                    result_header = row.iloc[0]  # 结果表头
                    
                    # 为每个银行添加映射
                    for i, bank in enumerate(bank_columns, 1):
                        bank_col = row.iloc[i]
                        if pd.notna(bank_col) and str(bank_col).strip():
                            mapping_config[bank][str(bank_col).strip()] = result_header
                
                return mapping_config
            except Exception as e:
                self.log(f"读取CSV配置文件失败: {e}")
                return self.get_default_mapping()
        return self.get_default_mapping()
    
    def get_default_mapping(self):
        """默认映射配置"""
        # 设置默认的列顺序
        self.result_column_order = [
            "交易日期", "记账日期", "账号", "账户", "对方账号", 
            "金额", "发生额", "备注", "摘要", "面额余额", "账户余额"
        ]
        
        return {
            "工商银行": {
                "交易时间": "交易日期", "交易日期": "记账日期", "帐户": "账号", "账户": "账户",
                "对方账户": "对方账号", "交易金额": "金额", "发生额": "发生额",
                "摘要": "备注", "交易摘要": "摘要", "余额": "面额余额", "账户余额": "账户余额"
            },
            "建设银行": {
                "时间": "交易日期", "记账日期": "记账日期", "帐号": "账号", "卡号": "账户",
                "对方帐号": "对方账号", "金额": "金额", "收支金额": "发生额",
                "备注信息": "备注", "附言": "摘要", "当前余额": "面额余额"
            },
            "招商银行": {
                "交易日": "交易日期", "入账日期": "记账日期", "账户号": "账号", "我方账号": "账户",
                "他方账号": "对方账号", "交易额": "金额", "人民币金额": "发生额",
                "用途": "备注", "交易备注": "摘要", "账面余额": "面额余额"
            },
            "农业银行": {
                "交易时间": "交易日期", "记账时间": "记账日期", "本方账号": "账号", "账号": "账户",
                "对方账号": "对方账号", "交易金额": "金额", "发生金额": "发生额",
                "摘要": "备注", "附言": "摘要", "账户余额": "账户余额"
            },
            "中国银行": {
                "交易日期": "交易日期", "记账日期": "记账日期", "账户": "账号", "本方账户": "账户",
                "对方账户": "对方账号", "交易金额": "金额", "借贷金额": "发生额",
                "交易摘要": "备注", "备注": "摘要", "余额": "面额余额"
            }
        }
    
    def setup_ui(self):
        """设置界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 顶部按钮区
        btn_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("导入文件夹")
        self.import_btn.clicked.connect(self.import_folder)
        btn_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("导出汇总")
        self.export_btn.clicked.connect(self.export_merged)
        self.export_btn.setEnabled(False)
        btn_layout.addWidget(self.export_btn)
        
        self.gen_demo_btn = QPushButton("生成Demo文件")
        self.gen_demo_btn.clicked.connect(self.generate_demo_files)
        btn_layout.addWidget(self.gen_demo_btn)
        
        btn_layout.addStretch()
        
        self.status_label = QLabel("请选择文件夹导入银行流水")
        btn_layout.addWidget(self.status_label)
        
        layout.addLayout(btn_layout)
        
        # 日志区域
        log_group = QGroupBox("处理日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)
        
        # 数据预览区
        preview_group = QGroupBox("数据预览")
        preview_layout = QVBoxLayout(preview_group)
        self.table = QTableWidget()
        preview_layout.addWidget(self.table)
        layout.addWidget(preview_group)
    
    def log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def import_folder(self):
        """导入文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择包含银行流水的文件夹")
        if not folder:
            return
        
        self.import_folder_path = Path(folder)
        self.log(f"选择文件夹: {folder}")
        self.process_folder(folder)
    
    def detect_bank(self, columns):
        """根据列名检测银行类型，要求全部字段匹配"""
        columns_set = set(columns)
        for bank_name, mapping in self.mapping_config.items():
            mapping_keys = set(mapping.keys())
            if columns_set.issubset(mapping_keys):
                return bank_name, mapping
        return None, None
    
    def apply_mapping(self, df, mapping):
        """应用字段映射"""
        rename_dict = {col: mapping[col] for col in df.columns if col in mapping}
        return df.rename(columns=rename_dict)
    
    def reorder_columns(self, df):
        """按照CSV配置的顺序重新排列列"""
        if not self.result_column_order:
            return df
        
        # 获取数据框中实际存在的列
        existing_columns = df.columns.tolist()
        
        # 按照配置顺序排列存在的列
        ordered_columns = []
        for col in self.result_column_order:
            if col in existing_columns:
                ordered_columns.append(col)
        
        # 添加不在配置中但存在于数据框的列（如"来源文件"）
        for col in existing_columns:
            if col not in ordered_columns:
                ordered_columns.append(col)
        
        return df[ordered_columns]
    
    def read_file(self, filepath):
        """读取单个文件"""
        ext = filepath.suffix.lower()
        try:
            if ext == '.csv':
                df = pd.read_csv(filepath, encoding='utf-8')
            elif ext == '.xls':
                df = pd.read_excel(filepath, engine='xlrd')
            elif ext == '.xlsx':
                df = pd.read_excel(filepath, engine='openpyxl')
            else:
                return None
            return df
        except UnicodeDecodeError:
            if ext == '.csv':
                return pd.read_csv(filepath, encoding='gbk')
        except Exception as e:
            self.log(f"读取文件失败 {filepath.name}: {e}")
            return None
    
    def process_folder(self, folder):
        """处理文件夹中的所有文件"""
        folder_path = Path(folder)
        files = list(folder_path.glob("*.xls")) + \
                list(folder_path.glob("*.xlsx")) + \
                list(folder_path.glob("*.csv"))
        
        if not files:
            QMessageBox.warning(self, "警告", "文件夹中没有找到 Excel 或 CSV 文件")
            return
        
        all_data = []
        processed = 0
        
        for filepath in files:
            self.log(f"处理文件: {filepath.name}")
            df = self.read_file(filepath)
            
            if df is None or df.empty:
                self.log(f"  跳过空文件或读取失败")
                continue
            
            bank_name, mapping = self.detect_bank(df.columns.tolist())
            
            if bank_name:
                self.log(f"  识别为: {bank_name}")
                df = self.apply_mapping(df, mapping)
            else:
                self.log(f"  未识别银行类型，保留原始列名")
            
            df['来源文件'] = filepath.name
            all_data.append(df)
            processed += 1
        
        if all_data:
            self.merged_data = pd.concat(all_data, ignore_index=True)
            # 按照CSV配置的顺序重新排列列
            self.merged_data = self.reorder_columns(self.merged_data)
            self.log(f"汇总完成: 共处理 {processed} 个文件, {len(self.merged_data)} 条记录")
            self.status_label.setText(f"已汇总 {len(self.merged_data)} 条记录")
            self.export_btn.setEnabled(True)
            self.update_preview()
        else:
            QMessageBox.warning(self, "警告", "没有成功处理任何文件")
    
    def update_preview(self):
        """更新数据预览"""
        if self.merged_data is None or self.merged_data.empty:
            return
        
        df = self.merged_data.head(100)
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns.tolist())
        
        for i, row in df.iterrows():
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val) if pd.notna(val) else "")
                self.table.setItem(i, j, item)
        
        self.table.resizeColumnsToContents()
    
    def get_account_columns(self):
        """获取所有账号相关的列名"""
        account_cols = {"账号", "对方账号"}
        # 从映射配置中收集所有映射到账号的原始列名
        for mapping in self.mapping_config.values():
            for orig, mapped in mapping.items():
                if mapped in account_cols:
                    account_cols.add(orig)
        return account_cols
    
    def format_account_for_export(self, df):
        """账号列保持原样"""
        return df.copy()
    
    def export_merged(self):
        """导出汇总数据"""
        if self.merged_data is None:
            return
        
        # 默认路径为导入文件夹的上一级
        default_dir = ""
        if self.import_folder_path:
            default_dir = str(self.import_folder_path.parent)
        
        # 默认文件名为 汇总结果-时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"汇总结果-{timestamp}.xlsx"
        default_path = str(Path(default_dir) / default_filename) if default_dir else default_filename
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "保存汇总文件", default_path, "Excel文件 (*.xlsx);;CSV文件 (*.csv)"
        )
        
        if not filepath:
            return
        
        try:
            # 对账号列添加前置单引号
            export_data = self.format_account_for_export(self.merged_data)
            
            if filepath.endswith('.csv'):
                export_data.to_csv(filepath, index=False, encoding='utf-8-sig')
            else:
                export_data.to_excel(filepath, index=False, engine='openpyxl')
            
            self.log(f"导出成功: {filepath}")
            QMessageBox.information(self, "成功", f"汇总数据已导出到:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def generate_demo_files(self):
        """生成Demo文件"""
        folder = QFileDialog.getExistingDirectory(self, "选择Demo文件保存位置")
        if not folder:
            return
        
        folder_path = Path(folder)
        
        # 生成映射配置文件
        config_path = folder_path / "mapping_config.csv"
        # 创建CSV格式的配置文件，包含所有银行
        csv_data = {
            '结果表头': ['日期', '日期', '账号', '账号', '对方账号', '金额', '金额', '备注', '备注', '余额', '余额'],
            '工商银行': ['交易时间', '交易日期', '帐户', '账户', '对方账户', '交易金额', '发生额', '摘要', '交易摘要', '余额', '账户余额'],
            '建设银行': ['时间', '记账日期', '帐号', '卡号', '对方帐号', '金额', '收支金额', '备注信息', '附言', '当前余额', ''],
            '招商银行': ['交易日', '入账日期', '账户号', '我方账号', '他方账号', '交易额', '人民币金额', '用途', '交易备注', '账面余额', ''],
            '农业银行': ['交易时间', '记账时间', '本方账号', '账号', '对方账号', '交易金额', '发生金额', '摘要', '附言', '账户余额', ''],
            '中国银行': ['交易日期', '记账日期', '账户', '本方账户', '对方账户', '交易金额', '借贷金额', '交易摘要', '备注', '余额', '']
        }
        config_df = pd.DataFrame(csv_data)
        config_df.to_csv(config_path, index=False, encoding='utf-8-sig')
        self.log(f"生成映射配置: {config_path.name}")
        
        # 工商银行示例数据
        icbc_data = {
            "交易时间": ["2024-01-01 10:30:00", "2024-01-02 14:20:00", "2024-01-03 09:15:00"],
            "帐户": ["6222021234567890", "6222021234567890", "6222021234567890"],
            "对方账户": ["6228481234567890", "6225881234567890", "6217001234567890"],
            "交易金额": [1000.00, -500.50, 2000.00],
            "摘要": ["工资", "转账", "报销"],
            "余额": [10000.00, 9499.50, 11499.50]
        }
        
        # 建设银行示例数据
        ccb_data = {
            "时间": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "帐号": ["6217001234567890", "6217001234567890", "6217001234567890"],
            "对方帐号": ["6222021234567890", "6228481234567890", "6225881234567890"],
            "金额": [500.00, -200.00, 1500.00],
            "备注信息": ["收款", "消费", "转入"],
            "当前余额": [5000.00, 4800.00, 6300.00]
        }
        
        # 招商银行示例数据
        cmb_data = {
            "交易日": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "账户号": ["6225881234567890", "6225881234567890", "6225881234567890"],
            "他方账号": ["6222021234567890", "6217001234567890", "6228481234567890"],
            "交易额": [800.00, -300.00, 1200.00],
            "用途": ["收入", "支出", "转账"],
            "账面余额": [8000.00, 7700.00, 8900.00]
        }
        
        # 农业银行示例数据
        abc_data = {
            "交易时间": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "本方账号": ["6228481234567890", "6228481234567890", "6228481234567890"],
            "对方账号": ["6222021234567890", "6217001234567890", "6225881234567890"],
            "交易金额": [600.00, -150.00, 900.00],
            "摘要": ["转入", "提取", "收入"],
            "账户余额": [6000.00, 5850.00, 6750.00]
        }
        
        # 中国银行示例数据
        boc_data = {
            "交易日期": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "账户": ["6217001234567890", "6217001234567890", "6217001234567890"],
            "对方账户": ["6222021234567890", "6228481234567890", "6225881234567890"],
            "交易金额": [500.00, -200.00, 1500.00],
            "交易摘要": ["收款", "消费", "转入"],
            "余额": [5000.00, 4800.00, 6300.00]
        }
        
        demo_files = [
            ("工商银行流水_demo.xlsx", icbc_data, "xlsx"),
            ("建设银行流水_demo.xls", ccb_data, "xls"),
            ("招商银行流水_demo.csv", cmb_data, "csv"),
            ("农业银行流水_demo.xlsx", abc_data, "xlsx"),
            ("中国银行流水_demo.csv", boc_data, "csv")
        ]
        
        for filename, data, fmt in demo_files:
            df = pd.DataFrame(data)
            filepath = folder_path / filename
            
            try:
                if fmt == "csv":
                    df.to_csv(filepath, index=False, encoding='utf-8-sig')
                elif fmt == "xlsx":
                    df.to_excel(filepath, index=False, engine='openpyxl')
                elif fmt == "xls":
                    try:
                        df.to_excel(filepath, index=False, engine='xlwt')
                    except:
                        filepath = folder_path / filename.replace('.xls', '.xlsx')
                        df.to_excel(filepath, index=False, engine='openpyxl')
                
                self.log(f"生成Demo文件: {filepath.name}")
            except Exception as e:
                self.log(f"生成失败 {filename}: {e}")
        
        QMessageBox.information(self, "成功", f"Demo文件已生成到:\n{folder}")


def main():
    app = QApplication(sys.argv)
    window = BankStatementMerger()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
