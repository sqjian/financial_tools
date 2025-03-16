import pandas as pd
from collections import defaultdict


def reconcile_accounts(file_path, col_a_name, col_b_name, sheet_name=0):
    output = []  # 用于收集输出内容的列表

    try:
        # 读取Excel文件
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        output.append(f"成功读取文件: {file_path}")

        # 校验必要列
        if not all(col in df.columns for col in [col_a_name, col_b_name]):
            raise ValueError(f"Excel文件必须包含'{col_a_name}'和'{col_b_name}'列")

        # 预处理数据并保留行号信息
        def preprocess_column(col_name):
            data = []
            for idx, value in df[col_name].items():
                if pd.notnull(value):
                    try:
                        amount = round(float(value) * 100)
                        data.append(
                            {"amount": amount, "row": idx + 2}
                        )  # +2因为Excel行号从1开始，索引从0开始
                    except:
                        pass
            return data

        col_a = preprocess_column(col_a_name)
        col_b = preprocess_column(col_b_name)
        output.append(f"预处理完成 | A列({col_a_name})记录数: {len(col_a)} | B列({col_b_name})记录数: {len(col_b)}")

        # 阶段1：精确匹配
        a_amount_map = defaultdict(list)
        for item in col_a:
            a_amount_map[item["amount"]].append(item)

        b_amount_map = defaultdict(list)
        for item in col_b:
            b_amount_map[item["amount"]].append(item)

        exact_matches = []
        used_a = set()
        used_b = set()

        # 处理精确匹配
        for amount in list(a_amount_map.keys()):
            if amount in b_amount_map:
                a_items = a_amount_map[amount]
                b_items = b_amount_map[amount]
                match_count = min(len(a_items), len(b_items))

                for i in range(match_count):
                    a_row = a_items[i]["row"]
                    b_row = b_items[i]["row"]
                    exact_matches.append(
                        {
                            "type": "exact",
                            "a_rows": [a_row],
                            "b_row": b_row,
                            "amount": a_items[i]["amount"] / 100,
                        }
                    )
                    used_a.add((amount, a_row))
                    used_b.add((amount, b_row))

        # 获取剩余未匹配项
        remaining_a = [
            item for item in col_a if (item["amount"], item["row"]) not in used_a
        ]
        remaining_b = [
            item for item in col_b if (item["amount"], item["row"]) not in used_b
        ]

        # 阶段2：组合匹配
        combo_matches = []
        a_available = remaining_a.copy()

        def find_combination(target, available, path, start):
            if sum(x["amount"] for x in path) == target:
                return path
            if sum(x["amount"] for x in path) > target:
                return None

            for i in range(start, len(available)):
                result = find_combination(
                    target, available, path + [available[i]], i + 1
                )
                if result:
                    return result
            return None

        # 按金额降序处理B列剩余项
        remaining_b_sorted = sorted(remaining_b, key=lambda x: -x["amount"])
        for b_item in remaining_b_sorted:
            combination = find_combination(b_item["amount"], a_available, [], 0)
            if combination:
                combo_matches.append(
                    {
                        "type": "combo",
                        "a_rows": [x["row"] for x in combination],
                        "b_row": b_item["row"],
                        "amount": b_item["amount"] / 100,
                    }
                )
                # 移除已使用的A列项
                for item in combination:
                    a_available.remove(item)
                # 标记B项为已匹配
                remaining_b.remove(b_item)

        # 收集最终结果
        unmatched_a = a_available
        unmatched_b = remaining_b

        # 构建结果字符串
        output.append("\n=== 匹配明细 ===")
        exact_count = len(exact_matches)
        output.append(f"精确匹配数量: {exact_count}笔")
        for match in combo_matches:
            output.append(
                f"组合匹配 | {col_a_name}=>行号: {match['a_rows']} | {col_b_name}=>行号: {match['b_row']} | 总金额: {match['amount']:.2f}"
            )

        output.append("\n=== 未匹配明细 ===")
        # 处理A列未匹配项
        output.append("A列未匹配项：")
        for item in unmatched_a:
            row_num = item["row"]
            row_idx = row_num - 2  # 转换为pandas索引
            if row_idx < 0 or row_idx >= len(df):
                output.append(f"行号 {row_num} 超出数据范围")
                continue
            row_data = df.iloc[row_idx]
            non_empty = {col: val for col, val in row_data.items() if pd.notnull(val)}
            details = ", ".join([f"{col}: {val}" for col, val in non_empty.items()])
            output.append(f"行号: {row_num} | {details}")

        # 处理B列未匹配项
        output.append("\nB列未匹配项：")
        for item in unmatched_b:
            row_num = item["row"]
            row_idx = row_num - 2
            if row_idx < 0 or row_idx >= len(df):
                output.append(f"行号 {row_num} 超出数据范围")
                continue
            row_data = df.iloc[row_idx]
            non_empty = {col: val for col, val in row_data.items() if pd.notnull(val)}
            details = ", ".join([f"{col}: {val}" for col, val in non_empty.items()])
            output.append(f"行号: {row_num} | {details}")

        return "\n".join(output)

    except Exception as e:
        output.append(f"错误: {str(e)}")
        return "\n".join(output)