import random, os, sys, console, console.utils
from InpAndVal import getInput
from copy import deepcopy
from console import fg, bg, fx

#remove the SPace class.. it adds nothing and only complicates things

#Global variables
gameversion = '2.0'
indent = ' '*2
banner = """

                         ███████████ ███                      ███                              
                        ░█░░░███░░░█░░░                      ░░░                               
                        ░   ░███  ░ ████   ███████ ████████  ████  █████                       
                            ░███   ░░███  ███░░███░░███░░███░░███ ███░░                        
                            ░███    ░███ ░███ ░███ ░███ ░░░  ░███░░█████                       
                            ░███    ░███ ░███ ░███ ░███      ░███ ░░░░███                      
                            █████   █████░░███████ █████     ███████████                       
                           ░░░░░   ░░░░░  ░░░░░███░░░░░     ░░░░░░░░░░░                        
                                          ███ ░███ ██████                                      
                                         ░░██████ ███░░███                                     
                                          ░░░░░░ ░░██████                                      
                                                  ██████                                       
                                                ░███░░███                                      
                                                ░███ ░░███                                     
             ██████████                   █████ ░░█████░███            █████                   
            ░░███░░░░░█                  ░░███   ░░░░░ ░░░            ░░███                    
             ░███  █ ░ █████ ████████████ ░███████  ████████  ██████  ███████    ██████  █████ 
             ░██████  ░░███ ░███░░███░░███░███░░███░░███░░███░░░░░███░░░███░    ███░░██████░░  
             ░███░░█   ░███ ░███ ░███ ░███░███ ░███ ░███ ░░░  ███████  ░███    ░███████░░█████ 
             ░███ ░   █░███ ░███ ░███ ░███░███ ░███ ░███     ███░░███  ░███ ███░███░░░  ░░░░███
             ██████████░░████████░███████ ████ ██████████   ░░████████ ░░█████ ░░██████ ██████ 
            ░░░░░░░░░░  ░░░░░░░░ ░███░░░ ░░░░ ░░░░░░░░░░     ░░░░░░░░   ░░░░░   ░░░░░░ ░░░░░░  
                                 ░███                                                          
                                 █████                                                         \n\n"""

