def get_group_data(conn, table_name, group1_col, group1_col_value, group2_col, group2_col_value, group3_col, group3_col_value, data_col):
    sql = f"SELECT * FROM {table_name} WHERE {group1_col} = '{group1_col_value}' AND {group2_col} = '{group2_col_value}' AND {group3_col} = '{group3_col_value}'"
    rst = conn.execute(sql).fetchdf()
    return rst[data_col].tolist()
