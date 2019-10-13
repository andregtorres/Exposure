#Exposure
#Andre Torres - 9.10.19
#Creates a composite image from the frames of videos.
#Inspired by the work of Jason Shulman
#https://www.publico.pt/2019/10/08/p3/fotogaleria/e-se-juntasses-todos-os-frames-de-um-filme-numa-so-imagem-397587?fbclid=IwAR0r5mGsVLrlsK5aNT-F_14q4zshxTwD6UKR2JmiVVtPcKGjoJmGJ5D9wME

## TODO: anti AA filter for decimation

import numpy as np
import cv2
import subprocess
import argparse
import sys

#inputFile="Jozin_z_Bazin_polskie_napisy.mp4"

def generateImage(inputFile, outputfile, n=0, mode='absolute', trim=['0','-1'], decimation=1, verbose=False):
    #trim video
    delete=False
    if trim != ['0','-1']:
        delete=True
        try:
            subprocess.Popen("rm aux.mp4", shell=True, stdout=subprocess.PIPE)
            t1=trim[0]
            t2=trim[1]
            args=""
            if t1 != "0" and t1!="00:00:00":
                args+=" -ss "+t1
            if t1 != "-1":
                args+=" -to "+t2
            cmd="ffmpeg -i "+inputFile+args+" aux.mp4"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            process.wait()
            inputFile="aux.mp4"
        except Exception as e:
            print("E: Error trimming video "+inputFile)
            return False


    #GET VIDEO
    try:
        vidcap = cv2.VideoCapture(inputFile)
    except Exception as e:
        print("E: Error loading file "+inputFile)
        return False


    #count frames
    numberOfFrames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    #read first frame
    rc,image = vidcap.read()
    if not rc:
        print("E: Clould not read image from file")
        return False
    height, width, channels = image.shape

    #create blank (black) canvas
    outputImage= np.ones(shape=[height, width, channels], dtype=np.float64)

    #set number of frames to print
    if n == 0 or n > numberOfFrames:
        n=numberOfFrames
        if verbose and  n>numberOfFrames :
            print("W: Input video only has {} frames.".format(numberOfFrames))
    if verbose:
        print("Printing {} out of {} frames".format(n,numberOfFrames))
        print("Dimensions: {}x{}".format(height, width))

    #Sum images
    sys.stdout.write('\r')  #progress bar
    j=0                     #progress bar
    for i in range (0,n,decimation):
        if rc:
            outputImage+=image.astype(np.float64)
        else:
            print("W: missing frame at i={}".format(i))
        vidcap.set(1,i)
        rc,image = vidcap.read()
        #progress bar
        if (i-1) >= int(n/20*(j+1)):
            j+=1
            sys.stdout.write("[%-20s] %d%%" % ('='*j, 5*j))
            sys.stdout.write('\r')
            sys.stdout.flush()
    sys.stdout.write('\n')

    #normalize
    #ABSOLUTE
    x=outputImage/(np.max(outputImage))*255
    outputImage_abs=x.astype(np.uint8)

    #CHANNEL
    maxs=np.array([0,0,0])
    for a in outputImage:
        for b in a:
            for i in range(3):
                if b[i]>maxs[i]:
                    maxs[i]=b[i]
    y =  outputImage/maxs*255
    outputImage_ch=y.astype(np.uint8)

    #write output file
    try:
        if mode=='absolute':
            cv2.imwrite(outputfile, outputImage_abs)
        if mode=='channel':
            cv2.imwrite(outputfile, outputImage_ch)
        if mode=='both':
            ext=outputfile.split(".")[-1]
            extlen=len(ext)
            outName=outputfile[:-1*extlen -1]
            outName_abs=outName+"_absolute."+ext
            outName_ch=outName+"_channel."+ext

            cv2.imwrite(outName_abs, outputImage_abs)
            cv2.imwrite(outName_ch, outputImage_ch)
    except:
        print("E: Error printing output file")
        return False

    #remove aux file
    if delete:
        subprocess.Popen("rm aux.mp4", shell=True, stdout=subprocess.PIPE)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates a composite image from the frames of videos.')
    parser.add_argument('input', metavar='inputFile',
                        help='Input file (.mp4 .mkv)')
    parser.add_argument('output', metavar='outputFile',
                        help='Output file (.png .jpg .jpeg)')
    parser.add_argument('-n', '--norm', dest='norm', action='store', default='absolute', choices=['absolute', 'channel', 'both'], help='Normalization method.')
    parser.add_argument('-t', '--trim', dest='times',  metavar=('t1','t2'), action='store', nargs=2, default=['0','-1'], help='Times for video trimming. Defaults to 0 -1')
    parser.add_argument('-d', '--decimation', dest='decimation',  metavar=("d"), action='store', default='1', help='Use every d frame')
    parser.add_argument("-v", "--verbose", help="Verbosity", action="store_true")


    #process parsed arguments
    args = parser.parse_args()
    inFile=args.input
    outFile=args.output
    mode=args.norm
    verbose=args.verbose
    times=args.times
    decimation=int(args.decimation)

    generateImage(inFile,outFile,0,mode, times,decimation, verbose)
