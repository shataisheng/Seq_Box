"""
Seq_Box - 历史记录页面
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt

from .base_page import BasePage, COLORS


class HistoryPage(BasePage):
    """历史记录页面"""
    
    def __init__(self, parent=None):
        super().__init__("历史记录", parent)
        self.history = []
    
    def setup_ui(self):
        super().setup_ui()
        
        # 说明
        desc = QLabel("显示最近的操作记录")
        desc.setStyleSheet(f"color: {COLORS['fg']}; padding-bottom: 10px;")
        self.layout.addWidget(desc)
        
        # 历史记录表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["时间", "操作", "输入", "输出"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        self.layout.addWidget(self.table)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        btn_refresh = QPushButton("🔄 刷新")
        btn_refresh.clicked.connect(self.load_history)
        btn_layout.addWidget(btn_refresh)
        
        btn_clear = QPushButton("🗑️ 清空")
        btn_clear.clicked.connect(self.clear_history)
        btn_layout.addWidget(btn_clear)
        
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)
        
        # 加载历史
        self.load_history()
    
    def load_history(self):
        """加载历史记录"""
        # 这里可以从文件加载历史记录
        # 目前仅显示示例数据
        self.history = [
            {"time": "--", "operation": "暂无历史记录", "input": "--", "output": "--"}
        ]
        
        self.table.setRowCount(len(self.history))
        for i, record in enumerate(self.history):
            self.table.setItem(i, 0, QTableWidgetItem(record["time"]))
            self.table.setItem(i, 1, QTableWidgetItem(record["operation"]))
            self.table.setItem(i, 2, QTableWidgetItem(record["input"]))
            self.table.setItem(i, 3, QTableWidgetItem(record["output"]))
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self.table.setRowCount(0)
        self.log("历史记录已清空")
    
    def add_record(self, operation: str, input_info: str, output_info: str):
        """添加历史记录"""
        from datetime import datetime
        
        record = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operation": operation,
            "input": input_info,
            "output": output_info
        }
        self.history.append(record)
        self.load_history()
