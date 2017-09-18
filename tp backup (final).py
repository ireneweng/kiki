from __future__ import with_statement
import contextlib
import urllib
import os

from Tkinter import *
from eventBasedAnimationClass import EventBasedAnimationClass

import tkMessageBox
import random
import copy

######################### KIKI'S DELIVERY SERVICE #########################

# imported images use code from notes
# http://www.kosbie.net/cmu/fall-11/15-112/handouts/misc-demos/src/
# imagesDemo1.py

class KikisDeliveryService(EventBasedAnimationClass):

    # from class notes
    @staticmethod
    def readFile(filename, mode="rt"):
        with open(filename, mode) as fin:
            return fin.read()

    # from class notes
    @staticmethod
    def writeFile(filename, contents, mode="wt"):
        with open(filename, mode) as fout:
            fout.write(contents)

############################## INIT EVERYTHING ############################

    def __init__(self):
        self.rows = 15
        self.cols = 20
        self.cell = 40
        self.width = self.cols * self.cell
        self.height = self.rows * self.cell
        super(KikisDeliveryService, self).__init__(self.width, self.height)

    def initAnimation(self):
        self.initVariables()
        self.initHighScore()
        self.initImages()
        self.createMaze()
        self.createWalls()
        self.initClasses()
        self.initObjects()
    
    def initVariables(self):
        # setup variables
        self.timerDelay = 1000
        self.menuCenter = 17.5*self.cell
        self.r = 85
        self.tempR = 85
        self.mazeRows = 15
        self.mazeCols = 15
        # game start variables
        self.gameOver = False
        self.gameWon = False
        self.playCustom = False
        self.level = 1
        self.timer = 30
        self.countdown = 5
        self.score = 0
        # gameplay variables
        self.lives, self.maxLives = 6, 6
        self.collected, self.allCollected = 0, 3
        self.money, self.moneyGained = 1500, 100
        self.jijiGain, self.packGain = 50, 100
        self.civilianLoss, self.PolicemanLoss = 25, 75

    def initHighScore(self):
        self.path = "KikiHighScore.txt"
        if not (os.path.exists(self.path)):
            self.highScore = 0
        else:
            self.highScore = int(KikisDeliveryService.readFile(self.path))
        self.contents = str(self.highScore)

    def initImages(self):
        self.house = PhotoImage(file="blank.gif")
        # http://www.deviantart.com/art/CobbleSidewalkCenter-479017818
        self.ground = PhotoImage(file="ground.gif")
        # http://ec.l.thumbs.canstockphoto.com/canstock16736352.jpg
        self.colPackage = PhotoImage(file="package.gif")
        self.pckShadow = PhotoImage(file="pckshadow.gif")
        # http://www.dvdactive.com/images/reviews/screenshot/2013/
        # 6/kikisdeliveryservicebdcap3_original.jpg
        self.hsScreen = PhotoImage(file="highscorescreen.gif")
        # drawn by me!
        self.livesImage = PhotoImage(file="lives.gif")
        self.livesShadow = PhotoImage(file="livesshadow.gif")

    def initClasses(self):
        # player
        self.kiki = Kiki()    
        # menus
        self.start = StartScreen(self.canvas, self.width, self.height, self)
        self.edit = LevelEditor(self.canvas, self.width, self.height, self)
        self.menu = Menu(self.canvas, self.width, self.height, self.cell,
            self)
        self.invn = Inventory(self.canvas, self)
        self.nxtlvl = NextLevel(self.canvas, self)
        # objects
        self.object = Object(self.canvas, self.maze, self.cell)
        self.jiji = Jiji(self.canvas, self.maze, self.cell)
        self.p1 = Package1(self.canvas, self.maze, self.cell)
        self.p2 = Package2(self.canvas, self.maze, self.cell)
        self.p3 = Package3(self.canvas, self.maze, self.cell)
        # customer
        self.customer = Customer(self.canvas, self.maze, self.cell)
        # obstacles
        self.civilian = Civilian(self.canvas, self.maze, self.cell)
        self.police = Policeman(self.canvas, self.maze, self.cell)

    def initObjects(self):
        self.object.place()
        self.jiji.place()
        self.customer.place()
        self.civilian.place()
        self.police.place()
        self.p1.place()
        self.p2.place()
        self.p3.place()

############################# CREATE MAZE ################################

    # createMaze method and all helper methods use Prim's Algorithm
    # instructions/guidelines from Wikipedia
    # http://en.wikipedia.org/wiki/Maze_generation_algorithm#
    # Randomized_Prim.27s_algorithm

    # help and debugging from my CA/mentor Owen Fan

    def createMaze(self):
        self.maze, self.inMaze, self.wallList = [], [], []
        self.maze += [[0]*self.mazeCols for row in xrange(self.mazeRows)]
        rows, cols = self.mazeRows, self.mazeCols
        # Pick a cell and mark it as part of the self.maze.
        self.currCellRow, self.currCellCol = 13, 13
        self.currCell = (self.currCellRow, self.currCellCol)
        self.maze[self.currCellRow][self.currCellCol] = 1
        self.inMaze += [self.currCell]
        # Add the walls of the cell to the wall list.
        self.addWalls(self.mazeRows, self.mazeCols)
        # While there are walls in the list:
        while len(self.wallList) != 0:
            # Pick a random wall from the list.
            self.randCell = random.choice(self.wallList)
            self.randCellRow = self.randCell[0]
            self.randCellCol = self.randCell[1]
            # If the cell on the opposite side isn't in the self.maze yet:
            self.currCellRow = self.currCellCol = None
            self.checkWall(self.mazeRows, self.mazeCols)
            if (self.currCellRow is not None):
                # Make the wall a passage and mark the cell on the
                # opposite side as part of the self.maze.
                self.maze[self.randCellRow][self.randCellCol] = 1
                self.maze[self.currCellRow][self.currCellCol] = 1
                self.inMaze += [(self.currCellRow, self.currCellCol)]
                # Add the neighboring walls of the cell to the wall list.
                self.addWalls(self.mazeRows, self.mazeCols)
            # Remove the wall from the list.
            self.wallList.remove(self.randCell)

    def addWalls(self, rows, cols):
        if self.currCellRow-1 > 0:
            self.wallList += [(self.currCellRow-1, self.currCellCol)]
        if self.currCellRow+1 < rows-1:
            self.wallList += [(self.currCellRow+1, self.currCellCol)]
        if self.currCellCol-1 > 0:
            self.wallList += [(self.currCellRow, self.currCellCol-1)]
        if self.currCellCol+1 < cols-1:
            self.wallList += [(self.currCellRow, self.currCellCol+1)]

    # check if the cell on opposite side of the current cell is a path
    # if not, add to maze
    def checkWall(self, rows, cols):
        if ((self.randCellRow+1, self.randCellCol) in self.inMaze
            and (self.randCellRow-1, self.randCellCol) not in self.inMaze
            and self.randCellRow-1 >= 0):
            self.currCellRow = self.randCellRow-1
            self.currCellCol = self.randCellCol
        elif ((self.randCellRow-1, self.randCellCol) in self.inMaze
            and (self.randCellRow+1, self.randCellCol) not in self.inMaze
            and self.randCellRow+1 < rows):
            self.currCellRow = self.randCellRow+1
            self.currCellCol = self.randCellCol
        elif ((self.randCellRow, self.randCellCol+1) in self.inMaze
            and (self.randCellRow, self.randCellCol-1) not in self.inMaze
            and self.randCellCol-1 >= 0):
            self.currCellRow = self.randCellRow
            self.currCellCol = self.randCellCol-1
        elif ((self.randCellRow, self.randCellCol-1) in self.inMaze
            and (self.randCellRow, self.randCellCol+1) not in self.inMaze
            and self.randCellCol+1 < cols):
            self.currCellRow = self.randCellRow
            self.currCellCol = self.randCellCol+1

    # update the list of adjacent walls
    def addNeighbors(self):
        if self.currCellRow-1 > 0:
            self.wallList += [(self.currCellRow-1, self.currCellCol)]
        if self.currCellRow+1 < rows-1:
            self.wallList += [(self.currCellRow+1, self.currCellCol)]
        if self.currCellRow-1 > 0:
            self.wallList += [(self.currCellRow, self.currCellCol-1)]
        if self.currCellCol+1 < cols-1:
            self.wallList += [(self.currCellRow, self.currCellCol+1)]

    # assign each value to an actual wall or path
    def createWalls(self):
        self.walls = copy.deepcopy(self.maze)
        for row in xrange(self.mazeRows):
            for col in xrange(self.mazeCols):
                if self.walls[row][col] == 0:
                    self.walls[row][col] = self.house
                elif self.walls[row][col] == 1:
                    self.walls[row][col] = self.ground

