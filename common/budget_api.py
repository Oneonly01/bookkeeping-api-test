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
