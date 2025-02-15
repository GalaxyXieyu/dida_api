"""
基础API类
"""
from typing import Dict, Any, Optional
from ..utils.http import HttpClient

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