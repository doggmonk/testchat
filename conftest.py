import pytest
from selenium import webdriver

from config import conf


@pytest.fixture(scope='session')
def driver():
    with webdriver.Chrome() as drv:
        yield drv


@pytest.fixture(scope='session')
def conf_data():
    return conf
