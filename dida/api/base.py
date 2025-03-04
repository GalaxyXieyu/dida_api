"""
基础API类
"""
from typing import Dict, Any, Optional
from ..utils.http import HttpClient
from datetime import datetime
import pytz

class BaseAPI:
    """所有API的基类"""
    
    def __init__(self, token: str):
        """
        初始化API实例
        
        Args:
            token: API访问令牌
        """
        self.token = token
        self.http = HttpClient(token)
    
    def _convert_date_format(self, date_str: Optional[str] = None, date_obj: Optional[datetime] = None) -> Optional[str]:
        """
        统一转换日期格式
        
        支持两种输入:
        1. 字符串格式 (YYYY-MM-DD HH:MM:SS)
        2. datetime对象
        
        返回格式: YYYY-MM-DDThh:mm:ss.000+0000
        
        Args:
            date_str: 日期字符串，格式为 "YYYY-MM-DD HH:MM:SS"
            date_obj: datetime对象
            
        Returns:
            str: 转换后的日期字符串
        """
        try:
            if date_str:
                # 解析输入的日期字符串
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            elif date_obj:
                dt = date_obj
            else:
                return None
                
            # 确保日期对象有时区信息
            if dt.tzinfo is None:
                local_tz = pytz.timezone('Asia/Shanghai')
                dt = local_tz.localize(dt)
            
            # 转换为UTC时间
            utc_dt = dt.astimezone(pytz.UTC)
            
            # 返回指定格式
            return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000+0000")
        except Exception as e:
            print(f"日期转换错误: {str(e)}")
            return None
    
    def _handle_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理API响应
        
        Args:
            response: API响应数据
            
        Returns:
            Dict: 处理后的响应数据
        """
        return response
    
    def _get(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送GET请求
        
        Args:
            endpoint: API端点
            params: 查询参数
            
        Returns:
            Dict: 响应数据
        """
        response = self.http.get(endpoint, params)
        return self._handle_response(response)
    
    def _post(
        self, 
        endpoint: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        发送POST请求
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            Dict: 响应数据
        """
        response = self.http.post(endpoint, data)
        return self._handle_response(response)
    
    def _put(
        self, 
        endpoint: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        发送PUT请求
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            Dict: 响应数据
        """
        response = self.http.put(endpoint, data)
        return self._handle_response(response)
    
    def _delete(self, endpoint: str) -> bool:
        """
        发送DELETE请求
        
        Args:
            endpoint: API端点
            
        Returns:
            bool: 是否删除成功
        """
        return self.http.delete(endpoint) 