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
    parser.add_argument('--verbosity','-v',default=3,
                        help='Verbosity - 0=errors,1=info,2=verbose,3=debug')   
    parser.add_argument('--subXform',default=True,action='store_false',
                        help='sub empty Prim Templates with Xform if they have a xFormOp:transform attribute')
    parser.add_argument('--subShader',default=True,action='store_false',
                        help='sub empty Prim Templates with Shader if they have an input:diffuse attribute or the right name')
    parser.add_argument('--subGeom',default=True,action='store_false',
                        help='sub empty Geom Templates the right name')
    parser.add_argument('--printAllDefs',default=False,action='store_true',
                        help='sub empty Prim Templates with Xform')
    parser.add_argument('--debugOutput',default=False,action='store_true',
                        help='Generate Debug Output')
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
    fullnamedict = {}
    prim_cur = None
    prim_cur_list = []
    dboutlines = []
    seenbeforecount = 0
    verbosity = 3

    def __init__(self,verb=3):
        self.primdict = {}
        self.verbosity = verb

    def registerFullName(self,fullname:str)->int:
        if fullname not in self.fullnamedict:
            self.fullnamedict[fullname] = 1
        else:
            self.fullnamedict[fullname] += 1
        return self.fullnamedict[fullname]



    def addPrim(self,ptype:str,qname:str,lineidx:int,curlycount):
        uqname = self.remove_quotes(qname)
        if lineidx==6385:
            pass
        if lineidx==4048:
            pass        
        fullname = self.get_prim_cur_path_name() + uqname
        icnt = self.registerFullName(fullname)
        basekeyname = f"{uqname}.{icnt}"
        keyname = f"{fullname}.{icnt}"
        notseenbefore = fullname not in self.primdict
        if notseenbefore:
            entry = {}
            entry["ptype"] = ptype
            entry["qname"] = qname
            entry["uqname"] = uqname
            entry["basename"] = uqname
            entry["fullname"] = fullname
            entry["keyname"] = keyname
            entry["basekeyname"] = basekeyname
            entry["instance_count"] = icnt
            entry["startidx"] = lineidx
            entry["endidx"] = -1
            entry["curlycount"] = curlycount
            entry["attributes"] = {}
            self.primdict[keyname] = entry
            self.push_prim_cur(entry)
        else:
            msg = f"{Fore.RED}seenbefore:{fullname} cnt:{icnt}"
            print(msg)
            self.dboutlines.append(msg)
            self.seenbeforecount += 1


    def getParentPrim(self,entry):
        fullname = entry["keyname"]
        newend = fullname.rfind("/")
        if newend<0:
            return None
        pfullname = fullname[:newend]
        pentry = self.primdict.get(pfullname)
        if pentry is not None:
            pass
        return pentry

    def hasParentPrimOfPtype(self,entry,ptype:str) -> bool:
        pentry = entry
        maxiter = 100
        iter = 0
        while pentry is not None:
            if pentry["ptype"] == ptype:
                return True
            pentry = self.getParentPrim(pentry)
            if iter>maxiter:
                print(f"MaxIter of {maxiter} exceeded in hasParerntPrimOfPtype:{ptype}")
                return False
            iter += 1
        return False

    def closePrim(self,linenum:int):
        prim_cur = self.get_prim_cur()
        if (prim_cur is not None):
            prim_cur["endidx"] = linenum
        self.pop_prim_cur()            

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
                    fore = sarr[0]
                if (len(sarr)>=2):
                    aft = sarr[1]
                if primfullname=="/Human_0064/Materials/Man001_color_28332/PreviewSurface":
                    pass
                for attname in usdattlist:
                    if attname in fore:
                        self.addAttribute(entry,attname,fore,aft)
    
    def addAttribute(self,entry,attname:str,fore:str,aft:str):
        attdict = entry["attributes"]
        attdict[attname] = {"attname":attname,"fore":fore,"aft":aft}

    def hasAttribute(self,primfullname:str,attname:str)->bool:
        entry = self.primdict.get(primfullname)
        if entry==None:
            print(f"Error in hasAttribute {primfullname} not in primdict")
            return False
        rv = attname in entry["attributes"]
        return rv

    def hasBasename(self,primfullname:str,qname:str)->bool:
        entry = self.primdict.get(primfullname)
        if entry==None:
            print(f"Error in hasBasename {primfullname} not in primdict")
            return False
        rv = entry["basename"]==qname
        return rv        

    def hasBasenameSuffix(self,primfullname:str,qnamesuffix:str)->bool:
        entry = self.primdict.get(primfullname)
        if entry==None:
            print(f"Error in hasBasenameSuffix {primfullname} not in primdict")
            return False
        rv = entry["basename"].endswith(qnamesuffix)
        if rv:
            pass
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
            path_name += self.remove_quotes(entry["basekeyname"]) + "/"
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



    def extractRawPrim(self,line:str,lineidx:int):
        tok = line.split() # whitespace split
        if lineidx==645:
            pass
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

    def extractPrims(self,linebuf:list,dbout:bool):
        lineidx = 0
        curlycount = 0
        triggercc = 0
        for line in linebuf:
            curlycount += line.count('{')
            curlycount -= line.count('}')  
            msg = f'{Fore.WHITE}{lineidx:5} {Fore.BLUE}cc:{curlycount} {Fore.YELLOW}"{line.strip()[:60]}"'
            if dbout:
                print(msg)
                self.dboutlines.append(msg)
            (isprim,ptype,qname) = self.extractRawPrim(line,lineidx)
            if isprim:
                self.addPrim(ptype,qname,lineidx,curlycount)
                triggercc = curlycount
                if dbout:
                   msg = f'{Fore.BLUE}Add Prim:{qname} idx:{lineidx}'                
                   print(msg)
                   self.dboutlines.append(msg)
            elif curlycount<=triggercc:
                 self.closePrim(lineidx)
                 msg = ""
                 if dbout:
                    prim_cur = self.get_prim_cur()
                    if prim_cur is not None:
                        uqname = prim_cur["uqname"]
                        msg = f'{Fore.CYAN}Close Prim:{uqname} idx:{lineidx}'
                    else:
                        msg = f'{Fore.CYAN}Close Prim:None idx:{lineidx}'
                    print(msg)
                    self.dboutlines.append(msg)

                 cp = self.get_prim_cur()
                 triggercc = curlycount
            lineidx += 1
        print(Fore.CYAN,f"End curlycount:{curlycount} seenbeforecount:{self.seenbeforecount} prims:{len(self.primdict.items())}")

        for  k,v in self.primdict.items():
            self.extractAttsForPrim(k,linebuf)

    def dumpPrims(self):
        for k,v in self.primdict.items():
            msg = f'prim: type:{Fore.BLUE}{v["ptype"]:15}{Fore.GREEN}  from {Fore.RED}{v["startidx"]:5}{Fore.GREEN} to {Fore.RED}{v["endidx"]:5} cc:{v["curlycount"]:2} {Fore.YELLOW}{k}'
            print(Fore.GREEN,msg)
            print(Fore.WHITE,f'    keyname:{v["keyname"]}  uqname:{v["uqname"]}')
            pprim = self.getParentPrim(v)
            if pprim!=None:
                print(Fore.WHITE,f'    parent:{pprim["keyname"]}')
            else:
                print(Fore.WHITE,f'    parent is None')
            hasMaterialParent = self.hasParentPrimOfPtype(v,"Material")
            print(Fore.WHITE,f"    hasParnetPrimOfPtype-Material:{hasMaterialParent}")

            atts = v["attributes"]
            if len(atts)==0:
                print(Fore.CYAN,"  no attributes")
            for k,v in atts.items():
                msg = f'  att:{v["attname"]:30}    - fore:{v["fore"]}'
                print(Fore.BLUE,msg)

        print(Fore.BLUE,f"Found {len(self.primdict)} prims")

    def primFromLine(self,linenum:int)->str:
        primname = "(null)"
        mindist = 9000000
        for k,v in self.primdict.items():
            if v["startidx"]<=linenum and linenum<=v["endidx"]:
                dist = linenum-v["startidx"]
                if dist<mindist:
                    primname = v["keyname"]
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
        if q1:
            return True
        q2 = tok.startswith('"') and tok.endswith('"')
        if q2:
            return True
    return False


