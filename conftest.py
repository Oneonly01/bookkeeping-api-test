import pytest
from common.account_api import AccountApi
from common.request import RequestClient
from utils.config import Config
from utils.data_factory import AccountDataFactory


@pytest.fixture(scope="session")
def config():
    """
    获取自动化测试配置。

    scope="session" 表示：

    整个 pytest 测试过程中
    只创建一次 Config 实例。
    """

    return Config()


@pytest.fixture(scope="session")
def client(
    config,
):
    """
    创建统一请求客户端。

    负责：

    1. 设置 base_url；
    2. 设置请求超时时间；
    3. 提供 GET / POST / PUT / DELETE；
    4. 后续可以统一设置 JWT Token。
    """

    request_client = RequestClient(
        base_url=config.base_url,
        timeout=config.timeout,
    )

    return request_client


@pytest.fixture(scope="session")
def access_token(
    config,
    client,
):
    """
    自动登录并获取 JWT Access Token。

    作用：

    1. 调用登录接口；
    2. 校验登录是否成功；
    3. 提取 access token；
    4. 返回给后续测试使用。

    scope="session" 表示：
    整个测试会话中只登录一次。
    """

    # ==========================================
    # 获取测试账号配置
    # ==========================================

    test_user = config.test_user

    # ==========================================
    # 拼接登录接口地址
    # ==========================================

    login_url = f"{config.api_prefix}" f"/auth/login/"

    # ==========================================
    # 发送登录请求
    # ==========================================

    response = client.post(
        login_url,
        json=test_user,
    )

    # ==========================================
    # 基础 HTTP 状态码校验
    # ==========================================

    assert response.status_code == 200, (
        f"登录接口请求失败，"
        f"status_code={response.status_code}，"
        f"response={response.text}"
    )

    # ==========================================
    # 转换 JSON 响应
    # ==========================================

    response_data = response.json()

    # ==========================================
    # 校验统一响应 code
    # ==========================================

    assert response_data.get("code") == 200, f"登录失败：{response_data}"

    # ==========================================
    # 获取 data
    # ==========================================

    data = response_data.get(
        "data",
        {},
    )

    # ==========================================
    # 提取 Access Token
    # ==========================================
    #
    # 登录接口实际返回：
    #
    # {
    #     "data": {
    #         "access_token": "xxx",
    #         "refresh_token": "xxx",
    #         "token_type": "Bearer"
    #     }
    # }
    #
    # ==========================================

    token = data.get("access_token")

    assert token, f"登录成功但未获取到 access token：" f"{response_data}"

    return token


@pytest.fixture(scope="session")
def auth_client(
    client,
    access_token,
):
    """
    创建已经完成 JWT 鉴权的请求客户端。

    后续所有需要登录的接口，
    直接使用 auth_client 即可。

    不需要每个测试都重复写：

    Authorization: Bearer xxx
    """

    client.set_token(access_token)

    return client


@pytest.fixture
def test_account(
    account_api,
    account_factory,
):
    """
    创建一个通用测试账户。

    主要作用：

    1. 测试开始前自动创建账户；
    2. 将创建成功后的账户数据返回给测试用例；
    3. 测试结束后自动清理账户；
    4. 避免每条账户测试用例都重复：
       - 构造账户数据；
       - 调用创建接口；
       - 获取账户 ID；
       - 调整余额；
       - 删除账户。

    使用方式：

    def test_xxx(
        self,
        test_account,
    ):
        account_id = test_account["id"]

    注意：

    当前系统规则：

    账户余额不为 0 时不能删除。

    因此 fixture 在清理测试数据时，
    会先将余额调整为 0，
    再执行删除账户操作。
    """

    # ======================================
    # 构造测试账户数据
    # ======================================
    #
    # AccountDataFactory 会自动：
    #
    # 1. 生成唯一账户名称；
    # 2. 设置账户类型；
    # 3. 设置初始余额；
    # 4. 设置测试备注。
    #
    # ======================================

    payload = account_factory.build_account(
        initial_balance="1000.00",
        note="pytest通用测试账户",
    )

    # ======================================
    # 创建测试账户
    # ======================================

    response = account_api.create_account(payload)

    # ======================================
    # 创建结果校验
    # ======================================
    #
    # fixture 属于测试前置条件。
    #
    # 如果账户创建失败，
    # 后面的测试继续执行已经没有意义，
    # 所以直接通过 assert 中断。
    #
    # ======================================

    assert response.status_code == 200, (
        f"创建测试账户失败，"
        f"status_code={response.status_code}，"
        f"response={response.text}"
    )

    response_data = response.json()

    assert response_data.get("code") == 200, (
        f"创建测试账户业务失败：" f"{response_data}"
    )

    # ======================================
    # 获取创建后的账户数据
    # ======================================

    account_data = response_data.get(
        "data",
        {},
    )

    # ======================================
    # 校验账户 ID
    # ======================================

    account_id = account_data.get("id")

    assert account_id, f"创建测试账户后未返回账户 ID：" f"{response_data}"

    # ======================================
    # 将账户数据交给测试用例
    # ======================================
    #
    # yield 前：
    #     属于测试前置操作。
    #
    # yield：
    #     将 account_data 返回给测试方法。
    #
    # yield 后：
    #     属于测试清理操作。
    #
    # ======================================

    yield account_data

    # ======================================
    # 清理测试数据
    # ======================================

    try:
        # ==================================
        # 将账户余额调整为 0
        # ==================================
        #
        # 当前账户初始余额为 1000.00，
        # 系统不允许直接删除非零余额账户，
        # 所以删除前统一归零。
        #
        # ==================================

        account_api.adjust_balance(
            account_id,
            {
                "balance": "0.00",
                "note": "pytest自动清理测试账户",
            },
        )

        # ==================================
        # 删除测试账户
        # ==================================

        account_api.delete_account(account_id)

    except Exception as exc:
        # ==================================
        # 清理失败时打印提示
        # ==================================
        #
        # 这里不建议因为清理失败，
        # 覆盖真正的测试失败原因。
        #
        # 后续正式框架中，
        # 可以进一步替换为 logging。
        #
        # ==================================

        print(f"测试账户清理失败：" f"account_id={account_id}，" f"error={exc}")


