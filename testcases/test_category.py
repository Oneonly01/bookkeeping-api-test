import allure
import pytest
from common.category_api import CategoryApi
from utils.assertions import assert_rejected


@allure.feature("分类模块")
class TestCategory:
    """
    分类业务测试。

    覆盖：

    1. 创建分类；
    2. 查询分类；
    3. 修改分类；
    4. 删除分类；
    5. 参数异常；
    6. 用户隔离。
    """

    @pytest.fixture(autouse=True)
    def cleanup_created_categories(self, category_api, monkeypatch):
        """清理当前用例创建且尚未删除的分类。"""
        created_ids = set()
        create = category_api.create_category
        delete = category_api.delete_category

        def tracked_create(payload):
            response = create(payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200 and result.get("data"):
                    category_id = result["data"].get("id")
                    if category_id is not None:
                        created_ids.add(category_id)
            return response

        def tracked_delete(category_id):
            response = delete(category_id)
            if response.status_code == 200 and response.json().get("code") == 200:
                created_ids.discard(category_id)
            return response

        monkeypatch.setattr(category_api, "create_category", tracked_create)
        monkeypatch.setattr(category_api, "delete_category", tracked_delete)
        yield
        for category_id in created_ids:
            response = delete(category_id)
            assert response.status_code == 200 and response.json().get("code") == 200, (
                f"清理测试分类失败：category_id={category_id}, response={response.text}"
            )

    # ======================================
    # 创建分类成功
    # ======================================

    @allure.story("分类管理")
    @allure.title("创建分类成功")
    def test_create_category_success(
        self,
        category_api,
        category_factory,
    ):
        """
        验证创建分类成功。
        """

        payload = category_factory.build_category()

        response = category_api.create_category(payload)

        assert response.status_code == 200

        result = response.json()

        assert result["code"] == 200

        data = result["data"]

        assert data["name"] == payload["name"]

        assert data["category_type"] == payload["category_type"]

    # ======================================
    # 获取分类列表成功
    # ======================================

    @allure.story("分类查询")
    @allure.title("获取分类列表成功")
    def test_get_category_list_success(
        self,
        category_api,
    ):

        response = category_api.get_category_list()

        assert response.status_code == 200

        result = response.json()

        assert result["code"] == 200

        assert isinstance(
            result["data"],
            list,
        )

    # ======================================
    # 获取分类详情成功
    # ======================================

    @allure.story("分类查询")
    @allure.title("获取分类详情成功")
    def test_get_category_detail_success(
        self,
        category_api,
        category_factory,
    ):

        payload = category_factory.build_category()

        create_response = category_api.create_category(payload)

        category_id = create_response.json()["data"]["id"]

        response = category_api.get_category_detail(category_id)

        assert response.status_code == 200

        result = response.json()

        assert result["code"] == 200

        assert result["data"]["id"] == category_id

    # ======================================
    # 修改分类成功
    # ======================================

    @allure.story("分类管理")
    @allure.title("修改分类成功")
    def test_update_category_success(
        self,
        category_api,
        category_factory,
    ):

        payload = category_factory.build_category()

        create_response = category_api.create_category(payload)

        category_id = create_response.json()["data"]["id"]

        update_data = {
            **payload,
            "name": category_factory.generate_name(),
        }

        response = category_api.update_category(
            category_id,
            update_data,
        )

        assert response.status_code == 200, response.text

        result = response.json()

        assert result["code"] == 200

        assert result["data"]["name"] == update_data["name"]

    # ======================================
    # 删除分类成功
    # ======================================

    @allure.story("分类管理")
    @allure.title("删除分类成功")
    def test_delete_category_success(
        self,
        category_api,
        category_factory,
    ):

        payload = category_factory.build_category()

        create_response = category_api.create_category(payload)

        category_id = create_response.json()["data"]["id"]

        response = category_api.delete_category(category_id)

        assert response.status_code == 200

        result = response.json()

        assert result["code"] == 200

    # ======================================
    # 创建重复分类失败
    # ======================================

    @allure.story("分类异常")
    @allure.title("创建重复分类失败")
    def test_create_duplicate_category_failed(
        self,
        category_api,
        category_factory,
    ):

        payload = category_factory.build_category()

        response = category_api.create_category(payload)

        assert response.status_code == 200

        response = category_api.create_category(payload)

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 创建分类名称为空失败
    # ======================================

    @allure.story("分类异常")
    @allure.title("分类名称为空创建失败")
    def test_create_category_empty_name_failed(
        self,
        category_api,
    ):

        response = category_api.create_category(
            {
                "name": "",
                "category_type": "expense",
            }
        )

        assert response.status_code in [
            400,
            422,
        ]

        result = response.json()

        assert result["code"] != 200

    # ======================================
    # 删除不存在分类失败
    # ======================================

    @allure.story("分类异常")
    @allure.title("删除不存在分类失败")
    def test_delete_nonexistent_category_failed(
        self,
        category_api,
    ):

        response = category_api.delete_category(999999)

        assert response.status_code in [
            400,
            404,
        ]

    @allure.story("分类权限")
    @allure.title("其他用户不能访问我的分类")
    def test_category_other_user_cannot_access(
        self, category_api, category_factory, another_auth_client, config
    ):
        """用户 A 创建分类，用户 B 不能查看、修改或删除。"""
        response = category_api.create_category(category_factory.build_category())
        assert response.status_code == 200, response.text
        category_id = response.json()["data"]["id"]

        # 使用用户 B 的 Token；类级清理 fixture 会删除用户 A 的分类。
        other = CategoryApi(another_auth_client, config.api_prefix)
        assert_rejected(other.get_category_detail(category_id))
        assert_rejected(other.update_category(category_id, {"name": "无权修改"}))
        assert_rejected(other.delete_category(category_id))

        # 越权请求不能改变分类，用户 A 仍能查询。
        response = category_api.get_category_detail(category_id)
        assert response.status_code == 200, response.text

    @allure.story("分类权限")
    @allure.title("系统分类不能修改或删除")
    def test_system_category_cannot_be_changed(self, category_api):
        """普通用户只能查看系统预置分类。"""
        response = category_api.get_category_list()
        assert response.status_code == 200, response.text
        system_categories = [
            item for item in response.json()["data"] if item["is_system"]
        ]
        assert system_categories, "测试环境缺少系统分类"
        category_id = system_categories[0]["id"]

        assert_rejected(category_api.update_category(category_id, {"name": "无权修改"}))
        assert_rejected(category_api.delete_category(category_id))

    @allure.story("分类查询")
    @allure.title("分类列表按收入支出筛选")
    def test_category_list_filters_type(self, category_api, category_factory):
        """分别创建收入和支出分类，验证筛选结果及非法参数。"""
        ids = []
        # 类级清理 fixture 会记录并删除这两个分类。
        for category_type in ("expense", "income"):
            payload = category_factory.build_category(category_type=category_type)
            response = category_api.create_category(payload)
            assert response.status_code == 200, response.text
            ids.append(response.json()["data"]["id"])

        for category_type, included_id, excluded_id in (
            ("expense", ids[0], ids[1]),
            ("income", ids[1], ids[0]),
        ):
            response = category_api.get_category_list({"category_type": category_type})
            assert response.status_code == 200, response.text
            items = response.json()["data"]
            assert all(item["category_type"] == category_type for item in items)
            returned_ids = {item["id"] for item in items}
            assert included_id in returned_ids
            assert excluded_id not in returned_ids

        assert_rejected(category_api.get_category_list({"category_type": "invalid"}))
