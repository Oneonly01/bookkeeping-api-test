from datetime import datetime
import allure
import uuid

import pytest


@allure.feature("账户管理")
class TestAccount:
    """
    账户接口自动化测试。

    当前覆盖：

    1. 新增账户成功；
    2. 查询账户列表成功。
    """

    @allure.story("新增账户")
    @allure.title("新增账户成功")
    def test_create_account_success(
        self,
        account_api,
        account_factory,
    ):
        """
        验证正常新增账户。

        验证内容：

        1. 创建账户接口请求成功；
        2. HTTP 状态码为 200；
        3. 业务 code 为 200；
        4. 返回账户 ID；
        5. 返回账户名称与请求参数一致；
        6. 测试结束后自动清理测试账户。
        """

        # ======================================
        # 构造账户测试数据
        # ======================================
        #
        # 测试数据统一由 AccountDataFactory 生成。
        #
        # 优点：
        #
        # 1. 自动生成唯一账户名称；
        # 2. 避免重复执行测试时账户名称冲突；
        # 3. 测试用例不需要重复维护 payload；
        # 4. 后续接口字段变化时统一修改数据工厂。
        #
        # ======================================

        payload = account_factory.build_account(
            initial_balance="1000.00",
            note="新增账户自动化测试",
        )

        # ======================================
        # 初始化账户 ID
        # ======================================
        #
        # 如果账户创建成功，
        # account_id 会保存接口返回的账户 ID。
        #
        # finally 中根据这个 ID 清理测试数据。
        #
        # 如果创建失败，
        # account_id 保持 None，
        # 不执行删除操作。
        #
        # ======================================

        account_id = None

        try:
            # ==================================
            # 调用创建账户接口
            # ==================================
            #
            # URL、HTTP 方法等细节
            # 已经封装在 AccountApi 中。
            #
            # 测试用例只负责传入测试数据。
            #
            # ==================================

            response = account_api.create_account(payload)

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert response.status_code == 200, (
                f"新增账户接口请求失败，"
                f"status_code={response.status_code}，"
                f"response={response.text}"
            )

            # ==================================
            # 解析 JSON 响应
            # ==================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ======================================

            assert response_data.get("code") == 200, (
                f"新增账户业务执行失败：" f"{response_data}"
            )

            # ==================================
            # 获取响应 data
            # ==================================

            data = response_data.get(
                "data",
                {},
            )

            # ==================================
            # 获取账户 ID
            # ======================================

            account_id = data.get("id")

            # 新增成功后必须返回账户 ID。
            assert account_id

            # ==================================
            # 账户名称断言
            # ======================================
            #
            # 验证后端实际保存并返回的账户名称
            # 与本次请求中的名称一致。
            #
            # ==================================

            assert data.get("name") == payload["name"]

            # ==================================
            # 账户类型断言
            # ======================================

            assert data.get("account_type") == payload["account_type"]

            # ==================================
            # 初始余额断言
            # ======================================
            #
            # 如果创建接口返回 initial_balance，
            # 则验证其与请求参数一致。
            #
            # ==================================

            assert data.get("initial_balance") == payload["initial_balance"]

        finally:
            # ==================================
            # 自动清理测试数据
            # ======================================
            #
            # 自动化测试不应该长期污染数据库。
            #
            # 当前后端规则：
            #
            # 账户余额不为 0 时不能删除。
            #
            # 所以这里先：
            #
            # 1. 将账户余额调整为 0；
            # 2. 再删除测试账户。
            #
            # 即使前面的断言失败，
            # finally 仍会执行。
            #
            # ==================================

            if account_id:
                # ==================================
                # 将测试账户余额归零
                # ==================================

                account_api.adjust_balance(
                    account_id,
                    {
                        "balance": "0.00",
                        "note": "自动化测试数据清理",
                    },
                )

                # ==================================
                # 删除测试账户
                # ==================================

                account_api.delete_account(account_id)

    @allure.story("账户详情")
    @allure.title("查询账户详情成功")
    def test_account_detail_success(
        self,
        account_api,
        test_account,
    ):
        """
        验证查询账户详情成功。

        验证内容：

        1. 使用 fixture 自动创建测试账户；
        2. 根据账户 ID 查询账户详情；
        3. HTTP 状态码为 200；
        4. 业务 code 为 200；
        5. 返回账户 ID 正确；
        6. 返回账户名称正确。

        测试完成后，
        test_account fixture 会自动清理测试数据，
        当前测试方法无需处理删除逻辑。
        """

        # ======================================
        # 获取 fixture 创建的账户 ID
        # ======================================

        account_id = test_account.get("id")

        # ======================================
        # 调用账户详情接口
        # ======================================
        #
        # URL 拼接和 GET 请求已经封装到
        # AccountApi.get_account_detail()。
        #
        # ======================================

        response = account_api.get_account_detail(account_id)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"查询账户详情失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"查询账户详情业务失败：" f"{response_data}"
        )

        # ======================================
        # 获取响应数据
        # ======================================

        data = response_data.get(
            "data",
            {},
        )

        # ======================================
        # 账户 ID 断言
        # ======================================

        assert data.get("id") == test_account.get("id")

        # ======================================
        # 账户名称断言
        # ======================================

        assert data.get("name") == test_account.get("name")

        # ======================================
        # 账户类型断言
        # ======================================

        assert data.get("account_type") == test_account.get("account_type")

    @allure.story("修改账户")
    @allure.title("修改账户成功")
    def test_update_account_success(
        self,
        account_api,
        test_account,
    ):
        """
        验证修改账户成功。

        验证内容：

        1. 使用 test_account fixture 自动创建测试账户；
        2. 修改账户名称；
        3. 修改账户颜色；
        4. 修改账户排序值；
        5. HTTP 状态码为 200；
        6. 业务 code 为 200；
        7. 接口返回的数据与修改参数一致；
        8. 再次查询账户详情，
        验证数据库中的实际数据已经更新。

        测试结束后，
        test_account fixture 会自动：

        1. 将账户余额调整为 0；
        2. 删除测试账户。

        因此当前测试方法不需要自己编写 finally 清理逻辑。
        """

        # ======================================
        # 获取测试账户 ID
        # ======================================
        #
        # test_account fixture 会在测试执行前
        # 自动创建一个真实账户。
        #
        # fixture 返回的是创建账户接口中的 data。
        #
        # ======================================

        account_id = test_account.get("id")

        # ======================================
        # 构造修改账户数据
        # ======================================
        #
        # 账户名称继续使用 UUID，
        # 避免和数据库中已有账户发生重名。
        #
        # 当前修改以下字段：
        #
        # 1. name
        # 2. color
        # 3. sort_order
        #
        # 这些字段都是当前账户接口
        # 已经实际支持并返回的字段。
        #
        # ======================================

        payload = {
            "name": ("修改后的自动化账户_" f"{uuid.uuid4().hex[:8]}"),
            "color": "#27BA9B",
            "sort_order": 9,
        }

        # ======================================
        # 调用修改账户接口
        # ======================================
        #
        # URL 拼接和 PUT 请求已经封装在：
        #
        # AccountApi.update_account()
        #
        # 测试用例只需要传：
        #
        # 1. account_id
        # 2. payload
        #
        # ======================================

        response = account_api.update_account(
            account_id,
            payload,
        )

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"修改账户接口请求失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"修改账户业务执行失败：" f"{response_data}"
        )

        # ======================================
        # 获取修改后的账户数据
        # ======================================

        data = response_data.get(
            "data",
            {},
        )

        # ======================================
        # 账户 ID 断言
        # ======================================
        #
        # 修改账户后，
        # 账户本身的 ID 不应该发生变化。
        #
        # ======================================

        assert data.get("id") == account_id

        # ======================================
        # 账户名称断言
        # ======================================

        assert data.get("name") == payload["name"]

        # ======================================
        # 账户颜色断言
        # ======================================

        assert data.get("color") == payload["color"]

        # ======================================
        # 排序值断言
        # ======================================

        assert data.get("sort_order") == payload["sort_order"]

        # ======================================
        # 再次查询账户详情
        # ======================================
        #
        # 为什么不能只验证 PUT 接口返回值？
        #
        # 因为接口返回正确，
        # 不一定代表数据库真的已经更新。
        #
        # 所以这里再次调用详情接口，
        # 做一次真实数据验证。
        #
        # ======================================

        detail_response = account_api.get_account_detail(account_id)

        # ======================================
        # 查询详情 HTTP 状态码断言
        # ======================================

        assert detail_response.status_code == 200, (
            f"修改后查询账户详情失败，"
            f"status_code={detail_response.status_code}，"
            f"response={detail_response.text}"
        )

        # ======================================
        # 解析详情接口响应
        # ======================================

        detail_response_data = detail_response.json()

        # ======================================
        # 详情接口业务状态码断言
        # ======================================

        assert detail_response_data.get("code") == 200, (
            f"修改后查询账户详情业务失败：" f"{detail_response_data}"
        )

        # ======================================
        # 获取详情数据
        # ======================================

        detail_data = detail_response_data.get(
            "data",
            {},
        )

        # ======================================
        # 验证数据库中的账户名称
        # ======================================

        assert detail_data.get("name") == payload["name"]

        # ======================================
        # 验证数据库中的账户颜色
        # ======================================

        assert detail_data.get("color") == payload["color"]

        # ======================================
        # 验证数据库中的排序值
        # ======================================

        assert detail_data.get("sort_order") == payload["sort_order"]

    @allure.story("账户详情")
    @allure.title("查询不存在的账户失败")
    def test_account_not_found(
        self,
        account_api,
    ):
        """
        验证查询不存在的账户时接口正确返回失败。

        验证内容：

        1. 使用一个不存在的账户 ID；
        2. 调用账户详情接口；
        3. HTTP 状态码符合后端异常响应规则；
        4. 业务 code 正确；
        5. 返回的错误信息能够明确表示账户不存在。

        该测试不需要创建测试账户，
        因为测试目标本身就是验证不存在的数据。
        """

        # ======================================
        # 构造不存在的账户 ID
        # ======================================
        #
        # 这里使用一个非常大的 ID，
        # 降低数据库中真实存在该账户的可能性。
        #
        # 后续如果框架进一步完善，
        # 可以专门封装一个：
        #
        # generate_not_found_id()
        #
        # 用于生成不存在的数据 ID。
        #
        # ======================================

        account_id = 999999999

        # ======================================
        # 调用账户详情接口
        # ======================================
        #
        # URL 拼接和 GET 请求已经封装在：
        #
        # AccountApi.get_account_detail()
        #
        # 测试用例不再自己编写：
        #
        # /api/v1/accounts/{id}/
        #
        # ======================================

        response = account_api.get_account_detail(account_id)

        # ======================================
        # HTTP 状态码断言
        # ======================================
        #
        # 当前项目统一业务异常通常返回 400。
        #
        # 如果你的后端实际返回 404，
        # 后续根据真实接口规则调整即可。
        #
        # ======================================

        assert response.status_code == 400, (
            f"查询不存在账户时接口响应异常，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 400, (
            f"查询不存在账户时业务状态码异常：" f"{response_data}"
        )

        # ======================================
        # 错误信息断言
        # ======================================
        #
        # 这里只验证核心关键词：
        #
        # "不存在"
        #
        # 而不是把完整错误文案写死。
        #
        # 这样可以避免后端只是调整了一点提示语，
        # 自动化用例就全部失败。
        #
        # 例如以下提示都可以接受：
        #
        # 账户不存在
        # 指定账户不存在
        # 当前账户不存在
        #
        # ======================================

        message = response_data.get(
            "message",
            "",
        )

        assert "不存在" in message, f"接口错误信息不符合预期：" f"{response_data}"

    @allure.story("删除账户")
    @allure.title("删除账户场景验证")
    @pytest.mark.parametrize(
        "initial_balance,expected_status,expected_code,expected_message",
        [
            (
                "0.00",
                200,
                200,
                "",
            ),
            (
                "100.00",
                400,
                400,
                "余额不为0",
            ),
        ],
        ids=[
            "delete_zero_balance_account_success",
            "delete_non_zero_balance_account_failed",
        ],
    )
    def test_delete_account(
        self,
        account_api,
        account_factory,
        initial_balance,
        expected_status,
        expected_code,
        expected_message,
    ):
        """
        验证删除账户的不同业务场景。

        当前通过 pytest 参数化，
        使用同一条测试方法覆盖多个删除场景。

        覆盖场景：

        1. 账户余额为 0：
        - 允许删除；
        - HTTP 状态码为 200；
        - 业务 code 为 200。

        2. 账户余额不为 0：
        - 不允许删除；
        - HTTP 状态码为 400；
        - 业务 code 为 400；
        - 错误信息包含“余额不为0”。

        参数说明：

        initial_balance：
            创建测试账户时的初始余额。

        expected_status：
            预期 HTTP 状态码。

        expected_code：
            预期业务 code。

        expected_message：
            预期错误信息关键词。

            删除成功场景不需要校验错误信息，
            所以传空字符串。
        """

        # ======================================
        # 构造测试账户数据
        # ======================================
        #
        # 不同测试场景只需要修改 initial_balance，
        # 其他测试数据统一由 AccountDataFactory 生成。
        #
        # 这样避免每个删除场景都重复编写 payload。
        #
        # ======================================

        payload = account_factory.build_account(
            initial_balance=initial_balance,
            note="删除账户自动化测试",
        )

        # ======================================
        # 创建测试账户
        # ======================================
        #
        # 删除账户测试必须先准备真实账户数据。
        #
        # 因为这里不同参数场景需要不同初始余额，
        # 所以不直接使用通用 test_account fixture。
        #
        # ======================================

        create_response = account_api.create_account(payload)

        # ======================================
        # 创建账户前置条件断言
        # ======================================

        assert create_response.status_code == 200, (
            f"删除账户测试前置数据创建失败，"
            f"status_code={create_response.status_code}，"
            f"response={create_response.text}"
        )

        create_response_data = create_response.json()

        assert create_response_data.get("code") == 200, (
            f"删除账户测试前置数据业务失败：" f"{create_response_data}"
        )

        # ======================================
        # 获取测试账户 ID
        # ======================================

        account_data = create_response_data.get(
            "data",
            {},
        )

        account_id = account_data.get("id")

        assert account_id, f"创建测试账户后未返回账户 ID：" f"{create_response_data}"

        # ======================================
        # 标记账户是否已经成功删除
        # ======================================
        #
        # 如果删除成功：
        #
        # deleted = True
        #
        # finally 中就不需要再次清理。
        #
        # 如果删除失败：
        #
        # deleted = False
        #
        # finally 中需要手动将余额归零并删除。
        #
        # ======================================

        deleted = False

        try:
            # ==================================
            # 调用删除账户接口
            # ==================================

            response = account_api.delete_account(account_id)

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert response.status_code == expected_status, (
                f"删除账户接口响应不符合预期，"
                f"initial_balance={initial_balance}，"
                f"expected_status={expected_status}，"
                f"actual_status={response.status_code}，"
                f"response={response.text}"
            )

            # ==================================
            # 解析响应 JSON
            # ==================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert response_data.get("code") == expected_code, (
                f"删除账户业务状态码不符合预期，"
                f"initial_balance={initial_balance}，"
                f"response={response_data}"
            )

            # ==================================
            # 删除成功场景
            # ==================================

            if expected_status == 200:
                deleted = True

            # ==================================
            # 删除失败场景
            # ======================================
            #
            # 如果 expected_message 不为空，
            # 说明当前场景需要校验错误信息。
            #
            # ==================================

            if expected_message:
                message = response_data.get(
                    "message",
                    "",
                )

                assert expected_message in message, (
                    f"删除账户错误信息不符合预期，"
                    f"expected_message={expected_message}，"
                    f"actual_message={message}"
                )

        finally:
            # ==================================
            # 清理删除失败场景的数据
            # ======================================
            #
            # 余额不为 0 的账户删除会失败，
            # 所以测试结束后需要：
            #
            # 1. 将余额调整为 0；
            # 2. 再删除测试账户。
            #
            # 如果前面已经删除成功，
            # deleted=True，
            # 这里不会重复删除。
            #
            # ==================================

            if not deleted:
                account_api.adjust_balance(
                    account_id,
                    {
                        "balance": "0.00",
                        "note": "自动化测试数据清理",
                    },
                )

                account_api.delete_account(account_id)

    @allure.story("余额调整")
    @allure.title("账户余额调整成功")
    def test_adjust_account_balance_success(
        self,
        account_api,
        test_account,
    ):
        """
        验证账户余额调整成功。

        验证内容：

        1. 使用 test_account fixture 自动创建测试账户；
        2. 调用账户余额调整接口；
        3. HTTP 状态码为 200；
        4. 业务 code 为 200；
        5. 返回余额等于目标余额；
        6. 再次查询账户详情；
        7. 验证账户实际余额已经更新；
        8. 查询余额调整记录；
        9. 验证至少存在一条余额调整记录。

        测试结束后，
        test_account fixture 会自动：

        1. 将账户余额调整为 0；
        2. 删除测试账户。

        因此本测试方法无需编写额外清理逻辑。
        """

        # ======================================
        # 获取测试账户 ID
        # ======================================
        #
        # test_account fixture 会在测试开始前
        # 自动创建一个真实测试账户。
        #
        # 当前 fixture 创建的账户默认余额为：
        #
        # 1000.00
        #
        # ======================================

        account_id = test_account.get("id")

        # ======================================
        # 构造余额调整参数
        # ======================================
        #
        # 当前测试将账户余额从：
        #
        # 1000.00
        #
        # 调整为：
        #
        # 1500.00
        #
        # ======================================

        payload = {
            "balance": "1500.00",
            "note": "自动化测试余额调整",
        }

        # ======================================
        # 调用余额调整接口
        # ======================================
        #
        # URL 和 POST 请求已经封装在：
        #
        # AccountApi.adjust_balance()
        #
        # 测试用例只需要传入：
        #
        # 1. account_id
        # 2. payload
        #
        # ======================================

        response = account_api.adjust_balance(
            account_id,
            payload,
        )

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"账户余额调整接口请求失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"账户余额调整业务执行失败：" f"{response_data}"
        )

        # ======================================
        # 获取响应 data
        # ======================================

        data = response_data.get(
            "data",
            {},
        )

        # ======================================
        # 返回余额断言
        # ======================================
        #
        # 调整成功后，
        # 接口返回余额应该与目标余额一致。
        #
        # ======================================

        assert data.get("balance") == payload["balance"], (
            f"余额调整结果不正确，"
            f"expected={payload['balance']}，"
            f"actual={data.get('balance')}"
        )

        # ======================================
        # 再次查询账户详情
        # ======================================
        #
        # 为什么还要再查询一次？
        #
        # 因为只验证调整接口返回值，
        # 不能完全证明数据库里的余额真的修改成功。
        #
        # 所以需要再次查询账户详情，
        # 验证实际账户余额。
        #
        # ======================================

        detail_response = account_api.get_account_detail(account_id)

        # ======================================
        # 详情接口状态码断言
        # ======================================

        assert detail_response.status_code == 200, (
            f"余额调整后查询账户详情失败，"
            f"status_code="
            f"{detail_response.status_code}，"
            f"response={detail_response.text}"
        )

        # ======================================
        # 获取详情接口数据
        # ======================================

        detail_response_data = detail_response.json()

        assert detail_response_data.get("code") == 200, (
            f"余额调整后查询账户详情业务失败：" f"{detail_response_data}"
        )

        detail_data = detail_response_data.get(
            "data",
            {},
        )

        # ======================================
        # 实际账户余额断言
        # ======================================

        assert detail_data.get("balance") == payload["balance"], (
            f"数据库中的账户余额未正确更新，"
            f"expected={payload['balance']}，"
            f"actual={detail_data.get('balance')}"
        )

        # ======================================
        # 查询余额调整记录
        # ======================================
        #
        # GET
        #
        # /api/v1/accounts/{account_id}/
        # balance-adjustments/
        #
        # 已封装在：
        #
        # AccountApi.get_balance_adjustments()
        #
        # ======================================

        history_response = account_api.get_balance_adjustments(account_id)

        # ======================================
        # 调整记录接口状态码断言
        # ======================================

        assert history_response.status_code == 200, (
            f"查询余额调整记录失败，"
            f"status_code="
            f"{history_response.status_code}，"
            f"response={history_response.text}"
        )

        # ======================================
        # 解析调整记录响应
        # ======================================

        history_response_data = history_response.json()

        # ======================================
        # 调整记录业务状态码断言
        # ======================================

        assert history_response_data.get("code") == 200, (
            f"查询余额调整记录业务失败：" f"{history_response_data}"
        )

        # ======================================
        # 获取调整记录
        # ======================================

        records = history_response_data.get(
            "data",
            [],
        )

        # ======================================
        # 调整记录存在性断言
        # ======================================
        #
        # 当前测试执行过一次余额调整，
        # 所以至少应该存在一条调整记录。
        #
        # ======================================

        assert records, f"余额调整成功后未生成调整记录：" f"{history_response_data}"

    @allure.story("账户列表")
    @allure.title("查询账户列表成功")
    def test_account_list_success(
        self,
        account_api,
        test_account,
    ):
        """
        验证查询账户列表成功。

        测试前置：

        1. 使用 test_account fixture 自动创建一个真实测试账户；
        2. 获取当前测试账户 ID 和账户名称。

        测试步骤：

        1. 调用账户列表接口；
        2. 获取账户列表数据；
        3. 在列表中查找当前 fixture 创建的账户。

        验证内容：

        1. HTTP 状态码为 200；
        2. 业务 code 为 200；
        3. 返回结果中包含账户列表；
        4. 当前测试账户存在于账户列表中；
        5. 账户 ID 正确；
        6. 账户名称正确；
        7. 账户类型正确。

        测试结束后，
        test_account fixture 会自动：

        1. 将账户余额调整为 0；
        2. 删除测试账户。
        """

        # ======================================
        # 获取测试账户信息
        # ======================================
        #
        # test_account fixture 会在测试开始前
        # 自动创建一个真实账户。
        #
        # 这里保存账户 ID，
        # 后面用于在账户列表中查找。
        #
        # ======================================

        account_id = test_account.get("id")

        account_name = test_account.get("name")

        # ======================================
        # 调用账户列表接口
        # ======================================
        #
        # GET
        #
        # /api/v1/accounts/
        #
        # URL 和 GET 请求已经封装在：
        #
        # AccountApi.get_account_list()
        #
        # ======================================

        response = account_api.get_account_list()

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"查询账户列表失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"查询账户列表业务失败：" f"{response_data}"
        )

        # ======================================
        # 获取响应 data
        # ======================================

        data = response_data.get(
            "data",
            [],
        )

        # ======================================
        # 兼容分页和非分页结构
        # ======================================
        #
        # 部分列表接口可能直接返回：
        #
        # {
        #     "data": [...]
        # }
        #
        # 也可能使用分页结构：
        #
        # {
        #     "data": {
        #         "results": [...]
        #     }
        # }
        #
        # 所以这里做兼容处理。
        #
        # ======================================

        if isinstance(data, dict):
            account_list = data.get(
                "results",
                [],
            )

        elif isinstance(data, list):
            account_list = data

        else:
            account_list = []

        # ======================================
        # 列表类型断言
        # ======================================

        assert isinstance(
            account_list,
            list,
        ), (
            f"账户列表数据类型错误：" f"{response_data}"
        )

        # ======================================
        # 查找当前测试账户
        # ======================================
        #
        # 不直接使用 account_list[0]，
        #
        # 因为账户列表的排序规则
        # 可能受到：
        #
        # 1. sort_order；
        # 2. 创建时间；
        # 3. 默认账户；
        # 4. 后端排序规则；
        #
        # 等因素影响。
        #
        # 所以这里按照账户 ID
        # 查找当前 fixture 创建的账户。
        #
        # ======================================

        current_account = next(
            (account for account in account_list if account.get("id") == account_id),
            None,
        )

        # ======================================
        # 测试账户存在性断言
        # ======================================

        assert current_account is not None, (
            f"账户列表中未找到测试账户，"
            f"account_id={account_id}，"
            f"account_name={account_name}，"
            f"response={response_data}"
        )

        # ======================================
        # 账户 ID 断言
        # ======================================

        assert current_account.get("id") == account_id

        # ======================================
        # 账户名称断言
        # ======================================

        assert current_account.get("name") == test_account.get("name"), (
            f"账户名称不正确，"
            f"expected={test_account.get('name')}，"
            f"actual={current_account.get('name')}"
        )

        # ======================================
        # 账户类型断言
        # ======================================

        assert current_account.get("account_type") == test_account.get(
            "account_type"
        ), (
            f"账户类型不正确，"
            f"expected="
            f"{test_account.get('account_type')}，"
            f"actual="
            f"{current_account.get('account_type')}"
        )

    @allure.story("新增账户")
    @allure.title("创建重复账户名称失败")
    def test_create_duplicate_account_name_failed(
        self,
        account_api,
        account_factory,
    ):
        """
        验证创建重复账户名称时接口正确返回失败。

        测试步骤：

        1. 使用 account_factory 构造第一份账户数据；
        2. 创建第一个账户；
        3. 使用相同账户名称构造第二份账户数据；
        4. 再次调用创建账户接口；
        5. 验证接口正确拒绝重复账户名称。

        验证内容：

        1. 第一个账户创建成功；
        2. 第二次创建返回失败；
        3. HTTP 状态码为 400；
        4. 业务 code 为 400；
        5. 错误信息能够明确表示账户名称重复；
        6. 测试结束后自动清理第一个测试账户。

        注意：

        第二个账户创建失败，
        因此不会产生需要清理的账户数据。
        """

        # ======================================
        # 构造第一个账户测试数据
        # ======================================
        #
        # account_factory 会自动生成
        # 一个唯一账户名称。
        #
        # 后面第二次创建时，
        # 故意复用这个名称，
        # 从而触发重复名称校验。
        #
        # ======================================

        first_payload = account_factory.build_account(
            initial_balance="1000.00",
            note="重复账户名称测试-第一个账户",
        )

        # ======================================
        # 初始化第一个账户 ID
        # ======================================
        #
        # 用于 finally 中清理测试数据。
        #
        # ======================================

        first_account_id = None

        try:
            # ==================================
            # 创建第一个账户
            # ==================================

            first_response = account_api.create_account(first_payload)

            # ==================================
            # 第一个账户 HTTP 状态码断言
            # ==================================

            assert first_response.status_code == 200, (
                f"创建第一个测试账户失败，"
                f"status_code="
                f"{first_response.status_code}，"
                f"response={first_response.text}"
            )

            # ==================================
            # 解析第一个账户响应
            # ==================================

            first_response_data = first_response.json()

            # ==================================
            # 第一个账户业务状态码断言
            # ==================================

            assert first_response_data.get("code") == 200, (
                f"创建第一个测试账户业务失败：" f"{first_response_data}"
            )

            # ==================================
            # 获取第一个账户数据
            # ==================================

            first_account_data = first_response_data.get(
                "data",
                {},
            )

            # ==================================
            # 获取第一个账户 ID
            # ==================================

            first_account_id = first_account_data.get("id")

            assert first_account_id, (
                f"创建第一个账户后未返回账户 ID：" f"{first_response_data}"
            )

            # ==================================
            # 构造重复名称账户数据
            # ======================================
            #
            # 这里最关键的是：
            #
            # name 必须和第一个账户完全相同。
            #
            # 其他字段可以不同，
            # 这样可以明确验证：
            #
            # 导致失败的原因是账户名称重复，
            # 而不是其他字段。
            #
            # ==================================

            duplicate_payload = account_factory.build_account(
                name=first_payload["name"],
                initial_balance="500.00",
                note="重复账户名称测试-第二个账户",
            )

            # ==================================
            # 再次创建相同名称账户
            # ==================================

            duplicate_response = account_api.create_account(duplicate_payload)

            # ==================================
            # HTTP 状态码断言
            # ======================================
            #
            # 当前后端业务异常规则：
            #
            # 重复账户名称返回 400。
            #
            # ==================================

            assert duplicate_response.status_code == 400, (
                f"重复账户名称未被正确拦截，"
                f"status_code="
                f"{duplicate_response.status_code}，"
                f"response={duplicate_response.text}"
            )

            # ==================================
            # 解析重复创建响应
            # ==================================

            duplicate_response_data = duplicate_response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert duplicate_response_data.get("code") == 400, (
                f"重复账户名称业务状态码异常：" f"{duplicate_response_data}"
            )

            # ==================================
            # 获取错误信息
            # ==================================

            message = duplicate_response_data.get(
                "message",
                "",
            )

            # ==================================
            # 错误信息断言
            # ======================================
            #
            # 不建议把整句错误文案完全写死。
            #
            # 后端可能返回：
            #
            # 账户名称已存在
            # 已存在同名账户
            # 该账户名称已经存在
            #
            # 所以这里先校验核心关键词。
            #
            # ==================================

            assert "存在" in message or "重复" in message, (
                f"重复账户名称错误信息不符合预期，"
                f"actual_message={message}，"
                f"response={duplicate_response_data}"
            )

        finally:
            # ==================================
            # 清理第一个测试账户
            # ======================================
            #
            # 第二个账户创建失败，
            # 所以只需要清理第一个账户。
            #
            # 当前系统规则：
            #
            # 非零余额账户不能直接删除。
            #
            # 因此需要：
            #
            # 1. 将余额调整为 0；
            # 2. 删除账户。
            #
            # ==================================

            if first_account_id:
                # ==================================
                # 将账户余额归零
                # ==================================

                account_api.adjust_balance(
                    first_account_id,
                    {
                        "balance": "0.00",
                        "note": "重复账户名称测试数据清理",
                    },
                )

                # ==================================
                # 删除测试账户
                # ==================================

                account_api.delete_account(first_account_id)

    @allure.story("余额调整")
    @allure.title("余额调整记录内容正确")
    def test_balance_adjustment_record_success(
        self,
        account_api,
        test_account,
    ):
        """
        验证余额调整记录内容正确。

        测试步骤：

        1. 使用 test_account fixture 自动创建测试账户；
        2. 将账户余额调整为 1500.00；
        3. 查询账户余额调整记录；
        4. 找到本次调整对应的记录。

        验证内容：

        1. 余额调整接口调用成功；
        2. 查询余额调整记录接口成功；
        3. 业务 code 为 200；
        4. 至少存在一条调整记录；
        5. 本次调整后的余额为 1500.00；
        6. 本次调整备注为“余额记录校验”。

        测试结束后，
        test_account fixture 会自动：

        1. 将账户余额调整为 0；
        2. 删除测试账户。
        """

        # ======================================
        # 获取测试账户 ID
        # ======================================
        #
        # test_account fixture 会提前创建
        # 一个真实测试账户。
        #
        # 当前默认初始余额：
        #
        # 1000.00
        #
        # ======================================

        account_id = test_account.get("id")

        # ======================================
        # 构造余额调整参数
        # ======================================

        payload = {
            "balance": "1500.00",
            "note": "余额记录校验",
        }

        # ======================================
        # 调用余额调整接口
        # ======================================
        #
        # URL 和 POST 请求已经封装在：
        #
        # AccountApi.adjust_balance()
        #
        # ======================================

        response = account_api.adjust_balance(
            account_id,
            payload,
        )

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"账户余额调整失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析余额调整响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"账户余额调整业务失败：" f"{response_data}"
        )

        # ======================================
        # 查询余额调整记录
        # ======================================
        #
        # URL 和 GET 请求已经封装在：
        #
        # AccountApi.get_balance_adjustments()
        #
        # ======================================

        history_response = account_api.get_balance_adjustments(account_id)

        # ======================================
        # 查询记录 HTTP 状态码断言
        # ======================================

        assert history_response.status_code == 200, (
            f"查询余额调整记录失败，"
            f"status_code="
            f"{history_response.status_code}，"
            f"response={history_response.text}"
        )

        # ======================================
        # 解析调整记录响应
        # ======================================

        history_response_data = history_response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert history_response_data.get("code") == 200, (
            f"查询余额调整记录业务失败：" f"{history_response_data}"
        )

        # ======================================
        # 获取调整记录列表
        # ======================================

        records = history_response_data.get(
            "data",
            [],
        )

        # ======================================
        # 调整记录存在性断言
        # ======================================

        assert records, (
            f"账户余额已经调整，" f"但未查询到余额调整记录：" f"{history_response_data}"
        )

        # ======================================
        # 查找本次余额调整对应的记录
        # ======================================
        #
        # 不建议直接使用：
        #
        # records[0]
        #
        # 因为接口的排序规则以后可能变化。
        #
        # 所以这里根据：
        #
        # 1. 调整后的余额；
        # 2. 调整备注；
        #
        # 查找当前测试生成的记录。
        #
        # ======================================

        current_record = next(
            (
                record
                for record in records
                if (
                    record.get("new_balance") == payload["balance"]
                    and record.get("note") == payload["note"]
                )
            ),
            None,
        )

        # ======================================
        # 本次调整记录存在性断言
        # ======================================

        assert current_record is not None, (
            f"未找到本次余额调整记录，"
            f"expected_balance="
            f"{payload['balance']}，"
            f"expected_note="
            f"{payload['note']}，"
            f"records={records}"
        )

        # ======================================
        # 调整前余额断言
        # ======================================

        assert current_record.get("old_balance") == "1000.00", (
            f"调整前余额不正确，"
            f"expected=1000.00，"
            f"actual={current_record.get('old_balance')}"
        )

        # ======================================
        # 调整后余额断言
        # ======================================

        assert current_record.get("new_balance") == payload["balance"], (
            f"调整后余额不正确，"
            f"expected={payload['balance']}，"
            f"actual={current_record.get('new_balance')}"
        )

        # ======================================
        # 余额变化金额断言
        # ======================================
        #
        # 1000.00 → 1500.00
        #
        # 本次增加：
        #
        # 500.00
        #
        # ======================================

        assert current_record.get("difference") == "500.00", (
            f"余额变化金额不正确，"
            f"expected=500.00，"
            f"actual={current_record.get('difference')}"
        )

        # ======================================
        # 调整备注断言
        # ======================================

        assert current_record.get("note") == payload["note"], (
            f"余额调整备注不正确，"
            f"expected={payload['note']}，"
            f"actual={current_record.get('note')}"
        )

    @allure.story("账户转账")
    @allure.title("账户转账成功")
    def test_transfer_success(
        self,
        account_api,
        transfer_accounts,
    ):
        """
        验证两个账户之间正常转账成功。

        测试前置：

        1. 转出账户余额：
        1000.00

        2. 转入账户余额：
        500.00

        测试操作：

        转出账户向转入账户转账：

        200.00

        预期结果：

        1. 转账接口返回成功；
        2. 返回转账记录 ID；
        3. 转出账户余额变为 800.00；
        4. 转入账户余额变为 700.00；
        5. 转账金额正确；
        6. 转账双方账户 ID 正确。

        测试结束后，
        transfer_accounts fixture
        会自动清理两个测试账户。
        """

        # ======================================
        # 获取转出账户
        # ======================================

        source_account = transfer_accounts.get(
            "source",
            {},
        )

        source_id = source_account.get("id")

        # ======================================
        # 获取转入账户
        # ======================================

        target_account = transfer_accounts.get(
            "target",
            {},
        )

        target_id = target_account.get("id")

        # ======================================
        # 构造转账请求参数
        # ======================================

        payload = {
            "source_account_id": source_id,
            "target_account_id": target_id,
            "amount": "200.00",
            "transfer_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "自动化测试正常转账",
        }

        # ======================================
        # 调用转账接口
        # ======================================

        response = account_api.create_transfer(payload)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"账户转账接口请求失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析转账接口响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"账户转账业务执行失败：" f"{response_data}"
        )

        # ======================================
        # 获取转账记录数据
        # ======================================

        data = response_data.get(
            "data",
            {},
        )

        # ======================================
        # 转账记录 ID 断言
        # ======================================

        transfer_id = data.get("id")

        assert transfer_id, f"转账成功后未返回转账记录 ID：" f"{response_data}"

        # ======================================
        # 转账账户断言
        # ======================================

        assert (
            data.get("source_account") == source_id
            or data.get("source_account_id") == source_id
        )

        assert (
            data.get("target_account") == target_id
            or data.get("target_account_id") == target_id
        )

        # ======================================
        # 转账金额断言
        # ======================================

        assert data.get("amount") == payload["amount"]

        # ======================================
        # 查询转出账户详情
        # ======================================

        source_response = account_api.get_account_detail(source_id)

        assert source_response.status_code == 200

        source_data = source_response.json().get(
            "data",
            {},
        )

        # ======================================
        # 验证转出账户余额
        # ======================================
        #
        # 1000.00 - 200.00
        #
        # = 800.00
        #
        # ======================================

        assert source_data.get("balance") == "800.00", (
            f"转账后转出账户余额错误：" f"{source_data}"
        )

        # ======================================
        # 查询转入账户详情
        # ======================================

        target_response = account_api.get_account_detail(target_id)

        assert target_response.status_code == 200

        target_data = target_response.json().get(
            "data",
            {},
        )

        # ======================================
        # 验证转入账户余额
        # ======================================
        #
        # 500.00 + 200.00
        #
        # = 700.00
        #
        # ======================================

        assert target_data.get("balance") == "700.00", (
            f"转账后转入账户余额错误：" f"{target_data}"
        )

    @allure.story("账户转账")
    @allure.title("查询转账记录列表成功")
    def test_transfer_list_success(
        self,
        account_api,
        transfer_accounts,
    ):
        """
        验证查询账户转账记录列表成功。

        测试前置：

        1. transfer_accounts fixture 自动创建两个账户；
        2. 转出账户初始余额为 1000.00；
        3. 转入账户初始余额为 500.00。

        测试步骤：

        1. 创建一笔真实转账；
        2. 获取转账记录 ID；
        3. 调用转账记录列表接口；
        4. 在列表中查找刚刚创建的转账记录。

        验证内容：

        1. 创建转账成功；
        2. 查询转账列表成功；
        3. HTTP 状态码为 200；
        4. 业务 code 为 200；
        5. 列表中存在刚刚创建的转账记录；
        6. 转账金额正确；
        7. 转出账户正确；
        8. 转入账户正确。

        测试结束后，
        transfer_accounts fixture
        会自动清理两个测试账户。
        """

        # ======================================
        # 获取转出账户
        # ======================================

        source_account = transfer_accounts.get(
            "source",
            {},
        )

        source_id = source_account.get("id")

        # ======================================
        # 获取转入账户
        # ======================================

        target_account = transfer_accounts.get(
            "target",
            {},
        )

        target_id = target_account.get("id")

        # ======================================
        # 构造转账请求数据
        # ======================================
        #
        # 查询列表之前，
        # 先主动创建一条属于当前测试的转账记录。
        #
        # 这样可以避免依赖数据库中
        # 原本已经存在的历史数据。
        #
        # ======================================

        payload = {
            "source_account_id": source_id,
            "target_account_id": target_id,
            "amount": "100.00",
            "transfer_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "自动化测试-转账列表查询",
        }

        # ======================================
        # 创建测试转账记录
        # ======================================

        transfer_response = account_api.create_transfer(payload)

        # ======================================
        # 创建转账 HTTP 状态码断言
        # ======================================

        assert transfer_response.status_code == 200, (
            f"创建转账测试数据失败，"
            f"status_code="
            f"{transfer_response.status_code}，"
            f"response={transfer_response.text}"
        )

        # ======================================
        # 解析创建转账响应
        # ======================================

        transfer_response_data = transfer_response.json()

        # ======================================
        # 创建转账业务状态码断言
        # ======================================

        assert transfer_response_data.get("code") == 200, (
            f"创建转账测试数据业务失败：" f"{transfer_response_data}"
        )

        # ======================================
        # 获取创建后的转账数据
        # ======================================

        transfer_data = transfer_response_data.get(
            "data",
            {},
        )

        # ======================================
        # 获取转账记录 ID
        # ======================================

        transfer_id = transfer_data.get("id")

        assert transfer_id, f"创建转账成功后未返回转账 ID：" f"{transfer_response_data}"

        # ======================================
        # 查询转账记录列表
        # ======================================

        response = account_api.get_transfer_list()

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"查询转账记录列表失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"查询转账记录列表业务失败：" f"{response_data}"
        )

        # ======================================
        # 获取响应 data
        # ======================================

        data = response_data.get(
            "data",
            {},
        )

        # ======================================
        # 兼容分页和非分页列表结构
        # ======================================
        #
        # 当前项目部分列表接口
        # 可能返回：
        #
        # {
        #     "data": {
        #         "results": [...]
        #     }
        # }
        #
        # 也可能直接返回：
        #
        # {
        #     "data": [...]
        # }
        #
        # 所以这里做一层兼容处理。
        #
        # ======================================

        if isinstance(data, dict):
            transfer_list = data.get(
                "results",
                [],
            )

        elif isinstance(data, list):
            transfer_list = data

        else:
            transfer_list = []

        # ======================================
        # 列表类型断言
        # ======================================

        assert isinstance(
            transfer_list,
            list,
        )

        # ======================================
        # 查找刚刚创建的转账记录
        # ======================================
        #
        # 不直接写：
        #
        # transfer_list[0]
        #
        # 因为列表可能按照时间倒序、
        # ID 倒序或者其他规则排序。
        #
        # 最可靠的方法是按照 transfer_id 查找。
        #
        # ======================================

        current_transfer = next(
            (item for item in transfer_list if item.get("id") == transfer_id),
            None,
        )

        # ======================================
        # 转账记录存在性断言
        # ======================================

        assert current_transfer is not None, (
            f"转账列表中未找到刚刚创建的记录，"
            f"transfer_id={transfer_id}，"
            f"response={response_data}"
        )

        # ======================================
        # 转账金额断言
        # ======================================

        assert current_transfer.get("amount") == payload["amount"]

        # ======================================
        # 转出账户断言
        # ======================================
        #
        # 兼容当前接口可能使用：
        #
        # source_account
        #
        # 或：
        #
        # source_account_id
        #
        # ======================================

        assert (
            current_transfer.get("source_account") == source_id
            or current_transfer.get("source_account_id") == source_id
        )

        # ======================================
        # 转入账户断言
        # ======================================

        assert (
            current_transfer.get("target_account") == target_id
            or current_transfer.get("target_account_id") == target_id
        )

    @allure.story("账户转账")
    @allure.title("查询转账详情成功")
    def test_transfer_detail_success(
        self,
        account_api,
        transfer_accounts,
    ):
        """
        验证查询转账详情成功。

        测试前置：

        1. transfer_accounts fixture 自动创建两个账户；
        2. 转出账户初始余额为 1000.00；
        3. 转入账户初始余额为 500.00。

        测试步骤：

        1. 创建一笔真实转账；
        2. 获取创建成功后的 transfer_id；
        3. 根据 transfer_id 查询转账详情。

        验证内容：

        1. 创建转账成功；
        2. 查询转账详情成功；
        3. HTTP 状态码为 200；
        4. 业务 code 为 200；
        5. 返回 transfer_id 正确；
        6. 转账金额正确；
        7. 转出账户正确；
        8. 转入账户正确；
        9. 备注信息正确。

        测试结束后，
        transfer_accounts fixture
        会自动清理两个测试账户。
        """

        # ======================================
        # 获取转出账户
        # ======================================

        source_account = transfer_accounts.get(
            "source",
            {},
        )

        source_id = source_account.get("id")

        # ======================================
        # 获取转入账户
        # ======================================

        target_account = transfer_accounts.get(
            "target",
            {},
        )

        target_id = target_account.get("id")

        # ======================================
        # 构造转账请求数据
        # ======================================
        #
        # 为了保证测试独立性，
        # 这里不依赖数据库中已有转账记录，
        # 而是当前测试自己创建一笔真实转账。
        #
        # ======================================

        payload = {
            "source_account_id": source_id,
            "target_account_id": target_id,
            "amount": "100.00",
            "transfer_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "自动化测试-转账详情查询",
        }

        # ======================================
        # 创建转账记录
        # ======================================

        create_response = account_api.create_transfer(payload)

        # ======================================
        # 创建转账 HTTP 状态码断言
        # ======================================

        assert create_response.status_code == 200, (
            f"创建转账测试数据失败，"
            f"status_code="
            f"{create_response.status_code}，"
            f"response={create_response.text}"
        )

        # ======================================
        # 解析创建转账响应
        # ======================================

        create_response_data = create_response.json()

        # ======================================
        # 创建转账业务状态码断言
        # ======================================

        assert create_response_data.get("code") == 200, (
            f"创建转账测试数据业务失败：" f"{create_response_data}"
        )

        # ======================================
        # 获取创建后的转账数据
        # ======================================

        create_data = create_response_data.get(
            "data",
            {},
        )

        # ======================================
        # 获取 transfer_id
        # ======================================

        transfer_id = create_data.get("id")

        assert transfer_id, (
            f"创建转账成功后未返回 transfer_id：" f"{create_response_data}"
        )

        # ======================================
        # 查询转账详情
        # ======================================
        #
        # GET
        #
        # /api/v1/accounts/transfers/{transfer_id}/
        #
        # URL 和 GET 请求已经封装在：
        #
        # AccountApi.get_transfer_detail()
        #
        # ======================================

        response = account_api.get_transfer_detail(transfer_id)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"查询转账详情失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析详情接口响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"查询转账详情业务失败：" f"{response_data}"
        )

        # ======================================
        # 获取详情数据
        # ======================================

        data = response_data.get(
            "data",
            {},
        )

        # ======================================
        # transfer_id 断言
        # ======================================

        assert data.get("id") == transfer_id, (
            f"转账详情 ID 不正确，"
            f"expected={transfer_id}，"
            f"actual={data.get('id')}"
        )

        # ======================================
        # 转账金额断言
        # ======================================

        assert data.get("amount") == payload["amount"], (
            f"转账金额不正确，"
            f"expected={payload['amount']}，"
            f"actual={data.get('amount')}"
        )

        # ======================================
        # 转出账户断言
        # ======================================
        #
        # 兼容接口可能返回：
        #
        # source_account
        #
        # 或：
        #
        # source_account_id
        #
        # ======================================

        assert (
            data.get("source_account") == source_id
            or data.get("source_account_id") == source_id
        ), (f"转出账户不正确，" f"expected={source_id}，" f"data={data}")

        # ======================================
        # 转入账户断言
        # ======================================

        assert (
            data.get("target_account") == target_id
            or data.get("target_account_id") == target_id
        ), (f"转入账户不正确，" f"expected={target_id}，" f"data={data}")

        # ======================================
        # 备注信息断言
        # ======================================
        #
        # 如果当前接口返回 note 字段，
        # 则验证其与创建转账时传入的数据一致。
        #
        # ======================================

        if "note" in data:
            assert data.get("note") == payload["note"], (
                f"转账备注不正确，"
                f"expected={payload['note']}，"
                f"actual={data.get('note')}"
            )

    @allure.story("账户转账")
    @allure.title("转账失败场景验证")
    @pytest.mark.parametrize(
        (
            "case_name,"
            "amount,"
            "target_type,"
            "expected_status,"
            "expected_code,"
            "expected_message"
        ),
        [
            (
                "余额不足",
                "2000.00",
                "normal",
                400,
                400,
                "余额不足",
            ),
            (
                "转给自己",
                "100.00",
                "self",
                400,
                400,
                "不能",
            ),
            (
                "目标账户不存在",
                "100.00",
                "not_found",
                400,
                400,
                "不存在",
            ),
        ],
        ids=[
            "insufficient_balance",
            "transfer_to_self",
            "target_account_not_found",
        ],
    )
    def test_transfer_failed(
        self,
        account_api,
        transfer_accounts,
        case_name,
        amount,
        target_type,
        expected_status,
        expected_code,
        expected_message,
    ):
        """
        验证账户转账失败场景。

        当前使用 pytest 参数化，
        一条测试方法覆盖多个异常场景。

        覆盖场景：

        1. 余额不足；
        2. 转给自己；
        3. 目标账户不存在。

        验证内容：

        1. 接口 HTTP 状态码正确；
        2. 业务 code 正确；
        3. 错误信息符合预期；
        4. 转账失败后，
        转出账户余额不发生变化；
        5. 正常目标账户余额不发生变化。

        参数说明：

        case_name：
            当前测试场景名称。

        amount：
            当前测试使用的转账金额。

        target_type：
            目标账户类型。

            normal：
                使用正常目标账户。

            self：
                目标账户使用转出账户自身。

            not_found：
                使用一个不存在的账户 ID。

        expected_status：
            预期 HTTP 状态码。

        expected_code：
            预期业务 code。

        expected_message：
            预期错误信息关键词。
        """

        # ======================================
        # 获取转出账户
        # ======================================

        source_account = transfer_accounts.get(
            "source",
            {},
        )

        source_id = source_account.get("id")

        # ======================================
        # 获取正常目标账户
        # ======================================

        target_account = transfer_accounts.get(
            "target",
            {},
        )

        normal_target_id = target_account.get("id")

        # ======================================
        # 保存转账前余额
        # ======================================
        #
        # transfer_accounts fixture 当前约定：
        #
        # 转出账户余额：
        # 1000.00
        #
        # 目标账户余额：
        # 500.00
        #
        # 转账失败后，
        # 这两个余额都不应该发生变化。
        #
        # ======================================

        source_balance_before = "1000.00"

        target_balance_before = "500.00"

        # ======================================
        # 根据测试场景确定目标账户 ID
        # ======================================

        if target_type == "normal":
            # ==================================
            # 正常目标账户
            # ==================================

            target_id = normal_target_id

        elif target_type == "self":
            # ==================================
            # 转给自己
            # ==================================
            #
            # source_account_id
            # 和 target_account_id
            # 使用同一个账户 ID。
            #
            # ==================================

            target_id = source_id

        elif target_type == "not_found":
            # ==================================
            # 不存在的目标账户
            # ==================================

            target_id = 999999999

        else:
            # ==================================
            # 防止测试数据配置错误
            # ==================================

            pytest.fail(f"未知 target_type：" f"{target_type}")

        # ======================================
        # 构造转账请求数据
        # ======================================

        payload = {
            "source_account_id": source_id,
            "target_account_id": target_id,
            "amount": amount,
            "transfer_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": (f"自动化测试-" f"{case_name}"),
        }

        # ======================================
        # 调用转账接口
        # ======================================

        response = account_api.create_transfer(payload)

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == expected_status, (
            f"转账失败场景 HTTP 状态码异常，"
            f"case_name={case_name}，"
            f"expected_status={expected_status}，"
            f"actual_status={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == expected_code, (
            f"转账失败场景业务状态码异常，"
            f"case_name={case_name}，"
            f"response={response_data}"
        )

        # ======================================
        # 错误信息断言
        # ======================================

        message = response_data.get(
            "message",
            "",
        )

        assert expected_message in message, (
            f"转账失败场景错误信息异常，"
            f"case_name={case_name}，"
            f"expected_message={expected_message}，"
            f"actual_message={message}"
        )

        # ======================================
        # 查询转出账户详情
        # ======================================

        source_response = account_api.get_account_detail(source_id)

        assert source_response.status_code == 200

        source_response_data = source_response.json()

        source_data = source_response_data.get(
            "data",
            {},
        )

        # ======================================
        # 转出账户余额断言
        # ======================================
        #
        # 转账失败后，
        # 转出账户不能被扣款。
        #
        # ======================================

        assert source_data.get("balance") == source_balance_before, (
            f"转账失败后转出账户余额发生变化，"
            f"case_name={case_name}，"
            f"actual_balance="
            f"{source_data.get('balance')}"
        )

        # ======================================
        # 查询正常目标账户详情
        # ======================================
        #
        # 即使当前场景是：
        #
        # 1. 转给自己；
        # 2. 目标账户不存在；
        #
        # fixture 中的正常目标账户
        # 也不应该被修改。
        #
        # ======================================

        target_response = account_api.get_account_detail(normal_target_id)

        assert target_response.status_code == 200

        target_response_data = target_response.json()

        target_data = target_response_data.get(
            "data",
            {},
        )

        # ======================================
        # 正常目标账户余额断言
        # ======================================

        assert target_data.get("balance") == target_balance_before, (
            f"转账失败后目标账户余额发生变化，"
            f"case_name={case_name}，"
            f"actual_balance="
            f"{target_data.get('balance')}"
        )

    @allure.story("账户统计")
    @allure.title("查询账户统计成功")
    def test_account_statistics_success(
        self,
        account_api,
        test_account,
    ):
        """
        验证账户统计接口查询成功。

        测试前置：

        1. 使用 test_account fixture 自动创建一个真实测试账户；
        2. 当前测试账户初始余额为 1000.00。

        测试步骤：

        1. 调用账户统计接口；
        2. 获取统计结果；
        3. 验证接口返回结构正确。

        验证内容：

        1. HTTP 状态码为 200；
        2. 业务 code 为 200；
        3. data 不为空；
        4. 返回数据类型正确；
        5. 统计接口能够正常返回账户相关统计数据。

        注意：

        由于当前统计接口具体字段
        需要以实际后端返回结构为准，

        所以这一版先验证：

        1. 接口可用；
        2. 数据结构正常；
        3. data 有实际内容。

        等获取真实响应字段后，
        再进一步增加金额、数量等精确断言。
        """

        # ======================================
        # 确认测试账户已经创建
        # ======================================
        #
        # 这里虽然不直接使用 account_id，
        # 但引入 test_account fixture
        # 可以确保当前用户至少存在一个账户，
        # 从而让统计接口有真实测试数据。
        #
        # ======================================

        account_id = test_account.get("id")

        assert account_id, f"测试账户创建失败：" f"{test_account}"

        # ======================================
        # 调用账户统计接口
        # ======================================
        #
        # GET
        #
        # /api/v1/accounts/statistics/
        #
        # 已封装在：
        #
        # AccountApi.get_statistics()
        #
        # ======================================

        response = account_api.get_statistics()

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"查询账户统计失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"查询账户统计业务失败：" f"{response_data}"
        )

        # ======================================
        # 获取统计数据
        # ======================================

        data = response_data.get("data")

        # ======================================
        # data 非空断言
        # ======================================
        #
        # 当前已经存在测试账户，
        # 统计接口应该能够返回统计数据。
        #
        # ======================================

        assert data is not None, f"账户统计接口 data 为空：" f"{response_data}"

        # ======================================
        # 数据类型断言
        # ======================================
        #
        # 统计接口一般会返回 dict。
        #
        # 如果你的实际接口返回 list，
        # 后面根据真实响应调整。
        #
        # ======================================

        assert isinstance(
            data,
            dict,
        ), (
            f"账户统计 data 类型错误，"
            f"expected=dict，"
            f"actual={type(data).__name__}，"
            f"data={data}"
        )

        # ======================================
        # 统计数据非空断言
        # ======================================

        assert data, f"账户统计接口未返回任何统计内容：" f"{response_data}"

    @allure.story("资产汇总")
    @allure.title("查询资产汇总成功")
    def test_asset_summary_success(
        self,
        account_api,
        test_account,
    ):
        """
        验证资产汇总接口查询成功。

        测试前置：

        1. 使用 test_account fixture 自动创建一个真实测试账户；
        2. 当前测试账户初始余额为 1000.00。

        测试步骤：

        1. 调用资产汇总接口；
        2. 获取资产汇总结果；
        3. 验证接口返回结构正确。

        验证内容：

        1. HTTP 状态码为 200；
        2. 业务 code 为 200；
        3. data 不为空；
        4. data 类型为 dict；
        5. 资产汇总接口能够返回实际统计数据。

        注意：

        当前先验证接口结构和可用性。

        等拿到接口真实字段后，
        再进一步补充：

        1. 总资产；
        2. 总负债；
        3. 净资产；
        4. 各账户类型资产；
        5. 账户数量；

        等精确断言。
        """

        # ======================================
        # 确认测试账户已经创建
        # ======================================
        #
        # test_account fixture 会在测试开始前
        # 自动创建一个真实账户。
        #
        # 当前默认初始余额：
        #
        # 1000.00
        #
        # 这样可以确保资产汇总接口
        # 至少存在一笔真实账户数据。
        #
        # ======================================

        account_id = test_account.get("id")

        assert account_id, f"测试账户创建失败：" f"{test_account}"

        # ======================================
        # 调用资产汇总接口
        # ======================================
        #
        # GET
        #
        # /api/v1/accounts/asset-summary/
        #
        # URL 和 GET 请求已经封装在：
        #
        # AccountApi.get_asset_summary()
        #
        # ======================================

        response = account_api.get_asset_summary()

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"查询资产汇总失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"查询资产汇总业务失败：" f"{response_data}"
        )

        # ======================================
        # 获取资产汇总数据
        # ======================================

        data = response_data.get("data")

        # ======================================
        # data 非空断言
        # ======================================

        assert data is not None, f"资产汇总接口 data 为空：" f"{response_data}"

        # ======================================
        # data 类型断言
        # ======================================
        #
        # 资产汇总接口正常情况下
        # 应该返回字典结构。
        #
        # ======================================

        assert isinstance(
            data,
            dict,
        ), (
            f"资产汇总 data 类型错误，"
            f"expected=dict，"
            f"actual={type(data).__name__}，"
            f"data={data}"
        )

        # ======================================
        # 资产汇总内容非空断言
        # ======================================
        #
        # 当前已经存在一个测试账户，
        # 所以正常情况下 data 不应该为空字典。
        #
        # ======================================

        assert data, f"资产汇总接口未返回任何数据：" f"{response_data}"

    @allure.story("默认账户")
    @allure.title("设置默认账户成功")
    def test_set_default_account_success(
        self,
        account_api,
        test_account,
    ):
        """
        验证设置默认账户成功。

        测试前置：

        1. 使用 test_account fixture 自动创建一个真实测试账户；
        2. 获取当前测试账户 ID。

        测试步骤：

        1. 调用账户修改接口；
        2. 将 is_default 设置为 True；
        3. 再次查询账户详情。

        验证内容：

        1. 修改账户接口调用成功；
        2. HTTP 状态码为 200；
        3. 业务 code 为 200；
        4. 修改接口返回 is_default=True；
        5. 再次查询账户详情时，
        is_default 仍然为 True。

        测试结束后，
        test_account fixture 会自动：

        1. 将账户余额调整为 0；
        2. 删除测试账户。
        """

        # ======================================
        # 获取测试账户 ID
        # ======================================
        #
        # test_account fixture 会在测试开始前
        # 自动创建一个真实账户。
        #
        # ======================================

        account_id = test_account.get("id")

        # ======================================
        # 构造设置默认账户参数
        # ======================================
        #
        # 当前后端已经确认支持：
        #
        # PUT /api/v1/accounts/{id}/
        #
        # 请求：
        #
        # {
        #     "is_default": true
        # }
        #
        # ======================================

        payload = {
            "is_default": True,
        }

        # ======================================
        # 调用账户修改接口
        # ======================================
        #
        # URL 和 PUT 请求已经封装在：
        #
        # AccountApi.update_account()
        #
        # ======================================

        response = account_api.update_account(
            account_id,
            payload,
        )

        # ======================================
        # HTTP 状态码断言
        # ======================================

        assert response.status_code == 200, (
            f"设置默认账户失败，"
            f"status_code={response.status_code}，"
            f"response={response.text}"
        )

        # ======================================
        # 解析响应 JSON
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务状态码断言
        # ======================================

        assert response_data.get("code") == 200, (
            f"设置默认账户业务失败：" f"{response_data}"
        )

        # ======================================
        # 获取修改后的账户数据
        # ======================================

        data = response_data.get(
            "data",
            {},
        )

        # ======================================
        # 账户 ID 断言
        # ======================================

        assert data.get("id") == account_id, (
            f"设置默认账户后账户 ID 错误，"
            f"expected={account_id}，"
            f"actual={data.get('id')}"
        )

        # ======================================
        # 默认账户状态断言
        # ======================================

        assert data.get("is_default") is True, f"账户未成功设置为默认账户：" f"{data}"

        # ======================================
        # 再次查询账户详情
        # ======================================
        #
        # 仅验证修改接口返回值还不够，
        # 这里再次查询账户详情，
        # 确认数据库中的实际状态已经更新。
        #
        # ======================================

        detail_response = account_api.get_account_detail(account_id)

        # ======================================
        # 查询详情 HTTP 状态码断言
        # ======================================

        assert detail_response.status_code == 200, (
            f"设置默认账户后查询详情失败，"
            f"status_code="
            f"{detail_response.status_code}，"
            f"response={detail_response.text}"
        )

        # ======================================
        # 解析详情接口响应
        # ======================================

        detail_response_data = detail_response.json()

        # ======================================
        # 详情接口业务状态码断言
        # ======================================

        assert detail_response_data.get("code") == 200, (
            f"设置默认账户后查询详情业务失败：" f"{detail_response_data}"
        )

        # ======================================
        # 获取账户详情数据
        # ======================================

        detail_data = detail_response_data.get(
            "data",
            {},
        )

        # ======================================
        # 数据库实际默认状态断言
        # ======================================

        assert detail_data.get("is_default") is True, (
            f"数据库中的默认账户状态未正确更新：" f"{detail_data}"
        )

    @allure.story("默认账户")
    @allure.title("切换默认账户成功")
    def test_switch_default_account_success(
        self,
        account_api,
        account_factory,
    ):
        """
        验证默认账户能够正确切换。

        测试前置：

        1. 创建账户 A；
        2. 创建账户 B。

        测试步骤：

        1. 将账户 A 设置为默认账户；
        2. 查询账户 A，确认 is_default=True；
        3. 将账户 B 设置为默认账户；
        4. 查询账户 A；
        5. 查询账户 B。

        预期结果：

        1. 账户 A 第一次设置默认成功；
        2. 账户 B 设置默认成功；
        3. 当账户 B 成为默认账户后，
        账户 A 自动取消默认状态；
        4. 最终只存在一个默认账户：

        A.is_default == False

        B.is_default == True

        测试结束后：

        1. 将两个测试账户余额归零；
        2. 删除两个测试账户；
        3. 避免测试数据污染数据库。
        """

        # ======================================
        # 构造账户 A 测试数据
        # ======================================

        account_a_payload = account_factory.build_account(
            initial_balance="1000.00",
            note="默认账户切换测试-A",
        )

        # ======================================
        # 构造账户 B 测试数据
        # ======================================

        account_b_payload = account_factory.build_account(
            initial_balance="500.00",
            note="默认账户切换测试-B",
        )

        # ======================================
        # 初始化账户 ID
        # ======================================
        #
        # finally 中根据 ID 清理测试数据。
        #
        # 如果某一个账户创建失败，
        # 对应 ID 会保持 None，
        # 清理阶段不会错误删除。
        #
        # ======================================

        account_a_id = None
        account_b_id = None

        try:
            # ==================================
            # 创建账户 A
            # ==================================

            account_a_response = account_api.create_account(account_a_payload)

            # ==================================
            # 账户 A 创建状态码断言
            # ==================================

            assert account_a_response.status_code == 200, (
                f"创建账户 A 失败，"
                f"status_code="
                f"{account_a_response.status_code}，"
                f"response="
                f"{account_a_response.text}"
            )

            # ==================================
            # 解析账户 A 响应
            # ==================================

            account_a_response_data = account_a_response.json()

            assert account_a_response_data.get("code") == 200, (
                f"创建账户 A 业务失败：" f"{account_a_response_data}"
            )

            # ==================================
            # 获取账户 A ID
            # ==================================

            account_a_data = account_a_response_data.get(
                "data",
                {},
            )

            account_a_id = account_a_data.get("id")

            assert account_a_id, (
                f"创建账户 A 后未返回账户 ID：" f"{account_a_response_data}"
            )

            # ==================================
            # 创建账户 B
            # ==================================

            account_b_response = account_api.create_account(account_b_payload)

            # ==================================
            # 账户 B 创建状态码断言
            # ==================================

            assert account_b_response.status_code == 200, (
                f"创建账户 B 失败，"
                f"status_code="
                f"{account_b_response.status_code}，"
                f"response="
                f"{account_b_response.text}"
            )

            # ==================================
            # 解析账户 B 响应
            # ==================================

            account_b_response_data = account_b_response.json()

            assert account_b_response_data.get("code") == 200, (
                f"创建账户 B 业务失败：" f"{account_b_response_data}"
            )

            # ==================================
            # 获取账户 B ID
            # ==================================

            account_b_data = account_b_response_data.get(
                "data",
                {},
            )

            account_b_id = account_b_data.get("id")

            assert account_b_id, (
                f"创建账户 B 后未返回账户 ID：" f"{account_b_response_data}"
            )

            # ==================================
            # 将账户 A 设置为默认账户
            # ======================================

            set_a_response = account_api.update_account(
                account_a_id,
                {
                    "is_default": True,
                },
            )

            # ==================================
            # 设置账户 A 默认状态断言
            # ==================================

            assert set_a_response.status_code == 200, (
                f"设置账户 A 为默认账户失败，"
                f"status_code="
                f"{set_a_response.status_code}，"
                f"response={set_a_response.text}"
            )

            set_a_response_data = set_a_response.json()

            assert set_a_response_data.get("code") == 200, (
                f"设置账户 A 为默认账户业务失败：" f"{set_a_response_data}"
            )

            set_a_data = set_a_response_data.get(
                "data",
                {},
            )

            assert set_a_data.get("is_default") is True, (
                f"账户 A 未成功设置为默认账户：" f"{set_a_data}"
            )

            # ==================================
            # 查询账户 A
            # ======================================
            #
            # 设置完成后再次查询，
            # 确认数据库中的状态确实为 True。
            #
            # ======================================

            account_a_detail_response = account_api.get_account_detail(account_a_id)

            assert account_a_detail_response.status_code == 200

            account_a_detail_data = account_a_detail_response.json().get(
                "data",
                {},
            )

            assert account_a_detail_data.get("is_default") is True, (
                f"账户 A 默认状态未保存成功：" f"{account_a_detail_data}"
            )

            # ==================================
            # 将账户 B 设置为默认账户
            # ======================================
            #
            # 这里是当前用例真正要验证的核心。
            #
            # 如果系统要求每个用户
            # 只能存在一个默认账户，
            #
            # 那么 B 设置为默认账户以后，
            # A 应该自动变成 False。
            #
            # ======================================

            set_b_response = account_api.update_account(
                account_b_id,
                {
                    "is_default": True,
                },
            )

            # ==================================
            # 设置账户 B 默认状态断言
            # ==================================

            assert set_b_response.status_code == 200, (
                f"设置账户 B 为默认账户失败，"
                f"status_code="
                f"{set_b_response.status_code}，"
                f"response={set_b_response.text}"
            )

            set_b_response_data = set_b_response.json()

            assert set_b_response_data.get("code") == 200, (
                f"设置账户 B 为默认账户业务失败：" f"{set_b_response_data}"
            )

            set_b_data = set_b_response_data.get(
                "data",
                {},
            )

            assert set_b_data.get("is_default") is True, (
                f"账户 B 未成功设置为默认账户：" f"{set_b_data}"
            )

            # ==================================
            # 再次查询账户 A
            # ======================================

            final_a_response = account_api.get_account_detail(account_a_id)

            assert final_a_response.status_code == 200

            final_a_response_data = final_a_response.json()

            assert final_a_response_data.get("code") == 200

            final_a_data = final_a_response_data.get(
                "data",
                {},
            )

            # ==================================
            # 验证账户 A 已取消默认
            # ======================================

            assert final_a_data.get("is_default") is False, (
                f"账户 B 设置为默认后，"
                f"账户 A 未自动取消默认状态："
                f"{final_a_data}"
            )

            # ==================================
            # 再次查询账户 B
            # ======================================

            final_b_response = account_api.get_account_detail(account_b_id)

            assert final_b_response.status_code == 200

            final_b_response_data = final_b_response.json()

            assert final_b_response_data.get("code") == 200

            final_b_data = final_b_response_data.get(
                "data",
                {},
            )

            # ==================================
            # 验证账户 B 保持默认
            # ======================================

            assert final_b_data.get("is_default") is True, (
                f"账户 B 默认状态不正确：" f"{final_b_data}"
            )

        finally:
            # ==================================
            # 清理账户 A
            # ======================================

            if account_a_id:
                try:
                    # 将账户 A 余额归零。
                    account_api.adjust_balance(
                        account_a_id,
                        {
                            "balance": "0.00",
                            "note": "默认账户切换测试清理-A",
                        },
                    )

                    # 删除账户 A。
                    account_api.delete_account(account_a_id)

                except Exception as exc:
                    print(
                        f"账户 A 清理失败，"
                        f"account_id={account_a_id}，"
                        f"error={exc}"
                    )

            # ==================================
            # 清理账户 B
            # ======================================

            if account_b_id:
                try:
                    # 将账户 B 余额归零。
                    account_api.adjust_balance(
                        account_b_id,
                        {
                            "balance": "0.00",
                            "note": "默认账户切换测试清理-B",
                        },
                    )

                    # 删除账户 B。
                    account_api.delete_account(account_b_id)

                except Exception as exc:
                    print(
                        f"账户 B 清理失败，"
                        f"account_id={account_b_id}，"
                        f"error={exc}"
                    )
