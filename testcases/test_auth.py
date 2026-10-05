import allure


@allure.feature("用户认证")
class TestAuth:
    """
    用户认证接口自动化测试。

    当前覆盖：

    1. 登录成功；
    2. 登录失败。
    """

    @allure.story("用户登录")
    @allure.title("登录成功")
    def test_login_success(
        self,
        client,
        config,
    ):
        """
        测试正常账号密码登录。

        验证：

        1. HTTP 状态码为 200；
        2. 业务 code 为 200；
        3. 返回 access token；
        4. 返回 refresh token。
        """

        # ======================================
        # 获取登录接口地址
        # ======================================

        login_url = f"{config.api_prefix}" f"/auth/login/"

        # ======================================
        # 获取测试账号
        # ======================================

        test_user = config.test_user

        # ======================================
        # 发送登录请求
        # ======================================

        response = client.post(
            login_url,
            json=test_user,
        )

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200

        # ======================================
        # 解析 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200

        # ======================================
        # 获取 data
        # ======================================

        data = response_data.get(
            "data",
            {},
        )

        # ======================================
        # Token 断言
        # ======================================

        assert data.get("access_token")

        assert data.get("refresh_token")
        assert data.get("token_type") == "Bearer"

    @allure.story("用户登录")
    @allure.title("登录失败-密码错误")
    def test_login_wrong_password(
        self,
        client,
        config,
    ):
        """
        测试错误密码登录。

        验证：

        1. 接口不能返回登录成功；
        2. 业务 code 不能是 200。
        """

        # ======================================
        # 获取登录接口地址
        # ======================================

        login_url = f"{config.api_prefix}" f"/auth/login/"

        # ======================================
        # 构造错误登录参数
        # ======================================

        test_user = config.test_user.copy()

        test_user["password"] = "wrong_password_123456"

        # ======================================
        # 发送请求
        # ======================================

        response = client.post(
            login_url,
            json=test_user,
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 登录失败断言
        # ======================================

        assert response_data.get("code") != 200
