gameversion = '1.0'
import random
from copy import deepcopy
import os
import sys
import colorama
from colorama import Fore, Back, Style


class Piece():
	def __init__(self,ptype,color='',faction=None,treasure=False,border=False):
		self.ptype = ptype
		self.color = color
		
		self.treasure = treasure
		self.border = border
		self.faction = faction
		self.coord = None
		self.style = self.setStyle()

	def setStyle(self): 
		if self.ptype == 'catastrophe':
			return Back.YELLOW + Fore.BLACK + ' % ' + Style.RESET_ALL
		elif self.ptype == 'tile':
			if self.treasure:
				if self.border:
					return Back.RED + Fore.WHITE + ' + ' + Style.RESET_ALL
				return Back.RED + Fore.YELLOW + ' + ' + Style.RESET_ALL
			elif self.color == 'black':
				return Back.WHITE + Fore.BLACK + ' . ' + Style.RESET_ALL
			else:
				return getattr(Back, self.color.upper()) + Fore.BLACK + ' . ' + Style.RESET_ALL
		elif self.ptype == 'leader':
			if self.color == 'black':
				return Back.WHITE + Fore.BLACK + ' ' + self.faction[0] + ' ' + Style.RESET_ALL
			else:
				return getattr(Back, self.color.upper()) + Fore.WHITE + ' ' + self.faction[0] + ' ' + Style.RESET_ALL
		elif self.ptype == 'monument':
			if self.color.split('+')[0] == 'black':
				half1 = Back.WHITE + Fore.BLACK + ' .' + Style.RESET_ALL
			else:
				half1 = getattr(Back, self.color.split('+')[0].upper()) + Fore.BLACK + ' .' + Style.RESET_ALL
			if self.color.split('+')[1] == 'black':
				half2 = Back.WHITE + Fore.BLACK + ' ' + Style.RESET_ALL
			else:
				half2 = getattr(Back, self.color.split('+')[1].upper()) + Fore.BLACK + ' ' + Style.RESET_ALL
			if self.treasure:
				half1 = half1.replace(f'{Fore.BLACK} .', f'{Fore.YELLOW} +')
			self.style = half1+half2



