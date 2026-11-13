# chonkconf

A tiny TOML config loader with computed values.

> **A demo library.** chonkconf was built for a video about the Mistral Agents SDK, as the dependency an agent keeps up to date. Don't use it in production.

## Install

```bash
uv add "chonkconf @ git+https://github.com/megaconfidence/chonkconf" --tag v1.2.0
```

## Use it

Write a value as `"{{ ... }}"` and chonkconf computes it when the file loads:

```toml
[cache]
max_age = "{{ 7 * 24 * 60 * 60 }}"
```

```python
import chonkconf

config = chonkconf.load("app.toml")
config["cache"]["max_age"]  # 604800
```

Pass your own functions to use them in computed values:

```python
config = chonkconf.load("app.toml", functions={"days": lambda n: n * 86400})
```

```toml
[cache]
max_age = "{{ days(7) }}"
```

## License

MIT
