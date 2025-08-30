import pytest
from spypointapi.client import SpypointApi


def test_client_constructor():
    c = SpypointApi("e", "p")
    assert c is not None
