"""商品和价格历史接口测试；每个用例只处理自己创建的商品。"""

import allure
import pytest


@pytest.fixture
def product_ids(product_api):
    """用例结束后，删除仍在列表里的商品。"""

    # ======================================
    # 保存本用例创建的商品 ID
    # ======================================

    ids = []
    yield ids

    # ======================================
    # 用例结束后清理仍在列表中的商品
    # ======================================

    for product_id in ids:
        response = product_api.delete_product(product_id)
        assert response.status_code == 200, response.text


@pytest.fixture
def test_product(product_api, product_factory, product_ids):
    """创建商品，并登记其 ID 供用例结束时清理。"""

    # ======================================
    # 创建商品并登记待清理 ID
    # ======================================

    payload = product_factory.build_product()
    response = product_api.create_product(payload)
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    product_ids.append(data["id"])
    return data


@allure.feature("商品模块")
class TestProduct:
    @allure.story("商品管理")
    @allure.title("新增商品成功")
    def test_create_product_success(self, product_api, product_factory, product_ids):
        """创建商品后核对 ID、名称和品牌。"""

        # ======================================
        # 创建唯一名称的商品
        # ======================================

        payload = product_factory.build_product()
        response = product_api.create_product(payload)
        assert response.status_code == 200, response.text
        result = response.json()
        assert result["code"] == 200
        data = result["data"]
        product_ids.append(data["id"])

        # ======================================
        # 核对返回的商品信息
        # ======================================

        assert data["id"]
        assert data["name"] == payload["name"]
        assert data["brand"] == payload["brand"]

    @allure.story("商品查询")
    @allure.title("商品列表包含当前用户创建的商品")
    def test_get_product_list_success(self, product_api, test_product):
        """列表中应该能找到当前用例创建的商品。"""

        # ======================================
        # 查询商品列表并查找本用例商品
        # ======================================

        response = product_api.get_product_list()
        assert response.status_code == 200, response.text
        items = response.json()["data"]
        ids = {item["id"] for item in items}
        assert test_product["id"] in ids

    @allure.story("商品查询")
    @allure.title("查询商品详情成功")
    def test_get_product_detail_success(self, product_api, test_product):
        """详情返回的 ID 和名称应与创建结果一致。"""

        # ======================================
        # 查询商品详情
        # ======================================

        product_id = test_product["id"]
        response = product_api.get_product_detail(product_id)
        assert response.status_code == 200, response.text
        data = response.json()["data"]

        # 核对详情与创建结果一致。
        assert data["id"] == product_id
        assert data["name"] == test_product["name"]

    @allure.story("商品管理")
    @allure.title("修改商品后详情同步更新")
    def test_update_product_success(self, product_api, test_product):
        """修改分类和备注，再读详情确认后端已保存。"""

        # ======================================
        # 修改商品分类和备注
        # ======================================

        product_id = test_product["id"]
        payload = {"category": "更新后的分类", "note": "已修改"}
        response = product_api.update_product(product_id, payload)
        assert response.status_code == 200, response.text
        assert response.json()["data"]["category"] == payload["category"]

        # ======================================
        # 再查详情，确认修改已保存
        # ======================================

        response = product_api.get_product_detail(product_id)
        assert response.json()["data"]["note"] == payload["note"]

    @allure.story("商品管理")
    @allure.title("删除商品后详情不可查询")
    def test_delete_product_success(self, product_api, test_product, product_ids):
        """逻辑删除后详情不可访问，且不重复清理已删除商品。"""

        # ======================================
        # 删除商品并从自动清理列表中移除
        # ======================================

        product_id = test_product["id"]
        response = product_api.delete_product(product_id)
        assert response.status_code == 200, response.text
        assert response.json()["code"] == 200
        product_ids.remove(product_id)

        # ======================================
        # 再查详情，确认已删除商品不可访问
        # ======================================

        response = product_api.get_product_detail(product_id)
        assert response.status_code in (400, 404), response.text

    @allure.story("商品价格")
    @allure.title("新增商品价格记录成功")
    def test_create_price_record_success(
        self, product_api, product_factory, test_product
    ):
        """新增价格记录时核对返回的金额。"""

        # ======================================
        # 为测试商品新增价格记录
        # ======================================

        payload = product_factory.build_price("99.00")
        product_id = test_product["id"]
        response = product_api.create_price_record(product_id, payload)

        # 验证接口成功，并核对返回金额。
        assert response.status_code == 200, response.text
        assert response.json()["code"] == 200
        assert response.json()["data"]["price"] == "99.00"

    @allure.story("商品价格")
    @allure.title("查询商品价格历史及最高最低价")
    def test_get_price_records_success(
        self, product_api, product_factory, test_product
    ):
        """录入两笔价格，检查历史数量及价格汇总。"""

        # ======================================
        # 为同一商品新增两条不同价格记录
        # ======================================

        product_id = test_product["id"]
        for price in ("99.00", "129.00"):
            payload = product_factory.build_price(price)
            response = product_api.create_price_record(product_id, payload)
            assert response.status_code == 200, response.text

        # ======================================
        # 查询价格历史并核对最高最低价
        # ======================================

        response = product_api.get_price_records(product_id)
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["record_count"] == 2
        assert data["lowest_price"] == "99.00"
        assert data["highest_price"] == "129.00"
        assert len(data["records"]) == 2
