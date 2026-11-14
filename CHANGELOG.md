# Changelog

## 2.0.0 (security fix)

**Security fix (critical).** Up to 1.2.0, chonkconf computed `"{{ ... }}"` values with Python's `eval()`, so a config file you didn't write could run any code on your machine:

```toml
name = "Totally normal theme"
oops = "{{ __import__('os').system('id') }}"
```

Version 2.0.0 computes `{{ }}` values with a small arithmetic evaluator instead. There is no fix for 1.x: upgrade to 2.0.0. Details: [security advisories](https://github.com/megaconfidence/chonkconf/security/advisories).

### Breaking changes

- `{{ }}` values can only use numbers, `+ - * / // % **`, parentheses and the built-in units below. Anything else raises `chonkconf.UnsafeExpressionError`.
- The `functions=` option of `load()` and `loads()` is removed. Use the built-in units, or compute the value in your own code after loading.

| Units | Value |
|---|---|
| `second`, `minute`, `hour`, `day`, `week` | seconds |
| `KB`, `MB`, `GB` | bytes, powers of 1000 |
| `KiB`, `MiB`, `GiB` | bytes, powers of 1024 |

### Upgrading from 1.x

1. Remove `functions=` from your `load()` and `loads()` calls.
2. Rewrite the function calls in your config files with units:

| 1.x, with your own function | 2.0 |
|---|---|
| `"{{ days(7) }}"` | `"{{ 7 * day }}"` |
| `"{{ hours(12) }}"` | `"{{ 12 * hour }}"` |
| `"{{ megabytes(25) }}"`, where a megabyte is 1024 * 1024 bytes | `"{{ 25 * MiB }}"` |
| `"{{ megabytes(25) }}"`, where a megabyte is 1,000,000 bytes | `"{{ 25 * MB }}"` |

## 1.2.0

- A computed value that fails raises `chonkconf.ConfigError`, and the message names its key: `cache.max_age: could not compute ...`.

## 1.1.0

- Computed values work inside arrays too: `sizes = ["{{ 2 * 64 }}", 512]`.

## 1.0.0

- First release: `load()` and `loads()` read TOML and compute `"{{ ... }}"` values, with your own `functions=`.