########################### DRAW EVERYTHING ############################

    def drawMaze(self):
        for row in xrange(self.mazeRows):
            for col in xrange(self.mazeCols):
                wall = self.walls[row][col]
                self.drawMazeCells(row, col, wall)

    def drawMazeCells(self, row, col, wall):
        left, top = col * self.cell, row * self.cell
        right, bottom = left + self.cell, top + self.cell
        self.canvas.create_image(left+self.cell/2, top+self.cell/2,
            image=wall)

    def drawVisibility(self):
        for row in xrange(self.mazeRows):
            for col in xrange(self.mazeCols):
                visible = self.walls[row][col]
                left, top = col * self.cell, row * self.cell
                right, bottom = left + self.cell, top + self.cell
                if (left <= self.kiki.kx*self.cell-self.r or
                    top <= self.kiki.ky*self.cell-self.r or
                    right >= self.kiki.kx*self.cell+self.r or
                    bottom >= self.kiki.ky*self.cell+self.r):
                    visible = "black"
                    self.canvas.create_rectangle(left, top,
                        right, bottom, fill=visible, width=0)

    def drawTimer(self):
        y = 150
        self.canvas.create_text(self.menuCenter, y,
            text="Time: %d seconds"%self.timer, font="Helvetica 12")

    def drawMoney(self):
        y = 175
        self.canvas.create_text(self.menuCenter, y,
            text="Money: $%d"%self.money, font="Helvetica 12")

    def drawScore(self):
        y = 200
        self.canvas.create_text(self.menuCenter, y,
            text="Score: %d"%self.score, font="Helvetica 12")

    def drawHighScore(self):
        y = 225
        self.canvas.create_text(self.menuCenter, y,
            text="High Score: %d"%self.highScore, font="Helvetica 12")

    def drawCollected(self):
        packages = 3
        textY = 250
        top, space, imgWidth = 2.5, 1.5, 40
        self.canvas.create_text(self.menuCenter, textY, text="Packages:",
            font="Helvetica 12")
        for i in xrange(packages):
            wrapX = 16.55*self.cell+(i%3*imgWidth)
            wrapY = 285
            self.canvas.create_image(wrapX, wrapY, image=self.pckShadow)
        for i in xrange(self.collected):
            wrapX = 16.55*self.cell+(i%3*imgWidth)
            wrapY = 285
            self.canvas.create_image(wrapX, wrapY, image=self.colPackage)

    def drawLives(self):
        textY = 325
        top, space, imgWidth = 2.5, 1.5, 55
        self.canvas.create_text(self.menuCenter, textY,
            text="Lives:", font="Helvetica 12")
        # wrap around to next row
        for i in xrange(self.maxLives):
            wrap = i/3
            wrapX = 16.2*self.cell+(i%3*imgWidth)
            wrapY = 370+self.cell*space*wrap
            self.canvas.create_image(wrapX, wrapY,
                image=self.livesShadow)
        for i in xrange(self.lives):
            wrap = i/3
            wrapX = 16.2*self.cell+(i%3*imgWidth)
            wrapY = 370+self.cell*space*wrap
            self.canvas.create_image(wrapX, wrapY,
                image=self.livesImage)

    def drawMenu(self):
        self.drawTimer()
        self.drawMoney()
        self.drawScore()
        self.drawHighScore()
        self.drawCollected()
        self.drawLives()

    def drawHighScoreScreen(self, width, height):
        self.canvas.create_image(self.width/2, self.height/2,
            image=self.hsScreen)
        self.canvas.create_text(self.width/4, self.height/3,
            text="High Score : %s"%self.contents, fill="white",
            font="Helvetica 20")

    def drawWin(self):
        textY = 50
        self.canvas.create_text(self.mazeCols*self.cell/2,
            self.mazeRows*self.cell/2, text="You win!",
            font="Helvetica 20")

    def drawLose(self):
        textY = 50
        self.canvas.create_text(self.mazeCols*self.cell/2,
            self.mazeRows*self.cell/2, text="You lose!",
            font="Helvetica 20")
        self.canvas.create_text(self.mazeCols*self.cell/2,
            self.mazeRows*self.cell/2+textY, text="Click to play again",
            font="Helvetica 20")

    def drawObjects(self):
        if self.jiji.jiji not in self.kiki.visited:
            if self.lives <= 5:
                self.jiji.draw(self.jiji.jiji)
        if self.p1.p1 not in self.kiki.visited:
            self.p1.draw(self.p1.p1)
        if self.p2.p2 not in self.kiki.visited:
            self.p2.draw(self.p2.p2)
        if self.p3.p3 not in self.kiki.visited:
            self.p3.draw(self.p3.p3)
        self.civilian.draw(self.canvas, self.cell)
        self.police.draw(self.canvas, self.cell)
        self.customer.draw(self.canvas, self.cell)

