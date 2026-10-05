def test_config(
    config,
):
    """
    验证配置文件能够正常读取。
    """

    assert config.base_url

    assert config.api_prefix

    assert config.timeout > 0


def test_client(
    client,
):
    """
    验证请求客户端能够正常创建。
    """

    assert client is not None

    assert client.base_url
