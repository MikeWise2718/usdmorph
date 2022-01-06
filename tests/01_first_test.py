import pytest
import os
print(f"cwd:{os.getcwd()}")
import usdmod

dirname = os.path.dirname(__file__)


def test_pytest():
    newone = "1"
    query_newone = "1"
    assert query_newone == newone


def test_primcat():
    primcat = usdmod.PrimCat(None)
    assert primcat is not None
    linebuf = primcat.GetLineBuf()
    assert 0 == len(linebuf)
    primdict = primcat.GetPrimDict()
    assert 0 == len(primdict.items())
    primcat.extractPrimsFile("tests/first_test_data/sceneFile.usda")
    linebuf = primcat.GetLineBuf()
    assert 652 == len(linebuf)
    primdict = primcat.GetPrimDict()
    assert 17 == len(primdict.items())
