"""
滴答清单SDK主客户端
"""
from typing import Optional
from .api import TaskAPI, ProjectAPI, TagAPI
from .utils.auth import TokenManager
from .exceptions import ConfigurationError

class DidaClient:
    """滴答清单SDK的主客户端类"""
    
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
            token: 访问令牌
            
        Raises:
            ConfigurationError: 配置错误
        """
        # 初始化Token管理器
        self._token_manager = TokenManager(token)
        
        # 如果没有token，尝试登录
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
        """获取当前token"""
        return self._token_manager.token
    
    def login(self, email: str, password: str):
        """
        使用邮箱和密码登录
        
        Args:
            email: 用户邮箱
            password: 用户密码
        """
        self._token_manager.login(email, password)
        self._init_apis()
    
    def set_token(self, token: str):
        """
        设置新的token
        
        Args:
            token: 访问令牌
        """
        self._token_manager.token = token
        self._init_apis() 