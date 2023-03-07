
# flake8: noqa

from colored import fg, bg, attr
import argparse
import time

starttime = time.time()


parser = argparse.ArgumentParser(description="Merge two text files",
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-mf", "--mainfile", action='store', required=True, help="Main file to copy", default="")
parser.add_argument("-f1", "--file1", action='store', required=True, help="File 1 to merge into main file", default="")
parser.add_argument("-idx1", "--index1", action='store', required=True,type=int, help="Index to merge file one in from", default="")
parser.add_argument("-of", "--outfile", action='store', required=True, help="Output file", default="")
parser.add_argument("-os", "--outskip", action='store', required=False, type=int, help="Line output increment", default=1000)
parser.add_argument("-v", "--verbose", action='store_true', default=False)

args = parser.parse_args()


mainfile = open(args.mainfile, 'r')
f1file = open(args.file1,'r')
outfile = open(args.outfile, 'w')
count = 0
  
while True:
  
    # Get next line from file
    line = mainfile.readline()
  
    if not line:
        break

    # print(f"count:{count} index1:{args.index1} c:{count==args.index1}")
    if count==args.index1:
        # print("inserting")
        while True:
            iline = f1file.readline()
            if not iline:
          #       print("Broke")
                break
            outfile.writelines(iline)

    outfile.writelines(line)

    if args.verbose or (count>0 and count%args.outskip == 0):
        elap = time.time()-starttime
        print(f"{count} - elap:{elap:.1f}")

    count += 1
  
mainfile.close()
outfile.close()


c1 = bg('navy_blue') + fg('white')
c2 = bg('navy_blue') + fg('yellow')

elap = time.time()-starttime

print(f"{c1}Merge took {c2}{elap:.3f}{c1} secs ")