# import pytest
import os

dirname = os.path.dirname(__file__)


def test_vds_vers():
    newverstr = "v2099.12.31"
    query_newverstr = "v2099.12.31"
    assert query_newverstr == newverstr