############################## INTERACTIONS ##############################

    def interactions(self):
        self.pickup()
        self.collide()
        self.delivery()

    def pickup(self):
        # player picks up cat
        if self.maze[self.kiki.ky][self.kiki.kx] == "jiji":
            self.maze[self.kiki.ky][self.kiki.kx] = 1
            self.score += self.jijiGain
            if self.lives < self.maxLives:
                self.lives += 1
        # player picks up package
        if (self.maze[self.kiki.ky][self.kiki.kx] == "p1" or 
            self.maze[self.kiki.ky][self.kiki.kx] == "p2" or
            self.maze[self.kiki.ky][self.kiki.kx] == "p3"):
            self.maze[self.kiki.ky][self.kiki.kx] = 1
            self.score += self.packGain
            self.collected += 1
            self.r += self.cell

    def collide(self):
        # player runs into civilian
        if self.maze[self.kiki.ky][self.kiki.kx] == "civilian":
            if self.score - self.civilianLoss >= 0:
                self.score -= self.civilianLoss
            self.r -= self.cell
        # player runs into police
        if self.maze[self.kiki.ky][self.kiki.kx] == "police":
            if self.score - self.PolicemanLoss >= 0:
                self.score -= self.PolicemanLoss
            self.lives -= 1

    def delivery(self):
        # player delivers to customer
        if (self.customer.cu == (self.kiki.kx, self.kiki.ky) and
            self.maze[self.kiki.ky][self.kiki.kx] == "customer" and
            self.collected == self.allCollected):
            if self.playCustom == False:
                self.nxtlvl.next = True
                self.money += self.moneyGained*self.level
                self.level += 1
                self.countdown = 5
                self.nextLevel()
            else:
                self.gameOver = True
                self.gameWon = True

############################## NEXT LEVEL ##############################

    def nextLevel(self):
        self.createMaze()
        self.createWalls()
        for row in xrange(self.mazeRows):
            for col in xrange(self.mazeCols):
                if (self.maze[row][col] == "customer"):
                    self.maze[row][col] = True
                if (self.maze[row][col] == "civilian"):
                    self.maze[row][col] = True
                if (self.maze[row][col] == "police"):
                    self.maze[row][col] = True
        self.nextLvlObjects()
        self.nextLvlVariables()
        self.nextLvlTime()
        self.nxtlvl.choose()

    def nextLvlObjects(self):
        self.object = Object(self.canvas, self.maze, self.cell)
        self.jiji = Jiji(self.canvas, self.maze, self.cell)
        self.p1 = Package1(self.canvas, self.maze, self.cell)
        self.p2 = Package2(self.canvas, self.maze, self.cell)
        self.p3 = Package3(self.canvas, self.maze, self.cell)
        self.customer = Customer(self.canvas, self.maze, self.cell)
        self.civilian = Civilian(self.canvas, self.maze, self.cell)
        self.police = Policeman(self.canvas, self.maze, self.cell)
        self.jiji.place()
        self.object.place()
        self.civilian.place()
        self.police.place()
        self.p1.place()
        self.p2.place()
        self.p3.place()
        self.customer.place()

    def nextLvlVariables(self):
        self.r = 85
        self.collected = 0
        self.kiki.visited = set()
        self.object.emptySpaces = [(13, 13)]
        self.kiki.kx, self.kiki.ky = 13, 13

    def nextLvlTime(self):
        easy = 3
        medium = 6
        hard = 9
        if self.level <= easy:
            self.timer = 30
        elif self.level > easy and self.level <= medium:
            self.timer = 25
        elif self.level > medium and self.level <= hard:
            self.timer = 20
        else: self.timer = 15

