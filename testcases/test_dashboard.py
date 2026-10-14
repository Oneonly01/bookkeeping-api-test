from decimal import Decimal

import allure


@allure.feature("首页聚合模块")
class TestDashboard:
    @allure.story("首页汇总")
    @allure.title("获取首页资产收支预算和储蓄汇总")
    def test_dashboard_summary_success(self, dashboard_api):
        """验证首页聚合数据结构，以及资产和收支的基本计算关系。"""

        # ======================================
        # 查询首页汇总
        # ======================================

        response = dashboard_api.get_summary()
        assert response.status_code == 200, response.text
        result = response.json()
        assert result["code"] == 200
        data = result["data"]

        # ======================================
        # 检查各模块数据均已返回
        # ======================================

        for key in ("assets", "month_statistics", "budget", "savings", "recent_transactions"):
            assert key in data

        # ======================================
        # 检查资产与本月收支计算关系
        # ======================================

        assets = data["assets"]
        assert Decimal(assets["net_assets"]) == (
            Decimal(assets["total_assets"]) - Decimal(assets["total_liabilities"])
        )
        month = data["month_statistics"]
        assert Decimal(month["balance"]) == (
            Decimal(month["income"]) - Decimal(month["expense"])
        )

    @allure.story("跨模块联动")
    @allure.title("新增支出同步更新账户预算和首页")
    def test_expense_updates_account_budget_dashboard(
        self, dashboard_api, account_api, test_account, category_api,
        category_factory, budget_api, budget_factory, transaction_api,
        transaction_factory,
    ):
        """一笔本月支出应同时反映在账户、预算进度和首页汇总。"""

        # ======================================
        # 准备清理变量与独立测试账户
        # ======================================

        category_id = budget_id = transaction_id = None
        account_id = test_account["id"]
        try:
            # ======================================
            # 创建独立支出分类
            # ======================================

            response = category_api.create_category(category_factory.build_category())
            assert response.status_code == 200, response.text
            category_id = response.json()["data"]["id"]

            # ======================================
            # 记录首页基线与后端当前月份
            # ======================================

            response = dashboard_api.get_summary()
            assert response.status_code == 200, response.text
            dashboard_before = response.json()["data"]
            year = dashboard_before["year"]
            month = dashboard_before["month"]

            # ======================================
            # 创建本月分类预算
            # ======================================

            response = budget_api.create_budget(budget_factory.build_budget(
                budget_type="category", year=year, month=month,
                category_id=category_id, amount="1000.00",
            ))
            assert response.status_code == 200, response.text
            budget_id = response.json()["data"]["id"]

            # ======================================
            # 记录账户余额与预算进度基线
            # ======================================

            response = account_api.get_account_detail(account_id)
            assert response.status_code == 200, response.text
            balance_before = Decimal(response.json()["data"]["balance"])
            response = budget_api.get_progress({"year": year, "month": month})
            assert response.status_code == 200, response.text
            progress_before = next(
                item for item in response.json()["data"]["budgets"]
                if item["budget_id"] == budget_id
            )

            # ======================================
            # 创建一笔本月支出
            # ======================================

            payload = transaction_factory.build_expense(
                account_id=account_id, category_id=category_id,
                amount="100.00", transaction_time=f"{year}-{month:02d}-15 12:00:00",
            )
            response = transaction_api.create_transaction(payload)
            assert response.status_code == 200, response.text
            transaction_id = response.json()["data"]["id"]

            # ======================================
            # 验证账户余额减少 100 元
            # ======================================

            response = account_api.get_account_detail(account_id)
            assert response.status_code == 200, response.text
            assert Decimal(response.json()["data"]["balance"]) == balance_before - Decimal("100.00")

            # ======================================
            # 验证分类预算已用金额增加 100 元
            # ======================================

            response = budget_api.get_progress({"year": year, "month": month})
            assert response.status_code == 200, response.text
            progress_after = next(
                item for item in response.json()["data"]["budgets"]
                if item["budget_id"] == budget_id
            )
            assert Decimal(progress_after["spent_amount"]) == (
                Decimal(progress_before["spent_amount"]) + Decimal("100.00")
            )

            # ======================================
            # 验证首页资产减少、本月支出增加
            # ======================================

            response = dashboard_api.get_summary()
            assert response.status_code == 200, response.text
            dashboard_after = response.json()["data"]
            assert Decimal(dashboard_after["assets"]["net_assets"]) == (
                Decimal(dashboard_before["assets"]["net_assets"]) - Decimal("100.00")
            )
            assert Decimal(dashboard_after["month_statistics"]["expense"]) == (
                Decimal(dashboard_before["month_statistics"]["expense"]) + Decimal("100.00")
            )
        finally:
            # ======================================
            # 按账单、预算、分类的顺序清理测试数据
            # ======================================

            if transaction_id is not None:
                response = transaction_api.delete_transaction(transaction_id)
                assert response.status_code == 200, response.text
            if budget_id is not None:
                response = budget_api.delete_budget(budget_id)
                assert response.status_code == 200, response.text
            if category_id is not None:
                response = category_api.delete_category(category_id)
                assert response.status_code == 200, response.text
