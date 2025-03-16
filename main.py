import tkinter as tk
from tkinter import ttk, filedialog  # 添加ttk导入

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
        self.geometry("800x500")  # 设置初始窗口尺寸
        self._configure_grid()  # 配置网格布局管理器
        self._create_widgets()  # 创建所有界面组件

    def _configure_grid(self):
        """配置网格布局行列权重，实现响应式布局"""
        self.columnconfigure(0, weight=1)  # 配置列权重
        self.columnconfigure(1, weight=1)  # 配置列权重

        # 行配置（结果区域需要更多空间）
        self.rowconfigure(1, weight=1)  # 分组条件区域
        self.rowconfigure(2, weight=1)  # 分组条件区域
        self.rowconfigure(3, weight=4)  # 结果显示区域（分配更多权重）

    def _create_widgets(self):
        """创建所有界面组件"""
        self._create_file_loader()  # 创建文件加载区域
        self._create_group_conditions()  # 创建分组条件区域
        self._create_result_display()  # 创建结果显示区域

    def _load_file_a(self):
        """加载甲方文件"""
        file_path = tk.filedialog.askopenfilename(title="选择甲方文件", filetypes=[("Excel files", "*.xlsx *.xls")])
        self.table_a_file_path = file_path  # 保存文件路径
        if file_path:
            result = get_excel_stats(file_path)
            sheet_names = result["sheet_names"]
            self.combo_a["values"] = sheet_names
            if sheet_names:
                self.combo_a.current(0)  # 默认选中第一个
                self._on_combo_a_select()  # 触发选中事件

    def get_table_cols_from_db_conn(self, conn, table_name):
        """从数据库连接中获取表的列名"""
        columns_info = conn.sql(f"PRAGMA table_info('{table_name}');".strip()).fetchall()

        column_names = [column[1] for column in columns_info]

        return column_names

    def _on_combo_a_select(self, event=None):
        """当下拉框的值变化时触发的事件"""

        selected_value = self.combo_a.get()  # 获取当前选中的值
        print(f"选中的值: {selected_value}")
        self.part_a_conn = load_excel_to_table(self.table_a_file_path, selected_value, "part_a")
        table_cols = self.get_table_cols_from_db_conn(self.part_a_conn, "part_a")
        self.lbl_a.config(text=f"{selected_value} 共有 {len(table_cols)}列")

        if len(self.combo_b.get()):
            print("乙方表已经加载，可以开始对账")
            for col in table_cols:
                self.group1.insert(tk.END, col)
                self.group2.insert(tk.END, col)
                self.group3.insert(tk.END, col)
        else:
            print("乙方表未加载，无法开始对账")

    def _load_file_b(self):
        """加载甲方文件"""

        file_path = tk.filedialog.askopenfilename(title="选择乙方文件", filetypes=[("Excel files", "*.xlsx *.xls")])
        self.table_b_file_path = file_path  # 保存文件路径
        print(self.table_b_file_path)
        if file_path:
            result = get_excel_stats(file_path)
            sheet_names = result["sheet_names"]
            self.combo_b["values"] = sheet_names
            if sheet_names:
                self.combo_b.current(0)  # 默认选中第一个
                self._on_combo_b_select()  # 触发选中事件

    def _on_combo_b_select(self, event=None):
        """当下拉框的值变化时触发的事件"""

        selected_value = self.combo_b.get()  # 获取当前选中的值
        print(f"选中的值: {selected_value}")
        self.part_b_conn = load_excel_to_table(self.table_b_file_path, selected_value, "part_b")
        table_cols = self.get_table_cols_from_db_conn(self.part_b_conn, "part_b")
        self.lbl_b.config(text=f"{selected_value} 共有 {len(table_cols)}列")

        if len(self.combo_a.get()):
            print("甲方表已经加载，可以开始对账")
            for col in table_cols:
                self.group1.insert(tk.END, col)
                self.group2.insert(tk.END, col)
                self.group3.insert(tk.END, col)
        else:
            print("甲方表未加载，无法开始对账")

    def _create_file_loader(self):
        """创建文件加载区域组件"""
        frame = ttk.LabelFrame(self, text="文件加载", padding=(10, 10))
        frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=10)

        # 甲方文件加载控件
        btn_a = ttk.Button(frame, text="加载甲方表", command=self._load_file_a)
        btn_a.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.combo_a = ttk.Combobox(frame, state="readonly")
        self.combo_a.bind("<<ComboboxSelected>>", self._on_combo_a_select)
        self.combo_a.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        self.lbl_a = ttk.Label(frame, text="甲方表的基本统计信息", relief="sunken", anchor=tk.W)
        self.lbl_a.grid(row=0, column=2, padx=5, pady=10, sticky=tk.EW)

        # 乙方加载控件
        btn_b = ttk.Button(frame, text="加载乙方表", command=self._load_file_b)
        btn_b.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.combo_b = ttk.Combobox(frame, state="readonly")
        self.combo_b.bind("<<ComboboxSelected>>", self._on_combo_b_select)
        self.combo_b.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        self.lbl_b = ttk.Label(frame, text="乙方表的基本统计信息", relief="sunken", anchor=tk.W)
        self.lbl_b.grid(row=1, column=2, padx=5, pady=10, sticky=tk.EW)

    def _create_group_conditions(self):
        """创建分组条件区域组件"""
        frame = ttk.LabelFrame(self, text="分组条件", padding=(10, 10))
        frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)

        # 配置框架内部网格
        for col in range(3):
            frame.columnconfigure(col, weight=1)
        frame.columnconfigure(3, weight=0)
        frame.rowconfigure(0, weight=1)

        # 创建三个分组列表框
        self.group1 = self._create_group_box(frame, "分组一", 0)
        self.group2 = self._create_group_box(frame, "分组二", 1)
        self.group3 = self._create_group_box(frame, "分组三", 2)

        # 创建开始对账按钮
        btn = ttk.Button(frame, text="开始对账")
        btn.grid(row=0, column=3, padx=5, pady=5, sticky=tk.NS)

    def _create_group_box(self, parent, title, column):
        """创建单个分组条件组件"""
        subframe = ttk.Frame(parent)
        subframe.grid(row=0, column=column, padx=5, pady=5, sticky=tk.NSEW)

        ttk.Label(subframe, text=title).pack(pady=2)

        lb = tk.Listbox(subframe, width=18, height=6)  # 保留原始Listbox，因为ttk没有Listbox组件
        lb.pack(expand=True, fill=tk.BOTH)
        return lb

    def _create_result_display(self):
        """创建对账结果显示区域"""
        frame = ttk.LabelFrame(self, text="对账结果", padding=(10, 10))
        frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)

        text = tk.Text(frame, wrap=tk.WORD)  # 保留原始Text，因为ttk没有Text组件
        scrollbar = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        text.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS + tk.E)

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)


if __name__ == "__main__":
    app = App()  # 创建应用实例
    app.mainloop()  # 启动主事件循环
