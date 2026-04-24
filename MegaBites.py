#Initialising modules
import random
import math
import pygame
from pygame.locals import *
import copy
pygame.init()
clock = pygame.time.Clock()

#Common colours
wallCol = (50,60,80)
counterCol = (180,150,130)
white = (255,255,255)
lightgrey = (200,200,200)
grey = (150,150,150)
mediumgrey = (100,100,100)
darkgrey = (50,50,50)
black = (0,0,0)
red = (255,100,100)
green = (100,255,100)
blue = (100,100,255)
yellow = (255,255,100)
labelFont = pygame.font.Font(None,40)

#Initialising the background
screen = pygame.display.set_mode() #Initialise screen
background = pygame.Surface((1920,1080)) #Create blank background
background.fill(wallCol) #Drawing the wall/top half
pygame.draw.rect(background,counterCol,Rect(0,500,1920,600)) #Drawing the counter/bottom half

def addZeros(value,max): #Fixes the length of value to max characters
    value = str(value)
    for i in range(max-len(value)):
        value = "0" + value
    return value

def scaleTuple(value,max):
    low = 0 #Ensuring all elements are greater than or equal to 0
    for i in value:
        if i < low:
            low = i
    value = (value[0]-low, value[1]-low, value[2]-low)
    high = 0 #Ensuring all elements are less than or equal to max
    for i in value:
        if i > high:
            high = i
    if high > max: #Scaling all elements down so that the largest element becomes max
        value = (int(value[0]*max/high),int(value[1]*max/high),int(value[2]*max/high))
    return value
    
class Food():
    def __init__(self,food,base,col):
        self.foodType = food #"D", "N" or "C" determines how Food is processed
        self.base = base #Determines how Food is formatted as a string
        self.colour = col #Determines how Food is coloured as a Surface
        self.plated = False #Determines if Food is underlined when formatted
        self.skewered = False #Determines if Food has strikethrough when formatted
        self.slices = 1 #Determines how many lines are drawn across it when formatted
        self.formatted = pygame.Surface((0,0)) #Not yet been formatted
    def format(self,maxSize,background=black):
        baseFont = pygame.font.Font(None,1000) #Ensures Food is formatted with high resolution
        if self.plated: #Underlining Food
            baseFont.set_underline(True)
        if self.skewered: #Drawing a line through Food
            baseFont.set_strikethrough(True)
        fontSize = baseFont.size(self.base) #Returns the size of base
        newSurface = baseFont.render(self.base,True,self.colour,background) #Creating text Surface
        if self.slices >1: #Does not draw lines if slices is 0 or 1
            centre = (int(fontSize[0]/2),int(fontSize[1]/2)) #Find midpoint of text Surface
            length = math.sqrt(centre[0]**2 + centre[1]**2) #Max length that may be drawn
            sliceAngle = 0 #Angle at which each cut should be drawn
            for i in range(self.slices): #Drawing lines from the centre to the edge of newSurface
                edge = (centre[0]+(math.cos(sliceAngle)*length),centre[1]+(math.sin(sliceAngle)*length))
                pygame.draw.line(newSurface,background,centre,edge,20)
                sliceAngle += 2*math.pi/self.slices
        scale = fontSize[0]/maxSize[0] #Scale based on width
        if scale < fontSize[1]/maxSize[1]: #Checks which scale is greater
            scale = fontSize[1]/maxSize[1] #Scale based on height
        fontSize = (int(fontSize[0]/scale),int(fontSize[1]/scale)) #Scale newSurface to fit maxSize
        self.formatted = pygame.transform.scale(newSurface,fontSize)
        return self.formatted #Should still return the formatted Surface if needed
        
class Station():
    def __init__(self, size=(0,0), pos=(0,0)): #Default size and pos means the blank Stations stay invisible
        self.wall = pygame.Surface(size)
        self.hover = 0
        self.position = pos
        self.buttonColours = [] #Values added in subclass initialisations
    def getButton(self,mouse): #Test if the cursor is within the boundaries of any buttons
        pass #Stations with no buttons will inherit this method so should always return 0
    def shadeButtons(self,start,end,default): #default is the colour of the button without a cursor over it
        for i in range(start,end):
            if i+1 == self.hover:
                self.buttonColours[i] = (default[0]-50,default[1]-50,default[2]-50)
            else:
                self.buttonColours[i] = default
    def clicked(self): #Triggers an action corresponding to hover
        pass
    def update(self):
        return self.wall #Stations which don't get repeatedly updated will inherit this method
    def passed(self,value,port): #Receive value from a Bus
        pass #Stations will be completed before some they pass to are started, so must allow Buses to pass to them
    def randomButtons(self,size,start,next,buttons):
        new = random.randint(0,size-1) #Chooses a random index (within the range passed)
        for i in range(0,size): #Used to check if the next element in buttons is empty if previous choice failed
            pos = start + (new+i)%size #Loops back to start position when new+i reaches size
            if buttons[pos] == None:
                buttons[pos] = next #Assign the button if the index is empty
                return buttons
            
class WALL_CLOCK(Station):
    def __init__(self):
        Station.__init__(self,(600,235),(0,0))
        self.wall.fill(wallCol)
        self.state = 2 #Index in states
        self.states = ["FETCH","DECODE","EXECUTE"]
        self.gameSpeed = 0.005
        self.buttonColours = [white]*2
        self.skip = Rect(250,145,105,50) #Skip button boundaries
        self.esc = Rect(5,5,60,35) #Quit button boundaries
        pygame.draw.circle(self.wall,black,(130,130),100) #Clock outline
        self.wall.blit(labelFont.render("CLOCK",True,black),(81,5)) #Clock label
        for i in range(3): #Bus references
            self.wall.blit(labelFont.render(["Control","Address","Data"][i]+" bus",True,[red,blue,green][i]),(400,135+(25*i)))
    def changeState(self):
        self.state = (self.state+1)%3 #Cycles state through 0 1 and 2
        pygame.draw.rect(self.wall,white,Rect(250,45,320,75),0,20) #speech bubble
        self.wall.blit(pygame.font.Font(None,90).render(self.states[self.state],True,black),(255,55))
        self.handAngle = 3*math.pi/2 #Reset to default
        if self.state == 0: #On fetch
            passto("PC",True,0)
            passto("DATA",False,1)
            passto("INSTR",True,3)
        elif self.state == 1: #On decode
            passto("CIR",True,0)
        elif self.state == 2: #On execute
            passto("CIR",False,0)
    def getButton(self,mouse):
        if self.skip.collidepoint(mouse):
            self.hover = 1
        elif self.esc.collidepoint(mouse):
            self.hover = 2
        else:
            self.hover = 0
    def clicked(self):
        if self.hover == 1: #Skip button
            self.changeState()
        elif self.hover == 2: #Quit button
            pygame.time.set_timer(QUIT,100)
    def update(self):
        self.shadeButtons(0,2,white)
        pygame.draw.rect(self.wall,self.buttonColours[0],self.skip,0,10) #Skip button
        self.wall.blit(pygame.font.Font(None,60).render("Skip",True,black),(255,150)) #Skip text
        pygame.draw.rect(self.wall,self.buttonColours[1],self.esc,0,5) #Quit button
        self.wall.blit(labelFont.render("Esc",True,black),(10,10)) #Esc label
        self.handAngle += self.gameSpeed
        if self.handAngle >= 7*math.pi/2: #When the hand does a full loop
            self.changeState()
        pygame.draw.circle(self.wall,white,(130,130),95) #clock face
        pygame.draw.line(self.wall,black,(130,130),(130+(math.cos(self.handAngle)*90),130+(math.sin(self.handAngle)*90)),5)
        return self.wall
    def passed(self,value,port):
        self.gameSpeed += 0.011/(value-2) #From RAM_INSTR

