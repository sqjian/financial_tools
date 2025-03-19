```sql
select
	*
from
	main.part_a
where
	统一仓库 = '河南新乡仓'
	AND 统一名称 = '徐福记卷心酥香草牛奶味袋装扫码专供@4(6x52g) CN'
	and 统一日期 = '45627.0'
```


```txt
甲方：过滤出单据号
乙方：客户订单号
```

```
统一仓库 -> 统一名称 -> 统一日期 -> 单据号：原因
统一仓库 -> 统一名称 -> 统一日期 -> 单据号：原因
```

```python
import pandas as pd
from datetime import datetime

def match_and_format_data(part_a, part_b):
    """
    1、输入数据为 part_a、part_b，结构为：

    part_a={
        "date":["data1","data2","data3"],
        "numbers":[number1,number2,number3]
        }
    part_b={
        "date":["data1","data2","data3"],
        "numbers":[number2,number3，number4]
        }

    2、求两个数据的最佳匹配，匹配规则如下：
    - 输出为表格，有四列（part_a.date, part_a,numbers,part_b,date,part_b.numbers）
    - 求 part_a、part_b 中 numbers 完全匹配的个数最多有多少，限制条件为：
        - part_a.date >= part_b.date
        - part_a.date 和 part_b.date 为同一年
        - 不可交叉匹配，如part_a.date[0] 与 part_b.date[1] 、part_a.date[1] 与 part_b.date[0] 匹配
    - 匹配失败的按下面要求：
        - 未匹配的数据按日期顺序插入到匹配数据前后，保证匹配的数据能在一行就行
        - part_a.date、part_b.date 各自的原始的顺序保持不变
    """
    pass
```