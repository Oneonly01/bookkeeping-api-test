class ProductApi:
    """封装商品及价格历史接口。"""

    def __init__(self, client, api_prefix):
        # 保存已认证客户端并构造商品接口基础路径。
        self.client = client
        self.base_url = f"{api_prefix.rstrip('/')}/products/"

    def create_product(self, payload):
        """新增商品。"""

        # 通过 POST 请求提交商品数据。
        return self.client.post(self.base_url, json=payload)

    def get_product_list(self, params=None):
        """查询商品列表，可传筛选参数。"""

        # 将筛选条件作为 URL 查询参数提交。
        return self.client.get(self.base_url, params=params)

    def get_product_detail(self, product_id):
        """查询单个商品。"""

        # 在路径中加入商品 ID 后查询详情。
        url = f"{self.base_url}{product_id}/"
        return self.client.get(url)

    def update_product(self, product_id, payload):
        """修改商品。"""

        # 指定商品 ID，并提交需要修改的字段。
        url = f"{self.base_url}{product_id}/"
        return self.client.put(url, json=payload)

    def delete_product(self, product_id):
        """逻辑删除商品。"""

        # 指定商品 ID 后发送删除请求。
        url = f"{self.base_url}{product_id}/"
        return self.client.delete(url)

    def create_price_record(self, product_id, payload):
        """给商品新增一条价格记录。"""

        # 构造价格记录路径并提交一条新价格。
        url = f"{self.base_url}{product_id}/prices/"
        return self.client.post(url, json=payload)

    def get_price_records(self, product_id):
        """查询商品价格历史与价格汇总。"""

        # 查询该商品的价格历史与汇总。
        url = f"{self.base_url}{product_id}/prices/"
        return self.client.get(url)
