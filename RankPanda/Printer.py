# Testing reportlab

#import reportlab
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics, ttfonts
import PIL
from PIL import Image
import CoreWrapper
import GUIField

#register DejaVuSansMono
pdfmetrics.registerFont(ttfonts.TTFont('DejaVuSansMono', 'DejaVuSansMono.ttf'))
addMapping('DejaVuSansMono', 0, 0, 'DejaVuSansMono')

#constants
page_size = (LETTER[1],LETTER[0]) #landscape of letter standard
field_size = (9*inch, 5*inch)
field_height = 3*inch
widthHeightRatio= GUIField.FIELD_LENGTH_STEPS/GUIField.FIELD_WIDTH_STEPS

top_margin = page_size[1] - inch
bottom_margin = inch
left_margin = inch
right_margin = page_size[0] - inch
frame_width = right_margin - left_margin

def splitString(commStr, charLim, splitChar):
    strLength=0
    aStr=""
    bStr=commStr
    i=0
    while (strLength<(charLim-2)):
        partStr=bStr.partition(splitChar)
        aStrNew = aStr + partStr[0] + splitChar
        bStrNew = partStr[2]
        strLength=len(aStrNew)
        if(strLength<charLim-2):
            aStr=aStrNew
            bStr=bStrNew
        else:
            if(i==0):
                splStr=splitString(bStr.strip(),charLim-2," ")
                aStrNew = aStr + splStr[0]
                bStrNew = splStr[1]
                strLength=len(aStrNew)
                
                if(strLength<charLim-2):
                    aStr=aStrNew
                    bStr=bStrNew
        i=i+1
        
    return([aStr, bStr.strip()])

  
def drawEven(textObj, stringList, charactersPerLine, columns):
    i=0
    charactersPerCol = charactersPerLine/columns
    
    while (i<len(stringList)):
        k=0
        if(i!=0):
            textObj.setXPos((-1*columns)*(right_margin-left_margin)/columns)
        while ((k<columns) and (i<len(stringList))):
            
            commString = stringList[i]
            lineLength=len(commString) + 2 #leave space at the end to separate columns
            if (lineLength > charactersPerCol):    
                splStr=splitString(commString, charactersPerCol, ",")
                if (k == columns-1): textObj.textLine(splStr[0])
                else: textObj.textOut(splStr[0])
                if (splStr[1] != ""):
                    if(i+columns > len(stringList)):
                        j=0
                        lenStrL=len(stringList)
                        while(j < (i+columns-lenStrL+1)):
                            stringList.insert(len(stringList),"")
                            j=j+1
                    stringList.insert(i+columns, "   " + splStr[1])
                i=i+1
            else:
                if (k == columns-1): textObj.textLine(commString)
                else: textObj.textOut(commString)
                i=i+1
            k=k+1
            textObj.setXPos((right_margin-left_margin)/columns)
            

def printDrill(song, stringPath, moveNames, commandStrings, fontSize, columnsArr, measureInfo, movetexts):
    
    if (not (stringPath.endswith(".pdf"))):
        stringPath=stringPath + ".pdf"
        
    if (os.path.exists(stringPath)):
        if (os.path.isfile(stringPath)):
            #check if open?
            os.remove(stringPath)

    canv = canvas.Canvas(stringPath, page_size)
    i=0
    while (i<len(moveNames)):
        canv.setFont('DejaVuSansMono',12)
        canv.drawString(left_margin, field_height + field_size[1] + 10, song)
        canv.drawCentredString(0.5*page_size[0], 0.5 * inch,"Page %d" % canv.getPageNumber())
        canv.drawString(right_margin - 2*inch, field_height + field_size[1] + 10, moveNames[i])
        canv.drawCentredString(0.5*page_size[0], field_height + field_size[1] + 10,"Measures: "
                               + str(int(measureInfo[i][0])) + "-" +  str(int(measureInfo[i][1])))
        
        fieldImage = "fieldPic"+ moveNames[i] +".bmp"

        canv.drawImage(fieldImage, (page_size[0]-field_size[0])*.5,
                   field_height, field_size[0], field_size[1])
        if (os.path.exists(fieldImage)):
            if (os.path.isfile(fieldImage)):
                os.remove(fieldImage)
        canv.line(left_margin, field_height + field_size[1], right_margin, field_height + field_size[1])
        canv.line(left_margin, field_height, right_margin, field_height)
        
        tx = canv.beginText(left_margin, 2.5 * inch)
        tx.setFont("DejaVuSansMono", fontSize)
        stringList = commandStrings[i]
        if (movetexts[i][1]):
            drawEven(tx, [movetexts[i][0]], 1080/fontSize, 1) #overwrite only
        else:
            if(movetexts[i][0] is not None):
                drawEven(tx, [movetexts[i][0]], 1080/fontSize, 1)
                tx.setXPos(left_margin-right_margin)
                tx.textLine()
            drawEven(tx, stringList, 1080/fontSize, columnsArr[i])
        canv.drawText(tx)
        canv.showPage()
        
        i=i+1
    
    canv.save()

def printInd(song, stringPath, moveNames, commandStrings, fontSize, columns, measureInfo):
    
    if (not (stringPath.endswith(".pdf"))):
        stringPath=stringPath + ".pdf"
        
    if (os.path.exists(stringPath)):
        if (os.path.isfile(stringPath)):
            #check if open?
            os.remove(stringPath)

    canv = canvas.Canvas(stringPath, page_size)
    i=0
    while (i<len(commandStrings)):
        
        tx = canv.beginText(left_margin, top_margin)
        tx.setFont("DejaVuSansMono", fontSize)
        j=0
        stringList=[]
        while((j<columns) and (i+j<len(commandStrings))):
            stringList.append(commandStrings[i+j])
            j=j+1
        drawEven(tx, stringList, 1080/fontSize, columns)
        canv.drawText(tx)
        canv.showPage()
        
        i=i+columns
    
    canv.save()
    


