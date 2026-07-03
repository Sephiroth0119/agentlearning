from erp_kchz_agent.common.llm import LlmSettings, build_openai_client_kwargs


def test_build_openai_client_kwargs_uses_openai_compatible_settings():
    settings = LlmSettings(api_key="secret", base_url="https://api.example.com/v1", model="dp-v4-pro")

    kwargs = build_openai_client_kwargs(settings)

    assert kwargs == {"api_key": "secret", "base_url": "https://api.example.com/v1"}