class Player():
	def __init__(self,faction):
		self.faction=faction
		self.points = {'red':0,'black':0,'blue':0,'green':0}
		self.treasures=0
		self.leaders={'red':Piece('leader','red',faction),'black':Piece('leader','black',faction),'blue':Piece('leader','blue',faction),'green':Piece('leader','green',faction),}
		self.catastrophes=[Piece('catastrophe'),Piece('catastrophe')]
		self.hand=[]

	def drawTiles(self, board_instance):
		if len(self.hand) < 6:
			random.shuffle(board_instance.bag)
			for _ in range(6-len(self.hand)):
				try:
					self.hand.append(board_instance.bag.pop())
				except IndexError:
					print('No more tiles to draw. Final scoring...')
					return board_instance.endGame()
					

	def discardTiles(self, board_instance, *tiles):
		for tile in tiles:
			self.hand.remove(tile)
		self.drawTiles(board_instance)

	def placePiece(self, piece, space, board_instance): 
		if not board_instance.checkValidPlacement(piece,space):
			board_instance.printBoard()
			print(f"{Fore.RED}{self.faction}'s {piece.color} {piece.ptype} cannot be placed on {space}.")
			return False
		else:
			if piece.ptype == 'leader':
				if piece.coord:
					board_instance.coords[piece.coord] = None
				piece.coord = space
			elif piece.ptype == 'catastrophe':
				self.catastrophes.pop()
			else:
				self.hand.remove(piece)
			board_instance.coords[space] = piece
			board_instance.checkLeaders()
			if piece.ptype == 'tile':
				candidates = board_instance.checkMonumentPlacement(space, piece.color)
				if len(candidates) > 0:
					self.placeMonument(candidates, piece.color, board_instance)
			board_instance.kingdoms, score = board_instance.updateKingdoms(space, self)
			if piece.ptype == 'tile' and score:
				board_instance.tileScore(piece.color, space)
			return True

	def placeMonument(self, candidates, color, board_instance, hastr=False):
		a1, a2, a3 = '','',''
		while not a1 or a1.lower() not in 'yn':
			a1 = input(f'A {color} monument can be placed on {*candidates,}. Proceed? [y/n]\n')
		if a1.lower() == 'n':
			return False
		elif len(candidates) > 1:
			while not a2 or tuple(a2.split(',')) not in candidates:
				a2 = input('On which space? Coords refer to the NW corner.\n')
			chosen = tuple(a2.split(','))
		else:
			chosen = candidates[0]
		chosen4 = [chosen,(chosen[0],chosen[1]+1),(chosen[0]+1,chosen[1]),(chosen[0]+1,chosen[1]+1)]
		monlist = [mon for mon in board_instance.monuments if color in mon.color]
		while not a3 or a3 not in map(str, range(1,len(monlist)+1)):
			for i, mon in enumerate(monlist):
				print(f'{i+1}: {mon.color} | ', end='')
			a3 = input('Choose one of the monuments above (choose a number).\n')
		chosen_mon = monlist[int(a3)-1]
		for space in chosen4:
			if board_instance.coords[space].treasure:
				hastr = True
			board_instance.coords[space] = chosen_mon
		if hastr:
			chosen_mon.treasure = True
		chosen_mon.setStyle()
		board_instance.checkLeaders()
		return True

	def playTurn(self, board_instance, moves=2): #implement passing
		counts = {'r':sum(tile.color == 'red' for tile in self.hand),'b':sum(tile.color == 'black' for tile in self.hand),'l':sum(tile.color == 'blue' for tile in self.hand),'g':sum(tile.color == 'green' for tile in self.hand),'c':len(self.catastrophes)}
		mapping = {'r':'red','b':'black','l':'blue','g':'green','lr':'red','lb':'black','ll':'blue','lg':'green'}
		print(f"{self.faction}'s hand: {counts['r']} red | {counts['b']} black | {counts['l']} blue | {counts['g']} green | {counts['c']} catastrophes\n{self.faction}'s leaders: {self.leaders['red'].coord} red | {self.leaders['black'].coord} black | {self.leaders['blue'].coord} blue | {self.leaders['green'].coord} green |\n{self.faction}'s points: {self.points['red']} red | {self.points['black']} black | {self.points['blue']} blue | {self.points['green']} green | {self.treasures} treasures\nMoves left: {moves}\n")
		answer = ''
		while not answer or answer.lower() not in ['r','b','l','g','lr','lb','ll','lg','c','d','a'] or (answer.lower() in ['r','b','l','g','c'] and counts[answer] == 0):
			if answer.lower() == 'p':
				board_instance.printBoard()
				print(f"{self.faction}'s hand: {counts['r']} red | {counts['b']} black | {counts['l']} blue | {counts['g']} green | {counts['c']} catastrophes\n{self.faction}'s leaders: {self.leaders['red'].coord} red | {self.leaders['black'].coord} black | {self.leaders['blue'].coord} blue | {self.leaders['green'].coord} green |\n{self.faction}'s points: {self.points['red']} red | {self.points['black']} black | {self.points['blue']} blue | {self.points['green']} green | {self.treasures} treasures\nMoves left: {moves}\n")
			answer = input('What would you like to do?\nPlay a tile - [r]ed [b]lack b[l]ue [g]reen [c]atastrophe\nPlay a leader - [lr]ed [lb]lack b[ll]ue [lg]reen\nRe[d]raw tiles or [p]rint board again or p[a]ss?\n')
		if answer.lower() == 'a':
			pass
		elif answer.lower() != 'd':
			space = ''
			while not space or len(space) != 2 or space[0] not in map(str, range(11)) or space[1] not in map(str, range(16)):
				if isinstance(space, str) and space.lower() == 'p':
					board_instance.printBoard()
					print(f"{self.faction}'s hand: {counts['r']} red | {counts['b']} black | {counts['l']} blue | {counts['g']} green | {counts['c']} catastrophes\n{self.faction}'s leaders: {self.leaders['red'].coord} red | {self.leaders['black'].coord} black | {self.leaders['blue'].coord} blue | {self.leaders['green'].coord} green |\n{self.faction}'s points: {self.points['red']} red | {self.points['black']} black | {self.points['blue']} blue | {self.points['green']} green | {self.treasures} treasures\nMoves left: {moves}\n")
				space = input(f'Place {answer} on which space (0,0 to 15,15 - or [p]rint board)?\n').split(',')
			space = tuple(map(int, space))
			if answer.lower() in ['r','b','l','g']:
				piece = next(tile for tile in self.hand if tile.color == mapping[answer])
			elif answer.lower() == 'c':
				piece = self.catastrophes[-1]
			else:
				piece = self.leaders[mapping[answer]]
			if not self.placePiece(piece, space, board_instance):
				print('\n')
				return self.playTurn(board_instance, moves=moves)
		else:
			todiscard = ''
			while not todiscard or any([char not in map(str, range(1,len(self.hand)+1)) for char in todiscard]):
				if isinstance(todiscard, str) and todiscard == 'p':
					board_instance.printBoard()
					print(f"{self.faction}'s hand: {counts['r']} red | {counts['b']} black | {counts['l']} blue | {counts['g']} green | {counts['c']} catastrophes\n{self.faction}'s leaders: {self.leaders['red'].coord} red | {self.leaders['black'].coord} black | {self.leaders['blue'].coord} blue | {self.leaders['green'].coord} green |\n{self.faction}'s points: {self.points['red']} red | {self.points['black']} black | {self.points['blue']} blue | {self.points['green']} green | {self.treasures} treasures\nMoves left: {moves}\n")					
				print('Select tiles to discard (e.g. 124):\n')
				for i, tile in enumerate(self.hand):
					print(f'{i+1}: {tile.color} | ', end='')
				todiscard = input('')
			todiscard = [self.hand[int(ind)-1] for ind in todiscard]
			self.discardTiles(board_instance, *todiscard)
		
		moves -= 1
		if moves > 0:
			board_instance.printBoard()
			return self.playTurn(board_instance, moves=moves)
		else:
			board_instance.printBoard()
			return True



