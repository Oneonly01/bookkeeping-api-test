import allure
import pytest

from common.budget_api import BudgetApi
from utils.assertions import assert_rejected


@allure.feature("预算管理")
class TestBudget:

    @allure.story("创建预算")
    @allure.title("创建总预算成功")
    def test_create_overall_budget_success(
        self,
        budget_api,
        budget_factory,
    ):
        """
        验证创建总预算成功。

        测试流程：

        1. 查询当前预算列表；
        2. 收集已经存在的总预算年月；
        3. 自动寻找一个未被占用的年月；
        4. 创建总预算；
        5. 验证返回结果；
        6. 删除测试预算。

        这样可以避免因为固定年月已经存在预算，
        导致自动化用例重复执行失败。
        """

        # ======================================
        # 初始化预算 ID
        # ======================================

        budget_id = None

        try:
            # ==================================
            # 查询当前预算列表
            # ==================================

            list_response = budget_api.get_budget_list()

            assert list_response.status_code == 200, (
                f"查询预算列表失败，"
                f"status_code="
                f"{list_response.status_code}，"
                f"response="
                f"{list_response.text}"
            )

            list_response_data = list_response.json()

            assert list_response_data.get("code") == 200, (
                f"查询预算列表业务失败：" f"{list_response_data}"
            )

            # ==================================
            # 获取预算列表
            # ==================================

            budget_list = list_response_data.get(
                "data",
                [],
            )

            # ==================================
            # 兼容分页结构
            # ======================================

            if isinstance(
                budget_list,
                dict,
            ):
                budget_list = budget_list.get(
                    "results",
                    budget_list.get(
                        "items",
                        budget_list.get(
                            "budgets",
                            [],
                        ),
                    ),
                )

            assert isinstance(
                budget_list,
                list,
            ), (
                f"预算列表结构错误：" f"{list_response_data}"
            )

            # ==================================
            # 收集已有总预算年月
            # ======================================

            existing_overall_periods = set()

            for item in budget_list:

                if item.get("budget_type") == "overall":
                    year = item.get("year")

                    month = item.get("month")

                    if year is not None and month is not None:
                        existing_overall_periods.add(
                            (
                                int(year),
                                int(month),
                            )
                        )

            # ==================================
            # 自动寻找未被占用的年月
            # ======================================
            #
            # 从 2027 年开始往后寻找。
            #
            # 最多扫描到 2036 年，
            # 足够自动化测试使用。
            #
            # ======================================

            target_year = None
            target_month = None

            for year in range(
                2027,
                2037,
            ):
                for month in range(
                    1,
                    13,
                ):
                    if (
                        year,
                        month,
                    ) not in existing_overall_periods:

                        target_year = year
                        target_month = month

                        break

                if target_year is not None:
                    break

            # ==================================
            # 必须成功找到可用年月
            # ======================================

            assert target_year is not None and target_month is not None, (
                "未找到可用于创建总预算的" "空闲年月"
            )

            # ==================================
            # 构造预算数据
            # ======================================

            payload = budget_factory.build_budget(
                budget_type="overall",
                year=target_year,
                month=target_month,
                amount="1000.00",
                alert_threshold="80.00",
                note="自动化测试总预算",
            )

            # ==================================
            # 创建总预算
            # ======================================

            response = budget_api.create_budget(payload)

            # ==================================
            # HTTP 状态码断言
            # ======================================

            assert response.status_code == 200, (
                f"创建总预算失败，"
                f"status_code="
                f"{response.status_code}，"
                f"response="
                f"{response.text}"
            )

            # ==================================
            # 解析响应
            # ======================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ======================================

            assert response_data.get("code") == 200, (
                f"创建总预算业务失败：" f"{response_data}"
            )

            # ==================================
            # 获取预算数据
            # ======================================

            budget_data = response_data.get(
                "data",
                {},
            )

            assert isinstance(
                budget_data,
                dict,
            ), (
                f"预算创建响应结构错误：" f"{response_data}"
            )

            # ==================================
            # 获取预算 ID
            # ======================================

            budget_id = budget_data.get("id")

            assert budget_id, f"创建总预算后" f"未返回 budget_id：" f"{response_data}"

            # ==================================
            # 预算类型断言
            # ======================================

            assert budget_data.get("budget_type") == "overall"

            # ==================================
            # 年份断言
            # ======================================

            assert int(budget_data.get("year")) == target_year

            # ==================================
            # 月份断言
            # ======================================

            assert int(budget_data.get("month")) == target_month

            # ==================================
            # 金额断言
            # ======================================

            assert str(budget_data.get("amount")) == "1000.00"

        finally:
            # ==================================
            # 清理测试预算
            # ======================================

            if budget_id:

                delete_response = budget_api.delete_budget(budget_id)

                if delete_response.status_code != 200:
                    print(
                        f"总预算测试数据"
                        f"清理失败，"
                        f"budget_id="
                        f"{budget_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("创建预算")
    @allure.title("创建分类预算成功")
    def test_create_category_budget_success(
        self,
        budget_api,
        budget_factory,
        transaction_context,
    ):
        """
        验证创建分类预算成功。

        测试场景：

            budget_type = category

        分类预算必须绑定一个有效分类。

        测试流程：

        1. 获取有效支出分类；
        2. 查询现有预算；
        3. 自动寻找该分类未被占用的年月；
        4. 创建分类预算；
        5. 验证返回结果；
        6. 删除测试预算。

        这样可以避免：

            同一分类
            同一年
            同一个月

        已经存在预算时造成测试数据冲突。
        """

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        category_id = expense_category.get("id")

        category_name = expense_category.get("name")

        assert category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 初始化预算 ID
        # ======================================

        budget_id = None

        try:
            # ==================================
            # 查询已有预算
            # ==================================

            list_response = budget_api.get_budget_list()

            assert list_response.status_code == 200, (
                f"查询预算列表失败，"
                f"status_code="
                f"{list_response.status_code}，"
                f"response="
                f"{list_response.text}"
            )

            list_response_data = list_response.json()

            assert list_response_data.get("code") == 200, (
                f"查询预算列表业务失败：" f"{list_response_data}"
            )

            # ==================================
            # 获取预算列表
            # ==================================

            budget_list = list_response_data.get(
                "data",
                [],
            )

            # ==================================
            # 兼容分页结构
            # ==================================

            if isinstance(
                budget_list,
                dict,
            ):
                budget_list = budget_list.get(
                    "results",
                    budget_list.get(
                        "items",
                        budget_list.get(
                            "budgets",
                            [],
                        ),
                    ),
                )

            assert isinstance(
                budget_list,
                list,
            ), (
                f"预算列表结构错误：" f"{list_response_data}"
            )

            # ==================================
            # 收集当前分类已有预算年月
            # ======================================

            existing_periods = set()

            for item in budget_list:

                if item.get("budget_type") != "category":
                    continue

                # ==================================
                # 后端返回分类字段结构
                # 可能存在以下形式：
                #
                # category_id
                #
                # 或：
                #
                # category
                #
                # ==================================

                item_category_id = item.get("category_id")

                if item_category_id is None:
                    item_category_id = item.get("category")

                # ==================================
                # category 也可能是对象
                # ==================================

                if isinstance(
                    item_category_id,
                    dict,
                ):
                    item_category_id = item_category_id.get("id")

                if item_category_id is None or int(item_category_id) != int(
                    category_id
                ):
                    continue

                year = item.get("year")

                month = item.get("month")

                if year is not None and month is not None:
                    existing_periods.add(
                        (
                            int(year),
                            int(month),
                        )
                    )

            # ==================================
            # 自动寻找未使用年月
            # ======================================

            target_year = None
            target_month = None

            for year in range(
                2027,
                2037,
            ):
                for month in range(
                    1,
                    13,
                ):
                    if (
                        year,
                        month,
                    ) not in existing_periods:

                        target_year = year
                        target_month = month
                        break

                if target_year is not None:
                    break

            assert target_year is not None and target_month is not None, (
                "未找到可用于创建分类预算的" "空闲年月"
            )

            # ==================================
            # 构造分类预算请求数据
            # ======================================

            payload = budget_factory.build_budget(
                budget_type="category",
                year=target_year,
                month=target_month,
                amount="500.00",
                category_id=category_id,
                alert_threshold="80.00",
                note="自动化测试分类预算",
            )

            # ==================================
            # 创建分类预算
            # ======================================

            response = budget_api.create_budget(payload)

            # ==================================
            # HTTP 状态码断言
            # ======================================

            assert response.status_code == 200, (
                f"创建分类预算失败，"
                f"status_code="
                f"{response.status_code}，"
                f"response="
                f"{response.text}"
            )

            # ==================================
            # 解析响应
            # ======================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ======================================

            assert response_data.get("code") == 200, (
                f"创建分类预算业务失败：" f"{response_data}"
            )

            # ==================================
            # 获取预算数据
            # ======================================

            budget_data = response_data.get(
                "data",
                {},
            )

            assert isinstance(
                budget_data,
                dict,
            ), (
                f"创建分类预算返回结构错误：" f"{response_data}"
            )

            # ==================================
            # 获取预算 ID
            # ======================================

            budget_id = budget_data.get("id")

            assert budget_id, f"创建分类预算后" f"未返回 budget_id：" f"{response_data}"

            # ==================================
            # 预算类型断言
            # ======================================

            assert budget_data.get("budget_type") == "category"

            # ==================================
            # 年份断言
            # ======================================

            assert int(budget_data.get("year")) == target_year

            # ==================================
            # 月份断言
            # ======================================

            assert int(budget_data.get("month")) == target_month

            # ==================================
            # 金额断言
            # ======================================

            assert str(budget_data.get("amount")) == "500.00"

            # ==================================
            # 分类 ID 断言
            # ======================================
            #
            # 兼容后端可能返回：
            #
            # category_id: 1
            #
            # 或：
            #
            # category: 1
            #
            # 或：
            #
            # category: {
            #     "id": 1,
            #     "name": "餐饮"
            # }
            #
            # ======================================

            actual_category = budget_data.get("category_id")

            if actual_category is None:
                actual_category = budget_data.get("category")

            if isinstance(
                actual_category,
                dict,
            ):

                actual_category_id = actual_category.get("id")

                # ==================================
                # 如果返回分类名称，
                # 顺便验证名称
                # ==================================

                actual_category_name = actual_category.get("name")

                if actual_category_name:
                    assert actual_category_name == category_name

            else:
                actual_category_id = actual_category

            assert int(actual_category_id) == int(category_id), (
                f"分类预算 category_id 错误，"
                f"expected="
                f"{category_id}，"
                f"actual="
                f"{actual_category_id}"
            )

        finally:
            # ==================================
            # 清理测试预算
            # ======================================

            if budget_id:

                delete_response = budget_api.delete_budget(budget_id)

                if delete_response.status_code != 200:
                    print(
                        f"分类预算测试数据"
                        f"清理失败，"
                        f"budget_id="
                        f"{budget_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("查询预算")
    @allure.title("查询预算详情成功")
    def test_get_budget_detail_success(
        self,
        budget_api,
        budget_factory,
    ):
        """
        验证查询预算详情成功。

        测试流程：

        1. 创建一个测试总预算；
        2. 获取 budget_id；
        3. 查询预算详情；
        4. 验证返回状态；
        5. 验证详情字段；
        6. 清理测试预算。
        """

        # ======================================
        # 初始化预算 ID
        # ======================================

        budget_id = None

        try:
            # ==================================
            # 先查询现有预算
            # ==================================
            #
            # 自动寻找一个未被占用的年月，
            # 避免和已有总预算冲突。
            #
            # ==================================

            list_response = budget_api.get_budget_list()

            assert list_response.status_code == 200, (
                f"查询预算列表失败，" f"response=" f"{list_response.text}"
            )

            list_response_data = list_response.json()

            assert list_response_data.get("code") == 200

            budget_list = list_response_data.get(
                "data",
                [],
            )

            # ==================================
            # 兼容分页结构
            # ==================================

            if isinstance(
                budget_list,
                dict,
            ):
                budget_list = budget_list.get(
                    "results",
                    budget_list.get(
                        "items",
                        budget_list.get(
                            "budgets",
                            [],
                        ),
                    ),
                )

            assert isinstance(
                budget_list,
                list,
            )

            # ==================================
            # 收集已有总预算年月
            # ==================================

            existing_periods = set()

            for item in budget_list:

                if item.get("budget_type") != "overall":
                    continue

                year = item.get("year")

                month = item.get("month")

                if year is not None and month is not None:
                    existing_periods.add(
                        (
                            int(year),
                            int(month),
                        )
                    )

            # ==================================
            # 自动寻找空闲年月
            # ==================================

            target_year = None
            target_month = None

            for year in range(
                2027,
                2037,
            ):
                for month in range(
                    1,
                    13,
                ):
                    if (
                        year,
                        month,
                    ) not in existing_periods:

                        target_year = year
                        target_month = month
                        break

                if target_year is not None:
                    break

            assert target_year is not None and target_month is not None, (
                "未找到可用于详情查询测试的" "空闲年月"
            )

            # ==================================
            # 构造测试预算
            # ==================================

            payload = budget_factory.build_budget(
                budget_type="overall",
                year=target_year,
                month=target_month,
                amount="1200.00",
                alert_threshold="80.00",
                note="自动化测试-预算详情",
            )

            # ==================================
            # 创建测试预算
            # ==================================

            create_response = budget_api.create_budget(payload)

            assert create_response.status_code == 200, (
                f"创建详情测试预算失败，" f"response=" f"{create_response.text}"
            )

            create_response_data = create_response.json()

            assert create_response_data.get("code") == 200

            create_data = create_response_data.get(
                "data",
                {},
            )

            budget_id = create_data.get("id")

            assert budget_id, f"创建预算后未返回 budget_id：" f"{create_response_data}"

            # ==================================
            # 查询预算详情
            # ==================================

            detail_response = budget_api.get_budget_detail(budget_id)

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert detail_response.status_code == 200, (
                f"查询预算详情失败，"
                f"status_code="
                f"{detail_response.status_code}，"
                f"response="
                f"{detail_response.text}"
            )

            # ==================================
            # 解析响应
            # ==================================

            detail_response_data = detail_response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert detail_response_data.get("code") == 200, (
                f"查询预算详情业务失败：" f"{detail_response_data}"
            )

            # ==================================
            # 获取详情数据
            # ==================================

            detail_data = detail_response_data.get(
                "data",
                {},
            )

            assert isinstance(
                detail_data,
                dict,
            ), (
                f"预算详情 data 结构错误：" f"{detail_response_data}"
            )

            # ==================================
            # ID 断言
            # ==================================

            assert detail_data.get("id") == budget_id, (
                f"预算 ID 不一致，"
                f"expected="
                f"{budget_id}，"
                f"actual="
                f"{detail_data.get('id')}"
            )

            # ==================================
            # 类型断言
            # ==================================

            assert detail_data.get("budget_type") == "overall"

            # ==================================
            # 年份断言
            # ==================================

            assert int(detail_data.get("year")) == target_year

            # ==================================
            # 月份断言
            # ==================================

            assert int(detail_data.get("month")) == target_month

            # ==================================
            # 金额断言
            # ==================================

            assert str(detail_data.get("amount")) == "1200.00"

            # ==================================
            # 提醒阈值断言
            # ======================================

            if detail_data.get("alert_threshold") is not None:
                assert str(detail_data.get("alert_threshold")) == "80.00"

            # ==================================
            # 备注断言
            # ======================================

            if "note" in detail_data:
                assert detail_data.get("note") == "自动化测试-预算详情"

        finally:
            # ==================================
            # 清理测试预算
            # ==================================

            if budget_id:

                delete_response = budget_api.delete_budget(budget_id)

                if delete_response.status_code != 200:
                    print(
                        f"预算详情测试数据"
                        f"清理失败，"
                        f"budget_id="
                        f"{budget_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("修改预算")
    @allure.title("修改预算成功")
    def test_update_budget_success(
        self,
        budget_api,
        budget_factory,
    ):
        """
        验证修改预算成功。

        后端当前允许修改字段：

        1. amount
            预算金额；

        2. alert_threshold
            提醒阈值；

        3. note
            备注；

        4. is_active
            是否启用。

        不允许修改：

            budget_type
            year
            month
            category_id

        测试流程：

        1. 查询当前预算列表；
        2. 自动寻找一个未被占用的年月；
        3. 创建一个测试总预算；
        4. 修改 amount；
        5. 修改 alert_threshold；
        6. 修改 note；
        7. 修改 is_active；
        8. 验证更新接口返回；
        9. 再次查询预算详情；
        10. 验证修改后的数据已经真正保存；
        11. 验证不可修改字段没有发生变化；
        12. 删除测试预算。
        """

        # ======================================
        # 初始化预算 ID
        # ======================================

        budget_id = None

        try:
            # ==================================
            # 查询当前预算列表
            # ======================================
            #
            # 因为：
            #
            # 同一个用户
            # 同一年
            # 同一个月
            #
            # 只能存在一个 overall 总预算，
            #
            # 所以不能直接把年月写死。
            #
            # ==================================

            list_response = budget_api.get_budget_list()

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert list_response.status_code == 200, (
                f"查询预算列表失败，"
                f"status_code="
                f"{list_response.status_code}，"
                f"response="
                f"{list_response.text}"
            )

            # ==================================
            # 解析响应
            # ==================================

            list_response_data = list_response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert list_response_data.get("code") == 200, (
                f"查询预算列表业务失败：" f"{list_response_data}"
            )

            # ==================================
            # 获取预算列表
            # ==================================

            budget_list = list_response_data.get(
                "data",
                [],
            )

            # ==================================
            # 兼容分页结构
            # ======================================
            #
            # 后端可能返回：
            #
            # data: [...]
            #
            # 或：
            #
            # data: {
            #     "results": [...]
            # }
            #
            # 或：
            #
            # data: {
            #     "items": [...]
            # }
            #
            # 或：
            #
            # data: {
            #     "budgets": [...]
            # }
            #
            # ==================================

            if isinstance(
                budget_list,
                dict,
            ):
                budget_list = budget_list.get(
                    "results",
                    budget_list.get(
                        "items",
                        budget_list.get(
                            "budgets",
                            [],
                        ),
                    ),
                )

            # ==================================
            # 列表结构断言
            # ==================================

            assert isinstance(
                budget_list,
                list,
            ), (
                f"预算列表结构错误：" f"{list_response_data}"
            )

            # ==================================
            # 收集已有总预算年月
            # ======================================

            existing_periods = set()

            for item in budget_list:

                # ==================================
                # 只处理 overall 总预算
                # ==================================

                if item.get("budget_type") != "overall":
                    continue

                year = item.get("year")

                month = item.get("month")

                # ==================================
                # 年月有效才加入集合
                # ==================================

                if year is not None and month is not None:
                    existing_periods.add(
                        (
                            int(year),
                            int(month),
                        )
                    )

            # ==================================
            # 自动寻找空闲年月
            # ======================================
            #
            # 从 2027 年开始扫描。
            #
            # 找到第一个没有总预算的月份。
            #
            # ==================================

            target_year = None
            target_month = None

            for year in range(
                2027,
                2037,
            ):
                for month in range(
                    1,
                    13,
                ):
                    if (
                        year,
                        month,
                    ) not in existing_periods:

                        target_year = year
                        target_month = month

                        break

                if target_year is not None:
                    break

            # ==================================
            # 必须找到可用年月
            # ==================================

            assert target_year is not None and target_month is not None, (
                "未找到可用于修改预算测试的" "空闲年月"
            )

            # ==================================
            # 构造创建预算请求数据
            # ======================================
            #
            # 创建时需要：
            #
            # budget_type
            # year
            # month
            # amount
            #
            # 可选：
            #
            # alert_threshold
            # note
            #
            # ==================================

            create_payload = budget_factory.build_budget(
                budget_type="overall",
                year=target_year,
                month=target_month,
                amount="1000.00",
                alert_threshold="80.00",
                note="自动化测试-修改预算前",
            )

            # ==================================
            # 创建测试预算
            # ==================================

            create_response = budget_api.create_budget(create_payload)

            # ==================================
            # 创建 HTTP 状态码断言
            # ==================================

            assert create_response.status_code == 200, (
                f"创建修改预算测试数据失败，"
                f"status_code="
                f"{create_response.status_code}，"
                f"response="
                f"{create_response.text}"
            )

            # ==================================
            # 解析创建响应
            # ==================================

            create_response_data = create_response.json()

            # ==================================
            # 创建业务状态码断言
            # ==================================

            assert create_response_data.get("code") == 200, (
                f"创建修改预算测试数据" f"业务失败：" f"{create_response_data}"
            )

            # ==================================
            # 获取创建后的预算数据
            # ==================================

            create_data = create_response_data.get(
                "data",
                {},
            )

            assert isinstance(
                create_data,
                dict,
            ), (
                f"创建预算返回 data " f"结构错误：" f"{create_response_data}"
            )

            # ==================================
            # 获取 budget_id
            # ==================================

            budget_id = create_data.get("id")

            assert budget_id, (
                f"创建测试预算后" f"未返回 budget_id：" f"{create_response_data}"
            )

            # ==================================
            # 保存修改前的重要数据
            # ======================================
            #
            # 后续修改完成以后，
            # 用于确认这些不允许修改的字段
            # 没有发生变化。
            #
            # ==================================

            original_budget_type = create_data.get("budget_type")

            original_year = create_data.get("year")

            original_month = create_data.get("month")

            original_category_id = create_data.get("category_id")

            # ==================================
            # 构造修改请求
            # ======================================
            #
            # 后端当前只允许修改：
            #
            # amount
            # alert_threshold
            # note
            # is_active
            #
            # 所以这里绝对不传：
            #
            # budget_type
            # year
            # month
            # category_id
            #
            # ==================================

            update_payload = {
                "amount": "1800.00",
                "alert_threshold": "90.00",
                "note": "自动化测试-修改预算后",
                "is_active": False,
            }

            # ==================================
            # 修改预算
            # ==================================

            update_response = budget_api.update_budget(
                budget_id,
                update_payload,
            )

            # ==================================
            # 修改 HTTP 状态码断言
            # ==================================

            assert update_response.status_code == 200, (
                f"修改预算失败，"
                f"status_code="
                f"{update_response.status_code}，"
                f"response="
                f"{update_response.text}"
            )

            # ==================================
            # 解析修改响应
            # ==================================

            update_response_data = update_response.json()

            # ==================================
            # 修改业务状态码断言
            # ==================================

            assert update_response_data.get("code") == 200, (
                f"修改预算业务失败：" f"{update_response_data}"
            )

            # ==================================
            # 获取修改后的返回数据
            # ==================================

            update_data = update_response_data.get(
                "data",
                {},
            )

            assert isinstance(
                update_data,
                dict,
            ), (
                f"修改预算返回 data " f"结构错误：" f"{update_response_data}"
            )

            # ==================================
            # budget_id 不能变化
            # ==================================

            assert update_data.get("id") == budget_id, (
                f"修改预算后 ID 发生变化，"
                f"expected="
                f"{budget_id}，"
                f"actual="
                f"{update_data.get('id')}"
            )

            # ==================================
            # amount 修改断言
            # ==================================

            assert str(update_data.get("amount")) == "1800.00", (
                f"预算金额修改失败，"
                f"expected=1800.00，"
                f"actual="
                f"{update_data.get('amount')}"
            )

            # ==================================
            # alert_threshold 修改断言
            # ==================================

            assert str(update_data.get("alert_threshold")) == "90.00", (
                f"预算提醒阈值修改失败，"
                f"expected=90.00，"
                f"actual="
                f"{update_data.get('alert_threshold')}"
            )

            # ==================================
            # note 修改断言
            # ==================================

            assert update_data.get("note") == "自动化测试-修改预算后", (
                f"预算备注修改失败，" f"actual=" f"{update_data.get('note')}"
            )

            # ==================================
            # is_active 修改断言
            # ==================================

            assert update_data.get("is_active") is False, (
                f"预算启用状态修改失败，"
                f"expected=False，"
                f"actual="
                f"{update_data.get('is_active')}"
            )

            # ==================================
            # 再次查询预算详情
            # ======================================
            #
            # 只验证 PUT 返回 200 不够。
            #
            # 必须重新 GET，
            # 确认数据库里的真实结果。
            #
            # ==================================

            detail_response = budget_api.get_budget_detail(budget_id)

            # ==================================
            # 详情 HTTP 状态码断言
            # ==================================

            assert detail_response.status_code == 200, (
                f"修改预算后查询详情失败，"
                f"status_code="
                f"{detail_response.status_code}，"
                f"response="
                f"{detail_response.text}"
            )

            # ==================================
            # 解析详情响应
            # ==================================

            detail_response_data = detail_response.json()

            # ==================================
            # 详情业务状态码断言
            # ==================================

            assert detail_response_data.get("code") == 200, (
                f"修改预算后查询详情" f"业务失败：" f"{detail_response_data}"
            )

            # ==================================
            # 获取详情数据
            # ==================================

            detail_data = detail_response_data.get(
                "data",
                {},
            )

            assert isinstance(
                detail_data,
                dict,
            ), (
                f"预算详情 data " f"结构错误：" f"{detail_response_data}"
            )

            # ==================================
            # ID 断言
            # ==================================

            assert detail_data.get("id") == budget_id

            # ==================================
            # 数据库最终 amount 断言
            # ==================================

            assert str(detail_data.get("amount")) == "1800.00", (
                f"预算修改后数据库金额错误，"
                f"expected=1800.00，"
                f"actual="
                f"{detail_data.get('amount')}"
            )

            # ==================================
            # 数据库最终提醒阈值断言
            # ==================================

            assert str(detail_data.get("alert_threshold")) == "90.00", (
                f"预算修改后数据库提醒阈值错误，"
                f"expected=90.00，"
                f"actual="
                f"{detail_data.get('alert_threshold')}"
            )

            # ==================================
            # 数据库最终备注断言
            # ==================================

            assert detail_data.get("note") == "自动化测试-修改预算后", (
                f"预算修改后数据库备注错误，" f"actual=" f"{detail_data.get('note')}"
            )

            # ==================================
            # 数据库最终启用状态断言
            # ==================================

            assert detail_data.get("is_active") is False, (
                f"预算修改后数据库启用状态错误，"
                f"expected=False，"
                f"actual="
                f"{detail_data.get('is_active')}"
            )

            # ==================================
            # 不允许修改字段验证
            # ======================================
            #
            # 即使更新接口只传了可修改字段，
            # 仍然需要确认：
            #
            # budget_type
            # year
            # month
            #
            # 没有受到影响。
            #
            # ==================================

            assert detail_data.get("budget_type") == original_budget_type, (
                f"修改预算后 budget_type "
                f"发生变化，"
                f"before="
                f"{original_budget_type}，"
                f"after="
                f"{detail_data.get('budget_type')}"
            )

            assert int(detail_data.get("year")) == int(original_year), (
                f"修改预算后 year "
                f"发生变化，"
                f"before="
                f"{original_year}，"
                f"after="
                f"{detail_data.get('year')}"
            )

            assert int(detail_data.get("month")) == int(original_month), (
                f"修改预算后 month "
                f"发生变化，"
                f"before="
                f"{original_month}，"
                f"after="
                f"{detail_data.get('month')}"
            )

            # ==================================
            # 总预算 category_id 验证
            # ======================================
            #
            # overall 总预算正常情况下
            # category_id 应该是 None。
            #
            # 如果接口返回了这个字段，
            # 则确认修改前后保持一致。
            #
            # ==================================

            if "category_id" in detail_data:
                assert detail_data.get("category_id") == original_category_id, (
                    f"修改预算后 category_id "
                    f"发生变化，"
                    f"before="
                    f"{original_category_id}，"
                    f"after="
                    f"{detail_data.get('category_id')}"
                )

        finally:
            # ==================================
            # 清理测试预算
            # ======================================
            #
            # 无论中途哪个断言失败，
            # 只要预算已经创建成功，
            # 都尽量删除测试数据。
            #
            # ==================================

            if budget_id:

                delete_response = budget_api.delete_budget(budget_id)

                # ==================================
                # 清理失败不直接覆盖原测试异常
                # ==================================

                if delete_response.status_code != 200:
                    print(
                        f"修改预算测试数据"
                        f"清理失败，"
                        f"budget_id="
                        f"{budget_id}，"
                        f"status_code="
                        f"{delete_response.status_code}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("删除预算")
    @allure.title("删除预算成功且删除后不可查询")
    def test_delete_budget_success(
        self,
        budget_api,
        budget_factory,
    ):
        """
        验证删除预算成功。

        测试流程：

        1. 查询当前预算列表；
        2. 自动寻找一个未被占用的年月；
        3. 创建一个测试总预算；
        4. 删除该预算；
        5. 验证删除接口返回成功；
        6. 再次查询预算详情；
        7. 验证已删除预算不可继续查询。

        测试重点：

        不能只验证 DELETE 返回成功，
        还需要再次查询详情确认预算确实已经删除。
        """

        # ======================================
        # 初始化预算 ID
        # ======================================

        budget_id = None

        # ======================================
        # 标记预算是否已经主动删除
        # ======================================
        #
        # 如果测试已经执行完 DELETE，
        # finally 中就不要重复删除。
        #
        # ======================================

        budget_deleted = False

        try:
            # ==================================
            # 查询当前预算列表
            # ==================================

            list_response = budget_api.get_budget_list()

            assert list_response.status_code == 200, (
                f"查询预算列表失败，"
                f"status_code="
                f"{list_response.status_code}，"
                f"response="
                f"{list_response.text}"
            )

            # ==================================
            # 解析列表响应
            # ==================================

            list_response_data = list_response.json()

            assert list_response_data.get("code") == 200, (
                f"查询预算列表业务失败：" f"{list_response_data}"
            )

            # ==================================
            # 获取预算列表
            # ==================================

            budget_list = list_response_data.get(
                "data",
                [],
            )

            # ==================================
            # 兼容分页结构
            # ==================================

            if isinstance(
                budget_list,
                dict,
            ):
                budget_list = budget_list.get(
                    "results",
                    budget_list.get(
                        "items",
                        budget_list.get(
                            "budgets",
                            [],
                        ),
                    ),
                )

            assert isinstance(
                budget_list,
                list,
            ), (
                f"预算列表结构错误：" f"{list_response_data}"
            )

            # ==================================
            # 收集已有总预算年月
            # ==================================

            existing_periods = set()

            for item in budget_list:

                if item.get("budget_type") != "overall":
                    continue

                year = item.get("year")

                month = item.get("month")

                if year is not None and month is not None:
                    existing_periods.add(
                        (
                            int(year),
                            int(month),
                        )
                    )

            # ==================================
            # 自动寻找未占用年月
            # ==================================

            target_year = None
            target_month = None

            for year in range(
                2027,
                2037,
            ):
                for month in range(
                    1,
                    13,
                ):
                    if (
                        year,
                        month,
                    ) not in existing_periods:

                        target_year = year
                        target_month = month

                        break

                if target_year is not None:
                    break

            assert target_year is not None and target_month is not None, (
                "未找到可用于删除预算测试的" "空闲年月"
            )

            # ==================================
            # 构造测试预算
            # ==================================

            payload = budget_factory.build_budget(
                budget_type="overall",
                year=target_year,
                month=target_month,
                amount="888.88",
                alert_threshold="80.00",
                note="自动化测试-删除预算",
            )

            # ==================================
            # 创建测试预算
            # ==================================

            create_response = budget_api.create_budget(payload)

            assert create_response.status_code == 200, (
                f"创建删除测试预算失败，"
                f"status_code="
                f"{create_response.status_code}，"
                f"response="
                f"{create_response.text}"
            )

            create_response_data = create_response.json()

            assert create_response_data.get("code") == 200, (
                f"创建删除测试预算业务失败：" f"{create_response_data}"
            )

            # ==================================
            # 获取 budget_id
            # ==================================

            budget_id = create_response_data.get(
                "data",
                {},
            ).get("id")

            assert budget_id, (
                f"创建删除测试预算后" f"未返回 budget_id：" f"{create_response_data}"
            )

            # ==================================
            # 删除预算
            # ==================================

            delete_response = budget_api.delete_budget(budget_id)

            # ==================================
            # DELETE HTTP 状态码断言
            # ======================================

            assert delete_response.status_code == 200, (
                f"删除预算失败，"
                f"status_code="
                f"{delete_response.status_code}，"
                f"response="
                f"{delete_response.text}"
            )

            # ==================================
            # 解析删除响应
            # ==================================

            delete_response_data = delete_response.json()

            # ==================================
            # 删除业务状态码断言
            # ==================================

            assert delete_response_data.get("code") == 200, (
                f"删除预算业务失败：" f"{delete_response_data}"
            )

            # ==================================
            # 标记已经删除
            # ==================================

            budget_deleted = True

            # ==================================
            # 删除后再次查询详情
            # ======================================

            detail_response = budget_api.get_budget_detail(budget_id)

            # ==================================
            # 删除后不能继续正常查询
            # ======================================
            #
            # 后端可能返回：
            #
            # 404
            # 400
            #
            # 具体取决于你的统一异常处理。
            #
            # 当前先验证：
            #
            # 不能返回 200。
            #
            # ======================================

            assert detail_response.status_code != 200, (
                f"预算已经删除，"
                f"但详情接口仍然返回成功，"
                f"budget_id="
                f"{budget_id}，"
                f"response="
                f"{detail_response.text}"
            )

            # ==================================
            # 解析删除后详情响应
            # ======================================

            detail_response_data = detail_response.json()

            # ==================================
            # 业务状态码也不能成功
            # ==================================

            assert detail_response_data.get("code") != 200, (
                f"预算已经删除，" f"但业务状态仍然返回成功：" f"{detail_response_data}"
            )

            # ==================================
            # 删除后不应该返回有效预算数据
            # ==================================

            deleted_data = detail_response_data.get("data")

            if isinstance(
                deleted_data,
                dict,
            ):
                assert not deleted_data.get("id"), (
                    f"预算删除后仍然返回有效数据：" f"{detail_response_data}"
                )

        finally:
            # ==================================
            # 异常情况下清理测试预算
            # ======================================
            #
            # 如果测试在真正 DELETE 之前失败，
            # budget_deleted=False，
            # 此时尝试清理预算。
            #
            # 如果预算已经删除成功，
            # 不再重复删除。
            #
            # ==================================

            if budget_id and not budget_deleted:

                cleanup_response = budget_api.delete_budget(budget_id)

                if cleanup_response.status_code != 200:
                    print(
                        f"删除预算测试数据"
                        f"清理失败，"
                        f"budget_id="
                        f"{budget_id}，"
                        f"status_code="
                        f"{cleanup_response.status_code}，"
                        f"response="
                        f"{cleanup_response.text}"
                    )

    @allure.story("预算异常场景")
    @allure.title("重复创建同年月总预算失败")
    def test_create_duplicate_overall_budget_failed(
        self,
        budget_api,
        budget_factory,
    ):
        """
        验证同一个用户在相同年份和月份下，
        不能重复创建 overall 总预算。

        测试流程：

        1. 查询当前预算列表；
        2. 自动寻找一个未被占用的年月；
        3. 创建第一个总预算；
        4. 使用相同年月再次创建第二个总预算；
        5. 验证第二次创建失败；
        6. 验证没有返回新的预算 ID；
        7. 清理第一个测试预算。

        后端业务规则：

            同一个用户
            + 同一年
            + 同一月份
            + overall 总预算

            只能存在一条。
        """

        # ======================================
        # 初始化第一个预算 ID
        # ======================================

        first_budget_id = None

        try:
            # ==================================
            # 查询当前预算列表
            # ==================================

            list_response = budget_api.get_budget_list()

            assert list_response.status_code == 200, (
                f"查询预算列表失败，"
                f"status_code="
                f"{list_response.status_code}，"
                f"response="
                f"{list_response.text}"
            )

            list_response_data = list_response.json()

            assert list_response_data.get("code") == 200, (
                f"查询预算列表业务失败：" f"{list_response_data}"
            )

            # ==================================
            # 获取预算列表
            # ==================================

            budget_list = list_response_data.get(
                "data",
                [],
            )

            # ==================================
            # 兼容分页结构
            # ==================================

            if isinstance(
                budget_list,
                dict,
            ):
                budget_list = budget_list.get(
                    "results",
                    budget_list.get(
                        "items",
                        budget_list.get(
                            "budgets",
                            [],
                        ),
                    ),
                )

            assert isinstance(
                budget_list,
                list,
            ), (
                f"预算列表结构错误：" f"{list_response_data}"
            )

            # ==================================
            # 收集已经存在的总预算年月
            # ==================================

            existing_periods = set()

            for item in budget_list:

                if item.get("budget_type") != "overall":
                    continue

                year = item.get("year")

                month = item.get("month")

                if year is not None and month is not None:
                    existing_periods.add(
                        (
                            int(year),
                            int(month),
                        )
                    )

            # ==================================
            # 自动寻找一个未占用年月
            # ==================================

            target_year = None
            target_month = None

            for year in range(
                2027,
                2037,
            ):
                for month in range(
                    1,
                    13,
                ):
                    if (
                        year,
                        month,
                    ) not in existing_periods:

                        target_year = year
                        target_month = month
                        break

                if target_year is not None:
                    break

            assert target_year is not None and target_month is not None, (
                "未找到可用于重复预算测试的" "空闲年月"
            )

            # ==================================
            # 构造第一个总预算
            # ==================================

            first_payload = budget_factory.build_budget(
                budget_type="overall",
                year=target_year,
                month=target_month,
                amount="1000.00",
                alert_threshold="80.00",
                note="自动化测试-第一个总预算",
            )

            # ==================================
            # 创建第一个总预算
            # ==================================

            first_response = budget_api.create_budget(first_payload)

            assert first_response.status_code == 200, (
                f"创建第一个总预算失败，"
                f"status_code="
                f"{first_response.status_code}，"
                f"response="
                f"{first_response.text}"
            )

            first_response_data = first_response.json()

            assert first_response_data.get("code") == 200

            first_budget_id = first_response_data.get(
                "data",
                {},
            ).get("id")

            assert first_budget_id, (
                f"创建第一个总预算后" f"未返回 ID：" f"{first_response_data}"
            )

            # ==================================
            # 构造第二个相同年月总预算
            # ======================================
            #
            # 注意：
            #
            # 金额不同
            # 备注不同
            #
            # 但：
            #
            # budget_type
            # year
            # month
            #
            # 完全相同。
            #
            # ==================================

            duplicate_payload = budget_factory.build_budget(
                budget_type="overall",
                year=target_year,
                month=target_month,
                amount="2000.00",
                alert_threshold="90.00",
                note="自动化测试-重复总预算",
            )

            # ==================================
            # 第二次创建
            # ==================================

            duplicate_response = budget_api.create_budget(duplicate_payload)

            # ==================================
            # HTTP 状态码断言
            # ======================================

            assert duplicate_response.status_code == 400, (
                f"重复创建相同年月总预算"
                f"未按预期失败，"
                f"status_code="
                f"{duplicate_response.status_code}，"
                f"response="
                f"{duplicate_response.text}"
            )

            # ==================================
            # 解析响应
            # ==================================

            duplicate_response_data = duplicate_response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert duplicate_response_data.get("code") == 400, (
                f"重复创建总预算业务状态错误：" f"{duplicate_response_data}"
            )

            # ==================================
            # 错误信息断言
            # ======================================

            message = duplicate_response_data.get(
                "message",
                "",
            )

            assert message, (
                f"重复创建总预算失败后" f"未返回错误信息：" f"{duplicate_response_data}"
            )

            # ==================================
            # 根据当前后端真实返回验证
            # ======================================

            assert "已经存在总预算" in message, (
                f"重复总预算错误提示不符合预期，" f"message=" f"{message}"
            )

            # ==================================
            # 失败后不应该返回新预算 ID
            # ======================================

            duplicate_data = duplicate_response_data.get("data")

            if isinstance(
                duplicate_data,
                dict,
            ):
                assert not duplicate_data.get("id"), (
                    f"重复创建总预算失败后"
                    f"不应该返回新的预算 ID："
                    f"{duplicate_response_data}"
                )

        finally:
            # ==================================
            # 清理第一个测试预算
            # ======================================

            if first_budget_id:

                delete_response = budget_api.delete_budget(first_budget_id)

                if delete_response.status_code != 200:
                    print(
                        f"重复预算测试数据"
                        f"清理失败，"
                        f"budget_id="
                        f"{first_budget_id}，"
                        f"status_code="
                        f"{delete_response.status_code}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("预算异常场景")
    @allure.title("分类预算缺少分类ID创建失败")
    def test_create_category_budget_without_category_failed(
        self,
        budget_api,
        budget_factory,
    ):
        """
        验证创建分类预算时，
        如果没有提供 category_id，
        接口必须拒绝创建。

        测试流程：

        1. 构造 category 分类预算；
        2. 不传 category_id；
        3. 调用创建预算接口；
        4. 验证 HTTP 状态码为 400；
        5. 验证业务状态码为 400；
        6. 验证返回错误信息；
        7. 验证没有生成预算 ID。

        业务规则：

            budget_type = overall
                category_id 可以不传

            budget_type = category
                category_id 必须存在
        """

        # ======================================
        # 构造分类预算
        # ======================================
        #
        # 这里故意不传：
        #
        # category_id
        #
        # 用于验证后端分类预算参数校验。
        #
        # ======================================

        payload = budget_factory.build_budget(
            budget_type="category",
            year=2028,
            month=1,
            amount="500.00",
            alert_threshold="80.00",
            note="自动化测试-分类预算缺少分类",
        )

        # ======================================
        # 确认测试数据中没有 category_id
        # ======================================

        assert "category_id" not in payload, (
            f"当前异常测试数据不正确，"
            f"payload 中不应该存在 category_id："
            f"{payload}"
        )

        # ======================================
        # 创建分类预算
        # ======================================

        response = budget_api.create_budget(payload)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 400, (
            f"分类预算缺少 category_id "
            f"未按预期失败，"
            f"status_code="
            f"{response.status_code}，"
            f"response="
            f"{response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 400, (
            f"分类预算缺少 category_id " f"业务状态错误：" f"{response_data}"
        )

        # ======================================
        # 错误信息断言
        # ======================================

        message = response_data.get(
            "message",
            "",
        )

        assert message, (
            f"分类预算缺少 category_id " f"失败后没有返回错误信息：" f"{response_data}"
        )

        # ======================================
        # 不应该返回有效预算数据
        # ======================================

        data = response_data.get("data")

        if isinstance(
            data,
            dict,
        ):
            assert not data.get("id"), (
                f"分类预算缺少 category_id "
                f"失败后不应该返回 budget_id："
                f"{response_data}"
            )

    @allure.story("预算异常场景")
    @allure.title("非法预算类型创建失败")
    def test_create_budget_with_invalid_type_failed(
        self,
        budget_api,
        budget_factory,
    ):
        """
        验证传入非法 budget_type 时，
        创建预算必须失败。

        合法值：

            overall
                总预算

            category
                分类预算

        当前测试故意传入：

            invalid

        测试流程：

        1. 构造非法预算类型请求；
        2. 调用创建预算接口；
        3. 验证 HTTP 状态码为 400；
        4. 验证业务状态码为 400；
        5. 验证返回错误信息；
        6. 验证没有生成有效预算 ID。
        """

        # ======================================
        # 构造非法预算类型数据
        # ======================================

        payload = budget_factory.build_budget(
            budget_type="invalid",
            year=2028,
            month=2,
            amount="1000.00",
            alert_threshold="80.00",
            note="自动化测试-非法预算类型",
        )

        # ======================================
        # 创建预算
        # ======================================

        response = budget_api.create_budget(payload)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 400, (
            f"非法 budget_type "
            f"未按预期失败，"
            f"status_code="
            f"{response.status_code}，"
            f"response="
            f"{response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 400, (
            f"非法 budget_type " f"业务状态错误：" f"{response_data}"
        )

        # ======================================
        # 错误信息断言
        # ======================================

        message = response_data.get(
            "message",
            "",
        )

        assert message, (
            f"非法 budget_type " f"失败后未返回错误信息：" f"{response_data}"
        )

        # ======================================
        # 错误内容断言
        # ======================================
        #
        # 你的 DRF 前面已经返回过：
        #
        # “monthly” 不是合法选项。
        #
        # 所以这里验证错误信息中
        # 包含“不合法”相关内容。
        #
        # ======================================

        assert "不是合法选项" in message or "budget_type" in message, (
            f"非法 budget_type " f"错误提示不符合预期：" f"{message}"
        )

        # ======================================
        # 不应该生成预算 ID
        # ======================================

        data = response_data.get("data")

        if isinstance(
            data,
            dict,
        ):
            assert not data.get("id"), (
                f"非法 budget_type " f"失败后不应该返回 budget_id：" f"{response_data}"
            )

    @allure.story("预算异常场景")
    @allure.title("预算金额为0创建失败")
    def test_create_budget_with_zero_amount_failed(
        self,
        budget_api,
        budget_factory,
    ):
        """
        验证预算金额为 0 时创建失败。

        测试流程：

        1. 构造 amount=0 的总预算；
        2. 调用创建预算接口；
        3. 验证 HTTP 状态码为 400；
        4. 验证业务状态码为 400；
        5. 验证返回错误信息；
        6. 验证没有生成有效预算 ID。
        """

        # ======================================
        # 构造金额为 0 的预算数据
        # ======================================

        payload = budget_factory.build_budget(
            budget_type="overall",
            year=2028,
            month=3,
            amount="0.00",
            alert_threshold="80.00",
            note="自动化测试-预算金额为0",
        )

        # ======================================
        # 创建预算
        # ======================================

        response = budget_api.create_budget(payload)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 400, (
            f"预算金额为 0 "
            f"未按预期失败，"
            f"status_code="
            f"{response.status_code}，"
            f"response="
            f"{response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 400, (
            f"预算金额为 0 " f"业务状态错误：" f"{response_data}"
        )

        # ======================================
        # 错误信息断言
        # ======================================

        message = response_data.get(
            "message",
            "",
        )

        assert message, f"预算金额为 0 " f"失败后未返回错误信息：" f"{response_data}"

        # ======================================
        # 不应该生成有效预算 ID
        # ======================================

        data = response_data.get("data")

        if isinstance(
            data,
            dict,
        ):
            assert not data.get("id"), (
                f"预算金额为 0 " f"失败后不应该返回 budget_id：" f"{response_data}"
            )

    @allure.story("预算异常场景")
    @allure.title("预算金额为负数创建失败")
    def test_create_budget_with_negative_amount_failed(
        self,
        budget_api,
        budget_factory,
    ):
        """
        验证预算金额小于 0 时，
        创建预算必须失败。

        测试流程：

        1. 构造 amount=-100.00 的总预算；
        2. 调用创建预算接口；
        3. 验证 HTTP 状态码为 400；
        4. 验证业务状态码为 400；
        5. 验证返回错误信息；
        6. 验证没有创建有效预算数据。
        """

        # ======================================
        # 构造负数预算金额
        # ======================================

        payload = budget_factory.build_budget(
            budget_type="overall",
            year=2028,
            month=4,
            amount="-100.00",
            alert_threshold="80.00",
            note="自动化测试-预算金额为负数",
        )

        # ======================================
        # 创建预算
        # ======================================

        response = budget_api.create_budget(payload)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 400, (
            f"预算金额为负数"
            f"未按预期失败，"
            f"status_code="
            f"{response.status_code}，"
            f"response="
            f"{response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 400, (
            f"预算金额为负数" f"业务状态错误：" f"{response_data}"
        )

        # ======================================
        # 错误信息断言
        # ======================================

        message = response_data.get(
            "message",
            "",
        )

        assert message, f"预算金额为负数失败后" f"未返回错误信息：" f"{response_data}"

        # ======================================
        # 不应该返回有效预算 ID
        # ======================================

        data = response_data.get("data")

        if isinstance(
            data,
            dict,
        ):
            assert not data.get("id"), (
                f"预算金额为负数失败后" f"不应该返回 budget_id：" f"{response_data}"
            )

    @allure.story("预算异常场景")
    @allure.title("预算月份非法创建失败")
    @pytest.mark.parametrize(
        "month",
        [
            0,
            13,
        ],
    )
    def test_create_budget_with_invalid_month_failed(
        self,
        budget_api,
        budget_factory,
        month,
    ):
        """
        验证预算月份超出合法范围时创建失败。

        合法月份范围：

            1 ～ 12

        当前使用边界值法覆盖：

            month = 0
                小于最小合法值 1

            month = 13
                大于最大合法值 12

        测试流程：

        1. 构造非法月份预算数据；
        2. 调用创建预算接口；
        3. 验证 HTTP 状态码为 400；
        4. 验证业务状态码为 400；
        5. 验证返回错误信息；
        6. 验证没有生成有效预算 ID。
        """

        # ======================================
        # 构造非法月份预算
        # ======================================

        payload = budget_factory.build_budget(
            budget_type="overall",
            year=2028,
            month=month,
            amount="1000.00",
            alert_threshold="80.00",
            note=(f"自动化测试-非法月份-{month}"),
        )

        # ======================================
        # 创建预算
        # ======================================

        response = budget_api.create_budget(payload)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 400, (
            f"month={month} "
            f"未按预期创建失败，"
            f"status_code="
            f"{response.status_code}，"
            f"response="
            f"{response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 400, (
            f"month={month} " f"业务状态错误：" f"{response_data}"
        )

        # ======================================
        # 错误信息断言
        # ======================================

        message = response_data.get(
            "message",
            "",
        )

        assert message, f"month={month} " f"失败后未返回错误信息：" f"{response_data}"

        # ======================================
        # 不应该生成有效预算 ID
        # ======================================

        data = response_data.get("data")

        if isinstance(
            data,
            dict,
        ):
            assert not data.get("id"), (
                f"month={month} " f"失败后不应该返回 budget_id：" f"{response_data}"
            )

    @allure.story("预算异常场景")
    @allure.title("查询不存在的预算失败")
    def test_get_nonexistent_budget_failed(
        self,
        budget_api,
    ):
        """
        验证查询不存在的预算 ID 时，
        接口必须返回失败。

        测试流程：

        1. 使用一个不存在的 budget_id；
        2. 调用预算详情接口；
        3. 验证 HTTP 状态码不是 200；
        4. 验证业务状态码不是 200；
        5. 验证返回错误信息；
        6. 验证没有返回有效预算数据。
        """

        # ======================================
        # 构造不存在的预算 ID
        # ======================================
        #
        # 使用一个非常大的 ID，
        # 避免和测试环境真实数据冲突。
        #
        # ======================================

        budget_id = 999999999

        # ======================================
        # 查询预算详情
        # ======================================

        response = budget_api.get_budget_detail(budget_id)

        # ======================================
        # HTTP 状态不能成功
        # ======================================
        #
        # 后端可能返回：
        #
        # 404
        # 400
        #
        # 具体取决于统一异常处理。
        #
        # 当前核心要求：
        #
        # 不能返回 200。
        #
        # ======================================

        assert response.status_code != 200, (
            f"查询不存在的预算"
            f"错误返回成功，"
            f"budget_id="
            f"{budget_id}，"
            f"status_code="
            f"{response.status_code}，"
            f"response="
            f"{response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码不能成功
        # ======================================

        assert response_data.get("code") != 200, (
            f"查询不存在预算时" f"业务状态错误：" f"{response_data}"
        )

        # ======================================
        # 错误信息必须存在
        # ======================================

        message = response_data.get(
            "message",
            "",
        )

        assert message, f"查询不存在预算失败后" f"未返回错误信息：" f"{response_data}"

        # ======================================
        # 不应该返回有效预算数据
        # ======================================

        data = response_data.get("data")

        if isinstance(
            data,
            dict,
        ):
            assert not data.get("id"), (
                f"查询不存在预算失败后" f"不应该返回有效 budget_id：" f"{response_data}"
            )

    @allure.story("预算异常场景")
    @allure.title("更新不存在的预算失败")
    def test_update_nonexistent_budget_failed(
        self,
        budget_api,
    ):
        """
        验证更新不存在的预算 ID 时，
        接口必须返回失败。

        测试流程：

        1. 使用一个不存在的 budget_id；
        2. 构造合法的更新数据；
        3. 调用预算更新接口；
        4. 验证 HTTP 状态码不是 200；
        5. 验证业务状态码不是 200；
        6. 验证返回错误信息；
        7. 验证没有返回有效预算数据。
        """

        # ======================================
        # 构造不存在的预算 ID
        # ======================================

        budget_id = 999999999

        # ======================================
        # 构造合法更新数据
        # ======================================
        #
        # 后端当前允许修改：
        #
        # amount
        # alert_threshold
        # note
        # is_active
        #
        # ======================================

        payload = {
            "amount": "1500.00",
            "alert_threshold": "85.00",
            "note": "自动化测试-更新不存在预算",
            "is_active": False,
        }

        # ======================================
        # 更新预算
        # ======================================

        response = budget_api.update_budget(
            budget_id,
            payload,
        )

        # ======================================
        # HTTP 状态不能成功
        # ======================================

        assert response.status_code != 200, (
            f"更新不存在的预算"
            f"错误返回成功，"
            f"budget_id="
            f"{budget_id}，"
            f"status_code="
            f"{response.status_code}，"
            f"response="
            f"{response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码不能成功
        # ======================================

        assert response_data.get("code") != 200, (
            f"更新不存在预算时" f"业务状态错误：" f"{response_data}"
        )

        # ======================================
        # 错误信息必须存在
        # ======================================

        message = response_data.get(
            "message",
            "",
        )

        assert message, f"更新不存在预算失败后" f"未返回错误信息：" f"{response_data}"

        # ======================================
        # 不应该返回有效预算 ID
        # ======================================

        data = response_data.get("data")

        if isinstance(
            data,
            dict,
        ):
            assert not data.get("id"), (
                f"更新不存在预算失败后" f"不应该返回有效 budget_id：" f"{response_data}"
            )

    @allure.story("预算异常场景")
    @allure.title("删除不存在的预算失败")
    def test_delete_nonexistent_budget_failed(
        self,
        budget_api,
    ):
        """
        验证删除不存在的预算 ID 时，
        接口必须返回失败。

        测试流程：

        1. 使用一个不存在的 budget_id；
        2. 调用预算删除接口；
        3. 验证 HTTP 状态码不是 200；
        4. 验证业务状态码不是 200；
        5. 验证返回错误信息；
        6. 验证没有返回有效预算数据。
        """

        # ======================================
        # 构造不存在的预算 ID
        # ======================================
        #
        # 使用一个非常大的 ID，
        # 避免和测试环境中的真实预算冲突。
        #
        # ======================================

        budget_id = 999999999

        # ======================================
        # 删除预算
        # ======================================

        response = budget_api.delete_budget(budget_id)

        # ======================================
        # HTTP 状态码不能成功
        # ======================================
        #
        # 后端可能返回：
        #
        # 404
        # 400
        #
        # 具体状态码取决于你的统一异常处理。
        #
        # 当前核心要求：
        #
        # 不允许返回 200。
        #
        # ======================================

        assert response.status_code != 200, (
            f"删除不存在的预算"
            f"错误返回成功，"
            f"budget_id="
            f"{budget_id}，"
            f"status_code="
            f"{response.status_code}，"
            f"response="
            f"{response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码不能成功
        # ======================================

        assert response_data.get("code") != 200, (
            f"删除不存在预算时" f"业务状态错误：" f"{response_data}"
        )

        # ======================================
        # 错误信息必须存在
        # ======================================

        message = response_data.get(
            "message",
            "",
        )

        assert message, f"删除不存在预算失败后" f"未返回错误信息：" f"{response_data}"

        # ======================================
        # 不应该返回有效预算 ID
        # ======================================

        data = response_data.get("data")

        if isinstance(
            data,
            dict,
        ):
            assert not data.get("id"), (
                f"删除不存在预算失败后" f"不应该返回有效 budget_id：" f"{response_data}"
            )

    @allure.story("预算权限")
    @allure.title("不同用户不能查看其他用户预算")
    def test_budget_list_user_isolation(
        self,
        budget_api,
        budget_factory,
        another_auth_client,
    ):
        """
        验证预算用户隔离。

        流程：

        1. 用户A创建预算；
        2. 用户B查询预算列表；
        3. 验证用户B无法看到用户A预算。

        """

        budget_id = None

        try:

            # ==================================
            # 用户A创建预算
            # ==================================

            with allure.step("用户A创建预算"):

                payload = budget_factory.build_budget(
                    budget_type="overall",
                    year=2030,
                    month=1,
                    amount="1000.00",
                    note="用户A私有预算",
                )

                response = budget_api.create_budget(payload)

                assert response.status_code == 200

                result = response.json()

                assert result["code"] == 200

                budget_id = result["data"]["id"]

            # ==================================
            # 创建用户B预算接口客户端
            # ==================================

            with allure.step("用户B查询预算列表"):

                another_api = BudgetApi(
                    client=another_auth_client,
                    api_prefix="/api/v1",
                )

                response = another_api.get_budget_list()

                assert response.status_code == 200

                result = response.json()

                assert result["code"] == 200

            # ==================================
            # 获取预算列表
            # ==================================

            data = result.get(
                "data",
                [],
            )

            if isinstance(
                data,
                dict,
            ):

                budgets = data.get(
                    "results",
                    [],
                )

            else:

                budgets = data

            assert isinstance(
                budgets,
                list,
            )

            # ==================================
            # 提取预算ID
            # ==================================

            budget_ids = [item.get("id") for item in budgets]

            # ==================================
            # 验证用户隔离
            # ==================================

            assert budget_id not in budget_ids, (
                f"存在预算数据泄露:" f"用户B查看到了用户A预算:" f"{budgets}"
            )

        finally:

            # ==================================
            # 清理用户A测试数据
            # ==================================

            if budget_id:

                try:

                    budget_api.delete_budget(budget_id)

                except Exception as e:

                    print(
                        "预算清理失败:",
                        e,
                    )

    @allure.story("预算查询")
    @allure.title("预算列表按年月类型分类和状态筛选")
    def test_budget_list_filters(
        self, budget_api, budget_factory, category_api, category_factory
    ):
        """创建两种预算，逐项验证列表筛选不会混入另一种预算。"""
        # 分类预算需要一个真实的支出分类。
        category_response = category_api.create_category(
            category_factory.build_category()
        )
        assert category_response.status_code == 200, category_response.text
        category_id = category_response.json()["data"]["id"]
        budget_ids = []

        try:
            # 同月创建总预算和分类预算，便于检查筛选是否区分它们。
            for payload in (
                budget_factory.build_budget(year=2098, month=11),
                budget_factory.build_budget(
                    budget_type="category", year=2098, month=11,
                    category_id=category_id,
                ),
            ):
                response = budget_api.create_budget(payload)
                assert response.status_code == 200, response.text
                budget_ids.append(response.json()["data"]["id"])

            filters = (
                ({"year": 2098, "month": 11}, set(budget_ids)),
                ({"budget_type": "overall"}, {budget_ids[0]}),
                ({"budget_type": "category"}, {budget_ids[1]}),
                ({"category_id": category_id}, {budget_ids[1]}),
                ({"is_active": True}, set(budget_ids)),
            )
            for params, expected_ids in filters:
                response = budget_api.get_budget_list(params)
                assert response.status_code == 200, response.text
                actual_ids = {item["id"] for item in response.json()["data"]}
                # 必须包含预期预算，且不能包含本次创建的另一种预算。
                assert expected_ids <= actual_ids
                assert not (set(budget_ids) - expected_ids) & actual_ids
        finally:
            # 先删除预算，再删除预算所引用的分类。
            for budget_id in budget_ids:
                response = budget_api.delete_budget(budget_id)
                assert response.status_code == 200, response.text
            response = category_api.delete_category(category_id)
            assert response.status_code == 200, response.text

    @allure.story("预算统计")
    @allure.title("查询预算执行进度成功")
    def test_budget_progress_success(self, budget_api, budget_factory):
        """创建未来月份预算，验证金额、剩余额度和进度字段。"""

        # ======================================
        # 创建未来月份总预算
        # ======================================

        response = budget_api.create_budget(
            budget_factory.build_budget(year=2095, month=7, amount="1200.00")
        )
        assert response.status_code == 200, response.text
        budget_id = response.json()["data"]["id"]

        try:
            # ======================================
            # 查询预算执行进度并核对金额
            # ======================================

            response = budget_api.get_progress({"year": 2095, "month": 7})
            assert response.status_code == 200, response.text
            data = response.json()["data"]
            assert data["year"] == 2095 and data["month"] == 7
            item = next(x for x in data["budgets"] if x["budget_id"] == budget_id)
            assert item["budget_amount"] == "1200.00"
            assert item["spent_amount"] == "0.00"
            assert item["remaining_amount"] == "1200.00"
        finally:
            # 清理本用例创建的预算。
            response = budget_api.delete_budget(budget_id)
            assert response.status_code == 200, response.text

    @allure.story("预算统计")
    @allure.title("查询月度预算概览成功")
    def test_budget_overview_success(self, budget_api, budget_factory):
        """验证概览汇总包含本次创建的总预算。"""

        # ======================================
        # 创建未来月份总预算
        # ======================================

        response = budget_api.create_budget(
            budget_factory.build_budget(year=2095, month=8, amount="800.00")
        )
        assert response.status_code == 200, response.text
        budget_id = response.json()["data"]["id"]

        try:
            # ======================================
            # 查询预算概览并核对汇总
            # ======================================

            response = budget_api.get_overview({"year": 2095, "month": 8})
            assert response.status_code == 200, response.text
            data = response.json()["data"]
            assert data["year"] == 2095 and data["month"] == 8
            assert data["total_budget"] == "800.00"
            assert data["total_spent"] == "0.00"
            assert data["budget_count"] >= 1
        finally:
            # 清理本用例创建的预算。
            response = budget_api.delete_budget(budget_id)
            assert response.status_code == 200, response.text

    @allure.story("预算管理")
    @allure.title("复制月度预算成功")
    def test_copy_monthly_budget_success(self, budget_api, budget_factory):
        """复制来源月预算，并确认目标月金额一致。"""

        # ======================================
        # 保存来源月和目标月预算 ID
        # ======================================

        budget_ids = []
        try:
            # ======================================
            # 在来源月份创建总预算
            # ======================================

            response = budget_api.create_budget(
                budget_factory.build_budget(year=2095, month=9, amount="900.00")
            )
            assert response.status_code == 200, response.text
            budget_ids.append(response.json()["data"]["id"])

            # ======================================
            # 复制到目标月份并核对结果
            # ======================================

            response = budget_api.copy_budgets(
                {
                    "source_year": 2095,
                    "source_month": 9,
                    "target_year": 2095,
                    "target_month": 10,
                }
            )
            assert response.status_code == 200, response.text
            data = response.json()["data"]
            budget_ids.extend(item["id"] for item in data["budgets"])
            assert data["created_count"] == 1
            assert data["skipped_count"] == 0
            assert data["budgets"][0]["amount"] == "900.00"
            assert data["budgets"][0]["month"] == 10
        finally:
            # ======================================
            # 清理来源预算与复制结果
            # ======================================

            for budget_id in budget_ids:
                response = budget_api.delete_budget(budget_id)
                assert response.status_code == 200, response.text

    @allure.story("创建预算")
    @allure.title("总预算不能绑定分类")
    def test_overall_budget_with_category_failed(
        self, budget_api, budget_factory, category_api, category_factory
    ):
        """总预算与分类预算的分类字段规则不同。"""
        # ======================================
        # 创建有效支出分类
        # ======================================

        response = category_api.create_category(category_factory.build_category())
        assert response.status_code == 200, response.text
        category_id = response.json()["data"]["id"]

        try:
            # ======================================
            # 总预算绑定分类并验证失败
            # ======================================

            payload = budget_factory.build_budget(category_id=category_id)
            response = budget_api.create_budget(payload)
            assert_rejected(response)
        finally:
            # 清理本用例创建的分类。
            response = category_api.delete_category(category_id)
            assert response.status_code == 200, response.text

    @allure.story("创建预算")
    @allure.title("收入分类不能用于支出预算")
    def test_category_budget_income_category_failed(
        self, budget_api, budget_factory, category_api, category_factory
    ):
        """分类预算只能关联支出分类。"""
        # ======================================
        # 创建收入分类
        # ======================================

        response = category_api.create_category(
            category_factory.build_category(category_type="income")
        )
        assert response.status_code == 200, response.text
        category_id = response.json()["data"]["id"]

        try:
            # ======================================
            # 收入分类用于分类预算并验证失败
            # ======================================

            payload = budget_factory.build_budget(
                budget_type="category", category_id=category_id
            )
            response = budget_api.create_budget(payload)
            assert_rejected(response)
        finally:
            # 清理本用例创建的分类。
            response = category_api.delete_category(category_id)
            assert response.status_code == 200, response.text

    @allure.story("预算统计")
    @allure.title("查询进度或概览时年月必须同时提供")
    @pytest.mark.parametrize("method_name", ("get_progress", "get_overview"))
    @pytest.mark.parametrize("params", ({"year": 2095}, {"month": 7}))
    def test_budget_statistics_partial_date_failed(
        self, budget_api, method_name, params
    ):
        """只给年份或只给月份时，都无法确定统计区间。"""

        # ======================================
        # 根据参数选择进度或概览接口
        # ======================================

        method = getattr(budget_api, method_name)

        # 只提交年份或月份，验证请求被拒绝。
        response = method(params)
        assert_rejected(response)

    @allure.story("预算管理")
    @allure.title("不能复制预算到同一个月份")
    def test_copy_budget_same_month_failed(self, budget_api):
        """来源月和目标月相同时，复制没有意义，应直接拒绝。"""

        # ======================================
        # 构造来源月和目标月相同的请求
        # ======================================

        payload = {
            "source_year": 2095,
            "source_month": 9,
            "target_year": 2095,
            "target_month": 9,
        }

        # ======================================
        # 提交复制请求并验证失败
        # ======================================

        response = budget_api.copy_budgets(payload)
        assert_rejected(response)
