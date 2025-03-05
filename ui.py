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
        self.geometry("1000x800")
        self.df = None
        self.excel_file = None
        self.current_file_path = None

        # 配置主题和颜色
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 创建界面组件
        self.create_widgets()
        self.configure_tags()

        # 绑定事件
        self.setup_events()

    def create_widgets(self):
        """创建所有界面组件"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # 文件选择区域
        self.file_frame = ctk.CTkFrame(self, corner_radius=10)
        self.file_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.file_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.file_frame, text="文件操作", font=("Microsoft YaHei", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        self.btn_load = ctk.CTkButton(
            self.file_frame,
            text="选择Excel文件",
            width=120,
            fg_color="#4B8DDE",
            hover_color="#3675B3",
        )
        self.btn_load.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.file_info_label = ctk.CTkLabel(
            self.file_frame, text="未选择任何文件", text_color="#666666", anchor="w"
        )
        self.file_info_label.grid(row=1, column=1, padx=10, sticky="ew")

        # 工作表选择区域
        self.sheet_frame = ctk.CTkFrame(self, corner_radius=10)
        self.sheet_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(
            self.sheet_frame, text="工作表设置", font=("Microsoft YaHei", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        ctk.CTkLabel(self.sheet_frame, text="选择工作表:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.sheet_selector = ctk.CTkComboBox(
            self.sheet_frame,
            values=[],
            state="disabled",
            width=300,
            dropdown_fg_color="#F0F0F0",
        )
        self.sheet_selector.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # 列选择区域
        self.column_frame = ctk.CTkFrame(self, corner_radius=10)
        self.column_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.column_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(
            self.column_frame, text="对账设置", font=("Microsoft YaHei", 14, "bold")
        ).grid(row=0, column=0, columnspan=4, pady=5, sticky="w")

        ctk.CTkLabel(self.column_frame, text="比对列 A:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.column_a = ctk.CTkComboBox(
            self.column_frame,
            values=[],
            state="disabled",
            width=200,
            dropdown_fg_color="#F0F0F0",
        )
        self.column_a.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.column_frame, text="比对列 B:").grid(
            row=1, column=2, padx=10, pady=5, sticky="w"
        )
        self.column_b = ctk.CTkComboBox(
            self.column_frame,
            values=[],
            state="disabled",
            width=200,
            dropdown_fg_color="#F0F0F0",
        )
        self.column_b.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        # 操作按钮区域（修改此处）
        self.btn_frame = ctk.CTkFrame(self, corner_radius=10)
        self.btn_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.btn_frame.grid_columnconfigure(0, weight=1)  # 新增列权重配置

        self.btn_calculate = ctk.CTkButton(
            self.btn_frame,
            text="开始对账",
            state="disabled",
            fg_color="#5DAE8B",
            hover_color="#4C8C6D",
            height=40
        )
        self.btn_calculate.grid(row=0, column=0, padx=20, pady=10, sticky="ew")  # 改为grid布局

        # 结果显示区域（修改此处）
        self.result_frame = ctk.CTkFrame(self, corner_radius=10)
        self.result_frame.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_rowconfigure(0, weight=1)

        self.result_text = ctk.CTkTextbox(
            self.result_frame,
            wrap="word",
            font=("Microsoft YaHei", 11),  # 调小字体大小
            fg_color="#F8F9FA",
            text_color="#333333",
            scrollbar_button_color="#D3D3D3",
            padx=15,  # 增加水平内边距
            pady=15   # 增加垂直内边距
        )
        self.result_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 进度条
        self.progressbar = ctk.CTkProgressBar(
            self,
            mode="indeterminate",
            height=3,
            fg_color="#E9ECEF",
            progress_color="#4B8DDE",
        )
    def configure_tags(self):
        """配置文本标签样式（适配 CustomTkinter 限制）"""
        # 使用统一的文本区域字体
        self.result_text.configure(font=("Microsoft YaHei", 12))

        # 仅配置颜色样式（不设置字体）
        self.result_text.tag_config("header", foreground="#2C3E50")
        self.result_text.tag_config("subheader", foreground="#34495E")
        self.result_text.tag_config("success", foreground="#27AE60")
        self.result_text.tag_config("warning", foreground="#F39C12")
        self.result_text.tag_config("error", foreground="#E74C3C")
        self.result_text.tag_config("highlight", foreground="#2980B9")

        # 通过添加空格和符号模拟标题样式
        self.result_text.tag_config("title_pad", spacing3=15)
        self.result_text.tag_config("section_pad", spacing2=10)

    def setup_events(self):
        """绑定事件处理"""
        self.btn_load.configure(command=self.load_file)
        self.sheet_selector.configure(command=self.on_sheet_selected)
        self.btn_calculate.configure(command=self.perform_reconciliation)

    def show_progress(self):
        """显示进度条"""
        self.progressbar.grid(row=5, column=0, sticky="ew", padx=20)
        self.progressbar.start()

    def hide_progress(self):
        """隐藏进度条"""
        self.progressbar.stop()
        self.progressbar.grid_forget()

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel文件", "*.xlsx *.xls")]
        )
        if file_path:
            try:
                self.show_progress()
                self.current_file_path = file_path
                excel_info = get_excel_stats(file_path)
                if excel_info:
                    self.excel_file = pd.ExcelFile(file_path)
                    self.file_info_label.configure(
                        text=f"已选文件: {file_path}\n工作表数: {excel_info['sheet_count']}",
                        text_color="#333333",
                    )
                    self.sheet_configure(excel_info)
            except Exception as e:
                self.result_text.insert(
                    "end", f"错误: 文件读取失败 - {str(e)}\n", "error"
                )
            finally:
                self.hide_progress()

    def sheet_configure(self, excel_info):
        """配置工作表选项"""
        self.sheet_selector.configure(values=excel_info["sheet_names"], state="normal")
        self.sheet_selector.set(excel_info["sheet_names"][0])
        self.on_sheet_selected()

    def on_sheet_selected(self, event=None):
        selected_sheet = self.sheet_selector.get()
        if selected_sheet and self.current_file_path:
            try:
                self.show_progress()
                columns = get_excel_cols(self.current_file_path, selected_sheet)
                self.column_configure(columns)
            except Exception as e:
                self.result_text.insert(
                    "end", f"错误: 读取列信息失败 - {str(e)}\n", "error"
                )
            finally:
                self.hide_progress()

    def column_configure(self, columns):
        """配置列选项"""
        for combo in [self.column_a, self.column_b]:
            combo.configure(values=columns, state="normal")
        if columns:
            self.column_a.set(columns[0])
            self.column_b.set(columns[1] if len(columns) > 1 else columns[0])
        self.btn_calculate.configure(state="normal")

    def perform_reconciliation(self):
        if not self.validate_inputs():
            return

        try:
            self.show_progress()
            result = reconcile_accounts(
                self.current_file_path,
                self.column_a.get(),
                self.column_b.get(),
                self.sheet_selector.get(),
            )
            self.display_result(result)
        except Exception as e:
            self.result_text.insert("end", f"\n错误: 对账失败 - {str(e)}\n", "error")
        finally:
            self.hide_progress()

    def validate_inputs(self):
        """验证输入有效性"""
        if self.column_a.get() == self.column_b.get():
            self.result_text.insert("end", "错误: 请选择不同的比对列\n", "error")
            return False
        return True

    def display_result(self, result):
        """显示对账结果"""
        self.result_text.delete("1.0", "end")

        # 使用符号和颜色模拟标题样式
        self.result_text.insert(
            "end", "◆" * 5 + " 对账结果报告 " + "◆" * 5 + "\n", ("header", "title_pad")
        )
        self.result_text.insert("end", "=" * 40 + "\n", "section_pad")
        self.result_text.insert("end", result)
        self.result_text.insert("end", "\n" + "=" * 40 + "\n", "section_pad")
        self.result_text.see("end")


if __name__ == "__main__":
    app = ReconciliationApp()
    app.mainloop()
