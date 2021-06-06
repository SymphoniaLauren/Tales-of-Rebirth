import sys
from HelperFunctions import *



if __name__ == "__main__":
    
    
    helper = Helper()
    sourceFile = sys.argv[1]
    baseheader = sys.argv[2]
    fileName = sys.argv[3]
    
    
    #Run the script
    helper.runscript(sourceFile, fileName)
    
    #Clean the dump file
    helper.cleanDump(fileName+"_dump.txt", baseheader)
