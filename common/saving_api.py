class SavingApi:
    """
    目标储蓄模块接口封装。

    当前后端真实路由：

        /savings/goals/
        /savings/goals/{goal_id}/
        /savings/goals/{goal_id}/deposit/
        /savings/goals/{goal_id}/withdraw/
        /savings/goals/{goal_id}/records/
        /savings/goals/{goal_id}/pause/
        /savings/goals/{goal_id}/resume/
        /savings/summary/
    """

    def __init__(
        self,
        client,
        api_prefix,
    ):
        """
        初始化储蓄目标 API。
        """

        self.client = client
        self.api_prefix = api_prefix

        # ======================================
        # 储蓄目标基础 URL
        # ======================================

        self.goal_base_url = f"{self.api_prefix}/savings/goals/"

        # ======================================
        # 储蓄汇总 URL
        # ======================================

        self.summary_url = f"{self.api_prefix}/savings/summary/"

    # ======================================
    # 创建储蓄目标
    # ======================================

    def create_saving(
        self,
        payload,
    ):
        """
        创建储蓄目标。

        POST /api/v1/savings/goals/
        """

        return self.client.post(
            self.goal_base_url,
            json=payload,
        )

    # ======================================
    # 查询储蓄目标列表
    # ======================================

    def get_saving_list(
        self,
        params=None,
    ):
        """
        查询储蓄目标列表。

        GET /api/v1/savings/goals/
        """

        return self.client.get(
            self.goal_base_url,
            params=params,
        )

    # ======================================
    # 查询储蓄目标详情
    # ======================================

    def get_saving_detail(
        self,
        saving_id,
    ):
        """
        查询储蓄目标详情。

        GET /api/v1/savings/goals/{goal_id}/
        """

        url = f"{self.goal_base_url}" f"{saving_id}/"

        return self.client.get(url)

    # ======================================
    # 修改储蓄目标
    # ======================================

    def update_saving(
        self,
        saving_id,
        payload,
    ):
        """
        修改储蓄目标。

        PUT /api/v1/savings/goals/{goal_id}/
        """

        url = f"{self.goal_base_url}" f"{saving_id}/"

        return self.client.put(
            url,
            json=payload,
        )

    # ======================================
    # 删除储蓄目标
    # ======================================

    def delete_saving(
        self,
        saving_id,
    ):
        """
        删除储蓄目标。

        DELETE /api/v1/savings/goals/{goal_id}/
        """

        url = f"{self.goal_base_url}" f"{saving_id}/"

        return self.client.delete(url)

    # ======================================
    # 存入资金
    # ======================================

    def deposit(
        self,
        saving_id,
        payload,
    ):
        """
        向储蓄目标存入资金。

        POST
        /api/v1/savings/goals/{goal_id}/deposit/
        """

        url = f"{self.goal_base_url}" f"{saving_id}/deposit/"

        return self.client.post(
            url,
            json=payload,
        )

    # ======================================
    # 取出资金
    # ======================================

    def withdraw(
        self,
        saving_id,
        payload,
    ):
        """
        从储蓄目标取出资金。

        POST
        /api/v1/savings/goals/{goal_id}/withdraw/
        """

        url = f"{self.goal_base_url}" f"{saving_id}/withdraw/"

        return self.client.post(
            url,
            json=payload,
        )

    # ======================================
    # 查询储蓄流水
    # ======================================

    def get_records(
        self,
        saving_id,
        params=None,
    ):
        """
        查询储蓄流水。

        GET
        /api/v1/savings/goals/{goal_id}/records/
        """

        url = f"{self.goal_base_url}" f"{saving_id}/records/"

        return self.client.get(
            url,
            params=params,
        )

    # ======================================
    # 暂停储蓄目标
    # ======================================

    def pause(
        self,
        saving_id,
    ):
        """
        暂停储蓄目标。

        POST
        /api/v1/savings/goals/{goal_id}/pause/
        """

        url = f"{self.goal_base_url}" f"{saving_id}/pause/"

        return self.client.post(url)

    # ======================================
    # 恢复储蓄目标
    # ======================================

    def resume(
        self,
        saving_id,
    ):
        """
        恢复储蓄目标。

        POST
        /api/v1/savings/goals/{goal_id}/resume/
        """

        url = f"{self.goal_base_url}" f"{saving_id}/resume/"

        return self.client.post(url)

    # ======================================
    # 储蓄汇总
    # ======================================

    def get_summary(
        self,
    ):
        """
        查询储蓄汇总。

        GET /api/v1/savings/summary/
        """

        return self.client.get(self.summary_url)