############################## ONMOUSEPRESSED ##############################

    def onMousePressed(self, event):
        x, y = event.x, event.y
        bx = mx = 15.5*self.cell
        icony, width, height = 10, 80, 80
        if (self.start.startScreen == True and
            self.start.levelEditor == False):
            self.startMouse(event.x, event.y)
            self.returnToStart(event.x, event.y)
        elif self.start.levelEditor == True:
            self.editMouse(event.x, event.y)
        else:
            self.gameMouse(event.x, event.y)
            # click on menu
            if self.gameOver == True and self.gameWon == False:
                self.gameOver = False
                self.lives = 5
                self.level = 1
                self.nextLevel()

    # onMousePressed during the start screen
    def startMouse(self, x, y):
        px, py, pwidth, pheight = 180, self.height-175, 90, 90
        ix, iy, iwidth, iheight = 450, self.height-145, 200, 50
        hx, hy, hwidth, hheight = 180, self.height-105, 200, 70
        lx, ly, lwidth, lheight = 450, self.height-75, 200, 60
        # click play
        if x >= px and x <= px+pwidth and y >= py and y <= py+pheight:
            self.start.startScreen = False
        # click instructions
        elif x >= ix and x <= ix+iwidth and y >= iy and y <= iy+iheight:
            self.start.instructions = True
        # click high score
        elif x >= hx and x <= hx+hwidth and y >= hy and y <= hy+hheight:
            self.start.highScore = True
        # click level editor
        elif x >= lx and x <= lx+lwidth and y >= ly and y <= ly+lheight:
            self.start.levelEditor = True

    def returnToStart(self, x, y):
        hx, icony, width, height = 16.75*self.cell, 10, 100, 80
        # return to game from instructions
        if self.start.instructions == True:
            if (x >= hx and x <= hx+width and
                y >= self.height-(icony+height) and
                y <= self.height-icony):
                self.start.instructions = False
        # return to game from high scores
        if self.start.highScore == True:
            if (x >= hx and x <= hx+width and
                y >= self.height-(icony+height) and
                y <= self.height-icony):
                self.start.highScore = False

    # onMousePressed during the level editor
    def editMouse(self, x, y):
        hx, icony, width, height = 16.75*self.cell, 10, 100, 80
        # click return to game
        if (x >= hx and x <= hx+width and y >= self.height-(icony+height)
            and y <= self.height-icony):
            self.start.levelEditor = False
        self.clickWallOrPath(x, y)
        self.clickLoadButton(x, y)
        self.clickClearButton(x, y)
    
    def clickWallOrPath(self, x, y):
        for row in xrange(self.mazeRows):
            for col in xrange(self.mazeCols):
                if (((x >= col*self.cell and x < (col+1)*self.cell) and
                    (y >= row*self.cell and y < (row+1)*self.cell)) and
                    (row != 0 and row != self.mazeRows-1) and
                    (col != 0 and col != self.mazeCols-1)):
                    if self.edit.maze[row][col] == 0:
                        self.edit.maze[row][col] = 1
                        self.edit.walls[row][col] = self.ground
                    elif self.edit.maze[row][col] == 1:
                        self.edit.maze[row][col] = 0
                        self.edit.walls[row][col] = self.house

    def clickLoadButton(self, x, y):
        lx, width, height = 16.5*self.cell, 100, 50
        pathCount = 0
        stop = "Wait a minute!"
        morePaths = "You need to lay down more paths!"
        for row in xrange(self.mazeRows):
            for col in xrange(self.mazeCols):
                if self.edit.maze[row][col] == 1:
                    pathCount += 1
        if (x >= lx and x <= x+width and y >= self.height/2-height and 
            y <= self.height/2+height):
            if pathCount  >= 30:
                self.gameOver = False
                self.playCustom = True
                self.start.startScreen = False
                self.start.instructions = False
                self.start.levelEditor = False
                self.loadCustomLevel()
            else:
                tkMessageBox.showinfo(stop, morePaths)

    def loadCustomLevel(self):
        self.maze = self.edit.maze
        self.createWalls()
        self.nextLvlObjects()
        self.nextLvlVariables()
        self.nextLvlTime()
        self.nxtlvl.choose()

    def clickClearButton(self, x, y):
        cx, cy, width, height = 16.5*self.cell, 375, 100, 60
        rows, cols = self.mazeRows, self.mazeCols
        if (x >= cx and x <= x+width and y >= cy and 
            y <= cy+height):
            for row in xrange(self.mazeRows):
                for col in xrange(self.mazeCols):
                    if self.edit.maze[row][col] == 1:
                        self.edit.maze[row][col] = 0
                        self.edit.walls[row][col] = self.house
                        self.edit.maze[self.edit.x][self.edit.y] = 1
                        self.edit.walls[self.edit.x][self.edit.y]=self.ground

    # onMousePressed during the gameplay
    def gameMouse(self, x, y):
        bx = mx = 15.5*self.cell
        sx = hx = 18*self.cell
        icony, width, height = 10, 80, 80
        # click on bag
        if x >= bx and x <= bx+width and y >= icony and y <= icony+height:
            if self.nxtlvl.next == False:
                self.menu.bagButtonPressed()
        # click on shop
        elif (x >= sx and x <= sx+width and y >= icony and
            y <= icony+height):
            if self.nxtlvl.next == False:
                self.menu.shopButtonPressed()
        # click on menu
        elif (x >= mx and x <= mx+width and y >= self.height-(icony+height)
            and y <= self.height-icony):
            self.start.startScreen = True
        # click on help
        elif (x >= hx and x <= hx+width and y >= self.height-(icony+height)
            and y <= self.height-icony):
            if self.nxtlvl.next == False:
                self.menu.helpButtonPressed()

############################## ONKEYPRESSED ##############################

    def onKeyPressed(self, event):
        if self.gameOver == False:
            if self.start.startScreen == False:
                self.playGame(event)
                self.cheats(event)
            if self.score > self.highScore:
                self.highScore = self.score
                self.contents = str(self.highScore)
                KikisDeliveryService.writeFile(self.path, self.contents)

    # arrow key controls during the gameplay
    def playGame(self, event):
        self.interactions()
        if event.keysym == "Up":
            self.kiki.image = self.kiki.back
            self.kiki.move(-1, 0, self.maze)
        elif event.keysym == "Down":
            self.kiki.image = self.kiki.fwd
            self.kiki.move(1, 0, self.maze)
        elif event.keysym == "Left":
            self.kiki.image = self.kiki.left
            self.kiki.move(0, -1, self.maze)
        elif event.keysym == "Right":
            self.kiki.image = self.kiki.right
            self.kiki.move(0, 1, self.maze)
        if self.r <= 40 or self.lives == 0:
            self.gameOver = True

    def cheats(self, event):
        # uncover/recover maze
        if event.keysym == "u":
            self.tempR = copy.copy(self.r)
            self.r = 600
        elif event.keysym == "r":
            self.r = self.tempR
        elif event.keysym == "m":
            self.nextLevel()
            self.r = 600

############################## ONTIMERFIRED ##############################

    def onTimerFired(self):
        if self.gameOver == False:
            if self.start.startScreen == False:
                if self.nxtlvl.next == False:
                    if self.timer > 0:
                        self.timer -= 1
                    else:
                        self.lives -= 1
                        if self.lives > 0:
                            if self.level <= 3:
                                self.timer = 30
                            elif self.level > 3 and self.level <= 6:
                                self.timer = 25
                            elif self.level > 6 and self.level <= 9:
                                self.timer = 20
                            else: self.timer = 15
                        else:
                            self.timer = 0
                            self.gameOver = True
                if self.nxtlvl.next == True:
                    if self.countdown > 0:
                        self.countdown -= 1
                if self.countdown == 0:
                    self.nxtlvl.next = False

    def drawStartScreen(self):
        self.start.drawTitle()
        self.start.drawButtons()
        if self.start.instructions == True:
            self.start.drawInstructions(self.width, self.height)
        elif self.start.highScore == True:
            self.drawHighScoreScreen(self.width, self.height)
        elif self.start.levelEditor == True:
            self.edit.drawMaze()
            self.edit.drawMenu()

    def drawGame(self):
        self.drawMaze()
        self.drawObjects()
        if self.gameOver == False:
            self.drawVisibility()
        self.kiki.draw(self.canvas, self.kiki.kx, self.kiki.ky, self.cell)
        self.drawMenu()
        self.menu.draw()
        # next level scre ren
        if self.nxtlvl.next == True:
            self.nxtlvl.draw(self.canvas)
        # game over screen
        if self.gameOver == True and self.gameWon == False:
            self.drawLose()
        elif self.gameOver == True and self.gameWon == True:
            self.drawWin()

    def redrawAll(self):
        self.canvas.delete(ALL)
        # start screen open
        if self.start.startScreen == True:
            self.drawStartScreen()
        # game screen open
        else:
            self.drawGame()

############################## START SCREEN ##############################

