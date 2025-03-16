import tkinter as tk
from tkinter import ttk, filedialog
from source.get_excel_stats import get_excel_stats
from source.load_excel_to_table import load_excel_to_table


class App(tk.Tk):
    """主应用程序类，继承自tk.Tk"""

    def __init__(self):
        """初始化应用程序窗口"""
        super().__init__()  # 调用父类构造函数

        style = ttk.Style()
        style.theme_use("default")

        self.title("对账工具")  # 设置窗口标题
        self.geometry("800x600")  # 增加窗口高度，提供更多空间
        self._configure_grid()  # 配置网格布局管理器
        self._create_widgets()  # 创建所有界面组件

    def _configure_grid(self):
        """配置网格布局行列权重，实现响应式布局"""
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # 为各区域分配明确的行和权重，确保有足够空间
        self.rowconfigure(0, weight=0)  # 文件加载区域 - 固定高度
        self.rowconfigure(1, weight=0)  # 分组条件区域 - 固定高度
        self.rowconfigure(2, weight=1)  # 对账结果区域 - 可扩展

    def _create_widgets(self):
        """创建所有界面组件"""
        self._create_file_loader()
        self._create_group_conditions()
        self._create_result_display()

    def _load_file_a(self):
        """加载甲方文件"""
        file_path = filedialog.askopenfilename(title="选择甲方文件", filetypes=[("Excel files", "*.xlsx *.xls")])
        self.table_a_file_path = file_path
        if file_path:
            result = get_excel_stats(file_path)
            sheet_names = result["sheet_names"]
            self.combo_a["values"] = sheet_names
            if sheet_names:
                self.combo_a.current(0)
                self._on_combo_a_select()

    def _on_combo_a_select(self, event=None):
        """甲方表选择事件"""
        selected_sheet = self.combo_a.get()
        self.part_a_conn = load_excel_to_table(self.table_a_file_path, selected_sheet, "part_a")
        cols_a = self.get_table_cols_from_db_conn(self.part_a_conn, "part_a")
        self.lbl_a.config(text=f"{selected_sheet} 共有 {len(cols_a)}列")

        # 如果乙方表已加载，更新共有列
        if self.combo_b.get():
            cols_b = self.get_table_cols_from_db_conn(self.part_b_conn, "part_b")
            common_cols = list(set(cols_a) & set(cols_b))
            self._update_group_combos(common_cols)

    def _load_file_b(self):
        """加载乙方文件"""
        file_path = filedialog.askopenfilename(title="选择乙方文件", filetypes=[("Excel files", "*.xlsx *.xls")])
        self.table_b_file_path = file_path
        if file_path:
            result = get_excel_stats(file_path)
            sheet_names = result["sheet_names"]
            self.combo_b["values"] = sheet_names
            if sheet_names:
                self.combo_b.current(0)
                self._on_combo_b_select()

    def _on_combo_b_select(self, event=None):
        """乙方表选择事件"""
        selected_sheet = self.combo_b.get()
        self.part_b_conn = load_excel_to_table(self.table_b_file_path, selected_sheet, "part_b")
        cols_b = self.get_table_cols_from_db_conn(self.part_b_conn, "part_b")
        self.lbl_b.config(text=f"{selected_sheet} 共有 {len(cols_b)}列")

        # 如果甲方表已加载，更新共有列
        if self.combo_a.get():
            cols_a = self.get_table_cols_from_db_conn(self.part_a_conn, "part_a")
            common_cols = list(set(cols_a) & set(cols_b))
            self._update_group_combos(common_cols)

    def _update_group_combos(self, columns):
        """更新所有分组下拉框的选项"""
        self.group1["values"] = columns
        self.group2["values"] = columns
        self.group3["values"] = columns
        if columns:
            self.group1.current(0)
            self.group2.current(0)
            self.group3.current(0)

    def get_table_cols_from_db_conn(self, conn, table_name):
        """从数据库连接获取列名"""
        return [col[1] for col in conn.sql(f"PRAGMA table_info('{table_name}')").fetchall()]

    def _create_file_loader(self):
        """创建文件加载区域"""
        frame = ttk.LabelFrame(self, text="文件加载", padding=10)
        frame.grid(row=0, column=0, columnspan=2, sticky="new", padx=10, pady=10)

        # 设置固定高度，确保内容完全可见
        frame.grid_propagate(False)
        frame.config(height=100)

        # 甲方文件控件
        ttk.Button(frame, text="加载甲方表", command=self._load_file_a).grid(row=0, column=0, padx=5, pady=2)
        self.combo_a = ttk.Combobox(frame, state="readonly")
        self.combo_a.bind("<<ComboboxSelected>>", self._on_combo_a_select)
        self.combo_a.grid(row=0, column=1, padx=5, pady=2)
        self.lbl_a = ttk.Label(frame, text="等待加载甲方表...", relief="sunken")
        self.lbl_a.grid(row=0, column=2, sticky="ew", padx=5, pady=2)

        # 乙方文件控件
        ttk.Button(frame, text="加载乙方表", command=self._load_file_b).grid(row=1, column=0, padx=5, pady=2)
        self.combo_b = ttk.Combobox(frame, state="readonly")
        self.combo_b.bind("<<ComboboxSelected>>", self._on_combo_b_select)
        self.combo_b.grid(row=1, column=1, padx=5, pady=2)
        self.lbl_b = ttk.Label(frame, text="等待加载乙方表...", relief="sunken")
        self.lbl_b.grid(row=1, column=2, sticky="ew", padx=5, pady=2)

        # 配置列权重
        frame.columnconfigure(2, weight=1)

    def _create_group_conditions(self):
        """创建分组条件区域"""
        frame = ttk.LabelFrame(self, text="分组条件", padding=10)
        frame.grid(row=1, column=0, columnspan=2, sticky="new", padx=10, pady=10)

        # 设置固定高度，确保内容完全可见
        frame.grid_propagate(False)
        frame.config(height=100)

        # 配置列权重，使列均匀分布
        for i in range(4):  # 三个分组列加一个按钮列
            frame.columnconfigure(i, weight=1)

        # 创建三个分组下拉框
        self.group1 = self._create_group_combo(frame, "分组一", 0)
        self.group2 = self._create_group_combo(frame, "分组二", 1)
        self.group3 = self._create_group_combo(frame, "分组三", 2)

        # 开始对账按钮 - 跨两行以与下拉框对齐
        ttk.Label(frame, text="").grid(row=0, column=3)  # 空标签保持对齐
        ttk.Button(frame, text="开始对账").grid(row=1, column=3, sticky="ew", padx=5)

    def _create_group_combo(self, parent, title, column):
        """创建单个分组下拉框"""
        # 直接在父框架中创建标签和下拉框
        ttk.Label(parent, text=title).grid(row=0, column=column, sticky="w", padx=5)
        combo = ttk.Combobox(parent, state="readonly")
        combo.grid(row=1, column=column, sticky="ew", padx=5)

        return combo

    def _create_result_display(self):
        """创建结果展示区域"""
        frame = ttk.LabelFrame(self, text="对账结果", padding=10)
        frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        text = tk.Text(frame, wrap="word")
        scrollbar = ttk.Scrollbar(frame, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)

        text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)


if __name__ == "__main__":
    app = App()
    app.mainloop()
