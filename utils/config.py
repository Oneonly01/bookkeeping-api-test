from pathlib import Path

import yaml


class Config:
    """
    自动化测试配置读取工具。

    负责：

    1. 读取 config.yaml；
    2. 获取 base_url；
    3. 获取 api_prefix；
    4. 获取请求超时时间；
    5. 获取测试账号配置。
    """

    # ==========================================
    # 项目根目录
    # ==========================================
    #
    # 当前文件：
    #
    # utils/config.py
    #
    # parent:
    # utils
    #
    # parent.parent:
    # bookkeeping_api_test
    #
    # ==========================================

    BASE_DIR = Path(__file__).resolve().parent.parent

    CONFIG_FILE = BASE_DIR / "config" / "config.yaml"

    def __init__(
        self,
    ):
        """
        初始化并加载配置文件。
        """

        self._config = self._load_config()

    def _load_config(
        self,
    ) -> dict:
        """
        读取 YAML 配置文件。
        """

        # ======================================
        # 检查配置文件是否存在
        # ======================================

        if not self.CONFIG_FILE.exists():
            raise FileNotFoundError(f"配置文件不存在：" f"{self.CONFIG_FILE}")

        # ======================================
        # 读取 YAML
        # ======================================

        with self.CONFIG_FILE.open(
            mode="r",
            encoding="utf-8",
        ) as file:

            config = yaml.safe_load(file)

        # ======================================
        # 防止空配置文件
        # ======================================

        if not config:
            raise ValueError("config.yaml 配置内容不能为空")

        return config

    @property
    def environment(
        self,
    ) -> str:
        """
        获取当前测试环境。
        """

        return self._config.get(
            "environment",
            "test",
        )

    @property
    def base_url(
        self,
    ) -> str:
        """
        获取接口基础地址。
        """

        return self._config["base_url"].rstrip("/")

    @property
    def api_prefix(
        self,
    ) -> str:
        """
        获取接口统一前缀。
        """

        return self._config.get(
            "api_prefix",
            "/api/v1",
        )

    @property
    def timeout(
        self,
    ) -> int:
        """
        获取接口请求超时时间。
        """

        request_config = self._config.get(
            "request",
            {},
        )

        return request_config.get(
            "timeout",
            10,
        )

    @property
    def test_user(
        self,
    ) -> dict:
        """
        获取测试账号配置。
        """

        return self._config.get(
            "test_user",
            {},
        )
