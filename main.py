from source.reconcile_accounts import reconcile_accounts

# 使用示例
if __name__ == "__main__":
    rst=reconcile_accounts(
        file_path="testdata/测试表.xlsx",
        col_a_name="应付增减",
        col_b_name="金额",
        sheet_name="原始表",
    )

    print("---")
    print(rst)
