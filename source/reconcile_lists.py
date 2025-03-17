import rich
from collections import Counter

def reconcile_lists(list_a, list_b):
    """实现数值对账功能，包含精确匹配和双向组合匹配，以及多对多匹配

    Args:
        list_a: 数值列表A (e.g. [10.0, 20.0, 30.0])
        list_b: 数值列表B (e.g. [15.0, 25.0, 35.0])

    Returns:
        匹配结果字典
    """
    EPSILON = 1e-7

    # 使用Counter直接计数
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

    # 生成剩余数值列表
    remaining_a = [num for num, count in a_counter.items() for _ in range(count)]
    remaining_b = [num for num, count in b_counter.items() for _ in range(count)]

    # 辅助函数：使用动态规划查找和为target的组合
    def find_combination_dp(candidates, target):
        if not candidates or abs(target) < EPSILON:
            return [] if abs(target) < EPSILON else None

        candidates.sort(reverse=True)
        memo = {}

        def dp(i, remaining):
            if abs(remaining) < EPSILON:
                return []
            if i >= len(candidates) or remaining < 0 - EPSILON:
                return None

            key = (i, round(remaining, 7))
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

    # 新增: 多对多匹配功能
    # 先尝试找到sum(a_subset) == sum(b_subset)的情况
    def find_equal_sum_subsets():
        many_to_many_matches = []

        # 获取所有可能的A列表组合的和值
        a_sums = {}
        for size in range(2, min(5, len(remaining_a) + 1)):  # 限制组合大小以控制复杂度
            for combo in generate_combinations(remaining_a, size):
                combo_sum = sum(combo)
                a_sums.setdefault(combo_sum, []).append(combo)

        # 获取所有可能的B列表组合的和值
        b_sums = {}
        for size in range(2, min(5, len(remaining_b) + 1)):
            for combo in generate_combinations(remaining_b, size):
                combo_sum = sum(combo)
                b_sums.setdefault(combo_sum, []).append(combo)

        # 找到相同的和值
        common_sums = set(a_sums.keys()) & set(b_sums.keys())

        # 处理所有匹配的情况
        for sum_val in sorted(common_sums, reverse=True):
            for a_combo in a_sums[sum_val]:
                for b_combo in b_sums[sum_val]:
                    # 检查这些元素是否还可用（未被匹配）
                    if all(val in remaining_a for val in a_combo) and all(val in remaining_b for val in b_combo):
                        many_to_many_matches.append({"type": "many_to_many", "a_values": a_combo, "b_values": b_combo, "sum": sum_val})

                        # 从剩余列表中移除这些已匹配的元素
                        for val in a_combo:
                            remaining_a.remove(val)
                        for val in b_combo:
                            remaining_b.remove(val)

                        # 一旦找到匹配就处理下一个和值
                        break

                # 如果已经找到匹配，处理下一个和值
                if any(match["sum"] == sum_val for match in many_to_many_matches):
                    break

        return many_to_many_matches

    # 辅助函数：生成列表的所有组合
    def generate_combinations(items, size):
        if size == 0:
            yield []
        elif items:
            # 包含第一个元素的组合
            first = items[0]
            for combo in generate_combinations(items[1:], size - 1):
                yield [first] + combo

            # 不包含第一个元素的组合
            for combo in generate_combinations(items[1:], size):
                yield combo

    # 进行常规的组合匹配
    # 复制列表用于组合匹配
    temp_a = sorted(remaining_a, reverse=True)
    temp_b = sorted(remaining_b, reverse=True)

    # 创建值到索引的映射
    a_indices = {v: i for i, v in enumerate(temp_a)}
    b_indices = {v: i for i, v in enumerate(temp_b)}

    # 组合匹配结果
    combo_a_to_b = []
    combo_b_to_a = []

    # 1. A 到 B 的组合匹配
    for b_val in sorted(set(temp_b), reverse=True):
        if b_val not in b_indices:
            continue

        b_idx = b_indices[b_val]
        current_a = [a for a in temp_a]

        combination = find_combination_dp(current_a, b_val)
        if combination:
            combo_a_to_b.append({"b": b_val, "a": combination})

            # 移除已匹配的值
            del temp_b[b_idx]
            b_indices = {v: i for i, v in enumerate(temp_b)}

            for a_val in combination:
                a_idx = temp_a.index(a_val)
                del temp_a[a_idx]

            # 更新索引映射
            a_indices = {v: i for i, v in enumerate(temp_a)}

    # 2. B 到 A 的组合匹配
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

            # 更新索引映射
            b_indices = {v: i for i, v in enumerate(temp_b)}

    # 最后进行多对多匹配，优先级最低
    # 注意：我们需要使用temp_a和temp_b，因为这些是经过前面的匹配后剩余的元素
    remaining_a = temp_a
    remaining_b = temp_b
    many_to_many_matches = find_equal_sum_subsets()

    return {
        "exact_matches": exact_matches,
        "combo_matches_a_to_b": combo_a_to_b,
        "combo_matches_b_to_a": combo_b_to_a,
        "many_to_many_matches": many_to_many_matches,
        "unmatched_a": remaining_a,
        "unmatched_b": remaining_b,
    }


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

    # 测试案例5: 两遍双向匹配
    list_a = [45.0, 65, 1, 2, 3]
    list_b = [105, 1, 5, 5]
    result = reconcile_lists(list_a, list_b)
    rich.print(result)