class StartScreen(object):
    def __init__(self, canvas, width, height, game):
        self.canvas = canvas
        self.width, self.height = width, height
        self.game = game
        self.initAnimation()

    def initAnimation(self):
        self.startScreen = True
        self.instructions = False
        self.highScore = False
        self.levelEditor = False
        self.instrX = self.width/2
        self.instrY = self.height*9/10

        # http://fanart.tv/movie/16859/kikis-delivery-service/
        self.title = PhotoImage(file="title.gif")

        self.playImage = PhotoImage(file="playbutton.gif")
        self.instrImage = PhotoImage(file="instrbutton.gif")
        self.hsImage = PhotoImage(file="hsbutton.gif")
        self.lvlEdImage = PhotoImage(file="leveleditbutton.gif")
        self.instructionsSlide = PhotoImage(file="instructions slide.gif")

        self.instrText = "Navigate using the arrow keys.\
        \nWrite more instructions later."

    def drawTitle(self):
        titleY = self.height/2.5
        self.canvas.create_rectangle(0,0,self.width, self.height,
            fill="black", width=0)
        self.canvas.create_image(self.width/2, titleY, image=self.title)

    def drawButtons(self):
        px, ix, py, iy = 225, 550, 125, 130
        hx, lx, hy, ly = 225, 550, 55, 60
        self.canvas.create_image(px, self.height-py, image=self.playImage)
        self.canvas.create_image(ix, self.height-iy, image=self.instrImage)
        self.canvas.create_image(hx, self.height-hy, image=self.hsImage)
        self.canvas.create_image(lx, self.height-ly, image=self.lvlEdImage)

    def drawInstructions(self, width, height):
        self.canvas.create_image(self.width/2, self.height/2,
            image=self.instructionsSlide)

############################## MENU ##############################

# buttons use code from notes
# http://www.kosbie.net/cmu/fall-11/15-112/handouts/misc-demos/src/
# button-demo4.py

class Menu(object):
    def __init__(self, canvas, width, height, cell, game):
        self.canvas = canvas
        self.width, self.height = width, height
        self.cell = cell
        self.initButton()
        self.game = game
        self.start = StartScreen(canvas, width, height, self)
        self.inventory = Inventory(self.canvas, game)

    def initButton(self):
        padX, padY = 25, 5
        # http://images.neopets.com/items/sch_bpack_meowclops.gif
        self.bag = PhotoImage(file="bag.gif")
        # http://images.neopets.com/items/broken_bag_np.gif
        self.shop = PhotoImage(file="shop.gif")
        # http://images.neopets.com/items/boo_founder.gif
        self.book = PhotoImage(file="menu.gif")
        # http://images.neopets.com/items/foo_questionmark_cupcake.gif
        self.help = PhotoImage(file="help.gif")

    def bagButtonPressed(self):
        if self.game.gameOver == False:
            if self.inventory.bagOpen == False:
                self.inventory.bagOpen = True
            else:
                self.inventory.bagOpen = False
            # close other windows
            if self.inventory.shopOpen == True:
                self.inventory.shopOpen = False
            if self.start.instructions == True:
                self.start.instructions = False

    def shopButtonPressed(self):
        if self.game.gameOver == False:
            if self.inventory.shopOpen == False:
                self.inventory.shopOpen = True
            else:
                self.inventory.shopOpen = False
            # close other windows
            if self.inventory.bagOpen == True:
                self.inventory.bagOpen = False
            if self.start.instructions == True:
                self.start.instructions = False

    def helpButtonPressed(self):
        if self.game.gameOver == False:
            if self.start.instructions == False:
                self.start.instructions = True
            else:
                self.start.instructions = False
            # close other windows
            if self.inventory.bagOpen == True:
                self.inventory.bagOpen = False
            if self.inventory.shopOpen == True:
                self.inventory.shopOpen = False

    def draw(self):
        bagX = menuX = 16.25*self.cell
        shopX = helpX = 18.75*self.cell
        y, z = 50, 60
        self.canvas.create_image(bagX, y, image=self.bag)
        self.canvas.create_text(bagX, y*2, text="Bag", font="Helvetica 12")
        self.canvas.create_image(shopX, y, image=self.shop)
        self.canvas.create_text(shopX, y*2, text="Shop", font="Helvetica 12")
        self.canvas.create_image(menuX, self.height-y, image=self.book)
        self.canvas.create_text(menuX, self.height-y*2, text="Menu",
            font="Helvetica 12")
        self.canvas.create_image(helpX, self.height-y, image=self.help)
        self.canvas.create_text(helpX, self.height-y*2, text="Help",
            font="Helvetica 12")
        # open icons
        if self.inventory.bagOpen == True:
            self.inventory.drawBag(self.canvas)
        if self.inventory.shopOpen == True:
            self.inventory.drawShop(self.canvas)
        if self.start.instructions == True:
            self.start.drawInstructions(self.width, self.height)

############################## INVENTORY ##############################

# pop-up windows use code from notes
# http://www.kosbie.net/cmu/fall-11/15-112/handouts/misc-demos/src/
# dialogs-demo1.py

class Inventory(object):
    def __init__(self, canvas, game):
        self.canvas = canvas
        self.game = game
        self.rows, self.cols = 15, 15
        self.margin, self.cell = 40,40
        self.width = self.cols * self.cell
        self.height = self.rows * self.cell
        self.bagOpen = False
        self.shopOpen = False
        self.initPotions()
        self.imgWidth = 145
        self.noMoney = "Oh no!"
        self.noMoney2 = "You don't have enough money to buy this!"
        self.noItems = "You have no items :(\
            \nClick on the shop to buy something!"
        self.sure = "Are you sure?"
        self.initButtons()

    def initButtons(self):
        # bag
        self.initBagButtons()
        self.myObjects = []
        self.bagButtons = []
        # shop
        self.initShopButtons()
        self.shopObjects = [self.sec3potion, self.sec5potion,
            self.sec10potion, self.sec15potion, self.mysteryPotion,
            self.lifePotion, self.glasses, self.visiCloak]
        self.shopText = [self.sec3desc, self.sec5desc, self.sec10desc,
            self.sec15desc, self.mysteryDesc, self.lifeDesc,
            self.glassesDesc, self.visiDesc]
        self.shopButtons = [self.sec3Button, self.sec5Button,
            self.sec10Button, self.sec15Button, self.mysteryButton,
            self.lifeButton, self.glassesButton, self.visiButton]

    @staticmethod
    def randomLife(): return random.choice([-1, 1])
    
    def initPotions(self):
        # http://images.neopets.com/items/foo_twirlyfruit_sparkling.gif
        self.sec3potion = PhotoImage(file="sec3potion.gif")
        self.sec3desc = "Mini Swirl Soda\n+3 seconds"

        # http://images.neopets.com/items/foo_harffel_sparkling.gif
        self.sec5potion = PhotoImage(file="sec5potion.gif")
        self.sec5desc = "Fizzy Melon Juice\n+5 seconds"

        # http://images.neopets.com/items/foo_roseattle_sparkling.gif
        self.sec10potion = PhotoImage(file="sec10potion.gif")
        self.sec10desc = "Cool Polka Dot Pop\n+10 seconds"

        # http://images.neopets.com/items/foo_rhubyfruit_sparkling.gif
        self.sec15potion = PhotoImage(file="sec15potion.gif")
        self.sec15desc = "Super Turnip Tonic\n+15 seconds"

        # http://images.neopets.com/items/spf_droolikdrool.gif
        self.mysteryPotion = PhotoImage(file="mysterypotion.gif")
        self.mysteryDesc = "(Un)Lucky Potion\n-1 or +1 life"

        # http://images.neopets.com/items/gift_val_bottle.gif
        self.lifePotion = PhotoImage(file="lifepotion.gif")
        self.lifeDesc = "Bottle of Hearts\n+1 life"

        # http://images.neopets.com/items/clo_ixi_aviator_sunglass.gif
        self.glasses = PhotoImage(file="glasses.gif")
        self.glassesDesc = "Shiny Shades\n+1 visibility level"

        # http://images.neopets.com/items/bd_cloakofnight.gif
        self.visiCloak = PhotoImage(file="visibilitycloak.gif")
        self.visiDesc = "Visibility Cloak\nview entire maze"

