class PreferenceApi:
    """封装当前用户偏好设置接口。"""

    def __init__(self, client, api_prefix):
        # 保存已认证客户端并构造偏好接口地址。
        self.client = client
        self.url = f"{api_prefix.rstrip('/')}/preferences/"

    def get_preference(self):
        """GET /api/v1/preferences/"""

        # 查询当前用户偏好。
        return self.client.get(self.url)

    def update_preference(self, payload):
        """PUT /api/v1/preferences/"""

        # 提交需要修改的偏好字段。
        return self.client.put(self.url, json=payload)
