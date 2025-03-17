import rich
from collections import defaultdict, Counter
import heapq


def reconcile_lists(list_a, list_b):
    """实现数值对账功能，包含精确匹配和双向组合匹配

    Args:
        list_a: 数值列表A (e.g. [10.0, 20.0, 30.0])
        list_b: 数值列表B (e.g. [15.0, 25.0, 35.0])

    Returns:
        匹配结果字典
    """
    EPSILON = 1e-7

    # 使用Counter直接计数，比defaultdict更高效
    a_counter = Counter(list_a)
    b_counter = Counter(list_b)

    # 处理精确匹配
    exact_matches = {}
    common_nums = set(a_counter) & set(b_counter)
    for num in common_nums:
        match_count = min(a_counter[num], b_counter[num])
        if match_count > 0:
            exact_matches[num] = match_count
            a_counter[num] -= match_count
            b_counter[num] -= match_count

    # 只保留计数大于0的项
    a_counter = {k: v for k, v in a_counter.items() if v > 0}
    b_counter = {k: v for k, v in b_counter.items() if v > 0}

    # 生成剩余数值列表，直接使用列表推导式
    remaining_a = [num for num, count in a_counter.items() for _ in range(count)]
    remaining_b = [num for num, count in b_counter.items() for _ in range(count)]

    # 优化的组合查找函数，使用动态规划思想
    def find_combination_dp(candidates, target):
        """使用动态规划查找和为target的组合"""
        if not candidates or abs(target) < EPSILON:
            return [] if abs(target) < EPSILON else None

        # 提前终止条件：如果所有数的总和小于目标值，或最大值大于目标值
        total_sum = sum(candidates)
        if total_sum < target - EPSILON or max(candidates) > target + EPSILON:
            return None

        # 按降序排序，有助于更快找到解
        candidates.sort(reverse=True)

        # 使用记忆化存储已计算的结果
        memo = {}

        def dp(i, remaining):
            if abs(remaining) < EPSILON:
                return []
            if i >= len(candidates) or remaining < 0 - EPSILON:
                return None

            key = (i, round(remaining, 7))  # 使用有限精度作为键
            if key in memo:
                return memo[key]

            # 不选当前元素
            skip = dp(i + 1, remaining)

            # 选当前元素
            take = None
            if candidates[i] <= remaining + EPSILON:
                rest = dp(i + 1, remaining - candidates[i])
                if rest is not None:
                    take = [candidates[i]] + rest

            # 返回长度较小的那个非None结果
            result = None
            if take is not None and skip is not None:
                result = take if len(take) <= len(skip) else skip
            else:
                result = take if take is not None else skip

            memo[key] = result
            return result

        return dp(0, target)

    # 组合匹配结果
    combo_a_to_b = []
    combo_b_to_a = []

    # 复制列表用于组合匹配，并排序以提高效率
    temp_a = sorted(remaining_a, reverse=True)
    temp_b = sorted(remaining_b, reverse=True)

    # 创建值到索引的映射，加速后续删除操作
    a_indices = {v: i for i, v in enumerate(temp_a)}
    b_indices = {v: i for i, v in enumerate(temp_b)}

    # 1. 处理 A 到 B 的组合匹配 - 优先处理大额
    for b_val in sorted(set(temp_b), reverse=True):
        # 只处理每个唯一值一次，而不是重复处理
        if b_val not in b_indices:
            continue

        b_idx = b_indices[b_val]
        current_a = [a for a in temp_a]  # 当前可用的A值

        combination = find_combination_dp(current_a, b_val)
        if combination:
            combo_a_to_b.append({"b": b_val, "a": combination})

            # 移除已匹配的值
            del temp_b[b_idx]
            b_indices = {v: i for i, v in enumerate(temp_b)}  # 更新索引

            for a_val in combination:
                a_idx = temp_a.index(a_val)  # 找到要删除的值的索引
                del temp_a[a_idx]

            # 更新A的索引映射
            a_indices = {v: i for i, v in enumerate(temp_a)}

    # 2. 处理 B 到 A 的组合匹配
    for a_val in sorted(set(temp_a), reverse=True):
        if a_val not in a_indices:
            continue

        a_idx = a_indices[a_val]
        current_b = [b for b in temp_b]

        combination = find_combination_dp(current_b, a_val)
        if combination:
            combo_b_to_a.append({"a": a_val, "b": combination})

            # 移除已匹配的值
            del temp_a[a_idx]
            a_indices = {v: i for i, v in enumerate(temp_a)}

            for b_val in combination:
                b_idx = temp_b.index(b_val)
                del temp_b[b_idx]

            # 更新B的索引映射
            b_indices = {v: i for i, v in enumerate(temp_b)}

    return {"exact_matches": exact_matches, "combo_matches_a_to_b": combo_a_to_b, "combo_matches_b_to_a": combo_b_to_a, "unmatched_a": temp_a, "unmatched_b": temp_b}


# 示例测试
if __name__ == "__main__":
    # 测试案例1: 基础场景
    list_a = [20.0, 30.0, 50.0, 50.0]
    list_b = [10.0, 20.0, 30.0, 40.0]
    result = reconcile_lists(list_a, list_b)
    rich.print(result)

    # 测试案例2: 包含重复值
    list_a = [30.0, 15.0, 30.0, 15.0]
    list_b = [15.0, 15.0, 30.0, 9.99, 5.01]
    result = reconcile_lists(list_a, list_b)
    rich.print(result)

    # 测试案例3: 双向匹配
    list_a = [20.0, 30.0, 50.0, 50.0, 15, 2]
    list_b = [10.0, 20.0, 30.0, 40.0, 65]
    result = reconcile_lists(list_a, list_b)
    rich.print(result)

    # 测试案例4: 一边完全为空
    list_a = [10.0, 20.0, 30.0, 40.0, 65]
    list_b = []
    result = reconcile_lists(list_a, list_b)
    rich.print(result)
