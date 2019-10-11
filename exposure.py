#Exposure
#Andre Torres - 9.10.19
#Creates a composite image from the frames of videoself.
#Inspired by the work of Jason Shulman
#https://www.publico.pt/2019/10/08/p3/fotogaleria/e-se-juntasses-todos-os-frames-de-um-filme-numa-so-imagem-397587?fbclid=IwAR0r5mGsVLrlsK5aNT-F_14q4zshxTwD6UKR2JmiVVtPcKGjoJmGJ5D9wME
import numpy as np
import cv2
import sys

#inputFile="Jozin_z_Bazin_polskie_napisy.mp4"

def generateImage(inputFile, outputfile, n=0, mode= 0, verbose=False):
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
    sys.stdout.write('\r')
    j=0
    for i in range (n):
        if rc:
            outputImage+=image.astype(np.float64)
        else:
            print("W: missing frame at i={}".format(i))
        rc,image = vidcap.read()
        if (i+1) % int(n/20) == 0:
            j+=1
            sys.stdout.write("[%-20s] %d%%" % ('='*j, 5*j))
            sys.stdout.write('\r')
            sys.stdout.flush()
    sys.stdout.write('\n')

    #normalize
    #mode0
    x=outputImage/(np.max(outputImage))*255
    outputImage0=x.astype(np.uint8)

    #mode1
    maxs=np.array([0,0,0])
    for a in outputImage:
        for b in a:
            for i in range(3):
                if b[i]>maxs[i]:
                    maxs[i]=b[i]
    y =  outputImage/maxs*255
    outputImage1=y.astype(np.uint8)

    #write output file
    try:
        if mode==0:
            cv2.imwrite(outputfile, outputImage0)
        if mode==1:
            cv2.imwrite(outputfile, outputImage1)
        if mode==2:
            ext=outputfile.split(".")[-1]
            extlen=len(ext)
            outName=outputfile[:-1*extlen -1]
            outName0=outName+"_0."+ext
            outName1=outName+"_1."+ext

            cv2.imwrite(outName0, outputImage0)
            cv2.imwrite(outName1, outputImage1)
    except:
        print("E: Error printing output file")
        return False

    return True

def printHelp(argv0):
    print("Usage: python3" + argv0 + " inputFile.mp4 outputfile.png/.jpeg [mode]")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        printHelp(sys.argv[0])
    else:
        inputFile=sys.argv[1]
        outputFile=sys.argv[2]
        if len(sys.argv) > 3:
            mode=int(sys.argv[3])
        else:
            mode=0
        generateImage(inputFile,outputFile,0,mode,True)
