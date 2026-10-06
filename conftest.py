import pytest
from common.account_api import AccountApi
from common.auth_api import AuthApi
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

    主要负责：

    1. 设置 base_url；
    2. 设置请求超时时间；
    3. 统一管理 requests.Session；
    4. 提供 GET / POST / PUT / DELETE；
    5. 支持统一设置 JWT Token。

    当前 client 属于整个自动化框架
    最底层的 HTTP 请求对象。

    上层业务接口例如：

    AuthApi
    AccountApi

    都会继续复用这个 RequestClient。
    """

    request_client = RequestClient(
        base_url=config.base_url,
        timeout=config.timeout,
    )

    return request_client


@pytest.fixture(scope="session")
def auth_api(
    client,
    config,
):
    """
    提供用户认证模块 API 对象。

    主要作用：

    1. 统一封装认证模块 URL；
    2. 统一处理认证模块 HTTP 请求；
    3. 避免 fixture 和测试用例重复拼接 URL。

    注意：

    这里使用的是未登录状态的 client。

    因为：

    登录接口本身就是为了获取 JWT Token，
    不应该依赖已经认证的 auth_client。
    """

    return AuthApi(
        client=client,
        api_prefix=config.api_prefix,
    )


@pytest.fixture(scope="session")
def auth_tokens(
    config,
    auth_api,
):
    """
    自动登录并获取完整 JWT Token 数据。

    主要作用：

    1. 从配置文件读取测试账号；
    2. 调用用户登录接口；
    3. 校验登录是否成功；
    4. 一次性提取：
       - access_token；
       - refresh_token；
       - token_type；
    5. 提供给其他 Token fixture 复用。

    为什么需要 auth_tokens：

    原来如果分别定义：

    access_token
    refresh_token

    并且两个 fixture 都自己调用登录接口，

    那么整个 pytest 测试会话中
    会重复登录两次。

    现在统一由 auth_tokens 登录一次，
    后续：

    access_token
    refresh_token

    都直接从 auth_tokens 中读取即可。

    scope="session" 表示：

    整个 pytest 测试会话中，
    登录操作只执行一次。
    """

    # ==========================================
    # 获取测试账号
    # ==========================================
    #
    # 测试账号统一来自：
    #
    # config/config.yaml
    #
    # 使用 copy()，
    # 避免后续测试代码修改原始配置。
    #
    # ==========================================

    test_user = config.test_user.copy()

    # ==========================================
    # 调用登录接口
    # ==========================================
    #
    # 登录请求统一通过：
    #
    # AuthApi.login()
    #
    # 不再直接使用 client.post()
    # 也不再手动拼接登录 URL。
    #
    # ==========================================

    response = auth_api.login(test_user)

    # ==========================================
    # HTTP 状态码断言
    # ==========================================

    assert response.status_code == 200, (
        f"自动登录接口请求失败，"
        f"status_code={response.status_code}，"
        f"response={response.text}"
    )

    # ==========================================
    # 解析登录响应
    # ==========================================

    response_data = response.json()

    # ==========================================
    # 业务状态码断言
    # ==========================================

    assert response_data.get("code") == 200, f"自动登录业务失败：" f"{response_data}"

    # ==========================================
    # 获取登录 data
    # ==========================================

    data = response_data.get(
        "data",
        {},
    )

    # ==========================================
    # 获取 Access Token
    # ==========================================

    access_token_value = data.get("access_token")

    assert access_token_value, f"登录成功但未返回 access_token：" f"{response_data}"

    # ==========================================
    # 获取 Refresh Token
    # ==========================================

    refresh_token_value = data.get("refresh_token")

    assert refresh_token_value, f"登录成功但未返回 refresh_token：" f"{response_data}"

    # ==========================================
    # 获取 Token 类型
    # ==========================================

    token_type = data.get("token_type")

    assert token_type == "Bearer", (
        f"Token 类型错误，" f"expected=Bearer，" f"actual={token_type}"
    )

    # ==========================================
    # 返回完整 Token 数据
    # ==========================================
    #
    # 后续其他 fixture 可以直接使用：
    #
    # auth_tokens["access_token"]
    #
    # auth_tokens["refresh_token"]
    #
    # ==========================================

    return {
        "access_token": access_token_value,
        "refresh_token": refresh_token_value,
        "token_type": token_type,
    }


@pytest.fixture(scope="session")
def access_token(
    auth_tokens,
):
    """
    获取当前测试会话的 Access Token。

    Access Token 不再自己调用登录接口，

    而是直接复用：

    auth_tokens

    中已经获取到的 Token。
    """

    return auth_tokens["access_token"]


@pytest.fixture(scope="session")
def refresh_token(
    auth_tokens,
):
    """
    获取当前测试会话的 Refresh Token。

    Refresh Token 不再重复调用登录接口，

    而是直接复用：

    auth_tokens

    中已经获取到的数据。

    后续可用于：

    1. Token 刷新；
    2. 用户退出；
    3. Refresh Token 失效验证。
    """

    return auth_tokens["refresh_token"]


@pytest.fixture(scope="session")
def auth_client(
    client,
    access_token,
):
    """
    创建已经完成 JWT 鉴权的请求客户端。

    主要作用：

    1. 获取 Access Token；
    2. 设置 Authorization 请求头；
    3. 提供给需要登录的业务接口使用。

    后续例如：

    AccountApi
    TransactionApi
    BudgetApi

    都可以基于这个 auth_client
    调用需要登录权限的接口。
    """

    # ==========================================
    # 设置 JWT Access Token
    # ==========================================
    #
    # RequestClient.set_token()
    # 会统一设置：
    #
    # Authorization: Bearer <access_token>
    #
    # ==========================================

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


@pytest.fixture
def fresh_auth_context(
    config,
):
    """
    创建一次性的认证测试上下文。

    主要用于：

    1. Token 刷新测试；
    2. 退出登录测试；
    3. Refresh Token 黑名单测试；
    4. Token 失效测试；
    5. 其他会改变 Token 状态的认证场景。

    为什么需要这个 fixture：

    当前 auth_tokens 使用：

        scope="session"

    整个 pytest 测试会话只登录一次。

    对于普通业务接口测试来说没有问题，
    因为 Access Token 可以重复使用。

    但是 logout 等接口会导致：

        refresh_token 失效
        或
        refresh_token 被加入黑名单

    如果继续复用 session 级 Refresh Token，
    就可能出现：

        单独执行用例 -> PASS
        整套执行用例 -> FAIL

    这属于典型的测试用例相互污染。

    因此这里使用默认的 function scope：

        每执行一次测试方法，
        都创建一套全新的 Token。

    同时这里创建独立的 RequestClient，

    不复用全局 client，

    避免修改 Authorization 请求头时
    影响其他测试。
    """

    # ==========================================
    # 创建独立 RequestClient
    # ==========================================
    #
    # 注意：
    #
    # 这里不能直接复用 session 级 client。
    #
    # 原因：
    #
    # auth_client 会对全局 client 执行：
    #
    # client.set_token(access_token)
    #
    # 如果生命周期测试继续修改同一个 client，
    # 可能影响其他测试用例。
    #
    # 所以这里单独创建一个新的请求客户端。
    #
    # ==========================================

    fresh_client = RequestClient(
        base_url=config.base_url,
        timeout=config.timeout,
    )

    # ==========================================
    # 创建独立 AuthApi
    # ==========================================

    fresh_auth_api = AuthApi(
        client=fresh_client,
        api_prefix=config.api_prefix,
    )

    # ==========================================
    # 获取测试账号
    # ==========================================

    test_user = config.test_user.copy()

    # ==========================================
    # 调用登录接口
    # ==========================================

    login_response = fresh_auth_api.login(test_user)

    # ==========================================
    # 登录 HTTP 状态码断言
    # ==========================================

    assert login_response.status_code == 200, (
        f"创建一次性认证上下文失败，"
        f"status_code={login_response.status_code}，"
        f"response={login_response.text}"
    )

    # ==========================================
    # 解析登录响应
    # ==========================================

    login_response_data = login_response.json()

    # ==========================================
    # 登录业务状态码断言
    # ==========================================

    assert login_response_data.get("code") == 200, (
        f"创建一次性认证上下文登录失败：" f"{login_response_data}"
    )

    # ==========================================
    # 获取 Token 数据
    # ==========================================

    data = login_response_data.get(
        "data",
        {},
    )

    access_token_value = data.get("access_token")

    refresh_token_value = data.get("refresh_token")

    # ==========================================
    # Access Token 存在性断言
    # ==========================================

    assert access_token_value, (
        f"登录成功但未返回 access_token：" f"{login_response_data}"
    )

    # ==========================================
    # Refresh Token 存在性断言
    # ==========================================

    assert refresh_token_value, (
        f"登录成功但未返回 refresh_token：" f"{login_response_data}"
    )

    # ==========================================
    # 给独立 Client 设置 Access Token
    # ==========================================
    #
    # 后面的 logout 等接口要求：
    #
    # Authorization: Bearer <access_token>
    #
    # 所以这里登录成功后，
    # 立即设置 Authorization 请求头。
    #
    # ==========================================

    fresh_client.set_token(access_token_value)

    # ==========================================
    # 返回当前测试专属认证上下文
    # ==========================================
    #
    # 测试方法可以直接使用：
    #
    # fresh_auth_context["auth_api"]
    #
    # fresh_auth_context["access_token"]
    #
    # fresh_auth_context["refresh_token"]
    #
    # ==========================================

    return {
        "client": fresh_client,
        "auth_api": fresh_auth_api,
        "access_token": access_token_value,
        "refresh_token": refresh_token_value,
    }
