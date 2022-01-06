from argparse import ArgumentParser
import colorama
from colorama import Fore
colorama.init()
from .primcat import PrimCat

usdattlist = [
    "xformOp:transform", "xformOpOrder", "transform", "translate", "scale", "rotate",
    "inputs:diffuseColor"
]


def initbuffer(usdfname: str):
    with open(usdfname) as file:
        lines = file.readlines()
    print(Fore.BLUE, f"read {len(lines)} lines")
    return lines


def tokenize(line: str):
    toks = line.split()
    return toks


def isquoted(tok: str) -> bool:
    if (len(tok) >= 2):
        q1 = tok.startswith("'") and tok.endswith("'")
        if q1:
            return True
        q2 = tok.startswith('"') and tok.endswith('"')
        if q2:
            return True
    return False


def insertPtype(iline: str, ptype: str) -> str:
    rv = iline.replace("def", f"def {ptype}")
    return rv


def appendSkelApiRef(iline: str) -> str:
    rv = iline.strip() + '( prepend apiSchemas = ["SkelBindingAPI"] )\n'
    return rv


class Morpher:
    nXformChanges = 0
    nShaderChanges = 0
    nSkelChanges = 0
    nSkelApiChanges = 0
    nVaryingChanges = 0
    args = None

    printAllDefs = False
    subShader = False
    subGeom = False
    subXform = False
    subSkelApi = False
    ofname = ""
    verbosity = 0

    def __init__(self, args: ArgumentParser):
        self.args = args
        if args is not None:
            self.printAllDefs = args.printAllDefs
            self.subShader = args.subShader
            self.subGeom = args.subGeom
            self.subXform = args.subXform
            self.subSkelApi = args.subSkelApi
            self.ofname = args.ofname
            self.verbosity = args.verbosity

    def morphLines(self, primcat: PrimCat):
        print(Fore.YELLOW, "Starting usd procssing" + Fore.BLUE)

        lines = primcat.GetLineBuf()
        verb = self.verbosity

        olines = []
        lineidx = 0
        self.nXformChanges = 0
        self.nShaderChanges = 0
        self.nSkelChanges = 0
        self.nSkelApiChanges = 0
        self.nVaryingChanges = 0
        print(Fore.YELLOW, "Starting morphing" + Fore.BLUE)
        primvarst_triggerd = False
        primvarst_triggerlineidx = 0
        for line in lines:
            (primKeyName, prim) = primcat.primFromLine(lineidx)
            (isprim, ptype, qname) = primcat.extractRawPrim(line, lineidx)

            if lineidx == 220:
                pass

            nline = line
            if isprim:
                if self.printAllDefs:
                    print(str(lineidx) + Fore.MAGENTA + line.rstrip() + " " + Fore.BLUE + primKeyName)

                if self.ofname != "":
                    if ptype == "(ptype missing)":
                        if verb >= 3:
                            print(str(lineidx), ": " + Fore.RED + line.rstrip() + " " + Fore.BLUE + primKeyName)
                        if self.subShader and primcat.hasAttribute(primKeyName, "inputs:diffuseColor"):
                            nline = insertPtype(line, "Shader")
                            prim["ptype"] = "Shader"
                            self.nShaderChanges += 1
                            if verb > 2:
                                print(str(lineidx), ": " + Fore.MAGENTA + nline.rstrip() + " " + Fore.BLUE + primKeyName)
                        elif self.subShader and primcat.hasBasename(primKeyName, "PreviewSurface"):
                            nline = insertPtype(line, "Shader")
                            prim["ptype"] = "Shader"
                            self.nShaderChanges += 1
                            if verb > 2:
                                print(str(lineidx), ": " + Fore.MAGENTA + nline.rstrip() + " " + Fore.BLUE + primKeyName)
                        elif self.subGeom and primcat.hasBasename(primKeyName, "Reference"):
                            nline = insertPtype(line, "Skeleton")
                            prim["ptype"] = "Skeleton"
                            self.nSkelChanges += 1
                            if verb > 2:
                                print(str(lineidx), ": " + Fore.MAGENTA + nline.rstrip() + " " + Fore.BLUE + primKeyName)
                        elif self.subGeom and primcat.hasBasenameSuffix(primKeyName, "_Clone_"):
                            nline = insertPtype(line, "SkelRoot")
                            prim["ptype"] = "SkelRoot"
                            self.nSkelChanges += 1
                            if verb > 2:
                                print(str(lineidx), ": " + Fore.MAGENTA + nline.rstrip() + " " + Fore.BLUE + primKeyName)
                        elif self.subXform and primcat.hasAttribute(primKeyName, "transform"):
                            nline = insertPtype(line, "Xform")
                            prim["ptype"] = "Xform"
                            self.nXformChanges += 1
                            if verb > 2:
                                print(str(lineidx), ": " + Fore.MAGENTA + nline.rstrip() + " " + Fore.BLUE + primKeyName)
                    elif ptype == "Mesh" and self.subSkelApi and primcat.hasParentPrimOfPtype(prim, "SkelRoot"):
                        nline = appendSkelApiRef(line)
                        self.nSkelApiChanges += 1
                        if verb > 2:
                            print(str(lineidx), ": " + Fore.CYAN + nline.rstrip() + " " + Fore.BLUE + primKeyName)
            else:
                if not primvarst_triggerd:
                    if line.find("primvars:st") >= 0:
                        if primcat.hasParentPrimOfPtype(prim, "SkelRoot"):
                            primvarst_triggerd = True
                            primvarst_triggerlineidx = lineidx
                else:
                    if line.find('interpolation = "constant"') >= 0:
                        nline = line.replace("constant", "varying")
                        self.nVaryingChanges += 1
                    if lineidx - primvarst_triggerlineidx > 4:
                        primvarst_triggerd = False
                        primvarst_triggerlineidx = 0

            if self.ofname != "" and self.subXform:
                olines.append(nline)

            lineidx += 1

        msg = f"Changes: Xform:{self.nXformChanges} Shader:{self.nShaderChanges} Skel:{self.nSkelChanges} SkelApi:{self.nSkelApiChanges} Varying:{self.nVaryingChanges}"

        print(msg)

        return olines, primcat.dboutlines
