import allure


@allure.feature("用户偏好模块")
class TestPreference:
    @allure.story("偏好查询")
    @allure.title("查询当前用户偏好成功")
    def test_get_preference_success(self, preference_api):
        """首次查询也应返回当前用户的一份有效偏好配置。"""

        # ======================================
        # 查询当前用户偏好
        # ======================================

        response = preference_api.get_preference()
        assert response.status_code == 200, response.text
        result = response.json()

        # ======================================
        # 验证业务结果与默认值范围
        # ======================================

        assert result["code"] == 200
        assert result["data"]["theme"] in ("light", "dark", "system")
        assert 5 <= result["data"]["page_size"] <= 100

    @allure.story("偏好修改")
    @allure.title("修改偏好后查询结果同步更新")
    def test_update_preference_success(self, preference_api):
        """修改主题和分页大小，并在 finally 中恢复原设置。"""

        # ======================================
        # 保存原偏好并构造不同的新值
        # ======================================

        response = preference_api.get_preference()
        assert response.status_code == 200, response.text
        original = response.json()["data"]
        new_theme = "dark" if original["theme"] != "dark" else "light"
        new_page_size = 50 if original["page_size"] != 50 else 20

        try:
            # ======================================
            # 提交偏好修改并验证响应
            # ======================================

            response = preference_api.update_preference(
                {"theme": new_theme, "page_size": new_page_size}
            )
            assert response.status_code == 200, response.text
            assert response.json()["data"]["theme"] == new_theme
            assert response.json()["data"]["page_size"] == new_page_size

            # ======================================
            # 再次查询并确认修改已保存
            # ======================================

            response = preference_api.get_preference()
            assert response.status_code == 200, response.text
            assert response.json()["data"]["theme"] == new_theme
            assert response.json()["data"]["page_size"] == new_page_size
        finally:
            # ======================================
            # 恢复原设置，避免影响其他操作
            # ======================================

            response = preference_api.update_preference(
                {"theme": original["theme"], "page_size": original["page_size"]}
            )
            assert response.status_code == 200, response.text