class PC(Station):
    def __init__(self):
        Station.__init__(self,(180,90),(65,240))
        self.wall.fill(wallCol)
        self.orderline = 21 #The first instruction to be accessed will be at address 021
        pygame.draw.rect(self.wall,grey,Rect(5,5,120,80),0,15) #PC outline
        self.wall.blit(labelFont.render("PC",True,black),(130,10)) #PC label
    def passed(self,value,port): #As there is only port 0 there is no need for selection
        passto("MAR",self.orderline,0)
        self.orderline +=1
        if self.orderline%10==0:
            self.orderline+=1
        pygame.draw.rect(self.wall,white,Rect(15,15,100,60),0,5) #PC orderline display
        self.wall.blit(pygame.font.Font(None,75).render(addZeros(self.orderline,3),True,black),(20,20))

class MAR(Station):
    def __init__(self):
        Station.__init__(self,(160,165),(60,330))
        self.wall.fill(wallCol)
        self.buttonColours = [white]
        self.receipt = False #Whether the button is visible or not
        self.button = Rect(25,104,110,58) #Receipt button dimensions
        pygame.draw.rect(self.wall,grey,Rect(5,30,150,70)) #Printer body
        pygame.draw.line(self.wall,mediumgrey,(20,90),(140,90),6) #Receipt slit
        pygame.draw.rect(self.wall,white,Rect(25,92,110,12)) #Receipt edge
        for i in range(0,22,2): #Draw dashes on the receipt edge
            pygame.draw.line(self.wall,grey,(27+(i*5),102),(27+((i+1)*5),102))
        self.wall.blit(labelFont.render("MAR",True,black),(10,60)) #MAR label
    def getButton(self,mouse):
        if self.button.collidepoint(mouse) and self.receipt:
            self.hover = 1
        else:
            self.hover = 0
    def clicked(self): #hover does not have to be checked as there is only one button
        passto("INSTR",self.receiptAddress,0)
        self.receipt = False #Prevent the receipt button from being clicked
        pygame.draw.rect(self.wall,wallCol,self.button) #Remove receipt by drawing over it
    def update(self):
        self.shadeButtons(0,1,white)
        if self.receipt: #Only show if button can be clicked
            pygame.draw.rect(self.wall,self.buttonColours[0],self.button) #Receipt button
            self.wall.blit(pygame.font.Font(None,75).render(addZeros(self.receiptAddress,3),True,black),(35,108))
            for i in range(0,22,2): #Draw dashes on the receipt button's edge
                pygame.draw.line(self.wall,grey,(27+(i*5),160),(27+((i+1)*5),160))
        return self.wall
    def passed(self,value,port):
        if port == 0: #From PC
            self.receipt = True #Allowing the button to be clicked
            self.receiptAddress = value
        elif port == 1: #From CIR
            if value <20: #Memory locations 0-19 store Food in RAM_DATA
                passto("DATA",value,0)
            else: #Memory locations 20+ store instructions in RAM_INSTRUCTIONS
                passto("INSTR",value,0)
        self.address = value #Both ports assign value to address
        pygame.draw.rect(self.wall,black,Rect(70,5,80,50)) #Printer screen
        self.wall.blit(pygame.font.Font(None,55).render(addZeros(self.address,3),True,white),(77,13))

