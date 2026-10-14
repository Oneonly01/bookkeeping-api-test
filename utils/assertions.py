import json


def assert_success(
    response,
    message="接口请求失败",
):
    """
    校验接口成功响应。

    校验：

    1. HTTP状态码
    2. 业务code

    返回：

    response.data
    """

    # ======================================
    # HTTP状态码
    # ======================================

    assert response.status_code == 200, (
        f"{message}\n"
        f"HTTP状态码异常\n"
        f"status_code={response.status_code}\n"
        f"response={response.text}"
    )

    # ======================================
    # JSON解析
    # ======================================

    result = response.json()

    # ======================================
    # 业务code
    # ======================================

    assert result.get("code") == 200, (
        f"{message}\n"
        f"业务返回失败\n"
        f"{json.dumps(result, ensure_ascii=False, indent=4)}"
    )

    return result
