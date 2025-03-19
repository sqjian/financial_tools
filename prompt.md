```python
import pandas as pd
from datetime import datetime

def match_and_format_data(part_a, part_b):
    """
    匹配两部分数据并格式化输出为表格
    
    参数:
    part_a: 包含 date 和 numbers 的字典
    part_b: 包含 date 和 numbers 的字典
    
    返回:
    pandas DataFrame: 按照要求格式化的结果表格
    """
    # 将输入数据转换为DataFrame
    df_a = pd.DataFrame(part_a)
    df_b = pd.DataFrame(part_b)
    
    # 转换日期字符串为日期对象以便比较
    df_a['date'] = pd.to_datetime(df_a['date'])
    df_b['date'] = pd.to_datetime(df_b['date'])
    
    # 为原始索引创建列
    df_a['a_idx'] = df_a.index
    df_b['b_idx'] = df_b.index
    
    # 创建所有可能的匹配对
    matches = []
    
    for i, row_a in df_a.iterrows():
        for j, row_b in df_b.iterrows():
            # 检查日期条件: part_a.date >= part_b.date
            if row_a['date'] >= row_b['date']:
                # 检查数字是否匹配
                if row_a['numbers'] == row_b['numbers']:
                    matches.append({
                        'a_idx': i,
                        'b_idx': j,
                        'a_date': row_a['date'],
                        'b_date': row_b['date'],
                        'is_match': True
                    })
    
    # 如果没有匹配，创建空结果
    if not matches:
        result = pd.DataFrame(columns=['part_a.date', 'part_a.numbers', 'part_b.date', 'part_b.numbers'])
        # 按照日期约束创建未匹配的行
        unmatched_rows = []
        for i, row_a in df_a.iterrows():
            closest_b = None
            min_date_diff = float('inf')
            
            for j, row_b in df_b.iterrows():
                if row_a['date'] >= row_b['date']:
                    date_diff = (row_a['date'] - row_b['date']).total_seconds()
                    if date_diff < min_date_diff:
                        min_date_diff = date_diff
                        closest_b = row_b
            
            if closest_b is not None:
                unmatched_rows.append({
                    'part_a.date': row_a['date'],
                    'part_a.numbers': row_a['numbers'],
                    'part_b.date': closest_b['date'],
                    'part_b.numbers': closest_b['numbers']
                })
            else:
                unmatched_rows.append({
                    'part_a.date': row_a['date'],
                    'part_a.numbers': row_a['numbers'],
                    'part_b.date': None,
                    'part_b.numbers': None
                })
        
        # 使用 concat 代替 append
        if unmatched_rows:
            result = pd.concat([result, pd.DataFrame(unmatched_rows)], ignore_index=True)
        
        # 排序并返回结果
        result = result.sort_values(['part_b.date', 'part_a.date'], na_position='last')
        return result
    
    # 创建匹配图
    match_graph = {}
    for match in matches:
        a_idx = match['a_idx']
        b_idx = match['b_idx']
        if a_idx not in match_graph:
            match_graph[a_idx] = []
        match_graph[a_idx].append(b_idx)
    
    # 使用贪心算法查找最大匹配数
    used_b = set()
    matches_found = []
    
    # 按日期排序处理 part_a
    for a_idx in sorted(match_graph.keys(), key=lambda x: df_a.loc[x, 'date']):
        # 按日期排序潜在匹配
        potential_matches = sorted(match_graph[a_idx], key=lambda x: df_b.loc[x, 'date'])
        
        for b_idx in potential_matches:
            if b_idx not in used_b:
                matches_found.append((a_idx, b_idx))
                used_b.add(b_idx)
                break
    
    # 创建结果表格的行
    result_rows = []
    
    # 添加匹配的行
    for a_idx, b_idx in matches_found:
        result_rows.append({
            'part_a.date': df_a.loc[a_idx, 'date'],
            'part_a.numbers': df_a.loc[a_idx, 'numbers'],
            'part_b.date': df_b.loc[b_idx, 'date'],
            'part_b.numbers': df_b.loc[b_idx, 'numbers'],
            # 添加排序辅助列
            'sort_date': df_b.loc[b_idx, 'date']  # 使用 part_b 的日期进行排序
        })
    
    # 添加未匹配的 part_a 行
    matched_a = {a for a, b in matches_found}
    for i, row in df_a.iterrows():
        if i not in matched_a:
            # 查找日期最接近的 part_b
            closest_b = None
            min_date_diff = float('inf')
            
            for j, row_b in df_b.iterrows():
                if j not in used_b and row['date'] >= row_b['date']:
                    date_diff = (row['date'] - row_b['date']).total_seconds()
                    if date_diff < min_date_diff:
                        min_date_diff = date_diff
                        closest_b = j
            
            if closest_b is not None:
                result_rows.append({
                    'part_a.date': row['date'],
                    'part_a.numbers': row['numbers'],
                    'part_b.date': df_b.loc[closest_b, 'date'],
                    'part_b.numbers': df_b.loc[closest_b, 'numbers'],
                    'sort_date': df_b.loc[closest_b, 'date']  # 使用 part_b 的日期进行排序
                })
                used_b.add(closest_b)
            else:
                result_rows.append({
                    'part_a.date': row['date'],
                    'part_a.numbers': row['numbers'],
                    'part_b.date': None,
                    'part_b.numbers': None,
                    'sort_date': row['date']  # 如果没有 part_b，则使用 part_a 日期排序
                })
    
    # 添加未匹配的 part_b 行
    for i, row in df_b.iterrows():
        if i not in used_b:
            # 查找日期最接近的 part_a
            closest_a = None
            min_date_diff = float('inf')
            
            for j, row_a in df_a.iterrows():
                if j not in matched_a and row_a['date'] >= row['date']:
                    date_diff = (row_a['date'] - row['date']).total_seconds()
                    if date_diff < min_date_diff:
                        min_date_diff = date_diff
                        closest_a = j
            
            if closest_a is not None:
                result_rows.append({
                    'part_a.date': df_a.loc[closest_a, 'date'],
                    'part_a.numbers': df_a.loc[closest_a,'numbers'],
                    'part_b.date': row['date'],
                    'part_b.numbers': row['numbers'],
                    'sort_date': row['date']  # 使用 part_b 的日期进行排序
                })
                matched_a.add(closest_a)
            else:
                result_rows.append({
                    'part_a.date': None,
                    'part_a.numbers': None,
                    'part_b.date': row['date'],
                    'part_b.numbers': row['numbers'],
                    'sort_date': row['date']  # 使用 part_b 的日期进行排序
                })
    
    # 创建结果DataFrame
    result = pd.DataFrame(result_rows)
    
    # 首先按照排序日期列排序
    result = result.sort_values('sort_date', na_position='last')
    
    # 删除排序辅助列
    if 'sort_date' in result.columns:
        result = result.drop(columns=['sort_date'])
    
    return result

# 示例使用
if __name__ == "__main__":
    part_a={
        "date":["2024-11-13","2024-11-22","2024-12-06","2024-12-07","2024-12-20","2024-12-22","2024-12-29","2024-12-31"],
        "numbers":[797,453,150,250,210,130,60,120]
        }
    part_b={
        "date":["2024/10/31","2024/11/20","2024/11/21","2024/12/4","2024/12/6","2024/12/19","2024/12/21","2024/12/28","2024/12/29",],
        "numbers":[800,450,3,150,250,210,130,60,120]
        }
    
    result = match_and_format_data(part_a, part_b)
    print(result)
```

