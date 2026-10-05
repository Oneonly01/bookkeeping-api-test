import requests


class RequestClient:
    """
    接口请求客户端。

    统一处理：

    1. base_url；
    2. 请求超时时间；
    3. Authorization；
    4. GET / POST / PUT / DELETE 请求。
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
    ):
        """
        初始化请求客户端。
        """

        self.base_url = base_url.rstrip("/")

        self.timeout = timeout

        self.session = requests.Session()

    def set_token(
        self,
        token: str,
    ):
        """
        设置 JWT Access Token。

        后续所有请求自动携带：

        Authorization: Bearer xxx
        """

        self.session.headers.update({"Authorization": (f"Bearer {token}")})

    def clear_token(
        self,
    ):
        """
        清除当前 Token。
        """

        self.session.headers.pop(
            "Authorization",
            None,
        )

    def request(
        self,
        method: str,
        url: str,
        **kwargs,
    ):
        """
        发送统一 HTTP 请求。
        """

        # ======================================
        # 拼接完整请求地址
        # ======================================

        full_url = f"{self.base_url}" f"/{url.lstrip('/')}"

        # ======================================
        # 设置默认超时时间
        # ======================================

        kwargs.setdefault(
            "timeout",
            self.timeout,
        )

        # ======================================
        # 发送请求
        # ======================================

        response = self.session.request(
            method=method,
            url=full_url,
            **kwargs,
        )

        return response

    def get(
        self,
        url: str,
        **kwargs,
    ):
        """
        GET 请求。
        """

        return self.request(
            "GET",
            url,
            **kwargs,
        )

    def post(
        self,
        url: str,
        **kwargs,
    ):
        """
        POST 请求。
        """

        return self.request(
            "POST",
            url,
            **kwargs,
        )

    def put(
        self,
        url: str,
        **kwargs,
    ):
        """
        PUT 请求。
        """

        return self.request(
            "PUT",
            url,
            **kwargs,
        )

    def delete(
        self,
        url: str,
        **kwargs,
    ):
        """
        DELETE 请求。
        """

        return self.request(
            "DELETE",
            url,
            **kwargs,
        )
