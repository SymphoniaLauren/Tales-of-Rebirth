import os.path
import json
import subprocess
import shutil
import itertools
import pandas as pd
import pygsheets
import re
import binascii

class FunctionsReinsert:
    
    #Initialize object
    def __init__(self):
        
        self.basePath = os.path.abspath(os.path.dirname(__file__))
        print(self.basePath)
        self.tblName = "tod2_utf8.tbl"
        self.slpsOriginal = "SLPS_251.72"
        
        #Load the two json files for config
        with open(os.path.join(self.basePath, "sectionsSLPS.json")) as f:
            self.dataJson = json.load(f)
            self.dataItems = self.dataJson['items']
            
        self.keysTag, self.mappingTblTag = self.loadTableForHex("tags.tbl")
        self.keysCharacter, self.mappingTblCharacter = self.loadTableForHex("characters.tbl")
        
        #with open(os.path.join(self.basePath, "memoryBanks.json")) as f:
        #    data = json.load(f)
        #    self.dfBanks = pd.DataFrame.from_dict(data['memoryBanks'])
        #    self.dfBanks['BlockDesc'] = ''
            
        
        
        #Authentification
        self.gc = pygsheets.authorize(service_file=os.path.join(self.basePath,'gsheet.json'))
        
        self.currentMemoryId = 1
        self.currentStart = 0
        self.currentEnd = 0
        self.originalSectionEnd = 0
        self.offset= 0
        
        self.loadTable()
        
    def getJsonBlock(self,blockDesc):
        return [ele for ele in self.dataItems if ele['BlockDesc'] == blockDesc][0]
    
    def showSections(self,blockDesc):
        
        blockSections = self.getJsonBlock(blockDesc)
        sectionsInfos = [ [ele['SectionId'], ele['SectionDesc']] for ele in blockSections['Sections']]
        
        #Print the sections on the screen
        for sectionId, sectionDesc in sectionsInfos:
            print("{}. {}".format(sectionId, sectionDesc))
        print("\n")
       
        
        
    def parseText(self,fileName):
        
        fread = open(os.path.join( self.basePath,"abcde", fileName),encoding="utf-8", mode="r")
        lines = fread.readlines()
        
        start=0
        end=0
        mylist=[]
        dfLines = pd.DataFrame(lines, columns=["Text"])
        finalList=[]
        
        for i,line in enumerate(lines):
            
            if "//Text " in line:
                start=i
            if "// current" in line:    
                finalList.append("".join(dfLines['Text'][start:i]))
        
        return finalList

    def writeColumn(self,finalList, googleId):
        
        sh = self.gc.open_by_key(googleId)
    
        #Look for Dump sheet 
        wks = sh.worksheet('title','Dump')
          
        #update the first sheet with df, starting at cell B2. 
        df=pd.DataFrame({"Japanese":finalList, "English":finalList})
        wks.set_dataframe(df,(1,0))
    
    def getGoogleSheetTranslation(self,googlesheetId, sheetName):
        
        sh = self.gc.open_by_key(googlesheetId)
        sheets = sh.worksheets()
        
        idSheet = [ ele.index for ele in sheets if sheetName in ele.title ][0]
        if idSheet != None:
            wks = sh[idSheet]
            
            df = pd.DataFrame(wks.get_all_records())
            
            #with open("test.txt",encoding="utf-8", mode="w") as f:
            #    f.write(translationsText)
            self.dfData = df
        else:
            print("Cannot find the sheet name in the google sheet")
            return "No"
    

    def removeBlankPointerData(self,fileName):
        print(fileName)
        fread = open(os.path.join( self.basePath,"abcde", fileName),encoding="utf-8", mode="r")
        fwrite = open(os.path.join( self.basePath,"abcde", "w"+fileName),encoding="utf-8", mode="w")
        
        lines = fread.readlines()
        indexStart = [i for i,line in enumerate(lines) if "FFFFFFFFFFF01000" in line] 
        indexComp = [list(range(i,i+5)) for i in indexStart]
        indexComp = list(itertools.chain.from_iterable(indexComp))
        
        for i,line in enumerate(lines):
            if i not in indexComp:
                
                fwrite.write(line)
                
        fread.close()
        fwrite.close()
        
        shutil.copyfile( os.path.join(self.basePath, "abcde","w"+fileName), os.path.join(self.basePath, "abcde",fileName))
    
    def getHeader(self):
        headerTxt="""#VAR(Table_0, TABLE)
#ADDTBL("{}", Table_0)

//BLOCK #000 NAME:
#ACTIVETBL(Table_0) // Activate this block's starting TABLE
#VAR(ptr, CUSTOMPOINTER)
#CREATEPTR(ptr, "LINEAR", $-FF000, 32)

""".format(os.path.join(self.basePath, "..", "..","abcde", self.tblName))
    
    
        return headerTxt

    def loadTable(self):
    
        with open(os.path.join(self.basePath,"..","..", "abcde", self.tblName), encoding="utf-8", mode="r") as tblfile:
            lines=tblfile.readlines()
            
        df = pd.DataFrame(lines, columns=['Value'])
        
        df['Value'] = [re.sub(r'\n$', '', ele) for ele in  df['Value']]
        df['Split'] = df['Value'].str.split("=")
        df['Hex']   = df['Split'].apply(lambda x: x[0])
        #df['Text']  = df['Split'].apply(lambda x: x[-1])
        df['Text']  = df['Split'].apply(lambda x: x[-1].replace("[END]\\n","[END]").replace("\\n","\n"))
        df.loc[ df['Text'] == "", 'Text'] = "="
        df.loc[ df['Hex'] == "/00","Hex"] = "00"
        
        df['NbChar']= df['Text'].apply(lambda x: len(x))
        listKeys = df['Text'].tolist()
        listValue = df['Hex'].tolist()
        mydict = {listKeys[i]: listValue[i] for i in range(len(listKeys))} 
        keys =sorted(list(mydict.keys()),key=lambda x: len(x))[::-1]
        
        self.keys = keys
        self.mappingTbl = mydict
        
    def loadTableForHex(self, tblName):
    
        with open(os.path.join(self.basePath,"..","..", "abcde", tblName), encoding="utf-8", mode="r") as tblfile:
            lines=tblfile.readlines()
            
        df = pd.DataFrame(lines, columns=['Value'])
        
        df['Value'] = [re.sub(r'\n$', '', ele) for ele in  df['Value']]
        df['Split'] = df['Value'].str.split("=")
        df['Hex']   = df['Split'].apply(lambda x: x[0])
        #df['Text']  = df['Split'].apply(lambda x: x[-1])
        df['Text']  = df['Split'].apply(lambda x: x[-1].replace("[END]\\n","[END]").replace("\\n","\n"))
        df.loc[ df['Text'] == "", 'Text'] = "="
        df.loc[ df['Hex'] == "/00","Hex"] = "00"
        
        df['NbChar']= df['Text'].apply(lambda x: len(x))
        listKeys = df['Hex'].tolist()
        listValue = df['Text'].tolist()
        mydict = {listKeys[i]: listValue[i] for i in range(len(listKeys))} 
        keys =sorted(list(mydict.keys()),key=lambda x: len(x))[::-1]
        
        return keys, mydict

        

    def findall(self,p, s):
        '''Yields all the positions of
        the pattern p in the string s.'''
        i = s.find(p)
        while i != -1:
            yield i
            i = s.find(p, i+1)
    
    def countBytes(self,text):
        
        out=[]
        base=text
        for k in self.keys:
               
            if k in base:
                
                #nb = len(re.findall(k.replace("?","\?").replace("[","\["), v))
                nb = len([i for i in self.findall(k, base)])
          
                
                base=base.replace(k,'')
                #print(base)
                out.append(self.mappingTbl[k]*nb)
                
        res = len("".join(out))/2
        
        return res

    def replaceTags(self,text):
        
       
        base=text
        for k in self.keysTag:
               
            if k in base:
                
                base = base.replace(k, self.mappingTblTag[k])
      
                #print(base)
       
        
        return base
    
    def replace_str_index(self,text,index, replacement,origSize):
        return '%s%s%s'%(text[:index],replacement,text[index+origSize:])

    def replaceCharacters(self, hexText):

     
    
        #mapping["00"] = " "
        #mapping["01"] = "\n"
    
        Hex = list(hexText)
        outputText = hexText
        delta=0
        print("Replace Char")
        #print(Hex)
        i = 0
        print(len(hexText))
        while i < len(Hex)-1:
            print(i)
            if( i+3 < len(Hex) and Hex[i] + Hex[i+1] + Hex[i+2] + Hex[i+3] in self.mappingTblCharacter):
                
                #print(Hex[i] + Hex[i+1] + Hex[i+2] + Hex[i+3])
                textReplace = self.mappingTblCharacter[Hex[i] + Hex[i+1] + Hex[i+2] + Hex[i+3]]
          
                outputText = self.replace_str_index(outputText, delta, textReplace, 4)
                delta+= len(textReplace)
                i += 4
                #print(outputText)
            elif( i+1 <len(Hex) and Hex[i] + Hex[i+1] in self.mappingTblCharacter):
                textReplace = self.mappingTblCharacter[Hex[i] + Hex[i+1]]
                outputText = self.replace_str_index(outputText, delta, textReplace,2)
                delta+= len(textReplace)
                i += 2
                #print(outputText)
            else:
                i += 1
    
        return outputText
    
    def convertHexToText(self, hexText):
        
        
        #hexText="99 E0 99 47 99 FB 00 00 99 DE 99 EB 99 47 99 E4 99 DE 00 00 00 00 00 00 9A 53 99 FA 99 C6 99 C9 9A 5D 00 00 00 00 00 00 9C 9E 9B FA 00 00 00 00 99 C7 99 C9 99 EB 9A 49 00 00 00 00 00 00 00 00 99 D0 99 DE 99 E4 9A 49 00 00 00 00 00 00 00 00 9D 90 9B E8 00 00 00 00 9B F7 9A 9C 00 00 00 00 99 CD 9A 5D 99 E6 9A 4C 9A 5D 99 ED 00 00 00 00 41 72 74 65 73 00 00 00 99 FC 9A 55 99 C9 99 E4 99 C9 9A 49 00 00 00 00 9A 9C 9A 9D 9A 52 9A 5D 99 D4 00 00 00 00 00 00 9A F2 9A B8 99 F7 99 E8 99 ED 00 00 00 00 00 00 99 CD 9A 5D 99 D0 99 CB 9A 5D 99 ED 00 00 00 00 9A 55 9A 5D 99 DF 00 00 99 D1 9A 54 99 EE 00 00 09 35 00 00 00 9A C1 9C 56 01 09 36 00 00 00 9B 94 99 BD 01 09 37 00 00 00 99 D5 9A 52 99 FA 9C 4B 9C 4C 01 09 38 00 00 00 9F 4D 99 A5 9A DC 9A E0 00 00 00 00 00 00 00 99 89 99 A2 99 BB 99 81 99 D2 99 47 9D 44 9B F7 99 7D 99 9C 99 75 99 9A 9E E9 9E 81 99 87 99 BE 99 BD 04 05 00 00 00 99 D2 99 47 9A 40 9A 54 99 FC 04 07 00 00 00 99 A1 01 04 05 00 00 00 53 45 4C 45 43 54 9A 44 99 E4 9A 5D 04 07 00 00 00 99 C4 9E F0 99 8B 99 85 99 9A 99 9D 99 BA 99 BC 9E E9 9E 81 99 9A E1 8A 9E E9 9E 81 99 C4 01 9C 4B 99 BC 9C 4C 99 79 99 BB 99 BE 99 B0 99 8B 00 00 25 64 00 00 00 00 00 00 25 73 00 00 00 00 00 00 25 64 25 73 25 30 32 64 00 00 00 00 00 00 00 00 3A 00 00 00 00 00 00 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 00 80 FF 00 00 00 00 9A 7A 00 00 00 00 00 00 9A 82 00 00 00 00 00 00 9A 9C 9A 9D 9A 4A 9A 5D 99 F5 99 47 99 9D 9A 9C 9A 9D 9E 9C 9E 9D 99 9C 99 D2 9A 4C 9A 52 99 7D 99 75 99 B0 99 8D 99 C5 00 00 00 00 00 00 00 00 C4 D5 16 00 0C D7 16 00 0C D7 16 00 0C D7 16 00 A0 D2 16 00 0C D7 16 00 0C D7 16 00 0C D7 16 00 0C D7 16 00 0C D7 16 00 0C D7 16 00 E0 D3 16 00 68 D5 16 00 0C D7 16 00 0C D7 16 00 18 D6 16 00 60 D6 16 00 00 00 00 00 00 00 00 00 00 00 00 00 14 D5 16 00 14 D5 16 00 CC D4 16 00 E8 D4 16 00 F0 D4 16 00 F8 D4 16 00 14 D5 16 00 00 D5 16 00 14 D5 16 00 44 D5 16 00 00 00 00 00 00 00 00 00 C8 DA 16 00 EC DC 16 00 E8 D8 16 00 E8 D8 16 00 80 D7 16 00 EC DC 16 00 EC DC 16 00 EC DC 16 00 EC DC 16 00 EC DC 16 00 EC DC 16 00 FC D8 16 00 5C DA 16 00 18 DB 16 00 18 DB 16 00 18 DB 16 00 18 DB 16 00 00 00 00 00 00 00 00 00 00 00 00 00"
        hexText = hexText.replace(" ","")
        
        #Start with Tags
        hexTagsReplaced = self.replaceTags(hexText)
   
        
        hexCharReplaced = self.replaceCharacters(hexTagsReplaced)
        with open(os.path.join(self.basePath, "testCharacters.txt"),encoding="utf-8", mode="w") as fText:
            fText.write(hexCharReplaced)
    
    def dumpText(self, fileName):
        
        #Load the file
        fileName = r"G:\TalesHacking\TOD2\GitProject\Tales-of-Destiny-2\ps2\menus\06167.md1"
        f = open(fileName, "rb")
        fText = f.read()
        hexText = binascii.hexlify(fText).decode("utf-8").upper()
  
        d = self.convertHexToText(hexText)
        
        print(d)
    def cleanData(self):
        
        self.dfData['English'] = self.dfData['English'].apply(lambda x: re.sub('\[END]$', '[END]\n', x))
        self.dfData['English'] = self.dfData['English'].str.replace("\r","")


    def createAdjustedBlock(self):
    
        #keys = [x for x in keys if not (x.isdigit() or x[0] == '-' and x[1:].isdigit())]
        self.dfData['TranslatedText'] = self.dfData['English'].apply(lambda x: x.split(")",1)[-1][1:])
        #dfData['NbBytes'] = dfData['TranslatedText'].apply( lambda x: countBytes( keys, mappingTbl, x))
        #dfData.to_excel("test.xlsx")
        
        
        sectionText=""
        
       
        for index,row in self.dfData.iterrows():
            textAdd=""
            v = row['TranslatedText']
     
            
            nb = self.countBytes(v)
            
            
            if (self.offset + nb > self.currentEnd):
                print("Sub Section start:            {}".format(hex(int(self.currentStart))))
                print("Sub Section original end:     {}".format(hex(int(self.currentEnd))))
                print("Sub Section translated end:   {}\n".format(hex(int(self.offset))))
                print("Overlapp, jump needed")
                print("Offset: {}".format(hex(int(self.offset))))
                
                #print("endInt: {}".format(endInt))
                self.currentMemoryId+= 1
                
                #Go grab a bank of memory
                newbank = self.dfBanks[ self.dfBanks['Id'] == self.currentMemoryId]
                self.offset = int(newbank['TextStart'].tolist()[0], 16)
    
                self.currentEnd = int(newbank['TextEnd'].tolist()[0], 16)
                textAdd += "#JMP(${})\n".format(newbank['TextStart'].tolist()[0])
                
                self.currentStart = self.offset
                
            
            self.offset += nb
                
                
                
            textAdd += "{}\n".format( row['English'])
            sectionText += textAdd
                
        print("Final Section start:            {}".format(hex(int(self.currentStart))))
        print("Final Section original end:     {}".format(hex(int(self.originalSectionEnd))))
        print("Final Section translated end:   {}\n".format(hex(int(self.offset))))
        
        self.currentStart = self.offset
        
        return sectionText
        
    def createBlock(self,blockId):
        
        #gc = pygsheets.authorize(service_file="gsheet.json")
        
        #Go grab the TextStart for the jump
        block = self.getJsonBlock(blockId)
        sections = block['Sections']
        lastSection = max([ele['SectionId'] for ele in sections])
        #Variables for adjusting overlapping
        textStart = [ele['TextStart'] for ele in sections if ele['SectionId'] == 1][0]
        textEnd = [ele['TextEnd'] for ele in sections if ele['SectionId'] == lastSection][0]
        self.currentStart  = int(textStart, 16)
        self.currentEnd    = int(textEnd, 16)
        self.offset = int(textStart,16)
        
        
        #Add the first jump
        jumpText = "#JMP(${})\n".format(textStart)
        
        #Grab some infos for each sections
        sectionsList = [ (ele['SectionId'], ele['SectionDesc'], ele['GoogleSheetId']) for ele in sections ]
        
        #Create a block of text with each section
        blockText = ""
        blockText += jumpText
      
        
        for sectionId, sectionDesc, googleId in sectionsList:
            
            blockText += "//Section {}\n\n".format(sectionDesc)
            self.originalSectionEnd = int([ele['TextEnd'] for ele in sections if ele['SectionId'] == sectionId][0],16)
            if googleId != "":
                print(sectionDesc)
                
                #Grab the text from google sheet
                self.getGoogleSheetTranslation(googleId, sectionDesc)
                self.cleanData()
                
                sectionText = self.createAdjustedBlock()
                
                #Add the result to the section
                blockText += sectionText.replace("\r","")
        
        print("Max Block End               :   {}".format(hex(int(textEnd, 16))))
        return block['BlockDesc'], blockText

    def createAtlasScript_Block(self,blockId):
        

        blockDesc, block = self.createBlock(blockId)
       
        header = self.getHeader()
        with open(os.path.join(self.basePath,"abcde", "TODDC_"+blockDesc+"_Dump.txt"),encoding="utf-8", mode="w") as finalScript:
            finalScript.write(header + block)
    
    def reinsertText_Block(self,blockId, slpsName):
    
        #Copy the original SLPS file first
        shutil.copyfile( os.path.join(self.basePath,"abcde","SLPS_original",self.slpsOriginal), os.path.join(self.basePath,"abcde",self.slpsOriginal))
        
        #Run Atlas in command line
        blockDesc = [ele['BlockDesc'] for ele in self.dataItems if ele['BlockId'] == int(blockId)][0]
        
        args = ["perl", "abcde.pl", "-m", "text2bin", "-cm", "abcde::Atlas", self.slpsOriginal, "TODDC_"+blockDesc+"_Dump.txt"]
        listFile = subprocess.run(
            args,
            cwd= os.path.join(self.basePath, "abcde"),
            )
        
        #Copy the new SLPS back to Google drive
        #print( "Source: " + os.path.join(path, "SLPS_258.42"))
        #print( "Destination: " + os.path.join(path,"..","..", slpsName))
        shutil.copyfile( os.path.join(self.basePath,"abcde", "SLPS_258.42"), os.path.join(self.basePath,"..", slpsName))
    
    def createAllBanks(self):
        
        #Max of the current memoryBanks
        
        
        #For each block, pick the first and last Offset
        listBlock = [ [ ele['BlockDesc'], ele['Sections'][0]['TextStart'], ele['Sections'][-1]['TextEnd']] for ele in self.dataItems]
        dfBase = pd.DataFrame(listBlock, columns=['BlockDesc','TextStart','TextEnd'])
        
        
        #Add the 3 original memory banks
        #self.dfBanks = dfBase.append(self.dfBanks)
        self.dfBanks = dfBase
        self.dfBanks = self.dfBanks.reset_index(drop=True)
        self.dfBanks['Id'] = self.dfBanks.index + 1
    
    
    
    def createBlockAll(self):
            
        #Consider all section as if they are memory bank
        print("create banks")
        self.createAllBanks()
        
        #print( self.dfBanks)
        
        #tbl dataframe to use
        self.loadTable()
        
        #Variables for adjusting overlapping
        memoryId=1
        bank = self.dfBanks[ self.dfBanks['Id'] == memoryId]
        
        banksNotEmpty = self.dfBanks[ self.dfBanks['BlockDesc'] != ""]
        lastbank = banksNotEmpty[banksNotEmpty['Id'] == banksNotEmpty['Id'].max()]
        print(lastbank)
        
        textStart = bank['TextStart'][0]
        finalEnd = lastbank['TextEnd'].tolist()[0]
        self.currentStart  = int(textStart, 16)
        self.currentEnd    = int(bank['TextEnd'][0], 16)
        self.offset = self.currentStart
        
        #First Jump
        jumpText = "#JMP(${})\n".format(textStart)
        allText = jumpText
        
        #Loop over all block
        blockList = [ele for ele in self.dfBanks['BlockDesc'].tolist() if ele != ""]
        for blockDesc in blockList:
            
            #Grab some infos for each sections
            print("Block: {}".format(blockDesc))
            sections = [ele['Sections'] for ele in self.dataItems if ele['BlockDesc'] == blockDesc][0]
            #print(sections)
            sectionsList = [ (ele['SectionId'], ele['SectionDesc'], ele['GoogleSheetId']) for ele in sections ]
            
            #Create a block of text with each section
            blockText = ""
            for sectionId, sectionDesc, googleId in sectionsList:
            
                blockText += "//Section {}\n\n".format(sectionDesc)
                self.originalSectionEnd = int([ele['TextEnd'] for ele in sections if ele['SectionId'] == sectionId][0],16)
                if googleId != "":
                    print(sectionDesc)
                    print("Google Sheet : {}".format(sectionDesc))
                    self.getGoogleSheetTranslation(googleId, sectionDesc)
                    self.cleanData()
                    
                    print("Create Adjusted block : {}".format(sectionDesc))
                    sectionText = self.createAdjustedBlock()
                    
                    #Add the result to the section
                    blockText += sectionText.replace("\r","")
                    
            allText += blockText
            
        print("Max Block End               :   {}".format(hex(int(finalEnd, 16))))
        return allText
            
                    
    def createAtlasScript_All(self):
        

        allText = self.createBlockAll()
       
        header = self.getHeader()
        with open(os.path.join(self.basePath, "TOD2_All_Dump.txt"),encoding="utf-8", mode="w") as finalScript:
            finalScript.write(header + allText)

    
    def reinsertText_All(self):
    
        #Copy the original SLPS file first
        shutil.copyfile( os.path.join(self.basePath,"SLPS_original",self.slpsOriginal), os.path.join(self.basePath,self.slpsOriginal))
    
        
        args = ["perl", "abcde.pl", "-m", "text2bin", "-cm", "abcde::Atlas", os.path.join(self.basePath, self.slpsOriginal), os.path.join(self.basePath,"TOD2_All_Dump.txt")]
        listFile = subprocess.run(
            args,
            cwd= os.path.join(self.basePath,"..","..", "abcde"),
            )
        
        shutil.copyfile( os.path.join(self.basePath, self.slpsOriginal), os.path.join(self.basePath,"..", self.slpsOriginal))
    
  
        