############################## BAG ##############################

    def initBagButtons(self):
        pass
        self.use3button = Button(self.canvas, text="Use",
            command=self.useSec3, font="Helvetica 11")
        self.use5button = Button(self.canvas, text="Use",
            command=self.useSec5, font="Helvetica 11")
        self.use10button = Button(self.canvas, text="Use",
            command=self.useSec10, font="Helvetica 11")
        self.use15button = Button(self.canvas, text="Use",
            command=self.useSec15, font="Helvetica 11")
        self.useMysteryButton = Button(self.canvas, text="Use",
            command=self.useMystery, font="Helvetica 11")
        self.useLifeButton = Button(self.canvas, text="Use",
            command=self.useLife, font="Helvetica 11")
        self.useGlasses = Button(self.canvas, text="Use",
            command=self.useGlasses, font="Helvetica 11")
        self.useVisiButton = Button(self.canvas, text="Use",
            command=self.useVisi, font="Helvetica 11")

    def useSec3(self):
        response = tkMessageBox.askquestion(self.sure,
            "Use this potion for 3 more seconds?")
        if response == "yes":
            self.game.timer += 3
            self.myObjects.remove(self.sec3potion)
            self.bagOpen = False

    def useSec5(self):
        response = tkMessageBox.askquestion(self.sure,
            "Use this potion for 5 more seconds?")
        if response == "yes":
            self.game.timer += 5
            self.myObjects.remove(self.sec5potion)
            self.bagOpen = False

    def useSec10(self):
        response = tkMessageBox.askquestion(self.sure,
            "Use this potion for 10 more seconds?")
        if response == "yes":
            self.game.timer += 10
            self.myObjects.remove(self.sec10potion)
            self.bagOpen = False

    def useSec15(self):
        response = tkMessageBox.askquestion(self.sure,
            "Use this potion for 15 more seconds?")
        if response == "yes":
            self.game.timer += 15
            self.myObjects.remove(self.sec15potion)
            self.bagOpen = False

    def useMystery(self):
        response = tkMessageBox.askquestion(self.sure,
            "Careful! You can gain a life, but you can also lose one.\
            \nUse the potion anyways?")
        if response == "yes":
            result = Inventory.randomLife()
            self.game.lives += result
            self.myObjects.remove(self.mysteryPotion)
            self.bagOpen = False

    def useLife(self):
        response = tkMessageBox.askquestion(self.sure,
            "Use this potion for 1 extra life?")
        if response == "yes":
            self.game.lives += 1
            self.myObjects.remove(self.lifePotion)
            self.bagOpen = False

    def useGlasses(self):
        response = tkMessageBox.askquestion(self.sure,
            "Use these glasses for 1 more visibility level?")
        if response == "yes":
            self.game.r += self.game.cell
            self.myObjects.remove(self.glasses)
            self.bagOpen = False

    def useVisi(self):
        response = tkMessageBox.askquestion(self.sure,
            "Use this cloak to see the whole maze?")
        if response == "yes":
            self.game.r = 540
            self.myObjects.remove(self.visiCloak)
            self.bagOpen = False

    def drawBag(self, canvas):
        canvas.create_rectangle(0,0,self.width, self.height, fill="white",
            width=0)
        for i in xrange(len(self.myObjects)):
            top, space = 4.2, 4.5
            wrap = i/4
            by = 60
            wrapX = self.margin+self.cell+(i%4*self.imgWidth)
            wrapY = self.margin*top+self.cell*space*wrap
            canvas.create_image(wrapX, wrapY, image=self.myObjects[i])
            canvas.create_window(wrapX, wrapY+by, window=self.bagButtons[i])
        if self.myObjects == []:
            canvas.create_text(self.game.mazeCols*self.cell/2,
            self.game.mazeRows*self.cell/2, text=self.noItems,
            font="Helvetica 12")

