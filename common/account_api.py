class AccountApi:
    """
    账户模块接口封装。

    作用：

    1. 统一管理账户模块接口地址；
    2. 统一发送账户相关 HTTP 请求；
    3. 测试用例只关注测试数据和断言；
    4. 避免每个测试重复拼接 URL。
    """

    def __init__(
        self,
        client,
        api_prefix: str,
    ):
        """
        初始化账户 API。

        :param client:
            已完成 JWT 鉴权的 RequestClient。

        :param api_prefix:
            接口统一前缀，例如：

            /api/v1
        """

        self.client = client

        self.api_prefix = api_prefix.rstrip("/")

    # ==========================================
    # 账户列表 / 创建账户
    # ==========================================

    def create_account(
        self,
        payload: dict,
    ):
        """
        创建账户。

        POST /api/v1/accounts/
        """

        url = f"{self.api_prefix}" "/accounts/"

        return self.client.post(
            url,
            json=payload,
        )

    def get_account_list(
        self,
        params: dict | None = None,
    ):
        """
        查询账户列表。

        GET /api/v1/accounts/
        """

        url = f"{self.api_prefix}" "/accounts/"

        return self.client.get(
            url,
            params=params,
        )

    # ==========================================
    # 账户详情 / 修改 / 删除
    # ==========================================

    def get_account_detail(
        self,
        account_id: int,
    ):
        """
        查询账户详情。

        GET /api/v1/accounts/{account_id}/
        """

        url = f"{self.api_prefix}" f"/accounts/{account_id}/"

        return self.client.get(url)

    def update_account(
        self,
        account_id: int,
        payload: dict,
    ):
        """
        修改账户。

        PUT /api/v1/accounts/{account_id}/
        """

        url = f"{self.api_prefix}" f"/accounts/{account_id}/"

        return self.client.put(
            url,
            json=payload,
        )

    def delete_account(
        self,
        account_id: int,
    ):
        """
        删除账户。

        DELETE /api/v1/accounts/{account_id}/
        """

        url = f"{self.api_prefix}" f"/accounts/{account_id}/"

        return self.client.delete(url)

    # ==========================================
    # 账户余额调整
    # ==========================================

    def adjust_balance(
        self,
        account_id: int,
        payload: dict,
    ):
        """
        调整账户余额。

        POST
        /api/v1/accounts/{account_id}/adjust-balance/
        """

        url = f"{self.api_prefix}" f"/accounts/{account_id}/" "adjust-balance/"

        return self.client.post(
            url,
            json=payload,
        )

    def get_balance_adjustments(
        self,
        account_id: int,
    ):
        """
        查询账户余额调整记录。

        GET
        /api/v1/accounts/{account_id}/balance-adjustments/
        """

        url = f"{self.api_prefix}" f"/accounts/{account_id}/" "balance-adjustments/"

        return self.client.get(url)

    # ==========================================
    # 账户转账
    # ==========================================

    def create_transfer(
        self,
        payload: dict,
    ):
        """
        创建账户转账。

        POST /api/v1/accounts/transfers/
        """

        url = f"{self.api_prefix}" "/accounts/transfers/"

        return self.client.post(
            url,
            json=payload,
        )

    def get_transfer_list(
        self,
        params: dict | None = None,
    ):
        """
        查询转账记录列表。

        GET /api/v1/accounts/transfers/
        """

        url = f"{self.api_prefix}" "/accounts/transfers/"

        return self.client.get(
            url,
            params=params,
        )

    def get_transfer_detail(
        self,
        transfer_id: int,
    ):
        """
        查询转账记录详情。

        GET /api/v1/accounts/transfers/{transfer_id}/
        """

        url = f"{self.api_prefix}" f"/accounts/transfers/{transfer_id}/"

        return self.client.get(url)

    # ==========================================
    # 账户统计
    # ==========================================

    def get_statistics(
        self,
    ):
        """
        查询账户统计。

        GET /api/v1/accounts/statistics/
        """

        url = f"{self.api_prefix}" "/accounts/statistics/"

        return self.client.get(url)

    def get_asset_summary(
        self,
    ):
        """
        查询资产汇总。

        GET /api/v1/accounts/asset-summary/
        """

        url = f"{self.api_prefix}" "/accounts/asset-summary/"

        return self.client.get(url)
