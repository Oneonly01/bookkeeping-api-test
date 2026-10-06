import allure
import pytest


@allure.feature("用户认证")
class TestAuth:
    """
    用户认证接口自动化测试。

    当前覆盖：

    1. 登录成功；
    2. 登录失败场景。

    当前测试结构：

    AuthApi：
        负责接口调用。

    config：
        负责读取测试环境和测试账号。

    pytest 参数化：
        负责批量覆盖登录异常场景。

    TestAuth：
        只负责测试流程和断言。
    """

    # ==========================================
    # 登录成功
    # ==========================================

    @allure.story("用户登录")
    @allure.title("登录成功")
    def test_login_success(
        self,
        auth_api,
        config,
    ):
        """
        验证正常账号密码登录成功。

        测试步骤：

        1. 从配置文件读取测试账号；
        2. 调用登录接口；
        3. 获取登录响应；
        4. 校验 Token 和用户信息。

        验证内容：

        1. HTTP 状态码为 200；
        2. 业务 code 为 200；
        3. 返回 access_token；
        4. 返回 refresh_token；
        5. token_type 为 Bearer；
        6. 返回用户信息；
        7. 返回用户 ID。

        注意：

        测试账号密码统一来自 config.yaml，
        不在测试代码中写死真实账号密码。
        """

        # ======================================
        # 获取测试账号
        # ======================================
        #
        # config.test_user 来自：
        #
        # config/config.yaml
        #
        # 测试代码不直接保存真实密码。
        #
        # ======================================

        test_user = config.test_user.copy()

        # ======================================
        # 调用登录接口
        # ======================================
        #
        # URL 和 POST 请求已经封装在：
        #
        # AuthApi.login()
        #
        # 测试用例不再需要自己拼：
        #
        # /api/v1/auth/login/
        #
        # ======================================

        response = auth_api.login(test_user)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"用户登录接口请求失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"用户登录业务执行失败：" f"{response_data}"
        )

        # ======================================
        # 获取登录响应 data
        # ======================================

        data = response_data.get(
            "data",
            {},
        )

        # ======================================
        # Access Token 断言
        # ======================================

        access_token = data.get("access_token")

        assert access_token, f"登录成功后未返回 access_token：" f"{response_data}"

        # ======================================
        # Refresh Token 断言
        # ======================================

        refresh_token = data.get("refresh_token")

        assert refresh_token, f"登录成功后未返回 refresh_token：" f"{response_data}"

        # ======================================
        # Token 类型断言
        # ======================================

        assert data.get("token_type") == "Bearer", (
            f"Token 类型不正确，"
            f"expected=Bearer，"
            f"actual={data.get('token_type')}"
        )

        # ======================================
        # 用户信息断言
        # ======================================

        user = data.get(
            "user",
            {},
        )

        assert user, f"登录成功后未返回用户信息：" f"{response_data}"

        # ======================================
        # 用户 ID 断言
        # ======================================

        assert user.get("id"), f"登录返回用户信息中缺少用户 ID：" f"{user}"

    # ==========================================
    # 登录失败数据驱动
    # ==========================================

    @allure.story("用户登录")
    @allure.title("登录失败场景验证")
    @pytest.mark.parametrize(
        ("case_name," "username_mode," "password_mode"),
        [
            (
                "密码错误",
                "normal",
                "wrong",
            ),
            (
                "用户名不存在",
                "not_found",
                "normal",
            ),
            (
                "密码为空",
                "normal",
                "empty",
            ),
        ],
        ids=[
            "wrong_password",
            "username_not_found",
            "empty_password",
        ],
    )
    def test_login_failed(
        self,
        auth_api,
        config,
        case_name,
        username_mode,
        password_mode,
    ):
        """
        验证用户登录失败场景。

        当前使用 pytest 参数化，
        一条测试方法覆盖多个异常场景。

        当前覆盖：

        1. 密码错误；
        2. 用户名不存在；
        3. 密码为空。

        验证内容：

        1. 登录不能成功；
        2. 业务 code 不能为 200；
        3. 不应该返回 access_token；
        4. 不应该返回 refresh_token。

        参数说明：

        case_name：
            当前测试场景名称。

        username_mode：

            normal：
                使用正常用户名。

            not_found：
                使用不存在的用户名。

        password_mode：

            normal：
                使用正常密码。

            wrong：
                使用错误密码。

            empty：
                使用空密码。
        """

        # ======================================
        # 获取正常测试账号
        # ======================================
        #
        # 使用 copy()，
        # 防止修改 config.test_user 原始数据。
        #
        # ======================================

        payload = config.test_user.copy()

        # ======================================
        # 根据场景修改用户名
        # ======================================

        if username_mode == "not_found":
            # 使用一个基本不可能存在的用户名。
            payload["username"] = "not_exist_user_" "987654321"

        elif username_mode != "normal":
            pytest.fail(f"未知 username_mode：" f"{username_mode}")

        # ======================================
        # 根据场景修改密码
        # ======================================

        if password_mode == "wrong":
            # 故意使用错误密码。
            payload["password"] = "wrong_password_123456"

        elif password_mode == "empty":
            # 空密码边界场景。
            payload["password"] = ""

        elif password_mode != "normal":
            pytest.fail(f"未知 password_mode：" f"{password_mode}")

        # ======================================
        # 调用登录接口
        # ======================================

        response = auth_api.login(payload)

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================
        #
        # 登录失败时，
        # 业务 code 不能为 200。
        #
        # 暂时不把 HTTP 400/401 写死，
        # 因为不同失败场景可能有不同状态码。
        #
        # ======================================

        assert response_data.get("code") != 200, (
            f"异常登录场景错误返回成功，"
            f"case_name={case_name}，"
            f"response={response_data}"
        )

        # ======================================
        # Token 不存在断言
        # ======================================
        #
        # 登录失败情况下，
        # 后端不能签发有效 Token。
        #
        # ======================================

        data = response_data.get("data")

        if isinstance(data, dict):
            assert not data.get("access_token"), (
                f"登录失败却返回 access_token，"
                f"case_name={case_name}，"
                f"response={response_data}"
            )

            assert not data.get("refresh_token"), (
                f"登录失败却返回 refresh_token，"
                f"case_name={case_name}，"
                f"response={response_data}"
            )

    @allure.story("Token 刷新")
    @allure.title("Refresh Token 刷新成功")
    def test_refresh_token_success(
        self,
        auth_api,
        refresh_token,
    ):
        """
        验证使用有效 Refresh Token
        可以成功获取新的 Access Token。

        验证内容：

        1. Refresh Token 请求成功；
        2. HTTP 状态码为 200；
        3. 业务 code 为 200；
        4. 返回新的 access_token；
        5. access_token 不为空。
        """

        # ======================================
        # 构造刷新 Token 请求参数
        # ======================================
        #
        # 当前先按照常见字段：
        #
        # refresh_token
        #
        # 进行请求。
        #
        # 如果你的后端实际字段不同，
        # 根据实际接口返回调整即可。
        #
        # ======================================

        payload = {
            "refresh_token": refresh_token,
        }

        # ======================================
        # 调用 Token 刷新接口
        # ======================================

        response = auth_api.refresh_token(payload)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"Refresh Token 刷新失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"Refresh Token 刷新业务失败：" f"{response_data}"
        )

        # ======================================
        # 获取响应 data
        # ======================================

        data = response_data.get(
            "data",
            {},
        )

        # ======================================
        # Access Token 断言
        # ======================================

        new_access_token = data.get("access_token")

        assert new_access_token, (
            f"Refresh Token 刷新成功后" f"未返回 access_token：" f"{response_data}"
        )

    @allure.story("Token 刷新")
    @allure.title("无效 Refresh Token 刷新失败")
    def test_refresh_token_failed(
        self,
        auth_api,
    ):
        """
        验证无效 Refresh Token
        不能获取新的 Access Token。

        验证内容：

        1. 业务 code 不能为 200；
        2. 不应该返回 access_token。
        """

        # ======================================
        # 构造无效 Refresh Token
        # ======================================

        payload = {
            "refresh_token": ("invalid_refresh_token_123456"),
        }

        # ======================================
        # 调用 Token 刷新接口
        # ======================================

        response = auth_api.refresh_token(payload)

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") != 200, (
            f"无效 Refresh Token " f"错误返回成功：" f"{response_data}"
        )

        # ======================================
        # 不应该返回 Access Token
        # ======================================

        data = response_data.get("data")

        if isinstance(data, dict):
            assert not data.get("access_token"), (
                f"无效 Refresh Token " f"却返回 access_token：" f"{response_data}"
            )

    @allure.story("退出登录")
    @allure.title("用户退出登录成功")
    def test_logout_success(
        self,
        fresh_auth_context,
    ):
        """
        验证用户正常退出登录。

        当前测试使用独立的一次性认证上下文。

        每次执行本测试都会：

        1. 创建独立 RequestClient；
        2. 重新登录；
        3. 获取新的 Access Token；
        4. 获取新的 Refresh Token；
        5. 使用这组 Token 执行退出登录。

        因此退出操作不会污染：

        1. session 级 access_token；
        2. session 级 refresh_token；
        3. 其他认证测试；
        4. 账户等业务接口测试。
        """

        # ======================================
        # 获取当前测试专属 AuthApi
        # ======================================

        auth_api = fresh_auth_context["auth_api"]

        # ======================================
        # 获取当前测试专属 Refresh Token
        # ======================================

        refresh_token = fresh_auth_context["refresh_token"]

        # ======================================
        # 构造退出登录请求
        # ======================================

        payload = {
            "refresh_token": refresh_token,
        }

        # ======================================
        # 调用退出登录接口
        # ======================================
        #
        # fresh_auth_context 中的独立 client
        # 已经设置：
        #
        # Authorization: Bearer <access_token>
        #
        # 所以这里同时具备：
        #
        # Access Token
        # +
        # Refresh Token
        #
        # ======================================

        response = auth_api.logout(payload)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"用户退出登录失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"用户退出登录业务失败：" f"{response_data}"
        )

    @allure.story("退出登录")
    @allure.title("无效 Refresh Token 退出失败")
    def test_logout_invalid_refresh_token(
        self,
        auth_api,
    ):
        """
        验证使用无效 Refresh Token
        不能正常执行退出登录。

        测试步骤：

        1. 构造一个无效 Refresh Token；
        2. 调用退出登录接口；
        3. 验证接口正确返回失败。

        验证内容：

        1. 业务 code 不能为 200；
        2. 接口不能错误返回退出成功。

        该测试用于验证：

        1. Token 合法性校验；
        2. 异常 Token 处理；
        3. 退出接口安全性。
        """

        # ======================================
        # 构造无效 Refresh Token
        # ======================================

        payload = {
            "refresh_token": ("invalid_refresh_token_123456"),
        }

        # ======================================
        # 调用退出登录接口
        # ======================================

        response = auth_api.logout(payload)

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================
        #
        # 无效 Token 不能退出成功。
        #
        # HTTP 状态码暂时不写死，
        # 因为后端可能返回：
        #
        # 400
        # 401
        #
        # 这里首先验证统一业务 code。
        #
        # ======================================

        assert response_data.get("code") != 200, (
            f"无效 Refresh Token " f"错误返回退出成功：" f"{response_data}"
        )

    @allure.story("退出登录")
    @allure.title("退出登录后 Refresh Token 失效")
    def test_refresh_token_invalid_after_logout(
        self,
        fresh_auth_context,
    ):
        """
        验证用户退出登录后，
        原 Refresh Token 不能继续刷新 Access Token。

        测试流程：

        1. fresh_auth_context 自动重新登录；
        2. 获取当前测试专属 Access Token；
        3. 获取当前测试专属 Refresh Token；
        4. 使用当前 Token 执行退出登录；
        5. 再次使用同一个 Refresh Token
        调用 Token 刷新接口。

        预期结果：

        1. 退出登录成功；
        2. 退出接口 HTTP 状态码为 200；
        3. 退出接口业务 code 为 200；
        4. 退出后原 Refresh Token 已失效；
        5. 使用原 Refresh Token 再次刷新时失败；
        6. 不能再次获得新的 Access Token。

        测试意义：

        单纯验证 logout 接口返回 200，
        只能说明接口调用成功。

        但不能证明 Refresh Token
        是否真正失效。

        本测试通过：

        logout
        +
        refresh

        两个接口联合验证，

        可以确认退出登录后的
        Token 黑名单 / Token 失效机制
        是否真正生效。

        当前使用 fresh_auth_context，
        每条测试拥有独立 Token，

        因此不会污染其他认证测试。
        """

        # ======================================
        # 获取当前测试专属 AuthApi
        # ======================================

        auth_api = fresh_auth_context["auth_api"]

        # ======================================
        # 获取当前测试专属 Refresh Token
        # ======================================

        refresh_token = fresh_auth_context["refresh_token"]

        # ======================================
        # 构造退出登录请求数据
        # ======================================

        logout_payload = {
            "refresh_token": refresh_token,
        }

        # ======================================
        # 第一步：执行退出登录
        # ======================================
        #
        # fresh_auth_context 中的独立 client
        # 已经提前设置：
        #
        # Authorization: Bearer <access_token>
        #
        # 所以满足当前退出接口：
        #
        # 1. Access Token
        # 2. Refresh Token
        #
        # 两个认证条件。
        #
        # ======================================

        logout_response = auth_api.logout(logout_payload)

        # ======================================
        # 退出接口 HTTP 状态码断言
        # ======================================

        assert logout_response.status_code == 200, (
            f"退出登录失败，"
            f"status_code="
            f"{logout_response.status_code}，"
            f"response={logout_response.text}"
        )

        # ======================================
        # 解析退出响应
        # ======================================

        logout_response_data = logout_response.json()

        # ======================================
        # 退出接口业务状态码断言
        # ======================================

        assert logout_response_data.get("code") == 200, (
            f"退出登录业务失败：" f"{logout_response_data}"
        )

        # ======================================
        # 第二步：再次使用原 Refresh Token
        # ======================================
        #
        # 注意：
        #
        # 这里故意继续使用退出前的
        # refresh_token。
        #
        # 如果 logout 真正生效，
        # 这个 Token 应该已经：
        #
        # 1. 被加入黑名单；
        # 或
        # 2. 被后端标记为失效。
        #
        # ======================================

        refresh_payload = {
            "refresh_token": refresh_token,
        }

        refresh_response = auth_api.refresh_token(refresh_payload)

        # ======================================
        # 解析刷新接口响应
        # ======================================

        refresh_response_data = refresh_response.json()

        # ======================================
        # 刷新失败业务状态码断言
        # ======================================
        #
        # 退出成功后，
        # 原 Refresh Token 绝对不能
        # 再次返回业务 code=200。
        #
        # ======================================

        assert refresh_response_data.get("code") != 200, (
            f"用户退出登录后，"
            f"原 Refresh Token 仍然可以刷新，"
            f"说明 Token 失效机制可能未生效："
            f"{refresh_response_data}"
        )

        # ======================================
        # 验证不能返回新的 Access Token
        # ======================================

        refresh_data = refresh_response_data.get("data")

        if isinstance(
            refresh_data,
            dict,
        ):
            assert not refresh_data.get("access_token"), (
                f"用户退出登录后，"
                f"原 Refresh Token "
                f"仍然获得了新的 access_token："
                f"{refresh_response_data}"
            )