## 上面这段代码做了如下功能：

1、输入数据为 part_a、part_b，结构为：

```python
part_a={
    "date":["data1","data2","data3"],
    "numbers":[number1,number2,number3]
    }
part_b={
    "date":["data1","data2","data3"],
    "numbers":[number2,number3，number4]
    }
```

2、求两个数据的最佳匹配，匹配规则如下：
- 求 part_a、part_b 中 numbers 完全匹配的个数最多有多少，限制条件为 part_a 中的 number 对应的 date 需要大于等于 part_b 中的 date

3、输出格式如下：
- 输出为表格，有四列（part_a.date, part_a,numbers,part_b,date,part_b.numbers），把匹配成功的放在一行
- 匹配失败的按日期插入在匹配成功的前面或后面，把日期相近的放在一行，要求即 part_a.date > part_b.date
- 输出的表格整体按日期排序

## 问题：
下面是输出结果，可以看到 part_a.numbers 里出现了两次 453，这肯定是不对的

  part_a.date  part_a.numbers part_b.date  part_b.numbers
6  2024-11-13             797  2024-10-31             800
8  2024-11-22             453  2024-11-20             450
7  2024-11-22             453  2024-11-21               3
0  2024-12-06             150  2024-12-04             150
1  2024-12-07             250  2024-12-06             250
2  2024-12-20             210  2024-12-19             210
3  2024-12-22             130  2024-12-21             130
4  2024-12-29              60  2024-12-28              60
5  2024-12-31             120  2024-12-29             120
