import allure

from common.user_api import UserApi
from utils.request import RequestClient


@allure.feature("用户模块")
class TestUser:
    """
    用户业务测试。

    当前覆盖：

    1. 用户注册；
    2. 用户资料；
    3. 密码修改；
    4. 头像上传。

    """

    # ======================================
    # 用户注册
    # ======================================

    @allure.story("用户注册")
    @allure.title("用户注册成功")
    def test_register_success(
        self,
        auth_api,
        user_factory,
    ):
        """
        验证用户注册成功。


        测试流程：

        1. 生成唯一注册账号；
        2. 调用注册接口；
        3. 验证 HTTP 状态码；
        4. 验证业务状态码。


        """

        # ==================================
        # 创建注册数据
        # ==================================

        payload = user_factory.build_register()

        # ==================================
        # 调用注册接口
        # ==================================

        response = auth_api.register(payload)

        # ==================================
        # HTTP状态码校验
        # ==================================

        assert response.status_code == 200

        # ==================================
        # 响应数据解析
        # ==================================

        result = response.json()

        # ==================================
        # 业务状态码校验
        # ==================================

        assert result["code"] == 200

    # ======================================
    # 用户名重复
    # ======================================

    @allure.story("用户注册")
    @allure.title("用户名重复注册失败")
    def test_register_duplicate_username_failed(
        self,
        auth_api,
        user_factory,
    ):
        """
        验证用户名重复无法注册。


        测试流程：

        1. 第一次注册用户；
        2. 使用相同用户名再次注册；
        3. 验证第二次注册失败。


        """

        username = user_factory.generate_username()

        # ==================================
        # 第一次注册
        # ==================================

        first_payload = user_factory.build_register(
            username=username,
        )

        response = auth_api.register(first_payload)

        assert response.status_code == 200

        result = response.json()

        assert result["code"] == 200

        # ==================================
        # 第二次注册相同用户名
        # ==================================

        second_payload = user_factory.build_register(
            username=username,
        )

        response = auth_api.register(second_payload)

        assert response.status_code in [
            400,
            409,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 确认密码不一致
    # ======================================

    @allure.story("用户注册")
    @allure.title("确认密码不一致注册失败")
    def test_register_confirm_password_failed(
        self,
        auth_api,
        user_factory,
    ):
        """
        验证确认密码不一致注册失败。


        测试流程：

        1. 生成注册数据；
        2. 修改 confirm_password；
        3. 调用注册接口；
        4. 验证注册失败。


        """

        payload = user_factory.build_register()

        # ==================================
        # 修改确认密码
        # ==================================

        payload["confirm_password"] = "WrongPassword123"

        response = auth_api.register(payload)

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 获取用户信息
    # ======================================

    @allure.story("用户信息")
    @allure.title("获取当前用户信息成功")
    def test_get_profile_success(
        self,
        user_api,
        config,
    ):
        """
        验证获取当前用户信息成功。


        测试流程：

        1. 使用登录后的Token；
        2. 调用用户信息接口；
        3. 验证返回用户数据。


        """

        with allure.step("获取当前用户信息"):

            response = user_api.get_profile()

        # ==================================
        # HTTP状态码校验
        # ==================================

        assert response.status_code == 200

        # ==================================
        # 解析响应
        # ==================================

        result = response.json()

        # ==================================
        # 业务状态码校验
        # ==================================

        assert result["code"] == 200

        # ==================================
        # 数据校验
        # ==================================

        data = result["data"]

        assert data is not None

        assert data["username"] == config.test_user["username"]

    # ======================================
    # 修改用户信息
    # ======================================

    @allure.story("用户信息")
    @allure.title("修改用户信息成功")
    def test_update_profile_success(
        self,
        user_api,
        config,
    ):
        """
        验证修改用户信息成功。


        测试流程：

        1. 查询当前用户信息；
        2. 修改昵称；
        3. 验证修改接口成功；
        4. 查询用户信息；
        5. 验证昵称修改成功；
        6. 恢复原昵称。


        """

        # ==================================
        # 获取原用户信息
        # ==================================

        with allure.step("查询修改前用户信息"):

            response = user_api.get_profile()

            assert response.status_code == 200

            result = response.json()

            assert result["code"] == 200

            old_nickname = result["data"].get("nickname")

        # ==================================
        # 修改用户信息
        # ==================================

        new_nickname = "pytest修改用户" * 5

        payload = {"nickname": new_nickname}

        with allure.step("修改用户昵称"):

            response = user_api.update_profile(payload)

            assert response.status_code == 200

            result = response.json()

            assert result["code"] == 200

        # ==================================
        # 查询修改结果
        # ==================================

        with allure.step("验证用户信息修改结果"):

            response = user_api.get_profile()

            assert response.status_code == 200

            result = response.json()

            assert result["code"] == 200

            assert result["data"]["nickname"] == new_nickname

        # ==================================
        # 恢复原数据
        # ==================================

        if old_nickname:

            user_api.update_profile({"nickname": old_nickname})

    # ======================================
    # 修改密码成功
    # ======================================

    @allure.story("用户密码")
    @allure.title("修改密码成功")
    def test_change_password_success(
        self,
        auth_api,
        user_factory,
    ):
        """
        验证修改用户密码成功。


        测试流程：

        1. 创建临时测试用户；
        2. 注册用户；
        3. 使用旧密码登录；
        4. 获取 Access Token；
        5. 设置 JWT Token；
        6. 调用修改密码接口；
        7. 清除旧 Token；
        8. 使用新密码登录成功；
        9. 使用旧密码登录失败。


        为什么使用临时用户：

        修改密码属于破坏性操作。

        如果修改公共测试账号密码，
        会影响其他测试用例。


        """

        # ==================================
        # 生成临时用户
        # ==================================

        with allure.step("生成临时测试用户"):

            user_payload = user_factory.build_register()

        old_password = user_payload["password"]

        new_password = "NewTest@123456"

        # ==================================
        # 注册用户
        # ==================================

        with allure.step("注册测试用户"):

            response = auth_api.register(user_payload)

            assert response.status_code == 200

            result = response.json()

            assert result["code"] == 200

        # ==================================
        # 使用旧密码登录
        # ==================================

        with allure.step("使用旧密码登录"):

            login_response = auth_api.login(
                {
                    "username": user_payload["username"],
                    "password": old_password,
                }
            )

            assert login_response.status_code == 200

            login_result = login_response.json()

            assert login_result["code"] == 200

            # ==================================
            # 获取 Access Token
            # ==================================

            access_token = login_result["data"]["access_token"]

        # ==================================
        # 创建独立认证客户端
        #
        # 不污染 auth_api.client
        #
        # ==================================

        user_client = RequestClient(base_url=auth_api.client.base_url)

        user_client.set_token(access_token)

        # ==================================
        # 创建 UserApi
        # ==================================

        user_api = UserApi(
            client=user_client,
            api_prefix="/api/v1",
        )

        # ==================================
        # 修改密码
        # ==================================

        with allure.step("修改用户密码"):

            response = user_api.change_password(
                {
                    "old_password": old_password,
                    "new_password": new_password,
                    "confirm_password": new_password,
                }
            )

            assert response.status_code == 200

            result = response.json()

            assert result["code"] == 200

        # ==================================
        # 使用新密码登录
        # ==================================

        with allure.step("验证新密码登录成功"):

            response = auth_api.login(
                {
                    "username": user_payload["username"],
                    "password": new_password,
                }
            )

            assert response.status_code == 200

            result = response.json()

            assert result["code"] == 200

        # ==================================
        # 使用旧密码登录
        # ==================================

        with allure.step("验证旧密码登录失败"):

            response = auth_api.login(
                {
                    "username": user_payload["username"],
                    "password": old_password,
                }
            )

            result = response.json()

            assert result["code"] != 200

    # ======================================
    # 上传头像
    # ======================================

    @allure.story("用户头像")
    @allure.title("上传头像成功")
    def test_upload_avatar_success(
        self,
        user_api,
    ):
        """
        验证上传用户头像成功。


        测试流程：

        1. 打开测试图片；
        2. 调用上传头像接口；
        3. 验证上传成功；
        4. 查询用户信息；
        5. 验证头像地址存在。


        """

        # ==================================
        # 测试图片路径
        # ==================================

        image_path = "E:/Project/bookkeeping_api_test/data/imgs/avatar.gif"

        with allure.step("打开头像文件"):

            with open(
                image_path,
                "rb",
            ) as file:

                files = {"avatar": ("avatar.png", file, "image/png")}

                # ==================================
                # 上传头像
                # ==================================

                response = user_api.upload_avatar(files)

        # ==================================
        # HTTP状态码校验
        # ==================================

        assert response.status_code == 200

        result = response.json()

        # ==================================
        # 业务状态码校验
        # ==================================

        assert result["code"] == 200

        # ==================================
        # 查询用户信息
        # ==================================

        response = user_api.get_profile()

        assert response.status_code == 200

        result = response.json()

        assert result["code"] == 200

        # ==================================
        # 验证头像地址
        # ==================================

        assert result["data"]["avatar"] is not None

    # ======================================
    # 邮箱重复注册
    # ======================================
    @allure.story("用户注册")
    @allure.title("邮箱重复注册失败")
    def test_register_duplicate_email_failed(
        self,
        auth_api,
        user_factory,
    ):
        """
        验证邮箱重复无法注册。


        测试流程：

        1. 生成唯一邮箱；
        2. 使用邮箱注册用户；
        3. 使用相同邮箱再次注册；
        4. 验证第二次注册失败。


        """

        # ==================================
        # 生成测试邮箱
        # ==================================

        email = user_factory.generate_email()

        # ==================================
        # 第一次注册
        # ==================================

        with allure.step("第一次使用邮箱注册"):

            first_payload = user_factory.build_register(
                email=email,
            )

            response = auth_api.register(first_payload)

            assert response.status_code == 200

            result = response.json()

            assert result["code"] == 200

        # ==================================
        # 第二次使用相同邮箱注册
        # ==================================

        with allure.step("重复邮箱注册"):

            second_payload = user_factory.build_register(
                email=email,
            )

            response = auth_api.register(second_payload)

            # 根据后端实际情况
            # 可能返回400或者409

            assert response.status_code in [
                400,
                409,
            ]

            result = response.json()

            assert result["code"] != 200

    # ======================================
    # 手机号重复注册
    # ======================================
    @allure.story("用户注册")
    @allure.title("手机号重复注册失败")
    def test_register_duplicate_phone_failed(
        self,
        auth_api,
        user_factory,
    ):
        """
        验证手机号重复无法注册。


        测试流程：

        1. 生成唯一手机号；
        2. 第一次使用手机号注册；
        3. 第二次使用相同手机号注册；
        4. 验证注册失败。


        """

        # ==================================
        # 生成测试手机号
        # ==================================

        phone = user_factory.generate_phone()

        # ==================================
        # 第一次注册
        # ==================================

        with allure.step("第一次使用手机号注册"):

            first_payload = user_factory.build_register(
                phone=phone,
            )

            response = auth_api.register(first_payload)

            assert response.status_code == 200

            result = response.json()

            assert result["code"] == 200

        # ==================================
        # 第二次重复手机号注册
        # ==================================

        with allure.step("重复手机号注册"):

            second_payload = user_factory.build_register(
                phone=phone,
            )

            response = auth_api.register(second_payload)

            assert response.status_code in [
                400,
                409,
            ]

            result = response.json()

            assert result["code"] != 200

    # ======================================
    # 修改用户信息
    # ======================================
    # ======================================
    # 修改昵称为空失败
    # ======================================

    @allure.story("用户信息")
    @allure.title("修改昵称为空失败")
    def test_update_profile_empty_nickname_failed(
        self,
        user_api,
    ):
        """
        验证用户昵称为空时修改失败。


        测试流程：

        1. 调用修改用户信息接口；
        2. 传入空昵称；
        3. 验证修改失败。


        """

        with allure.step("提交空昵称修改请求"):

            response = user_api.update_profile(
                {
                    "nickname": "",
                }
            )

        # ==================================
        # 状态码校验
        # ==================================

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        # ==================================
        # 业务失败校验
        # ==================================

        assert result["code"] != 200

    # ======================================
    # 修改昵称长度超限失败
    # ======================================

    @allure.story("用户信息")
    @allure.title("修改昵称长度超限失败")
    def test_update_profile_long_nickname_failed(
        self,
        user_api,
    ):
        """
        验证昵称超过最大长度修改失败。


        测试流程：

        1. 构造超长昵称；
        2. 调用修改用户信息接口；
        3. 验证修改失败。


        """

        long_nickname = "a" * 51

        with allure.step("提交超长昵称"):

            response = user_api.update_profile(
                {
                    "nickname": long_nickname,
                }
            )

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 原密码错误修改失败
    # ======================================

    @allure.story("用户密码")
    @allure.title("原密码错误修改密码失败")
    def test_change_password_wrong_old_password_failed(
        self,
        auth_api,
        user_factory,
    ):
        """
        验证旧密码错误时不能修改密码。

        测试流程：

        1. 创建临时用户；
        2. 注册用户；
        3. 登录获取Token；
        4. 使用错误旧密码修改密码；
        5. 验证修改失败。


        """

        from common.user_api import UserApi

        # ==================================
        # 创建测试用户
        # ==================================

        user_payload = user_factory.build_register()

        old_password = user_payload["password"]

        response = auth_api.register(user_payload)

        assert response.status_code == 200

        # ==================================
        # 登录
        # ==================================

        login_response = auth_api.login(
            {
                "username": user_payload["username"],
                "password": old_password,
            }
        )

        assert login_response.status_code == 200

        token = login_response.json()["data"]["access_token"]

        auth_api.client.set_token(token)

        user_api = UserApi(
            client=auth_api.client,
            api_prefix="/api/v1",
        )

        # ==================================
        # 错误旧密码修改
        # ==================================

        response = user_api.change_password(
            {
                "old_password": "WrongPassword123",
                "new_password": "NewTest@123456",
                "confirm_password": "NewTest@123456",
            }
        )

        # ==================================
        # 校验失败
        # ==================================

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 新密码确认不一致失败
    # ======================================

    @allure.story("用户密码")
    @allure.title("新密码与确认密码不一致修改失败")
    def test_change_password_confirm_password_failed(
        self,
        auth_api,
        user_factory,
    ):
        """
        验证确认密码不一致时修改密码失败。


        测试流程：

        1. 创建临时用户；
        2. 注册用户；
        3. 登录获取Token；
        4. 提交不同的新密码和确认密码；
        5. 验证修改失败。


        """

        from common.user_api import UserApi

        # ==================================
        # 创建测试用户
        # ==================================

        user_payload = user_factory.build_register()

        old_password = user_payload["password"]

        response = auth_api.register(user_payload)

        assert response.status_code == 200

        # ==================================
        # 登录获取Token
        # ==================================

        response = auth_api.login(
            {
                "username": user_payload["username"],
                "password": old_password,
            }
        )

        assert response.status_code == 200

        token = response.json()["data"]["access_token"]

        auth_api.client.set_token(token)

        user_api = UserApi(
            client=auth_api.client,
            api_prefix="/api/v1",
        )

        # ==================================
        # 修改密码
        # ==================================

        response = user_api.change_password(
            {
                "old_password": old_password,
                "new_password": "NewTest@123456",
                "confirm_password": "DifferentPassword123",
            }
        )

        # ==================================
        # 校验失败
        # ==================================

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 新旧密码相同失败
    # ======================================

    @allure.story("用户密码")
    @allure.title("新密码与旧密码相同修改失败")
    def test_change_password_same_password_failed(
        self,
        auth_api,
        user_factory,
    ):
        """
        验证新密码不能和旧密码相同。


        测试流程：

        1. 创建临时用户；
        2. 登录；
        3. 使用原密码作为新密码；
        4. 验证修改失败。


        """

        from common.user_api import UserApi

        user_payload = user_factory.build_register()

        old_password = user_payload["password"]

        response = auth_api.register(user_payload)

        assert response.status_code == 200

        response = auth_api.login(
            {
                "username": user_payload["username"],
                "password": old_password,
            }
        )

        assert response.status_code == 200

        token = response.json()["data"]["access_token"]

        auth_api.client.set_token(token)

        user_api = UserApi(
            client=auth_api.client,
            api_prefix="/api/v1",
        )

        response = user_api.change_password(
            {
                "old_password": old_password,
                "new_password": old_password,
                "confirm_password": old_password,
            }
        )

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 上传非图片文件失败
    # ======================================

    @allure.story("用户头像")
    @allure.title("上传非图片文件失败")
    def test_upload_avatar_invalid_file_failed(
        self,
        user_api,
    ):
        """
        验证上传非图片文件失败。


        测试流程：

        1. 创建非图片文件；
        2. 调用头像上传接口；
        3. 验证上传失败。


        """

        import io

        # ==================================
        # 构造文本文件
        # ==================================

        file = io.BytesIO(b"this is not image")

        files = {
            "avatar": (
                "test.txt",
                file,
                "text/plain",
            )
        }

        with allure.step("上传非图片文件"):

            response = user_api.upload_avatar(files)

        # ==================================
        # 校验失败
        # ==================================

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 上传空文件失败
    # ======================================

    @allure.story("用户头像")
    @allure.title("上传空头像文件失败")
    def test_upload_avatar_empty_file_failed(
        self,
        user_api,
    ):
        """
        验证上传空文件失败。


        """

        import io

        file = io.BytesIO(b"")

        files = {
            "avatar": (
                "empty.png",
                file,
                "image/png",
            )
        }

        with allure.step("上传空文件"):

            response = user_api.upload_avatar(files)

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 上传超过5MB头像失败
    # ======================================

    @allure.story("用户头像")
    @allure.title("上传超过5MB头像失败")
    def test_upload_avatar_exceed_size_failed(
        self,
        user_api,
    ):
        """
        验证头像超过5MB上传失败。
        """

        image_path = "E:/Project/bookkeeping_api_test/" "data/imgs/" "large_avatar.png"

        with allure.step("上传超过5MB头像"):

            with open(
                image_path,
                "rb",
            ) as file:

                files = {
                    "avatar": (
                        "large_avatar.png",
                        file,
                        "image/png",
                    )
                }

                response = user_api.upload_avatar(files)

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 修改邮箱格式错误失败
    # ======================================

    @allure.story("用户信息")
    @allure.title("修改邮箱格式错误失败")
    def test_update_profile_invalid_email_failed(
        self,
        user_api,
    ):
        """
        验证修改邮箱格式错误时失败。


        测试流程：

        1. 调用修改用户信息接口；
        2. 传入非法邮箱；
        3. 验证修改失败。


        """

        with allure.step("提交非法邮箱"):

            response = user_api.update_profile(
                {
                    "email": "123456",
                }
            )

        # ==================================
        # 状态码校验
        # ==================================

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        # ==================================
        # 业务失败校验
        # ==================================

        assert result["code"] != 200

    # ======================================
    # 上传不支持图片格式失败
    # ======================================

    @allure.story("用户头像")
    @allure.title("上传不支持图片格式失败")
    def test_upload_avatar_unsupported_format_failed(
        self,
        user_api,
    ):
        """
        验证上传不支持的图片格式失败。


        当前系统支持：

        JPG
        PNG
        WEBP
        GIF


        BMP不支持。


        """

        image_path = "E:/Project/bookkeeping_api_test/" "data/imgs/avatar.bmp"

        with allure.step("上传BMP格式图片"):

            with open(
                image_path,
                "rb",
            ) as file:

                files = {
                    "avatar": (
                        "avatar.bmp",
                        file,
                        "image/bmp",
                    )
                }

                response = user_api.upload_avatar(files)

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200
