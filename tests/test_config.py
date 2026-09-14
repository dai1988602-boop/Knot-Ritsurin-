from knot_ritsurin.config import load_settings


def test_load_settings_defaults(monkeypatch):
    monkeypatch.delenv("BEDS24_REFRESH_TOKEN", raising=False)
    monkeypatch.delenv("PRICELABS_API_KEY", raising=False)
    monkeypatch.delenv("BEDS24_BASE_URL", raising=False)
    monkeypatch.delenv("PRICELABS_BASE_URL", raising=False)

    settings = load_settings()

    assert settings.beds24_base_url == "https://beds24.com/api/v2"
    assert settings.pricelabs_base_url == "https://api.pricelabs.co/v1"
    assert settings.beds24_refresh_token is None
    assert settings.pricelabs_api_key is None
