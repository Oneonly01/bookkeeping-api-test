class BudgetApi:
    """
    预算模块接口封装。
    """

    def __init__(
        self,
        client,
        api_prefix,
    ):
        self.client = client
        self.api_prefix = api_prefix

        self.base_url = f"{self.api_prefix}/budgets/"

    def create_budget(
        self,
        payload,
    ):
        """
        创建预算。

        POST /api/v1/budgets/
        """

        return self.client.post(
            self.base_url,
            json=payload,
        )

    def get_budget_list(
        self,
        params=None,
    ):
        """
        查询预算列表。
        """

        return self.client.get(
            self.base_url,
            params=params,
        )

    def get_budget_detail(
        self,
        budget_id,
    ):
        """
        查询预算详情。
        """

        url = f"{self.base_url}" f"{budget_id}/"

        return self.client.get(url)

    def update_budget(
        self,
        budget_id,
        payload,
    ):
        """
        修改预算。
        """

        url = f"{self.base_url}" f"{budget_id}/"

        return self.client.put(
            url,
            json=payload,
        )

    def delete_budget(
        self,
        budget_id,
    ):
        """
        删除预算。
        """

        url = f"{self.base_url}" f"{budget_id}/"

        return self.client.delete(url)

    def get_progress(self, params=None):
        """查询指定月份每项预算的执行进度。"""
        # params 可包含 year 和 month；由后端校验取值范围。
        return self.client.get(f"{self.base_url}progress/", params=params)

    def get_overview(self, params=None):
        """查询指定月份的预算汇总。"""
        # 概览会汇总该月全部有效预算，不需要传预算 ID。
        return self.client.get(f"{self.base_url}overview/", params=params)

    def copy_budgets(self, payload):
        """把来源月份的预算复制到目标月份。"""
        # payload 指定来源年月和目标年月，后端负责跳过重复预算。
        return self.client.post(f"{self.base_url}copy/", json=payload)
