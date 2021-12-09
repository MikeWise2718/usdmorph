import argparse
import time

starttime = time.time()

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def doit():
    parser = argparse.ArgumentParser(description='USD morph')
    parser.add_argument('--area', 
                        help='a predefined area to query against: currently eb12 or msft',
                        default='eb12')
    parser.add_argument('--id', 
                        help='id name - (same as area if not defined)',
                        default='')
    parser.add_argument('--tt', 
                        help='string: Plot title - (same as area if not defined)',
                        default='')
    parser.add_argument('--rg', 
                        help='string: Region name - (same as area if not defined)',
                        default='')
    parser.add_argument('--rc', 
                        help='string: Region color',
                        default='blue')                    

    parser.add_argument('--nord', 
                        type=str2bool, nargs='?',
                        help='bool: no OSM streets, roads, and highways',
                        default='False')                    
    parser.add_argument('--nomw', 
                        type=str2bool, nargs='?',
                        help='bool: no motorways',
                        default='False')                    
    parser.add_argument('--nobd', 
                        type=str2bool, nargs='?',
                        help='bool: no OSM buildings',
                        default='False')                    
    parser.add_argument('--nors', 
                        type=str2bool, nargs='?',
                        help='bool: no residencies or residential roads',
                        default='False')  
    parser.add_argument('--notr', 
                        type=str2bool, nargs='?',
                        help='bool: no trails or footpaths',
                        default='True')                              
    parser.add_argument('--nosv', 
                        type=str2bool, nargs='?',
                        help='bool: no service roads',
                        default='True')
    parser.add_argument('--nosr', 
                        type=str2bool, nargs='?',
                        help='bool: no streets and roads',
                        default='True')
    parser.add_argument('--slim', 
                        type=int, 
                        help='int: maxstreets',
                        default=1000)                    


    parser.add_argument('--doquery',
                        type=str2bool, nargs='?',
                        help='bool: run a new query against overpass (as opposed to using previously fetched results)',
                        default=False)

    parser.add_argument('--cs',
                        type=str2bool, nargs='?',
                        help='bool: export osm data as csharp file',
                        default=True)
    parser.add_argument('--csv',
                        type=str2bool, nargs='?',
                        help='bool: export osm data as csv file',
                        default=True)
    parser.add_argument('--csvx',
                        type=str2bool, nargs='?',
                        help='bool: export osm data as csvx file',
                        default=False)

    parser.add_argument('--ptx',
                        type=str2bool, nargs='?',
                        help='bool: plot text',
                        default=False) 
    parser.add_argument('--pntx',
                        type=str2bool, nargs='?',
                        help='bool: plot node text',
                        default=False) 
    parser.add_argument('--pll',
                        type=str2bool, nargs='?',
                        help='bool: plot lnglat',
                        default=True)                                            
    parser.add_argument('--bounds',
                        help='bounds: "latmin,lngmin, latmax,lngmax"',
                        default="")                    
    parser.add_argument('--bext',
                        help='bext: "lat,lng, latkm,lngkm"',
                        default="")   
    parser.add_argument('--bldyes',
                        help='bldyes: "the name that building type="yes" will be mapped to (mapping to yes is a noop)"',
                        default="yes")                                      
    parser.add_argument('--v',
                        type=int,
                        help='v: verbosity - 0 is minimal,1 is summary only,2 is more than that, 3 is maximal',
                        default=1)                    



def parseargs():
    parser = argparse.ArgumentParser(description='USD Morph')
    parser.add_argument('--ifname',default="",
                        help='the input USD file name')
    parser.add_argument('--ofname',default="",
                        help='the output USD file name - default has -out appended to name')
    # parser.add_argument('--buffer',
    #                     help='buffer the lines before processing')
    # parser.add_argument('--input',
    #                     help='the directory of the input frames')
    # parser.add_argument('--output',
    #                     help='the direcotry to store object detection results')
    # parser.add_argument('--frame',default="",
    #                     help='the frame file name')
    # parser.add_argument('--delframe',default=False,action='store_true',
    #                     help='delete frame after detection')
    # parser.add_argument('--boxplotlev',default=0,type=int,
    #                     help='create plots with detection boxes')
    # parser.add_argument('--redactlev',default=0,type=int,
    #                     help='redact frames (crop heads of persons')
    # parser.add_argument('--conflim',default=0.5,type=float,
    #                     help='confidence limit for detection')
    # parser.add_argument('--numfcand',default=50,type=int,
    #                     help='number of first stage candidates for object detection')
    # parser.add_argument('--modelname',default="rfcn-res101-2017",
    #                     help='model name for detection')
    # parser.add_argument('--maxobjnum',default=0,
    #                     help="max detection object number - zero means none")
    # parser.add_argument('--pooldir',default="",
    #                     help="Directory to pool compartive results to")
    args = parser.parse_args() 
    print("parsed args")
    return args

args = parseargs()
    

def initbuffer(usdfname:str):
    with open(usdfname) as file:
        lines = file.readlines()
    print(f"read {len(lines)} lines")
    return lines

def dowork(ifname:str,ofname:str):
    initbuffer(ifname)

print(f"USD morph")

if (args.ifname==""):
    print(f"error - no name specified")
else:
    dowork(args.ifname,args.ofname)    

elap = time.time() - starttime
print(f"main execution took {elap:.2f} secs")