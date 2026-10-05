from datetime import datetime
import allure
import uuid


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
        auth_client,
        config,
    ):
        """
        验证正常新增账户。

        验证内容：

        1. HTTP 状态码正确；
        2. 业务 code 为 200；
        3. 返回账户 ID；
        4. 返回账户名称正确；
        5. 测试完成后自动删除测试账户，
        避免污染数据库。
        """

        # ======================================
        # 新增账户接口地址
        # ======================================

        create_url = f"{config.api_prefix}" f"/accounts/"

        # ======================================
        # 测试数据
        # ======================================

        # ======================================
        # 生成唯一账户名称
        # ======================================
        #
        # 使用 UUID 生成随机后缀，
        # 避免重复执行自动化测试时
        # 出现同名账户。
        #
        # ======================================

        account_name = "自动化测试账户_" f"{uuid.uuid4().hex[:8]}"

        payload = {
            "name": account_name,
            "account_type": "cash",
            "initial_balance": "1000.00",
            "note": "pytest自动创建",
        }

        # ======================================
        # 初始化账户 ID
        # ======================================
        #
        # 如果创建失败，
        # account_id 会保持为 None，
        # finally 中就不会执行删除。
        #
        # ======================================

        account_id = None

        try:
            # ==================================
            # 创建账户
            # ==================================

            response = auth_client.post(
                create_url,
                json=payload,
            )

            # ==================================
            # HTTP 状态码断言
            # ==================================

            # assert response.status_code == 200
            assert response.status_code == 200, (
                f"新增账户失败，"
                f"status_code={response.status_code}，"
                f"response={response.text}"
            )

            # ==================================
            # 解析响应
            # ==================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert response_data.get("code") == 200
            assert response_data.get("code") == 200, (
                f"新增账户业务失败：" f"{response_data}"
            )
            data = response_data.get(
                "data",
                {},
            )

            # ==================================
            # 获取账户 ID
            # ==================================

            account_id = data.get("id")

            assert account_id

            # ==================================
            # 账户名称断言
            # ==================================

            assert data.get("name") == payload["name"]

        finally:
            # ==================================
            # 清理测试数据
            # ==================================
            #
            # 无论断言成功还是失败，
            # 只要账户已经创建成功，
            # 都尝试删除测试账户。
            #
            # ==================================

            if account_id:

                delete_url = f"{config.api_prefix}" f"/accounts/{account_id}/"

                auth_client.delete(delete_url)

    @allure.story("账户详情")
    @allure.title("查询账户详情成功")
    def test_account_detail_success(
        self,
        auth_client,
        config,
        test_account,
    ):
        """
        验证查询指定账户详情成功。

        验证：

        1. HTTP 状态码为 200；
        2. 业务 code 为 200；
        3. 返回账户 ID 正确；
        4. 返回账户名称正确。
        """

        # ======================================
        # 获取测试账户信息
        # ======================================

        account_id = test_account["id"]

        account_name = test_account["name"]

        # ======================================
        # 账户详情接口
        # ======================================

        url = f"{config.api_prefix}" f"/accounts/{account_id}/"

        # ======================================
        # 发送请求
        # ======================================

        response = auth_client.get(url)

        assert response.status_code == 200, f"查询账户详情失败：" f"{response.text}"

        response_data = response.json()

        assert response_data.get("code") == 200

        data = response_data.get(
            "data",
            {},
        )

        assert data.get("id") == account_id

        assert data.get("name") == account_name

    @allure.story("修改账户")
    @allure.title("修改账户成功")
    def test_update_account_success(
        self,
        auth_client,
        config,
        test_account,
    ):
        """
        验证修改账户成功。
        """

        # ======================================
        # 获取账户 ID
        # ======================================

        account_id = test_account["id"]

        # ======================================
        # 修改账户接口
        # ======================================

        url = f"{config.api_prefix}" f"/accounts/{account_id}/"

        # ======================================
        # 修改参数
        # ======================================

        payload = {
            "name": ("修改后的自动化账户_" f"{uuid.uuid4().hex[:6]}"),
            "color": "#27BA9B",
            "sort_order": 9,
        }

        # ======================================
        # 发送修改请求
        # ======================================

        response = auth_client.put(
            url,
            json=payload,
        )

        assert response.status_code == 200, f"修改账户失败：" f"{response.text}"

        response_data = response.json()

        assert response_data.get("code") == 200

        data = response_data.get(
            "data",
            {},
        )

        assert data.get("name") == payload["name"]

        assert data.get("color") == payload["color"]

        assert data.get("sort_order") == payload["sort_order"]

    @allure.story("账户详情")
    @allure.title("查询不存在账户")
    def test_account_not_found(
        self,
        auth_client,
        config,
    ):
        """
        验证查询不存在账户时，
        接口能够正确返回错误。
        """

        # ======================================
        # 使用一个不存在的账户 ID
        # ======================================

        account_id = 999999999

        url = f"{config.api_prefix}" f"/accounts/{account_id}/"

        response = auth_client.get(url)

        # ======================================
        # 解析响应
        # ======================================

        response_data = response.json()

        # ======================================
        # 业务失败断言
        # ======================================

        assert response_data.get("code") != 200

    @allure.story("删除账户")
    @allure.title("删除账户成功")
    def test_delete_account_success(
        self,
        auth_client,
        config,
    ):
        """
        验证删除账户成功。

        验证内容：

        1. 先创建一个专用测试账户；
        2. 删除该账户；
        3. 删除接口返回成功；
        4. 再次查询该账户时不能返回成功。
        """

        # ======================================
        # 生成唯一账户名称
        # ======================================

        account_name = "删除测试账户_" f"{uuid.uuid4().hex[:8]}"

        # ======================================
        # 创建账户接口
        # ======================================

        create_url = f"{config.api_prefix}" f"/accounts/"

        payload = {
            "name": account_name,
            "account_type": "cash",
            # 删除账户要求余额必须为 0。
            "initial_balance": "0.00",
        }

        # ======================================
        # 创建账户
        # ======================================

        create_response = auth_client.post(
            create_url,
            json=payload,
        )

        assert create_response.status_code == 200, (
            f"创建删除测试账户失败：" f"{create_response.text}"
        )

        create_data = create_response.json()

        assert create_data.get("code") == 200

        account_id = create_data.get("data", {}).get("id")

        assert account_id

        # ======================================
        # 删除账户
        # ======================================

        delete_url = f"{config.api_prefix}" f"/accounts/{account_id}/"

        delete_response = auth_client.delete(delete_url)

        assert delete_response.status_code == 200, (
            f"删除账户失败：" f"{delete_response.text}"
        )

        delete_data = delete_response.json()

        assert delete_data.get("code") == 200

        # ======================================
        # 删除后再次查询
        # ======================================

        detail_response = auth_client.get(delete_url)

        detail_data = detail_response.json()

        # 删除后不应该还能查询成功。
        assert detail_data.get("code") != 200

    @allure.story("余额调整")
    @allure.title("账户余额调整成功")
    def test_adjust_account_balance_success(
        self,
        auth_client,
        config,
        test_account,
    ):
        """
        验证账户余额调整成功。

        验证内容：

        1. 调整接口调用成功；
        2. 业务 code 为 200；
        3. 返回余额等于调整后的目标余额；
        4. 调整记录可以正常查询。
        """

        # ======================================
        # 获取测试账户 ID
        # ======================================

        account_id = test_account["id"]

        # ======================================
        # 余额调整接口
        # ======================================

        adjust_url = f"{config.api_prefix}" f"/accounts/{account_id}/adjust-balance/"

        # ======================================
        # 调整参数
        # ======================================

        payload = {
            "balance": "1500.00",
            "note": "自动化测试余额调整",
        }

        # ======================================
        # 发送余额调整请求
        # ======================================

        response = auth_client.post(
            adjust_url,
            json=payload,
        )

        assert response.status_code == 200, f"账户余额调整失败：" f"{response.text}"

        response_data = response.json()

        assert response_data.get("code") == 200

        data = response_data.get(
            "data",
            {},
        )

        # ======================================
        # 余额结果断言
        # ======================================

        assert data.get("balance") == payload["balance"]

        # ======================================
        # 查询余额调整记录
        # ======================================

        history_url = (
            f"{config.api_prefix}" f"/accounts/{account_id}/balance-adjustments/"
        )

        history_response = auth_client.get(history_url)

        assert history_response.status_code == 200, (
            f"查询余额调整记录失败：" f"{history_response.text}"
        )

        history_data = history_response.json()

        assert history_data.get("code") == 200

        records = history_data.get("data", [])

        # ======================================
        # 至少存在一条调整记录
        # ======================================

        assert records

    @allure.story("账户列表")
    @allure.title("查询账户列表成功")
    def test_account_list_success(
        self,
        auth_client,
        config,
    ):
        """
        验证账户列表查询成功。
        """

        url = f"{config.api_prefix}" f"/accounts/"

        response = auth_client.get(url)

        assert response.status_code == 200, f"查询账户列表失败：" f"{response.text}"

        response_data = response.json()

        assert response_data.get("code") == 200

        assert "data" in response_data

    @allure.story("删除账户")
    @allure.title("余额不为0时禁止删除账户")
    def test_delete_account_with_balance_failed(
        self,
        auth_client,
        config,
    ):
        """
        验证余额不为 0 的账户不能删除。
        """

        account_name = "删除失败账户_" f"{uuid.uuid4().hex[:8]}"

        create_url = f"{config.api_prefix}" f"/accounts/"

        payload = {
            "name": account_name,
            "account_type": "cash",
            "initial_balance": "100.00",
        }

        create_response = auth_client.post(
            create_url,
            json=payload,
        )

        assert create_response.status_code == 200

        create_data = create_response.json()

        account_id = create_data.get("data", {}).get("id")

        assert account_id

        delete_url = f"{config.api_prefix}" f"/accounts/{account_id}/"

        try:
            delete_response = auth_client.delete(delete_url)

            assert delete_response.status_code == 400

            delete_data = delete_response.json()

            assert delete_data.get("code") == 400

            assert "账户余额不为0" in delete_data.get(
                "message",
                "",
            )

        finally:
            # 当前账户余额不为 0，
            # 删除接口无法清理，
            # 后续可通过余额调整接口归零后再删除。
            adjust_url = (
                f"{config.api_prefix}" f"/accounts/{account_id}/" "adjust-balance/"
            )

            auth_client.post(
                adjust_url,
                json={
                    "balance": "0.00",
                    "note": "自动化清理测试账户",
                },
            )

            auth_client.delete(delete_url)

    @allure.story("新增账户")
    @allure.title("重复账户名称创建失败")
    def test_create_duplicate_account_name_failed(
        self,
        auth_client,
        config,
    ):
        """
        验证同一用户不能创建同名账户。
        """

        account_name = "重复账户_" f"{uuid.uuid4().hex[:8]}"

        url = f"{config.api_prefix}" f"/accounts/"

        payload = {
            "name": account_name,
            "account_type": "cash",
            "initial_balance": "0.00",
        }

        first_response = auth_client.post(
            url,
            json=payload,
        )

        assert first_response.status_code == 200

        first_data = first_response.json()

        account_id = first_data.get("data", {}).get("id")

        assert account_id

        try:
            second_response = auth_client.post(
                url,
                json=payload,
            )

            assert second_response.status_code == 400

            second_data = second_response.json()

            assert second_data.get("code") == 400

            assert "已存在同名账户" in second_data.get(
                "message",
                "",
            )

        finally:
            delete_url = f"{config.api_prefix}" f"/accounts/{account_id}/"

            auth_client.delete(delete_url)

    @allure.story("余额调整")
    @allure.title("余额调整记录内容正确")
    def test_balance_adjustment_record_success(
        self,
        auth_client,
        config,
        test_account,
    ):
        """
        验证余额调整记录内容正确。
        """

        account_id = test_account["id"]

        adjust_url = f"{config.api_prefix}" f"/accounts/{account_id}/" "adjust-balance/"

        payload = {
            "balance": "1500.00",
            "note": "余额记录校验",
        }

        response = auth_client.post(
            adjust_url,
            json=payload,
        )

        assert response.status_code == 200

        history_url = (
            f"{config.api_prefix}" f"/accounts/{account_id}/" "balance-adjustments/"
        )

        history_response = auth_client.get(history_url)

        assert history_response.status_code == 200

        history_data = history_response.json()

        assert history_data.get("code") == 200

        records = history_data.get(
            "data",
            [],
        )

        assert records

    @allure.story("账户转账")
    @allure.title("账户转账成功")
    def test_transfer_success(
        self,
        auth_client,
        config,
        transfer_accounts,
    ):
        """
        验证账户转账成功。

        验证内容：

        1. 转账接口调用成功；
        2. 转出账户余额减少；
        3. 转入账户余额增加；
        4. 金额变化正确。
        """

        # ======================================
        # 获取两个测试账户
        # ======================================

        source_account = transfer_accounts["source"]

        target_account = transfer_accounts["target"]

        source_id = source_account["id"]

        target_id = target_account["id"]

        # ======================================
        # 转账接口
        # ======================================

        transfer_url = f"{config.api_prefix}" f"/accounts/transfers/"

        # ======================================
        # 转账参数
        # ======================================

        payload = {
            "source_account_id": source_id,
            "target_account_id": target_id,
            "amount": "200.00",
            "transfer_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "自动化测试转账",
        }

        # ======================================
        # 发送转账请求
        # ======================================

        response = auth_client.post(
            transfer_url,
            json=payload,
        )

        assert response.status_code == 200, f"账户转账失败：" f"{response.text}"

        response_data = response.json()

        assert response_data.get("code") == 200

        # ======================================
        # 查询转出账户详情
        # ======================================

        source_url = f"{config.api_prefix}" f"/accounts/{source_id}/"

        source_response = auth_client.get(source_url)

        source_after = source_response.json().get(
            "data",
            {},
        )

        # ======================================
        # 查询转入账户详情
        # ======================================

        target_url = f"{config.api_prefix}" f"/accounts/{target_id}/"

        target_response = auth_client.get(target_url)

        target_after = target_response.json().get(
            "data",
            {},
        )

        # ======================================
        # 余额断言
        # ======================================

        assert source_after.get("balance") == "800.00"

        assert target_after.get("balance") == "700.00"

    @allure.story("账户转账")
    @allure.title("转账记录查询成功")
    def test_transfer_list_success(
        self,
        auth_client,
        config,
    ):
        """
        验证转账记录列表查询成功。

        验证内容：

        1. HTTP 状态码为 200；
        2. 业务 code 为 200；
        3. data 字段存在。
        """

        # ======================================
        # 转账记录列表接口
        # ======================================

        url = f"{config.api_prefix}" f"/accounts/transfers/"

        # ======================================
        # 发送请求
        # ======================================

        response = auth_client.get(url)

        assert response.status_code == 200, f"查询转账记录失败：" f"{response.text}"

        response_data = response.json()

        assert response_data.get("code") == 200

        assert "data" in response_data

    @allure.story("账户转账")
    @allure.title("余额不足时转账失败")
    def test_transfer_insufficient_balance(
        self,
        auth_client,
        config,
        transfer_accounts,
    ):
        """
        验证转出账户余额不足时，
        转账接口正确返回失败。

        验证内容：

        1. HTTP 状态码为 400；
        2. 业务 code 为 400；
        3. 返回余额不足相关提示；
        4. 转出、转入账户余额不应发生变化。
        """

        # ======================================
        # 获取测试账户
        # ======================================

        source_account = transfer_accounts["source"]

        target_account = transfer_accounts["target"]

        source_id = source_account["id"]

        target_id = target_account["id"]

        # ======================================
        # 转账接口
        # ======================================

        transfer_url = f"{config.api_prefix}" f"/accounts/transfers/"

        # ======================================
        # 构造超过账户余额的转账金额
        # ======================================
        #
        # fixture 中转出账户初始余额：
        # 1000.00
        #
        # 这里尝试转账：
        # 2000.00
        #
        # ======================================

        payload = {
            "source_account_id": source_id,
            "target_account_id": target_id,
            "amount": "2000.00",
            "transfer_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "余额不足转账测试",
        }

        # ======================================
        # 发送转账请求
        # ======================================

        response = auth_client.post(
            transfer_url,
            json=payload,
        )

        assert response.status_code == 400, (
            f"余额不足时接口未正确失败：" f"{response.text}"
        )

        response_data = response.json()

        assert response_data.get("code") == 400

        assert "余额不足" in response_data.get(
            "message",
            "",
        )

        # ======================================
        # 查询转出账户余额
        # ======================================

        source_url = f"{config.api_prefix}" f"/accounts/{source_id}/"

        source_response = auth_client.get(source_url)

        source_data = source_response.json().get(
            "data",
            {},
        )

        # ======================================
        # 查询转入账户余额
        # ======================================

        target_url = f"{config.api_prefix}" f"/accounts/{target_id}/"

        target_response = auth_client.get(target_url)

        target_data = target_response.json().get(
            "data",
            {},
        )

        # ======================================
        # 余额必须保持不变
        # ======================================

        assert source_data.get("balance") == "1000.00"

        assert target_data.get("balance") == "500.00"
