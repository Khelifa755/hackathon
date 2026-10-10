from config import CONFIG, Config, load_config


def test_default_config_is_deterministic(monkeypatch):
    monkeypatch.delenv("SEED", raising=False)
    assert load_config().seed == 26
    assert CONFIG == Config()


def test_seed_can_be_overridden(monkeypatch):
    monkeypatch.setenv("SEED", "123")
    assert load_config().seed == 123
