from typing import Dict, List, Optional, Union  
import pandas as pd  

def get_excel_stats(file_path: str) -> Optional[Dict[str, Union[str, int, List[str]]]]:  
    """  
    分析Excel文件并返回其工作表信息。  

    Args:  
        file_path (str): Excel文件的完整路径，支持.xlsx或.xls格式  

    Returns:  
        Optional[Dict[str, Union[str, int, List[str]]]]: 返回包含Excel工作表信息的字典，如果发生错误则返回None  
            返回字典的结构：  
            {  
                "file_path": str,       # Excel文件路径  
                "sheet_count": int,     # 工作表数量  
                "sheet_names": List[str] # 工作表名称列表  
            }  

    Raises:  
        FileNotFoundError: 当指定的Excel文件不存在时  
        Exception: 当读取Excel文件时发生其他错误  

    Examples:  
        >>> result = load_excel_sheets("example.xlsx")  
        >>> if result:  
        >>>     print(f"工作表数量: {result['sheet_count']}")  
        >>>     print(f"工作表名称: {result['sheet_names']}")  
    """  
    try:  
        # 读取Excel文件  
        excel_file = pd.ExcelFile(file_path)  
        
        # 获取所有工作表名称  
        sheet_names = excel_file.sheet_names  
        
        # 创建返回结果  
        result = {  
            "file_path": file_path,  
            "sheet_count": len(sheet_names),  
            "sheet_names": sheet_names  
        }  
        
        return result  
    
    except FileNotFoundError:  
        print(f"错误：文件 '{file_path}' 不存在")  
        return None  
    except Exception as e:  
        print(f"错误：读取Excel文件时发生错误 - {str(e)}")  
        return None  

# 使用示例  
if __name__ == "__main__":  
    excel_path = "./../testdata/测试表.xlsx"  
    result = get_excel_stats(excel_path)  
    
    if result:  
        print(f"Excel文件路径: {result['file_path']}")  
        print(f"工作表数量: {result['sheet_count']}")  
        print("工作表名称列表:")  
        for name in result['sheet_names']:  
            print(f"- {name}")  