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
                        help='sub empty Prim Templates with Xform if they have a xFormOp:transform attribute')
    parser.add_argument('--subShader',default=True,action='store_false',
                        help='sub empty Prim Templates with Shader if they have an input:diffuse attribute')
    parser.add_argument('--printAllDefs',default=False,action='store_true',
                        help='sub empty Prim Templates with Xform')
    args = parser.parse_args() 
    print(Fore.YELLOW+"parsed args")
    return args

args = parseargs()
    

usdattlist = [
"xformOp:transform", "xformOpOrder", "transform","translate","scale","rotate",
"inputs:diffuseColor"
]

class UsdPrim:
    # USD Home page - https://graphics.pixar.com/usd
    # Terms and Concepts - https://graphics.pixar.com/usd/release/glossary.html  
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
            entry["startidx"] = lineidx
            entry["endidx"] = -1
            entry["curlycount"] = curlycount
            entry["attributes"] = {}
            self.primdict[fullname] = entry
            self.push_prim_cur(entry)

    def extractAttsForPrim(self,primfullname,lines):
        entry = self.primdict.get(primfullname)
        if entry==None:
            print(f"Error in extractAttsForPrim {primfullname} not in primdict")
            return
        ifr = entry["startidx"]
        ito = entry["endidx"]
        for idx in range(ifr+1,ito+1):
            # we have to skip over embedded prims
            pfn = self.primFromLine(idx)
            if pfn==primfullname:
                line = lines[idx]
                fore = ""
                aft = ""
                sarr = line.split("=")
                if (len(sarr)>=1):
                    fore = sarr[0];
                if (len(sarr)>=2):
                    aft = sarr[1];
                for attname in usdattlist:
                    if attname in fore:
                        self.addAttribute(entry,attname,fore,aft)
    
    def addAttribute(self,entry,attname:str,fore:str,aft:str):
        attdict = entry["attributes"]
        attdict[attname] = {"name":attname,"fore":fore,"aft":aft}

    def hasAttribute(self,primfullname:str,attname:str)->bool:
        entry = self.primdict.get(primfullname)
        if entry==None:
            print(f"Error in hasAttribute {primfullname} not in primdict")
            return False
        rv = attname in entry["attributes"]
        return rv

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

    def extractRawPrim(self,line:str):
        tok = line.split() # whitespace split
        isprim = False
        ptype = "(ptype undefined)"
        qname = "(qname undefined)"
        if len(tok)>0 and tok[0]=='def':
            isprim = True
            if len(tok)<=1:
                ptype = "(ptype missing)"
                qname = "(qname missing)"
            if self.isquoted(tok[1]):
                ptype = "(ptype missing)"
                qname = tok[1]
            else:
                ptype = tok[1]
                if (len(tok)<2):
                    qname = "(qname missing)"
                else:
                    qname = tok[2]        
        return (isprim,ptype,qname)

    def extractPrims(self,linebuf:list):
        lineidx = 0
        curlycount = 0
        triggercc = 0
        for line in linebuf:
            curlycount += line.count('{')
            curlycount -= line.count('}')  
            msg = f'cc:{Fore.BLUE}{curlycount} {Fore.GREEN}line:{line}'
            (isprim,ptype,qname) = self.extractRawPrim(line)
            if isprim:
                self.addPrim(ptype,qname,lineidx,curlycount)
                triggercc = curlycount
            elif curlycount<=triggercc:
                 self.closePrim(lineidx)
                 cp = self.get_prim_cur()
                 triggercc = curlycount
            lineidx += 1

        for  k,v in self.primdict.items():
            self.extractAttsForPrim(k,linebuf)

        

    def dumpPrims(self):
        for k,v in self.primdict.items():
            msg = f'prim: type:{Fore.BLUE}{v["type"]:15}{Fore.GREEN}  from {Fore.RED}{v["startidx"]:5}{Fore.GREEN} to {Fore.RED}{v["endidx"]:5} cc:{v["curlycount"]:2} {Fore.YELLOW}{k}'
            print(Fore.GREEN,msg)
            atts = v["attributes"]
            if len(atts)==0:
                print(Fore.CYAN,"  no attributes")
            for k,v in atts.items():
                msg = f'  {v["name"]}    -  {v["fore"]}'
                print(Fore.BLUE,msg)

        print(Fore.BLUE,f"Found {len(self.primdict)} prims")

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
    print(Fore.BLUE,f"read {len(lines)} lines")
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

def insertShader(iline:str) -> str:
    rv = iline.replace("def","def Shader")
    return rv    

def morphLines(ifname:str,ofname:str):
    global args
    print(Fore.YELLOW,"Starting usd procssing"+Fore.BLUE)
    lines = initbuffer(ifname)
    usdprim = UsdPrim()
    usdprim.extractPrims(lines)
    usdprim.dumpPrims()
    olines = []
    linenum = 0
    print(Fore.YELLOW,"Starting morphing"+Fore.BLUE)
    for line in lines:
        primfullname = usdprim.primFromLine(linenum)
        (isprim,ptype,qname) = usdprim.extractRawPrim(line)

        nline = line
        if isprim:
            if args.printAllDefs:
                print(str(linenum)+Fore.MAGENTA+line.rstrip()+" "+Fore.BLUE+primfullname)

            if ofname!="" and ptype=="(ptype missing)":
                print(str(linenum),": "+Fore.RED+line.rstrip()+" "+Fore.BLUE+primfullname)
                if args.subXform:
                    if usdprim.hasAttribute(primfullname,"transform"):
                        nline = insertXform(line)
                        print(str(linenum),": "+Fore.MAGENTA+nline.rstrip()+" "+Fore.BLUE+primfullname)
                if args.subShader:
                    if usdprim.hasAttribute(primfullname,"input:diffuse"):
                        nline = insertShader(line)
                        print(str(linenum),": "+Fore.MAGENTA+nline.rstrip()+" "+Fore.BLUE+primfullname)

        if ofname!="" and args.subXform:
            olines.append(nline)

        linenum += 1

    if ofname!="":
        with open(ofname,"w") as file:
            file.writelines(olines)
        print(f"wrote {len(olines)} to {ofname}")


print(f"USD morph")

if (args.ifname==""):
    print(f"error - no name specified")
else:
    morphLines(args.ifname,args.ofname)    

elap = time.time() - starttime
print(Fore.BLUE+f"main execution took {elap:.2f} secs")