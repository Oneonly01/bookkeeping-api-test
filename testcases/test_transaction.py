from decimal import Decimal
import allure
import pytest


@allure.feature("账单管理")
class TestTransaction:
    """
    账单模块接口自动化测试。
    """

    @allure.story("新增账单")
    @allure.title("新增支出账单成功")
    def test_create_expense_transaction_success(
        self,
        account_api,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证正常新增支出账单成功。

        测试前置：

        1. transaction_context 自动创建测试账户；
        2. transaction_context 自动创建支出分类；
        3. 测试账户初始余额为 5000.00。

        测试步骤：

        1. 获取测试账户；
        2. 获取支出分类；
        3. 使用 TransactionDataFactory 构造支出账单；
        4. 调用新增账单接口；
        5. 校验新增账单响应；
        6. 查询账户详情；
        7. 验证支出后账户余额正确变化；
        8. 测试结束后自动删除当前账单。

        验证内容：

        1. HTTP 状态码为 200；
        2. 业务 code 为 200；
        3. 返回账单 ID；
        4. 账单类型为 expense；
        5. 账单金额正确；
        6. 账户 ID 正确；
        7. 分类 ID 正确；
        8. 支出后账户余额从 5000.00
        正确变为 4900.00。

        当前测试数据：

        初始账户余额：
            5000.00

        支出金额：
            100.00

        预期账户余额：
            4900.00
        """

        # ======================================
        # 获取测试账户
        # ======================================
        #
        # transaction_context fixture
        # 会在测试执行前自动创建一个
        # 用于账单测试的真实账户。
        #
        # 当前账户默认初始余额：
        #
        # 5000.00
        #
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        # ======================================
        # 获取账户 ID
        # ======================================

        account_id = account.get("id")

        # ======================================
        # 账户 ID 存在性断言
        # ======================================

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================
        #
        # transaction_context fixture
        # 同时会创建一个支出分类。
        #
        # 当前新增支出账单必须使用
        # expense 类型分类。
        #
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        # ======================================
        # 获取支出分类 ID
        # ======================================

        expense_category_id = expense_category.get("id")

        # ======================================
        # 支出分类 ID 存在性断言
        # ======================================

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 构造支出账单测试数据
        # ======================================
        #
        # TransactionDataFactory
        # 会统一构造账单 payload。
        #
        # build_expense() 会自动：
        #
        # 1. 设置 transaction_type=expense；
        # 2. 设置账户 ID；
        # 3. 设置分类 ID；
        # 4. 设置账单金额；
        # 5. 自动生成交易时间；
        # 6. 设置账单备注。
        #
        # 当前测试金额：
        #
        # 100.00
        #
        # ======================================

        payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="100.00",
            note="自动化测试-新增支出账单",
        )

        # ======================================
        # 初始化账单 ID
        # ======================================
        #
        # 如果账单创建成功，
        # transaction_id 会保存接口返回的 ID。
        #
        # finally 中会根据 transaction_id
        # 删除当前测试创建的账单，
        # 防止污染数据库。
        #
        # 如果创建失败，
        # transaction_id 保持 None，
        # 不执行删除。
        #
        # ======================================

        transaction_id = None

        try:
            # ==================================
            # 调用新增账单接口
            # ==================================
            #
            # URL 和 POST 请求
            # 已经统一封装在：
            #
            # TransactionApi.create_transaction()
            #
            # 测试用例只负责：
            #
            # 1. 准备测试数据；
            # 2. 调用接口；
            # 3. 进行断言。
            #
            # ==================================

            response = transaction_api.create_transaction(payload)

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert response.status_code == 200, (
                f"新增支出账单失败，"
                f"status_code="
                f"{response.status_code}，"
                f"response={response.text}"
            )

            # ==================================
            # 解析响应 JSON
            # ==================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert response_data.get("code") == 200, (
                f"新增支出账单业务失败：" f"{response_data}"
            )

            # ==================================
            # 获取响应 data
            # ==================================

            data = response_data.get(
                "data",
                {},
            )

            # ==================================
            # 获取账单 ID
            # ==================================

            transaction_id = data.get("id")

            # ==================================
            # 账单 ID 存在性断言
            # ==================================

            assert transaction_id, (
                f"新增支出账单后" f"未返回账单 ID：" f"{response_data}"
            )

            # ==================================
            # 账单类型断言
            # ======================================
            #
            # 当前测试创建的是支出账单，
            # 所以 transaction_type
            # 必须为 expense。
            #
            # ======================================

            assert data.get("transaction_type") == "expense", (
                f"账单类型不正确，"
                f"expected=expense，"
                f"actual="
                f"{data.get('transaction_type')}"
            )

            # ==================================
            # 账单金额断言
            # ======================================

            assert data.get("amount") == payload["amount"], (
                f"账单金额不正确，"
                f"expected={payload['amount']}，"
                f"actual={data.get('amount')}"
            )

            # ==================================
            # 账户 ID 断言
            # ======================================
            #
            # 当前后端实际返回字段
            # 可能使用：
            #
            # account
            #
            # 或：
            #
            # account_id
            #
            # 所以这里暂时兼容两种结构。
            #
            # 等账单接口真实响应完全确认后，
            # 后续可以统一成真实字段。
            #
            # ======================================

            assert (
                data.get("account") == account_id
                or data.get("account_id") == account_id
            ), (f"账单账户不正确，" f"expected={account_id}，" f"data={data}")

            # ==================================
            # 分类 ID 断言
            # ======================================
            #
            # 同样兼容：
            #
            # category
            #
            # 或：
            #
            # category_id
            #
            # ======================================

            assert (
                data.get("category") == expense_category_id
                or data.get("category_id") == expense_category_id
            ), (
                f"账单分类不正确，"
                f"expected="
                f"{expense_category_id}，"
                f"data={data}"
            )

            # ==================================
            # 查询支出后的账户详情
            # ======================================
            #
            # 新增支出账单以后，
            # 不能只验证账单接口返回成功。
            #
            # 还必须验证：
            #
            # 账户余额是否真实发生变化。
            #
            # 当前：
            #
            # 初始余额：
            # 5000.00
            #
            # 支出金额：
            # 100.00
            #
            # 预期余额：
            # 4900.00
            #
            # ======================================

            account_response = account_api.get_account_detail(account_id)

            # ==================================
            # 查询账户 HTTP 状态码断言
            # ======================================

            assert account_response.status_code == 200, (
                f"新增支出账单后"
                f"查询账户失败，"
                f"status_code="
                f"{account_response.status_code}，"
                f"response="
                f"{account_response.text}"
            )

            # ==================================
            # 解析账户详情响应
            # ======================================

            account_response_data = account_response.json()

            # ==================================
            # 账户详情业务状态码断言
            # ======================================

            assert account_response_data.get("code") == 200, (
                f"新增支出账单后" f"查询账户业务失败：" f"{account_response_data}"
            )

            # ==================================
            # 获取账户详情数据
            # ======================================

            account_data = account_response_data.get(
                "data",
                {},
            )

            # ==================================
            # 支出后账户余额断言
            # ======================================
            #
            # 5000.00 - 100.00
            #
            # = 4900.00
            #
            # ======================================

            assert account_data.get("balance") == "4900.00", (
                f"新增支出账单后账户余额错误，"
                f"expected=4900.00，"
                f"actual="
                f"{account_data.get('balance')}"
            )

        finally:
            # ==================================
            # 清理测试账单
            # ======================================
            #
            # transaction_context fixture
            # 会负责清理：
            #
            # 1. 测试账户；
            # 2. 支出分类；
            # 3. 收入分类。
            #
            # 但是当前测试创建出来的账单
            # 由当前测试自己负责删除。
            #
            # 删除账单时，
            # 后端业务逻辑应该自动：
            #
            # 1. 删除 / 逻辑删除账单；
            # 2. 回滚对应账户余额。
            #
            # ======================================

            if transaction_id:
                # ==================================
                # 删除当前测试账单
                # ==================================

                delete_response = transaction_api.delete_transaction(transaction_id)

                # ==================================
                # 清理阶段不强制断言
                # ======================================
                #
                # 测试主体的失败原因
                # 应该优先保留。
                #
                # 如果清理失败，
                # 这里打印提示即可。
                #
                # ==================================

                if delete_response.status_code != 200:
                    print(
                        f"支出账单测试数据清理失败，"
                        f"transaction_id="
                        f"{transaction_id}，"
                        f"status_code="
                        f"{delete_response.status_code}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("新增账单")
    @allure.title("新增收入账单成功")
    def test_create_income_transaction_success(
        self,
        account_api,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证正常新增收入账单成功。

        测试前置：

        1. transaction_context 自动创建测试账户；
        2. transaction_context 自动创建收入分类；
        3. 测试账户初始余额为 5000.00。

        测试步骤：

        1. 获取测试账户；
        2. 获取收入分类；
        3. 使用 TransactionDataFactory 构造收入账单；
        4. 调用新增账单接口；
        5. 校验新增账单响应；
        6. 查询账户详情；
        7. 验证收入后账户余额正确增加；
        8. 测试结束后自动删除当前账单。

        验证内容：

        1. HTTP 状态码为 200；
        2. 业务 code 为 200；
        3. 返回账单 ID；
        4. 账单类型为 income；
        5. 账单金额正确；
        6. 账户 ID 正确；
        7. 分类 ID 正确；
        8. 收入后账户余额从 5000.00
        正确变为 5500.00。

        当前测试数据：

        初始账户余额：
            5000.00

        收入金额：
            500.00

        预期账户余额：
            5500.00
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        # ======================================
        # 获取账户 ID
        # ======================================

        account_id = account.get("id")

        # ======================================
        # 账户 ID 存在性断言
        # ======================================

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取收入分类
        # ======================================

        income_category = transaction_context.get(
            "income_category",
            {},
        )

        # ======================================
        # 获取收入分类 ID
        # ======================================

        income_category_id = income_category.get("id")

        # ======================================
        # 收入分类 ID 存在性断言
        # ======================================

        assert income_category_id, f"未获取到收入分类 ID：" f"{transaction_context}"

        # ======================================
        # 构造收入账单测试数据
        # ======================================
        #
        # build_income() 会自动：
        #
        # 1. 设置 transaction_type=income；
        # 2. 设置账户 ID；
        # 3. 设置分类 ID；
        # 4. 设置账单金额；
        # 5. 自动生成交易时间；
        # 6. 设置账单备注。
        #
        # 当前测试收入金额：
        #
        # 500.00
        #
        # ======================================

        payload = transaction_factory.build_income(
            account_id=account_id,
            category_id=income_category_id,
            amount="500.00",
            note="自动化测试-新增收入账单",
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        transaction_id = None

        try:
            # ==================================
            # 调用新增账单接口
            # ==================================

            response = transaction_api.create_transaction(payload)

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert response.status_code == 200, (
                f"新增收入账单失败，"
                f"status_code="
                f"{response.status_code}，"
                f"response={response.text}"
            )

            # ==================================
            # 解析响应 JSON
            # ==================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert response_data.get("code") == 200, (
                f"新增收入账单业务失败：" f"{response_data}"
            )

            # ==================================
            # 获取账单数据
            # ==================================

            data = response_data.get(
                "data",
                {},
            )

            # ==================================
            # 获取账单 ID
            # ==================================

            transaction_id = data.get("id")

            assert transaction_id, (
                f"新增收入账单后" f"未返回账单 ID：" f"{response_data}"
            )

            # ==================================
            # 账单类型断言
            # ==================================

            assert data.get("transaction_type") == "income", (
                f"账单类型不正确，"
                f"expected=income，"
                f"actual="
                f"{data.get('transaction_type')}"
            )

            # ==================================
            # 账单金额断言
            # ==================================

            assert data.get("amount") == payload["amount"], (
                f"账单金额不正确，"
                f"expected={payload['amount']}，"
                f"actual={data.get('amount')}"
            )

            # ==================================
            # 账户 ID 断言
            # ======================================

            assert (
                data.get("account") == account_id
                or data.get("account_id") == account_id
            ), (f"账单账户不正确，" f"expected={account_id}，" f"data={data}")

            # ==================================
            # 分类 ID 断言
            # ======================================

            assert (
                data.get("category") == income_category_id
                or data.get("category_id") == income_category_id
            ), (
                f"账单分类不正确，"
                f"expected="
                f"{income_category_id}，"
                f"data={data}"
            )

            # ==================================
            # 查询收入后的账户详情
            # ======================================
            #
            # 初始余额：
            #
            # 5000.00
            #
            # 本次收入：
            #
            # 500.00
            #
            # 预期余额：
            #
            # 5500.00
            #
            # ======================================

            account_response = account_api.get_account_detail(account_id)

            # ==================================
            # 查询账户状态码断言
            # ======================================

            assert account_response.status_code == 200, (
                f"新增收入账单后"
                f"查询账户失败，"
                f"status_code="
                f"{account_response.status_code}，"
                f"response="
                f"{account_response.text}"
            )

            # ==================================
            # 解析账户响应
            # ======================================

            account_response_data = account_response.json()

            # ==================================
            # 账户详情业务状态码断言
            # ======================================

            assert account_response_data.get("code") == 200, (
                f"新增收入账单后" f"查询账户业务失败：" f"{account_response_data}"
            )

            # ==================================
            # 获取账户数据
            # ======================================

            account_data = account_response_data.get(
                "data",
                {},
            )

            # ==================================
            # 收入后账户余额断言
            # ======================================
            #
            # 5000.00 + 500.00
            #
            # = 5500.00
            #
            # ======================================

            assert account_data.get("balance") == "5500.00", (
                f"新增收入账单后账户余额错误，"
                f"expected=5500.00，"
                f"actual="
                f"{account_data.get('balance')}"
            )

        finally:
            # ==================================
            # 清理测试账单
            # ======================================
            #
            # 当前测试创建的收入账单
            # 由本测试自己负责删除。
            #
            # 删除账单后，
            # 后端应该自动回滚：
            #
            # 5500.00 - 500.00
            #
            # 最终恢复到：
            #
            # 5000.00
            #
            # ======================================

            if transaction_id:
                delete_response = transaction_api.delete_transaction(transaction_id)

                # ==================================
                # 清理失败时打印提示
                # ======================================

                if delete_response.status_code != 200:
                    print(
                        f"收入账单测试数据清理失败，"
                        f"transaction_id="
                        f"{transaction_id}，"
                        f"status_code="
                        f"{delete_response.status_code}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("账单详情")
    @allure.title("查询账单详情成功")
    def test_transaction_detail_success(
        self,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证查询账单详情成功。

        测试前置：

        1. transaction_context 自动创建测试账户；
        2. transaction_context 自动创建支出分类；
        3. 当前测试自己创建一笔支出账单。

        测试步骤：

        1. 获取测试账户；
        2. 获取支出分类；
        3. 创建一笔支出账单；
        4. 获取 transaction_id；
        5. 根据 transaction_id 查询账单详情。

        验证内容：

        1. 创建账单成功；
        2. 查询详情 HTTP 状态码为 200；
        3. 业务 code 为 200；
        4. 返回账单 ID 正确；
        5. 账单类型正确；
        6. 账单金额正确；
        7. 账户 ID 正确；
        8. 分类 ID 正确；
        9. 备注正确。

        测试结束后：

        自动删除当前测试创建的账单，
        避免污染数据库。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 构造账单测试数据
        # ======================================
        #
        # 当前创建一笔金额为 120.00
        # 的支出账单。
        #
        # 这里设置固定备注，
        # 后续查询详情时可以精确校验。
        #
        # ======================================

        payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="120.00",
            note="自动化测试-账单详情查询",
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        transaction_id = None

        try:
            # ==================================
            # 创建测试账单
            # ==================================

            create_response = transaction_api.create_transaction(payload)

            # ==================================
            # 创建账单 HTTP 状态码断言
            # ==================================

            assert create_response.status_code == 200, (
                f"创建账单测试数据失败，"
                f"status_code="
                f"{create_response.status_code}，"
                f"response="
                f"{create_response.text}"
            )

            # ==================================
            # 解析创建响应
            # ==================================

            create_response_data = create_response.json()

            # ==================================
            # 创建账单业务状态码断言
            # ==================================

            assert create_response_data.get("code") == 200, (
                f"创建账单测试数据业务失败：" f"{create_response_data}"
            )

            # ==================================
            # 获取创建后的账单数据
            # ==================================

            create_data = create_response_data.get(
                "data",
                {},
            )

            # ==================================
            # 获取 transaction_id
            # ==================================

            transaction_id = create_data.get("id")

            assert transaction_id, (
                f"创建账单后未返回 transaction_id：" f"{create_response_data}"
            )

            # ==================================
            # 查询账单详情
            # ======================================
            #
            # GET
            #
            # /api/v1/transactions/{id}/
            #
            # 已封装在：
            #
            # TransactionApi.get_transaction_detail()
            #
            # ======================================

            response = transaction_api.get_transaction_detail(transaction_id)

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert response.status_code == 200, (
                f"查询账单详情失败，"
                f"status_code="
                f"{response.status_code}，"
                f"response={response.text}"
            )

            # ==================================
            # 解析详情响应
            # ==================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert response_data.get("code") == 200, (
                f"查询账单详情业务失败：" f"{response_data}"
            )

            # ==================================
            # 获取详情数据
            # ==================================

            data = response_data.get(
                "data",
                {},
            )

            # ==================================
            # 账单 ID 断言
            # ==================================

            assert data.get("id") == transaction_id, (
                f"账单详情 ID 不正确，"
                f"expected={transaction_id}，"
                f"actual={data.get('id')}"
            )

            # ==================================
            # 账单类型断言
            # ==================================

            assert data.get("transaction_type") == "expense", (
                f"账单类型不正确，"
                f"expected=expense，"
                f"actual="
                f"{data.get('transaction_type')}"
            )

            # ==================================
            # 账单金额断言
            # ==================================

            assert data.get("amount") == payload["amount"], (
                f"账单金额不正确，"
                f"expected={payload['amount']}，"
                f"actual={data.get('amount')}"
            )

            # ==================================
            # 账户 ID 断言
            # ======================================

            assert (
                data.get("account") == account_id
                or data.get("account_id") == account_id
            ), (f"账单账户不正确，" f"expected={account_id}，" f"data={data}")

            # ==================================
            # 分类 ID 断言
            # ======================================

            assert (
                data.get("category") == expense_category_id
                or data.get("category_id") == expense_category_id
            ), (
                f"账单分类不正确，"
                f"expected="
                f"{expense_category_id}，"
                f"data={data}"
            )

            # ==================================
            # 备注断言
            # ======================================

            assert data.get("note") == payload["note"], (
                f"账单备注不正确，"
                f"expected={payload['note']}，"
                f"actual={data.get('note')}"
            )

        finally:
            # ==================================
            # 清理测试账单
            # ======================================

            if transaction_id:
                delete_response = transaction_api.delete_transaction(transaction_id)

                # ==================================
                # 清理失败时打印提示
                # ======================================

                if delete_response.status_code != 200:
                    print(
                        f"账单详情测试数据清理失败，"
                        f"transaction_id="
                        f"{transaction_id}，"
                        f"status_code="
                        f"{delete_response.status_code}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("修改账单")
    @allure.title("修改账单成功")
    def test_update_transaction_success(
        self,
        account_api,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证修改账单成功。

        测试前置：

        1. transaction_context 自动创建测试账户；
        2. transaction_context 自动创建支出分类；
        3. 当前测试自己创建一笔支出账单。

        测试步骤：

        1. 创建一笔支出账单；
        2. 获取 transaction_id；
        3. 修改账单金额；
        4. 修改账单备注；
        5. 调用修改账单接口；
        6. 查询账单详情；
        7. 验证数据库中的实际数据已经更新；
        8. 验证账户余额根据账单金额变化正确调整。

        当前测试数据：

        初始账户余额：
            5000.00

        原支出金额：
            100.00

        创建账单后余额：
            4900.00

        修改后支出金额：
            200.00

        修改账单后预期余额：
            4800.00

        测试结束后自动删除账单，
        删除后后端应该将账户余额恢复。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 构造原始账单
        # ======================================
        #
        # 原始支出金额：
        #
        # 100.00
        #
        # 创建成功后账户余额应该：
        #
        # 5000.00 - 100.00
        #
        # = 4900.00
        #
        # ======================================

        create_payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="100.00",
            note="自动化测试-修改前账单",
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        transaction_id = None

        try:
            # ==================================
            # 创建原始账单
            # ==================================

            create_response = transaction_api.create_transaction(create_payload)

            # ==================================
            # 创建账单 HTTP 状态码断言
            # ==================================

            assert create_response.status_code == 200, (
                f"创建修改测试账单失败，"
                f"status_code="
                f"{create_response.status_code}，"
                f"response="
                f"{create_response.text}"
            )

            # ==================================
            # 解析创建响应
            # ==================================

            create_response_data = create_response.json()

            # ==================================
            # 创建账单业务状态码断言
            # ==================================

            assert create_response_data.get("code") == 200, (
                f"创建修改测试账单业务失败：" f"{create_response_data}"
            )

            # ==================================
            # 获取账单 ID
            # ==================================

            create_data = create_response_data.get(
                "data",
                {},
            )

            transaction_id = create_data.get("id")

            assert transaction_id, (
                f"创建账单后未返回 transaction_id：" f"{create_response_data}"
            )

            # ==================================
            # 查询创建账单后的账户余额
            # ======================================

            before_update_response = account_api.get_account_detail(account_id)

            assert before_update_response.status_code == 200

            before_update_data = before_update_response.json().get(
                "data",
                {},
            )

            # ==================================
            # 创建账单后余额断言
            # ======================================

            assert before_update_data.get("balance") == "4900.00", (
                f"创建原始账单后账户余额错误，"
                f"expected=4900.00，"
                f"actual="
                f"{before_update_data.get('balance')}"
            )

            # ==================================
            # 构造修改后的账单数据
            # ======================================
            #
            # 当前将支出金额从：
            #
            # 100.00
            #
            # 修改为：
            #
            # 200.00
            #
            # 后端正确逻辑应该：
            #
            # 1. 先撤销原账单影响；
            # 2. 再应用修改后的账单影响。
            #
            # 所以最终余额应该：
            #
            # 5000.00 - 200.00
            #
            # = 4800.00
            #
            # ======================================

            update_payload = {
                "account_id": account_id,
                "category_id": expense_category_id,
                "transaction_type": "expense",
                "amount": "200.00",
                "transaction_time": (create_payload["transaction_time"]),
                "note": "自动化测试-修改后账单",
            }

            # ==================================
            # 调用修改账单接口
            # ======================================

            update_response = transaction_api.update_transaction(
                transaction_id,
                update_payload,
            )

            # ==================================
            # 修改账单 HTTP 状态码断言
            # ======================================

            assert update_response.status_code == 200, (
                f"修改账单失败，"
                f"status_code="
                f"{update_response.status_code}，"
                f"response="
                f"{update_response.text}"
            )

            # ==================================
            # 解析修改响应
            # ======================================

            update_response_data = update_response.json()

            # ==================================
            # 修改账单业务状态码断言
            # ======================================

            assert update_response_data.get("code") == 200, (
                f"修改账单业务失败：" f"{update_response_data}"
            )

            # ==================================
            # 获取修改后的账单数据
            # ======================================

            update_data = update_response_data.get(
                "data",
                {},
            )

            # ==================================
            # 账单 ID 断言
            # ======================================

            assert update_data.get("id") == transaction_id, (
                f"修改账单后 ID 发生变化，"
                f"expected={transaction_id}，"
                f"actual={update_data.get('id')}"
            )

            # ==================================
            # 修改后金额断言
            # ======================================

            assert update_data.get("amount") == update_payload["amount"], (
                f"修改后的账单金额不正确，"
                f"expected="
                f"{update_payload['amount']}，"
                f"actual={update_data.get('amount')}"
            )

            # ==================================
            # 修改后备注断言
            # ======================================

            assert update_data.get("note") == update_payload["note"], (
                f"修改后的账单备注不正确，"
                f"expected="
                f"{update_payload['note']}，"
                f"actual={update_data.get('note')}"
            )

            # ==================================
            # 再次查询账单详情
            # ======================================
            #
            # 不能只验证 PUT 接口返回结果。
            #
            # 再查询详情，
            # 确认数据库实际数据已经更新。
            #
            # ======================================

            detail_response = transaction_api.get_transaction_detail(transaction_id)

            # ==================================
            # 查询详情 HTTP 状态码断言
            # ======================================

            assert detail_response.status_code == 200, (
                f"修改后查询账单详情失败，"
                f"status_code="
                f"{detail_response.status_code}，"
                f"response="
                f"{detail_response.text}"
            )

            # ==================================
            # 解析详情响应
            # ======================================

            detail_response_data = detail_response.json()

            # ==================================
            # 详情接口业务状态码断言
            # ======================================

            assert detail_response_data.get("code") == 200, (
                f"修改后查询账单详情业务失败：" f"{detail_response_data}"
            )

            # ==================================
            # 获取详情数据
            # ======================================

            detail_data = detail_response_data.get(
                "data",
                {},
            )

            # ==================================
            # 数据库实际金额断言
            # ======================================

            assert detail_data.get("amount") == "200.00", (
                f"数据库中的账单金额未正确更新，"
                f"expected=200.00，"
                f"actual={detail_data.get('amount')}"
            )

            # ==================================
            # 数据库实际备注断言
            # ======================================

            assert detail_data.get("note") == "自动化测试-修改后账单", (
                f"数据库中的账单备注未正确更新，" f"actual={detail_data.get('note')}"
            )

            # ==================================
            # 查询修改后的账户余额
            # ======================================

            account_response = account_api.get_account_detail(account_id)

            assert account_response.status_code == 200

            account_response_data = account_response.json()

            assert account_response_data.get("code") == 200

            account_data = account_response_data.get(
                "data",
                {},
            )

            # ==================================
            # 修改账单后的账户余额断言
            # ======================================
            #
            # 正确实现：
            #
            # 原余额影响：
            #
            # -100.00
            #
            # 修改后应该先撤销：
            #
            # +100.00
            #
            # 再应用：
            #
            # -200.00
            #
            # 最终：
            #
            # 5000.00 - 200.00
            #
            # = 4800.00
            #
            # 如果这里出现 4700.00，
            # 就说明后端修改账单时
            # 没有先撤销原账单的余额影响。
            #
            # ======================================

            assert account_data.get("balance") == "4800.00", (
                f"修改账单后账户余额错误，"
                f"expected=4800.00，"
                f"actual="
                f"{account_data.get('balance')}"
            )

        finally:
            # ==================================
            # 清理测试账单
            # ======================================

            if transaction_id:
                delete_response = transaction_api.delete_transaction(transaction_id)

                # ==================================
                # 清理失败只打印提示
                # ======================================

                if delete_response.status_code != 200:
                    print(
                        f"修改账单测试数据清理失败，"
                        f"transaction_id="
                        f"{transaction_id}，"
                        f"status_code="
                        f"{delete_response.status_code}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("删除账单")
    @allure.title("删除账单成功并恢复账户余额")
    def test_delete_transaction_success(
        self,
        account_api,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证删除账单成功，
        并且删除后账户余额正确恢复。

        测试前置：

        1. transaction_context 自动创建测试账户；
        2. 测试账户初始余额为 5000.00；
        3. transaction_context 自动创建支出分类；
        4. 当前测试创建一笔 100.00 的支出账单。

        测试流程：

        1. 创建支出账单；
        2. 验证账户余额由 5000.00 变为 4900.00；
        3. 删除该账单；
        4. 再次查询账户详情；
        5. 验证账户余额恢复为 5000.00；
        6. 再次查询已删除账单；
        7. 验证已删除账单不能正常查询。

        验证内容：

        1. 创建账单成功；
        2. 创建账单后余额扣减正确；
        3. 删除账单接口成功；
        4. 删除账单后余额恢复正确；
        5. 已删除账单不能继续正常查询。

        该测试重点验证：

        删除账单不仅要删除业务数据，
        还必须正确回滚该账单
        对账户余额造成的影响。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 构造支出账单
        # ======================================
        #
        # 初始账户余额：
        #
        # 5000.00
        #
        # 支出金额：
        #
        # 100.00
        #
        # 创建成功后预期余额：
        #
        # 4900.00
        #
        # ======================================

        payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="100.00",
            note="自动化测试-删除账单",
        )

        # ======================================
        # 创建测试账单
        # ======================================

        create_response = transaction_api.create_transaction(payload)

        # ======================================
        # 创建账单 HTTP 状态码断言
        # ======================================

        assert create_response.status_code == 200, (
            f"创建删除测试账单失败，"
            f"status_code="
            f"{create_response.status_code}，"
            f"response={create_response.text}"
        )

        # ======================================
        # 解析创建响应
        # ======================================

        create_response_data = create_response.json()

        # ======================================
        # 创建账单业务状态码断言
        # ======================================

        assert create_response_data.get("code") == 200, (
            f"创建删除测试账单业务失败：" f"{create_response_data}"
        )

        # ======================================
        # 获取账单 ID
        # ======================================

        create_data = create_response_data.get(
            "data",
            {},
        )

        transaction_id = create_data.get("id")

        assert transaction_id, (
            f"创建账单后未返回 transaction_id：" f"{create_response_data}"
        )

        # ======================================
        # 查询创建账单后的账户余额
        # ======================================

        account_response = account_api.get_account_detail(account_id)

        assert account_response.status_code == 200

        account_response_data = account_response.json()

        assert account_response_data.get("code") == 200

        account_data = account_response_data.get(
            "data",
            {},
        )

        # ======================================
        # 创建支出账单后的余额断言
        # ======================================

        assert account_data.get("balance") == "4900.00", (
            f"创建支出账单后账户余额错误，"
            f"expected=4900.00，"
            f"actual="
            f"{account_data.get('balance')}"
        )

        # ======================================
        # 删除账单
        # ======================================

        delete_response = transaction_api.delete_transaction(transaction_id)

        # ======================================
        # 删除账单 HTTP 状态码断言
        # ======================================

        assert delete_response.status_code == 200, (
            f"删除账单失败，"
            f"status_code="
            f"{delete_response.status_code}，"
            f"response={delete_response.text}"
        )

        # ======================================
        # 解析删除响应
        # ======================================

        delete_response_data = delete_response.json()

        # ======================================
        # 删除账单业务状态码断言
        # ======================================

        assert delete_response_data.get("code") == 200, (
            f"删除账单业务失败：" f"{delete_response_data}"
        )

        # ======================================
        # 查询删除后的账户详情
        # ======================================
        #
        # 删除支出账单后，
        # 后端应该撤销这笔支出的余额影响。
        #
        # 原余额：
        #
        # 5000.00
        #
        # 创建支出账单：
        #
        # 4900.00
        #
        # 删除账单：
        #
        # 应恢复到 5000.00
        #
        # ======================================

        after_delete_account_response = account_api.get_account_detail(account_id)

        # ======================================
        # 查询账户状态码断言
        # ======================================

        assert after_delete_account_response.status_code == 200, (
            f"删除账单后查询账户失败，"
            f"status_code="
            f"{after_delete_account_response.status_code}，"
            f"response="
            f"{after_delete_account_response.text}"
        )

        # ======================================
        # 解析账户响应
        # ======================================

        after_delete_account_data = after_delete_account_response.json().get(
            "data",
            {},
        )

        # ======================================
        # 删除后余额恢复断言
        # ======================================

        assert after_delete_account_data.get("balance") == "5000.00", (
            f"删除账单后账户余额未正确恢复，"
            f"expected=5000.00，"
            f"actual="
            f"{after_delete_account_data.get('balance')}"
        )

        # ======================================
        # 再次查询已删除账单
        # ======================================
        #
        # 当前项目账单使用逻辑删除。
        #
        # 因此从正常业务接口角度，
        # 删除后的账单不应该继续正常查询。
        #
        # 具体返回 400 还是 404，
        # 以后端实际实现为准。
        #
        # ======================================

        detail_response = transaction_api.get_transaction_detail(transaction_id)

        detail_response_data = detail_response.json()

        # ======================================
        # 已删除账单不能正常查询
        # ======================================

        assert detail_response_data.get("code") != 200, (
            f"账单已经删除，" f"但仍然可以正常查询：" f"{detail_response_data}"
        )

    @allure.story("账单列表")
    @allure.title("查询账单列表成功")
    def test_transaction_list_success(
        self,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证查询账单列表成功。

        测试前置：

        1. transaction_context 自动创建测试账户；
        2. transaction_context 自动创建支出分类；
        3. 当前测试创建一笔支出账单。

        测试步骤：

        1. 创建一笔真实支出账单；
        2. 获取 transaction_id；
        3. 调用账单列表接口；
        4. 在列表中查找刚刚创建的账单。

        验证内容：

        1. 创建账单成功；
        2. 查询账单列表 HTTP 状态码为 200；
        3. 业务 code 为 200；
        4. 返回数据中存在账单列表；
        5. 当前测试创建的账单存在于列表中；
        6. 账单 ID 正确；
        7. 账单类型正确；
        8. 账单金额正确；
        9. 账户 ID 正确；
        10. 分类 ID 正确；
        11. 备注正确。

        测试结束后，
        自动删除当前测试创建的账单。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 构造测试账单数据
        # ======================================
        #
        # 当前使用唯一备注，
        # 方便后续在列表中定位当前测试数据。
        #
        # ======================================

        payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="88.88",
            note=(transaction_factory.generate_note("自动化测试-账单列表")),
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        transaction_id = None

        try:
            # ==================================
            # 创建测试账单
            # ==================================

            create_response = transaction_api.create_transaction(payload)

            # ==================================
            # 创建账单 HTTP 状态码断言
            # ==================================

            assert create_response.status_code == 200, (
                f"创建账单列表测试数据失败，"
                f"status_code="
                f"{create_response.status_code}，"
                f"response="
                f"{create_response.text}"
            )

            # ==================================
            # 解析创建响应
            # ==================================

            create_response_data = create_response.json()

            # ==================================
            # 创建账单业务状态码断言
            # ==================================

            assert create_response_data.get("code") == 200, (
                f"创建账单列表测试数据业务失败：" f"{create_response_data}"
            )

            # ==================================
            # 获取创建后的账单数据
            # ==================================

            create_data = create_response_data.get(
                "data",
                {},
            )

            transaction_id = create_data.get("id")

            assert transaction_id, (
                f"创建账单后未返回 transaction_id：" f"{create_response_data}"
            )

            # ==================================
            # 查询账单列表
            # ======================================
            #
            # GET
            #
            # /api/v1/transactions/
            #
            # 已封装在：
            #
            # TransactionApi.get_transaction_list()
            #
            # ======================================

            response = transaction_api.get_transaction_list()

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert response.status_code == 200, (
                f"查询账单列表失败，"
                f"status_code="
                f"{response.status_code}，"
                f"response={response.text}"
            )

            # ==================================
            # 解析账单列表响应
            # ==================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert response_data.get("code") == 200, (
                f"查询账单列表业务失败：" f"{response_data}"
            )

            # ==================================
            # 获取 data
            # ==================================

            data = response_data.get(
                "data",
                [],
            )

            # ==================================
            # 兼容分页和非分页结构
            # ======================================
            #
            # 当前列表接口可能返回：
            #
            # {
            #     "data": [...]
            # }
            #
            # 也可能返回：
            #
            # {
            #     "data": {
            #         "results": [...]
            #     }
            # }
            #
            # ======================================

            if isinstance(data, dict):
                transaction_list = data.get(
                    "results",
                    [],
                )

            elif isinstance(data, list):
                transaction_list = data

            else:
                transaction_list = []

            # ==================================
            # 列表结构断言
            # ==================================

            assert isinstance(
                transaction_list,
                list,
            ), (
                f"账单列表数据结构错误：" f"{response_data}"
            )

            # ==================================
            # 查找当前测试账单
            # ======================================
            #
            # 不直接使用：
            #
            # transaction_list[0]
            #
            # 因为列表排序规则可能变化。
            #
            # 最可靠的是根据 transaction_id
            # 查找当前测试创建的账单。
            #
            # ======================================

            current_transaction = next(
                (
                    item
                    for item in transaction_list
                    if (item.get("id") == transaction_id)
                ),
                None,
            )

            # ==================================
            # 当前账单存在性断言
            # ==================================

            assert current_transaction is not None, (
                f"账单列表中未找到当前测试账单，"
                f"transaction_id="
                f"{transaction_id}，"
                f"response={response_data}"
            )

            # ==================================
            # 账单 ID 断言
            # ==================================

            assert current_transaction.get("id") == transaction_id

            # ==================================
            # 账单类型断言
            # ==================================

            assert current_transaction.get("transaction_type") == "expense", (
                f"账单类型不正确，"
                f"actual="
                f"{current_transaction.get('transaction_type')}"
            )

            # ==================================
            # 账单金额断言
            # ==================================

            assert current_transaction.get("amount") == payload["amount"], (
                f"账单金额不正确，"
                f"expected={payload['amount']}，"
                f"actual="
                f"{current_transaction.get('amount')}"
            )

            # ==================================
            # 账户 ID 断言
            # ==================================

            assert (
                current_transaction.get("account") == account_id
                or current_transaction.get("account_id") == account_id
            ), (
                f"账单账户不正确，"
                f"expected={account_id}，"
                f"data={current_transaction}"
            )

            # ==================================
            # 分类 ID 断言
            # ==================================

            assert (
                current_transaction.get("category") == expense_category_id
                or current_transaction.get("category_id") == expense_category_id
            ), (
                f"账单分类不正确，"
                f"expected={expense_category_id}，"
                f"data={current_transaction}"
            )

            # ==================================
            # 账单备注断言
            # ==================================

            assert current_transaction.get("note") == payload["note"], (
                f"账单备注不正确，"
                f"expected={payload['note']}，"
                f"actual="
                f"{current_transaction.get('note')}"
            )

        finally:
            # ==================================
            # 清理测试账单
            # ==================================

            if transaction_id:
                delete_response = transaction_api.delete_transaction(transaction_id)

                # ==================================
                # 清理失败仅打印提示
                # ==================================

                if delete_response.status_code != 200:
                    print(
                        f"账单列表测试数据清理失败，"
                        f"transaction_id="
                        f"{transaction_id}，"
                        f"status_code="
                        f"{delete_response.status_code}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("账单筛选")
    @allure.title("账单条件筛选成功")
    @pytest.mark.parametrize(
        ("filter_type," "expected_type"),
        [
            (
                "transaction_type",
                "expense",
            ),
            (
                "account",
                "expense",
            ),
            (
                "category",
                "expense",
            ),
        ],
        ids=[
            "filter_by_transaction_type",
            "filter_by_account",
            "filter_by_category",
        ],
    )
    def test_transaction_filter_success(
        self,
        transaction_api,
        transaction_factory,
        transaction_context,
        filter_type,
        expected_type,
    ):
        """
        验证账单列表条件筛选功能。

        当前使用 pytest 参数化，
        一条测试方法覆盖多个筛选场景。

        当前覆盖：

        1. 按账单类型筛选；
        2. 按账户筛选；
        3. 按分类筛选。

        测试前置：

        1. transaction_context 自动创建测试账户；
        2. 自动创建支出分类；
        3. 自动创建收入分类；
        4. 当前测试创建：
        - 一笔支出账单；
        - 一笔收入账单。

        测试目标：

        根据不同筛选条件调用账单列表接口，
        并确认当前测试创建的数据
        能够被正确筛选出来。

        参数说明：

        filter_type：

            transaction_type：
                按收支类型筛选。

            account：
                按账户筛选。

            category：
                按分类筛选。

        expected_type：

            当前场景预期返回的账单类型。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id

        # ======================================
        # 获取收入分类
        # ======================================

        income_category = transaction_context.get(
            "income_category",
            {},
        )

        income_category_id = income_category.get("id")

        assert income_category_id

        # ======================================
        # 构造支出账单
        # ======================================
        #
        # 支出账单使用唯一备注，
        # 方便后续精确定位。
        #
        # ======================================

        expense_payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="66.66",
            note=(transaction_factory.generate_note("自动化测试-筛选-支出")),
        )

        # ======================================
        # 构造收入账单
        # ======================================

        income_payload = transaction_factory.build_income(
            account_id=account_id,
            category_id=income_category_id,
            amount="666.66",
            note=(transaction_factory.generate_note("自动化测试-筛选-收入")),
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        expense_id = None
        income_id = None

        try:
            # ==================================
            # 创建支出账单
            # ==================================

            expense_response = transaction_api.create_transaction(expense_payload)

            assert expense_response.status_code == 200, (
                f"创建筛选测试支出账单失败，" f"response={expense_response.text}"
            )

            expense_response_data = expense_response.json()

            assert expense_response_data.get("code") == 200

            expense_data = expense_response_data.get(
                "data",
                {},
            )

            expense_id = expense_data.get("id")

            assert expense_id

            # ==================================
            # 创建收入账单
            # ==================================

            income_response = transaction_api.create_transaction(income_payload)

            assert income_response.status_code == 200, (
                f"创建筛选测试收入账单失败，" f"response={income_response.text}"
            )

            income_response_data = income_response.json()

            assert income_response_data.get("code") == 200

            income_data = income_response_data.get(
                "data",
                {},
            )

            income_id = income_data.get("id")

            assert income_id

            # ==================================
            # 根据参数化场景构造查询条件
            # ======================================

            if filter_type == "transaction_type":
                # ==================================
                # 按支出类型筛选
                # ==================================

                params = {
                    "transaction_type": "expense",
                }

                expected_transaction_id = expense_id

            elif filter_type == "account":
                # ==================================
                # 按账户筛选
                # ==================================
                #
                # 当前收入、支出账单
                # 都属于同一个测试账户。
                #
                # 所以这里重点验证：
                #
                # 当前测试创建的两条账单
                # 都能够出现在筛选结果中。
                #
                # ==================================

                params = {
                    "account": account_id,
                }

                expected_transaction_id = expense_id

            elif filter_type == "category":
                # ==================================
                # 按支出分类筛选
                # ==================================
                #
                # 支出分类只属于
                # 当前支出测试账单。
                #
                # ==================================

                params = {
                    "category_id": (expense_category_id),
                }

                expected_transaction_id = expense_id

            else:
                # ==================================
                # 防止参数化数据配置错误
                # ==================================

                pytest.fail(f"未知 filter_type：" f"{filter_type}")

            # ==================================
            # 调用账单列表筛选接口
            # ======================================

            response = transaction_api.get_transaction_list(params=params)

            # ==================================
            # HTTP 状态码断言
            # ======================================

            assert response.status_code == 200, (
                f"账单筛选失败，"
                f"filter_type={filter_type}，"
                f"params={params}，"
                f"status_code="
                f"{response.status_code}，"
                f"response={response.text}"
            )

            # ==================================
            # 解析响应
            # ======================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ======================================

            assert response_data.get("code") == 200, (
                f"账单筛选业务失败，"
                f"filter_type={filter_type}，"
                f"response={response_data}"
            )

            # ==================================
            # 获取列表数据
            # ======================================

            data = response_data.get(
                "data",
                [],
            )

            # ==================================
            # 兼容分页 / 非分页结构
            # ======================================

            if isinstance(data, dict):
                transaction_list = data.get(
                    "results",
                    [],
                )

            elif isinstance(data, list):
                transaction_list = data

            else:
                transaction_list = []

            # ==================================
            # 列表类型断言
            # ======================================

            assert isinstance(
                transaction_list,
                list,
            )

            # ==================================
            # 查找当前预期账单
            # ======================================

            current_transaction = next(
                (
                    item
                    for item in transaction_list
                    if (item.get("id") == expected_transaction_id)
                ),
                None,
            )

            # ==================================
            # 筛选结果存在性断言
            # ======================================

            assert current_transaction is not None, (
                f"筛选结果中未找到预期账单，"
                f"filter_type={filter_type}，"
                f"params={params}，"
                f"expected_transaction_id="
                f"{expected_transaction_id}，"
                f"response={response_data}"
            )

            # ==================================
            # transaction_type 场景精确断言
            # ======================================

            if filter_type == "transaction_type":
                assert current_transaction.get("transaction_type") == expected_type, (
                    f"按账单类型筛选结果错误，"
                    f"expected={expected_type}，"
                    f"actual="
                    f"{current_transaction.get('transaction_type')}"
                )

                # ==================================
                # 当前收入账单不能出现在
                # expense 筛选结果中
                # ==================================

                income_exists = any(
                    (item.get("id") == income_id) for item in transaction_list
                )

                assert not income_exists, (
                    f"按 expense 筛选后"
                    f"错误返回了收入账单，"
                    f"income_id={income_id}"
                )

            # ==================================
            # account 场景精确断言
            # ======================================

            if filter_type == "account":
                result_ids = {item.get("id") for item in transaction_list}

                assert expense_id in result_ids, (
                    f"按账户筛选后" f"未找到支出账单：" f"{expense_id}"
                )

                assert income_id in result_ids, (
                    f"按账户筛选后" f"未找到收入账单：" f"{income_id}"
                )

            # ==================================
            # category 场景精确断言
            # ======================================

            if filter_type == "category":
                # 收入账单使用另外一个分类，
                # 不应该出现在支出分类结果中。

                income_exists = any(
                    (item.get("id") == income_id) for item in transaction_list
                )

                assert not income_exists, (
                    f"按支出分类筛选后" f"错误返回收入账单，" f"income_id={income_id}"
                )

        finally:
            # ==================================
            # 清理支出账单
            # ======================================

            if expense_id:
                delete_response = transaction_api.delete_transaction(expense_id)

                if delete_response.status_code != 200:
                    print(
                        f"筛选测试支出账单清理失败，"
                        f"transaction_id="
                        f"{expense_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

            # ==================================
            # 清理收入账单
            # ======================================

            if income_id:
                delete_response = transaction_api.delete_transaction(income_id)

                if delete_response.status_code != 200:
                    print(
                        f"筛选测试收入账单清理失败，"
                        f"transaction_id="
                        f"{income_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("账单搜索")
    @allure.title("根据关键词搜索账单成功")
    def test_transaction_search_success(
        self,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证根据关键词搜索账单成功。

        测试前置：

        1. transaction_context 自动创建测试账户；
        2. transaction_context 自动创建支出分类；
        3. 当前测试创建两笔支出账单；
        4. 两笔账单使用不同备注。

        测试步骤：

        1. 创建目标账单 A；
        2. 创建干扰账单 B；
        3. 使用目标账单 A 的唯一关键词执行搜索；
        4. 获取搜索结果；
        5. 验证目标账单 A 存在；
        6. 验证干扰账单 B 不存在。

        验证内容：

        1. 搜索接口 HTTP 状态码为 200；
        2. 业务 code 为 200；
        3. 目标账单能够被搜索出来；
        4. 不匹配关键词的干扰账单不能被返回；
        5. 搜索结果中的账单 ID 正确；
        6. 搜索结果中的备注正确。

        为什么创建两笔账单：

        如果只创建一笔账单，

        即使后端完全忽略 search 参数，
        当前账单仍然可能出现在列表中，

        测试就会出现：

            实际搜索没有生效
            但自动化仍然 PASS

        所以这里额外创建一笔
        不匹配关键词的干扰数据，

        用于真正验证搜索条件是否生效。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 生成目标搜索关键词
        # ======================================
        #
        # 使用 generate_note() 自动生成
        # 带随机后缀的唯一备注。
        #
        # 例如：
        #
        # 自动化搜索目标_a1b2c3d4
        #
        # ======================================

        target_note = transaction_factory.generate_note("自动化搜索目标")

        # ======================================
        # 生成干扰账单备注
        # ======================================

        other_note = transaction_factory.generate_note("自动化搜索干扰")

        # ======================================
        # 构造目标账单
        # ======================================

        target_payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="123.45",
            note=target_note,
        )

        # ======================================
        # 构造干扰账单
        # ======================================

        other_payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="543.21",
            note=other_note,
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        target_id = None
        other_id = None

        try:
            # ==================================
            # 创建目标账单
            # ==================================

            target_response = transaction_api.create_transaction(target_payload)

            # ==================================
            # 目标账单创建状态码断言
            # ==================================

            assert target_response.status_code == 200, (
                f"创建目标搜索账单失败，"
                f"status_code="
                f"{target_response.status_code}，"
                f"response="
                f"{target_response.text}"
            )

            # ==================================
            # 解析目标账单响应
            # ==================================

            target_response_data = target_response.json()

            assert target_response_data.get("code") == 200, (
                f"创建目标搜索账单业务失败：" f"{target_response_data}"
            )

            # ==================================
            # 获取目标账单 ID
            # ==================================

            target_data = target_response_data.get(
                "data",
                {},
            )

            target_id = target_data.get("id")

            assert target_id, (
                f"创建目标搜索账单后"
                f"未返回 transaction_id："
                f"{target_response_data}"
            )

            # ==================================
            # 创建干扰账单
            # ==================================

            other_response = transaction_api.create_transaction(other_payload)

            # ==================================
            # 干扰账单创建状态码断言
            # ==================================

            assert other_response.status_code == 200, (
                f"创建搜索干扰账单失败，"
                f"status_code="
                f"{other_response.status_code}，"
                f"response="
                f"{other_response.text}"
            )

            # ==================================
            # 解析干扰账单响应
            # ==================================

            other_response_data = other_response.json()

            assert other_response_data.get("code") == 200, (
                f"创建搜索干扰账单业务失败：" f"{other_response_data}"
            )

            # ==================================
            # 获取干扰账单 ID
            # ==================================

            other_data = other_response_data.get(
                "data",
                {},
            )

            other_id = other_data.get("id")

            assert other_id, (
                f"创建搜索干扰账单后"
                f"未返回 transaction_id："
                f"{other_response_data}"
            )

            # ==================================
            # 提取搜索关键词
            # ======================================
            # 后端账单列表接口支持：
            #
            # keyword
            #
            # 用于搜索：
            #
            # 商户 / 备注关键字
            #
            # 当前使用完整唯一备注进行搜索，
            # 避免命中其他历史测试数据。
            #
            # target_note 示例：
            #
            # 自动化搜索目标_a1b2c3d4
            #
            # 这里直接使用完整备注搜索，
            # 可以最大程度避免命中其他历史数据。
            #
            # ======================================

            search_keyword = target_note

            # ==================================
            # 构造搜索参数
            # ======================================
            #
            # 根据后端接口定义，
            # 账单关键词搜索参数不是：
            #
            # search
            #
            # 而是：
            #
            # keyword
            #
            # keyword 支持：
            #
            # 商户 / 备注关键字
            #
            # 当前按照常见 DRF SearchFilter
            # 使用：
            #
            # ?search=关键词
            #
            # ======================================

            params = {
                "keyword": search_keyword,
            }

            # ==================================
            # 调用账单列表搜索接口
            # ======================================

            response = transaction_api.get_transaction_list(params=params)

            # ==================================
            # HTTP 状态码断言
            # ======================================

            assert response.status_code == 200, (
                f"账单搜索失败，"
                f"search={search_keyword}，"
                f"status_code="
                f"{response.status_code}，"
                f"response={response.text}"
            )

            # ==================================
            # 解析搜索响应
            # ======================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ======================================

            assert response_data.get("code") == 200, (
                f"账单搜索业务失败，"
                f"search={search_keyword}，"
                f"response={response_data}"
            )

            # ==================================
            # 获取搜索结果 data
            # ======================================

            data = response_data.get(
                "data",
                [],
            )

            # ==================================
            # 兼容分页和非分页结构
            # ======================================

            if isinstance(data, dict):
                transaction_list = data.get(
                    "results",
                    [],
                )

            elif isinstance(data, list):
                transaction_list = data

            else:
                transaction_list = []

            # ==================================
            # 搜索结果类型断言
            # ======================================

            assert isinstance(
                transaction_list,
                list,
            ), (
                f"账单搜索结果结构错误：" f"{response_data}"
            )

            # ==================================
            # 获取搜索结果中的所有账单 ID
            # ======================================

            result_ids = {item.get("id") for item in transaction_list}

            # ==================================
            # 目标账单存在性断言
            # ======================================
            #
            # 搜索目标关键词以后，
            # 目标账单必须出现。
            #
            # ======================================

            assert target_id in result_ids, (
                f"使用目标关键词搜索后"
                f"未找到目标账单，"
                f"search={search_keyword}，"
                f"target_id={target_id}，"
                f"response={response_data}"
            )

            # ==================================
            # 干扰账单排除断言
            # ======================================
            #
            # 干扰账单备注不包含目标关键词，
            # 因此不能出现在搜索结果里。
            #
            # 如果它出现，
            # 很可能说明后端忽略了 search 参数。
            #
            # ======================================

            assert other_id not in result_ids, (
                f"账单搜索条件未正确生效，"
                f"不匹配关键词的干扰账单"
                f"仍然出现在结果中，"
                f"other_id={other_id}，"
                f"search={search_keyword}"
            )

            # ==================================
            # 获取目标账单
            # ======================================

            current_transaction = next(
                (item for item in transaction_list if item.get("id") == target_id),
                None,
            )

            # ==================================
            # 目标账单对象存在性断言
            # ======================================

            assert current_transaction is not None

            # ==================================
            # 目标账单备注断言
            # ======================================

            assert current_transaction.get("note") == target_note, (
                f"搜索结果中的账单备注错误，"
                f"expected={target_note}，"
                f"actual="
                f"{current_transaction.get('note')}"
            )

        finally:
            # ==================================
            # 清理目标账单
            # ======================================

            if target_id:
                delete_response = transaction_api.delete_transaction(target_id)

                if delete_response.status_code != 200:
                    print(
                        f"搜索目标账单清理失败，"
                        f"transaction_id="
                        f"{target_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

            # ==================================
            # 清理干扰账单
            # ======================================

            if other_id:
                delete_response = transaction_api.delete_transaction(other_id)

                if delete_response.status_code != 200:
                    print(
                        f"搜索干扰账单清理失败，"
                        f"transaction_id="
                        f"{other_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("账单筛选")
    @allure.title("按日期范围筛选账单成功")
    def test_transaction_date_range_filter_success(
        self,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证按日期范围筛选账单成功。

        测试思路：

        创建两笔账单：

        1. 目标账单：
        transaction_time = 2026-09-15 12:00:00

        2. 干扰账单：
        transaction_time = 2026-10-05 12:00:00

        然后按照：

            start_date = 2026-09-01
            end_date   = 2026-09-30

        进行筛选。

        预期：

        1. 2026-09-15 的目标账单能够返回；
        2. 2026-10-05 的干扰账单不能返回。

        这样可以真正验证日期筛选条件是否生效，
        而不是只判断接口是否返回 200。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 构造日期范围内的目标账单
        # ======================================

        target_payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="111.11",
            transaction_time=("2026-09-15 12:00:00"),
            note=(transaction_factory.generate_note("自动化测试-日期范围内")),
        )

        # ======================================
        # 构造日期范围外的干扰账单
        # ======================================

        other_payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="222.22",
            transaction_time=("2026-10-05 12:00:00"),
            note=(transaction_factory.generate_note("自动化测试-日期范围外")),
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        target_id = None
        other_id = None

        try:
            # ==================================
            # 创建日期范围内账单
            # ==================================

            target_response = transaction_api.create_transaction(target_payload)

            assert target_response.status_code == 200, (
                f"创建日期范围内账单失败，" f"response=" f"{target_response.text}"
            )

            target_response_data = target_response.json()

            assert target_response_data.get("code") == 200, (
                f"创建日期范围内账单业务失败：" f"{target_response_data}"
            )

            target_data = target_response_data.get(
                "data",
                {},
            )

            target_id = target_data.get("id")

            assert target_id, (
                f"创建日期范围内账单后"
                f"未返回 transaction_id："
                f"{target_response_data}"
            )

            # ==================================
            # 创建日期范围外账单
            # ==================================

            other_response = transaction_api.create_transaction(other_payload)

            assert other_response.status_code == 200, (
                f"创建日期范围外账单失败，" f"response=" f"{other_response.text}"
            )

            other_response_data = other_response.json()

            assert other_response_data.get("code") == 200, (
                f"创建日期范围外账单业务失败：" f"{other_response_data}"
            )

            other_data = other_response_data.get(
                "data",
                {},
            )

            other_id = other_data.get("id")

            assert other_id, (
                f"创建日期范围外账单后"
                f"未返回 transaction_id："
                f"{other_response_data}"
            )

            # ==================================
            # 构造日期范围筛选参数
            # ======================================
            #
            # 根据接口文档：
            #
            # start_date
            # end_date
            #
            # 日期格式：
            #
            # YYYY-MM-DD
            #
            # ======================================

            params = {
                "start_date": "2026-09-01",
                "end_date": "2026-09-30",
            }

            # ==================================
            # 调用账单列表接口
            # ==================================

            response = transaction_api.get_transaction_list(params=params)

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert response.status_code == 200, (
                f"按日期范围筛选账单失败，"
                f"params={params}，"
                f"status_code="
                f"{response.status_code}，"
                f"response={response.text}"
            )

            # ==================================
            # 解析响应
            # ==================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert response_data.get("code") == 200, (
                f"按日期范围筛选业务失败：" f"{response_data}"
            )

            # ==================================
            # 获取 data
            # ==================================

            data = response_data.get(
                "data",
                [],
            )

            # ==================================
            # 兼容分页 / 非分页数据结构
            # ======================================

            if isinstance(data, dict):
                transaction_list = data.get(
                    "results",
                    [],
                )

            elif isinstance(data, list):
                transaction_list = data

            else:
                transaction_list = []

            # ==================================
            # 列表结构断言
            # ==================================

            assert isinstance(
                transaction_list,
                list,
            ), (
                f"日期范围筛选返回结构错误：" f"{response_data}"
            )

            # ==================================
            # 获取结果中的账单 ID
            # ==================================

            result_ids = {item.get("id") for item in transaction_list}

            # ==================================
            # 日期范围内账单必须存在
            # ======================================

            assert target_id in result_ids, (
                f"日期范围内账单未被返回，"
                f"target_id={target_id}，"
                f"params={params}，"
                f"response={response_data}"
            )

            # ==================================
            # 日期范围外账单不能存在
            # ======================================

            assert other_id not in result_ids, (
                f"日期范围筛选未正确生效，"
                f"范围外账单仍然被返回，"
                f"other_id={other_id}，"
                f"params={params}"
            )

            # ==================================
            # 获取目标账单
            # ======================================

            current_transaction = next(
                (item for item in transaction_list if item.get("id") == target_id),
                None,
            )

            # ==================================
            # 目标账单对象存在
            # ======================================

            assert current_transaction is not None

            # ==================================
            # 目标账单时间断言
            # ======================================

            assert (
                current_transaction.get("transaction_time") == "2026-09-15 12:00:00"
            ), (
                f"目标账单时间不正确，"
                f"expected="
                f"2026-09-15 12:00:00，"
                f"actual="
                f"{current_transaction.get('transaction_time')}"
            )

        finally:
            # ==================================
            # 清理日期范围内账单
            # ======================================

            if target_id:
                delete_response = transaction_api.delete_transaction(target_id)

                if delete_response.status_code != 200:
                    print(
                        f"日期范围内账单清理失败，"
                        f"transaction_id="
                        f"{target_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

            # ==================================
            # 清理日期范围外账单
            # ======================================

            if other_id:
                delete_response = transaction_api.delete_transaction(other_id)

                if delete_response.status_code != 200:
                    print(
                        f"日期范围外账单清理失败，"
                        f"transaction_id="
                        f"{other_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("新增账单")
    @allure.title("新增账单异常场景")
    @pytest.mark.parametrize(
        ("case_type," "amount," "expected_code"),
        [
            (
                "zero_amount",
                "0.00",
                400,
            ),
            (
                "negative_amount",
                "-100.00",
                400,
            ),
            (
                "account_not_found",
                "100.00",
                400,
            ),
            (
                "category_not_found",
                "100.00",
                400,
            ),
        ],
        ids=[
            "zero_amount",
            "negative_amount",
            "account_not_found",
            "category_not_found",
        ],
    )
    def test_create_transaction_failed(
        self,
        account_api,
        transaction_api,
        transaction_factory,
        transaction_context,
        case_type,
        amount,
        expected_code,
    ):
        """
        验证新增账单异常场景。

        当前使用 pytest 参数化覆盖：

        1. 金额为 0；
        2. 金额为负数；
        3. 账户不存在；
        4. 分类不存在。

        测试目标：

        对非法账单数据进行提交时，
        后端应该拒绝创建账单。

        同时需要保证：

        1. 接口不能返回业务成功；
        2. 不能生成有效账单 ID；
        3. 非法账单不能影响正常账户余额。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 获取测试前账户余额
        # ======================================
        #
        # transaction_context 创建账户时，
        # 初始余额为：
        #
        # 5000.00
        #
        # 异常账单创建失败后，
        # 余额必须保持不变。
        #
        # ======================================

        before_response = transaction_context.get("account")

        before_balance = before_response.get("balance")

        # ======================================
        # 构造基础账单数据
        # ======================================

        payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount=amount,
            note=(
                transaction_factory.generate_note(f"自动化测试-异常账单-{case_type}")
            ),
        )

        # ======================================
        # 根据不同场景修改测试数据
        # ======================================

        if case_type == "account_not_found":
            # ==================================
            # 使用一个不存在的账户 ID
            # ==================================

            payload["account_id"] = 999999999

        elif case_type == "category_not_found":
            # ==================================
            # 使用一个不存在的分类 ID
            # ==================================

            payload["category_id"] = 999999999

        # ======================================
        # 调用新增账单接口
        # ======================================

        response = transaction_api.create_transaction(payload)

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # HTTP / 业务失败断言
        # ======================================
        #
        # 当前项目统一业务失败
        # 通常返回 code = 400。
        #
        # HTTP 状态码具体可能是：
        #
        # 400
        #
        # 或项目统一封装后仍返回 200。
        #
        # 所以这里重点以业务 code 为准。
        #
        # ======================================
        # ======================================
        # 查询异常请求后的账户余额
        # ======================================

        account_response = account_api.get_account_detail(account_id)

        assert account_response.status_code == 200, (
            f"异常账单测试后查询账户失败，"
            f"case_type={case_type}，"
            f"response={account_response.text}"
        )

        account_response_data = account_response.json()

        assert account_response_data.get("code") == 200

        account_data = account_response_data.get(
            "data",
            {},
        )

        # ======================================
        # 账户余额不能发生变化
        # ======================================
        #
        # 异常账单不能真正写入数据库，
        # 更不能修改账户余额。
        #
        # ======================================

        assert account_data.get("balance") == before_balance, (
            f"异常账单创建失败后"
            f"账户余额发生变化，"
            f"case_type={case_type}，"
            f"expected={before_balance}，"
            f"actual="
            f"{account_data.get('balance')}"
        )
        assert response_data.get("code") == expected_code, (
            f"异常账单场景未按预期失败，"
            f"case_type={case_type}，"
            f"payload={payload}，"
            f"status_code={response.status_code}，"
            f"response={response_data}"
        )

        # ======================================
        # 不能返回有效账单 ID
        # ======================================

        data = response_data.get("data")

        if isinstance(data, dict):
            assert not data.get("id"), (
                f"异常账单创建失败后"
                f"不应该返回有效账单 ID，"
                f"case_type={case_type}，"
                f"data={data}"
            )

        # ======================================
        # 查询账户详情
        # ======================================
        #
        # 只有：
        #
        # zero_amount
        # negative_amount
        # category_not_found
        #
        # 使用的是正常测试账户。
        #
        # account_not_found 使用的是不存在账户，
        # 但仍然需要确认原测试账户
        # 没有被错误影响。
        #
        # ======================================

        # 这里直接重新查询正常测试账户
        # 验证余额没有发生变化。

        from conftest import pytest  # noqa: F401

    @allure.story("新增账单")
    @allure.title("账单类型与分类类型不匹配时创建失败")
    @pytest.mark.parametrize(
        ("transaction_type," "category_type," "expected_code"),
        [
            (
                "expense",
                "income",
                400,
            ),
            (
                "income",
                "expense",
                400,
            ),
        ],
        ids=[
            "expense_with_income_category",
            "income_with_expense_category",
        ],
    )
    def test_create_transaction_category_type_mismatch(
        self,
        account_api,
        transaction_api,
        transaction_factory,
        transaction_context,
        transaction_type,
        category_type,
        expected_code,
    ):
        """
        验证账单类型与分类类型不匹配时，
        后端拒绝创建账单。

        当前覆盖：

        1. expense + income 分类；
        2. income + expense 分类。

        正确业务规则：

        expense：
            只能绑定支出分类。

        income：
            只能绑定收入分类。

        测试同时验证：

        1. 接口返回业务失败；
        2. 不返回有效账单 ID；
        3. 测试账户余额不能发生变化。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取账户测试前余额
        # ======================================

        before_account_response = account_api.get_account_detail(account_id)

        assert before_account_response.status_code == 200, (
            f"查询测试前账户详情失败，" f"response=" f"{before_account_response.text}"
        )

        before_account_response_data = before_account_response.json()

        assert before_account_response_data.get("code") == 200

        before_account_data = before_account_response_data.get(
            "data",
            {},
        )

        before_balance = before_account_data.get("balance")

        assert before_balance is not None

        # ======================================
        # 根据参数获取错误分类
        # ======================================
        #
        # 当前这里故意制造：
        #
        # expense + income 分类
        #
        # 或：
        #
        # income + expense 分类
        #
        # ======================================

        if category_type == "income":
            category = transaction_context.get(
                "income_category",
                {},
            )

        elif category_type == "expense":
            category = transaction_context.get(
                "expense_category",
                {},
            )

        else:
            pytest.fail(f"未知 category_type：" f"{category_type}")

        category_id = category.get("id")

        assert category_id, (
            f"未获取到测试分类 ID，" f"category_type=" f"{category_type}"
        )

        # ======================================
        # 构造不匹配的账单数据
        # ======================================

        payload = transaction_factory.build_transaction(
            account_id=account_id,
            category_id=category_id,
            transaction_type=(transaction_type),
            amount="100.00",
            note=(transaction_factory.generate_note("自动化测试-分类类型不匹配")),
        )

        # ======================================
        # 调用新增账单接口
        # ======================================

        response = transaction_api.create_transaction(payload)

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务失败断言
        # ======================================

        assert response_data.get("code") == expected_code, (
            f"账单类型与分类类型不匹配"
            f"但接口未按预期失败，"
            f"transaction_type="
            f"{transaction_type}，"
            f"category_type="
            f"{category_type}，"
            f"status_code="
            f"{response.status_code}，"
            f"response="
            f"{response_data}"
        )

        # ======================================
        # 不应该返回有效账单 ID
        # ======================================

        data = response_data.get("data")

        if isinstance(data, dict):
            assert not data.get("id"), (
                f"分类类型不匹配时" f"不应该创建账单，" f"但返回了账单 ID：" f"{data}"
            )

        # ======================================
        # 查询异常请求后的账户余额
        # ======================================

        after_account_response = account_api.get_account_detail(account_id)

        assert after_account_response.status_code == 200, (
            f"异常请求后查询账户详情失败，"
            f"response="
            f"{after_account_response.text}"
        )

        after_account_response_data = after_account_response.json()

        assert after_account_response_data.get("code") == 200

        after_account_data = after_account_response_data.get(
            "data",
            {},
        )

        after_balance = after_account_data.get("balance")

        # ======================================
        # 账户余额不能发生变化
        # ======================================
        #
        # 即使请求已经进入业务层，
        # 因为账单最终创建失败，
        #
        # 所以账户余额必须完整回滚。
        #
        # ======================================

        assert after_balance == before_balance, (
            f"账单类型与分类类型不匹配"
            f"创建失败后账户余额发生变化，"
            f"transaction_type="
            f"{transaction_type}，"
            f"category_type="
            f"{category_type}，"
            f"before_balance="
            f"{before_balance}，"
            f"after_balance="
            f"{after_balance}"
        )

    @allure.story("账单分页")
    @allure.title("账单列表分页查询成功")
    def test_transaction_pagination_success(
        self,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证账单列表分页功能。

        测试数据：

        当前测试创建一个独立账户，
        并在该账户下创建 3 笔支出账单。

        分页参数：

            page = 1
            page_size = 2

        预期：

        第 1 页：
            返回 2 条数据。

        第 2 页：
            返回 1 条数据。

        同时验证：

        1. count = 3；
        2. page = 1 / 2；
        3. page_size = 2；
        4. total_pages = 2；
        5. has_next；
        6. has_previous；
        7. 两页数据合并后，
        正好包含当前测试创建的 3 笔账单。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 保存当前测试创建的账单 ID
        # ======================================

        transaction_ids = []

        try:
            # ==================================
            # 创建 3 笔测试账单
            # ======================================

            for index in range(1, 4):

                payload = transaction_factory.build_expense(
                    account_id=account_id,
                    category_id=expense_category_id,
                    amount=f"{index * 10}.00",
                    note=(
                        transaction_factory.generate_note(f"自动化测试-分页-{index}")
                    ),
                )

                response = transaction_api.create_transaction(payload)

                # ==================================
                # 创建账单 HTTP 状态码断言
                # ==================================

                assert response.status_code == 200, (
                    f"创建分页测试账单失败，"
                    f"index={index}，"
                    f"response={response.text}"
                )

                # ==================================
                # 解析创建响应
                # ==================================

                response_data = response.json()

                assert response_data.get("code") == 200, (
                    f"创建分页测试账单业务失败，"
                    f"index={index}，"
                    f"response={response_data}"
                )

                # ==================================
                # 获取账单 ID
                # ==================================

                data = response_data.get(
                    "data",
                    {},
                )

                transaction_id = data.get("id")

                assert transaction_id, (
                    f"第 {index} 笔分页测试账单" f"未返回 transaction_id"
                )

                transaction_ids.append(transaction_id)

            # ======================================
            # 确认成功创建 3 笔账单
            # ======================================

            assert len(transaction_ids) == 3

            # ======================================
            # 查询第 1 页
            # ======================================
            #
            # 使用 account_id 隔离当前测试数据。
            #
            # transaction_context 每次测试都会
            # 创建独立账户，
            #
            # 因此理论上当前账户下
            # 只有这 3 笔账单。
            #
            # ======================================

            first_page_params = {
                "account_id": account_id,
                "page": 1,
                "page_size": 2,
            }

            first_page_response = transaction_api.get_transaction_list(
                params=first_page_params
            )

            # ======================================
            # 第 1 页 HTTP 状态码断言
            # ======================================

            assert first_page_response.status_code == 200, (
                f"查询账单第 1 页失败，" f"response=" f"{first_page_response.text}"
            )

            # ======================================
            # 解析第 1 页响应
            # ======================================

            first_response_data = first_page_response.json()

            assert first_response_data.get("code") == 200, (
                f"查询账单第 1 页业务失败：" f"{first_response_data}"
            )

            # ======================================
            # 获取分页 data
            # ======================================

            first_data = first_response_data.get(
                "data",
                {},
            )

            assert isinstance(
                first_data,
                dict,
            ), (
                f"分页接口 data 结构错误：" f"{first_response_data}"
            )

            # ======================================
            # 第 1 页分页字段断言
            # ======================================

            assert first_data.get("count") == 3, (
                f"分页总数量错误，" f"expected=3，" f"actual={first_data.get('count')}"
            )

            assert first_data.get("page") == 1, (
                f"当前页错误，" f"expected=1，" f"actual={first_data.get('page')}"
            )

            assert first_data.get("page_size") == 2, (
                f"分页大小错误，"
                f"expected=2，"
                f"actual={first_data.get('page_size')}"
            )

            assert first_data.get("total_pages") == 2, (
                f"总页数错误，"
                f"expected=2，"
                f"actual={first_data.get('total_pages')}"
            )

            # ======================================
            # 第 1 页翻页状态
            # ======================================

            assert first_data.get("has_next") is True, (
                f"第 1 页应该存在下一页，" f"data={first_data}"
            )

            assert first_data.get("has_previous") is False, (
                f"第 1 页不应该存在上一页，" f"data={first_data}"
            )

            # ======================================
            # 获取第 1 页 results
            # ======================================

            first_results = first_data.get(
                "results",
                [],
            )

            assert isinstance(
                first_results,
                list,
            )

            assert len(first_results) == 2, (
                f"第 1 页返回数量错误，" f"expected=2，" f"actual={len(first_results)}"
            )

            # ======================================
            # 查询第 2 页
            # ======================================

            second_page_params = {
                "account_id": account_id,
                "page": 2,
                "page_size": 2,
            }

            second_page_response = transaction_api.get_transaction_list(
                params=second_page_params
            )

            # ======================================
            # 第 2 页 HTTP 状态码断言
            # ======================================

            assert second_page_response.status_code == 200, (
                f"查询账单第 2 页失败，" f"response=" f"{second_page_response.text}"
            )

            # ======================================
            # 解析第 2 页响应
            # ======================================

            second_response_data = second_page_response.json()

            assert second_response_data.get("code") == 200, (
                f"查询账单第 2 页业务失败：" f"{second_response_data}"
            )

            second_data = second_response_data.get(
                "data",
                {},
            )

            # ======================================
            # 第 2 页分页字段断言
            # ======================================

            assert second_data.get("count") == 3

            assert second_data.get("page") == 2

            assert second_data.get("page_size") == 2

            assert second_data.get("total_pages") == 2

            # ======================================
            # 第 2 页翻页状态
            # ======================================

            assert second_data.get("has_next") is False, (
                f"第 2 页不应该存在下一页，" f"data={second_data}"
            )

            assert second_data.get("has_previous") is True, (
                f"第 2 页应该存在上一页，" f"data={second_data}"
            )

            # ======================================
            # 获取第 2 页 results
            # ======================================

            second_results = second_data.get(
                "results",
                [],
            )

            assert isinstance(
                second_results,
                list,
            )

            assert len(second_results) == 1, (
                f"第 2 页返回数量错误，" f"expected=1，" f"actual={len(second_results)}"
            )

            # ======================================
            # 合并两页账单 ID
            # ======================================

            first_page_ids = {item.get("id") for item in first_results}

            second_page_ids = {item.get("id") for item in second_results}

            result_ids = first_page_ids | second_page_ids

            expected_ids = set(transaction_ids)

            # ======================================
            # 分页完整性断言
            # ======================================
            #
            # 两页合并后，
            # 必须和当前测试创建的 3 条数据
            # 完全一致。
            #
            # 这样同时验证：
            #
            # 1. 没有漏数据；
            # 2. 没有重复数据；
            # 3. 没有混入其他账户的数据。
            #
            # ======================================

            assert result_ids == expected_ids, (
                f"分页结果数据不完整或存在异常，"
                f"expected={expected_ids}，"
                f"actual={result_ids}"
            )

            # ======================================
            # 两页不能出现重复账单
            # ======================================

            duplicate_ids = first_page_ids & second_page_ids

            assert not duplicate_ids, (
                f"分页结果出现重复账单，" f"duplicate_ids=" f"{duplicate_ids}"
            )

        finally:
            # ======================================
            # 清理当前测试创建的全部账单
            # ======================================

            for transaction_id in transaction_ids:

                delete_response = transaction_api.delete_transaction(transaction_id)

                if delete_response.status_code != 200:
                    print(
                        f"分页测试账单清理失败，"
                        f"transaction_id="
                        f"{transaction_id}，"
                        f"status_code="
                        f"{delete_response.status_code}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("账单统计")
    @allure.title("账单汇总统计成功")
    def test_transaction_summary_success(
        self,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证账单汇总统计接口。

        当前测试采用：

            统计前数据
                ↓
            创建测试账单
                ↓
            统计后数据
                ↓
            比较前后差值

        而不是直接断言：

            total_income = 500.00
            total_expense = 100.00

        原因：

        当前测试用户数据库中可能已经存在历史账单，
        summary 接口会统计这些历史账单。

        如果直接断言固定总金额，
        测试会受到历史数据影响。

        当前创建：

        收入：
            +500.00

        支出：
            +100.00

        所以预期：

        total_income：
            增加 500.00

        total_expense：
            增加 100.00

        balance：
            增加 400.00

        income_count：
            增加 1

        expense_count：
            增加 1

        total_count：
            增加 2
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 获取收入分类
        # ======================================

        income_category = transaction_context.get(
            "income_category",
            {},
        )

        income_category_id = income_category.get("id")

        assert income_category_id, f"未获取到收入分类 ID：" f"{transaction_context}"

        # ======================================
        # 查询创建账单前的汇总数据
        # ======================================
        #
        # 当前不再依赖 account_id
        # 对 summary 接口进行数据隔离。
        #
        # 直接记录整个用户当前的统计基线。
        #
        # ======================================

        before_response = transaction_api.get_summary()

        assert before_response.status_code == 200, (
            f"查询创建账单前汇总统计失败，" f"response={before_response.text}"
        )

        before_response_data = before_response.json()

        assert before_response_data.get("code") == 200, (
            f"查询创建账单前汇总统计业务失败：" f"{before_response_data}"
        )

        before_data = before_response_data.get(
            "data",
            {},
        )

        # ======================================
        # 保存创建前统计数据
        # ======================================

        before_income = Decimal(
            before_data.get(
                "total_income",
                "0.00",
            )
        )

        before_expense = Decimal(
            before_data.get(
                "total_expense",
                "0.00",
            )
        )

        before_balance = Decimal(
            before_data.get(
                "balance",
                "0.00",
            )
        )

        before_income_count = before_data.get(
            "income_count",
            0,
        )

        before_expense_count = before_data.get(
            "expense_count",
            0,
        )

        before_total_count = before_data.get(
            "total_count",
            0,
        )

        # ======================================
        # 构造支出账单
        # ======================================

        expense_payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="100.00",
            note=(transaction_factory.generate_note("自动化测试-汇总统计-支出")),
        )

        # ======================================
        # 构造收入账单
        # ======================================

        income_payload = transaction_factory.build_income(
            account_id=account_id,
            category_id=income_category_id,
            amount="500.00",
            note=(transaction_factory.generate_note("自动化测试-汇总统计-收入")),
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        expense_id = None
        income_id = None

        try:
            # ==================================
            # 创建支出账单
            # ==================================

            expense_response = transaction_api.create_transaction(expense_payload)

            assert expense_response.status_code == 200, (
                f"创建汇总统计支出账单失败，" f"response={expense_response.text}"
            )

            expense_response_data = expense_response.json()

            assert expense_response_data.get("code") == 200, (
                f"创建汇总统计支出账单业务失败：" f"{expense_response_data}"
            )

            expense_data = expense_response_data.get(
                "data",
                {},
            )

            expense_id = expense_data.get("id")

            assert expense_id

            # ==================================
            # 创建收入账单
            # ==================================

            income_response = transaction_api.create_transaction(income_payload)

            assert income_response.status_code == 200, (
                f"创建汇总统计收入账单失败，" f"response={income_response.text}"
            )

            income_response_data = income_response.json()

            assert income_response_data.get("code") == 200, (
                f"创建汇总统计收入账单业务失败：" f"{income_response_data}"
            )

            income_data = income_response_data.get(
                "data",
                {},
            )

            income_id = income_data.get("id")

            assert income_id

            # ==================================
            # 查询创建账单后的汇总数据
            # ==================================

            after_response = transaction_api.get_summary()

            assert after_response.status_code == 200, (
                f"查询创建账单后汇总统计失败，" f"response={after_response.text}"
            )

            after_response_data = after_response.json()

            assert after_response_data.get("code") == 200, (
                f"查询创建账单后汇总统计业务失败：" f"{after_response_data}"
            )

            after_data = after_response_data.get(
                "data",
                {},
            )

            # ==================================
            # 获取创建后统计数据
            # ==================================

            after_income = Decimal(
                after_data.get(
                    "total_income",
                    "0.00",
                )
            )

            after_expense = Decimal(
                after_data.get(
                    "total_expense",
                    "0.00",
                )
            )

            after_balance = Decimal(
                after_data.get(
                    "balance",
                    "0.00",
                )
            )

            after_income_count = after_data.get(
                "income_count",
                0,
            )

            after_expense_count = after_data.get(
                "expense_count",
                0,
            )

            after_total_count = after_data.get(
                "total_count",
                0,
            )

            # ==================================
            # 总收入增量断言
            # ======================================
            #
            # 新增收入：
            #
            # 500.00
            #
            # ==================================

            assert round(
                after_income - before_income,
                2,
            ) == Decimal("500.00"), (
                f"账单收入汇总增量错误，"
                f"before={before_income}，"
                f"after={after_income}，"
                f"expected_increment=500.00"
            )

            # ==================================
            # 总支出增量断言
            # ======================================

            assert round(
                after_expense - before_expense,
                2,
            ) == Decimal("100.00"), (
                f"账单支出汇总增量错误，"
                f"before={before_expense}，"
                f"after={after_expense}，"
                f"expected_increment=100.00"
            )

            # ==================================
            # 收支结余增量断言
            # ======================================
            #
            # 新增：
            #
            # +500 收入
            # -100 支出
            #
            # 净变化：
            #
            # +400
            #
            # ==================================

            assert round(
                after_balance - before_balance,
                2,
            ) == Decimal("400.00"), (
                f"账单收支结余增量错误，"
                f"before={before_balance}，"
                f"after={after_balance}，"
                f"expected_increment=400.00"
            )

            # ==================================
            # 收入账单数量断言
            # ======================================

            assert after_income_count - before_income_count == 1, (
                f"收入账单数量统计错误，"
                f"before={before_income_count}，"
                f"after={after_income_count}"
            )

            # ==================================
            # 支出账单数量断言
            # ======================================

            assert after_expense_count - before_expense_count == 1, (
                f"支出账单数量统计错误，"
                f"before={before_expense_count}，"
                f"after={after_expense_count}"
            )

            # ==================================
            # 总账单数量断言
            # ======================================

            assert after_total_count - before_total_count == 2, (
                f"账单总数量统计错误，"
                f"before={before_total_count}，"
                f"after={after_total_count}"
            )

        finally:
            # ==================================
            # 清理支出账单
            # ==================================

            if expense_id:
                delete_response = transaction_api.delete_transaction(expense_id)

                if delete_response.status_code != 200:
                    print(
                        f"汇总统计支出账单清理失败，"
                        f"transaction_id="
                        f"{expense_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

            # ==================================
            # 清理收入账单
            # ==================================

            if income_id:
                delete_response = transaction_api.delete_transaction(income_id)

                if delete_response.status_code != 200:
                    print(
                        f"汇总统计收入账单清理失败，"
                        f"transaction_id="
                        f"{income_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("账单统计")
    @allure.title("账单收支趋势统计成功")
    def test_transaction_trend_success(
        self,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证账单收支趋势统计接口。

        当前测试采用：

            创建测试数据前查询趋势
                    ↓
            记录当前日期统计基线
                    ↓
            创建一笔收入账单
            创建一笔支出账单
                    ↓
            再次查询趋势
                    ↓
            验证当前日期统计增量

        当前创建：

            收入：
                500.00

            支出：
                100.00

        所以预期：

            income：
                增加 500.00

            expense：
                增加 100.00

            balance：
                增加 400.00

        使用增量验证的好处：

        即使当前日期数据库中已经存在
        其他历史测试账单，

        也不会影响当前自动化测试结果。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 获取收入分类
        # ======================================

        income_category = transaction_context.get(
            "income_category",
            {},
        )

        income_category_id = income_category.get("id")

        assert income_category_id, f"未获取到收入分类 ID：" f"{transaction_context}"

        # ======================================
        # 构造支出账单
        # ======================================
        #
        # TransactionDataFactory 默认使用
        # 当前系统时间生成 transaction_time。
        #
        # 后面直接从这里提取当前测试日期。
        #
        # ======================================

        expense_payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="100.00",
            note=(transaction_factory.generate_note("自动化测试-趋势统计-支出")),
        )

        # ======================================
        # 构造收入账单
        # ======================================

        income_payload = transaction_factory.build_income(
            account_id=account_id,
            category_id=income_category_id,
            amount="500.00",
            note=(transaction_factory.generate_note("自动化测试-趋势统计-收入")),
        )

        # ======================================
        # 获取当前测试日期
        # ======================================
        #
        # transaction_time 示例：
        #
        # 2026-10-09 22:30:00
        #
        # 截取：
        #
        # 2026-10-09
        #
        # ======================================

        current_date = expense_payload["transaction_time"][:10]

        # ======================================
        # 定义内部辅助方法
        # ======================================
        #
        # 用于从 trend 返回列表中
        # 获取指定日期的数据。
        #
        # 如果当前日期不存在，
        # 说明当天原本没有账单，
        #
        # 则默认：
        #
        # income  = 0.00
        # expense = 0.00
        # balance = 0.00
        #
        # ======================================

        def get_trend_by_date(
            trend_data,
            target_date,
        ):
            for item in trend_data:
                if item.get("date") == target_date:
                    return item

            return {
                "date": target_date,
                "income": "0.00",
                "expense": "0.00",
                "balance": "0.00",
            }

        # ======================================
        # 查询创建账单前的趋势数据
        # ======================================

        before_response = transaction_api.get_trend()

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert before_response.status_code == 200, (
            f"查询创建账单前趋势统计失败，"
            f"status_code="
            f"{before_response.status_code}，"
            f"response="
            f"{before_response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        before_response_data = before_response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert before_response_data.get("code") == 200, (
            f"查询创建账单前趋势统计业务失败：" f"{before_response_data}"
        )

        # ======================================
        # 获取创建前趋势列表
        # ======================================

        before_data = before_response_data.get(
            "data",
            [],
        )

        assert isinstance(
            before_data,
            list,
        ), (
            f"创建前趋势统计 data " f"结构错误：" f"{before_response_data}"
        )

        # ======================================
        # 获取当前日期创建前统计
        # ======================================

        before_today = get_trend_by_date(
            before_data,
            current_date,
        )

        # ======================================
        # 转换为 Decimal
        # ======================================
        #
        # 金融金额测试统一使用 Decimal，
        # 避免 float 精度问题。
        #
        # ======================================

        before_income = Decimal(
            before_today.get(
                "income",
                "0.00",
            )
        )

        before_expense = Decimal(
            before_today.get(
                "expense",
                "0.00",
            )
        )

        before_balance = Decimal(
            before_today.get(
                "balance",
                "0.00",
            )
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        expense_id = None
        income_id = None

        try:
            # ==================================
            # 创建支出账单
            # ==================================

            expense_response = transaction_api.create_transaction(expense_payload)

            assert expense_response.status_code == 200, (
                f"创建趋势统计支出账单失败，" f"response=" f"{expense_response.text}"
            )

            expense_response_data = expense_response.json()

            assert expense_response_data.get("code") == 200, (
                f"创建趋势统计支出账单" f"业务失败：" f"{expense_response_data}"
            )

            expense_data = expense_response_data.get(
                "data",
                {},
            )

            expense_id = expense_data.get("id")

            assert expense_id, (
                f"创建趋势统计支出账单后"
                f"未返回 transaction_id："
                f"{expense_response_data}"
            )

            # ==================================
            # 创建收入账单
            # ==================================

            income_response = transaction_api.create_transaction(income_payload)

            assert income_response.status_code == 200, (
                f"创建趋势统计收入账单失败，" f"response=" f"{income_response.text}"
            )

            income_response_data = income_response.json()

            assert income_response_data.get("code") == 200, (
                f"创建趋势统计收入账单" f"业务失败：" f"{income_response_data}"
            )

            income_data = income_response_data.get(
                "data",
                {},
            )

            income_id = income_data.get("id")

            assert income_id, (
                f"创建趋势统计收入账单后"
                f"未返回 transaction_id："
                f"{income_response_data}"
            )

            # ==================================
            # 查询创建账单后的趋势数据
            # ==================================

            after_response = transaction_api.get_trend()

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert after_response.status_code == 200, (
                f"查询创建账单后趋势统计失败，"
                f"status_code="
                f"{after_response.status_code}，"
                f"response="
                f"{after_response.text}"
            )

            # ==================================
            # 解析响应
            # ==================================

            after_response_data = after_response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert after_response_data.get("code") == 200, (
                f"查询创建账单后趋势统计" f"业务失败：" f"{after_response_data}"
            )

            # ==================================
            # 获取趋势列表
            # ==================================

            after_data = after_response_data.get(
                "data",
                [],
            )

            assert isinstance(
                after_data,
                list,
            ), (
                f"创建后趋势统计 data " f"结构错误：" f"{after_response_data}"
            )

            # ==================================
            # 获取当前日期统计
            # ==================================

            after_today = get_trend_by_date(
                after_data,
                current_date,
            )

            # ==================================
            # 当前日期必须真实存在
            # ======================================
            #
            # 创建账单以后，
            # 当前日期应该已经出现在
            # trend 返回列表中。
            #
            # ==================================

            assert any((item.get("date") == current_date) for item in after_data), (
                f"创建账单后趋势统计中"
                f"未找到当前日期，"
                f"current_date={current_date}，"
                f"data={after_data}"
            )

            # ==================================
            # 转换创建后金额
            # ==================================

            after_income = Decimal(
                after_today.get(
                    "income",
                    "0.00",
                )
            )

            after_expense = Decimal(
                after_today.get(
                    "expense",
                    "0.00",
                )
            )

            after_balance = Decimal(
                after_today.get(
                    "balance",
                    "0.00",
                )
            )

            # ==================================
            # 收入趋势增量断言
            # ======================================
            #
            # 当前新增：
            #
            # +500.00
            #
            # ==================================

            income_increment = after_income - before_income

            assert income_increment == Decimal("500.00"), (
                f"当天收入趋势增量错误，"
                f"date={current_date}，"
                f"before={before_income}，"
                f"after={after_income}，"
                f"expected_increment=500.00"
            )

            # ==================================
            # 支出趋势增量断言
            # ======================================
            #
            # 当前新增：
            #
            # +100.00
            #
            # ==================================

            expense_increment = after_expense - before_expense

            assert expense_increment == Decimal("100.00"), (
                f"当天支出趋势增量错误，"
                f"date={current_date}，"
                f"before={before_expense}，"
                f"after={after_expense}，"
                f"expected_increment=100.00"
            )

            # ==================================
            # 收支结余增量断言
            # ======================================
            #
            # 500.00 - 100.00
            #
            # = 400.00
            #
            # ==================================

            balance_increment = after_balance - before_balance

            assert balance_increment == Decimal("400.00"), (
                f"当天收支结余趋势增量错误，"
                f"date={current_date}，"
                f"before={before_balance}，"
                f"after={after_balance}，"
                f"expected_increment=400.00"
            )

            # ==================================
            # balance 计算关系断言
            # ======================================
            #
            # trend 中每一天应该满足：
            #
            # balance
            # =
            # income - expense
            #
            # ==================================

            assert after_balance == (after_income - after_expense), (
                f"当天趋势 balance "
                f"计算关系错误，"
                f"income={after_income}，"
                f"expense={after_expense}，"
                f"balance={after_balance}"
            )

        finally:
            # ==================================
            # 清理支出账单
            # ==================================

            if expense_id:
                delete_response = transaction_api.delete_transaction(expense_id)

                if delete_response.status_code != 200:
                    print(
                        f"趋势统计支出账单"
                        f"清理失败，"
                        f"transaction_id="
                        f"{expense_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

            # ==================================
            # 清理收入账单
            # ==================================

            if income_id:
                delete_response = transaction_api.delete_transaction(income_id)

                if delete_response.status_code != 200:
                    print(
                        f"趋势统计收入账单"
                        f"清理失败，"
                        f"transaction_id="
                        f"{income_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("账单统计")
    @allure.title("账单分类统计成功")
    def test_transaction_category_statistics_success(
        self,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证账单分类统计接口。

        当前测试验证支出分类统计。

        测试流程：

        1. 查询创建账单前的支出分类统计；
        2. 获取当前测试支出分类的统计基线；
        3. 创建一笔 123.45 的支出账单；
        4. 再次查询支出分类统计；
        5. 找到当前测试支出分类；
        6. 验证分类金额增加 123.45；
        7. 验证分类账单数量增加 1；
        8. 验证支出总金额增加 123.45。

        分类统计接口实际返回结构：

        {
            "code": 200,
            "message": "获取分类统计成功",
            "data": {
                "transaction_type": "expense",
                "total_amount": "655.80",
                "categories": [
                    {
                        "category_id": 2,
                        "category_name": "餐饮",
                        "amount": "655.80",
                        "count": 3,
                        "percentage": "100.00"
                    }
                ]
            }
        }

        注意：

        category-statistics 接口要求：

            transaction_type

        为必填参数。

        当前测试使用：

            transaction_type = expense

        为什么使用“基线 + 增量”：

        数据库中可能已经存在历史账单，
        所以不能直接断言：

            total_amount = 123.45

        而应该验证：

            创建后金额 - 创建前金额
            = 123.45

        这样测试不会受到历史数据影响。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        expense_category_name = expense_category.get("name")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 定义分类统计查找方法
        # ======================================
        #
        # 根据 category_id
        # 从 categories 中找到
        # 当前测试分类。
        #
        # ======================================

        def find_category_statistics(
            statistics_data,
            target_category_id,
        ):
            for item in statistics_data:

                if item.get("category_id") == target_category_id:
                    return item

            return None

        # ======================================
        # 构造分类统计查询参数
        # ======================================
        #
        # category-statistics 接口要求：
        #
        # transaction_type
        #
        # 为必填参数。
        #
        # 当前测试验证支出分类，
        # 所以使用：
        #
        # expense
        #
        # ======================================

        params = {
            "transaction_type": "expense",
        }

        # ======================================
        # 查询创建账单前的分类统计
        # ======================================

        before_response = transaction_api.get_category_statistics(params=params)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert before_response.status_code == 200, (
            f"查询创建账单前分类统计失败，"
            f"status_code="
            f"{before_response.status_code}，"
            f"response="
            f"{before_response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        before_response_data = before_response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert before_response_data.get("code") == 200, (
            f"查询创建账单前分类统计业务失败：" f"{before_response_data}"
        )

        # ======================================
        # 获取 data
        # ======================================

        before_data = before_response_data.get(
            "data",
            {},
        )

        # ======================================
        # data 结构断言
        # ======================================

        assert isinstance(
            before_data,
            dict,
        ), (
            f"分类统计 data 结构错误：" f"{before_response_data}"
        )

        # ======================================
        # transaction_type 断言
        # ======================================

        assert before_data.get("transaction_type") == "expense", (
            f"分类统计 transaction_type 错误，"
            f"expected=expense，"
            f"actual="
            f"{before_data.get('transaction_type')}"
        )

        # ======================================
        # 获取创建前支出总金额
        # ======================================

        before_total_amount = Decimal(
            str(
                before_data.get(
                    "total_amount",
                    "0.00",
                )
            )
        )

        # ======================================
        # 获取 categories
        # ======================================

        before_categories = before_data.get(
            "categories",
            [],
        )

        # ======================================
        # categories 结构断言
        # ======================================

        assert isinstance(
            before_categories,
            list,
        ), (
            f"分类统计 categories 结构错误：" f"{before_data}"
        )

        # ======================================
        # 查找当前测试分类
        # ======================================

        before_category = find_category_statistics(
            before_categories,
            expense_category_id,
        )

        # ======================================
        # 获取当前分类创建前金额
        # ======================================
        #
        # transaction_context 每次测试
        # 创建新的分类。
        #
        # 正常情况下创建账单之前，
        # 该分类不会出现在统计结果中。
        #
        # 此时：
        #
        # amount = 0.00
        # count  = 0
        #
        # ======================================

        if before_category is None:

            before_amount = Decimal("0.00")

            before_count = 0

        else:

            before_amount = Decimal(
                str(
                    before_category.get(
                        "amount",
                        "0.00",
                    )
                )
            )

            before_count = before_category.get(
                "count",
                0,
            )

        # ======================================
        # 构造测试账单
        # ======================================
        #
        # 当前新增一笔：
        #
        # expense
        #
        # 金额：
        #
        # 123.45
        #
        # ======================================

        payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="123.45",
            note=(transaction_factory.generate_note("自动化测试-分类统计")),
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        transaction_id = None

        try:
            # ==================================
            # 创建测试账单
            # ==================================

            create_response = transaction_api.create_transaction(payload)

            # ==================================
            # 创建账单 HTTP 状态码断言
            # ==================================

            assert create_response.status_code == 200, (
                f"创建分类统计测试账单失败，"
                f"status_code="
                f"{create_response.status_code}，"
                f"response="
                f"{create_response.text}"
            )

            # ==================================
            # 解析创建响应
            # ==================================

            create_response_data = create_response.json()

            # ==================================
            # 创建账单业务状态码断言
            # ==================================

            assert create_response_data.get("code") == 200, (
                f"创建分类统计测试账单业务失败：" f"{create_response_data}"
            )

            # ==================================
            # 获取创建后的账单数据
            # ==================================

            create_data = create_response_data.get(
                "data",
                {},
            )

            # ==================================
            # 获取 transaction_id
            # ==================================

            transaction_id = create_data.get("id")

            assert transaction_id, (
                f"创建分类统计测试账单后"
                f"未返回 transaction_id："
                f"{create_response_data}"
            )

            # ==================================
            # 查询创建账单后的分类统计
            # ==================================

            after_response = transaction_api.get_category_statistics(params=params)

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert after_response.status_code == 200, (
                f"查询创建账单后分类统计失败，"
                f"status_code="
                f"{after_response.status_code}，"
                f"response="
                f"{after_response.text}"
            )

            # ==================================
            # 解析响应
            # ==================================

            after_response_data = after_response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert after_response_data.get("code") == 200, (
                f"查询创建账单后分类统计业务失败：" f"{after_response_data}"
            )

            # ==================================
            # 获取 data
            # ==================================

            after_data = after_response_data.get(
                "data",
                {},
            )

            # ==================================
            # data 结构断言
            # ==================================

            assert isinstance(
                after_data,
                dict,
            ), (
                f"创建后分类统计 data " f"结构错误：" f"{after_response_data}"
            )

            # ==================================
            # transaction_type 断言
            # ==================================

            assert after_data.get("transaction_type") == "expense", (
                f"创建后分类统计 "
                f"transaction_type 错误，"
                f"expected=expense，"
                f"actual="
                f"{after_data.get('transaction_type')}"
            )

            # ==================================
            # 获取创建后支出总金额
            # ==================================

            after_total_amount = Decimal(
                str(
                    after_data.get(
                        "total_amount",
                        "0.00",
                    )
                )
            )

            # ==================================
            # 获取 categories
            # ==================================

            after_categories = after_data.get(
                "categories",
                [],
            )

            # ==================================
            # categories 结构断言
            # ==================================

            assert isinstance(
                after_categories,
                list,
            ), (
                f"创建后 categories " f"结构错误：" f"{after_data}"
            )

            # ==================================
            # 查找当前测试分类
            # ==================================

            after_category = find_category_statistics(
                after_categories,
                expense_category_id,
            )

            # ==================================
            # 当前分类必须存在
            # ======================================

            assert after_category is not None, (
                f"分类统计中未找到当前测试分类，"
                f"category_id="
                f"{expense_category_id}，"
                f"category_name="
                f"{expense_category_name}，"
                f"categories="
                f"{after_categories}"
            )

            # ==================================
            # 分类 ID 断言
            # ==================================

            assert after_category.get("category_id") == expense_category_id, (
                f"分类统计 category_id 错误，"
                f"expected="
                f"{expense_category_id}，"
                f"actual="
                f"{after_category.get('category_id')}"
            )

            # ==================================
            # 分类名称断言
            # ======================================

            assert after_category.get("category_name") == expense_category_name, (
                f"分类统计 category_name 错误，"
                f"expected="
                f"{expense_category_name}，"
                f"actual="
                f"{after_category.get('category_name')}"
            )

            # ==================================
            # 获取创建后分类金额
            # ==================================

            after_amount = Decimal(
                str(
                    after_category.get(
                        "amount",
                        "0.00",
                    )
                )
            )

            # ==================================
            # 获取创建后分类账单数量
            # ==================================

            after_count = after_category.get(
                "count",
                0,
            )

            # ==================================
            # 分类金额增量断言
            # ======================================
            #
            # 当前新增：
            #
            # 123.45
            #
            # 所以：
            #
            # after_amount
            # -
            # before_amount
            #
            # 应该等于：
            #
            # 123.45
            #
            # ======================================

            amount_increment = after_amount - before_amount

            assert amount_increment == Decimal("123.45"), (
                f"分类统计金额增量错误，"
                f"category_id="
                f"{expense_category_id}，"
                f"before="
                f"{before_amount}，"
                f"after="
                f"{after_amount}，"
                f"expected_increment="
                f"123.45"
            )

            # ==================================
            # 分类账单数量增量断言
            # ======================================
            #
            # 当前只新增一笔账单，
            #
            # 所以：
            #
            # count + 1
            #
            # ======================================

            count_increment = after_count - before_count

            assert count_increment == 1, (
                f"分类统计账单数量增量错误，"
                f"category_id="
                f"{expense_category_id}，"
                f"before_count="
                f"{before_count}，"
                f"after_count="
                f"{after_count}，"
                f"expected_increment=1"
            )

            # ==================================
            # 支出总金额增量断言
            # ======================================
            #
            # 当前新增一笔支出：
            #
            # 123.45
            #
            # 因此整个 expense 类型的
            # total_amount 也应该增加：
            #
            # 123.45
            #
            # ======================================

            total_amount_increment = after_total_amount - before_total_amount

            assert total_amount_increment == Decimal("123.45"), (
                f"支出分类总金额增量错误，"
                f"before="
                f"{before_total_amount}，"
                f"after="
                f"{after_total_amount}，"
                f"expected_increment="
                f"123.45"
            )

            # ==================================
            # percentage 字段存在性断言
            # ======================================
            #
            # 当前接口返回：
            #
            # percentage
            #
            # 表示当前分类金额
            # 在该收支类型总金额中的占比。
            #
            # 当前这里只验证字段存在，
            # 后面可以单独设计
            # 多分类占比精确计算测试。
            #
            # ======================================

            assert after_category.get("percentage") is not None, (
                f"分类统计结果缺少 " f"percentage 字段：" f"{after_category}"
            )

        finally:
            # ==================================
            # 清理测试账单
            # ======================================

            if transaction_id:

                delete_response = transaction_api.delete_transaction(transaction_id)

                # ==================================
                # 清理失败仅打印提示
                # ==================================

                if delete_response.status_code != 200:
                    print(
                        f"分类统计测试账单"
                        f"清理失败，"
                        f"transaction_id="
                        f"{transaction_id}，"
                        f"status_code="
                        f"{delete_response.status_code}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("账单统计")
    @allure.title("账单月度统计成功")
    def test_transaction_monthly_statistics_success(
        self,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证账单月度统计接口。

        接口实际返回结构：

        {
            "code": 200,
            "message": "获取月度统计成功",
            "data": {
                "current_month": "2026-10",
                "previous_month": "2026-09",
                "current": {
                    "income": "500.00",
                    "expense": "220.00",
                    "balance": "280.00"
                },
                "previous": {
                    "income": "4400.00",
                    "expense": "535.80",
                    "balance": "3864.20"
                },
                "comparison": {
                    "income_rate": "-88.64",
                    "expense_rate": "-58.94"
                }
            }
        }

        当前测试采用：

            创建账单前查询月度统计
                    ↓
            记录当前月份统计基线
                    ↓
            创建收入 500.00
            创建支出 100.00
                    ↓
            再次查询月度统计
                    ↓
            验证当前月份统计增量

        预期：

            current.income：
                增加 500.00

            current.expense：
                增加 100.00

            current.balance：
                增加 400.00

        为什么使用基线 + 增量：

        当前月份可能已经存在历史账单，
        因此不能直接断言：

            income = 500.00
            expense = 100.00

        而应该验证：

            创建后 - 创建前

        是否等于本次测试新增金额。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 获取收入分类
        # ======================================

        income_category = transaction_context.get(
            "income_category",
            {},
        )

        income_category_id = income_category.get("id")

        assert income_category_id, f"未获取到收入分类 ID：" f"{transaction_context}"

        # ======================================
        # 查询创建账单前的月度统计
        # ======================================

        before_response = transaction_api.get_monthly_statistics()

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert before_response.status_code == 200, (
            f"查询创建账单前月度统计失败，"
            f"status_code="
            f"{before_response.status_code}，"
            f"response="
            f"{before_response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        before_response_data = before_response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert before_response_data.get("code") == 200, (
            f"查询创建账单前月度统计业务失败：" f"{before_response_data}"
        )

        # ======================================
        # 获取 data
        # ======================================

        before_data = before_response_data.get(
            "data",
            {},
        )

        assert isinstance(
            before_data,
            dict,
        ), (
            f"月度统计 data 结构错误：" f"{before_response_data}"
        )

        # ======================================
        # 获取当前月份
        # ======================================

        current_month = before_data.get("current_month")

        previous_month = before_data.get("previous_month")

        assert current_month, f"月度统计缺少 current_month：" f"{before_data}"

        assert previous_month, f"月度统计缺少 previous_month：" f"{before_data}"

        # ======================================
        # 获取当前月统计
        # ======================================

        before_current = before_data.get(
            "current",
            {},
        )

        assert isinstance(
            before_current,
            dict,
        ), (
            f"月度统计 current 结构错误：" f"{before_data}"
        )

        # ======================================
        # 当前月基线金额
        # ======================================

        before_income = Decimal(
            str(
                before_current.get(
                    "income",
                    "0.00",
                )
            )
        )

        before_expense = Decimal(
            str(
                before_current.get(
                    "expense",
                    "0.00",
                )
            )
        )

        before_balance = Decimal(
            str(
                before_current.get(
                    "balance",
                    "0.00",
                )
            )
        )

        # ======================================
        # 获取上月统计
        # ======================================
        #
        # 当前测试只创建本月账单，
        # 所以理论上 previous
        # 不应该发生变化。
        #
        # 后面会一起验证。
        #
        # ======================================

        before_previous = before_data.get(
            "previous",
            {},
        )

        assert isinstance(
            before_previous,
            dict,
        )

        before_previous_income = Decimal(
            str(
                before_previous.get(
                    "income",
                    "0.00",
                )
            )
        )

        before_previous_expense = Decimal(
            str(
                before_previous.get(
                    "expense",
                    "0.00",
                )
            )
        )

        before_previous_balance = Decimal(
            str(
                before_previous.get(
                    "balance",
                    "0.00",
                )
            )
        )

        # ======================================
        # 构造支出账单
        # ======================================

        expense_payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="100.00",
            note=(transaction_factory.generate_note("自动化测试-月度统计-支出")),
        )

        # ======================================
        # 构造收入账单
        # ======================================

        income_payload = transaction_factory.build_income(
            account_id=account_id,
            category_id=income_category_id,
            amount="500.00",
            note=(transaction_factory.generate_note("自动化测试-月度统计-收入")),
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        expense_id = None
        income_id = None

        try:
            # ==================================
            # 创建支出账单
            # ==================================

            expense_response = transaction_api.create_transaction(expense_payload)

            assert expense_response.status_code == 200, (
                f"创建月度统计支出账单失败，" f"response=" f"{expense_response.text}"
            )

            expense_response_data = expense_response.json()

            assert expense_response_data.get("code") == 200, (
                f"创建月度统计支出账单业务失败：" f"{expense_response_data}"
            )

            expense_data = expense_response_data.get(
                "data",
                {},
            )

            expense_id = expense_data.get("id")

            assert expense_id, (
                f"创建月度统计支出账单后"
                f"未返回 transaction_id："
                f"{expense_response_data}"
            )

            # ==================================
            # 创建收入账单
            # ==================================

            income_response = transaction_api.create_transaction(income_payload)

            assert income_response.status_code == 200, (
                f"创建月度统计收入账单失败，" f"response=" f"{income_response.text}"
            )

            income_response_data = income_response.json()

            assert income_response_data.get("code") == 200, (
                f"创建月度统计收入账单业务失败：" f"{income_response_data}"
            )

            income_data = income_response_data.get(
                "data",
                {},
            )

            income_id = income_data.get("id")

            assert income_id, (
                f"创建月度统计收入账单后"
                f"未返回 transaction_id："
                f"{income_response_data}"
            )

            # ==================================
            # 查询创建后的月度统计
            # ==================================

            after_response = transaction_api.get_monthly_statistics()

            assert after_response.status_code == 200, (
                f"查询创建账单后月度统计失败，" f"response=" f"{after_response.text}"
            )

            # ==================================
            # 解析响应
            # ==================================

            after_response_data = after_response.json()

            assert after_response_data.get("code") == 200, (
                f"查询创建账单后月度统计业务失败：" f"{after_response_data}"
            )

            after_data = after_response_data.get(
                "data",
                {},
            )

            assert isinstance(
                after_data,
                dict,
            )

            # ==================================
            # 月份不能发生变化
            # ======================================

            assert after_data.get("current_month") == current_month, (
                f"测试过程中 current_month "
                f"发生变化，"
                f"before={current_month}，"
                f"after="
                f"{after_data.get('current_month')}"
            )

            assert after_data.get("previous_month") == previous_month

            # ==================================
            # 获取创建后当前月统计
            # ======================================

            after_current = after_data.get(
                "current",
                {},
            )

            assert isinstance(
                after_current,
                dict,
            )

            after_income = Decimal(
                str(
                    after_current.get(
                        "income",
                        "0.00",
                    )
                )
            )

            after_expense = Decimal(
                str(
                    after_current.get(
                        "expense",
                        "0.00",
                    )
                )
            )

            after_balance = Decimal(
                str(
                    after_current.get(
                        "balance",
                        "0.00",
                    )
                )
            )

            # ==================================
            # 当前月收入增量断言
            # ======================================

            assert after_income - before_income == Decimal("500.00"), (
                f"当前月收入统计增量错误，"
                f"month={current_month}，"
                f"before={before_income}，"
                f"after={after_income}，"
                f"expected_increment=500.00"
            )

            # ==================================
            # 当前月支出增量断言
            # ======================================

            assert after_expense - before_expense == Decimal("100.00"), (
                f"当前月支出统计增量错误，"
                f"month={current_month}，"
                f"before={before_expense}，"
                f"after={after_expense}，"
                f"expected_increment=100.00"
            )

            # ==================================
            # 当前月结余增量断言
            # ======================================
            #
            # +500 收入
            # -100 支出
            #
            # = +400
            #
            # ======================================

            assert after_balance - before_balance == Decimal("400.00"), (
                f"当前月结余统计增量错误，"
                f"month={current_month}，"
                f"before={before_balance}，"
                f"after={after_balance}，"
                f"expected_increment=400.00"
            )

            # ==================================
            # 当前月 balance 计算关系断言
            # ======================================

            assert after_balance == (after_income - after_expense), (
                f"当前月 balance 计算错误，"
                f"income={after_income}，"
                f"expense={after_expense}，"
                f"balance={after_balance}"
            )

            # ==================================
            # 获取创建后的上月统计
            # ======================================

            after_previous = after_data.get(
                "previous",
                {},
            )

            assert isinstance(
                after_previous,
                dict,
            )

            after_previous_income = Decimal(
                str(
                    after_previous.get(
                        "income",
                        "0.00",
                    )
                )
            )

            after_previous_expense = Decimal(
                str(
                    after_previous.get(
                        "expense",
                        "0.00",
                    )
                )
            )

            after_previous_balance = Decimal(
                str(
                    after_previous.get(
                        "balance",
                        "0.00",
                    )
                )
            )

            # ==================================
            # 上月数据不能被本月账单影响
            # ======================================

            assert after_previous_income == before_previous_income, (
                f"创建本月账单后"
                f"上月收入发生变化，"
                f"before="
                f"{before_previous_income}，"
                f"after="
                f"{after_previous_income}"
            )

            assert after_previous_expense == before_previous_expense, (
                f"创建本月账单后"
                f"上月支出发生变化，"
                f"before="
                f"{before_previous_expense}，"
                f"after="
                f"{after_previous_expense}"
            )

            assert after_previous_balance == before_previous_balance, (
                f"创建本月账单后"
                f"上月结余发生变化，"
                f"before="
                f"{before_previous_balance}，"
                f"after="
                f"{after_previous_balance}"
            )

            # ==================================
            # comparison 字段存在性断言
            # ======================================
            #
            # 当前先验证字段结构。
            #
            # 环比百分比的精确计算
            # 后续可以独立设计测试，
            # 因为还需要确认：
            #
            # 1. 四舍五入规则；
            # 2. 上月为 0 时的处理规则。
            #
            # ======================================

            comparison = after_data.get(
                "comparison",
                {},
            )

            assert isinstance(
                comparison,
                dict,
            ), (
                f"月度统计 comparison " f"结构错误：" f"{after_data}"
            )

            assert comparison.get("income_rate") is not None, (
                f"comparison 缺少 " f"income_rate：" f"{comparison}"
            )

            assert comparison.get("expense_rate") is not None, (
                f"comparison 缺少 " f"expense_rate：" f"{comparison}"
            )

        finally:
            # ==================================
            # 清理支出账单
            # ==================================

            if expense_id:

                delete_response = transaction_api.delete_transaction(expense_id)

                if delete_response.status_code != 200:
                    print(
                        f"月度统计支出账单"
                        f"清理失败，"
                        f"transaction_id="
                        f"{expense_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

            # ==================================
            # 清理收入账单
            # ==================================

            if income_id:

                delete_response = transaction_api.delete_transaction(income_id)

                if delete_response.status_code != 200:
                    print(
                        f"月度统计收入账单"
                        f"清理失败，"
                        f"transaction_id="
                        f"{income_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("账单统计")
    @allure.title("获取账单年度统计成功")
    def test_transaction_yearly_statistics_success(
        self,
        transaction_api,
        transaction_factory,
        transaction_context,
    ):
        """
        验证账单年度统计接口可以正常返回数据。

        当前测试主要确认：

        1. yearly-statistics 接口 HTTP 状态码；
        2. 业务 code；
        3. data 是否存在；
        4. 年度统计真实返回结构；
        5. 当前创建的收入、支出账单是否进入年度统计。

        当前暂时不直接猜字段结构。

        原因：

        前面的统计接口：

        summary
        trend
        category-statistics
        monthly-statistics

        返回结构都不完全一致。

        所以这里先创建明确数据，
        再输出 yearly-statistics 的真实响应。

        下一步根据真实结构，
        再升级成正式的“基线 + 增量”测试。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        account = transaction_context.get(
            "account",
            {},
        )

        account_id = account.get("id")

        assert account_id, f"未获取到账单测试账户 ID：" f"{transaction_context}"

        # ======================================
        # 获取支出分类
        # ======================================

        expense_category = transaction_context.get(
            "expense_category",
            {},
        )

        expense_category_id = expense_category.get("id")

        assert expense_category_id, f"未获取到支出分类 ID：" f"{transaction_context}"

        # ======================================
        # 获取收入分类
        # ======================================

        income_category = transaction_context.get(
            "income_category",
            {},
        )

        income_category_id = income_category.get("id")

        assert income_category_id, f"未获取到收入分类 ID：" f"{transaction_context}"

        # ======================================
        # 构造年度统计支出账单
        # ======================================
        #
        # 使用当前系统时间，
        # 确保账单进入当前年度统计。
        #
        # ======================================

        expense_payload = transaction_factory.build_expense(
            account_id=account_id,
            category_id=expense_category_id,
            amount="100.00",
            note=(transaction_factory.generate_note("自动化测试-年度统计-支出")),
        )

        # ======================================
        # 构造年度统计收入账单
        # ======================================

        income_payload = transaction_factory.build_income(
            account_id=account_id,
            category_id=income_category_id,
            amount="500.00",
            note=(transaction_factory.generate_note("自动化测试-年度统计-收入")),
        )

        # ======================================
        # 初始化账单 ID
        # ======================================

        expense_id = None
        income_id = None

        try:
            # ==================================
            # 创建支出账单
            # ==================================

            expense_response = transaction_api.create_transaction(expense_payload)

            assert expense_response.status_code == 200, (
                f"创建年度统计支出账单失败，"
                f"status_code="
                f"{expense_response.status_code}，"
                f"response="
                f"{expense_response.text}"
            )

            expense_response_data = expense_response.json()

            assert expense_response_data.get("code") == 200, (
                f"创建年度统计支出账单业务失败：" f"{expense_response_data}"
            )

            expense_data = expense_response_data.get(
                "data",
                {},
            )

            expense_id = expense_data.get("id")

            assert expense_id, (
                f"创建年度统计支出账单后"
                f"未返回 transaction_id："
                f"{expense_response_data}"
            )

            # ==================================
            # 创建收入账单
            # ==================================

            income_response = transaction_api.create_transaction(income_payload)

            assert income_response.status_code == 200, (
                f"创建年度统计收入账单失败，"
                f"status_code="
                f"{income_response.status_code}，"
                f"response="
                f"{income_response.text}"
            )

            income_response_data = income_response.json()

            assert income_response_data.get("code") == 200, (
                f"创建年度统计收入账单业务失败：" f"{income_response_data}"
            )

            income_data = income_response_data.get(
                "data",
                {},
            )

            income_id = income_data.get("id")

            assert income_id, (
                f"创建年度统计收入账单后"
                f"未返回 transaction_id："
                f"{income_response_data}"
            )

            # ==================================
            # 调用年度统计接口
            # ======================================

            response = transaction_api.get_yearly_statistics()

            # ==================================
            # HTTP 状态码断言
            # ======================================

            assert response.status_code == 200, (
                f"查询账单年度统计失败，"
                f"status_code="
                f"{response.status_code}，"
                f"response="
                f"{response.text}"
            )

            # ==================================
            # 解析响应
            # ======================================

            response_data = response.json()

            # ==================================
            # 临时输出真实响应结构
            # ======================================
            #
            # 下一步字段确认后，
            # 会删除这些 print，
            # 改成正式金额和数量断言。
            #
            # ======================================

            print("\n========== 账单年度统计 ==========")

            print(
                "请求 URL：",
                response.request.url,
            )

            print(
                "接口响应：",
                response_data,
            )

            print("==================================")

            # ==================================
            # 业务状态码断言
            # ======================================

            assert response_data.get("code") == 200, (
                f"查询账单年度统计业务失败：" f"{response_data}"
            )

            # ==================================
            # data 字段存在性断言
            # ======================================

            assert "data" in response_data, (
                f"年度统计响应缺少 data 字段：" f"{response_data}"
            )

            # ==================================
            # data 不能为空
            # ======================================

            data = response_data.get("data")

            assert data is not None, f"年度统计 data 为 None：" f"{response_data}"

        finally:
            # ==================================
            # 清理支出账单
            # ==================================

            if expense_id:

                delete_response = transaction_api.delete_transaction(expense_id)

                if delete_response.status_code != 200:
                    print(
                        f"年度统计支出账单"
                        f"清理失败，"
                        f"transaction_id="
                        f"{expense_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

            # ==================================
            # 清理收入账单
            # ==================================

            if income_id:

                delete_response = transaction_api.delete_transaction(income_id)

                if delete_response.status_code != 200:
                    print(
                        f"年度统计收入账单"
                        f"清理失败，"
                        f"transaction_id="
                        f"{income_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )
