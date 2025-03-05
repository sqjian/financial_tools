from typing import List
import pandas as pd


def get_excel_cols(file_path: str, sheet_name: str) -> List[str]:
    """
    分析Excel文件并返回其工作簿非空列的名称列表

    Args:
        file_path (str): Excel文件的完整路径，支持.xlsx或.xls格式
        sheet_name (str): Excel文件的工作簿名称

    Returns:
        columns (List[str]):工作簿内非空列的名称

    Raises:
        FileNotFoundError: 当指定的Excel文件不存在时
        Exception: 当读取Excel文件时发生其他错误
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # 获取所有列名
        all_columns = df.columns.tolist()

        # 筛选非空列
        non_empty_columns = []
        for col in all_columns:
            # 检查列是否全为空值（NaN）
            if not df[col].isna().all():
                non_empty_columns.append(col)

        return non_empty_columns

    except FileNotFoundError:
        raise FileNotFoundError(f"Excel文件 '{file_path}' 不存在")
    except Exception as e:
        raise Exception(f"读取Excel文件时发生错误: {str(e)}")


# 使用示例
if __name__ == "__main__":
    result = get_excel_cols("./../testdata/测试表.xlsx", "原始表")

    print(result)
