import uuid
from datetime import datetime


class AccountDataFactory:
    """
    账户模块测试数据工厂。

    主要作用：

    1. 统一生成账户测试数据；
    2. 自动生成唯一账户名称；
    3. 避免测试用例中重复编写 payload；
    4. 避免重复执行自动化测试时出现同名账户；
    5. 后续修改账户接口字段时，只需要修改这里。

    示例：

    payload = AccountDataFactory.build_account()

    返回：

    {
        "name": "自动化测试账户_a1b2c3d4",
        "account_type": "cash",
        "initial_balance": "1000.00",
        "note": "pytest自动化测试"
    }
    """

    # ==========================================
    # 默认账户数据
    # ==========================================
    #
    # 这里统一维护账户测试默认值。
    #
    # 后面的测试用例如果没有特殊需求，
    # 可以直接使用这些默认值。
    #
    # ==========================================

    DEFAULT_ACCOUNT_TYPE = "cash"

    DEFAULT_INITIAL_BALANCE = "1000.00"

    DEFAULT_NOTE = "pytest自动化测试"

    # ==========================================
    # 生成唯一账户名称
    # ==========================================

    @staticmethod
    def generate_account_name(
        prefix: str = "自动化测试账户",
    ) -> str:
        """
        生成唯一账户名称。

        为什么不直接写：

        自动化测试账户

        因为账户名称不能重复。

        如果自动化测试重复执行，
        固定账户名称可能出现：

        已存在同名账户

        所以这里使用 UUID 生成随机后缀。

        示例：

        自动化测试账户_a3f829bc
        """

        # ======================================
        # 生成 UUID
        # ======================================
        #
        # uuid4()：
        # 生成随机 UUID。
        #
        # hex：
        # 去掉 UUID 中的 "-"。
        #
        # [:8]：
        # 只取前 8 位，
        # 对测试数据来说已经足够避免重复。
        #
        # ======================================

        random_suffix = uuid.uuid4().hex[:8]

        return f"{prefix}_" f"{random_suffix}"

    # ==========================================
    # 创建账户测试数据
    # ==========================================

    @classmethod
    def build_account(
        cls,
        name: str | None = None,
        account_type: str | None = None,
        initial_balance: str | None = None,
        note: str | None = None,
        **kwargs,
    ) -> dict:
        """
        构造创建账户接口测试数据。

        参数说明：

        name：
            账户名称。

            如果不传，
            自动生成唯一账户名称。

        account_type：
            账户类型。

            如果不传，
            默认使用 cash。

        initial_balance：
            初始余额。

            如果不传，
            默认使用 1000.00。

        note：
            账户备注。

            如果不传，
            使用默认自动化测试备注。

        **kwargs：
            用于支持额外账户字段。

            例如：

            color
            icon
            sort_order
            is_default
            is_active

        这样以后 Account 接口增加字段，
        不需要重新修改整个方法。
        """

        # ======================================
        # 创建基础测试数据
        # ======================================

        payload = {
            "name": (name or cls.generate_account_name()),
            "account_type": (account_type or cls.DEFAULT_ACCOUNT_TYPE),
            "initial_balance": (
                initial_balance
                if initial_balance is not None
                else cls.DEFAULT_INITIAL_BALANCE
            ),
            "note": (note if note is not None else cls.DEFAULT_NOTE),
        }

        # ======================================
        # 添加额外字段
        # ======================================
        #
        # 例如调用：
        #
        # AccountDataFactory.build_account(
        #     color="#27BA9B",
        #     sort_order=10,
        # )
        #
        # 最终 payload 会自动增加：
        #
        # "color": "#27BA9B"
        # "sort_order": 10
        #
        # ======================================

        payload.update(kwargs)

        return payload

    # ==========================================
    # 创建零余额账户数据
    # ==========================================

    @classmethod
    def build_zero_balance_account(
        cls,
        **kwargs,
    ) -> dict:
        """
        构造余额为 0 的账户。

        主要用于：

        1. 删除账户测试；
        2. 零余额边界测试；
        3. 清理测试数据。

        因为当前后端规则：

        账户余额不为 0 时不能删除。
        """

        return cls.build_account(
            initial_balance="0.00",
            **kwargs,
        )

    # ==========================================
    # 创建指定余额账户
    # ==========================================

    @classmethod
    def build_account_with_balance(
        cls,
        balance: str,
        **kwargs,
    ) -> dict:
        """
        构造指定初始余额的账户。

        示例：

        AccountDataFactory
        .build_account_with_balance(
            "5000.00"
        )

        适用于：

        1. 转账测试；
        2. 余额不足测试；
        3. 资产统计测试。
        """

        return cls.build_account(
            initial_balance=balance,
            **kwargs,
        )


