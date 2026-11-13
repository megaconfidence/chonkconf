import pytest

import chonkconf


def test_plain_values_pass_through():
    config = chonkconf.loads('name = "gallery"\n[server]\nport = 8080\n')
    assert config == {"name": "gallery", "server": {"port": 8080}}


def test_computed_values():
    assert chonkconf.loads('timeout = "{{ 5 * 60 }}"')["timeout"] == 300


def test_functions():
    config = chonkconf.loads('max_age = "{{ days(2) }}"', functions={"days": lambda n: n * 86400})
    assert config["max_age"] == 172800


def test_computed_values_in_arrays():
    assert chonkconf.loads('sizes = ["{{ 2 * 64 }}", 512]')["sizes"] == [128, 512]


def test_errors_name_the_key():
    with pytest.raises(chonkconf.ConfigError, match=r"cache\.max_age: could not compute"):
        chonkconf.loads('[cache]\nmax_age = "{{ weeks(2) }}"')


def test_load_reads_files(tmp_path):
    path = tmp_path / "app.toml"
    path.write_text('[cache]\nmax_age = "{{ 60 * 60 }}"\n')
    assert chonkconf.load(path) == {"cache": {"max_age": 3600}}
