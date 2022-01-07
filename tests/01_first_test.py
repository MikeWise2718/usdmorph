import os
from argparse import ArgumentParser

import usdmod

# print(f"cwd:{os.getcwd()}")

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


def test_morpher():
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

    morpher = usdmod.Morpher(None)
    (olines, _) = morpher.morphLinesIntoLists(primcat)
    assert olines is not None
    assert 0 == len(olines)
    assert 0 == morpher.nXformChanges
    assert 0 == morpher.nShaderChanges
    assert 0 == morpher.nSkelApiChanges
    assert 0 == morpher.nVaryingChanges
    assert 0 == morpher.nSkelChanges

    args = ["--ofname", "test.out.usda"]
    parsedargs: ArgumentParser = usdmod.MorphArgParser(args).parsedargs
    morpher = usdmod.Morpher(parsedargs)
    (olines, _) = morpher.morphLinesIntoLists(primcat)
    assert olines is not None
    assert 652 == len(olines)
    assert 3 == morpher.nXformChanges
    assert 0 == morpher.nShaderChanges
    assert 0 == morpher.nSkelApiChanges
    assert 0 == morpher.nVaryingChanges
    assert 0 == morpher.nSkelChanges    


def test_morpherwithhuman():
    args = ["--ifname", "tests/h56data/Human-0056.usda", "--ofname", "tests/h56data/Human-0056.out.usda"]
    parsedargs: ArgumentParser = usdmod.MorphArgParser(args).parsedargs
    primcat = usdmod.PrimCat(parsedargs)
    primcat.extractPrimsFile(parsedargs.ifname)
    linebuf = primcat.GetLineBuf()
    assert 1139 == len(linebuf)
    primdict = primcat.GetPrimDict()
    assert 57 == len(primdict.items())
    morpher = usdmod.Morpher(parsedargs)
    (olines, _) = morpher.morphLinesIntoLists(primcat)
    assert olines is not None
    assert 1139 == len(olines)
    assert 30 == morpher.nXformChanges
    assert 1 == morpher.nShaderChanges
    assert 2 == morpher.nSkelChanges
    assert 14 == morpher.nSkelApiChanges
    assert 14 == morpher.nVaryingChanges
