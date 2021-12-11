import argparse
import time
import datetime
import colorama
from colorama import Fore, Back, Style
colorama.init()
starttime = time.time()
startdaytime = datetime.datetime.now()
print(Fore.YELLOW+f"Starting usdmorph at:{startdaytime}")

def parseargs():
    parser = argparse.ArgumentParser(description='USD Morph')
    parser.add_argument('--ifname',default="",
                        help='the input USD file name')
    parser.add_argument('--ofname',default="",
                        help='the output USD file name - default has -out appended to name')
    parser.add_argument('--buffer',
                        help='buffer the lines before processing')
    parser.add_argument('--subXform',default=True,action='store_false',
                        help='sub empty Prim Templates with Xform')
    parser.add_argument('--printAllDefs',default=False,action='store_true',
                        help='sub empty Prim Templates with Xform')
    args = parser.parse_args() 
    print(Fore.YELLOW+"parsed args")
    return args

args = parseargs()
    

primdict = {}
prim_cur = None
def initPrimList():
    primdict = {}

def addPrim(type:str,qname:str,lineidx:int):
    global primdict,prim_cur
    fullname = qname
    if fullname not in primdict:
        entry = {}
        entry["type"] = type
        entry["qname"] = qname
        entry["fullname"] = fullname
        entry["endidx"] = -1
        entry["startidx"] = lineidx
        primdict[fullname] = entry
        prim_cur = entry

def closePrim(linenum:int):
    global primdict,prim_cur
    if (prim_cur is not None):
        prim_cur["endidx"] = linenum



def extractPrims(linebuf:list):
    global primdict,prim_cur
    lineidx = 0
    for line in linebuf:
        tok = tokenize(line)
        if len(tok)==0:
            continue
        if tok[0]=='def': 
            if len(tok)<=1:
                addPrim("(missing type)","(missing qname)",lineidx)
            if isquoted(tok[1]):
                addPrim("(missing type)",tok[1],lineidx)
            else:
                if (len(tok)<2):
                    qname = "(missing qname)"
                else:
                    qname = tok[2]
                addPrim(tok[1],qname,lineidx)
        elif tok[0]=="}":
            closePrim(lineidx)
        lineidx += 1

def dumpPrims():
    global primdict,prim_cur
    for k,v in primdict.items():
        msg = f'prim - fullname:{k} type:{v["type"]}  qname:{v["qname"]}from {v["startidx"]} to {v["endidx"]}'
        print(Fore.GREEN,msg)



def initbuffer(usdfname:str):
    with open(usdfname) as file:
        lines = file.readlines()
    print(f"read {len(lines)} lines")
    return lines

def tokenize(line:str):
    toks = line.split()
    return toks

def isquoted(tok:str) -> bool:
    if (len(tok)>=2):
        q1 = tok.startswith("'") and tok.endswith("'")
        if (q1):
            return True
        q2 = tok.startswith('"') and tok.endswith('"')
        if (q2):
            return True
    return False

def insertXform(iline:str) -> str:
    rv = iline.replace("def","def Xform")
    return rv


def dowork(ifname:str,ofname:str):
    global args
    lines = initbuffer(ifname)
    extractPrims(lines)
    dumpPrims()
    print(Fore.YELLOW,"Starting processing")
    olines = []
    for line in lines:
        toks = tokenize(line)

        if args.printAllDefs:
            if len(toks)>1 and toks[0]=='def':
                print(line.rstrip())

        if ofname!="" and args.subXform:
            if len(toks)>1 and toks[0]=='def' and isquoted(toks[1]):
                print(line.rstrip())
                nline = insertXform(line)
                print(nline.rstrip())
                line = nline

        if ofname!="" and args.subXform:
            olines.append(line)

    if ofname!="":
        with open(ofname,"w") as file:
            file.writelines(olines)
        print(f"wrote {len(olines)} to {ofname}")
    

print(f"USD morph")

if (args.ifname==""):
    print(f"error - no name specified")
else:
    dowork(args.ifname,args.ofname)    

elap = time.time() - starttime
print(Fore.BLUE+f"main execution took {elap:.2f} secs")