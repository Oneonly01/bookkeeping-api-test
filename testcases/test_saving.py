from decimal import Decimal
import allure


@allure.feature("目标储蓄")
class TestSaving:

    @allure.story("创建储蓄目标")
    @allure.title("创建储蓄目标成功")
    def test_create_saving_success(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证创建储蓄目标成功。
        """

        saving_id = None

        try:
            # ==================================
            # 构造储蓄目标
            # ==================================

            payload = saving_factory.build_saving(
                target_amount="10000.00",
                current_amount="0.00",
                deadline="2027-12-31",
            )

            # ==================================
            # 创建储蓄目标
            # ==================================

            response = saving_api.create_saving(payload)

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert response.status_code == 200, (
                f"创建储蓄目标失败，"
                f"status_code="
                f"{response.status_code}，"
                f"response="
                f"{response.text}"
            )

            # ==================================
            # 解析响应
            # ==================================

            response_data = response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert response_data.get("code") == 200, (
                f"创建储蓄目标业务失败：" f"{response_data}"
            )

            # ==================================
            # 获取返回数据
            # ==================================

            saving_data = response_data.get(
                "data",
                {},
            )

            # ==================================
            # 获取 ID
            # ==================================

            saving_id = saving_data.get("id")

            assert saving_id, f"创建储蓄目标后" f"未返回 saving_id：" f"{response_data}"

        finally:
            # ==================================
            # 清理测试数据
            # ==================================

            if saving_id:

                delete_response = saving_api.delete_saving(saving_id)

                if delete_response.status_code != 200:
                    print(
                        f"储蓄目标测试数据"
                        f"清理失败，"
                        f"saving_id="
                        f"{saving_id}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("查询储蓄目标")
    @allure.title("查询储蓄目标详情成功")
    def test_get_saving_detail_success(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证查询储蓄目标详情成功。

        测试流程：

        1. 创建一个测试储蓄目标；
        2. 获取 saving_id；
        3. 查询储蓄目标详情；
        4. 验证 HTTP 状态码；
        5. 验证业务状态码；
        6. 验证目标 ID；
        7. 验证目标名称；
        8. 验证目标金额；
        9. 验证当前已存金额；
        10. 验证截止日期；
        11. 清理测试数据。
        """

        # ======================================
        # 初始化储蓄目标 ID
        # ======================================

        saving_id = None

        try:
            # ==================================
            # 构造储蓄目标
            # ==================================

            payload = saving_factory.build_saving(
                target_amount="12000.00",
                current_amount="0.00",
                deadline="2027-12-31",
            )

            # ==================================
            # 创建储蓄目标
            # ==================================

            create_response = saving_api.create_saving(payload)

            # ==================================
            # 创建接口 HTTP 状态码断言
            # ==================================

            assert create_response.status_code == 200, (
                f"创建详情测试储蓄目标失败，"
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
            # 创建接口业务状态码断言
            # ==================================

            assert create_response_data.get("code") == 200, (
                f"创建详情测试储蓄目标" f"业务失败：" f"{create_response_data}"
            )

            # ==================================
            # 获取创建后的数据
            # ==================================

            create_data = create_response_data.get(
                "data",
                {},
            )

            assert isinstance(
                create_data,
                dict,
            ), (
                f"创建储蓄目标返回 data " f"结构错误：" f"{create_response_data}"
            )

            # ==================================
            # 获取储蓄目标 ID
            # ==================================

            saving_id = create_data.get("id")

            assert saving_id, (
                f"创建储蓄目标后" f"未返回 saving_id：" f"{create_response_data}"
            )

            # ==================================
            # 查询储蓄目标详情
            # ==================================

            detail_response = saving_api.get_saving_detail(saving_id)

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert detail_response.status_code == 200, (
                f"查询储蓄目标详情失败，"
                f"status_code="
                f"{detail_response.status_code}，"
                f"response="
                f"{detail_response.text}"
            )

            # ==================================
            # 解析详情响应
            # ==================================

            detail_response_data = detail_response.json()

            # ==================================
            # 业务状态码断言
            # ==================================

            assert detail_response_data.get("code") == 200, (
                f"查询储蓄目标详情" f"业务失败：" f"{detail_response_data}"
            )

            # ==================================
            # 获取详情数据
            # ==================================

            detail_data = detail_response_data.get(
                "data",
                {},
            )

            assert isinstance(
                detail_data,
                dict,
            ), (
                f"储蓄目标详情 data " f"结构错误：" f"{detail_response_data}"
            )

            # ==================================
            # ID 断言
            # ==================================

            assert detail_data.get("id") == saving_id, (
                f"储蓄目标 ID 不一致，"
                f"expected="
                f"{saving_id}，"
                f"actual="
                f"{detail_data.get('id')}"
            )

            # ==================================
            # 名称断言
            # ==================================

            if "name" in detail_data:
                assert detail_data.get("name") == payload.get("name"), (
                    f"储蓄目标名称不一致，"
                    f"expected="
                    f"{payload.get('name')}，"
                    f"actual="
                    f"{detail_data.get('name')}"
                )

            # ==================================
            # 目标金额断言
            # ==================================

            if "target_amount" in detail_data:
                assert str(detail_data.get("target_amount")) == str(
                    payload.get("target_amount")
                ), (
                    f"储蓄目标金额不一致，"
                    f"expected="
                    f"{payload.get('target_amount')}，"
                    f"actual="
                    f"{detail_data.get('target_amount')}"
                )

            # ==================================
            # 当前已存金额断言
            # ==================================

            if "current_amount" in detail_data:
                assert str(detail_data.get("current_amount")) == str(
                    payload.get("current_amount")
                ), (
                    f"当前已存金额不一致，"
                    f"expected="
                    f"{payload.get('current_amount')}，"
                    f"actual="
                    f"{detail_data.get('current_amount')}"
                )

            # ==================================
            # 截止日期断言
            # ==================================

            if "deadline" in detail_data:
                assert str(detail_data.get("deadline")) == str(
                    payload.get("deadline")
                ), (
                    f"储蓄目标截止日期不一致，"
                    f"expected="
                    f"{payload.get('deadline')}，"
                    f"actual="
                    f"{detail_data.get('deadline')}"
                )

        finally:
            # ==================================
            # 清理测试储蓄目标
            # ==================================

            if saving_id:

                delete_response = saving_api.delete_saving(saving_id)

                if delete_response.status_code != 200:
                    print(
                        f"储蓄目标详情测试数据"
                        f"清理失败，"
                        f"saving_id="
                        f"{saving_id}，"
                        f"status_code="
                        f"{delete_response.status_code}，"
                        f"response="
                        f"{delete_response.text}"
                    )

    @allure.story("修改储蓄目标")
    @allure.title("修改储蓄目标成功")
    def test_update_saving_success(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证修改储蓄目标成功。

        后端允许修改：

        1. name
        2. target_amount
        3. deadline
        4. icon
        5. color
        6. note

        测试流程：

        1. 创建测试储蓄目标；
        2. 查询修改前详情；
        3. 修改允许更新的字段；
        4. 验证修改接口返回成功；
        5. 再次查询储蓄目标详情；
        6. 验证修改后的字段已保存；
        7. 验证当前已存金额没有变化；
        8. 删除测试储蓄目标。
        """

        # ======================================
        # 初始化储蓄目标 ID
        # ======================================

        saving_id = None

        try:
            # ==================================
            # 构造创建数据
            # ==================================

            create_payload = saving_factory.build_saving(
                target_amount="10000.00",
                current_amount="0.00",
                deadline="2027-12-31",
            )

            # ==================================
            # 创建储蓄目标
            # ==================================

            create_response = saving_api.create_saving(create_payload)

            assert create_response.status_code == 200, (
                f"创建储蓄目标失败：" f"{create_response.text}"
            )

            create_result = create_response.json()

            assert create_result.get("code") == 200, (
                f"创建储蓄目标业务失败：" f"{create_result}"
            )

            create_data = create_result.get("data", {})

            assert isinstance(create_data, dict)

            saving_id = create_data.get("id")

            assert saving_id, f"创建成功后未返回储蓄目标 ID：" f"{create_result}"

            # ==================================
            # 查询修改前详情
            # ==================================

            before_response = saving_api.get_saving_detail(saving_id)

            assert before_response.status_code == 200, (
                f"修改前查询详情失败：" f"{before_response.text}"
            )

            before_result = before_response.json()

            assert before_result.get("code") == 200

            before_data = before_result.get("data", {})

            assert isinstance(before_data, dict)

            assert before_data.get("id") == saving_id

            # ==================================
            # 保存原始已存金额
            # ==================================
            #
            # current_amount 不属于普通更新字段。
            #
            # 修改目标名称、金额、日期等信息，
            # 不应该改变已经存入的资金。
            #
            # ==================================

            original_current_amount = Decimal(str(before_data["current_amount"]))

            # ==================================
            # 构造修改请求
            # ==================================
            #
            # 仅传后端允许修改的字段。
            #
            # icon/color 的示例值需要符合
            # 后端 Serializer 的实际校验规则。
            #
            # ==================================

            update_payload = {
                "name": "自动化测试-修改后的储蓄目标",
                "target_amount": "15000.00",
                "deadline": "2028-12-31",
                "icon": "piggy-bank",
                "color": "#27BA9B",
                "note": "自动化测试-储蓄目标修改成功",
            }

            # ==================================
            # 调用修改接口
            # ==================================

            update_response = saving_api.update_saving(
                saving_id,
                update_payload,
            )

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert update_response.status_code == 200, (
                f"修改储蓄目标失败，"
                f"status_code={update_response.status_code}，"
                f"response={update_response.text}"
            )

            # ==================================
            # 修改业务状态码断言
            # ==================================

            update_result = update_response.json()

            assert update_result.get("code") == 200, (
                f"修改储蓄目标业务失败：" f"{update_result}"
            )

            # ==================================
            # 再次查询详情
            # ==================================
            #
            # 不能只验证修改接口返回 200。
            #
            # 还要通过 GET 确认最终保存结果。
            #
            # ==================================

            detail_response = saving_api.get_saving_detail(saving_id)

            assert detail_response.status_code == 200, (
                f"修改后查询储蓄目标失败：" f"{detail_response.text}"
            )

            detail_result = detail_response.json()

            assert detail_result.get("code") == 200, (
                f"修改后查询储蓄目标业务失败：" f"{detail_result}"
            )

            detail_data = detail_result.get("data", {})

            assert isinstance(detail_data, dict), (
                f"详情返回结构错误：" f"{detail_result}"
            )

            # ==================================
            # ID 保持不变
            # ==================================

            assert detail_data.get("id") == saving_id, (
                f"修改后储蓄目标 ID 不一致：" f"{detail_data}"
            )

            # ==================================
            # 验证目标名称
            # ==================================

            assert detail_data.get("name") == update_payload["name"], (
                f"储蓄目标名称修改失败：" f"{detail_data}"
            )

            # ==================================
            # 验证目标金额
            # ==================================
            #
            # 金额使用 Decimal 比较，
            # 避免字符串格式差异影响判断。
            #
            # ==================================

            assert Decimal(str(detail_data["target_amount"])) == Decimal(
                update_payload["target_amount"]
            ), (f"目标金额修改失败：" f"{detail_data}")

            # ==================================
            # 验证截止日期
            # ==================================

            assert str(detail_data.get("deadline")) == (update_payload["deadline"]), (
                f"截止日期修改失败：" f"{detail_data}"
            )

            # ==================================
            # 验证图标
            # ==================================

            assert detail_data.get("icon") == update_payload["icon"], (
                f"图标修改失败：" f"{detail_data}"
            )

            # ==================================
            # 验证颜色
            # ==================================

            assert detail_data.get("color") == update_payload["color"], (
                f"颜色修改失败：" f"{detail_data}"
            )

            # ==================================
            # 验证备注
            # ==================================

            assert detail_data.get("note") == update_payload["note"], (
                f"备注修改失败：" f"{detail_data}"
            )

            # ==================================
            # 验证当前已存金额保持不变
            # ==================================
            #
            # 修改目标金额不等于存入资金。
            #
            # 因此：
            #
            # current_amount 必须保持原值。
            #
            # ==================================

            actual_current_amount = Decimal(str(detail_data["current_amount"]))

            assert actual_current_amount == original_current_amount, (
                f"修改储蓄目标后，当前已存金额发生变化，"
                f"before={original_current_amount}，"
                f"after={actual_current_amount}"
            )

        finally:
            # ==================================
            # 清理测试数据
            # ==================================
            #
            # 无论中途断言是否失败，
            # 都尝试清理本次创建的数据。
            #
            # ==================================

            if saving_id:

                delete_response = saving_api.delete_saving(saving_id)

                if delete_response.status_code != 200:
                    print(
                        f"储蓄目标测试数据清理失败，"
                        f"saving_id={saving_id}，"
                        f"response={delete_response.text}"
                    )

    @allure.story("删除储蓄目标")
    @allure.title("删除储蓄目标成功且删除后不可查询")
    def test_delete_saving_success(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证储蓄目标删除成功。

        测试流程：

        1. 创建储蓄目标；
        2. 获取目标 ID；
        3. 查询详情，确认目标存在；
        4. 删除储蓄目标；
        5. 验证删除接口成功；
        6. 再次查询详情；
        7. 验证已经删除的目标不可查询。

        测试重点：

        DELETE 返回成功并不代表删除逻辑正确。

        必须通过再次查询来验证：

            已删除目标不再对用户可见。

        该测试同时适用于后端使用逻辑删除的情况。
        """

        # ======================================
        # 初始化测试变量
        # ======================================

        saving_id = None

        # 标记是否已经删除成功。
        # 避免 finally 重复删除同一个目标。
        saving_deleted = False

        try:
            # ======================================
            # 1. 构造储蓄目标测试数据
            # ======================================

            create_payload = saving_factory.build_saving(
                target_amount="8000.00",
                current_amount="0.00",
                deadline="2027-12-31",
            )

            # ======================================
            # 2. 创建储蓄目标
            # ======================================

            create_response = saving_api.create_saving(create_payload)

            # HTTP 状态码断言。
            assert create_response.status_code == 200, (
                f"创建储蓄目标失败，"
                f"status_code={create_response.status_code}，"
                f"response={create_response.text}"
            )

            # 解析响应。
            create_result = create_response.json()

            # 业务状态码断言。
            assert create_result.get("code") == 200, (
                f"创建储蓄目标业务失败：" f"{create_result}"
            )

            # 获取创建后的目标信息。
            create_data = create_result.get("data")

            assert isinstance(create_data, dict), (
                f"创建储蓄目标返回数据结构错误：" f"{create_result}"
            )

            saving_id = create_data.get("id")

            assert saving_id, f"创建储蓄目标后未返回 ID：" f"{create_result}"

            # ======================================
            # 3. 删除前查询储蓄目标
            # ======================================
            #
            # 确认本次创建的目标确实存在，
            # 避免后续直接删除导致验证链路不完整。
            # ======================================

            before_response = saving_api.get_saving_detail(saving_id)

            assert before_response.status_code == 200, (
                f"删除前查询储蓄目标失败：" f"{before_response.text}"
            )

            before_result = before_response.json()

            assert before_result.get("code") == 200, (
                f"删除前查询储蓄目标业务失败：" f"{before_result}"
            )

            before_data = before_result.get("data")

            assert isinstance(before_data, dict)

            assert before_data.get("id") == saving_id, (
                f"删除前查询到错误的储蓄目标：" f"{before_data}"
            )

            # ======================================
            # 4. 删除储蓄目标
            # ======================================

            delete_response = saving_api.delete_saving(saving_id)

            # ======================================
            # 5. 删除接口 HTTP 状态码断言
            # ======================================

            assert delete_response.status_code == 200, (
                f"删除储蓄目标失败，"
                f"status_code={delete_response.status_code}，"
                f"response={delete_response.text}"
            )

            # ======================================
            # 6. 删除接口业务状态码断言
            # ======================================

            delete_result = delete_response.json()

            assert delete_result.get("code") == 200, (
                f"删除储蓄目标业务失败：" f"{delete_result}"
            )

            # 标记删除接口已经成功。
            saving_deleted = True

            # ======================================
            # 7. 删除后再次查询详情
            # ======================================

            after_response = saving_api.get_saving_detail(saving_id)

            # ======================================
            # 8. 验证删除后不可查询
            # ======================================
            #
            # 目前尚未确认后端具体返回：
            #
            # HTTP 404
            # HTTP 400
            #
            # 因此先验证不能返回成功。
            #
            # 后续确认接口契约后，
            # 应改为明确的预期状态码。
            # ======================================

            assert after_response.status_code in (400, 404), (
                f"储蓄目标删除后仍然可以查询，"
                f"saving_id={saving_id}，"
                f"status_code={after_response.status_code}，"
                f"response={after_response.text}"
            )

            # ======================================
            # 9. 验证业务状态码
            # ======================================

            after_result = after_response.json()

            assert after_result.get("code") != 200, (
                f"储蓄目标已经删除，" f"但查询详情仍然返回业务成功：" f"{after_result}"
            )

            # ======================================
            # 10. 验证不返回有效目标数据
            # ======================================

            after_data = after_result.get("data")

            if isinstance(after_data, dict):
                assert not after_data.get("id"), (
                    f"删除后仍然返回有效储蓄目标：" f"{after_result}"
                )

        finally:
            # ======================================
            # 11. 清理测试数据
            # ======================================
            #
            # 如果测试在主动删除之前失败，
            # 则尝试执行清理。
            #
            # 如果已经删除成功，则不重复删除。
            # ======================================

            if saving_id and not saving_deleted:

                try:
                    cleanup_response = saving_api.delete_saving(saving_id)

                    if cleanup_response.status_code != 200:
                        print(
                            f"储蓄目标清理失败，"
                            f"saving_id={saving_id}，"
                            f"status_code={cleanup_response.status_code}，"
                            f"response={cleanup_response.text}"
                        )

                except Exception as error:
                    print(
                        f"储蓄目标清理发生异常，"
                        f"saving_id={saving_id}，"
                        f"error={error}"
                    )

    @allure.story("储蓄资金管理")
    @allure.title("储蓄目标存入资金成功")
    def test_deposit_saving_success(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证储蓄目标存入资金成功。

        后端业务规则：

        1. 只能操作当前用户的储蓄目标；
        2. 已删除的目标不能存入；
        3. 已暂停的目标不能存入；
        4. 已完成的目标不能继续存入；
        5. 存入金额必须大于 0；
        6. 成功存入后 current_amount 增加；
        7. 成功存入后生成一条存入流水；
        8. 达到目标金额后自动标记 completed。

        当前测试场景：

            目标金额：10000.00
            初始已存：0.00
            存入金额：500.00
            预期已存：500.00

        测试流程：

        1. 创建储蓄目标；
        2. 查询存入前详情；
        3. 查询存入前流水；
        4. 存入 500.00 元；
        5. 验证存入接口成功；
        6. 查询存入后详情；
        7. 验证当前已存金额；
        8. 验证目标金额未改变；
        9. 查询存入后流水；
        10. 验证新增一条存入流水；
        11. 验证流水金额；
        12. 验证流水变动前金额；
        13. 验证流水变动后金额；
        14. 验证流水备注；
        15. 删除测试数据。
        """

        # ======================================
        # 初始化测试变量
        # ======================================

        saving_id = None

        # ======================================
        # 本次存入金额
        # ======================================
        #
        # 金额必须使用 Decimal。
        #
        # 不使用 float，
        # 避免浮点数计算误差。
        #
        # ======================================

        deposit_amount = Decimal("500.00")

        try:
            # ==================================
            # 1. 构造储蓄目标数据
            # ==================================

            create_payload = saving_factory.build_saving(
                target_amount="10000.00",
                current_amount="0.00",
                deadline="2027-12-31",
            )

            # ==================================
            # 2. 创建储蓄目标
            # ==================================

            create_response = saving_api.create_saving(create_payload)

            # ==================================
            # 创建接口 HTTP 状态码断言
            # ==================================

            assert create_response.status_code == 200, (
                f"创建储蓄目标失败，"
                f"status_code={create_response.status_code}，"
                f"response={create_response.text}"
            )

            # ==================================
            # 解析创建响应
            # ==================================

            create_result = create_response.json()

            # ==================================
            # 创建接口业务状态码断言
            # ==================================

            assert create_result.get("code") == 200, (
                f"创建储蓄目标业务失败：" f"{create_result}"
            )

            # ==================================
            # 获取创建后的目标数据
            # ==================================

            create_data = create_result.get("data")

            assert isinstance(create_data, dict), (
                f"创建储蓄目标返回结构错误：" f"{create_result}"
            )

            # ==================================
            # 获取储蓄目标 ID
            # ==================================

            saving_id = create_data.get("id")

            assert saving_id, f"创建储蓄目标后未返回 saving_id：" f"{create_result}"

            # ==================================
            # 3. 查询存入前储蓄目标详情
            # ==================================

            before_response = saving_api.get_saving_detail(saving_id)

            # ==================================
            # 查询 HTTP 状态码断言
            # ==================================

            assert before_response.status_code == 200, (
                f"查询存入前储蓄目标失败，"
                f"status_code={before_response.status_code}，"
                f"response={before_response.text}"
            )

            # ==================================
            # 解析存入前详情
            # ==================================

            before_result = before_response.json()

            assert before_result.get("code") == 200, (
                f"查询存入前储蓄目标业务失败：" f"{before_result}"
            )

            before_data = before_result.get("data")

            assert isinstance(before_data, dict), (
                f"存入前详情结构错误：" f"{before_result}"
            )

            # ==================================
            # 验证储蓄目标 ID
            # ==================================

            assert before_data.get("id") == saving_id, (
                f"查询到的储蓄目标 ID 不正确：" f"{before_data}"
            )

            # ==================================
            # 4. 获取存入前当前已存金额
            # ==================================

            before_amount = Decimal(str(before_data["current_amount"]))

            # ==================================
            # 5. 获取目标金额
            # ==================================
            #
            # 后面存入资金后，
            # 需要验证 target_amount 没有变化。
            #
            # ==================================

            target_amount = Decimal(str(before_data["target_amount"]))

            # ==================================
            # 初始金额断言
            # ==================================

            assert before_amount == Decimal("0.00"), (
                f"新建储蓄目标初始金额错误，"
                f"expected=0.00，"
                f"actual={before_amount}"
            )

            # ==================================
            # 目标金额断言
            # ==================================

            assert target_amount == Decimal("10000.00"), (
                f"储蓄目标金额错误，" f"expected=10000.00，" f"actual={target_amount}"
            )

            # ==================================
            # 6. 查询存入前储蓄流水
            # ==================================

            before_records_response = saving_api.get_records(saving_id)

            assert before_records_response.status_code == 200, (
                f"查询存入前流水失败，"
                f"status_code={before_records_response.status_code}，"
                f"response={before_records_response.text}"
            )

            before_records_result = before_records_response.json()

            assert before_records_result.get("code") == 200, (
                f"查询存入前流水业务失败：" f"{before_records_result}"
            )

            # ==================================
            # 获取存入前流水列表
            # ======================================
            #
            # 兼容以下常见返回格式：
            #
            # data: [...]
            #
            # data: {
            #     "results": [...]
            # }
            #
            # data: {
            #     "records": [...]
            # }
            #
            # ==================================

            before_records = before_records_result.get(
                "data",
                [],
            )

            if isinstance(before_records, dict):
                before_records = before_records.get(
                    "results",
                    before_records.get(
                        "records",
                        [],
                    ),
                )

            # ==================================
            # 流水列表结构断言
            # ==================================

            assert isinstance(before_records, list), (
                f"存入前流水列表结构错误：" f"{before_records_result}"
            )

            # ==================================
            # 保存存入前流水 ID
            # ======================================
            #
            # 后续通过 ID 差集，
            # 确认本次存入新增了哪条流水。
            #
            # ==================================

            before_record_ids = {item["id"] for item in before_records}

            # ==================================
            # 7. 构造存入资金请求
            # ======================================
            #
            # 根据后端 deposit() 方法确认：
            #
            # amount：必填
            #
            # note：可选
            #
            # ==================================

            deposit_payload = {
                "amount": str(deposit_amount),
                "note": "自动化测试-存入500元",
            }

            # ==================================
            # 8. 调用存入资金接口
            # ==================================

            deposit_response = saving_api.deposit(
                saving_id,
                deposit_payload,
            )

            # ==================================
            # 存入接口 HTTP 状态码断言
            # ==================================

            assert deposit_response.status_code == 200, (
                f"储蓄目标存入资金失败，"
                f"status_code={deposit_response.status_code}，"
                f"response={deposit_response.text}"
            )

            # ==================================
            # 9. 解析存入响应
            # ==================================

            deposit_result = deposit_response.json()

            # ==================================
            # 存入接口业务状态码断言
            # ==================================

            assert deposit_result.get("code") == 200, (
                f"储蓄目标存入资金业务失败：" f"{deposit_result}"
            )

            # ==================================
            # 10. 存入后重新查询目标详情
            # ======================================

            after_response = saving_api.get_saving_detail(saving_id)

            assert after_response.status_code == 200, (
                f"存入资金后查询详情失败，"
                f"status_code={after_response.status_code}，"
                f"response={after_response.text}"
            )

            # ==================================
            # 解析存入后详情
            # ==================================

            after_result = after_response.json()

            assert after_result.get("code") == 200, (
                f"存入资金后查询详情业务失败：" f"{after_result}"
            )

            after_data = after_result.get("data")

            assert isinstance(after_data, dict), (
                f"存入资金后详情结构错误：" f"{after_result}"
            )

            # ==================================
            # 11. 验证储蓄目标 ID 不变
            # ==================================

            assert after_data.get("id") == saving_id, (
                f"存入资金后储蓄目标 ID 发生变化：" f"{after_data}"
            )

            # ==================================
            # 12. 验证 current_amount
            # ======================================
            #
            # 后端计算规则：
            #
            # after_amount
            # =
            # before_amount + deposit_amount
            #
            # ==================================

            after_amount = Decimal(str(after_data["current_amount"]))

            expected_amount = before_amount + deposit_amount

            assert after_amount == expected_amount, (
                f"储蓄目标存入后金额错误，"
                f"before={before_amount}，"
                f"deposit={deposit_amount}，"
                f"expected={expected_amount}，"
                f"actual={after_amount}"
            )

            # ==================================
            # 13. 验证目标金额保持不变
            # ======================================

            actual_target_amount = Decimal(str(after_data["target_amount"]))

            assert actual_target_amount == target_amount, (
                f"存入资金后目标金额发生变化，"
                f"expected={target_amount}，"
                f"actual={actual_target_amount}"
            )

            # ==================================
            # 14. 验证存入后未达到目标金额
            # ======================================
            #
            # 当前：
            #
            # 500.00 < 10000.00
            #
            # 因此不应该进入 completed。
            #
            # ==================================

            assert after_amount < target_amount, (
                f"当前测试数据已经达到目标金额，"
                f"after_amount={after_amount}，"
                f"target_amount={target_amount}"
            )

            # ==================================
            # 验证目标未被错误标记为完成
            # ======================================
            #
            # 后端完成状态对应 completed。
            #
            # 当前未达到目标金额，
            # 不应该自动完成。
            #
            # ==================================

            if "status" in after_data:
                assert after_data["status"] != "completed", (
                    f"尚未达到目标金额，" f"储蓄目标却被标记为完成：" f"{after_data}"
                )

            # ==================================
            # 15. 查询存入后的储蓄流水
            # ==================================

            records_response = saving_api.get_records(saving_id)

            assert records_response.status_code == 200, (
                f"查询存入后流水失败，"
                f"status_code={records_response.status_code}，"
                f"response={records_response.text}"
            )

            # ==================================
            # 解析储蓄流水响应
            # ==================================

            records_result = records_response.json()

            assert records_result.get("code") == 200, (
                f"查询存入后储蓄流水业务失败：" f"{records_result}"
            )

            # ==================================
            # 16. 获取存入后流水列表
            # ==================================

            records = records_result.get(
                "data",
                [],
            )

            if isinstance(records, dict):
                records = records.get(
                    "results",
                    records.get(
                        "records",
                        [],
                    ),
                )

            assert isinstance(records, list), (
                f"存入后储蓄流水结构错误：" f"{records_result}"
            )

            # ==================================
            # 17. 查找本次新增的流水
            # ======================================
            #
            # 通过存入前和存入后的 ID 差集，
            # 找到本次新增的流水。
            #
            # ==================================

            new_records = [
                item for item in records if item.get("id") not in before_record_ids
            ]

            # ==================================
            # 18. 验证只新增一条流水
            # ======================================

            assert len(new_records) == 1, (
                f"存入一次资金应新增一条流水，"
                f"实际新增={len(new_records)}，"
                f"before_ids={before_record_ids}，"
                f"records={records}"
            )

            # ==================================
            # 获取本次存入流水
            # ==================================

            record = new_records[0]

            # ==================================
            # 19. 验证流水金额
            # ======================================

            actual_record_amount = Decimal(str(record["amount"]))

            assert actual_record_amount == deposit_amount, (
                f"存入流水金额错误，"
                f"expected={deposit_amount}，"
                f"actual={actual_record_amount}"
            )

            # ==================================
            # 20. 验证变动前金额
            # ======================================

            actual_before_amount = Decimal(str(record["before_amount"]))

            assert actual_before_amount == before_amount, (
                f"存入流水变动前金额错误，"
                f"expected={before_amount}，"
                f"actual={actual_before_amount}"
            )

            # ==================================
            # 21. 验证变动后金额
            # ======================================

            actual_after_amount = Decimal(str(record["after_amount"]))

            assert actual_after_amount == expected_amount, (
                f"存入流水变动后金额错误，"
                f"expected={expected_amount}，"
                f"actual={actual_after_amount}"
            )

            # ==================================
            # 22. 验证流水备注
            # ======================================

            assert record.get("note") == deposit_payload["note"], (
                f"存入流水备注错误，"
                f"expected={deposit_payload['note']}，"
                f"actual={record.get('note')}"
            )

            # ==================================
            # 23. 验证流水所属储蓄目标
            # ======================================
            #
            # 后端 SavingsRecord 使用：
            #
            # goal=goal
            #
            # 如果接口返回 goal 或 goal_id，
            # 验证流水关联正确。
            #
            # ==================================

            if "goal_id" in record:
                assert int(record["goal_id"]) == int(saving_id), (
                    f"存入流水所属目标错误：" f"{record}"
                )

            elif "goal" in record:
                record_goal = record["goal"]

                if isinstance(record_goal, dict):
                    record_goal = record_goal.get("id")

                assert int(record_goal) == int(saving_id), (
                    f"存入流水所属目标错误：" f"{record}"
                )

            # ==================================
            # 24. 输出本次新增流水
            # ======================================
            #
            # 用于首次确认实际 record_type 值。
            #
            # 后端：
            #
            # SavingsRecord.RecordType.DEPOSIT
            #
            # 但尚未看到该枚举对应的数据库值。
            #
            # 因此暂时不猜测是：
            #
            # deposit
            #
            # 还是其他枚举。
            #
            # ==================================

            print(
                "本次新增储蓄流水：",
                record,
            )

            # ==================================
            # 输出存入后的储蓄目标
            # ==================================

            print(
                "存入后储蓄目标：",
                after_data,
            )

        finally:
            # ==================================
            # 25. 清理测试储蓄目标
            # ======================================
            #
            # 发生断言失败时仍然尝试清理。
            #
            # 如果后端禁止删除含有流水的目标，
            # 清理失败会在控制台打印，
            # 不直接覆盖原始断言错误。
            #
            # ==================================

            if saving_id:

                try:
                    delete_response = saving_api.delete_saving(saving_id)

                    if delete_response.status_code != 200:
                        print(
                            f"储蓄目标测试数据清理失败，"
                            f"saving_id={saving_id}，"
                            f"status_code={delete_response.status_code}，"
                            f"response={delete_response.text}"
                        )

                except Exception as error:
                    print(
                        f"储蓄目标测试数据清理异常，"
                        f"saving_id={saving_id}，"
                        f"error={error}"
                    )

    @allure.story("储蓄资金管理")
    @allure.title("存入资金达到目标金额后自动完成")
    def test_deposit_saving_auto_completed_success(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证存入资金达到目标金额后，
        储蓄目标自动进入已完成状态。

        后端业务规则：

            if after_amount >= goal.target_amount:
                goal.status = SavingsGoal.Status.COMPLETED

        测试数据：

            目标金额：1000.00
            初始已存：0.00
            存入金额：1000.00

        预期结果：

            current_amount = 1000.00
            target_amount = 1000.00
            status = completed

        测试流程：

        1. 创建储蓄目标；
        2. 查询存入前详情；
        3. 查询存入前流水；
        4. 存入 1000.00；
        5. 验证存入接口成功；
        6. 查询存入后详情；
        7. 验证当前已存金额；
        8. 验证目标状态自动完成；
        9. 验证新增一条资金流水；
        10. 验证流水金额及前后余额；
        11. 清理测试数据。
        """

        # ======================================
        # 初始化测试变量
        # ======================================

        saving_id = None

        target_amount = Decimal("1000.00")
        deposit_amount = Decimal("1000.00")

        try:
            # ==================================
            # 1. 构造储蓄目标
            # ======================================

            create_payload = saving_factory.build_saving(
                target_amount=str(target_amount),
                current_amount="0.00",
                deadline="2027-12-31",
            )

            # ==================================
            # 2. 创建储蓄目标
            # ==================================

            create_response = saving_api.create_saving(create_payload)

            assert create_response.status_code == 200, (
                f"创建储蓄目标失败：" f"{create_response.text}"
            )

            create_result = create_response.json()

            assert create_result.get("code") == 200, (
                f"创建储蓄目标业务失败：" f"{create_result}"
            )

            create_data = create_result.get("data")

            assert isinstance(create_data, dict), (
                f"创建储蓄目标返回结构错误：" f"{create_result}"
            )

            saving_id = create_data.get("id")

            assert saving_id, f"创建储蓄目标后未返回 ID：" f"{create_result}"

            # ==================================
            # 3. 查询存入前详情
            # ==================================

            before_response = saving_api.get_saving_detail(saving_id)

            assert before_response.status_code == 200, (
                f"存入前查询详情失败：" f"{before_response.text}"
            )

            before_result = before_response.json()

            assert before_result.get("code") == 200

            before_data = before_result.get("data")

            assert isinstance(before_data, dict)

            # ==================================
            # 4. 记录初始金额
            # ==================================

            before_amount = Decimal(str(before_data["current_amount"]))

            assert before_amount == Decimal("0.00"), (
                f"储蓄目标初始金额错误：" f"{before_amount}"
            )

            # ==================================
            # 5. 查询存入前流水
            # ==================================

            before_records_response = saving_api.get_records(saving_id)

            assert before_records_response.status_code == 200, (
                f"查询存入前流水失败：" f"{before_records_response.text}"
            )

            before_records_result = before_records_response.json()

            assert before_records_result.get("code") == 200

            before_records = before_records_result.get(
                "data",
                [],
            )

            # ==================================
            # 兼容流水列表分页结构
            # ==================================

            if isinstance(before_records, dict):
                before_records = before_records.get(
                    "results",
                    before_records.get("records", []),
                )

            assert isinstance(before_records, list), (
                f"存入前流水结构错误：" f"{before_records_result}"
            )

            # 保存已有流水 ID。
            before_record_ids = {record["id"] for record in before_records}

            # ==================================
            # 6. 构造存入请求
            # ==================================

            deposit_payload = {
                "amount": str(deposit_amount),
                "note": "自动化测试-达到目标自动完成",
            }

            # ==================================
            # 7. 存入资金
            # ==================================

            deposit_response = saving_api.deposit(
                saving_id,
                deposit_payload,
            )

            # ==================================
            # HTTP 状态码断言
            # ==================================

            assert deposit_response.status_code == 200, (
                f"存入目标金额失败，"
                f"status_code={deposit_response.status_code}，"
                f"response={deposit_response.text}"
            )

            # ==================================
            # 业务状态码断言
            # ==================================

            deposit_result = deposit_response.json()

            assert deposit_result.get("code") == 200, (
                f"存入资金业务失败：" f"{deposit_result}"
            )

            # ==================================
            # 8. 查询存入后详情
            # ==================================

            after_response = saving_api.get_saving_detail(saving_id)

            assert after_response.status_code == 200, (
                f"存入后查询详情失败：" f"{after_response.text}"
            )

            after_result = after_response.json()

            assert after_result.get("code") == 200, (
                f"存入后查询详情业务失败：" f"{after_result}"
            )

            after_data = after_result.get("data")

            assert isinstance(after_data, dict), (
                f"存入后详情结构错误：" f"{after_result}"
            )

            # ==================================
            # 9. 验证储蓄目标 ID
            # ==================================

            assert after_data.get("id") == saving_id, (
                f"储蓄目标 ID 不一致：" f"{after_data}"
            )

            # ==================================
            # 10. 验证已存金额
            # ==================================
            #
            # current_amount：
            #
            # 0.00 + 1000.00 = 1000.00
            #
            # ==================================

            after_amount = Decimal(str(after_data["current_amount"]))

            expected_amount = before_amount + deposit_amount

            assert after_amount == expected_amount, (
                f"存入后金额不正确，"
                f"expected={expected_amount}，"
                f"actual={after_amount}"
            )

            # ==================================
            # 11. 验证目标金额不变
            # ==================================

            actual_target_amount = Decimal(str(after_data["target_amount"]))

            assert actual_target_amount == target_amount, (
                f"目标金额发生异常变化，"
                f"expected={target_amount}，"
                f"actual={actual_target_amount}"
            )

            # ==================================
            # 12. 验证已达到目标金额
            # ==================================

            assert after_amount >= target_amount, (
                f"当前金额尚未达到目标金额，"
                f"current={after_amount}，"
                f"target={target_amount}"
            )

            # ==================================
            # 13. 验证目标自动完成
            # ==================================
            #
            # 后端逻辑：
            #
            # SavingsGoal.Status.COMPLETED
            #
            # 当前按 completed 枚举值断言。
            #
            # ==================================

            actual_status = after_data.get("status")

            assert actual_status == "completed", (
                f"存入金额已达到目标金额，"
                f"但是目标没有自动完成，"
                f"expected=completed，"
                f"actual={actual_status}，"
                f"detail={after_data}"
            )

            # ==================================
            # 14. 查询存入后流水
            # ==================================

            records_response = saving_api.get_records(saving_id)

            assert records_response.status_code == 200, (
                f"查询存入后流水失败：" f"{records_response.text}"
            )

            records_result = records_response.json()

            assert records_result.get("code") == 200, (
                f"查询存入后流水业务失败：" f"{records_result}"
            )

            records = records_result.get(
                "data",
                [],
            )

            if isinstance(records, dict):
                records = records.get(
                    "results",
                    records.get("records", []),
                )

            assert isinstance(records, list), (
                f"存入后流水结构错误：" f"{records_result}"
            )

            # ==================================
            # 15. 查找新增流水
            # ==================================

            new_records = [
                record
                for record in records
                if record.get("id") not in before_record_ids
            ]

            assert len(new_records) == 1, (
                f"存入一次资金应新增一条流水，"
                f"actual={len(new_records)}，"
                f"records={records}"
            )

            record = new_records[0]

            # ==================================
            # 16. 验证流水金额
            # ==================================

            assert Decimal(str(record["amount"])) == deposit_amount, (
                f"存入流水金额错误：" f"{record}"
            )

            # ==================================
            # 17. 验证变动前金额
            # ==================================

            assert Decimal(str(record["before_amount"])) == before_amount, (
                f"存入流水变动前金额错误：" f"{record}"
            )

            # ==================================
            # 18. 验证变动后金额
            # ==================================

            assert Decimal(str(record["after_amount"])) == expected_amount, (
                f"存入流水变动后金额错误：" f"{record}"
            )

            # ==================================
            # 19. 验证流水备注
            # ==================================

            assert record.get("note") == deposit_payload["note"], (
                f"存入流水备注错误：" f"{record}"
            )

            # ==================================
            # 20. 输出关键结果
            # ==================================

            print("储蓄目标 ID：", saving_id)
            print("存入前金额：", before_amount)
            print("本次存入金额：", deposit_amount)
            print("存入后金额：", after_amount)
            print("完成状态：", actual_status)
            print("新增储蓄流水：", record)

        finally:
            # ==================================
            # 21. 清理测试数据
            # ==================================

            if saving_id:

                try:
                    delete_response = saving_api.delete_saving(saving_id)

                    if delete_response.status_code != 200:
                        print(
                            f"储蓄目标清理失败，"
                            f"saving_id={saving_id}，"
                            f"status_code={delete_response.status_code}，"
                            f"response={delete_response.text}"
                        )

                except Exception as error:
                    print(
                        f"储蓄目标清理异常，"
                        f"saving_id={saving_id}，"
                        f"error={error}"
                    )

    @allure.story("储蓄资金管理")
    @allure.title("已完成储蓄目标再次存入资金失败")
    def test_deposit_to_completed_saving_failed(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证已完成的储蓄目标不能再次存入资金。

        后端业务规则：

            if goal.status == SavingsGoal.Status.COMPLETED:
                raise BusinessException(
                    "储蓄目标已完成，无法继续存入资金"
                )

        测试场景：

            目标金额：1000.00
            初始已存：0.00
            第一次存入：1000.00
            第一次存入后状态：completed

            第二次存入：200.00
            预期：拒绝存入

        测试流程：

        1. 创建储蓄目标；
        2. 第一次存入资金，使目标达到完成状态；
        3. 验证目标状态为 completed；
        4. 查询第一次存入后的流水；
        5. 对已完成目标再次存入资金；
        6. 验证 HTTP 状态码为 400；
        7. 验证业务状态码为 400；
        8. 验证错误信息；
        9. 验证已存金额没有变化；
        10. 验证目标状态没有变化；
        11. 验证没有新增资金流水；
        12. 清理测试数据。
        """

        # ======================================
        # 初始化测试变量
        # ======================================

        saving_id = None

        # 目标金额。
        target_amount = Decimal("1000.00")

        # 第一次存入金额。
        first_deposit_amount = Decimal("1000.00")

        # 第二次尝试存入金额。
        second_deposit_amount = Decimal("200.00")

        try:
            # ==================================
            # 1. 创建测试储蓄目标
            # ==================================

            create_payload = saving_factory.build_saving(
                target_amount=str(target_amount),
                current_amount="0.00",
                deadline="2027-12-31",
            )

            create_response = saving_api.create_saving(create_payload)

            # ==================================
            # 创建接口断言
            # ==================================

            assert create_response.status_code == 200, (
                f"创建储蓄目标失败，" f"response={create_response.text}"
            )

            create_result = create_response.json()

            assert create_result.get("code") == 200, (
                f"创建储蓄目标业务失败：" f"{create_result}"
            )

            create_data = create_result.get("data")

            assert isinstance(create_data, dict), (
                f"创建目标返回数据结构错误：" f"{create_result}"
            )

            saving_id = create_data.get("id")

            assert saving_id, f"创建储蓄目标后未返回 ID：" f"{create_result}"

            # ==================================
            # 2. 第一次存入资金
            # ==================================
            #
            # 初始金额：
            #
            # 0.00
            #
            # 存入：
            #
            # 1000.00
            #
            # 预期：
            #
            # current_amount = 1000.00
            # status = completed
            #
            # ==================================

            first_deposit_payload = {
                "amount": str(first_deposit_amount),
                "note": "自动化测试-首次存入达到目标",
            }

            first_response = saving_api.deposit(
                saving_id,
                first_deposit_payload,
            )

            # ==================================
            # 第一次存入必须成功
            # ==================================

            assert first_response.status_code == 200, (
                f"首次存入资金失败，"
                f"status_code={first_response.status_code}，"
                f"response={first_response.text}"
            )

            first_result = first_response.json()

            assert first_result.get("code") == 200, (
                f"首次存入资金业务失败：" f"{first_result}"
            )

            # ==================================
            # 3. 查询第一次存入后的详情
            # ==================================

            completed_response = saving_api.get_saving_detail(saving_id)

            assert completed_response.status_code == 200, (
                f"查询已完成储蓄目标失败：" f"{completed_response.text}"
            )

            completed_result = completed_response.json()

            assert completed_result.get("code") == 200

            completed_data = completed_result.get("data")

            assert isinstance(completed_data, dict)

            # ==================================
            # 4. 验证目标已完成
            # ==================================

            assert completed_data.get("status") == "completed", (
                f"第一次存入达到目标金额后，"
                f"储蓄目标没有自动完成："
                f"{completed_data}"
            )

            # ==================================
            # 5. 保存第二次存入前的金额
            # ==================================

            before_amount = Decimal(str(completed_data["current_amount"]))

            assert before_amount == target_amount, (
                f"第一次存入后金额错误，"
                f"expected={target_amount}，"
                f"actual={before_amount}"
            )

            # ==================================
            # 6. 查询第二次存入前的流水
            # ==================================

            before_records_response = saving_api.get_records(saving_id)

            assert before_records_response.status_code == 200, (
                f"查询存入前流水失败：" f"{before_records_response.text}"
            )

            before_records_result = before_records_response.json()

            assert before_records_result.get("code") == 200

            before_records = before_records_result.get(
                "data",
                [],
            )

            # ==================================
            # 兼容分页格式
            # ==================================

            if isinstance(before_records, dict):
                before_records = before_records.get(
                    "results",
                    before_records.get("records", []),
                )

            assert isinstance(before_records, list), (
                f"存入前流水数据结构错误：" f"{before_records_result}"
            )

            # ==================================
            # 第一次存入应该产生一条流水
            # ==================================

            assert len(before_records) == 1, (
                f"首次存入应产生一条流水，"
                f"actual={len(before_records)}，"
                f"records={before_records}"
            )

            # ==================================
            # 保存第一次存入的流水 ID
            # ==================================

            before_record_ids = {record["id"] for record in before_records}

            # ==================================
            # 7. 第二次尝试存入资金
            # ==================================
            #
            # 此时目标状态已经是 completed。
            #
            # 本次存入金额本身合法：
            #
            # amount = 200.00
            #
            # 但业务状态不允许继续存入。
            #
            # ==================================

            second_deposit_payload = {
                "amount": str(second_deposit_amount),
                "note": "自动化测试-已完成目标再次存入",
            }

            second_response = saving_api.deposit(
                saving_id,
                second_deposit_payload,
            )

            # ==================================
            # 8. 验证 HTTP 状态码
            # ==================================
            #
            # 根据项目 BusinessException
            # 统一异常响应，预期返回 400。
            #
            # ==================================

            assert second_response.status_code == 400, (
                f"已完成储蓄目标再次存入资金"
                f"未按预期失败，"
                f"status_code={second_response.status_code}，"
                f"response={second_response.text}"
            )

            # ==================================
            # 9. 验证业务状态码
            # ==================================

            second_result = second_response.json()

            assert second_result.get("code") == 400, (
                f"已完成目标再次存入资金" f"业务状态码错误：" f"{second_result}"
            )

            # ==================================
            # 10. 验证错误信息
            # ==================================
            #
            # 后端明确抛出：
            #
            # 储蓄目标已完成，无法继续存入资金
            #
            # ==================================

            message = second_result.get(
                "message",
                "",
            )

            assert "储蓄目标已完成" in message, (
                f"已完成目标再次存入的" f"错误提示不正确：" f"{message}"
            )

            # ==================================
            # 11. 失败后重新查询目标详情
            # ==================================

            after_response = saving_api.get_saving_detail(saving_id)

            assert after_response.status_code == 200, (
                f"第二次存入失败后查询详情失败：" f"{after_response.text}"
            )

            after_result = after_response.json()

            assert after_result.get("code") == 200

            after_data = after_result.get("data")

            assert isinstance(after_data, dict)

            # ==================================
            # 12. 验证已存金额没有变化
            # ==================================
            #
            # 第二次存入失败，
            # current_amount 必须保持原值。
            #
            # 不能错误增加 200.00。
            #
            # ==================================

            after_amount = Decimal(str(after_data["current_amount"]))

            assert after_amount == before_amount, (
                f"已完成目标存入失败后金额发生变化，"
                f"before={before_amount}，"
                f"attempt={second_deposit_amount}，"
                f"after={after_amount}"
            )

            # ==================================
            # 13. 验证目标状态没有变化
            # ==================================

            assert after_data.get("status") == "completed", (
                f"已完成目标再次存入失败后" f"状态发生变化：" f"{after_data}"
            )

            # ==================================
            # 14. 验证目标金额没有变化
            # ==================================

            actual_target_amount = Decimal(str(after_data["target_amount"]))

            assert actual_target_amount == target_amount, (
                f"失败存入后目标金额发生变化，"
                f"expected={target_amount}，"
                f"actual={actual_target_amount}"
            )

            # ==================================
            # 15. 查询第二次存入后的流水
            # ==================================

            after_records_response = saving_api.get_records(saving_id)

            assert after_records_response.status_code == 200, (
                f"查询第二次存入后的流水失败：" f"{after_records_response.text}"
            )

            after_records_result = after_records_response.json()

            assert after_records_result.get("code") == 200

            after_records = after_records_result.get(
                "data",
                [],
            )

            if isinstance(after_records, dict):
                after_records = after_records.get(
                    "results",
                    after_records.get("records", []),
                )

            assert isinstance(after_records, list), (
                f"存入后流水结构错误：" f"{after_records_result}"
            )

            # ==================================
            # 16. 验证流水数量没有增加
            # ==================================
            #
            # 失败的存入请求不能生成流水。
            #
            # ==================================

            assert len(after_records) == len(before_records), (
                f"已完成目标存入失败后"
                f"流水数量发生变化，"
                f"before={len(before_records)}，"
                f"after={len(after_records)}"
            )

            # ==================================
            # 17. 验证流水 ID 没有增加
            # ==================================

            after_record_ids = {record["id"] for record in after_records}

            assert after_record_ids == before_record_ids, (
                f"已完成目标存入失败后"
                f"产生了额外流水，"
                f"before={before_record_ids}，"
                f"after={after_record_ids}"
            )

            # ==================================
            # 输出关键验证结果
            # ==================================

            print("储蓄目标 ID：", saving_id)
            print("储蓄目标状态：", after_data.get("status"))
            print("第二次存入金额：", second_deposit_amount)
            print("第二次存入响应：", second_result)
            print("存入前金额：", before_amount)
            print("存入后金额：", after_amount)
            print("存入前流水数：", len(before_records))
            print("存入后流水数：", len(after_records))

        finally:
            # ==================================
            # 18. 清理测试储蓄目标
            # ======================================
            #
            # 无论哪一个断言失败，
            # 都尽量清理本次创建的测试数据。
            #
            # ==================================

            if saving_id:

                try:
                    delete_response = saving_api.delete_saving(saving_id)

                    if delete_response.status_code != 200:
                        print(
                            f"储蓄目标清理失败，"
                            f"saving_id={saving_id}，"
                            f"status_code={delete_response.status_code}，"
                            f"response={delete_response.text}"
                        )

                except Exception as error:
                    print(
                        f"储蓄目标清理发生异常，"
                        f"saving_id={saving_id}，"
                        f"error={error}"
                    )

    @allure.story("储蓄资金管理")
    @allure.title("已暂停储蓄目标不能存入资金")
    def test_deposit_to_paused_saving_failed(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证已暂停储蓄目标不能存入资金。

        后端业务规则：

            if goal.status == SavingsGoal.Status.PAUSED:
                raise BusinessException(
                    "储蓄目标已暂停，无法存入资金"
                )

        测试场景：

            目标金额：10000.00
            初始已存：0.00
            目标状态：paused
            尝试存入：200.00

        预期：

            1. 存入接口返回 400；
            2. 返回明确的业务错误；
            3. current_amount 不变；
            4. target_amount 不变；
            5. status 保持 paused；
            6. 不产生新的储蓄流水。

        测试完成后清理储蓄目标。
        """

        # ======================================
        # 初始化测试变量
        # ======================================

        saving_id = None

        target_amount = Decimal("10000.00")
        deposit_amount = Decimal("200.00")

        try:
            # ==================================
            # 1. 创建储蓄目标
            # ==================================

            with allure.step("创建测试储蓄目标"):

                create_payload = saving_factory.build_saving(
                    target_amount=str(target_amount),
                    current_amount="0.00",
                    deadline="2027-12-31",
                )

                create_response = saving_api.create_saving(create_payload)

                assert create_response.status_code == 200, (
                    f"创建储蓄目标失败：" f"{create_response.text}"
                )

                create_result = create_response.json()

                assert create_result.get("code") == 200, (
                    f"创建储蓄目标业务失败：" f"{create_result}"
                )

                create_data = create_result.get("data")

                assert isinstance(create_data, dict), (
                    f"创建储蓄目标返回结构错误：" f"{create_result}"
                )

                saving_id = create_data.get("id")

                assert saving_id, f"创建储蓄目标后未返回 ID：" f"{create_result}"

            # ==================================
            # 2. 暂停储蓄目标
            # ==================================

            with allure.step("暂停储蓄目标"):

                pause_response = saving_api.pause(saving_id)

                assert pause_response.status_code == 200, (
                    f"暂停储蓄目标失败，"
                    f"status_code={pause_response.status_code}，"
                    f"response={pause_response.text}"
                )

                pause_result = pause_response.json()

                assert pause_result.get("code") == 200, (
                    f"暂停储蓄目标业务失败：" f"{pause_result}"
                )

            # ==================================
            # 3. 查询暂停后的目标详情
            # ==================================

            with allure.step("验证储蓄目标已暂停"):

                before_response = saving_api.get_saving_detail(saving_id)

                assert before_response.status_code == 200, (
                    f"查询暂停后储蓄目标失败：" f"{before_response.text}"
                )

                before_result = before_response.json()

                assert before_result.get("code") == 200

                before_data = before_result.get("data")

                assert isinstance(before_data, dict)

                # ==================================
                # 验证目标 ID
                # ==================================

                assert before_data.get("id") == saving_id

                # ==================================
                # 验证目标状态
                # ==================================
                #
                # 当前按照 paused 枚举值断言。
                # ==================================

                assert before_data.get("status") == "paused", (
                    f"暂停操作后目标状态错误：" f"{before_data}"
                )

                # ==================================
                # 保存存入前的金额
                # ==================================

                before_amount = Decimal(str(before_data["current_amount"]))

                assert before_amount == Decimal("0.00"), (
                    f"初始储蓄金额错误：" f"{before_amount}"
                )

            # ==================================
            # 4. 查询存入前资金流水
            # ==================================

            with allure.step("记录存入前的资金流水"):

                before_records_response = saving_api.get_records(saving_id)

                assert before_records_response.status_code == 200, (
                    f"查询存入前流水失败：" f"{before_records_response.text}"
                )

                before_records_result = before_records_response.json()

                assert before_records_result.get("code") == 200

                before_records = before_records_result.get(
                    "data",
                    [],
                )

                # ==================================
                # 兼容常见分页结构
                # ==================================

                if isinstance(before_records, dict):
                    before_records = before_records.get(
                        "results",
                        before_records.get("records", []),
                    )

                assert isinstance(before_records, list), (
                    f"存入前流水结构错误：" f"{before_records_result}"
                )

                # ==================================
                # 保存已有流水 ID
                # ==================================

                before_record_ids = {record["id"] for record in before_records}

            # ==================================
            # 5. 已暂停目标尝试存入资金
            # ==================================

            with allure.step("已暂停目标尝试存入200元"):

                deposit_payload = {
                    "amount": str(deposit_amount),
                    "note": "自动化测试-暂停目标存入资金",
                }

                deposit_response = saving_api.deposit(
                    saving_id,
                    deposit_payload,
                )

                # ==================================
                # HTTP 状态码断言
                # ==================================

                assert deposit_response.status_code == 400, (
                    f"已暂停储蓄目标存入资金未按预期失败，"
                    f"status_code={deposit_response.status_code}，"
                    f"response={deposit_response.text}"
                )

                # ==================================
                # 业务状态码断言
                # ==================================

                deposit_result = deposit_response.json()

                assert deposit_result.get("code") == 400, (
                    f"已暂停目标存入资金业务状态错误：" f"{deposit_result}"
                )

                # ==================================
                # 错误信息断言
                # ==================================

                message = deposit_result.get(
                    "message",
                    "",
                )

                assert "储蓄目标已暂停" in message, (
                    f"已暂停目标存入资金错误提示不正确：" f"{message}"
                )

                # ==================================
                # 失败响应不应返回有效存入结果
                # ==================================

                error_data = deposit_result.get("data")

                assert error_data is None or not error_data, (
                    f"暂停状态存入失败却返回有效数据：" f"{deposit_result}"
                )

            # ==================================
            # 6. 存入失败后重新查询详情
            # ==================================

            with allure.step("验证存入失败后金额与状态不变"):

                after_response = saving_api.get_saving_detail(saving_id)

                assert after_response.status_code == 200, (
                    f"存入失败后查询储蓄目标失败：" f"{after_response.text}"
                )

                after_result = after_response.json()

                assert after_result.get("code") == 200

                after_data = after_result.get("data")

                assert isinstance(after_data, dict)

                # ==================================
                # 目标 ID 不变
                # ==================================

                assert after_data.get("id") == saving_id

                # ==================================
                # 已存金额不能发生变化
                # ==================================
                #
                # 暂停状态下存入失败。
                #
                # 因此：
                #
                # after_amount == before_amount
                #
                # ==================================

                after_amount = Decimal(str(after_data["current_amount"]))

                assert after_amount == before_amount, (
                    f"暂停目标存入失败后金额发生变化，"
                    f"before={before_amount}，"
                    f"attempt={deposit_amount}，"
                    f"after={after_amount}"
                )

                # ==================================
                # 目标金额不变
                # ==================================

                actual_target_amount = Decimal(str(after_data["target_amount"]))

                assert actual_target_amount == target_amount, (
                    f"存入失败后目标金额发生变化，"
                    f"expected={target_amount}，"
                    f"actual={actual_target_amount}"
                )

                # ==================================
                # 目标必须仍处于暂停状态
                # ==================================

                assert after_data.get("status") == "paused", (
                    f"暂停目标存入失败后状态发生变化：" f"{after_data}"
                )

            # ==================================
            # 7. 存入失败后查询资金流水
            # ==================================

            with allure.step("验证存入失败不产生资金流水"):

                after_records_response = saving_api.get_records(saving_id)

                assert after_records_response.status_code == 200, (
                    f"查询存入失败后的流水失败：" f"{after_records_response.text}"
                )

                after_records_result = after_records_response.json()

                assert after_records_result.get("code") == 200

                after_records = after_records_result.get(
                    "data",
                    [],
                )

                if isinstance(after_records, dict):
                    after_records = after_records.get(
                        "results",
                        after_records.get("records", []),
                    )

                assert isinstance(after_records, list), (
                    f"存入失败后的流水结构错误：" f"{after_records_result}"
                )

                # ==================================
                # 流水数量不能增加
                # ==================================

                assert len(after_records) == len(before_records), (
                    f"暂停目标存入失败后流水数量发生变化，"
                    f"before={len(before_records)}，"
                    f"after={len(after_records)}"
                )

                # ==================================
                # 流水 ID 集合必须保持一致
                # ==================================

                after_record_ids = {record["id"] for record in after_records}

                assert after_record_ids == before_record_ids, (
                    f"暂停目标存入失败后产生额外流水，"
                    f"before={before_record_ids}，"
                    f"after={after_record_ids}"
                )

            # ==================================
            # 8. 输出验证结果
            # ==================================

            print("储蓄目标 ID：", saving_id)
            print("存入请求金额：", deposit_amount)
            print("存入接口响应：", deposit_result)
            print("存入前金额：", before_amount)
            print("存入后金额：", after_amount)
            print("储蓄目标状态：", after_data.get("status"))
            print("存入前流水数量：", len(before_records))
            print("存入后流水数量：", len(after_records))

        finally:
            # ==================================
            # 9. 清理测试数据
            # ======================================
            #
            # 即使中途出现断言失败，
            # 也尝试删除本次创建的目标。
            #
            # ==================================

            if saving_id:

                try:
                    delete_response = saving_api.delete_saving(saving_id)

                    if delete_response.status_code != 200:
                        print(
                            f"暂停储蓄目标测试数据清理失败，"
                            f"saving_id={saving_id}，"
                            f"status_code={delete_response.status_code}，"
                            f"response={delete_response.text}"
                        )

                except Exception as error:
                    print(
                        f"暂停储蓄目标清理发生异常，"
                        f"saving_id={saving_id}，"
                        f"error={error}"
                    )

    @allure.story("储蓄目标状态管理")
    @allure.title("恢复储蓄目标成功并可以正常存入资金")
    def test_resume_saving_and_deposit_success(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证暂停的储蓄目标恢复后可以正常存入资金。

        测试流程：

        1. 创建储蓄目标；
        2. 查询并保存初始状态和金额；
        3. 暂停储蓄目标；
        4. 验证状态为 paused；
        5. 恢复储蓄目标；
        6. 验证状态恢复正常；
        7. 查询存入前资金流水；
        8. 存入 300.00；
        9. 验证存入接口成功；
        10. 验证 current_amount 增加；
        11. 验证目标金额保持不变；
        12. 验证新增一条存入流水；
        13. 验证流水金额与前后余额；
        14. 清理测试数据。
        """

        # ======================================
        # 初始化测试变量
        # ======================================

        saving_id = None

        target_amount = Decimal("10000.00")
        deposit_amount = Decimal("300.00")

        try:
            # ==================================
            # 1. 创建储蓄目标
            # ==================================

            with allure.step("创建测试储蓄目标"):

                create_payload = saving_factory.build_saving(
                    target_amount=str(target_amount),
                    current_amount="0.00",
                    deadline="2027-12-31",
                )

                create_response = saving_api.create_saving(create_payload)

                assert create_response.status_code == 200, (
                    f"创建储蓄目标失败：" f"{create_response.text}"
                )

                create_result = create_response.json()

                assert create_result.get("code") == 200, (
                    f"创建储蓄目标业务失败：" f"{create_result}"
                )

                create_data = create_result.get("data")

                assert isinstance(create_data, dict), (
                    f"创建响应结构错误：" f"{create_result}"
                )

                saving_id = create_data.get("id")

                assert saving_id, f"创建储蓄目标未返回 ID：" f"{create_result}"

            # ==================================
            # 2. 查询初始状态
            # ======================================

            with allure.step("查询储蓄目标初始状态"):

                initial_response = saving_api.get_saving_detail(saving_id)

                assert initial_response.status_code == 200, (
                    f"查询初始详情失败：" f"{initial_response.text}"
                )

                initial_result = initial_response.json()

                assert initial_result.get("code") == 200

                initial_data = initial_result.get("data")

                assert isinstance(initial_data, dict)

                # 保存创建时的正常状态。
                initial_status = initial_data.get("status")

                assert initial_status, f"未获取到储蓄目标状态：" f"{initial_data}"

                assert initial_status not in (
                    "paused",
                    "completed",
                ), (
                    f"新创建的储蓄目标状态异常：" f"{initial_status}"
                )

                # 保存初始金额。
                initial_amount = Decimal(str(initial_data["current_amount"]))

                assert initial_amount == Decimal("0.00"), (
                    f"储蓄目标初始金额错误：" f"{initial_amount}"
                )

            # ==================================
            # 3. 暂停储蓄目标
            # ==================================

            with allure.step("暂停储蓄目标"):

                pause_response = saving_api.pause(saving_id)

                assert pause_response.status_code == 200, (
                    f"暂停储蓄目标失败：" f"{pause_response.text}"
                )

                pause_result = pause_response.json()

                assert pause_result.get("code") == 200, (
                    f"暂停储蓄目标业务失败：" f"{pause_result}"
                )

            # ==================================
            # 4. 验证暂停状态
            # ==================================

            with allure.step("验证储蓄目标处于暂停状态"):

                paused_response = saving_api.get_saving_detail(saving_id)

                assert paused_response.status_code == 200, (
                    f"查询暂停状态失败：" f"{paused_response.text}"
                )

                paused_result = paused_response.json()

                assert paused_result.get("code") == 200

                paused_data = paused_result.get("data")

                assert isinstance(paused_data, dict)

                # 暂停后状态必须为 paused。
                assert paused_data.get("status") == "paused", (
                    f"暂停后的状态错误：" f"{paused_data}"
                )

                # 暂停操作不能改变已存金额。
                paused_amount = Decimal(str(paused_data["current_amount"]))

                assert paused_amount == initial_amount, (
                    f"暂停操作导致已存金额变化，"
                    f"before={initial_amount}，"
                    f"after={paused_amount}"
                )

            # ==================================
            # 5. 恢复储蓄目标
            # ==================================

            with allure.step("恢复已暂停的储蓄目标"):

                resume_response = saving_api.resume(saving_id)

                assert resume_response.status_code == 200, (
                    f"恢复储蓄目标失败，"
                    f"status_code={resume_response.status_code}，"
                    f"response={resume_response.text}"
                )

                resume_result = resume_response.json()

                assert resume_result.get("code") == 200, (
                    f"恢复储蓄目标业务失败：" f"{resume_result}"
                )

            # ==================================
            # 6. 验证恢复后的状态
            # ==================================

            with allure.step("验证储蓄目标恢复正常"):

                resumed_response = saving_api.get_saving_detail(saving_id)

                assert resumed_response.status_code == 200, (
                    f"恢复后查询详情失败：" f"{resumed_response.text}"
                )

                resumed_result = resumed_response.json()

                assert resumed_result.get("code") == 200

                resumed_data = resumed_result.get("data")

                assert isinstance(resumed_data, dict)

                # ==================================
                # 验证状态恢复到初始正常状态
                # ==================================

                resumed_status = resumed_data.get("status")

                assert resumed_status == initial_status, (
                    f"储蓄目标恢复后的状态不正确，"
                    f"expected={initial_status}，"
                    f"actual={resumed_status}"
                )

                # ==================================
                # 恢复操作不能改变资金
                # ==================================

                before_deposit_amount = Decimal(str(resumed_data["current_amount"]))

                assert before_deposit_amount == initial_amount, (
                    f"恢复操作导致已存金额变化，"
                    f"expected={initial_amount}，"
                    f"actual={before_deposit_amount}"
                )

            # ==================================
            # 7. 查询存入前流水
            # ==================================

            with allure.step("记录存入前的储蓄流水"):

                before_records_response = saving_api.get_records(saving_id)

                assert before_records_response.status_code == 200, (
                    f"查询存入前流水失败：" f"{before_records_response.text}"
                )

                before_records_result = before_records_response.json()

                assert before_records_result.get("code") == 200

                before_records = before_records_result.get(
                    "data",
                    [],
                )

                # 兼容常见分页结构。
                if isinstance(before_records, dict):
                    before_records = before_records.get(
                        "results",
                        before_records.get("records", []),
                    )

                assert isinstance(before_records, list), (
                    f"存入前流水结构错误：" f"{before_records_result}"
                )

                # 保存现有流水 ID。
                before_record_ids = {record["id"] for record in before_records}

            # ==================================
            # 8. 恢复后存入资金
            # ==================================

            with allure.step("恢复后存入300元"):

                deposit_payload = {
                    "amount": str(deposit_amount),
                    "note": "自动化测试-恢复后存入资金",
                }

                deposit_response = saving_api.deposit(
                    saving_id,
                    deposit_payload,
                )

                # HTTP 状态码断言。
                assert deposit_response.status_code == 200, (
                    f"恢复后存入资金失败，"
                    f"status_code={deposit_response.status_code}，"
                    f"response={deposit_response.text}"
                )

                # 业务状态码断言。
                deposit_result = deposit_response.json()

                assert deposit_result.get("code") == 200, (
                    f"恢复后存入资金业务失败：" f"{deposit_result}"
                )

            # ==================================
            # 9. 查询存入后的储蓄目标
            # ==================================

            with allure.step("验证恢复后存入资金的金额变化"):

                after_response = saving_api.get_saving_detail(saving_id)

                assert after_response.status_code == 200, (
                    f"存入后查询详情失败：" f"{after_response.text}"
                )

                after_result = after_response.json()

                assert after_result.get("code") == 200

                after_data = after_result.get("data")

                assert isinstance(after_data, dict)

                # ==================================
                # 目标 ID 不能变化
                # ==================================

                assert after_data.get("id") == saving_id

                # ==================================
                # 验证 current_amount
                # ==================================
                #
                # 预期：
                #
                # 0.00 + 300.00 = 300.00
                #
                # ==================================

                after_amount = Decimal(str(after_data["current_amount"]))

                expected_amount = before_deposit_amount + deposit_amount

                assert after_amount == expected_amount, (
                    f"恢复后存入资金金额错误，"
                    f"before={before_deposit_amount}，"
                    f"deposit={deposit_amount}，"
                    f"expected={expected_amount}，"
                    f"actual={after_amount}"
                )

                # ==================================
                # 目标金额保持不变
                # ==================================

                actual_target_amount = Decimal(str(after_data["target_amount"]))

                assert actual_target_amount == target_amount, (
                    f"存入资金后目标金额发生变化，"
                    f"expected={target_amount}，"
                    f"actual={actual_target_amount}"
                )

                # ==================================
                # 未达到目标，不应自动完成
                # ==================================

                assert after_amount < target_amount

                assert after_data.get("status") == initial_status, (
                    f"恢复后正常存入资金导致状态异常，"
                    f"expected={initial_status}，"
                    f"actual={after_data.get('status')}"
                )

            # ==================================
            # 10. 查询存入后的资金流水
            # ==================================

            with allure.step("验证恢复后存入产生资金流水"):

                records_response = saving_api.get_records(saving_id)

                assert records_response.status_code == 200, (
                    f"查询存入后流水失败：" f"{records_response.text}"
                )

                records_result = records_response.json()

                assert records_result.get("code") == 200

                records = records_result.get(
                    "data",
                    [],
                )

                if isinstance(records, dict):
                    records = records.get(
                        "results",
                        records.get("records", []),
                    )

                assert isinstance(records, list), (
                    f"存入后流水结构错误：" f"{records_result}"
                )

                # ==================================
                # 查找新增的流水
                # ==================================

                new_records = [
                    record
                    for record in records
                    if record.get("id") not in before_record_ids
                ]

                # ==================================
                # 必须只新增一条
                # ==================================

                assert len(new_records) == 1, (
                    f"恢复后存入一次资金应产生一条流水，"
                    f"actual={len(new_records)}，"
                    f"records={records}"
                )

                record = new_records[0]

                # ==================================
                # 验证流水金额
                # ==================================

                assert Decimal(str(record["amount"])) == deposit_amount, (
                    f"存入流水金额错误：" f"{record}"
                )

                # ==================================
                # 验证变动前金额
                # ==================================

                assert Decimal(str(record["before_amount"])) == before_deposit_amount, (
                    f"流水变动前金额错误：" f"{record}"
                )

                # ==================================
                # 验证变动后金额
                # ==================================

                assert Decimal(str(record["after_amount"])) == expected_amount, (
                    f"流水变动后金额错误：" f"{record}"
                )

                # ==================================
                # 验证流水备注
                # ==================================

                assert record.get("note") == deposit_payload["note"], (
                    f"存入流水备注错误：" f"{record}"
                )

            # ==================================
            # 11. 输出关键测试结果
            # ==================================

            print("储蓄目标 ID：", saving_id)
            print("创建时状态：", initial_status)
            print("暂停后状态：", paused_data.get("status"))
            print("恢复后状态：", resumed_status)
            print("存入金额：", deposit_amount)
            print("存入前金额：", before_deposit_amount)
            print("存入后金额：", after_amount)
            print("新增储蓄流水：", record)

        finally:
            # ==================================
            # 12. 清理测试数据
            # ==================================
            #
            # 无论测试是否通过，
            # 都尝试删除本次创建的储蓄目标。
            #
            # ==================================

            if saving_id:

                try:
                    delete_response = saving_api.delete_saving(saving_id)

                    if delete_response.status_code != 200:
                        print(
                            f"储蓄目标测试数据清理失败，"
                            f"saving_id={saving_id}，"
                            f"status_code={delete_response.status_code}，"
                            f"response={delete_response.text}"
                        )

                except Exception as error:
                    print(
                        f"储蓄目标清理发生异常，"
                        f"saving_id={saving_id}，"
                        f"error={error}"
                    )

    @allure.story("储蓄资金管理")
    @allure.title("储蓄目标取出资金成功")
    def test_withdraw_saving_success(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证储蓄目标取出资金成功。

        后端业务规则：

        1. 只能操作当前用户的目标；
        2. 已删除目标不能操作；
        3. 已暂停目标不能取出；
        4. 取出金额不能超过当前余额；
        5. 使用 select_for_update 保证并发安全；
        6. 余额和资金流水在同一事务中更新。

        当前测试数据：

            目标金额：10000.00
            初始已存：0.00
            先存入：800.00
            再取出：300.00
            最终已存：500.00

        测试流程：

        1. 创建储蓄目标；
        2. 存入 800.00；
        3. 查询取出前详情；
        4. 记录取出前流水；
        5. 取出 300.00；
        6. 验证取出接口成功；
        7. 查询取出后详情；
        8. 验证已存金额减少；
        9. 验证目标金额与状态保持不变；
        10. 查询取出后流水；
        11. 验证新增一条取出流水；
        12. 验证流水金额与前后余额；
        13. 验证流水备注；
        14. 清理测试数据。
        """

        # ======================================
        # 初始化变量
        # ======================================

        saving_id = None

        target_amount = Decimal("10000.00")
        deposit_amount = Decimal("800.00")
        withdraw_amount = Decimal("300.00")

        try:
            # ==================================
            # 1. 创建储蓄目标
            # ==================================

            with allure.step("创建测试储蓄目标"):

                create_payload = saving_factory.build_saving(
                    target_amount=str(target_amount),
                    current_amount="0.00",
                    deadline="2027-12-31",
                )

                create_response = saving_api.create_saving(create_payload)

                assert create_response.status_code == 200, (
                    f"创建储蓄目标失败：" f"{create_response.text}"
                )

                create_result = create_response.json()

                assert create_result.get("code") == 200, (
                    f"创建储蓄目标业务失败：" f"{create_result}"
                )

                create_data = create_result.get("data")

                assert isinstance(create_data, dict), (
                    f"创建储蓄目标返回结构错误：" f"{create_result}"
                )

                saving_id = create_data.get("id")

                assert saving_id, f"创建目标后未返回 ID：" f"{create_result}"

            # ==================================
            # 2. 先存入 800.00
            # ======================================

            with allure.step("向储蓄目标存入800元"):

                deposit_payload = {
                    "amount": str(deposit_amount),
                    "note": "自动化测试-取出前存入资金",
                }

                deposit_response = saving_api.deposit(
                    saving_id,
                    deposit_payload,
                )

                assert deposit_response.status_code == 200, (
                    f"存入资金失败：" f"{deposit_response.text}"
                )

                deposit_result = deposit_response.json()

                assert deposit_result.get("code") == 200, (
                    f"存入资金业务失败：" f"{deposit_result}"
                )

            # ==================================
            # 3. 查询取出前的储蓄目标详情
            # ==================================

            with allure.step("验证取出前已存金额为800元"):

                before_response = saving_api.get_saving_detail(saving_id)

                assert before_response.status_code == 200, (
                    f"查询取出前详情失败：" f"{before_response.text}"
                )

                before_result = before_response.json()

                assert before_result.get("code") == 200

                before_data = before_result.get("data")

                assert isinstance(before_data, dict)

                # ==================================
                # 验证目标 ID
                # ==================================

                assert before_data.get("id") == saving_id

                # ==================================
                # 获取取出前的当前余额
                # ==================================

                before_amount = Decimal(str(before_data["current_amount"]))

                assert before_amount == deposit_amount, (
                    f"取出前已存金额错误，"
                    f"expected={deposit_amount}，"
                    f"actual={before_amount}"
                )

                # ==================================
                # 保存取出前状态
                # ==================================
                #
                # 本次取出前没有达到目标金额，
                # 因此取出后不应改变状态。
                #
                # ==================================

                before_status = before_data.get("status")

                assert before_status not in (
                    None,
                    "paused",
                    "completed",
                ), (
                    f"取出前目标状态异常：" f"{before_data}"
                )

                # ==================================
                # 验证目标金额
                # ==================================

                assert Decimal(str(before_data["target_amount"])) == target_amount, (
                    f"储蓄目标金额错误：" f"{before_data}"
                )

            # ==================================
            # 4. 查询取出前流水
            # ==================================

            with allure.step("记录取出前的资金流水"):

                before_records_response = saving_api.get_records(saving_id)

                assert before_records_response.status_code == 200, (
                    f"查询取出前流水失败：" f"{before_records_response.text}"
                )

                before_records_result = before_records_response.json()

                assert before_records_result.get("code") == 200

                before_records = before_records_result.get(
                    "data",
                    [],
                )

                # ==================================
                # 兼容现有流水列表结构
                # ==================================

                if isinstance(before_records, dict):
                    before_records = before_records.get(
                        "results",
                        before_records.get("records", []),
                    )

                assert isinstance(before_records, list), (
                    f"取出前流水结构错误：" f"{before_records_result}"
                )

                # ==================================
                # 先存入一次，应该有一条流水
                # ==================================

                assert len(before_records) == 1, (
                    f"取出前应有一条存入流水，"
                    f"actual={len(before_records)}，"
                    f"records={before_records}"
                )

                # ==================================
                # 记录存入流水信息
                # ==================================

                deposit_record = before_records[0]

                before_record_ids = {item["id"] for item in before_records}

            # ==================================
            # 5. 构造取出请求
            # ======================================
            #
            # 后端明确使用：
            #
            # amount：必填
            # note：可选
            #
            # ==================================

            withdraw_payload = {
                "amount": str(withdraw_amount),
                "note": "自动化测试-取出300元",
            }

            # ==================================
            # 6. 调用取出接口
            # ==================================

            with allure.step("从储蓄目标取出300元"):

                withdraw_response = saving_api.withdraw(
                    saving_id,
                    withdraw_payload,
                )

                # HTTP 状态码断言。
                assert withdraw_response.status_code == 200, (
                    f"取出储蓄资金失败，"
                    f"status_code={withdraw_response.status_code}，"
                    f"response={withdraw_response.text}"
                )

                # 业务状态码断言。
                withdraw_result = withdraw_response.json()

                assert withdraw_result.get("code") == 200, (
                    f"取出资金业务失败：" f"{withdraw_result}"
                )

            # ==================================
            # 7. 查询取出后详情
            # ==================================

            with allure.step("验证取出后的目标余额和状态"):

                after_response = saving_api.get_saving_detail(saving_id)

                assert after_response.status_code == 200, (
                    f"取出后查询详情失败：" f"{after_response.text}"
                )

                after_result = after_response.json()

                assert after_result.get("code") == 200

                after_data = after_result.get("data")

                assert isinstance(after_data, dict), (
                    f"取出后详情结构错误：" f"{after_result}"
                )

                # ==================================
                # 目标 ID 保持不变
                # ==================================

                assert after_data.get("id") == saving_id

                # ==================================
                # 8. 验证取出后的余额
                # ==================================
                #
                # 后端计算规则：
                #
                # after_amount
                # =
                # before_amount - withdraw_amount
                #
                # 800.00 - 300.00 = 500.00
                #
                # ==================================

                after_amount = Decimal(str(after_data["current_amount"]))

                expected_amount = before_amount - withdraw_amount

                assert after_amount == expected_amount, (
                    f"取出后金额错误，"
                    f"before={before_amount}，"
                    f"withdraw={withdraw_amount}，"
                    f"expected={expected_amount}，"
                    f"actual={after_amount}"
                )

                # ==================================
                # 9. 验证目标金额没有变化
                # ==================================

                actual_target_amount = Decimal(str(after_data["target_amount"]))

                assert actual_target_amount == target_amount, (
                    f"取出资金后目标金额发生变化，"
                    f"expected={target_amount}，"
                    f"actual={actual_target_amount}"
                )

                # ==================================
                # 10. 验证目标状态没有变化
                # ==================================
                #
                # 当前测试目标没有完成。
                #
                # 取出资金后，状态仍应保持原值。
                #
                # ==================================

                assert after_data.get("status") == before_status, (
                    f"取出资金后目标状态异常，"
                    f"before={before_status}，"
                    f"after={after_data.get('status')}"
                )

            # ==================================
            # 11. 查询取出后的储蓄流水
            # ==================================

            with allure.step("验证取出后新增一条资金流水"):

                records_response = saving_api.get_records(saving_id)

                assert records_response.status_code == 200, (
                    f"查询取出后流水失败：" f"{records_response.text}"
                )

                records_result = records_response.json()

                assert records_result.get("code") == 200

                records = records_result.get(
                    "data",
                    [],
                )

                if isinstance(records, dict):
                    records = records.get(
                        "results",
                        records.get("records", []),
                    )

                assert isinstance(records, list), (
                    f"取出后流水结构错误：" f"{records_result}"
                )

                # ==================================
                # 12. 验证流水数量增加一条
                # ==================================

                assert len(records) == len(before_records) + 1, (
                    f"取出一次资金应新增一条流水，"
                    f"before={len(before_records)}，"
                    f"after={len(records)}"
                )

                # ==================================
                # 13. 查找新增的取出流水
                # ==================================

                new_records = [
                    item for item in records if item.get("id") not in before_record_ids
                ]

                assert len(new_records) == 1, (
                    f"取出一次资金应新增一条流水，"
                    f"actual={len(new_records)}，"
                    f"records={records}"
                )

                withdraw_record = new_records[0]

                # ==================================
                # 14. 验证取出金额
                # ==================================

                assert Decimal(str(withdraw_record["amount"])) == withdraw_amount, (
                    f"取出流水金额错误：" f"{withdraw_record}"
                )

                # ==================================
                # 15. 验证变动前金额
                # ==================================

                assert (
                    Decimal(str(withdraw_record["before_amount"])) == before_amount
                ), (f"取出流水变动前金额错误：" f"{withdraw_record}")

                # ==================================
                # 16. 验证变动后金额
                # ==================================

                assert (
                    Decimal(str(withdraw_record["after_amount"])) == expected_amount
                ), (f"取出流水变动后金额错误：" f"{withdraw_record}")

                # ==================================
                # 17. 验证取出备注
                # ==================================

                assert withdraw_record.get("note") == (withdraw_payload["note"]), (
                    f"取出流水备注错误：" f"{withdraw_record}"
                )

                # ==================================
                # 18. 验证取出流水所属目标
                # ==================================

                if "goal_id" in withdraw_record:
                    assert int(withdraw_record["goal_id"]) == int(saving_id), (
                        f"流水所属储蓄目标错误：" f"{withdraw_record}"
                    )

                elif "goal" in withdraw_record:

                    record_goal = withdraw_record["goal"]

                    if isinstance(record_goal, dict):
                        record_goal = record_goal.get("id")

                    assert int(record_goal) == int(saving_id), (
                        f"流水所属储蓄目标错误：" f"{withdraw_record}"
                    )

                # ==================================
                # 19. 验证取出流水类型
                # ==================================
                #
                # 已确认后端存入和取出使用
                # 两个不同的 RecordType 枚举。
                #
                # 如果流水接口暴露 record_type，
                # 这里先校验存入和取出类型不同。
                #
                # 具体枚举值需要以 models.py 为准。
                #
                # ==================================

                if "record_type" in withdraw_record and "record_type" in deposit_record:
                    assert withdraw_record["record_type"] != (
                        deposit_record["record_type"]
                    ), (
                        f"存入和取出流水类型不应该相同，"
                        f"deposit={deposit_record}，"
                        f"withdraw={withdraw_record}"
                    )

            # ==================================
            # 20. 输出关键验证结果
            # ==================================

            print("储蓄目标 ID：", saving_id)
            print("目标金额：", target_amount)
            print("首次存入：", deposit_amount)
            print("本次取出：", withdraw_amount)
            print("取出前已存：", before_amount)
            print("取出后已存：", after_amount)
            print("取出后状态：", after_data.get("status"))
            print("存入流水：", deposit_record)
            print("取出流水：", withdraw_record)

        finally:
            # ==================================
            # 21. 清理测试数据
            # ==================================
            #
            # 无论测试中途是否失败，
            # 都尝试删除本次创建的储蓄目标。
            #
            # ==================================

            if saving_id:

                try:
                    delete_response = saving_api.delete_saving(saving_id)

                    if delete_response.status_code != 200:
                        print(
                            f"储蓄目标测试数据清理失败，"
                            f"saving_id={saving_id}，"
                            f"status_code={delete_response.status_code}，"
                            f"response={delete_response.text}"
                        )

                except Exception as error:
                    print(
                        f"储蓄目标清理异常，"
                        f"saving_id={saving_id}，"
                        f"error={error}"
                    )

    @allure.story("储蓄资金管理")
    @allure.title("已完成储蓄目标取出资金后自动恢复进行中")
    def test_withdraw_completed_saving_auto_active_success(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证已完成的储蓄目标取出资金后自动恢复进行中。

        后端业务规则：

        当目标处于 COMPLETED 状态，
        且取出后的金额低于目标金额时：

            status = ACTIVE

        测试数据：

            目标金额：1000.00
            初始已存：0.00
            存入金额：1000.00
            取出金额：300.00
            最终已存：700.00

        测试流程：

        1. 创建储蓄目标；
        2. 记录初始状态；
        3. 存入 1000.00；
        4. 验证自动完成；
        5. 记录取出前流水；
        6. 取出 300.00；
        7. 验证取出成功；
        8. 验证余额减少；
        9. 验证状态恢复进行中；
        10. 验证新增一条取出流水；
        11. 验证流水金额与前后余额；
        12. 清理测试数据。
        """

        # ======================================
        # 初始化测试变量
        # ======================================

        saving_id = None

        target_amount = Decimal("1000.00")
        deposit_amount = Decimal("1000.00")
        withdraw_amount = Decimal("300.00")

        try:
            # ==================================
            # 1. 创建储蓄目标
            # ==================================

            with allure.step("创建测试储蓄目标"):

                create_payload = saving_factory.build_saving(
                    target_amount=str(target_amount),
                    current_amount="0.00",
                    deadline="2027-12-31",
                )

                create_response = saving_api.create_saving(create_payload)

                assert create_response.status_code == 200, (
                    f"创建储蓄目标失败：" f"{create_response.text}"
                )

                create_result = create_response.json()

                assert create_result.get("code") == 200, (
                    f"创建储蓄目标业务失败：" f"{create_result}"
                )

                create_data = create_result.get("data")

                assert isinstance(
                    create_data, dict
                ), f"创建返回结构错误：{create_result}"

                saving_id = create_data.get("id")

                assert saving_id, f"创建储蓄目标后未返回 ID：" f"{create_result}"

            # ==================================
            # 2. 记录目标初始状态
            # ==================================

            with allure.step("记录储蓄目标初始状态"):

                initial_response = saving_api.get_saving_detail(saving_id)

                assert initial_response.status_code == 200, (
                    f"查询初始详情失败：" f"{initial_response.text}"
                )

                initial_result = initial_response.json()

                assert initial_result.get("code") == 200

                initial_data = initial_result.get("data")

                assert isinstance(initial_data, dict)

                # 初始状态应为正常进行中。
                # 保存真实状态值，避免猜测枚举字符串。
                initial_status = initial_data.get("status")

                assert initial_status not in (
                    None,
                    "paused",
                    "completed",
                ), (
                    f"新创建目标状态异常：" f"{initial_data}"
                )

                assert Decimal(str(initial_data["current_amount"])) == Decimal("0.00")

            # ==================================
            # 3. 存入 1000 元达到目标
            # ==================================

            with allure.step("存入1000元使目标自动完成"):

                deposit_payload = {
                    "amount": str(deposit_amount),
                    "note": "自动化测试-达到目标金额",
                }

                deposit_response = saving_api.deposit(
                    saving_id,
                    deposit_payload,
                )

                assert deposit_response.status_code == 200, (
                    f"存入资金失败：" f"{deposit_response.text}"
                )

                deposit_result = deposit_response.json()

                assert deposit_result.get("code") == 200, (
                    f"存入资金业务失败：" f"{deposit_result}"
                )

            # ==================================
            # 4. 验证目标已完成
            # ==================================

            with allure.step("验证储蓄目标自动完成"):

                completed_response = saving_api.get_saving_detail(saving_id)

                assert completed_response.status_code == 200, (
                    f"查询已完成目标失败：" f"{completed_response.text}"
                )

                completed_result = completed_response.json()

                assert completed_result.get("code") == 200

                completed_data = completed_result.get("data")

                assert isinstance(completed_data, dict)

                # 验证状态变为 completed。
                assert completed_data.get("status") == "completed", (
                    f"达到目标金额后未自动完成：" f"{completed_data}"
                )

                before_amount = Decimal(str(completed_data["current_amount"]))

                assert before_amount == target_amount, (
                    f"完成时金额错误，"
                    f"expected={target_amount}，"
                    f"actual={before_amount}"
                )

            # ==================================
            # 5. 查询取出前流水
            # ==================================

            with allure.step("记录取出前资金流水"):

                before_records_response = saving_api.get_records(saving_id)

                assert before_records_response.status_code == 200, (
                    f"查询取出前流水失败：" f"{before_records_response.text}"
                )

                before_records_result = before_records_response.json()

                assert before_records_result.get("code") == 200

                before_records = before_records_result.get(
                    "data",
                    [],
                )

                # 兼容列表和分页返回结构。
                if isinstance(before_records, dict):
                    before_records = before_records.get(
                        "results",
                        before_records.get("records", []),
                    )

                assert isinstance(before_records, list), (
                    f"取出前流水结构错误：" f"{before_records_result}"
                )

                # 首次存入应产生一条流水。
                assert len(before_records) == 1, (
                    f"取出前流水数量错误：" f"{before_records}"
                )

                before_record_ids = {record["id"] for record in before_records}

                deposit_record = before_records[0]

            # ==================================
            # 6. 从已完成目标取出300元
            # ==================================

            with allure.step("从已完成储蓄目标取出300元"):

                withdraw_payload = {
                    "amount": str(withdraw_amount),
                    "note": "自动化测试-完成目标取出300元",
                }

                withdraw_response = saving_api.withdraw(
                    saving_id,
                    withdraw_payload,
                )

                # 已完成目标允许取出资金。
                assert withdraw_response.status_code == 200, (
                    f"已完成目标取出资金失败，"
                    f"status_code={withdraw_response.status_code}，"
                    f"response={withdraw_response.text}"
                )

                withdraw_result = withdraw_response.json()

                assert withdraw_result.get("code") == 200, (
                    f"已完成目标取出资金业务失败：" f"{withdraw_result}"
                )

            # ==================================
            # 7. 查询取出后的目标详情
            # ==================================

            with allure.step("验证取出后余额及状态"):

                after_response = saving_api.get_saving_detail(saving_id)

                assert after_response.status_code == 200, (
                    f"取出后查询详情失败：" f"{after_response.text}"
                )

                after_result = after_response.json()

                assert after_result.get("code") == 200

                after_data = after_result.get("data")

                assert isinstance(after_data, dict)

                # 目标 ID 保持不变。
                assert after_data.get("id") == saving_id

                # ==================================
                # 验证余额变化
                # ==================================
                #
                # 1000.00 - 300.00 = 700.00
                #
                # ==================================

                after_amount = Decimal(str(after_data["current_amount"]))

                expected_amount = before_amount - withdraw_amount

                assert after_amount == expected_amount, (
                    f"已完成目标取出后金额错误，"
                    f"before={before_amount}，"
                    f"withdraw={withdraw_amount}，"
                    f"expected={expected_amount}，"
                    f"actual={after_amount}"
                )

                # ==================================
                # 验证余额低于目标
                # ==================================

                assert after_amount < target_amount, (
                    f"取出后余额未低于目标金额，"
                    f"current={after_amount}，"
                    f"target={target_amount}"
                )

                # ==================================
                # 验证状态自动恢复
                # ==================================
                #
                # 后端规则：
                #
                # COMPLETED -> ACTIVE
                #
                # 这里使用新建目标的初始状态，
                # 验证恢复到正常进行中状态。
                #
                # ==================================

                actual_status = after_data.get("status")

                assert actual_status == initial_status, (
                    f"已完成目标取出后没有恢复进行中，"
                    f"expected={initial_status}，"
                    f"actual={actual_status}，"
                    f"detail={after_data}"
                )

                # ==================================
                # 验证目标金额不变
                # ==================================

                assert Decimal(str(after_data["target_amount"])) == target_amount, (
                    f"取出后目标金额发生变化：" f"{after_data}"
                )

            # ==================================
            # 8. 查询取出后的资金流水
            # ==================================

            with allure.step("验证新增取出资金流水"):

                records_response = saving_api.get_records(saving_id)

                assert records_response.status_code == 200, (
                    f"查询取出后流水失败：" f"{records_response.text}"
                )

                records_result = records_response.json()

                assert records_result.get("code") == 200

                records = records_result.get("data", [])

                if isinstance(records, dict):
                    records = records.get(
                        "results",
                        records.get("records", []),
                    )

                assert isinstance(records, list), (
                    f"取出后流水结构错误：" f"{records_result}"
                )

                # ==================================
                # 应存在两条资金流水
                # ==================================
                #
                # 第一条：存入1000
                # 第二条：取出300
                #
                # ==================================

                assert len(records) == 2, (
                    f"存入和取出后应有两条流水，"
                    f"actual={len(records)}，"
                    f"records={records}"
                )

                # ==================================
                # 查找新增的取出流水
                # ==================================

                new_records = [
                    record
                    for record in records
                    if record.get("id") not in before_record_ids
                ]

                assert len(new_records) == 1, (
                    f"本次取出应新增一条流水，"
                    f"actual={len(new_records)}，"
                    f"records={records}"
                )

                withdraw_record = new_records[0]

                # ==================================
                # 验证流水金额
                # ==================================

                assert Decimal(str(withdraw_record["amount"])) == withdraw_amount, (
                    f"取出流水金额错误：" f"{withdraw_record}"
                )

                # ==================================
                # 验证变动前金额
                # ==================================

                assert (
                    Decimal(str(withdraw_record["before_amount"])) == before_amount
                ), (f"取出流水变动前金额错误：" f"{withdraw_record}")

                # ==================================
                # 验证变动后金额
                # ==================================

                assert (
                    Decimal(str(withdraw_record["after_amount"])) == expected_amount
                ), (f"取出流水变动后金额错误：" f"{withdraw_record}")

                # ==================================
                # 验证流水备注
                # ==================================

                assert withdraw_record.get("note") == (withdraw_payload["note"]), (
                    f"取出流水备注错误：" f"{withdraw_record}"
                )

                # ==================================
                # 验证存入和取出类型不同
                # ==================================
                #
                # 待确认 RecordType.WITHDRAW 的
                # 实际字符串后可以增加精确断言。
                #
                # ==================================

                if "record_type" in withdraw_record and "record_type" in deposit_record:
                    assert withdraw_record["record_type"] != (
                        deposit_record["record_type"]
                    ), (
                        f"存入和取出流水类型相同："
                        f"deposit={deposit_record}，"
                        f"withdraw={withdraw_record}"
                    )

            # ==================================
            # 9. 输出关键测试结果
            # ==================================

            print("储蓄目标 ID：", saving_id)
            print("目标金额：", target_amount)
            print("首次存入：", deposit_amount)
            print("取出金额：", withdraw_amount)
            print("取出前状态：", completed_data.get("status"))
            print("取出后状态：", actual_status)
            print("取出前余额：", before_amount)
            print("取出后余额：", after_amount)
            print("取出资金流水：", withdraw_record)

        finally:
            # ==================================
            # 10. 清理测试数据
            # ==================================
            #
            # 即使测试中途失败，
            # 也尝试清理本次创建的目标。
            #
            # ==================================

            if saving_id:

                try:
                    delete_response = saving_api.delete_saving(saving_id)

                    if delete_response.status_code != 200:
                        print(
                            f"储蓄目标测试数据清理失败，"
                            f"saving_id={saving_id}，"
                            f"status_code={delete_response.status_code}，"
                            f"response={delete_response.text}"
                        )

                except Exception as error:
                    print(
                        f"储蓄目标清理异常，"
                        f"saving_id={saving_id}，"
                        f"error={error}"
                    )

    @allure.story("储蓄资金管理")
    @allure.title("取出金额超过当前已存金额失败")
    def test_withdraw_exceed_balance_failed(
        self,
        saving_api,
        saving_factory,
    ):
        """
        验证取出金额超过储蓄目标当前余额时操作失败。

        后端业务规则：

            if amount > goal.current_amount:
                raise BusinessException(
                    "取出金额不能超过当前已存金额"
                )

        测试数据：

            目标金额：10000.00
            初始已存：0.00
            首次存入：500.00
            尝试取出：600.00

        预期结果：

            1. 取出操作失败；
            2. HTTP 状态码为 400；
            3. 业务状态码为 400；
            4. 返回余额不足的错误信息；
            5. current_amount 保持 500.00；
            6. target_amount 保持 10000.00；
            7. 目标状态不变；
            8. 不产生额外资金流水。

        测试完成后自动清理测试数据。
        """

        # ======================================
        # 1. 初始化测试数据
        # ======================================

        saving_id = None

        target_amount = Decimal("10000.00")
        deposit_amount = Decimal("500.00")
        withdraw_amount = Decimal("600.00")

        try:
            # ==================================
            # 2. 创建储蓄目标
            # ==================================

            with allure.step("创建储蓄目标"):

                create_payload = saving_factory.build_saving(
                    target_amount=str(target_amount),
                    current_amount="0.00",
                    deadline="2027-12-31",
                )

                create_response = saving_api.create_saving(create_payload)

                assert create_response.status_code == 200, (
                    f"创建储蓄目标失败：" f"{create_response.text}"
                )

                create_result = create_response.json()

                assert create_result.get("code") == 200, (
                    f"创建储蓄目标业务失败：" f"{create_result}"
                )

                create_data = create_result.get("data")

                assert isinstance(create_data, dict), (
                    f"创建储蓄目标返回结构错误：" f"{create_result}"
                )

                saving_id = create_data.get("id")

                assert saving_id, f"创建储蓄目标未返回 ID：" f"{create_result}"

            # ==================================
            # 3. 先存入 500 元
            # ==================================
            #
            # 为余额不足测试准备前置数据。
            #
            # ==================================

            with allure.step("存入500元准备测试余额"):

                deposit_payload = {
                    "amount": str(deposit_amount),
                    "note": "自动化测试-余额不足前置存入",
                }

                deposit_response = saving_api.deposit(
                    saving_id,
                    deposit_payload,
                )

                assert deposit_response.status_code == 200, (
                    f"前置存入资金失败：" f"{deposit_response.text}"
                )

                deposit_result = deposit_response.json()

                assert deposit_result.get("code") == 200, (
                    f"前置存入资金业务失败：" f"{deposit_result}"
                )

            # ==================================
            # 4. 查询取出前的储蓄目标
            # ==================================

            with allure.step("验证取出前储蓄余额"):

                before_response = saving_api.get_saving_detail(saving_id)

                assert before_response.status_code == 200, (
                    f"查询取出前详情失败：" f"{before_response.text}"
                )

                before_result = before_response.json()

                assert before_result.get("code") == 200, (
                    f"取出前查询业务失败：" f"{before_result}"
                )

                before_data = before_result.get("data")

                assert isinstance(before_data, dict), (
                    f"取出前详情结构错误：" f"{before_result}"
                )

                assert before_data.get("id") == saving_id

                # 获取取出前金额。
                before_amount = Decimal(str(before_data["current_amount"]))

                # 前置数据必须准备正确。
                assert before_amount == deposit_amount, (
                    f"取出前余额错误，"
                    f"expected={deposit_amount}，"
                    f"actual={before_amount}"
                )

                # 验证本次取出金额确实超过余额。
                assert withdraw_amount > before_amount, (
                    f"测试数据不符合余额不足场景，"
                    f"withdraw={withdraw_amount}，"
                    f"balance={before_amount}"
                )

                # 保存当前状态。
                before_status = before_data.get("status")

                assert before_status not in (
                    None,
                    "paused",
                    "completed",
                ), (
                    f"取出前储蓄目标状态异常：" f"{before_data}"
                )

                # 验证目标金额。
                before_target_amount = Decimal(str(before_data["target_amount"]))

                assert before_target_amount == target_amount, (
                    f"目标金额错误：" f"{before_data}"
                )

            # ==================================
            # 5. 查询取出前资金流水
            # ==================================

            with allure.step("记录取出前资金流水"):

                before_records_response = saving_api.get_records(saving_id)

                assert before_records_response.status_code == 200, (
                    f"查询取出前流水失败：" f"{before_records_response.text}"
                )

                before_records_result = before_records_response.json()

                assert before_records_result.get("code") == 200, (
                    f"查询取出前流水业务失败：" f"{before_records_result}"
                )

                before_records = before_records_result.get(
                    "data",
                    [],
                )

                # 兼容之前已使用的流水列表格式。
                if isinstance(before_records, dict):
                    before_records = before_records.get(
                        "results",
                        before_records.get("records", []),
                    )

                assert isinstance(before_records, list), (
                    f"取出前流水数据结构错误：" f"{before_records_result}"
                )

                # 前置操作只存入一次。
                assert len(before_records) == 1, (
                    f"取出前应只有一条存入流水，"
                    f"actual={len(before_records)}，"
                    f"records={before_records}"
                )

                # 保存原有流水 ID。
                before_record_ids = {record["id"] for record in before_records}

            # ==================================
            # 6. 尝试取出 600 元
            # ==================================
            #
            # 当前余额仅 500 元。
            #
            # 后端应拒绝此次请求。
            #
            # ==================================

            with allure.step("余额500元时尝试取出600元"):

                withdraw_payload = {
                    "amount": str(withdraw_amount),
                    "note": "自动化测试-取出金额超过余额",
                }

                withdraw_response = saving_api.withdraw(
                    saving_id,
                    withdraw_payload,
                )

                # ==================================
                # 7. HTTP 状态码断言
                # ==================================

                assert withdraw_response.status_code == 400, (
                    f"余额不足时取出操作未按预期失败，"
                    f"status_code={withdraw_response.status_code}，"
                    f"response={withdraw_response.text}"
                )

                # ==================================
                # 8. 业务状态码断言
                # ==================================

                withdraw_result = withdraw_response.json()

                assert withdraw_result.get("code") == 400, (
                    f"余额不足时取出业务状态码错误：" f"{withdraw_result}"
                )

                # ==================================
                # 9. 错误提示断言
                # ==================================
                #
                # 根据后端 BusinessException：
                #
                # 取出金额不能超过当前已存金额
                #
                # ==================================

                expected_message = "取出金额不能超过当前已存金额"

                actual_message = withdraw_result.get(
                    "message",
                    "",
                )

                assert expected_message in actual_message, (
                    f"余额不足错误提示不正确，"
                    f"expected={expected_message}，"
                    f"actual={actual_message}"
                )

            # ==================================
            # 10. 失败后再次查询储蓄目标
            # ==================================

            with allure.step("验证失败后余额及状态不变"):

                after_response = saving_api.get_saving_detail(saving_id)

                assert after_response.status_code == 200, (
                    f"取出失败后查询详情失败：" f"{after_response.text}"
                )

                after_result = after_response.json()

                assert after_result.get("code") == 200, (
                    f"取出失败后查询业务失败：" f"{after_result}"
                )

                after_data = after_result.get("data")

                assert isinstance(after_data, dict), (
                    f"取出失败后详情结构错误：" f"{after_result}"
                )

                # ==================================
                # 11. 验证目标 ID 不变
                # ==================================

                assert after_data.get("id") == saving_id

                # ==================================
                # 12. 验证当前已存金额没有变化
                # ==================================
                #
                # 余额不足时，不能发生扣款。
                #
                # 预期：
                #
                # before = 500.00
                # after  = 500.00
                #
                # ==================================

                after_amount = Decimal(str(after_data["current_amount"]))

                assert after_amount == before_amount, (
                    f"余额不足取出失败后，已存金额发生变化，"
                    f"before={before_amount}，"
                    f"withdraw={withdraw_amount}，"
                    f"after={after_amount}"
                )

                # ==================================
                # 13. 验证目标金额没有变化
                # ==================================

                after_target_amount = Decimal(str(after_data["target_amount"]))

                assert after_target_amount == before_target_amount, (
                    f"取出失败后目标金额发生变化，"
                    f"before={before_target_amount}，"
                    f"after={after_target_amount}"
                )

                # ==================================
                # 14. 验证目标状态没有变化
                # ==================================

                assert after_data.get("status") == before_status, (
                    f"取出失败后储蓄目标状态发生变化，"
                    f"before={before_status}，"
                    f"after={after_data.get('status')}"
                )

            # ==================================
            # 15. 查询取出失败后的资金流水
            # ==================================

            with allure.step("验证余额不足不生成资金流水"):

                after_records_response = saving_api.get_records(saving_id)

                assert after_records_response.status_code == 200, (
                    f"查询取出失败后流水失败：" f"{after_records_response.text}"
                )

                after_records_result = after_records_response.json()

                assert after_records_result.get("code") == 200, (
                    f"查询取出失败后流水业务失败：" f"{after_records_result}"
                )

                after_records = after_records_result.get(
                    "data",
                    [],
                )

                if isinstance(after_records, dict):
                    after_records = after_records.get(
                        "results",
                        after_records.get("records", []),
                    )

                assert isinstance(after_records, list), (
                    f"取出失败后流水结构错误：" f"{after_records_result}"
                )

                # ==================================
                # 16. 流水数量不能增加
                # ==================================

                assert len(after_records) == len(before_records), (
                    f"取出失败后流水数量发生变化，"
                    f"before={len(before_records)}，"
                    f"after={len(after_records)}"
                )

                # ==================================
                # 17. 流水 ID 集合不能变化
                # ==================================
                #
                # 防止余额未扣除，
                # 但意外创建了资金流水。
                #
                # ==================================

                after_record_ids = {record["id"] for record in after_records}

                assert after_record_ids == before_record_ids, (
                    f"余额不足取出失败后出现额外资金流水，"
                    f"before={before_record_ids}，"
                    f"after={after_record_ids}"
                )

            # ==================================
            # 18. 输出关键结果
            # ==================================

            print("储蓄目标 ID：", saving_id)
            print("目标金额：", target_amount)
            print("取出前余额：", before_amount)
            print("尝试取出金额：", withdraw_amount)
            print("取出接口响应：", withdraw_result)
            print("取出后余额：", after_amount)
            print("取出前状态：", before_status)
            print("取出后状态：", after_data.get("status"))
            print("取出前流水数量：", len(before_records))
            print("取出后流水数量：", len(after_records))

        finally:
            # ==================================
            # 19. 清理测试数据
            # ==================================
            #
            # 即使断言失败也尝试删除目标。
            #
            # 清理异常不覆盖原始测试异常。
            #
            # ==================================

            if saving_id:

                try:
                    delete_response = saving_api.delete_saving(saving_id)

                    if delete_response.status_code != 200:
                        print(
                            f"储蓄目标清理失败，"
                            f"saving_id={saving_id}，"
                            f"status_code={delete_response.status_code}，"
                            f"response={delete_response.text}"
                        )

                except Exception as error:
                    print(
                        f"储蓄目标清理发生异常，"
                        f"saving_id={saving_id}，"
                        f"error={error}"
                    )
