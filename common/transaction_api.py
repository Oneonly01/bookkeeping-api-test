class TransactionApi:
    """
    账单模块接口封装。

    主要作用：

    1. 统一管理账单模块接口地址；
    2. 统一发送账单相关 HTTP 请求；
    3. 避免测试用例中重复拼接 URL；
    4. 测试用例只关注：
       - 测试数据；
       - 业务场景；
       - 结果断言。

    当前计划覆盖：

    1. 新增账单；
    2. 查询账单列表；
    3. 查询账单详情；
    4. 修改账单；
    5. 删除账单；
    6. 账单汇总统计；
    7. 趋势统计；
    8. 分类统计；
    9. 月度统计；
    10. 年度统计；
    11. 账单图片；
    12. 后续标签相关场景。
    """

    def __init__(
        self,
        client,
        api_prefix: str,
    ):
        """
        初始化账单 API。

        :param client:
            已完成 JWT 鉴权的 RequestClient。

        :param api_prefix:
            API 统一前缀。

            例如：

            /api/v1
        """

        self.client = client

        # ======================================
        # 统一处理 API 前缀
        # ======================================
        #
        # 去掉末尾可能存在的 "/"
        # 避免后续 URL 拼接出现：
        #
        # /api/v1//transactions/
        #
        # ======================================

        self.api_prefix = api_prefix.rstrip("/")

    # ==========================================
    # 新增账单
    # ==========================================

    def create_transaction(
        self,
        payload: dict,
    ):
        """
        新增账单。

        POST /api/v1/transactions/

        :param payload:
            创建账单请求参数。

        :return:
            requests.Response
        """

        url = f"{self.api_prefix}" "/transactions/"

        return self.client.post(
            url,
            json=payload,
        )

    # ==========================================
    # 查询账单列表
    # ==========================================

    def get_transaction_list(
        self,
        params: dict | None = None,
    ):
        """
        查询账单列表。

        GET /api/v1/transactions/

        支持后续传入：

        1. 收支类型；
        2. 分类；
        3. 账户；
        4. 日期；
        5. 搜索关键词；
        6. 分页参数；

        等筛选条件。
        """

        url = f"{self.api_prefix}" "/transactions/"

        return self.client.get(
            url,
            params=params,
        )

    # ==========================================
    # 查询账单详情
    # ==========================================

    def get_transaction_detail(
        self,
        transaction_id: int,
    ):
        """
        查询账单详情。

        GET /api/v1/transactions/{transaction_id}/
        """

        url = f"{self.api_prefix}" f"/transactions/{transaction_id}/"

        return self.client.get(url)

    # ==========================================
    # 修改账单
    # ==========================================

    def update_transaction(
        self,
        transaction_id: int,
        payload: dict,
    ):
        """
        修改账单。

        PUT /api/v1/transactions/{transaction_id}/
        """

        url = f"{self.api_prefix}" f"/transactions/{transaction_id}/"

        return self.client.put(
            url,
            json=payload,
        )

    # ==========================================
    # 删除账单
    # ==========================================

    def delete_transaction(
        self,
        transaction_id: int,
    ):
        """
        删除账单。

        DELETE /api/v1/transactions/{transaction_id}/
        """

        url = f"{self.api_prefix}" f"/transactions/{transaction_id}/"

        return self.client.delete(url)

    # ==========================================
    # 账单汇总统计
    # ==========================================

    def get_summary(
        self,
        params: dict | None = None,
    ):
        """
        查询账单汇总统计。

        用于后续验证：

        1. 总收入；
        2. 总支出；
        3. 收支差额；
        4. 账单数量。

        具体返回字段
        以后端实际接口为准。
        """

        url = f"{self.api_prefix}" "/transactions/summary/"

        return self.client.get(
            url,
            params=params,
        )

    # ==========================================
    # 趋势统计
    # ==========================================

    def get_trend(
        self,
        params: dict | None = None,
    ):
        """
        查询账单趋势统计。
        """

        url = f"{self.api_prefix}" "/transactions/trend/"

        return self.client.get(
            url,
            params=params,
        )

    # ==========================================
    # 分类统计
    # ==========================================

    def get_category_statistics(
        self,
        params: dict | None = None,
    ):
        """
        查询账单分类统计。
        """

        url = f"{self.api_prefix}" "/transactions/category-statistics/"

        return self.client.get(
            url,
            params=params,
        )

    # ==========================================
    # 月度统计
    # ==========================================

    def get_monthly_statistics(
        self,
        params: dict | None = None,
    ):
        """
        查询月度账单统计。
        """

        url = f"{self.api_prefix}" "/transactions/monthly-statistics/"

        return self.client.get(
            url,
            params=params,
        )

    # ==========================================
    # 年度统计
    # ==========================================

    def get_yearly_statistics(
        self,
        params: dict | None = None,
    ):
        """
        查询年度账单统计。
        """

        url = f"{self.api_prefix}" "/transactions/yearly-statistics/"

        return self.client.get(
            url,
            params=params,
        )

    # ==========================================
    # 查询账单图片
    # ==========================================

    def get_transaction_images(
        self,
        transaction_id: int,
    ):
        """
        查询账单图片列表。

        GET
        /api/v1/transactions/{transaction_id}/images/
        """

        url = f"{self.api_prefix}" f"/transactions/{transaction_id}/images/"

        return self.client.get(url)

    # ==========================================
    # 上传账单图片
    # ==========================================

    def upload_transaction_image(
        self,
        transaction_id: int,
        files: dict,
    ):
        """
        上传账单图片。

        POST
        /api/v1/transactions/{transaction_id}/images/

        注意：

        图片上传使用 multipart/form-data，
        所以这里使用 files 参数，
        不能使用 json。
        """

        url = f"{self.api_prefix}" f"/transactions/{transaction_id}/images/"

        return self.client.post(
            url,
            files=files,
        )

    # ==========================================
    # 删除账单图片
    # ==========================================

    def delete_transaction_image(
        self,
        transaction_id: int,
        image_id: int,
    ):
        """
        删除账单图片。

        DELETE
        /api/v1/transactions/{transaction_id}/
        images/{image_id}/
        """

        url = (
            f"{self.api_prefix}"
            f"/transactions/{transaction_id}/"
            f"images/{image_id}/"
        )

        return self.client.delete(url)
