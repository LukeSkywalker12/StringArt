from PIL import Image, ImageOps
from xiaolinWusLineAlgorithm import draw_line
import numpy as np


class StringArt:
    def __init__(self, nails, input_image, resolution=0.7):
        if type(input_image) == str: 
            self.image  = self.load_image(input_image)
        else:
            self.image  = input_image
        self.scale      = resolution
        self.image      = self.image.resize((round(self.image.width*self.scale), round(self.image.height*self.scale)), Image.Resampling.LANCZOS)
        self.nails      = nails
        self.radius     = min(self.image.height, self.image.width)*0.49
        self.midx       = self.image.width / 2
        self.midy       = self.image.height / 2
        self.operations = []


    def load_image(self, path):
        image = Image.open(path).convert("L")  # Convert to grayscale
        return image

    def nailToCoordinate(self, nail):
        #from polar coordinates
        return round(self.midx + self.radius*np.cos(2*np.pi*(nail/self.nails))), round(self.midy + self.radius*np.sin(2*np.pi*nail/self.nails))
    
    def getLine(self, start, end):
        p0 = self.nailToCoordinate(start)
        p1 = self.nailToCoordinate(end)
        sum = [0.0, 0.1]
        def pixel(img, p, color, alpha_correction, transparency):
            sum[0] += transparency*img.getpixel(p)
            sum[1] += transparency
        draw_line(self.image, p0, p1, 0, 1.0, pixel)
        return sum[0]/sum[1]

    def drawLine(self, start, end, color=20, alpha_correction=1, function=None):
        p0 = self.nailToCoordinate(start)
        p1 = self.nailToCoordinate(end)
        if function is None:
            draw_line(self.image, p0, p1, color, alpha_correction)
        else:
            draw_line(self.image, p0, p1, color, alpha_correction, function)
        self.operations.append((start, end))

    def tryChange(self, start, end, color=20, alpha_correction=1, function=None):
        self.pending_img = self.image.copy()
        self.drawLine(start, end, color, alpha_correction, function)
        self.image, self.pending_img = self.pending_img, self.image
        self.operations = self.operations[:-1]
        self.pending_operation = (start,end)
        
        return self.pending_img
    
    def acceptChange(self):
        self.image = self.pending_img
        self.operations.append(self.pending_operation)

    def invert(self):
        self.image = ImageOps.invert(self.image)
    
    def printOperations(self, file=None):
        file = open("operations.txt", "w")
        file.write(str(self.nails) + "\n")

        for i in self.operations:
            file.write(str(i[0]) + " " + str(i[1]) + "\n")

        file.close()

    def drawImgWithLines(self, lineCount):
        
        p1 = 0


        for count in range(0, lineCount):
            maxLine = (0, 0, 0)

            for p2 in range(0, self.nails):
                if p1 != p2:
                    value = self.getLine(p1, p2)
                    if  value > maxLine[0]:
                        maxLine = (value, p1, p2)

            self.drawLine(maxLine[1], maxLine[2])

            p1 = maxLine[2]

            if count % 100 == 0:
                print(count)
    
    def isPointInList(self, list, end):
        for point in list:
            if end == point:
                return True
        
        return False

    def listAlgo(self, sizeLastLines):
        lines = []
        lastNLines = []

        for p1 in range(0, 288):
            for p2 in range(0, 288):
                if p1 != p2:
                    lines.append((self.getLine(p1, p2), p1, p2))
        
        lines.sort(reverse=True)

        lines_drawn = 0

        for count in range(len(lines)):

            bruch = self.getLine(lines[count][1], lines[count][2]) / lines[count][0]

            if bruch > 0 and not self.isPointInList(lastNLines, lines[count][2]):

                self.drawLine(lines[count][1], lines[count][2])

                if len(lastNLines) > sizeLastLines:
                    lastNLines.pop(0)
                    lastNLines.append(lines[count][2])
                else:
                    lastNLines.append(lines[count][2])

                lines_drawn += 1
        

            if count % 1000 == 0:
                print(count)
            
            if lines_drawn > 6000:
                break
    

        
    


stringart = StringArt(288, "StringArt-main/test-images/einstein.jpg")

stringart.invert()

stringart.listAlgo(200)


stringart.printOperations()
