from erp_kchz_agent.app.main import create_app


def test_create_app_has_health_route():
    app = create_app()
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/api/chat" in paths