class RAM_INSTR(Station):
    def __init__(self):
        Station.__init__(self,(640,450),(1260,25))
        self.wall.fill(grey) #This Station represents a gap in the wall
        self.customerID = 2
        self.address = 0
        self.patience = 0
        self.inRAM = 0
        pygame.draw.polygon(self.wall,white,((320,120),(320,160),(340,140))) #Speech bubble tail
        self.wall.blit(labelFont.render("RAM (INSTRUCTIONS)",True,black),(325,5)) #RAM label
    def lda(self,dish):
        if dish:
            address = random.randint(0,1) #Load dish
        else:
            address = random.randint(2,19) #Load non-dish
            if address >15: #Weighting towards choosing "C" foodTypes almost as often as "N" foodTypes
                address -= 4
        self.virtualStations["ACC"].passed(copy.copy(self.virtualStations["DATA"].contents[address]),0) #RAM to ACC
        return "LDA",address
    def sta(self):
        for address in range(16,20):
            if self.virtualStations["DATA"].contents[address] == None:
                break #Current memory location is empty
            elif address == 19: #If all memory locations checked but none empty
                address = random.randint(16,19)
                for i in range(4):
                    if address in self.unused: #Cannot overwrite unused Food
                        address = 16+((address-15)%4) #Increment by 1, looping back to 16 if 19
                    else:
                        break #Current memory location stores an already used Food
        self.virtualStations["ACC"].stackWidth -= self.virtualStations["ACC"].foodStack[-1].formatted.get_width()+15
        self.virtualStations["DATA"].contents[address]= self.virtualStations["ACC"].foodStack.pop() #Pop ACC to RAM
        self.unused.append(address) #Keeps track of Food stored by this customer
        if self.inRAM<4: #If not at max
            self.inRAM +=1
        return "STA",address
    def alu(self,fromStored):
        if fromStored:
            address = self.unused[-1] #Take the last stored Food by this customer
        else:
            address = random.randint(2,19+(2*self.inRAM)) #Take any non-dish Food in virtual RAM
            if address >19: #Weighting towards stored Food
                address = 6+(int(address/2))
            elif address >15: #Weighting towards "C" foodTypes
                address -= 4
        if fromStored or address in self.unused:
            self.unused.remove(address) #Food at this address is now used by this customer
        operator = ["SUM","SUB","MLT","EXP","DIV","MOD"][random.randint(0,5)] #Select random operator
        if operator == "EXP":
            module = "MLT" #EXP instructions are processed in ALU_MLT
        elif operator == "MOD":
            module = "DIV" #MOD instructions are processed in ALU_DIV
        else: #The other operators share their name with the key of their corresponding virtual station
            module = operator
        self.virtualStations["ACC"].stackWidth -= self.virtualStations["ACC"].foodStack[-1].formatted.get_width()+15
        self.virtualStations[module].passed(self.virtualStations["ACC"].foodStack.pop(),0) #Pop ACC to ALU
        self.virtualStations["ACC"].passed(copy.copy(self.virtualStations["DATA"].contents[address]),0) #RAM to ACC
        self.virtualStations["ACC"].stackWidth -= self.virtualStations["ACC"].foodStack[-1].formatted.get_width()+15
        self.virtualStations[module].passed(self.virtualStations["ACC"].foodStack.pop(),0) #Pop ACC to ALU
        if operator == "MLT":
            self.virtualStations["MLT"].dialStates[1] = 0 #x setting
        elif operator == "EXP":
            self.virtualStations["MLT"].dialStates[1] = 1 #^ setting
        elif module == "DIV":
            self.virtualStations["DIV"].setting = operator.lower() #div/mod setting depending on instruction
        self.virtualStations[module].process() #Process Food in corrsponding ALU module
        self.virtualStations["ACC"].passed(self.virtualStations[module].foodStack.pop(),0) #Pop ALU to ACC
        return operator, address
    def newCustomer(self):
        dishPos = random.randint(0,7) #Index of LDA (dish) in instructions
        self.unused = [] #Addresses of Food stored by this customer but not yet used
        self.instructions = [] #Delete previous instructions
        linesLeft = 7 #Number of instructions which have not been determined yet
        inACC = 0 #Number of Food currently in ACC (always 0 or 1)
        for orderline in range(0,8):
            if orderline == dishPos: #If at predetermined LDA (dish) instruction
                operator, address = self.lda(True)
            else:
                if linesLeft == len(self.unused): #Make sure all Food stored by this customer are used
                    operator, address = self.alu(True)
                elif inACC == 0: #If ACC is empty
                    operator, address = self.lda(False)
                    inACC = 1 #No longer empty
                elif operator == "LDA" or linesLeft == 1: #Should not STA if previously loaded
                    operator, address = self.alu(False)
                else:
                    next = random.randint(0,1) #Equal chance of ALU or STA
                    if next == 0 and linesLeft >2:
                        operator, address = self.sta()
                        inACC -= 1 #Food is removed from ACC and stored
                    else:
                        operator, address = self.alu(False)
                linesLeft -= 1
            self.instructions.append(self.instructionSet[operator]+addZeros(bin(address)[2:],9)) #Binary instruction
        self.instructions.append(self.instructionSet["STA"]+addZeros(bin(self.customerID*10)[2:],9)) #Final STA as binary
        self.virtualStations["ACC"].stackWidth -= self.virtualStations["ACC"].foodStack[-1].formatted.get_width()+15
        self.newFood = self.virtualStations["ACC"].foodStack.pop() #Final result of the 9 instructions
        pygame.draw.rect(self.wall,white,Rect(20,30,300,370),0,20) #Speech bubble
        randCol = (random.randint(0,255),random.randint(0,255),random.randint(0,255)) #Customer colour
        pygame.draw.rect(self.wall,randCol,Rect(380,180,200,270),0,30,30,30,0,0) #Customer body
        pygame.draw.circle(self.wall,randCol,(480,110),70) #Customer head
        self.wall.blit(pygame.font.Font(None,100).render(addZeros(self.customerID,2),True,black),(440,60)) #Customer eyes
        self.wall.blit(pygame.font.Font(None,100).render("0",True,black),(460,115)) #Customer mouth
        for i in range(1,10): #Displaying instruction indices in speech bubble
            self.wall.blit(pygame.font.Font(None,50).render(str(i)+")",True,black),(30,(i*40)))
    def passed(self,value,port):
        match port:
            case 0: #From MAR
                if value > self.customerID*10 and value < (self.customerID*10) +10: #1-9 of current customer's instructions
                    self.wall.blit(pygame.font.Font(None,50).render(self.instructions[(value-1)%10],True,black),(60,(value%10)*40))
                self.address = value
            case 1: #From MDR
                if self.address == self.customerID*10:
                    if self.newFood.foodType==value.foodType and self.newFood.base==value.base and self.newFood.colour==value.colour and self.newFood.plated==value.plated and self.newFood.skewered==value.skewered and self.newFood.slices==value.slices:
                        self.customerID +=1 #Next customer
                        self.patience = 0 #Reset countdown
                        self.newCustomer()
                        passto("CLOCK",self.customerID,0) #Increase game speed
                    else: #Display lose message and end game
                        self.wall.blit(pygame.font.Font(None,100).render("ERROR",True,black),(100,390))
                        pygame.time.set_timer(QUIT,3000) #Allow player to see error message before quitting
            case 2: #From main program, acts as a second initialisation
                self.instructionSet = value[0] #From CIR
                self.virtualStations = {"DATA":RAM_DATA(True),"ACC":ACC(True),"SUM":ALU_SUM(True),
                                        "SUB":ALU_SUB(True),"MLT":ALU_MLT(True),"DIV":ALU_DIV(True)}
                self.virtualStations["DATA"].contents = value[1] #From RAM_DATA
                self.newCustomer() #Create first customer
            case 3: #From CLOCK
                self.patience +=1
                if self.patience == 10: #10th fetch without Food being outputted
                    self.wall.blit(pygame.font.Font(None,100).render("OVERCLOCKED",True,black),(100,390))
                    pygame.time.set_timer(QUIT,3000) #Allow player to see error message before quitting

class MDR(Station):
    def __init__(self):
        Station.__init__(self,(300,290),(900,500))
        self.wall.fill(counterCol)
        self.buttonColours = [red]*5
        self.regValue = "" #Value on the display
        self.direction = 0 #Direction of output when submit it clicked
        self.submit = Rect(50,80,120,35) #Submit button boundaries
        self.cycle = Rect(210,80,40,35) #Cycle output button boundaries
        pygame.draw.rect(self.wall,lightgrey,Rect(10,10,280,270)) #Register body
        pygame.draw.rect(self.wall,grey,Rect(20,220,260,50)) #Register draw
        pygame.draw.line(self.wall,grey,(10,210),(289,210),4) #Draw divider
        pygame.draw.line(self.wall,grey,(10,65),(289,65),4) #Display divider
        self.wall.blit(labelFont.render("MDR",True,black),(120,235)) #MDR label
        labels = ["0","x","1"] #Button labels
        for i in range(3): #Binary input buttons
            pygame.draw.rect(self.wall,grey,Rect(45+(i*80),150,50,50)) #Outline
            self.wall.blit(labelFont.render(labels[i],True,grey),(63+(i*80),125)) #Label
        pygame.draw.rect(self.wall,grey,Rect(45,75,130,45)) #Submit button outline
        pygame.draw.rect(self.wall,grey,Rect(205,75,50,45)) #Cycle output button outline
        self.arrow = pygame.Surface((40,40)) #Creating output direction indicator symbol
        self.arrow.fill(white)
        pygame.draw.line(self.arrow,black,(10,20),(30,20),5)
        pygame.draw.line(self.arrow,black,(30,20),(20,10),5)
        pygame.draw.line(self.arrow,black,(30,20),(20,30),5)
    def getButton(self,mouse):
        if self.submit.collidepoint(mouse): #Hovering over submit button?
            self.hover = 4
        elif self.cycle.collidepoint(mouse): #Hovering over cycle output button?
            self.hover = 5
        else:
            for i in range(3): #Hovering one of the circular buttons?
                if ((mouse[0]-(70+(i*80)))**2) + ((mouse[1]-(175))**2)<20**2: #Equation of a circle
                    self.hover = i+1
                    return True #Prevent getting overwritten by 0 on next iteration
                else: #Hovering over none of the buttons
                    self.hover = 0
    def clicked(self):
        if self.hover == 1 or self.hover == 3: #0 or 1 button
            if type(self.regValue) == type("string"):
                if len(self.regValue)==12:
                    return False #Do nothing if at max
            else:
                self.regValue = "" #Removes Food object
            self.regValue += ["1","0"][self.hover%3]
        elif self.hover == 2: #x button
            if type(self.regValue) == type("string"):
                self.regValue = self.regValue[:len(self.regValue)-1] #Removes last character
            else:
                self.regValue = "" #Removes Food object
        elif self.hover == 4: #Submit button
            if type(self.regValue) == type("string"):
                if self.direction == 3: #Up
                    passto("CIR",self.regValue,1)
            elif self.direction !=3: #Right, down or left respectively
                passto(["INSTR","DATA","ACC"][self.direction],copy.copy(self.regValue),(self.direction+1)%3)
        elif self.hover == 5: #Cycle output button
            self.direction = (self.direction+1)%4
    def update(self):
        self.shadeButtons(0,5,red)
        for i in range(3): #Binary input buttons
            pygame.draw.circle(self.wall,self.buttonColours[i],(70+(80*i),175),20)
        pygame.draw.rect(self.wall,self.buttonColours[3],self.submit,0,5) #Submit button
        self.wall.blit(labelFont.render("Submit",True,black),(60,85)) #Submit button label
        pygame.draw.rect(self.wall,self.buttonColours[4],self.cycle,0,5) #Cycle output button
        pygame.draw.circle(self.wall,black,(230,98),15,6,True,True,True) #Cycle output label
        pygame.draw.polygon(self.wall,black,[(235,98),(247,98),(241,106)])
        pygame.draw.rect(self.wall,white,Rect(15,15,270,40)) #Input screen
        self.wall.blit(pygame.transform.rotate(self.arrow,self.direction*-90),(245,15)) #Current ouput direction
        if type(self.regValue) == type("string"): #If regValue is 0s and 1s
            self.wall.blit(labelFont.render(self.regValue,True,black),(23,23))
        else: #If regValue is Food
            self.wall.blit(self.regValue.formatted,(23,15))
        return self.wall
    def passed(self,value,port):
        if port == 2: #From RAM_INSTRUCTIONS
            pass #Ignore (visual purpose only)
        else: #From RAM_DATA or ACC
            self.regValue = value
            self.regValue.format((230,40),white)