class Kingdom():
	def __init__(self):
		self.spaces = set()
		self.tile_count = {'black':0, 'red':0, 'blue':0, 'green':0}
		self.treasure_count = 0
		self.leaders = {'black':None, 'red':None, 'blue':None, 'green':None}
		self.borders = set()
		self.monuments = set()

	def setSpaces(self, root, ignore_set, board_instance):
		neighbors = board_instance.findValidNeighbors(root)
		if not neighbors or all(x in ignore_set for x in neighbors):
			return
		self.spaces.update(neighbors)
		newignore = deepcopy(ignore_set)
		newignore.update(self.spaces)
		for neighbor in neighbors:
			self.setSpaces(neighbor, newignore, board_instance)

	def setAttrs(self, board_instance):
		'''
		#Sets tile count, leaders, treasure count and borders
		'''
		for space in self.spaces:
			if board_instance.coords[space].ptype == 'tile':
				self.tile_count[board_instance.coords[space].color] += 1
				if board_instance.coords[space].treasure:
					self.treasure_count += 1
			elif board_instance.coords[space].ptype == 'monument' and board_instance.coords[space] not in self.monuments:
				self.monuments.add(board_instance.coords[space])
				if board_instance.coords[space].treasure:
					self.treasure_count += 1
			elif board_instance.coords[space].ptype == 'leader':
				self.leaders[board_instance.coords[space].color] = board_instance.coords[space].faction
			self.borders.update(board_instance.findEmptyNeighbors(space))


