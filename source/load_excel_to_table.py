import duckdb


def load_excel_to_table(file_path, sheet_name, table_name):
    # 初始化内存数据库连接
    conn = duckdb.connect(":memory:")

    # 使用 f-string 动态构建 SQL 查询
    query = f"""
    CREATE OR REPLACE TABLE {table_name} AS
    SELECT 
        *
    FROM
        read_xlsx('{file_path}', sheet = '{sheet_name}');
    """

    # 执行 SQL 查询
    conn.sql(query.strip())

    # 返回连接对象以便后续操作
    return conn