class Game():
	'''
	Game state class, containing not just the board, but also the tile bag, list of kingdoms
	and dict of players.
	'''
	std_temples = ((0,10),(2,5),(4,13),(6,8),(9,5),(10,10),(1,1),(1,15),(7,1),(8,14)) #four last are the ones with borders
	std_rivers = ((0,4),(0,5),(0,6),(0,7),(0,8),(0,12),(1,4),(1,12),(2,3),(2,4),(2,12),(2,13),(3,0),(3,1),(3,2),(3,3),(3,13),(3,14),(3,15),(4,14),(4,15),(5,14),(6,0),(6,1),(6,2),(6,3),(6,12),(6,13),(6,14),(7,3),(7,4),(7,5),(7,6),(7,12),(8,6),(8,7),(8,8),(8,9),(8,10),(8,11),(8,12))
	adv_temples = ((0,4),(0,9),(1,14),(3,6),(3,11),(5,3),(7,7),(7,12),(2,1),(5,15),(7,0),(9,4),(10,9),(10,14)) #six last are the ones with borders
	adv_rivers = ((0,2),(0,3),(1,2),(1,3),(2,2),(2,3),(3,2),(4,2),(5,2),(6,2),(6,3),(7,3),(7,4),(7,5),(8,5),(8,6),(8,7),(9,6),(10,6),(9,7),(9,8),(9,9),(9,10),(9,11),(9,12),(9,13),(8,13),(7,13),(6,13),(6,12),(5,12),(4,12),(3,12),(3,13),(3,14),(3,15),(2,15),(1,15),(0,15))
	def __init__(self):
		self.side = 's'
		self.coords = dict()
		self.monuments = [Piece('monument','black+blue'),Piece('monument','black+green'),Piece('monument','black+red'),Piece('monument','red+blue'),Piece('monument','blue+green'),Piece('monument','green+red')]
		self.kingdoms = []
		self.players = dict() #Bull, Hunter, Pot, Lion
		self.treasures = 0
		self.bag = []
		self.gameSetup()
		self.turnLoop()
		
	def gameSetup(self):
		'''
		Sets up the board and players
		'''
		print(f'{indent}Welcome to Tigris & Euphrates v{gameversion}!')
		pmap = {0:'Bull',1:'Hunter',2:'Pot',3:'Lion'}
		#Initialize board
		std_or_adv = getInput(f'{indent}Play on the [s]tandard or [a]dvanced board?', 'char', extra_cond='sa')
		self.side = std_or_adv
		if self.side == 's':
			borders = 4
			temples = self.std_temples
			rivers = self.std_rivers
		else:
			borders = 6
			temples = self.adv_temples
			rivers = self.adv_rivers
		self.bag = self.initBag(len(temples))
		for row in range(11):
			for col in range(16):
				ct, rv, tr, bd  = None, False, False, False #content, river, treasure, border
				if (row,col) in temples:
					self.treasures += 1
					tr = True
					ct = Piece('tile','red', coord=(row,col))
					if (row,col) in temples[-borders:]:
						bd = True
				elif (row,col) in rivers:
					rv = True
				self.coords[(row,col)] = Space((row,col), ct, rv, tr, bd)
		#Add players
		howmany = getInput(f'{indent}How many players [2 to 4]?', 'int', extra_cond=(2,4))
		for x in range(howmany):
			self.addPlayer(pmap[x])

	def initBag(self,temples):
		'''
		Initializes the bag of tiles.
		'''
		bag = []
		for red in range(57-temples):
			bag.append(Piece('tile','red'))
		for black in range(30):
			bag.append(Piece('tile','black'))
		for blue in range(36):
			bag.append(Piece('tile','blue'))
		for green in range(30):
			bag.append(Piece('tile','green'))
		random.shuffle(bag)
		return bag

	def addPlayer(self, faction):
		'''
		Adds players to dict of players.
		'''
		self.players[faction] = Player(faction)
		self.players[faction].drawTiles(self)

	def turnLoop(self): #review prints after player stuff is rewritten
		'''
		Basic game loop
		'''
		rnd=0
		while True:
			rnd += 1
			for player, pobj in self.players.items():
				self.printBoard()
				print(f"{indent}{fx.bold}Round {rnd}.\n{indent}{player}'s turn.{fx.default}")
				pobj.playTurn(self)
				self.endTurnScore(pobj)
				for player in self.players.values():
					player.drawTiles(self)
				if self.checkEndGame():
					return self.endGame()

	def printBoard(self): 
		'''
		Prints the board.
		'''
		sep = indent + (' '*3) + '+---'*16 + '+'
		hcoords = '    '
		for x in range(16):
			hcoords += f'{x}'.center(4)
		print(indent + hcoords)
		print(sep)
		for r in range(11):
			linetoprint = '|'
			for k, v in self.coords.items():
				if k[0] == r:
					linetoprint += v.style + '|'
			print(indent + str(r).center(3) + linetoprint + '\n' + sep)
		print('')

	


