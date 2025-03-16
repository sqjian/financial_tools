def get_group_conditions(conn, table_name, group1_col, group2_col, group3_col):
    return {
        "group1_col": conn.execute(f"SELECT {group1_col} FROM {table_name}").fetchdf()[group1_col].drop_duplicates().to_list(),
        "group2_col": conn.execute(f"SELECT {group2_col} FROM {table_name}").fetchdf()[group2_col].drop_duplicates().to_list(),
        "group3_col": conn.execute(f"SELECT {group3_col} FROM {table_name}").fetchdf()[group3_col].drop_duplicates().to_list(),
    }