############################## SHOP ##############################

    def initShopButtons(self):
        self.sec3Button = Button(self.canvas, text="Buy for $400",
            command=self.sec3Button, font="Helvetica 11")
        self.sec5Button = Button(self.canvas, text="Buy for $500",
            command=self.sec5Button, font="Helvetica 11")
        self.sec10Button = Button(self.canvas, text="Buy for $900",
            command=self.sec10Button, font="Helvetica 11")
        self.sec15Button = Button(self.canvas, text="Buy for $1200",
            command=self.sec15Button, font="Helvetica 11")
        self.mysteryButton = Button(self.canvas, text="Buy for $2500",
            command=self.mysteryButton, font="Helvetica 11")
        self.lifeButton = Button(self.canvas, text="Buy for $5000",
            command=self.lifeButton, font="Helvetica 11")
        self.glassesButton = Button(self.canvas, text="Buy for $2000",
            command=self.glassesButton, font="Helvetica 11")
        self.visiButton = Button(self.canvas, text="Buy for $10000",
            command=self.visiButton, font="Helvetica 11")

    def sec3Button(self):
        if self.game.money - 400 >= 0:
            self.game.money -= 400
            self.myObjects += [self.sec3potion]
            self.bagButtons += [self.use3button]
        else:
            tkMessageBox.showinfo(self.noMoney, self.noMoney2)

    def sec5Button(self):
        if self.game.money - 500 >= 0:
            self.game.money -= 500
            self.myObjects += [self.sec5potion]
            self.bagButtons += [self.use5button]
        else:
            tkMessageBox.showinfo(self.noMoney, self.noMoney2)

    def sec10Button(self):
        if self.game.money - 900 >= 0:
            self.game.money -= 900
            self.myObjects += [self.sec10potion]
            self.bagButtons += [self.use10button]
        else:
            tkMessageBox.showinfo(self.noMoney, self.noMoney2)

    def sec15Button(self):
        if self.game.money - 1200 >= 0:
            self.game.money -= 1200
            self.myObjects += [self.sec15potion]
            self.bagButtons += [self.use15button]
        else:
            tkMessageBox.showinfo(self.noMoney, self.noMoney2)

    def mysteryButton(self):
        if self.game.money - 2500 >= 0:
            self.game.money -= 2500
            self.myObjects += [self.mysteryPotion]
            self.bagButtons += [self.useMysteryButton]
        else:
            tkMessageBox.showinfo(self.noMoney, self.noMoney2)

    def lifeButton(self):
        if self.game.money - 5000 >= 0:
            self.game.money -= 5000
            self.myObjects += [self.lifePotion]
            self.bagButtons += [self.useLifeButton]
        else:
            tkMessageBox.showinfo(self.noMoney, self.noMoney2)

    def glassesButton(self):
        if self.game.money - 2000 >= 0:
            self.game.money -= 2000
            self.myObjects += [self.glasses]
            self.bagButtons += [self.useGlasses]
        else:
            tkMessageBox.showinfo(self.noMoney, self.noMoney2)

    def visiButton(self):
        if self.game.money - 10000 >= 0:
            self.game.money -= 10000
            self.myObjects += [self.visiCloak]
            self.bagButtons += [self.useVisiButton]
        else:
            tkMessageBox.showinfo(self.noMoney, self.noMoney2)

    def drawShop(self, canvas):
        canvas.create_rectangle(0,0,self.width, self.height, fill="white",
            width=0)
        for i in xrange(len(self.shopObjects)):
            top, space = 4.2, 4.5
            wrap = i/4
            ty, by = 60, 90
            wrapX = self.margin+self.cell+(i%4*self.imgWidth)
            wrapY = self.margin*top+self.cell*space*wrap
            canvas.create_image(wrapX, wrapY, image=self.shopObjects[i])
            canvas.create_text(wrapX, wrapY+ty, text=self.shopText[i],
                font="Helvetica 11", justify=CENTER)
            canvas.create_window(wrapX, wrapY+by, window=self.shopButtons[i])

############################## NEXT LEVEL ##############################

class NextLevel(object):
    def __init__(self, canvas, game):
        self.canvas = canvas
        self.game = game
        self.rows, self.cols = 15, 15
        self.margin, self.cell = 40,40
        self.width = self.cols * self.cell
        self.height = self.rows * self.cell
        self.next = False

        # http://www.1zoom.net/Anime/Kiki's_Delivery_Service/t14/1/
        self.next1 = PhotoImage(file="next1.gif")
        self.next2 = PhotoImage(file="next2.gif")

        # http://hdwallpapersfactory.com/wallpaper/
        # kiki_delivery_service_desktop_1280x1024_hd-wallpaper-743007.jpg
        self.next3 = PhotoImage(file="next3.gif")

        # http://www.arts-wallpapers.com/comic_wallpapers/
        # Kikis%20Delivery%20Service/img1.jpg
        self.next4 = PhotoImage(file="next4.gif")
        self.slides = [self.next1, self.next2, self.next3, self.next4]
        self.choose()

    def choose(self):
        self.image = random.choice(self.slides)

    def draw(self, canvas):
        textY = 50
        canvas.create_image(self.width/2, self.height/2,
            image=self.image)
        canvas.create_text(self.width/2, textY,
            text="Level %d starts in %d"%(self.game.level,
                self.game.countdown), font="Helvetica 20", fill="white")

############################## KIKI ##############################

class Kiki(object):
    def __init__(self):
        self.x, self.y = 13, 13
        self.kx, self.ky = 13, 13
        self.visited = set((14,14))

        # all Kiki images drawn by me!
        self.back = PhotoImage(file="kikiBack.gif")
        self.fwd = PhotoImage(file="kikiFwd.gif")
        self.left = PhotoImage(file="kikiLeft.gif")
        self.right = PhotoImage(file="kikiRight.gif")
        self.image = self.left

    def canMove(self, maze):
        if (self.kx <= 0 or self.kx > self.x or
            self.ky <= 0 or self.ky > self.y):
            return False
        if maze[self.ky][self.kx] == False:
            return False
        return True

    def move(self, drow, dcol, maze):
        self.kx += dcol
        self.ky += drow
        self.visited.add((self.kx, self.ky))
    # check legality for every move
        if self.canMove(maze) == False:
            self.kx -= dcol
            self.ky -= drow

    def draw(self, canvas, row, col, cell):
        self.canvas = canvas
        left, top = col * cell, row * cell
        right, bottom = left + cell, top + cell
        canvas.create_image(self.kx*cell+cell/2, self.ky*cell,
            image=self.image)

############################## OBJECTS ##############################

class Object(object):
    def __init__(self, canvas, maze, cell):
        self.canvas = canvas
        self.maze = maze
        self.mazeRows, self.mazeCols = 15, 15
        self.cell, self.center = cell, cell/2
        self.kx, self.ky = 13, 13
        self.emptySpaces = []

        # http://ec.l.thumbs.canstockphoto.com/canstock16736352.jpg
        self.image = PhotoImage(file="package.gif")

    def place(self):
        for row in xrange(self.mazeRows):
            for col in xrange(self.mazeCols):
                if (self.maze[row][col] == 1 and (row, col) not in
                    self.emptySpaces) and row != self.kx and col != self.kx:
                    self.emptySpaces += [(col, row)]
        # ensures that only one object is placed on a cell
        self.jiji = random.choice(self.emptySpaces)
        self.emptySpaces.remove(self.jiji)
        self.p1 = random.choice(self.emptySpaces)
        self.emptySpaces.remove(self.p1)
        self.p2 = random.choice(self.emptySpaces)
        self.emptySpaces.remove(self.p2)
        self.p3 = random.choice(self.emptySpaces)
        self.emptySpaces.remove(self.p3)
        self.cu = random.choice(self.emptySpaces)
        self.emptySpaces.remove(self.cu)
        self.ci = random.choice(self.emptySpaces)
        self.emptySpaces.remove(self.ci)
        self.pol = random.choice(self.emptySpaces)
        self.emptySpaces.remove(self.pol)