class Space():
	'''
	Container class for every space in the board.
	'''
	bgfg = {
		'red': bg.red+fg.black,
		'black': bg.lightblack+fg.black
		'green': bg.green+fg.black
		'blue': bg.blue+fg.black
	}
	styles = {
		'catastrophe': bg.yellow+fg.black+' % '+fx.default,
		'tile': 'bgfg'+' . '+fx.default,
		'leader': 'bgfg'+' X '+fx.default,
		'monument': 'half1'+' .'+'half2'+' '+fx.default,
		'None': '   ',
		'river': bg.cyan+fg.blue+' r '+fx.default

	}

	def __init__(self, coord, content, river, treasure, border):
		self.coord = coord
		self.content = content
		self.river = river
		self.treasure = treasure
		self.border = border
		self.style = self.setStyle()
		self.neighbors = self.findNeighbors(self.coord)

	def setStyle(self): 
		if self.content:
			if self.content.ptype == 'monument'
				colors = self.content.color.split('+')
				style = self.styles[self.content.ptype].replace('half1', self.bgfg[colors[0]]).replace('half2', self.bgfg[colors[0]])
			else:
				style = self.styles[self.content.ptype].replace('bgfg', self.bgfg[self.content.color]).replace('X',self.content.faction[0])
				if self.content.treasure:
					if self.content.border:
						style = style.replace(f'{fg.black} .', f'{fg.white} +')
					else:
						style = style.replace(f'{fg.black} .', f'{fg.yellow} +')
		elif self.river:
			style = self.styles['river']
		else:
			style = '   '
		return style

	def findNeighbors(self,coord):
		neighbors = [(x,y) for x in range(coord[0]-1,coord[0]+2) if x>=0 and x<=10
			for y in range(coord[1]-1,coord[1]+2) if y>=0 and y <=15
			if (x,y) != coord]
		return neighbors

	def checkValidPlacement(self, piece, board_instance): #review
		if self.content:
			if self.content.ptype in ['monument','catastrophe','leader']:
				return False
			elif self.treasure or piece.ptype != 'catastrophe':
				return False
		elif piece.ptype == 'tile':
			if piece.color == 'blue' and not self.river:
				return False
			elif piece.color != 'blue' and self.river:
				return False
			if board_instance.checkKingdomsBorders(self)[0] > 2: #review
				return False
		elif piece.ptype == 'leader': 
			if self.river:
				return False
			if all([board_instance.coords[x].content.ptype != 'tile' or board_instance.coords[x].content.color != 'red' for x in self.neighbors if board_instance.coords[x].content]):
				return False
			if board_instance.checkKingdomsBorders(self, piece)[0] > 1: #review
				return False
		return True

class Piece():
	def __init__(self, ptype, color='', faction=None, coord=None):
		self.ptype = ptype
		self.color = color
		self.faction = faction
		self.coord = coord

