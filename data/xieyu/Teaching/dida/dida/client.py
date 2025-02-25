from .api.tasksv2 import TaskAPIV2  # 确保导入 TaskAPIV2

class DidaClient:
    def __init__(self, email=None, password=None, token=None):
        # 其他初始化代码...
        self.email = email
        self.password = password
        self.token = token
        
        # 实例化 TaskAPIV2
        self.tasksv2 = TaskAPIV2(self)

    # 其他方法... 