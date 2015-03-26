#!/usr/bin/env python
"""
This simple example is used for the line-by-line tutorial
that comes with pygame. It is based on a 'popular' web banner.
Note there are comments here, but for the full explanation, 
follow along in the tutorial.
"""


#Import Modules
import os, pygame, sys, random, math
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'


#functions to create our resources
def load_image(name, colorkey=None):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', fullname
		raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()

def load_sound(name):
	class NoneSound:
		def play(self): pass
	if not pygame.mixer or not pygame.mixer.get_init():
		return NoneSound()
	fullname = os.path.join('data', name)
	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		print 'Cannot load sound:', fullname
		raise SystemExit, message
	return sound

#classes for our game objects
class Square(pygame.sprite.Sprite):
	def __init__(self, x, y, b, s):	#, h=44):
		pygame.sprite.Sprite.__init__(self)
		self.isbrick = b
		self.issand = s
		self.x = x
		self.y = y
		
		#self.health=h

		if(b and s):
			self.image = pygame.image.load("sprites/bricksand.png").convert_alpha()
			self.rect = pygame.Rect(x*24, (y*24)-96, self.image.get_rect().width, self.image.get_rect().height)
		elif(b):
			self.isbrick = True
			self.image = pygame.image.load("sprites/brick.png").convert_alpha()
			self.rect = pygame.Rect(x*24, (y*24)-96, self.image.get_rect().width, self.image.get_rect().height)
		elif(s):
			self.issand = True
			self.image = pygame.image.load("sprites/sand.png").convert_alpha()
			self.rect = pygame.Rect(x*24, (y*24)-96, self.image.get_rect().width, self.image.get_rect().height)

#Bricks having health led to less chance of dieing and lower scores
#This type of situation is exactly what we were trying to avoid by adding death from red blocks reaching the bottom
#Because of this I am commenting out my Square health implementation
#def updateSquares(player, grid):
#	for x in range(0, len(grid)):
#		for y in range(0, len(grid[0])):
#			if grid[x][y].issand and grid[x][y].isbrick:
#				grid[x][y].health-=1
#				if grid[x][y].health<1:
#					grid[x][y]=Square(x,y,False,True)
#					player.bank-=1
#					if player.bank<0:
#						player.bank=0
		