class CIR(Station):
    def __init__(self):
        Station.__init__(self,(600,475),(620,20))
        self.wall.fill(wallCol)
        self.buttonColours = [lightgrey]*14 #Instruction buttons (first 8)
        for i in range(8,14):
            self.buttonColours[i] = green #Arrow buttons
        self.binOperator = "000" #Binary instruction
        self.binOperand = "000000000" #Binary address
        self.plainOperator = "" #Plaintext instruction
        self.decOperand = 0 #Decimal address
        self.locked = 1 #0 for unlocked, 1 for locked
        #Creating instruction set
        instr = [None]*8 #Plaintext instructions
        for i in ["LDA","STA","SUM","SUB","MLT","EXP","DIV","MOD"]:
            instr = self.randomButtons(8,0,i,instr)
        binary = [None]*8 #Binary instructions
        for i in range(8): #Get the binary string of numbers 0-8
            binary = self.randomButtons(8,0,addZeros(bin(i)[2:],3),binary)
        self.instructionSet = {}
        for i in range(8): #Assembling instruction set
            self.instructionSet[instr[i]] = binary[i]
    def getButton(self,mouse):
        if self.locked == 0:
            for i in range(3): #Hovering over instruction buttons?
                for j in range(3):
                    if Rect(60+(165*j),320+(50*i),150,40).collidepoint(mouse):
                        self.hover = (3*i+j+1)%9 #Excluding bottom right corner
                        return #Prevents hover from defaulting to 0
            for i in range(3): #Hovering over arrow buttons?
                if mouse[1]<145 and mouse[1]>-2*(mouse[0]-335-(i*59))+145 and mouse[1]>2*(mouse[0]-355-(i*59))+105:
                    self.hover = 9+i #Top arrow buttons
                    return
                elif mouse[1]>240 and mouse[1]<2*(mouse[0]-335-(i*59))+240 and mouse[1]<-2*(mouse[0]-355-(i*59))+280:
                    self.hover = 12+i #Bottom arrow buttons
                    return
        self.hover = 0
    def clicked(self):
        if self.hover <9: #Instruction buttons
            i = 1 #Must count i manually as dictionaries aren't scriptable with integers
            for instr in self.instructionSet.keys():
                if i == self.hover:
                    self.plainOperator = instr #Display the selected instruction
                    break
                else:
                    i+=1 #Check next hover
        else: #Up arrow if <12, down arrow if >11
            dir = 1 if self.hover<12 else -1 #Adding for up arrow, subtracting for down arrow
            self.decOperand += (10**(2-self.hover%3))*dir #Increment appropriate power of 10
            self.decOperand = scaleTuple((self.decOperand,0,0),511)[0] #Ensure within 0-511
    def update(self):
        pygame.draw.polygon(self.wall,black,[(0,0),(600,0),(550,300),(50,300)]) #Screen
        pygame.draw.polygon(self.wall,green,[(15,90),(585,90),(584,96),(16,96)]) #Horizontal divider
        pygame.draw.line(self.wall,green,(275,0),(275,300),10) #Vertical divider
        self.wall.blit(pygame.font.Font(None,70).render(self.binOperator,True,green),(160,25)) #Top left of display
        self.wall.blit(pygame.font.Font(None,70).render(self.binOperand,True,green),(300,25)) #Top right of display
        self.wall.blit(pygame.font.Font(None,140).render(self.plainOperator,True,green),(40,150)) #Left of display
        self.wall.blit(pygame.font.Font(None,140).render(addZeros(self.decOperand,3),True,green),(330,150)) #Right of display
        self.wall.blit(labelFont.render("CIR",True,green),(55,270)) #CIR label
        pygame.draw.rect(self.wall,green,Rect(40,40,30,30),0,2) #Padlock body
        pygame.draw.circle(self.wall,green,(33+(22*self.locked),40),13,4,True,True) #Padlock latch
        self.shadeButtons(0,8,lightgrey) #Instruction buttons
        self.shadeButtons(8,14,green) #Arrow buttons
        for i in range(3): #Each row of instruction buttons
            for j in range(3): #Each column of instruction buttons
                if not (i==2 and j==2): #There should be no 9th button
                    pygame.draw.rect(self.wall,self.buttonColours[3*i+j],Rect(60+(165*j),320+(50*i),150,40)) #Button
                    pygame.draw.line(self.wall,black,(142+(165*j),320+(50*i)),(142+(165*j),360+(50*i)),5) #Text/binary divider
        for k in range(2): #First the plaintext labels, then the binary labels
            i = 0 #i and j used in the same way as the nested for loop above
            j = 0 # ...to appropriately position the instruction labels
            for label in [self.instructionSet.keys(),self.instructionSet.values()][k]: #Instruction button labels
                self.wall.blit(pygame.font.Font(None,50).render(label,True,black),(60+(165*j)+(87*k),325+(50*math.floor(i))))
                i = i+0.34 #Increment every 3 loops (due to the floor function)
                j = (j+1)%3 #Increment every loop, resetting when i increments
        for i in range(3): #100, 10 and 1 button increments for each i respectively
            pygame.draw.polygon(self.wall,self.buttonColours[8+i],[(335+(i*59),145),(375+(i*59),145),(355+(i*59),105)]) #(^)
            pygame.draw.polygon(self.wall,self.buttonColours[11+i],[(335+(i*59),240),(375+(i*59),240),(355+(i*59),280)]) #(v)
        return self.wall
    def passed(self,value,port):
        match port:
            case 0: #From clock
                self.locked = not value #unlock on decode, lock on execute
                if not value: #if execute
                    passto("MAR",self.decOperand,1)
            case 1: #From MDR
                if self.locked and len(value)==12: #Only during fetch and correct length
                    self.binOperator = value[:3] #First 3 characters
                    self.binOperand = value[3:] #Last 9 characters
            
