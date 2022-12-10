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
        parser.add_argument('--verbosity', '-v', default=3, type=int,
                            help='Verbosity - 0=errors,1=info,2=verbose,3=debug')
        parser.add_argument('--attEchoVal', '-aev', default=100, type=int,
                            help='Attribute Echo value')
        parser.add_argument('--writeChanges', default=True, action='store_true',
                            help='write out changes to file')
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
        parser.add_argument('--fastAttExtract', "-fat", default=False, action='store_true',
                            help='Faster att extraction (new optimization)')
        parser.add_argument('--debugOutput', default=False, action='store_true',
                            help='Generate Debug Output')
        pa = parser.parse_args(argslist)
        print(Fore.YELLOW + "parsed args")
        print(Style.BRIGHT + Back.BLACK + "USD morph")
        print(Fore.YELLOW, f"    ifname:{Fore.CYAN}{pa.ifname}")
        print(Fore.YELLOW, f"    ofname:{Fore.CYAN}{pa.ofname}")
        print(Fore.YELLOW, f"    verbosity:{Fore.CYAN}{pa.verbosity}")
        print(Fore.YELLOW, f"    attEchoVal:{Fore.CYAN}{pa.attEchoVal}")
        print(Fore.YELLOW, f"    writeChanges:{Fore.CYAN}{pa.writeChanges}")
        print(Fore.YELLOW, f"    subXform:{Fore.CYAN}{pa.subXform}")
        print(Fore.YELLOW, f"    subShader:{Fore.CYAN}{pa.subShader}")
        print(Fore.YELLOW, f"    subGeom:{Fore.CYAN}{pa.subGeom}")
        print(Fore.YELLOW, f"    subSkelApi:{Fore.CYAN}{pa.subSkelApi}")
        print(Fore.YELLOW, f"    subStVary:{Fore.CYAN}{pa.subStVary}")
        print(Fore.YELLOW, f"    fastAttExtract:{Fore.CYAN}{pa.fastAttExtract}")
        print(Fore.YELLOW, f"    debugOutput:{Fore.CYAN}{pa.debugOutput}")
        self.parsedargs = pa
        return
