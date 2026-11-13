# Changelog

## 1.2.0

- A computed value that fails raises `chonkconf.ConfigError`, and the message names its key: `cache.max_age: could not compute ...`.

## 1.1.0

- Computed values work inside arrays too: `sizes = ["{{ 2 * 64 }}", 512]`.

## 1.0.0

- First release: `load()` and `loads()` read TOML and compute `"{{ ... }}"` values, with your own `functions=`.
