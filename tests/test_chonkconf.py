import pytest

import chonkconf


def test_plain_values_pass_through():
    config = chonkconf.loads('name = "gallery"\n[server]\nport = 8080\n')
    assert config == {"name": "gallery", "server": {"port": 8080}}


def test_computed_values():
    assert chonkconf.loads('timeout = "{{ 5 * 60 }}"')["timeout"] == 300


def test_units():
    config = chonkconf.loads(
        'max_age = "{{ 7 * day }}"\nmax_size = "{{ 25 * MiB }}"\nlimit = "{{ 2 * MB }}"\n'
    )
    assert config == {"max_age": 604800, "max_size": 26214400, "limit": 2000000}


def test_computed_values_in_arrays():
    assert chonkconf.loads('sizes = ["{{ 2 * 64 }}", 512]')["sizes"] == [128, 512]


def test_errors_name_the_key():
    with pytest.raises(chonkconf.ConfigError, match=r"cache\.max_age: could not compute"):
        chonkconf.loads('[cache]\nmax_age = "{{ 1 / 0 }}"')


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('id')",
        "open('/etc/passwd').read()",
        "().__class__.__bases__[0].__subclasses__()",
        "days(7)",
        "'a' * 3",
        "True + 1",
        "10 ** 1000",
    ],
)
def test_anything_but_arithmetic_is_refused(expression):
    with pytest.raises(chonkconf.UnsafeExpressionError):
        chonkconf.loads(f'x = "{{{{ {expression} }}}}"')


def test_the_functions_option_is_gone():
    with pytest.raises(TypeError):
        chonkconf.loads("x = 1", functions={"days": lambda n: n * 86400})


def test_load_reads_files(tmp_path):
    path = tmp_path / "app.toml"
    path.write_text('[cache]\nmax_age = "{{ hour }}"\n')
    assert chonkconf.load(path) == {"cache": {"max_age": 3600}}
