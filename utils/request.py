import requests
import json

import allure


class RequestClient:
    """
    HTTP 请求客户端。

    统一处理：

    1. Base URL；
    2. 请求超时时间；
    3. JWT Token；
    4. GET / POST / PUT / DELETE 请求；
    5. Allure 请求信息；
    6. Allure 响应状态码；
    7. Allure 响应 JSON。
    """

    def __init__(
        self,
        base_url,
        timeout=10,
    ):
        """
        初始化请求客户端。

        :param base_url:
            后端服务地址，例如：

            http://127.0.0.1:8000

        :param timeout:
            请求超时时间，默认 10 秒。
        """

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # ======================================
        # 创建 requests Session
        # ======================================

        self.session = requests.Session()

    # ======================================
    # 设置 Token
    # ======================================

    def set_token(
        self,
        token,
    ):
        """
        设置 JWT Access Token。
        """

        self.session.headers.update({"Authorization": (f"Bearer {token}")})

    # ======================================
    # 清除 Token
    # ======================================

    def clear_token(
        self,
    ):
        """
        清除 Authorization 请求头。
        """

        self.session.headers.pop(
            "Authorization",
            None,
        )

    # ======================================
    # 统一请求方法
    # ======================================

    def request(
        self,
        method,
        url,
        **kwargs,
    ):
        """
        统一发送 HTTP 请求。

        每次请求都会自动记录到 Allure：

        Request
        Response Status Code
        Response
        """

        # ======================================
        # 拼接完整 URL
        # ======================================

        if url.startswith("http://") or url.startswith("https://"):
            full_url = url

        else:
            full_url = f"{self.base_url}" f"{url}"

        # ======================================
        # 获取请求参数
        # ======================================

        params = kwargs.get("params")

        json_data = kwargs.get("json")

        data = kwargs.get("data")

        files = kwargs.get("files")

        # ======================================
        # 构造 Allure 请求信息
        # ======================================

        # ======================================
        # Allure：请求方式
        # ======================================

        allure.attach(
            method.upper(),
            name="Request Method",
            attachment_type=(allure.attachment_type.TEXT),
        )

        # ======================================
        # Allure：请求 URL
        # ======================================

        allure.attach(
            full_url,
            name="Request URL",
            attachment_type=(allure.attachment_type.TEXT),
        )

        # ======================================
        # Allure：Query 参数
        # ======================================

        if params is not None:
            allure.attach(
                json.dumps(
                    params,
                    ensure_ascii=False,
                    indent=4,
                    default=str,
                ),
                name="Request Params",
                attachment_type=(allure.attachment_type.JSON),
            )

        # ======================================
        # Allure：JSON 请求体
        # ======================================

        if json_data is not None:
            allure.attach(
                json.dumps(
                    json_data,
                    ensure_ascii=False,
                    indent=4,
                    default=str,
                ),
                name="Request JSON",
                attachment_type=(allure.attachment_type.JSON),
            )

        # ======================================
        # Allure：普通 Form/Data 请求体
        # ======================================

        if data is not None:
            allure.attach(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=4,
                    default=str,
                ),
                name="Request Data",
                attachment_type=(allure.attachment_type.JSON),
            )

        # ======================================
        # 文件上传信息
        # ======================================
        #
        # 文件对象不能直接 JSON 序列化，
        # 所以这里只记录：
        #
        # 字段名
        # 文件名
        #
        # ======================================

        if files:

            file_info = {}

            for (
                field_name,
                file_value,
            ) in files.items():

                if isinstance(
                    file_value,
                    tuple,
                ):
                    # ==================================
                    # requests 文件上传格式通常是：
                    #
                    # (
                    #     文件名,
                    #     文件对象,
                    #     Content-Type
                    # )
                    # ==================================

                    file_info[field_name] = {
                        "filename": (file_value[0]),
                    }

                    # ==================================
                    # 如果存在 Content-Type
                    # ==================================

                    if len(file_value) >= 3:
                        file_info[field_name]["content_type"] = file_value[2]

                else:
                    file_info[field_name] = str(file_value)

            allure.attach(
                json.dumps(
                    file_info,
                    ensure_ascii=False,
                    indent=4,
                    default=str,
                ),
                name="Upload Files",
                attachment_type=(allure.attachment_type.JSON),
            )

        # ======================================
        # 发送请求
        # ======================================

        response = self.session.request(
            method=method,
            url=full_url,
            timeout=self.timeout,
            **kwargs,
        )

        # ======================================
        # 响应状态码写入 Allure
        # ======================================

        allure.attach(
            str(response.status_code),
            name=("Response Status Code"),
            attachment_type=(allure.attachment_type.TEXT),
        )

        # ======================================
        # 响应内容写入 Allure
        # ======================================

        try:
            # ==================================
            # 优先按照 JSON 解析
            # ==================================

            response_json = response.json()

            response_content = json.dumps(
                response_json,
                ensure_ascii=False,
                indent=4,
                default=str,
            )

            response_type = allure.attachment_type.JSON

        except ValueError:
            # ==================================
            # 如果不是 JSON，
            # 按普通文本保存
            # ==================================

            response_content = response.text

            response_type = allure.attachment_type.TEXT

        # ======================================
        # 响应信息写入 Allure
        # ======================================

        allure.attach(
            response_content,
            name="Response",
            attachment_type=(response_type),
        )

        # ======================================
        # 返回原始 Response
        # ======================================

        return response

    # ======================================
    # GET
    # ======================================

    def get(
        self,
        url,
        **kwargs,
    ):
        """
        发送 GET 请求。
        """

        return self.request(
            "GET",
            url,
            **kwargs,
        )

    # ======================================
    # POST
    # ======================================

    def post(
        self,
        url,
        **kwargs,
    ):
        """
        发送 POST 请求。
        """

        return self.request(
            "POST",
            url,
            **kwargs,
        )

    # ======================================
    # PUT
    # ======================================

    def put(
        self,
        url,
        **kwargs,
    ):
        """
        发送 PUT 请求。
        """

        return self.request(
            "PUT",
            url,
            **kwargs,
        )

    # ======================================
    # PATCH
    # ======================================

    def patch(
        self,
        url,
        **kwargs,
    ):
        """
        发送 PATCH 请求。
        """

        return self.request(
            "PATCH",
            url,
            **kwargs,
        )

    # ======================================
    # DELETE
    # ======================================

    def delete(
        self,
        url,
        **kwargs,
    ):
        """
        发送 DELETE 请求。
        """

        return self.request(
            "DELETE",
            url,
            **kwargs,
        )