class Player():
	def __init__(self, faction):
		self.faction=faction
		self.points = {'red':0,'black':0,'blue':0,'green':0}
		self.treasures=0
		self.leaders={'red':Piece('leader','red',faction),'black':Piece('leader','black',faction),'blue':Piece('leader','blue',faction),'green':Piece('leader','green',faction),}
		self.catastrophes=[Piece('catastrophe'),Piece('catastrophe')]
		self.hand=[]

	def drawTiles(self, board_instance): #remember! end game has to do sys.exit()
		if len(self.hand) < 6:
			random.shuffle(board_instance.bag)
			for _ in range(6-len(self.hand)):
				try:
					self.hand.append(board_instance.bag.pop())
				except IndexError:
					print(f'{fg.red}No more tiles to draw. Final scoring...{fx.default}')
					return board_instance.endGame()

	def discardTiles(self, board_instance, *tiles):
		for tile in tiles:
			self.hand.remove(tile)
		self.drawTiles(board_instance)

	def playTurn(self, board_instance, moves=2):
		'''
		Individual turn loop.
		'''
		fgs = {'red':fg.red,'black':fg.lightblack,'blue':fg.blue,'green':fg.green} #maybe put this elsewhere
		counts = {'r':sum(tile.color == 'red' for tile in self.hand),'b':sum(tile.color == 'black' for tile in self.hand),'l':sum(tile.color == 'blue' for tile in self.hand),'g':sum(tile.color == 'green' for tile in self.hand),'c':len(self.catastrophes)}
		mapping = {'r':'red','b':'black','l':'blue','g':'green','e':'red','k':'black','u':'blue','n':'green'}
		player_hand = f"{indent}{self.faction}'s hand: {fg.red}{counts['r']} red{fx.default} | {fg.lightblack}{counts['b']} black{fx.default} | {fg.blue}{counts['l']} blue{fx.default} | {fg.green}{counts['g']} green{fx.default} | {fg.yellow}{counts['c']} catastrophes{fx.default}\n"
		player_ldrs = f"{indent}{self.faction}'s leaders: {fg.red}{self.leaders['red'].coord or 'N/A'} red{fx.default} | {fg.lightblack}{self.leaders['black'].coord or 'N/A'} black{fx.default} | {fg.blue}{self.leaders['blue'].coord or 'N/A'} blue{fx.default} | {fg.green}{self.leaders['green'].coord or 'N/A'} green{fx.default}\n"
		player_points = f"{indent}{self.faction}'s points: {fg.red}{self.points['red']} red{fx.default} | {fg.lightblack}{self.points['black']} black{fx.default} | {fg.blue}{self.points['blue']} blue{fx.default} | {fg.green}{self.points['green']} green{fx.default} | {fg.magenta}{self.treasures} treasures{fx.default}\n"
		player_moves_left = f"{indent}Moves left: {moves}\n"
		allinfo = player_hand + player_ldrs + player_points + player_moves_left
		print(allinfo, end='\n\n')

		possible_picks = ''.join([k for k,v in counts.items() if v != 0]) + 'ekunda'
		pick_prompt = f'{indent}What would you like to do?\n{indent}Play a tile   - {fg.red}[r]{fx.default}ed {fg.lightblack}[b]{fx.default}lack b{fg.blue}[l]{fx.default}ue {fg.green}[g]{fx.default}reen {fg.yellow}[c]{fx.default}atastrophe\n{indent}Play a leader - r{fg.red}[e]{fx.default}d blac{fg.lightblack}[k]{fx.default} bl{fg.blue}[u]{fx.default}e gree{fg.green}[n]{fx.default}\n{indent}Re{fx.bold}[d]{fx.default}raw tiles or p{fx.bold}[a]{fx.default}ss?'
		pick = getInput(pick_prompt, 'char', extra_cond=possible_picks)
		if pick == 'a':
			pass
		elif pick != 'd':
			space_prompt = f"{indent}Place piece on which space (0,0 to 10,15)?"
			space = getInput(space_prompt, 'coord', extra_cond=((0,10),(0,15)))
			if pick in 'rblg':
				piece = next(tile for tile in self.hand if tile.color == mapping[pick])
			elif pick == 'c':
				piece = self.catastrophes[-1]
			else:
				piece = self.leaders[mapping[pick]]
			if not self.placePiece(piece, space, board_instance):
				return self.playTurn(board_instance, moves=moves)
		else:
			possible_discards = ''.join(map(str, range(1,len(self.hand)+1)))
			discard_prompt = f"{indent}Select tiles to discard (e.g. 124):"
			print(indent, end='')
			for i, tile in enumerate(self.hand):
				print(f'{i+1}: {fgs[tile.color]}{tile.color}{fx.default}  ', end='')
			print('')
			todiscard = getInput(discard_prompt, 'string', extra_cond=possible_discards, maxlen=len(possible_discards))
			todiscard = [self.hand[int(ind)-1] for ind in todiscard]
			self.discardTiles(board_instance, *todiscard)
		
		moves -= 1
		if moves > 0:
			board_instance.printBoard()
			return self.playTurn(board_instance, moves=moves)
		else:
			return True

	def placePiece(self, piece, space, board_instance): #review
		'''
		Checks valid placement and calls a bunch of functions to update board state.
		'''
		if not board_instance[space].checkValidPlacement(piece, board_instance):
			board_instance.printBoard()
			print(f"{indent}{fg.red}{self.faction}'s {piece.color} {piece.ptype} cannot be placed on {space}.{fx.default}", end='\n\n')
			return False
		else:
			old_coord = None
			if piece.ptype == 'leader':
				if piece.coord:
					board_instance.coords[piece.coord].content = None
				piece.coord = space
			elif piece.ptype == 'catastrophe':
				self.catastrophes.pop()
			else:
				self.hand.remove(piece)
			board_instance.coords[space] = piece
			board_instance.checkLeaders()
			if piece.ptype == 'tile':
				howmany, kingdoms = board_instance.checkKingdomsJustPlacedTile(space)
				if howmany == 1:
					board_instance.tileScore(piece.color, space, kingdoms)
				candidates = board_instance.checkMonumentPlacement(space, piece.color)
				if len(candidates) > 0:
					self.placeMonument(candidates, piece.color, board_instance)
			board_instance.kingdoms = board_instance.updateKingdoms(space, self, piece)
			
			return True