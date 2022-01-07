from argparse import ArgumentParser
from colorama import Fore, Back, Style


class MorphArgParser:

    parsedargs = None

    def __init__(self, argslist):
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
        pa = parser.parse_args(argslist)
        print(Fore.YELLOW + "parsed args")
        print(Style.BRIGHT + Back.BLACK + "USD morph")
        print(Fore.YELLOW, f"    ifname:{pa.ifname}")
        print(Fore.YELLOW, f"    ofname:{pa.ofname}")
        print(Fore.YELLOW, f"    verbosity:{pa.verbosity}")
        print(Fore.YELLOW, f"    subXform:{pa.subXform}")
        print(Fore.YELLOW, f"    subShader:{pa.subShader}")
        print(Fore.YELLOW, f"    subGeom:{pa.subGeom}")
        print(Fore.YELLOW, f"    subSkelApi:{pa.subSkelApi}")
        print(Fore.YELLOW, f"    subStVary:{pa.subStVary}")
        print(Fore.YELLOW, f"    debugOutput:{pa.debugOutput}")
        self.parsedargs = pa
        return