class RAM_DATA(Station):
    def __init__(self,virtual=False):
        Station.__init__(self,(640,560),(1260,510))
        self.locked = 0 #1 for unlocked, 0 for locked
        self.address = 0 #Referenced when storing Food from MDR
        self.contents = [None]*20 #Last 4 memory locations are left as None
        if not virtual:
            self.wall.fill(mediumgrey)
            for i in ("O","I"): #First 2 memory locations are dishes
                newFood = Food("D",i,black)
                self.randomButtons(2,0,newFood,self.contents)
            for i in range(10): #Next 10 memory locations are numbers
                newFood = Food("N",str(i),black)
                self.randomButtons(10,2,newFood,self.contents)
            for i in range(4): #Next 4 memory locations are colours
                newFood = Food("C",["r","g","b","y"][i],[red,green,blue,yellow][i])
                self.randomButtons(4,12,newFood,self.contents)
            for i in range(16):
                self.contents[i].format((100,90),lightgrey)
            self.buttonColours = [lightgrey]*20
            self.buttons = []
            for i in range(5): #Each row of buttons
                for j in range(4): #Each column of buttons
                    self.buttons.append(Rect(40+(150*j),10+(110*i),140,100)) #Food button boundaries
    def getButton(self,mouse):
        collision = False
        lasthover = self.hover
        if self.locked == 1: #Do not shade buttons if locked
            for i in range(20): #Checking the boundaries of each Food button
                if self.buttons[i].collidepoint(mouse):
                    collision = True
                    self.hover = i+1
                    break #The cursor can only hover over one button, so the rest do not need to be checked
        if not collision: #If not hovering over any of the buttons
            self.hover = 0
        if lasthover != self.hover: #If the cursor if hovering over a different button from last check
            if self.contents[lasthover-1] != None and lasthover !=0: #If previous button was formatted
                self.contents[lasthover-1].format((100,90),lightgrey) #Unshade previously shaded button
            if self.contents[self.hover-1] != None and self.hover !=0: #If this button can be formatted
                self.contents[self.hover-1].format((100,90),grey) #Shade previously unshaded button
    def clicked(self):
        if self.contents[self.hover-1] != None and self.locked == 1:
            passto("MDR",copy.copy(self.contents[self.hover-1]),1)
    def update(self):
        self.shadeButtons(0,20,lightgrey)
        for i in range(5): #Each row of buttons
            for j in range(4): #Each column of buttons
                pos = (i*4)+j #This phrase is reused frequently below
                pygame.draw.rect(self.wall,self.buttonColours[pos],self.buttons[pos]) #Food buttons
                if self.contents[pos] != None: #Cannot format None type
                    self.wall.blit(self.contents[pos].formatted,(75+(150*j),15+(110*i))) #Formatted contents
                self.wall.blit(labelFont.render(str(pos),True,black),(42+(150*j),10+(110*i))) #Button address label
        return self.wall
    def passed(self,value,port):
        if port ==2: #From MDR
            self.contents[self.address] = value
            self.contents[self.address].format((100,90),lightgrey)
        else: #Side bar should only be updated when passed from MAR or Clock
            if port ==0: #From MAR
                self.address = value
                self.locked = 1 #Unlock RAM
            elif port ==1: #From Clock
                self.locked = 0 #Locks RAM
            pygame.draw.rect(self.wall,mediumgrey,Rect(0,0,40,560)) #Erase locked indicator and RAM label before updating
            pygame.draw.line(self.wall,black,(5,25),(35,25),5) #Locked indicator
            pygame.draw.lines(self.wall,black,False,((5+(self.locked*10),40),(5,25),(5+(self.locked*10),10)),5+self.locked) #|- for locked, <- for unlocked
            self.wall.blit(pygame.transform.rotate(labelFont.render("RAM (DATA)      STA  -> "+addZeros(self.address,3),True,black),-90),(5,70)) #RAM label

class ACC(Station):
    def __init__(self,virtual=False):
        Station.__init__(self,(800,250),(20,525))
        self.foodStack = [] #Stack starts empty
        self.stackWidth = 0
        if not virtual:
            self.wall.fill(counterCol)
            self.buttons = []
            self.buttonColours = [lightgrey]*6
            for i in range(4):
                self.buttons.append(Rect(20+(i*70),170,60,60)) #Pass to ALU button boundaries
            for i in range(2):
                self.buttons.append(Rect(530+(i*130),170,120,60)) #Misc button boundaries
            for i in range(0,16,2): #Dashed horizontal lines
                pygame.draw.line(self.wall,darkgrey,(i*50+25,5),((i+1)*50+25,5),5) #Top
                pygame.draw.line(self.wall,darkgrey,(i*50+25,245),((i+1)*50+25,245),5) #Bottom
            for i in range(0,5,2): #Dashed vertical lines
                pygame.draw.line(self.wall,darkgrey,(5,i*40+25),(5,(i+1)*40+25),5) #Left
                pygame.draw.line(self.wall,darkgrey,(795,i*40+25),(795,(i+1)*40+25),5) #Right
            self.wall.blit(labelFont.render("ACCUMULATOR",True,black),(300,200)) #ACC label
    def getButton(self,mouse):
        for i in range(6): #Check all 6 button boundaries
            if self.buttons[i].collidepoint(mouse):
                self.hover = i+1
                return
        self.hover = 0 #Defaults to 0 if no collision
    def clicked(self):
        if len(self.foodStack)>0: #Check that foodStack is not empty
            self.stackWidth -= self.foodStack[-1].formatted.get_width()+15
            temp = self.foodStack.pop() #Remove last Food from stack
            if self.hover !=5: #All buttons pass to another Station except <-- (hover 5)
                passto(["SUM","SUB","MLT","DIV",None,"MDR"][self.hover-1],copy.copy(temp),0)
    def update(self):
        self.shadeButtons(0,6,lightgrey)
        pygame.draw.rect(self.wall,counterCol,Rect(10,10,780,155))
        length = 10 #x co-ordinate of Food to be displayed at
        for i in self.foodStack:
            self.wall.blit(i.formatted,(length,10))
            length += i.formatted.get_width()+15 #Next Food put after the last, leaving a gap
        for i in range(6):
            pygame.draw.rect(self.wall,self.buttonColours[i],self.buttons[i],0,5) #Buttons
        pygame.draw.line(self.wall,black,(50,180),(50,220),10) #SUM label
        pygame.draw.line(self.wall,black,(30,200),(70,200),10)
        pygame.draw.line(self.wall,black,(100,200),(140,200),10) #SUB label
        pygame.draw.line(self.wall,black,(175,220),(205,180),10) #MLT label
        pygame.draw.line(self.wall,black,(175,180),(205,220),10)
        pygame.draw.line(self.wall,black,(240,200),(280,200),10) #DIV label
        pygame.draw.circle(self.wall,black,(260,185),5)
        pygame.draw.circle(self.wall,black,(260,215),5)
        pygame.draw.line(self.wall,black,(541,200),(640,200),10) #Delete label
        pygame.draw.lines(self.wall,black,False,[(560,180),(540,200),(560,220)],10)
        pygame.draw.line(self.wall,black,(670,200),(770,200),10) #Pass to MDR label
        pygame.draw.lines(self.wall,black,False,[(750,180),(770,200),(750,220)],10)
        return self.wall
    def passed(self,value,port): #All ports have the same functionality
        value.format((780,155),counterCol)
        modified = False
        if len(self.foodStack)>0: #Don't need to check Food in ACC if it is empty
            if value.foodType == "D": #Check if the passed Food is a dish
                if value.base == "O": #Check the dish type
                    self.foodStack[-1].plated = True #Modify Food
                elif value.base == "I": #Check the dish type
                    self.foodStack[-1].skewered = True #Modify Food
                self.stackWidth -= self.foodStack[-1].formatted.get_width()+15 #Update display width
                self.foodStack[-1].format((780,155),counterCol) #Re-format modified Food
                modified = True #Prevent value from being added to the stack
            elif self.foodStack[-1].foodType == "D": #Check if the top Food of stack is a dish
                if self.foodStack[-1].base == "O": #Check the dish type
                    value.plated = True #Modify Food
                elif self.foodStack[-1].base == "I": #Check the dish type
                    value.skewered = True #Modify Food
                value.format((780,155),counterCol) #Re-format modified Food
                self.stackWidth -= self.foodStack[-1].formatted.get_width()+15 #Update display width
                self.foodStack.pop() #Remove the dish used to modify passed Food
                modified = False #Allow value to be added to the stack
            if self.stackWidth+value.formatted.get_width()+15 > 780: #If adding Food exceeds display width
                passto(["MDR","SUM","SUB","MLT","DIV"][port],copy.copy(value),0)
                return #Reject Food and pass back to Station it was passed from
        if not modified:
            self.foodStack.append(value) #Accept Food and add it to the stack
        self.stackWidth += self.foodStack[-1].formatted.get_width()+15 #Update display width

