from argparse import ArgumentParser
import time
import datetime
import colorama
from colorama import Fore, Back, Style
from usdprim import UsdPrim


colorama.init()
starttime = time.time()
startdaytime = datetime.datetime.now()
print(Fore.YELLOW + f"Starting usdmorph at:{startdaytime}")


def parseargs():
    parser = ArgumentParser(description='USD Morph')
    parser.add_argument('--ifname', default="",
                        help='the input USD file name')
    parser.add_argument('--ofname', default="",
                        help='the output USD file name - default has -out appended to name')
    parser.add_argument('--verbosity', '-v', default=3,
                        help='Verbosity - 0=errors,1=info,2=verbose,3=debug')
    parser.add_argument('--subXform', default=True, action='store_false',
                        help='sub empty Prim Templates with Xform if they have a xFormOp:transform attribute')
    parser.add_argument('--subShader', default=True, action='store_false',
                        help='sub empty Prim Templates with Shader if they have an input:diffuse attribute or the right name')
    parser.add_argument('--subGeom', default=True, action='store_false',
                        help='sub empty Geom Templates the right name')
    parser.add_argument('--subSkelApi', default=True, action='store_false',
                        help='add SkelApi prefex to meshs in SkelRoots')
    parser.add_argument('--subStVary', default=True, action='store_false',
                        help='make st coordinates varying when declared as constant to meshs in SkelRoots')
    parser.add_argument('--printAllDefs', default=False, action='store_true',
                        help='sub empty Prim Templates with Xform')
    parser.add_argument('--debugOutput', default=False, action='store_true',
                        help='Generate Debug Output')
    args = parser.parse_args()
    print(Fore.YELLOW + "parsed args")
    return args


args = parseargs()


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


def morphLines(lines: list[str], primcat: UsdPrim):
    global args
    print(Fore.YELLOW, "Starting usd procssing" + Fore.BLUE)

    ofname = args.ofname
    verb = args.verbosity

    olines = []
    lineidx = 0
    nXformChanges = 0
    nShaderChanges = 0
    nSkelChanges = 0
    nSkelApiChanges = 0
    nVaryingChanges = 0
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
            if args.printAllDefs:
                print(str(lineidx) + Fore.MAGENTA + line.rstrip() + " " + Fore.BLUE + primKeyName)

            if ofname != "":
                if ptype == "(ptype missing)":
                    if verb >= 3:
                        print(str(lineidx), ": " + Fore.RED + line.rstrip() + " " + Fore.BLUE + primKeyName)
                    if args.subShader and primcat.hasAttribute(primKeyName, "inputs:diffuseColor"):
                        nline = insertPtype(line, "Shader")
                        prim["ptype"] = "Shader"
                        nShaderChanges += 1
                        if verb > 2:
                            print(str(lineidx), ": " + Fore.MAGENTA + nline.rstrip() + " " + Fore.BLUE + primKeyName)
                    elif args.subShader and primcat.hasBasename(primKeyName, "PreviewSurface"):
                        nline = insertPtype(line, "Shader")
                        prim["ptype"] = "Shader"
                        nShaderChanges += 1
                        if verb > 2:
                            print(str(lineidx), ": " + Fore.MAGENTA + nline.rstrip() + " " + Fore.BLUE + primKeyName)
                    elif args.subGeom and primcat.hasBasename(primKeyName, "Reference"):
                        nline = insertPtype(line, "Skeleton")
                        prim["ptype"] = "Skeleton"
                        nSkelChanges += 1
                        if verb > 2:
                            print(str(lineidx), ": " + Fore.MAGENTA + nline.rstrip() + " " + Fore.BLUE + primKeyName)
                    elif args.subGeom and primcat.hasBasenameSuffix(primKeyName, "_Clone_"):
                        nline = insertPtype(line, "SkelRoot")
                        prim["ptype"] = "SkelRoot"
                        nSkelChanges += 1
                        if verb > 2:
                            print(str(lineidx), ": " + Fore.MAGENTA + nline.rstrip() + " " + Fore.BLUE + primKeyName)
                    elif args.subXform and primcat.hasAttribute(primKeyName,"transform"):
                        nline = insertPtype(line, "Xform")
                        prim["ptype"] = "Xform"
                        nXformChanges += 1
                        if verb > 2:
                            print(str(lineidx), ": " + Fore.MAGENTA + nline.rstrip() + " " + Fore.BLUE + primKeyName)
                elif ptype == "Mesh" and args.subSkelApi and primcat.hasParentPrimOfPtype(prim, "SkelRoot"):
                    nline = appendSkelApiRef(line)
                    nSkelApiChanges += 1
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
                    nVaryingChanges += 1
                if lineidx - primvarst_triggerlineidx > 4:
                    primvarst_triggerd = False
                    primvarst_triggerlineidx = 0

        if ofname != "" and args.subXform:
            olines.append(nline)

        lineidx += 1

    print(f"Changes: Xform:{nXformChanges} Shader:{nShaderChanges} Skel:{nSkelChanges} SkelApi:{nSkelApiChanges} Varying:{nVaryingChanges}")

    return olines, primcat.dboutlines


print(Style.BRIGHT + Back.BLACK + "USD morph")
print(Fore.YELLOW, f"    ifname:{args.ifname}")
print(Fore.YELLOW, f"    ofname:{args.ofname}")
print(Fore.YELLOW, f"    verbosity:{args.verbosity}")
print(Fore.YELLOW, f"    subXform:{args.subXform}")
print(Fore.YELLOW, f"    subShader:{args.subShader}")
print(Fore.YELLOW, f"    subGeom:{args.subGeom}")
print(Fore.YELLOW, f"    subSkelApi:{args.subSkelApi}")
print(Fore.YELLOW, f"    subStVary:{args.subStVary}")
print(Fore.YELLOW, f"    debugOutput:{args.debugOutput}")

if (args.ifname == ""):
    print("error - no name specified")
else:
    lines = initbuffer(args.ifname)
    usdprim = UsdPrim(args)
    usdprim.extractPrims(lines)
    usdprim.dumpPrims()
    (olines, dblines) = morphLines(lines, usdprim)

    if args.ofname != "":
        with open(args.ofname, "w") as file:
            file.writelines(olines)
        print(f"{Fore.WHITE}Wrote {len(olines)} lines to {Fore.YELLOW}{args.ofname}" )

    if args.debugOutput:
        sep = "\n"
        newlines = sep.join(dblines)
        with open("dbout.ansi", "w") as file:
            file.writelines(newlines)


elap = time.time() - starttime
print(Fore.BLUE + f"main execution took {elap:.2f} secs")
