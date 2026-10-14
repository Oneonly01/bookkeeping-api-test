import allure
import pytest
from common.tag_api import TagApi
from utils.assertions import assert_rejected


@allure.feature("标签模块")
class TestTag:
    """
    标签业务测试。


    当前覆盖：

    1. 标签创建；
    2. 标签查询；
    3. 标签修改；
    4. 标签删除；
    5. 参数异常。


    """

    @pytest.fixture(autouse=True)
    def cleanup_created_tags(self, tag_api, monkeypatch):
        """清理当前用例创建且尚未删除的标签。"""
        created_ids = set()
        create = tag_api.create_tag
        delete = tag_api.delete_tag

        def tracked_create(payload):
            response = create(payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200 and result.get("data"):
                    tag_id = result["data"].get("id")
                    if tag_id is not None:
                        created_ids.add(tag_id)
            return response

        def tracked_delete(tag_id):
            response = delete(tag_id)
            if response.status_code == 200 and response.json().get("code") == 200:
                created_ids.discard(tag_id)
            return response

        monkeypatch.setattr(tag_api, "create_tag", tracked_create)
        monkeypatch.setattr(tag_api, "delete_tag", tracked_delete)
        yield
        for tag_id in created_ids:
            response = delete(tag_id)
            assert (
                response.status_code == 200 and response.json().get("code") == 200
            ), f"清理测试标签失败：tag_id={tag_id}, response={response.text}"

    # ======================================
    # 创建标签成功
    # ======================================

    @allure.story("标签管理")
    @allure.title("创建标签成功")
    def test_create_tag_success(
        self,
        tag_api,
        tag_factory,
    ):
        """
        验证创建标签成功。


        测试流程：

        1. 生成标签数据；
        2. 调用创建标签接口；
        3. 验证返回数据。


        """

        # ==================================
        # 创建测试数据
        # ==================================

        payload = tag_factory.build_tag()

        # ==================================
        # 调用创建接口
        # ==================================

        response = tag_api.create_tag(payload)

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
        # 数据校验
        # ==================================

        assert result["data"]["name"] == payload["name"]

    # ======================================
    # 获取标签列表成功
    # ======================================

    @allure.story("标签查询")
    @allure.title("获取标签列表成功")
    def test_get_tag_list_success(
        self,
        tag_api,
    ):
        """
        验证获取当前用户标签列表成功。


        """

        response = tag_api.get_tag_list()

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
        # 数据类型校验
        # ==================================

        assert isinstance(
            result["data"],
            list,
        )

    # ======================================
    # 获取标签详情成功
    # ======================================

    @allure.story("标签查询")
    @allure.title("获取标签详情成功")
    def test_get_tag_detail_success(
        self,
        tag_api,
        tag_factory,
    ):
        """
        验证获取标签详情成功。

        测试流程：

        1. 创建标签；
        2. 获取标签ID；
        3. 查询详情。

        """

        payload = tag_factory.build_tag()

        create_response = tag_api.create_tag(payload)

        tag_id = create_response.json()["data"]["id"]

        response = tag_api.get_tag_detail(tag_id)

        assert response.status_code == 200

        result = response.json()

        assert result["code"] == 200

        assert result["data"]["id"] == tag_id

    # ======================================
    # 修改标签成功
    # ======================================

    @allure.story("标签管理")
    @allure.title("修改标签成功")
    def test_update_tag_success(
        self,
        tag_api,
        tag_factory,
    ):
        """
        验证修改标签成功。

        测试流程：

        1. 创建标签；
        2. 修改标签名称；
        3. 查询修改结果。

        """

        payload = tag_factory.build_tag()

        create_response = tag_api.create_tag(payload)

        tag_id = create_response.json()["data"]["id"]

        update_payload = {
            "name": "修改后的自动化测试标签",
            "color": "#409EFF",
        }

        response = tag_api.update_tag(
            tag_id,
            update_payload,
        )

        assert response.status_code == 200

        result = response.json()

        assert result["code"] == 200

        assert result["data"]["name"] == update_payload["name"]

    # ======================================
    # 删除标签成功
    # ======================================

    @allure.story("标签管理")
    @allure.title("删除标签成功")
    def test_delete_tag_success(
        self,
        tag_api,
        tag_factory,
    ):
        """
        验证删除标签成功。


        后端采用：

        逻辑删除。


        """

        payload = tag_factory.build_tag()

        create_response = tag_api.create_tag(payload)

        tag_id = create_response.json()["data"]["id"]

        response = tag_api.delete_tag(tag_id)

        assert response.status_code == 200

        result = response.json()

        assert result["code"] == 200

    # ======================================
    # 创建重复标签失败
    # ======================================

    @allure.story("标签异常")
    @allure.title("创建重复标签失败")
    def test_create_duplicate_tag_failed(
        self,
        tag_api,
        tag_factory,
    ):
        """
        验证同名标签不能重复创建。


        """

        payload = tag_factory.build_tag()

        response = tag_api.create_tag(payload)

        assert response.status_code == 200

        response = tag_api.create_tag(payload)

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 标签名称为空失败
    # ======================================

    @allure.story("标签异常")
    @allure.title("标签名称为空创建失败")
    def test_create_tag_empty_name_failed(
        self,
        tag_api,
        tag_factory,
    ):
        """
        验证标签名称为空创建失败。


        """

        payload = tag_factory.build_tag(
            name="",
        )

        response = tag_api.create_tag(payload)

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 标签名称超长失败
    # ======================================

    @allure.story("标签异常")
    @allure.title("标签名称超长创建失败")
    def test_create_tag_long_name_failed(
        self,
        tag_api,
        tag_factory,
    ):
        """
        验证标签名称超过50字符创建失败。


        """

        payload = tag_factory.build_tag(
            name="a" * 51,
        )

        response = tag_api.create_tag(payload)

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 删除不存在标签失败
    # ======================================

    @allure.story("标签异常")
    @allure.title("删除不存在标签失败")
    def test_delete_nonexistent_tag_failed(
        self,
        tag_api,
    ):
        """
        验证删除不存在标签失败。


        """

        response = tag_api.delete_tag(999999)

        assert response.status_code in [
            400,
            404,
        ]

    # ======================================
    # 删除标签后列表不显示
    # ======================================

    @allure.story("标签管理")
    @allure.title("删除标签后列表不显示")
    def test_deleted_tag_not_in_list(
        self,
        tag_api,
        tag_factory,
    ):
        """
        验证标签逻辑删除后，
        不再出现在标签列表。


        测试流程：

        1. 创建标签；
        2. 删除标签；
        3. 查询标签列表；
        4. 验证不存在。


        """

        payload = tag_factory.build_tag()

        create_response = tag_api.create_tag(payload)

        tag_id = create_response.json()["data"]["id"]

        # ==================================
        # 删除标签
        # ==================================

        response = tag_api.delete_tag(tag_id)

        assert response.status_code == 200

        # ==================================
        # 查询列表
        # ==================================

        response = tag_api.get_tag_list()

        assert response.status_code == 200

        result = response.json()

        # ==================================
        # 验证删除标签不存在
        # ==================================

        ids = [item["id"] for item in result["data"]]

        assert tag_id not in ids

    # ======================================
    # 用户隔离删除失败
    # ======================================

    @allure.story("标签权限")
    @allure.title("用户不能删除其他用户标签")
    def test_delete_other_user_tag_failed(
        self,
        tag_api,
        tag_factory,
        another_user_context,
        config,
    ):
        """
        验证用户不能删除其他用户创建的标签。


        测试流程：

        1. 用户A创建标签；
        2. 切换用户B；
        3. 用户B删除用户A标签；
        4. 验证删除失败。


        """

        # ==================================
        # 用户A创建标签
        # ==================================

        payload = tag_factory.build_tag()

        create_response = tag_api.create_tag(payload)

        assert create_response.status_code == 200

        tag_id = create_response.json()["data"]["id"]

        # ==================================
        # 切换用户B
        # ==================================

        another_tag_api = TagApi(
            client=another_user_context["client"],
            api_prefix=config.api_prefix,
        )

        # ==================================
        # 用户B删除用户A标签
        # ==================================

        response = another_tag_api.delete_tag(tag_id)

        # ==================================
        # 校验失败
        # ==================================

        assert response.status_code in [
            400,
            404,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 删除后重新创建同名标签
    # ======================================

    @allure.story("标签管理")
    @allure.title("删除后允许重新创建同名标签")
    def test_create_same_tag_after_delete_success(
        self,
        tag_api,
        tag_factory,
    ):
        """
        验证逻辑删除后的标签，
        可以重新创建。


        测试流程：

        1. 创建标签；
        2. 删除标签；
        3. 使用相同名称重新创建；
        4. 验证创建成功。


        """

        # ==================================
        # 创建标签
        # ==================================

        tag_name = tag_factory.generate_tag_name()

        payload = {
            "name": tag_name,
            "color": "",
        }

        response = tag_api.create_tag(payload)

        assert response.status_code == 200

        tag_id = response.json()["data"]["id"]

        # ==================================
        # 删除标签
        # ==================================

        response = tag_api.delete_tag(tag_id)

        assert response.status_code == 200

        # ==================================
        # 再次创建同名标签
        # ==================================

        response = tag_api.create_tag(payload)

        assert response.status_code == 200

        result = response.json()

        assert result["code"] == 200

        assert result["data"]["name"] == tag_name

    @allure.story("标签权限")
    @allure.title("其他用户不能查看或修改我的标签")
    def test_tag_other_user_cannot_read_or_update(
        self, tag_api, tag_factory, another_auth_client, config
    ):
        """用户 A 创建标签后，用户 B 的详情和修改请求都应失败。"""
        response = tag_api.create_tag(tag_factory.build_tag())
        assert response.status_code == 200, response.text
        tag_id = response.json()["data"]["id"]

        # 使用独立的用户 B 客户端，避免改动用户 A 的登录状态。
        other = TagApi(another_auth_client, config.api_prefix)
        assert_rejected(other.get_tag_detail(tag_id))
        assert_rejected(other.update_tag(tag_id, {"name": "无权修改"}))

        # 用户 A 仍能读取；类级清理 fixture 会删除该标签。
        response = tag_api.get_tag_detail(tag_id)
        assert response.status_code == 200, response.text