class ALU(Station):
    def __init__(self,port=0,x=1920,max=[(1,1)]*2,back=[counterCol]*2,col=counterCol):
        Station.__init__(self,(300,280),(x,795))
        self.port = port
        self.maxSizes = max
        self.backgrounds = back
        self.wall.fill(col)
        pygame.draw.rect(self.wall,darkgrey,Rect(0,0,300,280),5) #Module outline
        self.foodStack = []
    def findCase(self,a,b):
        if a.foodType == "C":
            if b.foodType == "C":
                return 0
            elif b.foodType == "N":
                return 1
        elif a.foodType == "N":
            if b.foodType == "C":
                return 2
            elif b.foodType == "N":
                return 3
    def process(self,slices=1):
        newFood = Food(self.newType,self.newBase,self.newColour) #Result of module-specific processing
        if self.foodStack[0].plated or self.foodStack[1].plated:
            newFood.plated = True #If either processed Food are plated, newFood will be too
        if self.foodStack[0].skewered or self.foodStack[1].skewered:
            newFood.skewered = True #If either processed Food are skewered, newFood will be too
        self.foodStack = [newFood] #Overwrite foodStack, removing processed Food
        if slices >1:
            self.foodStack[0].slices = slices
        self.foodStack[0].format(self.maxSizes[0],self.backgrounds[0]) #Re-format resultant Food
    def passed(self,value,port):
        if len(self.foodStack)==2 or value.foodType == "D":
            passto("ACC",copy.copy(value),self.port) #Reject if module is full or passed Food is invalid
        else:
            self.foodStack.append(value) #Accept and add passed Food to stack
            self.foodStack[-1].format(self.maxSizes[len(self.foodStack)-1],self.backgrounds[len(self.foodStack)-1])

class ALU_SUM(ALU):
    def __init__(self,virtual=False):
        ALU.__init__(self,1,5,[(90,90)]*2,[lightgrey]*2)
        if not virtual:
            self.buttonColours = [lightgrey]*2
            pygame.draw.polygon(self.wall,blue,((100,200),(200,200),(220,270),(80,270))) #Blender base
            self.wall.blit(labelFont.render("ALU +",True,black),(110,201)) #ALU label
    def process(self):
        a=self.foodStack[0] #Reassigning for ease of use
        b=self.foodStack[1]
        #Creating attributes of the new Food
        match self.findCase(a,b):
            case 0:
                self.newType = "C"
                self.newBase = "a"
            case 1:
                self.newType = "N"
                self.newBase = b.base
            case 2:
                self.newType = "N"
                self.newBase = a.base
            case 3:
                self.newType = "N"
                self.newBase = str(int((int(a.base)/a.slices)+(int(b.base)/b.slices)))
        cols = []
        for i in range(3): #Can be done within the line 2 below but separated for readability
            cols.append(int((a.colour[i]/a.slices)+(b.colour[i]/b.slices)))
        self.newColour = scaleTuple((cols[0],cols[1],cols[2]),255)
        ALU.process(self) #General processing
    def getButton(self,mouse):
        for i in range(2):
            if ((mouse[0]-(i*70+115))**2) + ((mouse[1]-245)**2)<18**2: #Equation of a circle
                self.hover = i+1
                return #Prevents defaulting to 0
        self.hover = 0
    def clicked(self):
        match self.hover:
            case 1:
                if len(self.foodStack)==2:
                    self.process()
            case 2:
                if len(self.foodStack)>0:
                    temp = self.foodStack.pop()
                    passto("ACC",copy.copy(temp),self.port)
    def update(self):
        self.shadeButtons(0,2,lightgrey)
        for i in range(2): #Process and pop buttons
            pygame.draw.circle(self.wall,self.buttonColours[i],(i*70+115,245),18) 
            self.wall.blit(labelFont.render(["+","^"][i],True,black),(i*70+107,i*5+230)) #Button labels
        pygame.draw.polygon(self.wall,lightgrey,((80,10),(220,10),(200,200),(100,200))) #Blender glass
        height = 0
        for i in range(len(self.foodStack)):
            height +=self.foodStack[i].formatted.get_height()+5 #Vertical distance of top left corner from bottom
            x = 150-self.foodStack[i].formatted.get_width()/2 #Making Food central when displayed
            self.wall.blit(self.foodStack[i].formatted,(x,200-height)) #Display Food
        return self.wall

class ALU_SUB(ALU):
    def __init__(self,virtual=False):
        ALU.__init__(self,2,310,[(150,80),(55,120)],[counterCol,lightgrey])
        if not virtual:
            self.buttonColours = [lightgrey]*2
            pygame.draw.rect(self.wall,green,Rect(40,220,220,50)) #Frame base
            pygame.draw.rect(self.wall,green,Rect(230,90,30,130)) #Frame neck
            pygame.draw.line(self.wall,black,(205,91),(230,91),4) #Connects siv to frame
            self.wall.blit(pygame.transform.rotate(labelFont.render("ALU -",True,black),-90),(230,100)) #ALU label
    def process(self):
        a=self.foodStack[0] #Reassigning for ease of use
        b=self.foodStack[1]
        #Creating attributes of the new Food
        match self.findCase(a,b):
            case 0:
                self.newType = "C"
                self.newBase = "s"
            case 1:
                self.newType = "C"
                self.newBase = a.base
            case 2:
                self.newType = "N"
                self.newBase = a.base
            case 3:
                self.newType = "N"
                self.newBase = str(int((int(a.base)/a.slices)-(int(b.base)/b.slices)))
        cols = []
        for i in range(3): #Can be done within the line 2 below but separated for readability
            cols.append(int((a.colour[i]/a.slices)-(b.colour[i]/b.slices)))
        self.newColour = scaleTuple((cols[0],cols[1],cols[2]),255)
        ALU.process(self) #General processing
    def getButton(self,mouse):
        for i in range(2):
            if ((mouse[0]-(i*70+98))**2) + ((mouse[1]-245)**2)<20**2: #Equation of a circle
                self.hover = i+1
                return #Prevents defaulting to 0
        self.hover = 0
    def clicked(self):
        match self.hover:
            case 1:
                if len(self.foodStack)==2:
                    self.process()
            case 2:
                if len(self.foodStack)>0:
                    temp = self.foodStack.pop()
                    passto("ACC",copy.copy(temp),self.port)
    def update(self):
        self.shadeButtons(0,2,lightgrey)
        for i in range(2): #Process and pop buttons
            pygame.draw.circle(self.wall,self.buttonColours[i],(i*70+98,245),20) #Buttons
            self.wall.blit(labelFont.render(["-","^"][i],True,black),(i*66+94,i*5+230)) #Button labels
        pygame.draw.rect(self.wall,counterCol,Rect(65,10,150,80)) #Clearing Food above sieve
        pygame.draw.circle(self.wall,lightgrey,(130,90),80,0,False,False,True,True) #Sieve
        if len(self.foodStack)>0: #If 1 or 2 Food in stack
            x = 130-self.foodStack[0].formatted.get_width()/2 #Making Food central when displayed
            self.wall.blit(self.foodStack[0].formatted,(x,10)) #Display 1st Food
            if len(self.foodStack)>1: #If 2 Food in stack
                x = 130-self.foodStack[1].formatted.get_height()/2 #Making Food central when displayed
                self.wall.blit(pygame.transform.rotate(self.foodStack[1].formatted,-90),(x,95)) #Display 2nd Food
        return self.wall

