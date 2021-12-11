import argparse
import time
import datetime
from typing import Literal
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
    


class UsdPrim:
    primdict = {}
    prim_cur = None
    prim_cur_list = []


    def __init__(self):
        self.primdict = {}

    def addPrim(self,type:str,qname:str,lineidx:int,curlycount):
        uqname = self.remove_quotes(qname)
        fullname = self.get_prim_cur_path_name() + uqname
        if fullname not in self.primdict:
            entry = {}
            entry["type"] = type
            entry["qname"] = qname
            entry["uqname"] = uqname
            entry["fullname"] = fullname
            entry["endidx"] = -1
            entry["startidx"] = lineidx
            entry["curlycount"] = curlycount
            self.primdict[fullname] = entry
            self.push_prim_cur(entry)

    def remove_quotes(self,tok:str):
        tok = tok.removeprefix("'")
        tok = tok.removeprefix('"')
        tok = tok.removesuffix("'")
        tok = tok.removesuffix('"')
        return tok       

    def isquoted(self,tok:str) -> bool:
        if (len(tok)>=2):
            q1 = tok.startswith("'") and tok.endswith("'")
            if (q1):
                return True
            q2 = tok.startswith('"') and tok.endswith('"')
            if (q2):
                return True
        return False             

    def get_prim_cur_path_name(self):
        path_name = "/"
        for entry in self. prim_cur_list:
            path_name += self.remove_quotes(entry["uqname"]) + "/"
        return path_name

    def push_prim_cur(self,entry):
        self.prim_cur_list.append(entry)

    def pop_prim_cur(self):
        ln = len(self.prim_cur_list)
        if ln>0:
            entry = self.prim_cur_list[ln-1]
            self.prim_cur_list.remove(entry)

    def get_prim_cur(self):
        ln = len(self.prim_cur_list)
        if ln==0:
            return None
        return self.prim_cur_list[ln-1]

    def closePrim(self,linenum:int):
        prim_cur = self.get_prim_cur();
        if (prim_cur is not None):
            prim_cur["endidx"] = linenum
        self.pop_prim_cur()


    def extractPrims(self,linebuf:list):
        lineidx = 0
        curlycount = 0
        for line in linebuf:
            tok = tokenize(line)
            if len(tok)==0:
                lineidx += 1
                continue
            curlycount += line.count('{')
            curlycount -= line.count('}')  
            msg = f'cc:{Fore.BLUE}{curlycount} {Fore.GREEN}line:{line}'
            # print(msg)
            if tok[0]=='def':
                if len(tok)<=1:
                    ptype = "(missing type)"
                    qname = "(missing qname)"
                if self.isquoted(tok[1]):
                    ptype = "(missing type)"
                    qname = tok[1]
                else:
                    ptype = tok[1]
                    if (len(tok)<2):
                        qname = "(missing qname)"
                    else:
                        qname = tok[2]
                self.addPrim(ptype,qname,lineidx,curlycount)
            elif tok[0]=="}":
                self.closePrim(lineidx)
            lineidx += 1

    def dumpPrims(self):
        for k,v in self.primdict.items():
            msg = f'prim: type:{Fore.BLUE}{v["type"]:15}{Fore.GREEN}  from {Fore.RED}{v["startidx"]:5}{Fore.GREEN} to {Fore.RED}{v["endidx"]:5} cc:{v["curlycount"]:2} {Fore.YELLOW}{k}'
            print(Fore.GREEN,msg)

    def primFromLine(self,linenum:int)->str:
        primname = "(null)"
        mindist = 9000000
        for k,v in self.primdict.items():
            if v["startidx"]<=linenum and linenum<=v["endidx"]:
                dist = linenum-v["startidx"]
                if dist<mindist:
                    primname = v["fullname"]
                    mindist = dist
        return primname



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
    usdprim = UsdPrim()
    usdprim.extractPrims(lines)
    usdprim.dumpPrims()
    print(Fore.YELLOW,"Starting processing")
    olines = []
    linenum = 0
    for line in lines:
        toks = tokenize(line)

        primfullname = usdprim.primFromLine(linenum)
        if args.printAllDefs:
            if len(toks)>1 and toks[0]=='def':
                print(str(linenum)+Fore.MAGENTA+line.rstrip()+" "+Fore.BLUE+primfullname)

        if ofname!="" and args.subXform:
            if len(toks)>1 and toks[0]=='def' and isquoted(toks[1]):
                print(str(linenum)+Fore.RED+line.rstrip()+" "+Fore.BLUE+primfullname)
                nline = insertXform(line)
                print(str(linenum)+Fore.MAGENTA+nline.rstrip()+" "+Fore.BLUE+primfullname)
                line = nline

        if ofname!="" and args.subXform:
            olines.append(line)
        linenum += 1

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