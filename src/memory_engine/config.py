from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, Mapping

import yaml


_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")


class ConfigError(ValueError):
    """Raised for user-fixable configuration/env-file problems."""


def load_config(path: str | Path, *, env: Mapping[str, str] | None = None) -> Dict[str, Any]:
    """Load YAML config and expand Docker-friendly ${ENV} placeholders.

    `${NAME}` is required and raises ConfigError when NAME is missing or empty.
    `${NAME:-default}` uses `default` when NAME is missing or empty.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(
            f"Missing config file: {config_path}. Copy config.example.yaml to config.yaml and edit it."
        )

    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {config_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"Config file {config_path} must contain a YAML mapping at the top level")

    return _expand_env(data, os.environ if env is None else env)


def validate_scan_config(
    cfg: Dict[str, Any], *, env: Mapping[str, str] | None = None
) -> tuple[str, list[dict[str, str]], Path]:
    """Validate only the config fields needed to start a read-only scan."""
    current_env = os.environ if env is None else env

    immich_cfg = cfg.get("immich")
    if not isinstance(immich_cfg, dict):
        raise ConfigError("Missing immich section in config")

    base_url = immich_cfg.get("url")
    if not isinstance(base_url, str) or not base_url.strip():
        raise ConfigError("Missing immich.url in config. Use ${IMMICH_URL} and set IMMICH_URL in .env.")

    raw_users = immich_cfg.get("users")
    if not isinstance(raw_users, list) or not raw_users:
        raise ConfigError("Missing immich.users in config. Add at least one user with name and api_key_env.")

    users: list[dict[str, str]] = []
    for index, user in enumerate(raw_users, start=1):
        if not isinstance(user, dict):
            raise ConfigError(f"immich.users[{index}] must be a mapping")
        owner = user.get("name")
        api_key_env = user.get("api_key_env")
        if not isinstance(owner, str) or not owner.strip():
            raise ConfigError(f"immich.users[{index}] is missing name")
        if not isinstance(api_key_env, str) or not api_key_env.strip():
            raise ConfigError(f"immich.users[{index}] is missing api_key_env")
        if not current_env.get(api_key_env):
            raise ConfigError(
                f"Missing API key environment variable {api_key_env} for user {owner}. "
                "Set it in .env; never commit .env."
            )
        users.append({"name": owner.strip(), "api_key_env": api_key_env.strip()})

    output_cfg = cfg.get("output", {})
    if output_cfg is None:
        output_cfg = {}
    if not isinstance(output_cfg, dict):
        raise ConfigError("output section must be a mapping when present")
    output_dir = output_cfg.get("dir") or "output"
    if not isinstance(output_dir, str):
        raise ConfigError("output.dir must be a path string when present")

    return base_url.strip(), users, Path(output_dir)


def _expand_env(value: Any, env: Mapping[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: _expand_env(item, env) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand_env(item, env) for item in value]
    if isinstance(value, str):
        return _expand_env_string(value, env)
    return value


def _expand_env_string(value: str, env: Mapping[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        default = match.group(2)
        env_value = env.get(name)
        if env_value:
            return env_value
        if default is not None:
            return default
        raise ConfigError(
            f"Missing environment variable {name} referenced in config. "
            "Set it in .env; never commit .env."
        )

    return _ENV_PATTERN.sub(replace, value)
