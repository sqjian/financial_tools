import tkinter as tk  # 导入tkinter模块，用于创建GUI应用程序


class App(tk.Tk):
    """主应用程序类，继承自tk.Tk"""

    def __init__(self):
        """初始化应用程序窗口"""
        super().__init__()  # 调用父类构造函数
        self.title("对账工具")  # 设置窗口标题
        self.geometry("800x500")  # 设置初始窗口尺寸
        self._configure_grid()  # 配置网格布局管理器
        self._create_widgets()  # 创建所有界面组件

    def _configure_grid(self):
        """配置网格布局行列权重，实现响应式布局"""
        # 列配置（左侧按钮列:右侧内容区域 = 1:4）
        self.columnconfigure(0, weight=1)  # 左侧列（按钮区）
        self.columnconfigure(1, weight=10)  # 右侧列（内容显示区）

        # 行配置（结果区域需要更多空间）
        self.rowconfigure(2, weight=1)  # 分组条件区域
        self.rowconfigure(3, weight=3)  # 结果显示区域（分配更多权重）

    def _create_widgets(self):
        """创建所有界面组件"""
        self._create_file_loader()  # 创建文件加载区域
        self._create_group_conditions()  # 创建分组条件区域
        self._create_result_display()  # 创建结果显示区域

    def _create_file_loader(self):
        """创建文件加载区域组件"""
        # 甲方文件加载控件
        btn_a = tk.Button(self, text="加载甲方表", width=15)  # 加载按钮
        btn_a.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)  # 左侧对齐

        # 甲方文件信息标签（凹陷样式，左对齐文本）
        lbl_a = tk.Label(self, text="甲方表的基本统计信息", relief=tk.SUNKEN, anchor=tk.W)
        lbl_a.grid(row=0, column=1, padx=5, pady=10, sticky=tk.EW)  # 横向拉伸填充

        # 乙方文件加载控件（布局同上）
        btn_b = tk.Button(self, text="加载乙方表", width=15)
        btn_b.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        lbl_b = tk.Label(self, text="乙方表的基本统计信息", relief=tk.SUNKEN, anchor=tk.W)
        lbl_b.grid(row=1, column=1, padx=5, pady=10, sticky=tk.EW)

    def _create_group_conditions(self):
        """创建分组条件区域组件"""
        # 创建分组框架容器（带标题）
        frame = tk.LabelFrame(self, text="分组条件", padx=10, pady=10)
        frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)  # 跨两列  # 四向拉伸

        # 配置框架内部网格（前三列平均分配，第四列固定宽度）
        for col in range(3):
            frame.columnconfigure(col, weight=1)  # 前3列平均分配空间
        frame.columnconfigure(3, weight=0)  # 按钮列不扩展
        frame.rowconfigure(0, weight=1)  # 单行布局

        # 创建三个分组列表框（横向排列）
        self.group1 = self._create_group_box(frame, "分组一", 0)
        self.group2 = self._create_group_box(frame, "分组二", 1)
        self.group3 = self._create_group_box(frame, "分组三", 2)

        # 创建开始对账按钮（垂直居中）
        btn = tk.Button(frame, text="开始对账", width=12)
        btn.grid(row=0, column=3, padx=5, pady=5, sticky=tk.NS)  # 垂直拉伸对齐

    def _create_group_box(self, parent, title, column):
        """创建单个分组条件组件"""
        # 创建子容器框架
        subframe = tk.Frame(parent)
        subframe.grid(row=0, column=column, padx=5, pady=5, sticky=tk.NSEW)

        # 分组标题标签
        tk.Label(subframe, text=title).pack(pady=2)  # 顶部留白

        # 创建列表框（用于显示/选择分组字段）
        lb = tk.Listbox(subframe, width=18, height=6)  # 固定尺寸
        lb.pack(expand=True, fill=tk.BOTH)  # 填充可用空间
        return lb  # 返回列表框引用，供后续操作

    def _create_result_display(self):
        """创建对账结果显示区域"""
        # 创建带标题的结果框架
        frame = tk.LabelFrame(self, text="对账结果", padx=10, pady=10)
        frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)  # 跨两列  # 四向拉伸

        # 创建文本框（用于显示详细结果）
        text = tk.Text(frame, wrap=tk.WORD)  # 自动换行
        scrollbar = tk.Scrollbar(frame, command=text.yview)  # 垂直滚动条
        text.configure(yscrollcommand=scrollbar.set)  # 绑定滚动事件

        # 布局组件
        text.grid(row=0, column=0, sticky=tk.NSEW)  # 文本框四向拉伸
        scrollbar.grid(row=0, column=1, sticky=tk.NS + tk.E)  # 右侧垂直滚动条

        # 配置框架内部布局权重
        frame.columnconfigure(0, weight=1)  # 文本框列扩展
        frame.rowconfigure(0, weight=1)  # 单行布局


if __name__ == "__main__":
    app = App()  # 创建应用实例
    app.mainloop()  # 启动主事件循环
