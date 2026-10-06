class AuthApi:
    """
    用户认证模块接口封装。

    主要作用：

    1. 统一管理认证模块接口地址；
    2. 统一发送认证相关 HTTP 请求；
    3. 避免测试用例中重复拼接 URL；
    4. 让测试用例只关注测试数据和断言。

    当前封装：

    1. 用户登录；
    2. Token 刷新；
    3. 用户退出。

    后续如果增加：

    1. 用户注册；
    2. 找回密码；
    3. 验证码；
    4. 密码重置；

    也可以继续统一放在这里。
    """

    def __init__(
        self,
        client,
        api_prefix: str,
    ):
        """
        初始化认证 API。

        :param client:
            RequestClient 请求对象。

        :param api_prefix:
            API 统一前缀。

            例如：

            /api/v1
        """

        self.client = client

        # 去掉末尾可能存在的 "/"
        # 避免后续 URL 出现 "//"。
        self.api_prefix = api_prefix.rstrip("/")

    # ==========================================
    # 用户登录
    # ==========================================

    def login(
        self,
        payload: dict,
    ):
        """
        用户登录。

        POST /api/v1/auth/login/

        :param payload:
            登录请求参数。

        例如：

        {
            "username": "test001",
            "password": "123456"
        }

        :return:
            requests.Response
        """

        url = f"{self.api_prefix}" "/auth/login/"

        return self.client.post(
            url,
            json=payload,
        )

    # ==========================================
    # Token 刷新
    # ==========================================

    def refresh_token(
        self,
        payload: dict,
    ):
        """
        刷新 Access Token。

        POST /api/v1/auth/refresh/

        具体请求字段以后端实际接口为准。
        """

        url = f"{self.api_prefix}" "/auth/refresh/"

        return self.client.post(
            url,
            json=payload,
        )

    # ==========================================
    # 用户退出
    # ==========================================

    def logout(
        self,
        payload: dict | None = None,
    ):
        """
        用户退出。

        POST /api/v1/auth/logout/

        如果当前退出接口需要 refresh_token，
        可以通过 payload 传入。

        如果接口不需要请求体，
        payload 可以为空。
        """

        url = f"{self.api_prefix}" "/auth/logout/"

        return self.client.post(
            url,
            json=payload,
        )