class ALU_MLT(ALU):
    def __init__(self,virtual=False):
        ALU.__init__(self,3,615,[(120,100)]*2,[darkgrey]*2,mediumgrey)
        self.dialStates = [0,0] #0 for left, 1 for right (index for l/r dial and value for indicator direction)
        if not virtual:
            self.buttonColours = [lightgrey]*2
            self.heaterColours = [black,black] #For cross and square heaters respectively
            for i in range(4):
                self.wall.blit(labelFont.render(["0","1","x","^"][i],True,black),(15+(i*85),45)) #Dial labels
            self.wall.blit(labelFont.render("ALU x",True,black),(110,5)) #ALU label
    def process(self):
        a=self.foodStack[0] #Reassigning for ease of use
        b=self.foodStack[1]
        #Creating attributes of the new Food
        cols = []
        if self.dialStates[1] == 0: #x setting
            for i in range(3):
                cols.append(int(((a.colour[i]/a.slices)+(b.colour[i]/b.slices))/2))
        else: #^/sq setting
            for i in range(3):
                cols.append(int((a.colour[i]/a.slices)*(b.colour[i]/b.slices)))
        self.newColour = scaleTuple((cols[0],cols[1],cols[2]),255)
        match self.findCase(a,b):
            case 0:
                self.newType = "C"
                self.newBase = "m"
            case 1:
                self.newType = "N"
                self.newBase = b.base
            case 2:
                self.newType = "N"
                self.newBase = a.base
            case 3:
                self.newType = "N"
                if self.dialStates[1] == 0: #x setting
                    self.newBase = str(int((int(a.base)/a.slices)*(int(b.base)/b.slices)))
                else: #^/sq setting
                    try:
                        self.newBase = str(int((int(a.base)/a.slices)**(int(b.base)/b.slices)))
                    except:
                        self.newBase = str(int((int(a.base)/a.slices)))
        ALU.process(self) #General processing
    def getButton(self,mouse):
        for i in range(2):
            if ((mouse[0]-(65+i*170))**2) + ((mouse[1]-60)**2)<30**2: #Equation of a circle
                self.hover = i+1
                return #Prevents defaulting to 0
        self.hover = 0
    def clicked(self):
        self.dialStates[self.hover-1]=1-self.dialStates[self.hover-1] #Flip relevant state: 1->0 or 0->1
        if self.hover ==1: #On/off button
                if len(self.foodStack)==2 and self.dialStates[0]==1: #Clicked when on setting 0
                    self.heaterColours[self.dialStates[1]] = red #Colour relevant heater
                    self.process()
                elif len(self.foodStack)>0 and self.dialStates[0]==0: #Clicked when on setting 1
                    self.heaterColours = [black]*2 #Uncolour both heaters
                    temp = self.foodStack.pop()
                    passto("ACC",copy.copy(temp),self.port)
    def update(self):
        self.shadeButtons(0,2,lightgrey)
        pygame.draw.rect(self.wall,darkgrey,Rect(20,100,260,160)) #Oven chamber
        for i in range(2):
            pygame.draw.line(self.wall,self.heaterColours[0],(30,112+(i*35)),(269,147-(i*36)),4) #Cross heater
            pygame.draw.circle(self.wall,self.buttonColours[i],(65+(i*170),60),30) #Dial buttons
            pygame.draw.line(self.wall,black,(65+(i*170),60),(40+(i*170)+(self.dialStates[i]*50),60),4) #Setting indicators
        pygame.draw.rect(self.wall,self.heaterColours[1],Rect(30,110,240,40),4) #Square heater
        for i in range(len(self.foodStack)):
            x = 85-self.foodStack[i].formatted.get_width()/2 #Centralises Food for display
            y = 205-self.foodStack[i].formatted.get_height()/2 #Centralises Food for display
            self.wall.blit(self.foodStack[i].formatted,(x+(i*130),y)) #Display Food
        return self.wall