class Player(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("sprites/player.png").convert_alpha()
		self.rect = pygame.Rect(-12, 0, self.image.get_rect().width, self.image.get_rect().height)
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		
		self.pos = 0
		self.maxPos = 19
		self.attacks = 0
		dir = 0
		
		self.animating=False
		
		self.score = 0
		self.bank = 0
		self.mult = 1
		self.alive = True
		
		self.font = pygame.font.Font('data/impact.ttf', 18)
		self.lfont = pygame.font.Font('data/impact.ttf', 35)
		self.loseTXT=self.lfont.render('',1,(0,0,0))
		self.scoreTXT=self.font.render(str(self.score),1,(0,0,0))
		self.attacksTXT=self.font.render(str(self.attacks),1,(0,0,0))
		self.bankTXT=self.font.render(str(self.bank),1,(0,0,0))
		self.multTXT=self.font.render(str(self.mult),1,(0,0,0))
	
	def move(self, dir):
		self.moving = True
		self.dir=dir
		if dir > 0 and self.pos<self.maxPos:
			self.image=pygame.image.load("sprites/player_down.png").convert_alpha()
			self.animating=True
			self.pos+=1
			self.rect = self.rect.move(self.image.get_rect().width/2,0)
			#print "yay"
		elif dir > 0 and self.pos==self.maxPos:
			self.image=pygame.image.load("sprites/player_down.png").convert_alpha()
			self.animating=True
			self.pos=0
			self.rect = self.rect.move(-19*self.image.get_rect().width/2,0)
		elif dir < 0 and self.pos > 0:
			self.image=pygame.image.load("sprites/player_down.png").convert_alpha()
			self.animating=True
			self.pos-=1
			self.rect = self.rect.move(-1*self.image.get_rect().width/2,0)
		elif dir < 0 and self.pos==0:
			self.image=pygame.image.load("sprites/player_down.png").convert_alpha()
			self.animating=True
			self.pos=self.maxPos
			self.rect = self.rect.move(19*self.image.get_rect().width/2,0)
			#print "yeah"
	
	def drill(self, grid):
		self.image=pygame.image.load("sprites/player_up.png").convert_alpha()
		self.animating=True
		if self.bank>0:
			self.mult=1
		if grid[self.pos][len(grid[self.pos])-1].isbrick:
			self.mult=1
			self.bank-=1
			if self.bank<0:
				self.bank=0
		elif grid[self.pos][len(grid[self.pos])-1].issand:
			grid[self.pos][len(grid[self.pos])-1]=Square(self.pos, len(grid[self.pos])-1, False, False)
			drillCol(self.pos, grid)
			
	def attack(self, grid):
		if self.attacks > 0:
			for x in range(0,20):
				if grid[x][len(grid[0])-2].issand:
					grid[x][len(grid[0])-2] = Square(x,len(grid[0])-2,False,True)
			self.attacks -= 1

def drillCol(x, grid):
	y=len(grid[x])-1
	if x >=0 or x<20:
		for i in range(0, y):
			if grid[x][y-1-i].issand:
				grid[x][y-i]=Square(x, y-i, grid[x][y-1-i].isbrick, grid[x][y-1-i].issand)
			else:
				grid[x][y-i]=Square(x, y-i, False, False)
				return

def moveGrid(grid, player):
	l=len(grid[0])-1
	gainMult=False
	for x in range(0, len(grid)):
		for y in range(0, len(grid[x])-1):
			if grid[x][l-1-y].issand or grid[x][l-1-y].isbrick:
				if not(grid[x][l-y].issand or grid[x][l-y].isbrick):
					if y==0:
						grid[x][l-y]=Square(x, l-y, True, True)
						gainMult=True
						player.bank+=1
					else:
						if grid[x][l-y+1].issand:
							grid[x][l-y]=Square(x, l-y, grid[x][l-1-y].isbrick, True)
							gainMult=True
							player.bank+=1
						else:
							grid[x][l-y]=Square(x, l-y, grid[x][l-1-y].isbrick, grid[x][l-1-y].issand)
					grid[x][l-1-y]=Square(x, l-1-y, False, False)
				#elif (not grid[x][l-1-y].issand and grid[x][l-y].issand):
				#	grid[x][l-1-y]=Square(x, l-1-y, True, True)
				#	gainMult=True
				#	player.bank+=1
	if gainMult:
		player.mult+=1

def detectLine(grid,player,sfx_flat):
	flat = True
	above = False
	row = 0

	found = False
	for y in range(0,len(grid[0])):
		if grid[0][y].issand and not(found):
			row = y
			found = True

	for x in range(0,20):	
		if not(grid[x][row].issand):
			flat = False

	for x in range(0,20):	
		if grid[x][row-1].issand:
			above = True
						
	if (not(above) and flat):
		for y in range(row, len(grid[0])):
			for x in range(0,20):
				grid[x][y] = Square(x,y,False,True)
		attack_mod = (player.bank*player.mult) / 75
		player.attacks += attack_mod
		player.score += player.bank*player.mult
		player.bank = 0
		player.mult = 1
		#sfx_flat.play()

def generateBricks(grid):
	generate = random.randint(0,9)
	if(generate == 0 or generate == 1):
		generate = True
	if(generate):
		start = random.randint(0,20)
		for x in range(start, start+2):
			for y in range(0,2):
				brick = random.randint(0,1)
				if(brick == 0):
					if(x<20):
						grid[x][y] = Square(x,0,True,False)

def stillPlaying(grid,player):
	for x in range(0,20):
		for y in range(0,4):
			if grid[x][y].issand:
				player.alive = False
	for x in range(0,20):
		if grid[x][len(grid[0])-1].isbrick:
			player.alive = False

def updateHUD(player):
	player.scoreTXT=player.font.render(str(player.score),1,(0,0,0))
	player.attacksTXT=player.font.render(str(player.attacks),1,(0,0,0))
	player.multTXT=player.font.render(str(player.mult),1,(0,0,0))
	player.bankTXT=player.font.render(str(player.bank),1,(0,0,0))
		
def main():
	"""this function is called when the program starts.
	   it initializes everything it needs, then runs in
	   a loop until the function returns."""
#Initialize Everything
	pygame.init()
	screen = pygame.display.set_mode((600, 720))
	pygame.display.set_caption('Mr. Flatland!')
	pygame.mouse.set_visible(0)

#Create The Backgound
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((250, 250, 250))
	backgroundImg = pygame.image.load('data/sky.png')
	backgroundImgRect = backgroundImg.get_rect()
	
#Put Text On The Background, Centered
	#if pygame.font:
		#font = pygame.font.Font(None, 36)
		#text = font.render("Mr. Flatland Rocks!", 1, (10, 10, 10))
		#textpos = text.get_rect(centerx=background.get_width()/2)
		#backgroundImg.blit(text, textpos)

#Display The Background
	screen.blit(background, (0,0))
	screen.blit(backgroundImg, backgroundImgRect)
	pygame.display.flip()
	
#Prepare Game Objects
	#Load Sounds
	music_bg = load_sound('background.wav')
	sfx_dig = load_sound('dig.wav')
	sfx_flat = load_sound('flat.wav')
	sfx_boo = load_sound('boo.wav')

	pygame.mixer.find_channel().play(music_bg, -1, 0)
	
	clock = pygame.time.Clock()
	player = Player()
	allsprites = pygame.sprite.RenderPlain((player))
	
	seconds = 0
	quarterSeconds=0
	fastScroll=False
	genTimer = random.randint(1,5)

	#Game Setup
	#Empty space
	grid = []
	for x in range(0,20):
		grid.append([])
		for y in range(0,32):
			grid[x].append(Square(x,y,False,False))

	#Sand
	for x in range(0,20):
		for y in range(20,32):
			grid[x][y] = Square(x,y,False,True)

#Main Loop
	while 1:
		clock.tick()
		
		if seconds < pygame.time.get_ticks()/1000.0 and player.alive:
			increment = (-0.14 * math.log(player.score+.0000001, 2.71828183)) + 1.386
			if fastScroll:
				seconds+=.05
			elif increment>1:
				seconds+=1
			elif increment<.1:
				seconds+=.1
			else:
				seconds+= increment
			#put code here that happens every second!
			#updateSquares(player, grid)
			detectLine(grid,player,sfx_flat)
			moveGrid(grid, player)
			stillPlaying(grid,player)
			if(int(seconds) % genTimer == 0):
				max = 5-int(player.score/2000.0)
				if max<1:
					max=1
				genTimer = random.randint(1,max)
				generateBricks(grid)
			updateHUD(player)
		elif not player.alive:
			player.loseTXT = player.lfont.render('you lose!',1,(0,0,0))
			sfx_boo.play()
		
		if quarterSeconds < pygame.time.get_ticks()/1000.0:
			quarterSeconds+=.25
			if player.animating:
				player.image=pygame.image.load("sprites/player.png").convert_alpha()
				player.animating=False
			#put stuff like the player animation here!
		
	
	#Handle Input Events
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					return
				elif event.key == pygame.K_RIGHT:
					player.move(1)
					#print "right"
				elif event.key == pygame.K_LEFT:
					player.move(-1)
					#print "left"
				elif event.key == pygame.K_SPACE:
					player.drill(grid)
					sfx_dig.play()
				elif event.key == pygame.K_UP:
					player.attack(grid)
				elif event.key == pygame.K_DOWN:
					fastScroll=True
			elif event.type == KEYUP:
				if event.key == K_DOWN:
					fastScroll=False

		allsprites.update()

	#Draw Everything
		screen.blit(background, (0,0))
		screen.blit(backgroundImg, backgroundImgRect)

		for x in range(0,20):
			for y in range(0,len(grid[0])):
				if(grid[x][y].issand or grid[x][y].isbrick):
					screen.blit(grid[x][y].image, grid[x][y].rect)
		
		screen.blit(player.loseTXT, (190,325,0,0))
		screen.blit(player.scoreTXT,(492,587,0,0))
		screen.blit(player.attacksTXT,(492,620,0,0))
		screen.blit(player.bankTXT,(505,430,0,0))
		screen.blit(player.multTXT,(505,508,0,0))
		allsprites.draw(screen)
		pygame.display.flip()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()
