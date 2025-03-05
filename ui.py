import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
import warnings
from typing import Optional, Dict, Union, List
from source.get_excel_stats import get_excel_stats
from source.get_excel_cols import get_excel_cols
from source.reconcile_accounts import reconcile_accounts

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


class ReconciliationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("财务对账工具 v1.0")
        self.geometry("800x600")
        self.df = None
        self.excel_file = None
        self.current_file_path = None

        # 界面布局
        self.create_widgets()

        # 绑定事件
        self.btn_load.configure(command=self.load_file)
        self.sheet_selector.configure(command=self.on_sheet_selected)
        self.btn_calculate.configure(command=self.perform_reconciliation)

    def create_widgets(self):
        """创建所有界面组件"""
        # 文件选择区域
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, padx=10, fill="x")

        self.btn_load = ctk.CTkButton(self.file_frame, text="加载Excel文件", width=120)
        self.btn_load.pack(side="left", padx=5)

        self.file_info_label = ctk.CTkLabel(
            self.file_frame, text="未选择文件", anchor="w"
        )
        self.file_info_label.pack(side="left", fill="x", expand=True)

        # 工作表选择区域
        self.sheet_frame = ctk.CTkFrame(self)
        self.sheet_frame.pack(pady=10, padx=10, fill="x")

        self.sheet_label = ctk.CTkLabel(self.sheet_frame, text="选择工作表:", width=80)
        self.sheet_label.pack(side="left")

        self.sheet_selector = ctk.CTkComboBox(
            self.sheet_frame, values=[], state="disabled", width=300
        )
        self.sheet_selector.pack(side="left", padx=5)

        # 列选择区域
        self.column_frame = ctk.CTkFrame(self)
        self.column_frame.pack(pady=10, padx=10, fill="x")

        self.column_a_label = ctk.CTkLabel(self.column_frame, text="比对列A:", width=80)
        self.column_a_label.pack(side="left")

        self.column_a = ctk.CTkComboBox(
            self.column_frame, values=[], state="disabled", width=300
        )
        self.column_a.pack(side="left", padx=5)

        self.column_b_label = ctk.CTkLabel(self.column_frame, text="比对列B:", width=80)
        self.column_b_label.pack(side="left", padx=(20, 0))

        self.column_b = ctk.CTkComboBox(
            self.column_frame, values=[], state="disabled", width=300
        )
        self.column_b.pack(side="left", padx=5)

        # 操作按钮区域
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10, padx=10)

        self.btn_calculate = ctk.CTkButton(
            self.btn_frame, text="开始对账", state="disabled", width=120
        )
        self.btn_calculate.pack(side="left", padx=5)

        # 结果显示区域
        self.result_frame = ctk.CTkFrame(self)
        self.result_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.result_text = ctk.CTkTextbox(
            self.result_frame, wrap="word", font=("Consolas", 12)
        )
        self.result_text.pack(fill="both", expand=True)

        # 进度条
        self.progressbar = ctk.CTkProgressBar(
            self.result_frame, mode="indeterminate", height=3
        )

    def setup_events(self):
        """绑定事件处理"""
        self.btn_load.configure(command=self.load_file)
        self.sheet_selector.configure(command=self.on_sheet_selected)
        self.btn_calculate.configure(command=self.execute_reconciliation)

    def configure_tags(self):
        """配置文本标签样式"""
        self.result_text.tag_config("error", foreground="red")
        self.result_text.tag_config("success", foreground="green")
        self.result_text.tag_config("header", font=("Arial", 14, "bold"))
        self.result_text.tag_config("subheader", font=("Arial", 12, "bold"))
        self.result_text.tag_config("highlight", foreground="#2ecc71")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.current_file_path = file_path
            # 使用get_excel_stats获取Excel信息
            excel_info = get_excel_stats(file_path)
            if excel_info:
                self.excel_file = pd.ExcelFile(file_path)
                self.file_info_label.configure(
                    text=f"已选择: {file_path}\n工作表数量: {excel_info['sheet_count']}"
                )

                # 更新工作表选择下拉框
                self.sheet_selector.configure(
                    values=excel_info["sheet_names"], state="normal"
                )
                self.sheet_selector.set(excel_info["sheet_names"][0])
                self.on_sheet_selected()  # 触发工作表选择事件

    def on_sheet_selected(self, event=None):
        selected_sheet = self.sheet_selector.get()
        if selected_sheet and self.current_file_path:
            # 使用get_excel_cols获取列信息
            columns = get_excel_cols(self.current_file_path, selected_sheet)

            # 更新列选择下拉框
            self.column_a.configure(values=columns, state="normal")
            self.column_b.configure(values=columns, state="normal")

            if len(columns) > 0:
                self.column_a.set(columns[0])
                self.column_b.set(columns[0] if len(columns) == 1 else columns[1])

            self.enable_controls()

    def perform_reconciliation(self):
        if not self.current_file_path:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", "请先选择Excel文件")
            return

        selected_sheet = self.sheet_selector.get()
        col_a = self.column_a.get()
        col_b = self.column_b.get()

        if col_a == col_b:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", "请选择不同的列进行对账")
            return

        # 执行对账操作
        try:
            result = reconcile_accounts(
                self.current_file_path, col_a, col_b, selected_sheet
            )

            # 显示结果
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", result)

        except Exception as e:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", f"对账过程中发生错误：{str(e)}")

    def enable_controls(self):
        self.btn_calculate.configure(state="normal")


if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    app = ReconciliationApp()
    app.mainloop()
