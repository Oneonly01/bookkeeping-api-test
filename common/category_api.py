class CategoryApi:
    """
    分类模块接口封装。

    当前主要用于账单自动化测试准备分类数据。

    主要作用：

    1. 创建测试分类；
    2. 查询分类列表；
    3. 查询分类详情；
    4. 删除测试分类；
    5. 避免账单测试依赖数据库已有分类。

    后续如果单独开发分类模块自动化，
    也可以继续复用这个类。
    """

    def __init__(
        self,
        client,
        api_prefix: str,
    ):
        """
        初始化分类 API。

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

        self.api_prefix = api_prefix.rstrip("/")

    # ==========================================
    # 创建分类
    # ==========================================

    def create_category(
        self,
        payload: dict,
    ):
        """
        创建分类。

        POST /api/v1/categories/
        """

        url = f"{self.api_prefix}" "/categories/"

        return self.client.post(
            url,
            json=payload,
        )

    # ==========================================
    # 查询分类列表
    # ==========================================

    def get_category_list(
        self,
        params: dict | None = None,
    ):
        """
        查询分类列表。

        GET /api/v1/categories/
        """

        url = f"{self.api_prefix}" "/categories/"

        return self.client.get(
            url,
            params=params,
        )

    # ==========================================
    # 查询分类详情
    # ==========================================

    def get_category_detail(
        self,
        category_id: int,
    ):
        """
        查询分类详情。

        GET /api/v1/categories/{category_id}/
        """

        url = f"{self.api_prefix}" f"/categories/{category_id}/"

        return self.client.get(url)

    # ==========================================
    # 删除分类
    # ==========================================

    def delete_category(
        self,
        category_id: int,
    ):
        """
        删除分类。

        DELETE /api/v1/categories/{category_id}/
        """

        url = f"{self.api_prefix}" f"/categories/{category_id}/"

        return self.client.delete(url)
