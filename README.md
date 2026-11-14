# chonkconf

A tiny TOML config loader with computed values.

> **A demo library.** chonkconf was built for a video about the Mistral Agents SDK, as the dependency an agent keeps up to date. Don't use it in production.

> **Security:** versions up to 1.2.0 let a config file run code (see the [security advisories](https://github.com/megaconfidence/chonkconf/security/advisories)). Upgrade to 2.0.0; see the [upgrade guide](CHANGELOG.md#upgrading-from-1x).

## Install

```bash
uv add "chonkconf @ git+https://github.com/megaconfidence/chonkconf" --tag v2.0.0
```

## Use it

Write a value as `"{{ ... }}"` and chonkconf computes it when the file loads:

```toml
[cache]
max_age = "{{ 7 * day }}"

[uploads]
max_size = "{{ 25 * MiB }}"
```

```python
import chonkconf

config = chonkconf.load("app.toml")
config["cache"]["max_age"]  # 604800
```

Computed values are arithmetic only: numbers, `+ - * / // % **`, parentheses and these units:

| Units | Value |
|---|---|
| `second`, `minute`, `hour`, `day`, `week` | seconds |
| `KB`, `MB`, `GB` | bytes, powers of 1000 |
| `KiB`, `MiB`, `GiB` | bytes, powers of 1024 |

Anything else raises `chonkconf.UnsafeExpressionError`, so loading a file you didn't write can't run code on your machine.

## License

MIT
