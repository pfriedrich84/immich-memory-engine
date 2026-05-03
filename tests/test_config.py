import pytest

from memory_engine.config import ConfigError, load_config, validate_scan_config


def test_load_config_expands_required_and_default_env(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
immich:
  url: "${IMMICH_URL}"
output:
  dir: "${OUTPUT_DIR:-output}"
""".strip(),
        encoding="utf-8",
    )

    cfg = load_config(config_path, env={"IMMICH_URL": "http://immich.test"})

    assert cfg["immich"]["url"] == "http://immich.test"
    assert cfg["output"]["dir"] == "output"


def test_load_config_requires_referenced_env(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text('immich:\n  url: "${IMMICH_URL}"\n', encoding="utf-8")

    with pytest.raises(ConfigError, match="IMMICH_URL"):
        load_config(config_path, env={})


def test_scan_config_requires_user_api_key_env(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
immich:
  url: "http://immich.test"
  users:
    - name: "paul"
      api_key_env: "IMMICH_API_KEY_PAUL"
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.delenv("IMMICH_API_KEY_PAUL", raising=False)

    cfg = load_config(config_path)

    with pytest.raises(ConfigError, match="IMMICH_API_KEY_PAUL"):
        validate_scan_config(cfg, env={})


def test_scan_config_defaults_output_dir(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
immich:
  url: "http://immich.test"
  users:
    - name: "paul"
      api_key_env: "IMMICH_API_KEY_PAUL"
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setenv("IMMICH_API_KEY_PAUL", "secret")

    cfg = load_config(config_path)
    _base_url, _users, output_dir = validate_scan_config(cfg, env={"IMMICH_API_KEY_PAUL": "secret"})

    assert str(output_dir) == "output"
