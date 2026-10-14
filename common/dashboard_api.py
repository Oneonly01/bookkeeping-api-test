class DashboardApi:
    """封装首页汇总接口。"""

    def __init__(self, client, api_prefix):
        # 保存已认证客户端并构造首页汇总地址。
        self.client = client
        self.url = f"{api_prefix.rstrip('/')}/dashboard/summary/"

    def get_summary(self):
        """GET /api/v1/dashboard/summary/"""

        # 查询当前用户的首页数据。
        return self.client.get(self.url)