@pytest.fixture
def transfer_accounts(
    account_api,
    account_factory,
):
    """
    创建账户转账测试所需要的两个账户。

    fixture 会自动创建：

    1. 转出账户：
       初始余额 1000.00

    2. 转入账户：
       初始余额 500.00

    测试结束后自动：

    1. 将两个账户余额调整为 0；
    2. 删除两个测试账户。

    主要用于：

    1. 转账成功；
    2. 余额不足；
    3. 转给自己；
    4. 目标账户不存在；
    5. 转账列表；
    6. 转账详情；
    7. 后续转账冲正测试。

    测试方法中可以直接使用：

    transfer_accounts["source"]
    transfer_accounts["target"]
    """

    # ======================================
    # 构造转出账户测试数据
    # ======================================
    #
    # 转出账户初始余额：
    #
    # 1000.00
    #
    # ======================================

    source_payload = account_factory.build_account_with_balance(
        "1000.00",
        note="自动化测试转出账户",
    )

    # ======================================
    # 构造转入账户测试数据
    # ======================================
    #
    # 转入账户初始余额：
    #
    # 500.00
    #
    # ======================================

    target_payload = account_factory.build_account_with_balance(
        "500.00",
        note="自动化测试转入账户",
    )

    # ======================================
    # 创建转出账户
    # ======================================

    source_response = account_api.create_account(source_payload)

    # ======================================
    # 转出账户创建结果断言
    # ======================================

    assert source_response.status_code == 200, (
        f"创建转出测试账户失败，"
        f"status_code={source_response.status_code}，"
        f"response={source_response.text}"
    )

    source_response_data = source_response.json()

    assert source_response_data.get("code") == 200, (
        f"创建转出测试账户业务失败：" f"{source_response_data}"
    )

    # ======================================
    # 获取转出账户数据
    # ======================================

    source_account = source_response_data.get(
        "data",
        {},
    )

    source_id = source_account.get("id")

    assert source_id, f"创建转出账户后未返回账户 ID：" f"{source_response_data}"

    # ======================================
    # 创建转入账户
    # ======================================

    target_response = account_api.create_account(target_payload)

    # ======================================
    # 转入账户创建结果断言
    # ======================================

    assert target_response.status_code == 200, (
        f"创建转入测试账户失败，"
        f"status_code={target_response.status_code}，"
        f"response={target_response.text}"
    )

    target_response_data = target_response.json()

    assert target_response_data.get("code") == 200, (
        f"创建转入测试账户业务失败：" f"{target_response_data}"
    )

    # ======================================
    # 获取转入账户数据
    # ======================================

    target_account = target_response_data.get(
        "data",
        {},
    )

    target_id = target_account.get("id")

    assert target_id, f"创建转入账户后未返回账户 ID：" f"{target_response_data}"

    # ======================================
    # 将账户数据提供给测试方法
    # ======================================
    #
    # yield 前：
    #
    # 测试前置数据准备。
    #
    # yield：
    #
    # 正式执行测试方法。
    #
    # yield 后：
    #
    # 自动清理测试数据。
    #
    # ======================================

    yield {
        "source": source_account,
        "target": target_account,
    }

    # ======================================
    # 清理转出账户
    # ======================================

    try:
        # ==================================
        # 将转出账户余额归零
        # ==================================
        #
        # 无论测试过程中余额变成多少，
        # 最终都统一调整为 0。
        #
        # ==================================

        account_api.adjust_balance(
            source_id,
            {
                "balance": "0.00",
                "note": "自动化测试清理转出账户",
            },
        )

        # ==================================
        # 删除转出账户
        # ==================================

        account_api.delete_account(source_id)

    except Exception as exc:
        # ==================================
        # 清理失败不覆盖原始测试结果
        # ==================================

        print(f"转出账户清理失败：" f"account_id={source_id}，" f"error={exc}")

    # ======================================
    # 清理转入账户
    # ======================================

    try:
        # ==================================
        # 将转入账户余额归零
        # ==================================

        account_api.adjust_balance(
            target_id,
            {
                "balance": "0.00",
                "note": "自动化测试清理转入账户",
            },
        )

        # ==================================
        # 删除转入账户
        # ==================================

        account_api.delete_account(target_id)

    except Exception as exc:
        # ==================================
        # 清理失败不覆盖原始测试结果
        # ==================================

        print(f"转入账户清理失败：" f"account_id={target_id}，" f"error={exc}")


@pytest.fixture(scope="session")
def account_api(
    auth_client,
    config,
):
    """
    提供账户模块 API 对象。

    作用：

    1. 统一封装账户模块接口；
    2. 测试用例不再重复拼接 URL；
    3. 测试用例只关注：
       - 测试数据；
       - 调用接口；
       - 结果断言。
    """

    return AccountApi(
        client=auth_client,
        api_prefix=config.api_prefix,
    )


@pytest.fixture(scope="session")
def account_factory():
    """
    提供账户测试数据工厂。

    测试用例中可以直接使用：

    account_factory.build_account()

    或：

    account_factory.build_zero_balance_account()

    或：

    account_factory.build_account_with_balance(
        "5000.00"
    )

    这样测试用例不需要重复写大量 payload。
    """

    return AccountDataFactory
