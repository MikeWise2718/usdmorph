from argparse import ArgumentParser
import time
import datetime
import colorama
from colorama import Fore, Back, Style
import usdmod

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
    return args


args = parseargs()



if (args.ifname == ""):
    print("error - no name specified")
else:
    # lines = initbuffer(args.ifname)
    primcat = usdmod.PrimCat(args)
    # primcat.extractPrims(lines)
    primcat.extractPrimsFile(args.ifname)
    primcat.dumpPrims()

    morpher = usdmod.Morpher(args)
    (olines, dblines) = morpher.morphLines(primcat)

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
