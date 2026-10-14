class UserApi:
    """
    用户业务接口封装。

    主要负责：

    1. 获取当前用户信息；
    2. 修改用户信息；
    3. 修改密码；
    4. 上传头像。

    注意：

    登录、注册、Token刷新、退出登录：

    属于认证模块 AuthApi。

    用户资料相关：

    属于 UserApi。
    """

    def __init__(
        self,
        client,
        api_prefix: str,
    ):
        """
        初始化用户接口。

        参数：

        client:
            已设置 JWT Token 的 RequestClient。

        api_prefix:
            API统一前缀。

            例如：

            /api/v1
        """

        self.client = client

        self.api_prefix = api_prefix.rstrip("/")

    # ======================================
    # 获取当前用户信息
    # ======================================

    def get_profile(
        self,
    ):
        """
        获取当前登录用户信息。

        接口：

        GET /api/v1/users/me/


        返回：

        requests.Response
        """

        # ==================================
        # 拼接接口地址
        # ==================================

        url = f"{self.api_prefix}" "/users/me/"

        # ==================================
        # 发送 GET 请求
        # ==================================

        return self.client.get(url)

    # ======================================
    # 修改用户信息
    # ======================================

    def update_profile(
        self,
        payload: dict,
    ):
        """
        修改当前用户信息。


        接口：

        PUT /api/v1/users/me/


        参数：

        payload:
            用户修改后的数据。


        返回：

        requests.Response
        """

        # ==================================
        # 拼接接口地址
        # ==================================

        url = f"{self.api_prefix}" "/users/me/"

        # ==================================
        # 发送 PUT 请求
        #
        # 用户资料修改使用 JSON
        #
        # ==================================

        return self.client.put(
            url,
            json=payload,
        )

    # ======================================
    # 修改密码
    # ======================================

    def change_password(
        self,
        payload: dict,
    ):
        """
        修改用户密码。


        接口：

        PUT /api/v1/users/password/


        参数：

        payload:

            {
                old_password:
                new_password:
                confirm_password:
            }


        返回：

        requests.Response
        """

        # ==================================
        # 拼接接口地址
        # ==================================

        url = f"{self.api_prefix}" "/users/password/"

        # ==================================
        # 发送修改密码请求
        # ==================================

        return self.client.put(
            url,
            json=payload,
        )

    # ======================================
    # 上传用户头像
    # ======================================

    def upload_avatar(
        self,
        files: dict,
    ):
        """
        上传用户头像。


        接口：

        POST /api/v1/users/avatar/


        参数：

        files:

            multipart/form-data 文件。


            示例：

            {
                "avatar": (
                    "test.png",
                    file_object,
                    "image/png"
                )
            }


        返回：

        requests.Response
        """

        # ==================================
        # 拼接接口地址
        # ==================================

        url = f"{self.api_prefix}" "/users/avatar/"

        # ==================================
        # 文件上传

        # 注意：

        # 不能使用 json 参数

        # 必须使用 files

        # ==================================

        return self.client.post(
            url,
            files=files,
        )
