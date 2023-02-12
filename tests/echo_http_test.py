import pytest
import json
import requests
from src import config
BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1")

def test_echo_http(clear):
    echo_val = 5
    echo_response = requests.get(f"{BASE_URL}/echo?data={echo_val}")
    assert echo_response.status_code == 200
    echo_data = json.loads(echo_response.text)
    assert echo_data['data'] == '5'


def test_echo_fail(clear):
    echo_val = "echo"
    echo_response = requests.get(f"{BASE_URL}/echo?data={echo_val}")
    assert echo_response.status_code == 400