def insertPtype(iline:str,ptype:str)->str:
    rv = iline.replace("def",f"def {ptype}")
    return rv


def morphLines(lines,usdprim):
    global args
    print(Fore.YELLOW,"Starting usd procssing"+Fore.BLUE)

    ofname = args.ofname
    verb = args.verbosity

    olines = []
    lineidx = 0
    nXformChanges = 0
    nShaderChanges = 0
    nSkelChanges = 0
    print(Fore.YELLOW,"Starting morphing"+Fore.BLUE)
    for line in lines:
        primfullname = usdprim.primFromLine(lineidx)
        (isprim,ptype,qname) = usdprim.extractRawPrim(line,lineidx)

        if lineidx==519:
            pass

        nline = line
        if isprim:
            if args.printAllDefs:
                print(str(lineidx)+Fore.MAGENTA+line.rstrip()+" "+Fore.BLUE+primfullname)

            if ofname!="" and ptype=="(ptype missing)":
                if verb>=3:
                    print(str(lineidx),": "+Fore.RED+line.rstrip()+" "+Fore.BLUE+primfullname)
                if args.subShader and usdprim.hasAttribute(primfullname,"inputs:diffuseColor"):
                        nline = insertPtype(line,"Shader")
                        nShaderChanges += 1
                        if verb>2:
                            print(str(lineidx),": "+Fore.MAGENTA+nline.rstrip()+" "+Fore.BLUE+primfullname)
                elif args.subShader and usdprim.hasBasename(primfullname,"PreviewSurface"):
                        nline = insertPtype(line,"Shader")
                        nShaderChanges += 1
                        if verb>2:
                            print(str(lineidx),": "+Fore.MAGENTA+nline.rstrip()+" "+Fore.BLUE+primfullname)
                elif args.subGeom and usdprim.hasBasename(primfullname,"Reference"):
                        nline = insertPtype(line,"Skeleton")
                        nSkelChanges += 1
                        if verb>2:
                            print(str(lineidx),": "+Fore.MAGENTA+nline.rstrip()+" "+Fore.BLUE+primfullname)
                elif args.subGeom and usdprim.hasBasenameSuffix(primfullname,"_Clone_"):
                        nline = insertPtype(line,"SkelRoot")
                        nSkelChanges += 1
                        if verb>2:
                            print(str(lineidx),": "+Fore.MAGENTA+nline.rstrip()+" "+Fore.BLUE+primfullname)
                elif args.subXform and usdprim.hasAttribute(primfullname,"transform"):
                        nline = insertPtype(line,"Xform")
                        nXformChanges += 1
                        if verb>2:
                            print(str(lineidx),": "+Fore.MAGENTA+nline.rstrip()+" "+Fore.BLUE+primfullname)
                                        

        if ofname!="" and args.subXform:
            olines.append(nline)

        lineidx += 1

    if ofname!="":
        with open(ofname,"w") as file:
            file.writelines(olines)
        print(f"wrote {len(olines)} to {ofname} - Changes: Xform:{nXformChanges} Shader:{nShaderChanges} Skel:{nSkelChanges}")

    if args.debugOutput:
        sep = "\n" 
        newlines = sep.join(usdprim.dboutlines)
        with open("dbout.ansi","w") as file:
            file.writelines(newlines)


print(Style.BRIGHT+Back.BLACK+f"USD morph")
print(Fore.YELLOW,f"    ifname:{args.ifname}")
print(Fore.YELLOW,f"    ofname:{args.ofname}")
print(Fore.YELLOW,f"    verbosity:{args.verbosity}")
print(Fore.YELLOW,f"    subXform:{args.subXform}")
print(Fore.YELLOW,f"    subShader:{args.subShader}")
print(Fore.YELLOW,f"    subGeom:{args.subGeom}")
print(Fore.YELLOW,f"    debugOutput:{args.debugOutput}")

if (args.ifname==""):
    print(f"error - no name specified")
else:
    lines = initbuffer(args.ifname)
    usdprim = UsdPrim(args.verbosity)
    usdprim.extractPrims(lines,args.debugOutput)
    usdprim.dumpPrims()    
    morphLines(lines,usdprim)    

elap = time.time() - starttime
print(Fore.BLUE+f"main execution took {elap:.2f} secs")