############################## JIJI ##############################

class Jiji(Object):
    def __init__(self, canvas, maze, cell):
        super(Jiji, self).__init__(canvas, maze, cell)
        
        # http://coynino.deviantart.com/art/FanArt-Jiji-337762845
        self.image = PhotoImage(file="jiji.gif")

    def place(self):
        super(Jiji, self).place()
        self.maze[self.jiji[1]][self.jiji[0]] = "jiji"

    def draw(self, pos):
        self.canvas.create_image(self.jiji[0]*self.cell+self.center,
            self.jiji[1]*self.cell+self.center/2, image=self.image)

############################## PACKAGES ##############################

class Package1(Object):
    def place(self):
        super(Package1, self).place()
        self.maze[self.p1[1]][self.p1[0]] = "p1"

    def draw(self, pos):
        self.canvas.create_image(self.p1[0]*self.cell+self.center,
            self.p1[1]*self.cell+self.center, image=self.image)

class Package2(Object):
    def place(self):
        super(Package2, self).place()
        self.maze[self.p2[1]][self.p2[0]] = "p2"

    def draw(self, pos):
        self.canvas.create_image(self.p2[0]*self.cell+self.center,
            self.p2[1]*self.cell+self.center, image=self.image)

class Package3(Object):
    def place(self):
        super(Package3, self).place()
        self.maze[self.p3[1]][self.p3[0]] = "p3"

    def draw(self, pos):
        self.canvas.create_image(self.p3[0]*self.cell+self.center,
            self.p3[1]*self.cell+self.center, image=self.image)

############################## CUSTOMER ##############################

# customer images by moedini on deviantART
class Customer(Object):
    def __init__(self, canvas, maze, cell):
        super(Customer, self).__init__(canvas, maze, cell)

        # http://moedini.deviantart.com/art/No-Face-213987682
        self.c1 = PhotoImage(file="customer1.gif")
        # http://moedini.deviantart.com/art/Totoro-256342308
        self.c2 = PhotoImage(file="customer2.gif")
        self.customers = [self.c1, self.c2]
        self.image = random.choice(self.customers)

    def place(self):
        super(Customer, self).place()
        self.maze[self.cu[1]][self.cu[0]] = "customer"

    def draw(self, canvas, cell):
        self.canvas.create_image(self.cu[0]*self.cell+self.center,
            self.cu[1]*self.cell, image=self.image)

############################## CIVILIAN ##############################

# civilian images by moedini on deviantART
class Civilian(Object):
    def __init__(self, canvas, maze, cell):
        super(Civilian, self).__init__(canvas, maze, cell)

        # http://moedini.deviantart.com/art/Chihiro-212733110
        self.c1 = PhotoImage(file="civilian1.gif")
        # http://moedini.deviantart.com/art/Ponyo-213544678
        self.c2 = PhotoImage(file="civilian2.gif")
        # http://moedini.deviantart.com/art/Princess-Mononoke-213868400
        self.c3 = PhotoImage(file="civilian3.gif")

        self.civilians = [self.c1, self.c2, self.c3]
        self.image = random.choice(self.civilians)

    def place(self):
        super(Civilian, self).place()
        self.maze[self.ci[1]][self.ci[0]] = "civilian"

    def draw(self, canvas, cell):
        self.canvas.create_image(self.ci[0]*self.cell+self.center,
            self.ci[1]*self.cell, image=self.image)

############################## POLICEMAN ##############################

class Policeman(Object):
    def __init__(self, canvas, maze, cell):
        super(Policeman, self).__init__(canvas, maze, cell)

        # policeman image drawn by me!
        self.image = PhotoImage(file="police.gif")

    def place(self):
        super(Policeman, self).place()
        self.maze[self.pol[1]][self.pol[0]] = "police"

    def draw(self, canvas, cell):
        self.canvas.create_image(self.pol[0]*self.cell+self.center,
            self.pol[1]*self.cell-self.center/2, image=self.image)

############################## LEVEL EDITOR ##############################

class LevelEditor(object):
    def __init__(self, canvas, width, height, game):
        self.canvas = canvas
        self.width, self.height = width, height
        self.game = game
        self.position = []
        self.initMaze()
        self.createWalls()
        self.loadImage = PhotoImage(file="loadbutton.gif")
        self.clearImage = PhotoImage(file="clearbutton.gif")
        self.returnImage = PhotoImage(file="returnbutton.gif")
        self.text = "Click anywhere to begin!\
        \n\nWhite squares are walls.\
        \nPatterned squares are paths.\
        \n\nClick again to toggle\
        \nbetween walls and paths."

    def initMaze(self):
        self.mazeRows, self.mazeCols = 15, 15
        self.x, self.y = 13, 13
        self.maze = []
        self.maze += [[0]*self.mazeCols for row in xrange(self.mazeRows)]
        for row in xrange(self.mazeRows):
            for col in xrange(self.mazeCols):
                if (row == 0 or row == self.mazeRows-1 or col == 0 or
                    col == self.mazeCols-1):
                    self.maze[row][col] = 0
                if row == self.x and col == self.y:
                    self.maze[row][col] = 1

    def createWalls(self):
        self.walls = copy.deepcopy(self.maze)
        for row in xrange(self.mazeRows):
            for col in xrange(self.mazeCols):
                if self.walls[row][col] == 0:
                    self.walls[row][col] = self.game.house
                else:
                    self.walls[row][col] = self.game.ground

    def drawMaze(self):
        for row in xrange(self.mazeRows):
            for col in xrange(self.mazeCols):
                wall = self.walls[row][col]
                self.drawMazeCells(row, col, wall)

    def drawMazeCells(self, row, col, wall):
        left, top = col * self.game.cell, row * self.game.cell
        right, bottom = left + self.game.cell, top + self.game.cell
        self.canvas.create_image(left+self.game.cell/2, top+self.game.cell/2,
            image=wall)

    def drawMenu(self):
        startRow, startCol = 0, 15
        textX = self.game.menuCenter+10
        textY, clearY, retY = 100, 100, self.height-38
        self.canvas.create_rectangle(self.game.cell*startCol, 0,
            self.width, self.height, fill="black", width=0)
        self.canvas.create_text(textX, textY, text=self.text,
            fill="white", font="Helvetica 12")
        # menu
        self.canvas.create_image(self.game.menuCenter, self.height/2,
            image=self.loadImage)
        self.canvas.create_image(self.game.menuCenter, self.height/2+clearY,
            image=self.clearImage)
        self.canvas.create_image(self.game.menuCenter, retY,
            image=self.returnImage)

############################## RUN ##############################

tp = KikisDeliveryService()
tp.run()