class TransactionDataFactory:
    """
    账单模块测试数据工厂。

    主要作用：

    1. 统一生成账单测试数据；
    2. 避免测试用例重复编写 payload；
    3. 支持收入 / 支出不同场景；
    4. 自动生成唯一备注；
    5. 后续接口字段变化时集中维护。

    当前计划支持：

    1. 支出账单；
    2. 收入账单；
    3. 指定金额；
    4. 指定账户；
    5. 指定分类；
    6. 指定交易时间；
    7. 指定备注；
    8. 指定标签。
    """

    # ==========================================
    # 默认测试数据
    # ==========================================

    DEFAULT_EXPENSE_AMOUNT = "100.00"

    DEFAULT_INCOME_AMOUNT = "500.00"

    DEFAULT_TRANSACTION_TYPE_EXPENSE = "expense"

    DEFAULT_TRANSACTION_TYPE_INCOME = "income"

    DEFAULT_NOTE_PREFIX = "pytest自动化账单"

    # ==========================================
    # 生成唯一备注
    # ==========================================

    @staticmethod
    def generate_note(
        prefix: str = DEFAULT_NOTE_PREFIX,
    ) -> str:
        """
        生成唯一账单备注。

        为什么需要唯一备注：

        1. 方便在账单列表中定位当前测试数据；
        2. 避免依赖列表排序；
        3. 后续搜索测试可以直接复用；
        4. 多次执行自动化测试时不容易混淆。

        示例：

        pytest自动化账单_a1b2c3d4
        """

        random_suffix = uuid.uuid4().hex[:8]

        return f"{prefix}_" f"{random_suffix}"

    # ==========================================
    # 生成交易时间
    # ==========================================

    @staticmethod
    def generate_transaction_time() -> str:
        """
        生成当前交易时间。

        返回格式：

        YYYY-MM-DD HH:MM:SS

        例如：

        2026-10-09 21:30:00
        """

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ==========================================
    # 构造通用账单数据
    # ==========================================

    @classmethod
    def build_transaction(
        cls,
        account_id: int,
        category_id: int,
        transaction_type: str,
        amount: str,
        transaction_time: str | None = None,
        note: str | None = None,
        tag_ids: list | None = None,
        **kwargs,
    ) -> dict:
        """
        构造通用账单请求数据。

        参数说明：

        account_id：
            账单所属账户 ID。

        category_id：
            账单所属分类 ID。

        transaction_type：
            账单类型。

            当前计划：

            expense：
                支出

            income：
                收入

        amount：
            账单金额。

        transaction_time：
            交易时间。

            如果不传，
            自动使用当前时间。

        note：
            账单备注。

            如果不传，
            自动生成唯一备注。

        tag_ids：
            标签 ID 列表。

            如果不传，
            默认不添加标签。

        **kwargs：
            后续用于扩展其他账单字段。
        """

        # ======================================
        # 构造基础 payload
        # ======================================

        payload = {
            "account_id": account_id,
            "category_id": category_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "transaction_time": (transaction_time or cls.generate_transaction_time()),
            "note": (note or cls.generate_note()),
        }

        # ======================================
        # 添加标签
        # ======================================
        #
        # tag_ids 是可选字段。
        #
        # 如果没有传，
        # 不主动添加到 payload，
        # 避免和后端字段默认值产生冲突。
        #
        # ======================================

        if tag_ids is not None:
            payload["tag_ids"] = tag_ids

        # ======================================
        # 添加额外字段
        # ======================================

        payload.update(kwargs)

        return payload

    # ==========================================
    # 构造支出账单
    # ==========================================

    @classmethod
    def build_expense(
        cls,
        account_id: int,
        category_id: int,
        amount: str | None = None,
        **kwargs,
    ) -> dict:
        """
        构造支出账单。

        默认金额：

        100.00

        示例：

        TransactionDataFactory.build_expense(
            account_id=1,
            category_id=2,
        )
        """

        return cls.build_transaction(
            account_id=account_id,
            category_id=category_id,
            transaction_type=(cls.DEFAULT_TRANSACTION_TYPE_EXPENSE),
            amount=(amount if amount is not None else cls.DEFAULT_EXPENSE_AMOUNT),
            **kwargs,
        )

    # ==========================================
    # 构造收入账单
    # ==========================================

    @classmethod
    def build_income(
        cls,
        account_id: int,
        category_id: int,
        amount: str | None = None,
        **kwargs,
    ) -> dict:
        """
        构造收入账单。

        默认金额：

        500.00
        """

        return cls.build_transaction(
            account_id=account_id,
            category_id=category_id,
            transaction_type=(cls.DEFAULT_TRANSACTION_TYPE_INCOME),
            amount=(amount if amount is not None else cls.DEFAULT_INCOME_AMOUNT),
            **kwargs,
        )
