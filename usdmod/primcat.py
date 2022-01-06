from argparse import ArgumentParser
import colorama
from colorama import Fore
colorama.init()

usdattlist = [
    "xformOp:transform", "xformOpOrder", "transform","translate","scale","rotate",
    "inputs:diffuseColor"
]


class PrimCat:
    # USD Home page - https://graphics.pixar.com/usd
    # Terms and Concepts - https://graphics.pixar.com/usd/release/glossary.html  
    primdict = {}
    fullnamedict = {}
    prim_cur = None
    prim_cur_list = []
    dbout = False
    dboutlines = []
    seenbeforecount = 0
    linebuf = []

    def __init__(self, args: ArgumentParser):
        self.primdict = {}
        self.dbout = False
        if args is not None:
            self.dbout = args.debugOutput

    def registerFullName(self, fullname: str) -> int:
        if fullname not in self.fullnamedict:
            self.fullnamedict[fullname] = 1
        else:
            self.fullnamedict[fullname] += 1
        return self.fullnamedict[fullname]

    def addPrim(self, ptype: str, qname: str, lineidx: int, curlycount):
        uqname = self.remove_quotes(qname)
        if lineidx == 6385:
            pass
        if lineidx == 4048:
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
            if self.dbout:
                self.dboutlines.append(msg)
            self.seenbeforecount += 1

    def getParentPrim(self, entry):
        fullname = entry["keyname"]
        newend = fullname.rfind("/")
        if newend < 0:
            return None
        pfullname = fullname[:newend]
        pentry = self.primdict.get(pfullname)
        if pentry is not None:
            pass
        return pentry

    def hasParentPrimOfPtype(self, entry, ptype: str) -> bool:
        pentry = entry
        maxiter = 100
        iter = 0
        while pentry is not None:
            if pentry["ptype"] == ptype:
                return True
            pentry = self.getParentPrim(pentry)
            if iter > maxiter:
                print(f"MaxIter of {maxiter} exceeded in hasParerntPrimOfPtype:{ptype}")
                return False
            iter += 1
        return False

    def closePrim(self, linenum: int):
        prim_cur = self.get_prim_cur()
        if (prim_cur is not None):
            prim_cur["endidx"] = linenum
        self.pop_prim_cur()

    def extractAttsForPrim(self, seekPrimKeyName):
        entry = self.primdict.get(seekPrimKeyName)
        if entry is None:
            print(f"Error in extractAttsForPrim {seekPrimKeyName} not in primdict")
            return
        ifr = entry["startidx"]
        ito = entry["endidx"]
        for idx in range(ifr + 1, ito + 1):
            # we have to skip over embedded prims
            (primKeyName, prim) = self.primFromLine(idx)
            if primKeyName == seekPrimKeyName:
                line = self.linebuf[idx]
                fore = ""
                aft = ""
                sarr = line.split("=")
                if (len(sarr) >= 1):
                    fore = sarr[0]
                if (len(sarr) >= 2):
                    aft = sarr[1]
                if seekPrimKeyName == "/Human_0064/Materials/Man001_color_28332/PreviewSurface":
                    pass
                for attname in usdattlist:
                    if attname in fore:
                        self.addAttribute(entry, attname, fore, aft)

    def addAttribute(self, entry, attname: str, fore: str, aft: str):
        attdict = entry["attributes"]
        attdict[attname] = {"attname": attname, "fore": fore, "aft": aft}

    def hasAttribute(self, primfullname: str, attname: str) -> bool:
        entry = self.primdict.get(primfullname)
        if entry is None:
            print(f"Error in hasAttribute {primfullname} not in primdict")
            return False
        rv = attname in entry["attributes"]
        return rv

    def hasBasename(self, primfullname: str, qname: str) -> bool:
        entry = self.primdict.get(primfullname)
        if entry is None:
            print(f"Error in hasBasename {primfullname} not in primdict")
            return False
        rv = entry["basename"] == qname
        return rv

    def hasBasenameSuffix(self, primfullname: str, qnamesuffix: str) -> bool:
        entry = self.primdict.get(primfullname)
        if entry is None:
            print(f"Error in hasBasenameSuffix {primfullname} not in primdict")
            return False
        rv = entry["basename"].endswith(qnamesuffix)
        if rv:
            pass
        return rv

    def remove_quotes(self, tok: str):
        tok = tok.removeprefix("'")
        tok = tok.removeprefix('"')
        tok = tok.removesuffix("'")
        tok = tok.removesuffix('"')
        return tok

    def isquoted(self, tok: str) -> bool:
        if (len(tok) >= 2):
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

    def push_prim_cur(self, entry):
        self.prim_cur_list.append(entry)

    def pop_prim_cur(self):
        ln = len(self.prim_cur_list)
        if ln > 0:
            entry = self.prim_cur_list[ln - 1]
            self.prim_cur_list.remove(entry)

    def get_prim_cur(self):
        ln = len(self.prim_cur_list)
        if ln == 0:
            return None
        return self.prim_cur_list[ln - 1]

    def extractRawPrim(self, line: str, lineidx: int):
        tok = line.split()  # whitespace split
        if lineidx == 645:
            pass
        isprim = False
        ptype = "(ptype undefined)"
        qname = "(qname undefined)"
        if len(tok) > 0 and tok[0] == 'def':
            isprim = True
            if len(tok) <= 1:
                ptype = "(ptype missing)"
                qname = "(qname missing)"
            if self.isquoted(tok[1]):
                ptype = "(ptype missing)"
                qname = tok[1]
            else:
                ptype = tok[1]
                if (len(tok) < 2):
                    qname = "(qname missing)"
                else:
                    qname = tok[2]
        return (isprim, ptype, qname)

    def GetLineBuf(self):
        return self.linebuf

    def GetPrimDict(self):       
        return self.primdict

    def extractPrimsFile(self, filename: str):
        with open(filename) as file:
            self.linebuf = file.readlines()

        lineidx = 0
        curlycount = 0
        triggercc = 0

        for line in self.linebuf:
            curlycount += line.count('{')
            curlycount -= line.count('}')
            msg = f'{Fore.WHITE}{lineidx:5} {Fore.BLUE}cc:{curlycount} {Fore.YELLOW}"{line.strip()[:60]}"'
            if self.dbout:
                print(msg)
                self.dboutlines.append(msg)
            (isprim, ptype, qname) = self.extractRawPrim(line,lineidx)
            if isprim:
                self.addPrim(ptype, qname, lineidx, curlycount)
                triggercc = curlycount
                if self.dbout:
                    msg = f'{Fore.BLUE}Add Prim:{qname} idx:{lineidx}'
                    print(msg)
                    self.dboutlines.append(msg)
            elif curlycount <= triggercc:
                msg = ""
                if self.dbout:
                    prim_cur = self.get_prim_cur()
                    if prim_cur is not None:
                        uqname = prim_cur["uqname"]
                        msg = f'{Fore.CYAN}Close Prim:{uqname} idx:{lineidx}'
                    else:
                        msg = f'{Fore.CYAN}Close Prim:None idx:{lineidx}'
                    print(msg)
                    if self.dbout:
                        self.dboutlines.append(msg)
                self.closePrim(lineidx)
                # cp = self.get_prim_cur()
                triggercc = curlycount - 1
            lineidx += 1
        print(Fore.CYAN, f"End curlycount:{curlycount} seenbeforecount:{self.seenbeforecount} prims:{len(self.primdict.items())}")

        for k, _ in self.primdict.items():
            self.extractAttsForPrim(k)

    def dumpPrims(self):
        for k, v in self.primdict.items():
            msg = f'prim: type:{Fore.BLUE}{v["ptype"]:15}{Fore.GREEN}  from {Fore.RED}{v["startidx"]:5}{Fore.GREEN} to {Fore.RED}{v["endidx"]:5} cc:{v["curlycount"]:2} {Fore.YELLOW}{k}'
            print(Fore.GREEN, msg)
            print(Fore.WHITE, f'    keyname:{v["keyname"]}  uqname:{v["uqname"]}')
            pprim = self.getParentPrim(v)
            if pprim is not None:
                print(Fore.WHITE, f'    parent:{pprim["keyname"]}')
            else:
                print(Fore.WHITE, '    parent is None')
            # hasMaterialParent = self.hasParentPrimOfPtype(v,"Material")
            # print(Fore.WHITE,f"    hasParnetPrimOfPtype-Material:{hasMaterialParent}")

            atts = v["attributes"]
            if len(atts) == 0:
                print(Fore.CYAN, "  no attributes")
            for k, v in atts.items():
                msg = f'  att:{v["attname"]:30}    - fore:{v["fore"]}'
                print(Fore.BLUE, msg)

        print(Fore.BLUE, f"Found {len(self.primdict)} prims")

    def primFromLine(self, linenum: int) -> str:
        primKeyName = "(null)"
        mindist = 9000000
        primEntry = None
        for _, v in self.primdict.items():
            if v["startidx"] <= linenum and linenum <= v["endidx"]:
                dist = linenum - v["startidx"]
                if dist < mindist:
                    primKeyName = v["keyname"]
                    mindist = dist
                    primEntry = v
        return (primKeyName, primEntry)
