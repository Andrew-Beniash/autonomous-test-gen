import pytest
from src.core.config import Config

def test_config_loads_environment_variables():
    config = Config()
    assert config.database_url is not None
    assert config.mongodb_url is not None
    assert config.secret_key is not None

def test_config_validates_required_variables():
    with pytest.raises(ValueError):
        Config(database_url=None)