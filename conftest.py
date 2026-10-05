import pytest
import uuid
from common.request import RequestClient
from utils.config import Config


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
    auth_client,
    config,
):
    """
    创建测试账户并自动清理。

    使用方式：

    测试开始：
        自动创建一个账户。

    测试执行：
        将账户数据提供给测试用例。

    测试结束：
        自动删除测试账户。

    好处：

    1. 避免每个测试重复创建账户；
    2. 避免测试数据污染数据库；
    3. 即使用例失败，也会执行清理逻辑。
    """

    # ==========================================
    # 生成唯一账户名称
    # ==========================================

    account_name = "自动化账户_" f"{uuid.uuid4().hex[:8]}"

    # ==========================================
    # 创建账户接口
    # ==========================================

    url = f"{config.api_prefix}" f"/accounts/"

    # ==========================================
    # 创建账户参数
    # ==========================================

    payload = {
        "name": account_name,
        "account_type": "cash",
        "initial_balance": "1000.00",
        "note": "pytest fixture创建",
    }

    # ==========================================
    # 创建测试账户
    # ==========================================

    response = auth_client.post(
        url,
        json=payload,
    )

    assert response.status_code == 200, f"创建测试账户失败：" f"{response.text}"

    response_data = response.json()

    assert response_data.get("code") == 200, f"创建测试账户失败：" f"{response_data}"

    account_data = response_data.get(
        "data",
        {},
    )

    account_id = account_data.get("id")

    assert account_id

    # ==========================================
    # 将测试账户提供给测试用例
    # ==========================================

    yield account_data

    # ==========================================
    # 测试结束自动清理
    # ==========================================

    delete_url = f"{config.api_prefix}" f"/accounts/{account_id}/"

    auth_client.delete(delete_url)


@pytest.fixture
def transfer_accounts(
    auth_client,
    config,
):
    """
    创建两个用于转账测试的账户，
    并在测试结束后自动清理。

    source_account：
        转出账户

    target_account：
        转入账户
    """

    # ==========================================
    # 账户列表接口
    # ==========================================

    account_url = f"{config.api_prefix}" f"/accounts/"

    # ==========================================
    # 创建转出账户
    # ==========================================

    source_payload = {
        "name": ("转出账户_" f"{uuid.uuid4().hex[:8]}"),
        "account_type": "cash",
        "initial_balance": "1000.00",
    }

    source_response = auth_client.post(
        account_url,
        json=source_payload,
    )

    assert source_response.status_code == 200, (
        f"创建转出账户失败：" f"{source_response.text}"
    )

    source_data = source_response.json().get(
        "data",
        {},
    )

    source_id = source_data.get("id")

    assert source_id

    # ==========================================
    # 创建转入账户
    # ==========================================

    target_payload = {
        "name": ("转入账户_" f"{uuid.uuid4().hex[:8]}"),
        "account_type": "cash",
        "initial_balance": "500.00",
    }

    target_response = auth_client.post(
        account_url,
        json=target_payload,
    )

    assert target_response.status_code == 200, (
        f"创建转入账户失败：" f"{target_response.text}"
    )

    target_data = target_response.json().get(
        "data",
        {},
    )

    target_id = target_data.get("id")

    assert target_id

    # ==========================================
    # 提供给测试用例使用
    # ==========================================

    yield {
        "source": source_data,
        "target": target_data,
    }

    # ==========================================
    # 测试结束清理账户
    # ==========================================
    #
    # 因为转账完成后余额不为 0，
    # 所以先调整为 0，再删除。
    # ==========================================

    for account_id in [
        source_id,
        target_id,
    ]:
        adjust_url = f"{config.api_prefix}" f"/accounts/{account_id}/" "adjust-balance/"

        auth_client.post(
            adjust_url,
            json={
                "balance": "0.00",
                "note": "自动化测试清理",
            },
        )

        delete_url = f"{config.api_prefix}" f"/accounts/{account_id}/"

        auth_client.delete(delete_url)
