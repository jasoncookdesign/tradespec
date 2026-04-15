from app.core.config import Settings


def test_settings_parse_comma_separated_allowed_origins(monkeypatch) -> None:
    monkeypatch.setenv(
        "TRADESPEC_ALLOWED_ORIGINS",
        "http://localhost:3000, http://localhost:3001",
    )

    settings = Settings()

    assert settings.allowed_origins == [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
