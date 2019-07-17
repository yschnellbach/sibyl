import pytest
import snake

@pytest.fixture
def cobalt():
    snake.openFile("cobalt_watchman.root")

def test_getEvent(cobalt):
    snake.getEvent(0)
