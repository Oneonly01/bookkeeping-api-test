class TagApi:
    """
    标签接口封装。

    负责封装 tags 模块相关接口。

    测试用例层只负责：

    1. 准备测试数据；
    2. 调用业务 API；
    3. 执行断言。

    不直接在测试用例中拼接 URL。
    """

    def __init__(
        self,
        client,
        api_prefix,
    ):
        """
        初始化标签 API。

        :param client:
            RequestClient 实例。

        :param api_prefix:
            API 前缀，例如：

            /api/v1
        """

        self.client = client
        self.api_prefix = api_prefix

        # ======================================
        # 标签基础路径
        # ======================================

        self.base_url = f"{self.api_prefix}/tags/"

    # ======================================
    # 创建标签
    # ======================================

    def create_tag(
        self,
        payload,
    ):
        """
        创建标签。

        POST /api/v1/tags/
        """

        return self.client.post(
            self.base_url,
            json=payload,
        )

    # ======================================
    # 查询标签列表
    # ======================================

    def get_tag_list(
        self,
        params=None,
    ):
        """
        查询标签列表。

        GET /api/v1/tags/
        """

        return self.client.get(
            self.base_url,
            params=params,
        )

    # ======================================
    # 查询标签详情
    # ======================================

    def get_tag_detail(
        self,
        tag_id,
    ):
        """
        查询标签详情。

        GET /api/v1/tags/{id}/
        """

        url = f"{self.base_url}" f"{tag_id}/"

        return self.client.get(url)

    # ======================================
    # 修改标签
    # ======================================

    def update_tag(
        self,
        tag_id,
        payload,
    ):
        """
        修改标签。

        PUT /api/v1/tags/{id}/
        """

        url = f"{self.base_url}" f"{tag_id}/"

        return self.client.put(
            url,
            json=payload,
        )

    # ======================================
    # 删除标签
    # ======================================

    def delete_tag(
        self,
        tag_id,
    ):
        """
        删除标签。

        DELETE /api/v1/tags/{id}/
        """

        url = f"{self.base_url}" f"{tag_id}/"

        return self.client.delete(url)
