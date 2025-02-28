import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


class ReconciliationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("财务对账工具 v1.0")
        self.geometry("800x600")
        self.df = None

        # 界面布局
        self.create_widgets()

    def create_widgets(self):
        # 文件选择部分
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, padx=10, fill="x")

        self.btn_load = ctk.CTkButton(
            self.file_frame, text="加载Excel文件", command=self.load_file
        )
        self.btn_load.pack(side="left", padx=5)

        self.file_info_label = ctk.CTkLabel(self.file_frame, text="未选择文件")
        self.file_info_label.pack(side="left", padx=10)

        # 列选择部分
        self.selection_frame = ctk.CTkFrame(self)
        self.selection_frame.pack(pady=10, padx=10, fill="x")

        self.column_a = ctk.CTkComboBox(
            self.selection_frame, values=[], state="disabled", width=200
        )
        self.column_a.pack(side="left", padx=5)

        self.column_b = ctk.CTkComboBox(
            self.selection_frame, values=[], state="disabled", width=200
        )
        self.column_b.pack(side="left", padx=5)

        self.btn_calculate = ctk.CTkButton(
            self.selection_frame,
            text="开始对账",
            command=self.calculate_reconciliation,
            state="disabled",
        )
        self.btn_calculate.pack(side="left", padx=5)

        # 结果显示
        self.result_text = ctk.CTkTextbox(self, wrap="word")
        self.result_text.pack(pady=10, padx=10, fill="both", expand=True)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                self.update_file_info()
                self.enable_controls()
            except Exception as e:
                self.file_info_label.configure(text=f"错误: {str(e)}")

    def update_file_info(self):
        if self.df is not None:
            info = f"已加载文件 | 行数: {len(self.df)} | 列数: {len(self.df.columns)}"
            self.file_info_label.configure(text=info)

            columns = self.df.columns.tolist()
            self.column_a.configure(values=columns, state="readonly")
            self.column_b.configure(values=columns, state="readonly")
            self.column_a.set(columns[0])
            self.column_b.set(columns[1] if len(columns) > 1 else "")

    def enable_controls(self):
        self.btn_calculate.configure(state="normal")

    def calculate_reconciliation(self):
        if self.df is None:
            return

        col_a = self.column_a.get()
        col_b = self.column_b.get()

        if not col_a or not col_b:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", "请选择需要对比的两列")
            return

        try:
            set_a = set(self.df[col_a].dropna().astype(str))
            set_b = set(self.df[col_b].dropna().astype(str))

            a_only = set_a - set_b
            b_only = set_b - set_a
            matches = set_a & set_b

            result = [
                f"【对账结果】",
                f"列 {col_a} 独有项 ({len(a_only)} 条):",
                "\n".join(sorted(a_only)[:10]),  # 显示前10条
                "\n--------------------------",
                f"列 {col_b} 独有项 ({len(b_only)} 条):",
                "\n".join(sorted(b_only)[:10]),
                "\n--------------------------",
                f"匹配项数量: {len(matches)}",
            ]

            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", "\n".join(result))

        except Exception as e:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", f"计算错误: {str(e)}")


if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    app = ReconciliationApp()
    app.mainloop()