class ALU_DIV(ALU):
    def __init__(self,virtual=False):
        ALU.__init__(self,4,920,[(130,130),(28,28)],[(250,220,160),counterCol])
        self.setting = None #div/mod
        if not virtual:
            self.buttonColours = [grey,grey,lightgrey]
            self.button = Rect(55,205,190,65) #Pop button boundaries
            self.wall.blit(labelFont.render("ALU /",True,black),(110,15)) #ALU label
    def process(self):
        a=self.foodStack[0]
        b=self.foodStack[1]
        if b.base == "0": 
            b.base = "1"
        #Creating attributes of the new Food
        slices = 1 #Default
        cols = []
        if self.setting == "div":
            if a.foodType == "C":
                self.newType = "C"
                self.newBase = a.base
            elif a.foodType == "N":
                self.newType = "N"
                self.newBase = str(int(int(a.base)/a.slices))
            if b.foodType == "N":
                for i in range(3):
                    cols.append(int((a.colour[i]/a.slices)//(int(b.base)/b.slices)))
                    slices = int(int(b.base)/b.slices)
            elif b.foodType == "C":
                for i in range(3):
                    if b.colour[i] == 0: col2 = 1
                    else: col2 = b.colour[i]
                    cols.append(int((a.colour[i]/a.slices)/(col2/b.slices)))
        elif self.setting == "mod":
            match self.findCase(a,b):
                case 0:
                    self.newType = "C"
                    self.newBase = "d"
                case 1:
                    self.newType = "C"
                    self.newBase = a.base
                case 2:
                    self.newType = "N"
                    self.newBase = a.base
                case 3:
                    self.newType = "N"
                    self.newBase = str(int((int(a.base)/a.slices)%(int(b.base)/b.slices)))
            for i in range(3):
                cols.append(int((a.colour[i]/a.slices)-(b.colour[i]/b.slices)))
                if cols[i] < 0: #Making any negative values 0
                    cols[i] = 0
        self.newColour = scaleTuple((cols[0],cols[1],cols[2]),255)
        ALU.process(self,slices)
    def getButton(self,mouse):
        if ((mouse[0]-50)**2) + ((mouse[1]-160)**2)<25**2: #Equation of a circle
            self.hover = 1 #Pizza cutter button
        elif mouse[1]<140 and mouse[0]<270 and mouse[1]>(-85/30)*mouse[0]+820: #Equations of lines
            self.hover = 2 #Knife button
        elif self.button.collidepoint(mouse):
            self.hover = 3 #Pop Food button
        else:
            self.hover = 0 #Defaults to 0
    def clicked(self):
        if self.hover == 3 and len(self.foodStack)>0: #Pop Food button
            temp = self.foodStack.pop()
            passto("ACC",copy.copy(temp),self.port)
        elif len(self.foodStack)==2: #Other 2 buttons only considered if stack is full
            if self.hover == 1:
                self.setting = "div"
            elif self.hover == 2:
                self.setting = "mod"
            self.process()
    def update(self):
        self.shadeButtons(0,2,grey)
        self.shadeButtons(2,3,lightgrey)
        pygame.draw.rect(self.wall,(250,220,160),Rect(10,50,280,150),0,20) #Cutting board
        pygame.draw.circle(self.wall,counterCol,(40,80),20) #Hole (foodStack[1] put here)
        pygame.draw.circle(self.wall,self.buttonColours[0],(50,160),25) #Pizza cutter blade (button)
        self.wall.blit(pygame.font.Font(None,90).render("/",True,black),(41,133)) #Cutter label
        self.wall.blit(pygame.transform.rotate(pygame.font.Font(None,110).render("T",True,black),165),(33,64)) #Cutter handle
        pygame.draw.rect(self.wall,black,Rect(260,140,10,50)) #Knife handle
        pygame.draw.polygon(self.wall,self.buttonColours[1],((240,140),(270,140),(270,55))) #Knife blade (button)
        for i in range(2): #Knife label
            self.wall.blit(labelFont.render("0",True,black),(235+(18*i),(85+(25*i))))
        if len(self.foodStack)>0: #If 1 or 2 Food in stack
            x = 160-self.foodStack[0].formatted.get_width()/2 #Centralises Food for display
            y = 125-self.foodStack[0].formatted.get_height()/2 #Centralises Food for display
            self.wall.blit(self.foodStack[0].formatted,(x,y)) #Display Food on board
        if len(self.foodStack)>1: #If 2 Food in stack
            x = 40-self.foodStack[1].formatted.get_width()/2 #Centralises Food for display
            y = 80-self.foodStack[1].formatted.get_height()/2 #Centralises Food for display
            self.wall.blit(self.foodStack[1].formatted,(x,y)) #Display Food in hole
        pygame.draw.rect(self.wall,self.buttonColours[2],self.button) #Pop button
        pygame.draw.lines(self.wall,black,False,((225,245),(75,245),(75,225)),4) #Pop button label
        pygame.draw.polygon(self.wall,black,((70,225),(82,225),(76,215))) #Pop button label (arrowhead)
        return self.wall
        
stations = {"CLOCK":WALL_CLOCK(),
            "PC":PC(),
            "MAR":MAR(),
            "INSTR":RAM_INSTR(),
            "MDR":MDR(),
            "CIR":CIR(),
            "DATA":RAM_DATA(),
            "ACC":ACC(),
            "SUM":ALU_SUM(),
            "SUB":ALU_SUB(),
            "MLT":ALU_MLT(),
            "DIV":ALU_DIV()}

class Bus():
    def __init__(self,col=black,coords=(),visible=False):
        self.colour = col #red for control, blue for address, green for data
        self.bends = coords #Vertices of Bus' path
        self.visible = visible #Whether Bus should be drawn
        self.latency = 0 #'Time' since passto was called
    def getCol(self):
        if self.latency>0:
            self.latency += 1
            if self.latency <30:
                return white #Flash white briefly when used
            else:
                self.latency = 0 #Reset to normal colour
        return self.colour
    def passto(self,dest,value,port):
        stations[dest].passed(value,port) #Pass on to correct Station
        self.latency +=1 #Start flash

buses = {"CLOCK":[Bus()], #Invisible (from INSTR)
         "PC":[Bus(red,((130,230),(130,244)),True)], #From CLOCK
         "MAR":[Bus(blue,((110,325),(110,359)),True), #From PC
                Bus(blue,((1034,321),(1034,329),(170,329),(170,334)),True)], #From CIR
         "INSTR":[Bus(blue,((205,430),(205,490),(1215,490),(1215,480),(1300,480),(1300,425)),True), #From MAR
                  Bus(green,((1190,535),(1225,535),(1225,490),(1740,490),(1740,475)),True), #From MDR
                  Bus(),Bus()], #Invisible (from CLOCK/CIR/DATA)
         "MDR":[Bus(green,((800,725),(825,725),(825,540),(910,540)),True), #From ACC
                Bus(green,((1259,540),(1190,540)),True), #From DATA
                Bus(green,((1305,425),(1305,485),(1220,485),(1220,530),(1190,530)),True)], #From INSTR
         "CIR":[Bus(red,((230,130),(637,130)),True), #From CLOCK
                Bus(green,((1165,509),(1165,321)),True)], #From MDR
         "DATA":[Bus(blue,((200,430),(200,495),(1280,495),(1280,509)),True), #From MAR
                 Bus(red,((29,130),(15,130),(15,500),(1275,500),(1275,509)),True), #From CLOCK
                 Bus(green,((1165,565),(1165,575),(1225,575),(1225,915),(1259,915)),True)], #From MDR
         "ACC":[Bus(green,((910,535),(810,535)),True), #From MDR
                Bus(green,((73,794),(73,755)),True), #From SUM
                Bus(green,((143,794),(143,755)),True), #From SUB
                Bus(green,((213,794),(213,755)),True), #From MLT
                Bus(green,((283,794),(283,755)),True)], #From DIV
         "SUM":[Bus(green,((67,755),(67,794)),True)], #From ACC
         "SUB":[Bus(green,((137,755),(137,794)),True)], #From ACC
         "MLT":[Bus(green,((207,755),(207,794)),True)], #From ACC
         "DIV":[Bus(green,((277,755),(277,794)),True)]} #From ACC

def passto(dest,value,port):
    buses[dest][port].passto(dest,value,port)

passto("INSTR",[stations["CIR"].instructionSet,copy.copy(stations["DATA"].contents)],2)
stations["CLOCK"].changeState()
running = True
while running:
    clock.tick(20) #20 frames per second
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]: #Detects if the escape key has been pressed
        running = False
    for event in pygame.event.get(): #Detects if the player tries to close the window
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            for i in stations.keys(): #Checks each Station to see if the cursor is over any of its buttons
                if stations[i].hover > 0:
                    stations[i].clicked()
    mouse = pygame.mouse.get_pos() #Gets co-ordinates of cursor
    mouse = (mouse[0]*1920/screen.get_width(),mouse[1]*1080/screen.get_height()) #Scales mouse for collisions
    for i in stations.keys():
        #Updates each Station's hover with mouse co-ordinate relative to each Station's position on background
        stations[i].getButton((mouse[0]-stations[i].position[0],mouse[1]-stations[i].position[1]))
        background.blit(stations[i].update(),stations[i].position)
    for stop in stations.keys():
        for bus in buses[stop]:
            if bus.visible:
                pygame.draw.lines(background,bus.getCol(),False,bus.bends,4)
    screen.blit(pygame.transform.scale(background,screen.get_size()),(0,0))
    pygame.display.flip() #Scaling the background to fit the player's screen and displaying it
