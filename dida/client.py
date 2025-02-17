"""
滴答清单SDK主客户端
"""
from typing import Optional
from .api import TaskAPI, ProjectAPI, TagAPI
from .utils.auth import TokenManager
from .exceptions import ConfigurationError

class DidaClient:
    """
    滴答清单SDK的主客户端类
    
    使用方式:
    1. 使用邮箱密码初始化，自动获取token:
        client = DidaClient(email="your_email", password="your_password")
        token = client.token  # 获取token以便后续使用
        
    2. 使用已有token初始化（推荐，避免多次登录）:
        client = DidaClient(token="your_token")
    """
    
    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None
    ):
        """
        初始化客户端
        
        Args:
            email: 用户邮箱
            password: 用户密码
            token: 访问令牌。如果提供了token，将优先使用token而不是邮箱密码
            
        Raises:
            ConfigurationError: 当既没有提供有效的token，也没有提供正确的邮箱密码组合时
        """
        # 初始化Token管理器
        self._token_manager = TokenManager(token)
        
        # 如果没有token，尝试使用邮箱密码登录获取token
        if not token and email and password:
            self._token_manager.login(email, password)
            
        # 验证是否有可用的token
        if not self._token_manager.is_valid():
            raise ConfigurationError(
                "请提供有效的token或email/password组合"
            )
            
        # 初始化API模块
        self._init_apis()
    
    def _init_apis(self):
        """初始化API模块"""
        self.tasks = TaskAPI(self._token_manager.token)
        self.projects = ProjectAPI(self._token_manager.token)
        self.tags = TagAPI(self._token_manager.token)
    
    @property
    def token(self) -> str:
        """
        获取当前的访问令牌
        
        Returns:
            str: 当前有效的访问令牌。可以保存这个token，下次直接使用token初始化客户端
        """
        return self._token_manager.token
    
    def login(self, email: str, password: str):
        """
        使用邮箱和密码登录，获取新的token
        
        Args:
            email: 用户邮箱
            password: 用户密码
            
        注意：
            登录成功后会自动更新客户端使用的token
        """
        self._token_manager.login(email, password)
        self._init_apis()
    
    def set_token(self, token: str):
        """
        设置新的访问令牌
        
        Args:
            token: 访问令牌
            
        注意：
            设置新token后会自动更新所有API模块使用的token
        """
        self._token_manager.token = token
        self._init_apis() 