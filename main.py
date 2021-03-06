from argparse import ArgumentParser
import time
import sys
import datetime
import colorama
from colorama import Fore
import usdmod

colorama.init()
starttime = time.time()
startdaytime = datetime.datetime.now()
print(Fore.YELLOW + f"Starting usdmorph at:{startdaytime}")


parsedargs: ArgumentParser = usdmod.MorphArgParser(sys.argv[1:]).parsedargs


if (parsedargs.ifname == ""):
    print("error - no name specified")
else:
    primcat = usdmod.PrimCat(parsedargs)
    primcat.extractPrimsFile(parsedargs.ifname)
    primcat.dumpPrims()

    morpher = usdmod.Morpher(parsedargs)
    morpher.morphLines(primcat)


elap = time.time() - starttime
print(Fore.BLUE + f"main execution took {elap:.2f} secs")