class Board():
	'''
	Game state class, containing not just the board, but also the tile bag and kingdoms.
	'''
	std_temples = ((0,10),(2,5),(4,13),(6,8),(9,5),(10,10),(1,1),(1,15),(7,1),(8,14)) #four last are the ones with borders
	std_rivers = ((0,4),(0,5),(0,6),(0,7),(0,8),(0,12),(1,4),(1,12),(2,3),(2,4),(2,12),(2,13),(3,0),(3,1),(3,2),(3,3),(3,13),(3,14),(3,15),(4,14),(4,15),(5,14),(6,0),(6,1),(6,2),(6,3),(6,12),(6,13),(6,14),(7,3),(7,4),(7,5),(7,6),(7,12),(8,6),(8,7),(8,8),(8,9),(8,10),(8,11),(8,12))
	adv_temples = () #implement
	adv_rivers = () #implement
	def __init__(self,side='Standard'):
		self.coords = dict()
		self.monuments = [Piece('monument','black+blue'),Piece('monument','black+green'),Piece('monument','black+red'),Piece('monument','red+blue'),Piece('monument','blue+green'),Piece('monument','green+red')]
		self.kingdoms = [] 
		self.players = dict() #Bull, Hunter, Pot, Lion
		self.treasures = 0
		if side == 'Standard':
			self.bag = self.initBag(len(self.std_temples))
			for row in range(11):
				for col in range(16):
					if (row,col) in self.std_temples:
						self.treasures += 1
						if (row,col) in self.std_temples[-4:]:
							self.coords[(row,col)] = Piece('tile','red',treasure=True, border=True)
						else:
							self.coords[(row,col)] = Piece('tile','red',treasure=True)
					elif (row,col) in self.std_rivers:
						self.coords[(row,col)] = 'river'
					else:
						self.coords[(row,col)] = None

	def initBag(self,temples):
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

	def findNeighbors(self,coord):
		neighbors = []
		if coord[0] > 0:
			neighbors.append((coord[0]-1,coord[1]))
		if coord[0] < 10:
			neighbors.append((coord[0]+1,coord[1]))
		if coord[1] > 0:
			neighbors.append((coord[0],coord[1]-1))
		if coord[1] < 15:
			neighbors.append((coord[0],coord[1]+1))
		neighbors = list(filter(None, neighbors))
		return neighbors

	def findValidNeighbors(self, coord):
		valid_neighbors = list(filter(lambda x: isinstance(self.coords[x], Piece) and self.coords[x].ptype != 'catastrophe', self.findNeighbors(coord)))
		return valid_neighbors
	def findEmptyNeighbors(self, coord):
		empty_neighbors = list(filter(lambda x: not isinstance(self.coords[x], Piece), self.findNeighbors(coord)))
		return empty_neighbors
	def findTileNeighbors(self, coord, color): 
		tile_neighbors = list(filter(lambda x: isinstance(self.coords[x], Piece) and self.coords[x].ptype == 'tile' and self.coords[x].color == color, self.findNeighbors(coord)))
		return tile_neighbors
	def findLeaderNeighbors(self, coord): 
		ldr_neighbors = list(filter(lambda x: isinstance(self.coords[x], Piece) and self.coords[x].ptype == 'leader', self.findNeighbors(coord)))
		return ldr_neighbors

	def addPlayer(self, faction):
		self.players[faction] = Player(faction)
		self.players[faction].drawTiles(self)

	def checkValidPlacement(self,obj,space):
		if isinstance(self.coords[space], Piece):
			if self.coords[space].ptype in ['monument','catastrophe','leader']:
				return False
			elif self.coords[space].treasure or obj.ptype != 'catastrophe':
				return False
		elif obj.ptype == 'tile':
			if obj.color == 'blue' and self.coords[space] != 'river':
				return False
			elif obj.color != 'blue' and self.coords[space] != None:
				return False
			if self.checkHowManyKingdoms(space) > 2:
				return False
		elif obj.ptype == 'leader': 
			if self.coords[space] != None:
				return False
			neighbors = self.findNeighbors(space)
			if all([self.coords[x].ptype != 'tile' or self.coords[x].color != 'red' for x in neighbors if isinstance(self.coords[x], Piece)]):
				return False
			if self.checkHowManyKingdoms(space, obj.coord) > 1:
				return False
		return True

	def checkHowManyKingdoms(self,space, ldr_coord=False):
		'''
		Checks how many kingdoms border a given tile.
		'''
		howmany = 0
		for kingdom in self.kingdoms:
			if space in kingdom.borders:
				if ldr_coord and ldr_coord in kingdom.spaces: #prevents moving leader from being counted twice
					continue
				howmany += 1
		return howmany

	def checkRevolt(self,space):
		kingdomtocheck = None
		for k in self.kingdoms:
			if space in k.borders:
				kingdomtocheck = k
				break
		if kingdomtocheck.leaders[self.coords[space].color]:
			attacker = self.players[self.coords[space].faction]
			defender = self.players[kingdomtocheck.leaders[self.coords[space].color]]
			color = self.coords[space].color
			self.resolveRevolt(kingdomtocheck,color,attacker,defender)

	def resolveRevolt(self,kingdom,conflict_color,attacker,defender):
		attacker_str = len(self.findTileNeighbors(attacker.leaders[conflict_color].coord, 'red'))
		defender_str = len(self.findTileNeighbors(defender.leaders[conflict_color].coord, 'red'))
		att_hand = sum(tile.color == 'red' for tile in attacker.hand)
		def_hand = sum(tile.color == 'red' for tile in defender.hand)
		a1, d1 = '', ''
		input(f"Revolt! Attacker: {attacker.faction}'s {conflict_color} leader (str {attacker_str}). Defender: {defender.faction}'s {conflict_color} leader (str {defender_str}).\nPress Enter to choose attacker's extras.\n")
		while a1 not in map(str, range(att_hand+1)):
			if a1.lower() == 'p':
				self.printBoard()
			a1 = input(f"Attacker can use up to {att_hand} red tiles. How many do you want to use (re[p]rint board)?\n")
		a1 = int(a1)
		print('\n'*50)
		while d1 not in map(str, range(def_hand+1)):
			if d1.lower() == 'p':
				self.printBoard()
			d1 = input(f"Defender can use up to {def_hand} red tiles. How many do you want to use (re[p]rint board)?\n")
		d1 = int(d1)
		print('\n'*50)
		attacker_str += a1
		defender_str += d1
		if attacker_str > defender_str:
			victor = attacker
			loser = defender
		else:
			victor = defender
			loser = attacker
		input(f"{victor.faction} wins ({max(defender_str,attacker_str)} x {min(attacker_str,defender_str)})! {victor.faction} gains 1 red point.")
		self.coords[loser.leaders[conflict_color].coord] = None
		loser.leaders[conflict_color].coord = None
		victor.points['red'] += 1
		while a1 > 0:
			for tile in attacker.hand:
				if tile.color == 'red':
					attacker.hand.remove(tile)
					break
			a1 -= 1
		while d1 > 0:
			for tile in defender.hand:
				if tile.color == 'red':
					defender.hand.remove(tile)
					break
			d1 -= 1

	def checkWars(self, space, active_player):
		pindex = list(self.players.keys())
		activeindex = pindex.index(self.players[active_player.faction].faction)
		sortedpindex = []
		for n in range(len(pindex)):
			sortedpindex.append(pindex[(activeindex+n)%len(pindex)]) #sorting player order to determine attacker
		
		realms = []
		conflicts = []
		for k in self.kingdoms:
			if space in k.borders:
				realms.append(k)
				continue
		for color, faction in realms[0].leaders.items():
			if realms[0].leaders[color] and realms[1].leaders[color]:
				belligerents = sorted([realms[0].leaders[color],realms[1].leaders[color]], key=lambda x: sortedpindex.index(x))
				for realm in realms:
					if self.players[belligerents[0]].leaders[color].coord in realm.spaces:
						attrealm = realm
					else:
						defrealm = realm
				conflicts.append({'color':color,'attacker':(belligerents[0],attrealm),'defender':(belligerents[1],defrealm)})
		self.goThroughConflicts(conflicts, active_player)
		return True
				
		
	def goThroughConflicts(self, confs, active_player):
		conflicts = deepcopy(confs)
		if conflicts:
			if len(conflicts) == 1:
				self.resolveWar(conflicts[0]) 
				return True
			else:
				self.printBoard()
				print(f"{len(conflicts)} conflicts triggered:")
				for i, conf in enumerate(conflicts):
					print(f"{i+1}) {conf['color']}: {conf['attacker'][0]} vs {conf['defender'][0]}")
				answer = ''
				while len(answer) != 1 or answer not in map(str, range(1,len(conflicts)+1)):
					if answer.lower() == 'p':
						self.printBoard()
						print(f"{len(conflicts)}conflicts triggered:")
						for i, conf in enumerate(conflicts):
							print(f"{i+1}: {conf['color']}: {conf['attacker'][0]} vs {conf['defender'][0]}")
					answer = input(f"{active_player.faction}, choose number to resolve (or [p] to reprint board):")
				self.resolveWar(conflicts[int(answer)-1])
				del conflicts[int(answer)-1]
				for conf in conflicts:
					att_coord = self.players[conf['attacker'][0]].leaders[conf['color']].coord
					def_coord = self.players[conf['defender'][0]].leaders[conf['color']].coord
					attkingdom = Kingdom()
					attkingdom.spaces.add(att_coord)
					attkingdom.setSpaces(att_coord, set(att_coord), self)
					defkingdom = Kingdom()
					defkingdom.spaces.add(def_coord)
					defkingdom.setSpaces(def_coord, set(def_coord), self)
					if att_coord in defkingdom.spaces:
						return self.goThroughConflicts(conflicts, active_player)
					else:
						continue
				return True
	

	def resolveWar(self, conflict):
		points_gained = 0
		att_supp = [space for space in conflict['attacker'][1].spaces if self.coords[space].color == conflict['color'] and self.coords[space].ptype == 'tile']
		att_str = len(att_supp)
		def_supp = [space for space in conflict['defender'][1].spaces if self.coords[space].color == conflict['color'] and self.coords[space].ptype == 'tile']
		def_str = len(def_supp)
		att_hand = sum(tile.color == conflict['color'] for tile in self.players[conflict['attacker'][0]].hand)
		def_hand = sum(tile.color == conflict['color'] for tile in self.players[conflict['defender'][0]].hand)
		a1, d1 = '', ''
		input(f"War! Attacker: {conflict['attacker'][0]}'s {conflict['color']} leader (str {att_str}). Defender: {conflict['defender'][0]}'s {conflict['color']} leader (str {def_str}).\nPress Enter to choose attacker's extras.\n")
		self.printBoard()
		while a1 not in map(str, range(att_hand+1)):
			if a1.lower() == 'p':
				self.printBoard()
			a1 = input(f"{conflict['attacker'][0]} (attacker with str {att_str}) can use up to {att_hand} {conflict['color']} tiles. How many do you want to use (re[p]rint board)?\n")
		a1 = int(a1)
		print('\n'*50)
		self.printBoard()
		while d1 not in map(str, range(def_hand+1)):
			if d1.lower() == 'p':
				self.printBoard()
			d1 = input(f"{conflict['defender'][0]} (defender with str {def_str}) can use up to {def_hand} {conflict['color']} tiles. How many do you want to use (re[p]rint board)?\n")
		d1 = int(d1)
		print('\n'*50)
		att_str += a1
		def_str += d1
		if att_str > def_str:
			victor = self.players[conflict['attacker'][0]]
			loser = self.players[conflict['defender'][0]]
			loser_supp = def_supp
			loser_realm = conflict['defender'][1]
		else:
			victor = self.players[conflict['defender'][0]]
			loser = self.players[conflict['attacker'][0]]
			loser_supp = att_supp
			loser_realm = conflict['attacker'][1]
	
		self.coords[loser.leaders[conflict['color']].coord] = None
		loser_realm.spaces.remove(loser.leaders[conflict['color']].coord)
		loser_realm.leaders[conflict['color']] = None
		loser.leaders[conflict['color']].coord = None
		points_gained += 1
		
		for space in loser_supp:
			if conflict['color'] != 'red' or (not self.coords[space].treasure and not self.findLeaderNeighbors(space)):
				points_gained += 1
				if conflict['color'] == 'blue':
					self.coords[space] = 'river'
					loser_realm.spaces.remove(space)
				else:
					self.coords[space] = None
					loser_realm.spaces.remove(space)

		victor.points[conflict['color']] += points_gained
		input(f"{victor.faction} wins ({max(def_str,att_str)} x {min(att_str,def_str)})! {victor.faction} gains {points_gained} {conflict['color']} points.")
		while a1 > 0:
			for tile in self.players[conflict['attacker'][0]].hand:
				if tile.color == 'red':
					self.players[conflict['attacker'][0]].hand.remove(tile)
					break
			a1 -= 1
		while d1 > 0:
			for tile in self.players[conflict['defender'][0]].hand:
				if tile.color == 'red':
					self.players[conflict['defender'][0]].hand.remove(tile)
					break
			d1 -= 1

	def checkMonumentPlacement(self, space, color):
		monlist = [mon for mon in self.monuments if color in mon.color]
		if not monlist:
			return False
		ne = (space[0]-1,space[1]+1)
		se = (space[0]+1,space[1]+1)
		sw = (space[0]+1,space[1]-1)
		nw = (space[0]-1,space[1]-1)
		candidates = []
		neighbors = self.findTileNeighbors(space, color)
		if (space[0]+1,space[1]) in neighbors and (space[0],space[1]+1) in neighbors:
			if isinstance(self.coords[se], Piece) and self.coords[se].ptype == 'tile' and self.coords[se].color == color:
				candidates.append(space)
		if (space[0]-1,space[1]) in neighbors and (space[0],space[1]+1) in neighbors:
			if isinstance(self.coords[ne], Piece) and self.coords[ne].ptype == 'tile' and self.coords[ne].color == color:
				candidates.append((space[0]-1,space[1]))
		if (space[0]-1,space[1]) in neighbors and (space[0],space[1]-1) in neighbors:
			if isinstance(self.coords[nw], Piece) and self.coords[nw].ptype == 'tile' and self.coords[nw].color == color:
				candidates.append(nw)
		if (space[0]+1,space[1]) in neighbors and (space[0],space[1]-1) in neighbors:
			if isinstance(self.coords[sw], Piece) and self.coords[sw].ptype == 'tile' and self.coords[sw].color == color:
				candidates.append((space[0],space[1]-1))
		return candidates
		


	def checkLeaders(self):
		for player in self.players.values():
			for leader in player.leaders.values():
				if leader.coord and not self.findTileNeighbors(leader.coord, 'red'):
					self.coords[leader.coord] = None
					leader.coord = None

	def updateKingdoms(self, just_placed, active_player):
		kingdoms = []
		score = False
		if self.coords[just_placed].ptype == 'tile':
			if self.checkHowManyKingdoms(just_placed) == 1:
				score = True 
			elif self.checkHowManyKingdoms(just_placed) == 2: 
				war = self.checkWars(just_placed, active_player)
				if not war:
					score = True
		elif self.coords[just_placed].ptype == 'leader' and self.checkHowManyKingdoms(just_placed, True) == 1:
			self.checkRevolt(just_placed) 
		for player in self.players.values():
			for leader in player.leaders.values():
				if not leader.coord or any([leader.coord in x.spaces for x in kingdoms]): #if leaders not on board or already in a kingdom
					continue
				newkingdom = Kingdom()
				newkingdom.spaces.add(leader.coord)
				newkingdom.setSpaces(leader.coord, set(leader.coord), self)
				newkingdom.setAttrs(self)
				kingdoms.append(newkingdom)
		return kingdoms, score

	def tileScore(self, color, space):
		for kingdom in self.kingdoms:
			if space in kingdom.spaces:
				if kingdom.leaders[color]:
					self.players[kingdom.leaders[color]].points[color] += 1
					input(f'{self.players[kingdom.leaders[color]].faction} received 1 {color} point for tile.')
				elif kingdom.leaders['black']:
					self.players[kingdom.leaders['black']].points[color] += 1
					input(f"{self.players[kingdom.leaders['black']].faction} received 1 {color} point for tile.")
				break

	def gameSetup(self):
		print(f'Welcome to Tigris & Euphrates v{gameversion}!')
		#input('Standard or Advanced?') Implement!

		pmap = {0:'Bull',1:'Hunter',2:'Pot',3:'Lion'}
		answer = ''
		while not answer or answer not in '234':
			answer = input('How many players [2 to 4]?\n')
		for x in range(int(answer)):
			self.addPlayer(pmap[x])

	def turnLoop(self, turn=1):
		self.printBoard()
		print(f'Turn {turn}')
		turn += 1
		for player, pobj in self.players.items():
			print(f"{Fore.YELLOW}{player}'s turn.")
			pobj.playTurn(self)
			self.endTurnScore(pobj)
			for player in self.players.values():
				player.drawTiles(self)
			if self.checkEndGame():
				return self.endGame()
		self.turnLoop(turn)

	def endTurnScore(self, player):
		for kingdom in self.kingdoms:
			for monument in kingdom.monuments:
				for color in monument.color.split('+'):
					if kingdom.leaders[color] == player.faction:
						player.points[color] += 1
						input(f'{player.faction} received 1 {color} point for monument')
			if kingdom.treasure_count > 1 and kingdom.leaders['green']:
				left_to_take = kingdom.treasure_count-1
				input(f"{kingdom.leaders['green']} will take {kingdom.treasure_count-1} treasures.")
				totake_border = [coord for coord in kingdom.spaces if self.coords[coord].treasure and self.coords[coord].border]
				if len(totake_border) > 0 and len(totake_border) <= left_to_take:
					for coord in totake_border:
						self.coords[coord].treasure = False
						self.coords[coord].style = self.coords[coord].setStyle()
						self.treasures -= 1
						left_to_take -= 1
				elif len(totake_border) > left_to_take:
					t1 = ''
					while not t1 or len(t1) != left_to_take or any([char not in map(str, range(1,len(totake_border)+1)) for char in t1]):
						for i, tr in enumerate(totake_border):
							print(f'{i+1}: {tr} | ', end='')
						t1 = input(f'Choose {left_to_take} border treasures to take.\n')
					for ind in t1:
						self.coords[totake_border[int(ind)-1]].treasure = False
						self.coords[totake_border[int(ind)-1]].style = self.coords[totake_border[int(ind)-1]].setStyle()
						self.treasures -= 1
						left_to_take -= 1
				if left_to_take > 0:
					self.printBoard()
					totake = [coord for coord in kingdom.spaces if self.coords[coord].treasure and not self.coords[coord].border]
					t2 = ''				
					while not t2 or len(t2) != left_to_take or any([char not in map(str, range(1,len(totake)+1)) for char in t2]):
						for i, tr in enumerate(totake):
							print(f'{i+1}: {tr} | ', end='')
						t2 = input(f'Choose {left_to_take} treasures to take\n')
					for ind in t2:
						self.coords[totake[int(ind)-1]].treasure = False
						self.coords[totake[int(ind)-1]].style = self.coords[totake[int(ind)-1]].setStyle()
						self.treasures -= 1
						left_to_take -= 1
				self.players[kingdom.leaders['green']].treasures += kingdom.treasure_count-1
				kingdom.treasure_count = 1
				self.printBoard()
				





	def checkEndGame(self):
		if self.treasures < 3 or len(self.bag) == 0:
			return True

	def endGame(self):
		minpoints = {}
		for player in self.players.values():
			colorpoints = sorted(player.points.items(), key=lambda x: x[1])
			while player.treasures > 0:
				colorpoints[0] = (colorpoints[0][0], colorpoints[0][1]+1)
				player.treasures -= 1
				colorpoints = sorted(colorpoints, key=lambda x: x[1])
			minpoints[player.faction] = colorpoints

		for attempt in range(4):
			highest = max([v[attempt][1] for v in minpoints.values()])
			victor = [k for k, v in minpoints.items() if v[attempt][1] == highest]
			if len(victor) != 1:
				input(f'Players {*victor,} are tied after {attempt+1} attempts, with {minpoints[victor[0]][attempt][1]} tiles!\nBreaking tie...')
				continue				
			else:
				input(f'And the victory goes to {victor[0]} after {attempt+1} attempts, with {minpoints[victor[0]][attempt][1]} tiles!')
				sys.exit()
				return
	
	def printBoard(self): 
		sep = '   ' + '+---'*16 + '+'
		hcoords = '    '
		for x in range(16):
			hcoords += f'{x}'.center(4)
		print(hcoords)
		print(sep)
		for r in range(11):
			linetoprint = '|'
			for k, v in self.coords.items():
				if k[0] == r:
					if isinstance(v, Piece):
						linetoprint += v.style + '|'
					elif v == 'river':
						linetoprint += Back.CYAN + Fore.BLUE + ' r ' + Style.RESET_ALL + '|' 
					else:
						linetoprint += '   |'
			print(str(r).center(3) + linetoprint + '\n' + sep)
		


if __name__ == '__main__':
	os.system('mode con lines=40')
	os.system(f'title Tigris ^& Euphrates v{gameversion} by Bernardo Tonasse')
	colorama.init(autoreset=True)
	theBoard = Board()
	theBoard.gameSetup()
	theBoard.turnLoop()
	
