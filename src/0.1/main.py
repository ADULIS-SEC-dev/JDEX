#!/usr/bin/env python3.11

"""
	* Copyright(c) 2024, ADULIS(R) SECURITIES. All rights reserved.
	* Copyright(c) JEGOL(TM) Decentralized Exchange.
"""

__ver__: int = 0.1

import argparse
import logging
import hashlib
import os

import telebot
import pandas as pd

from dataclasses import (
	dataclass,
	field
)
from datetime import datetime
from abc import (
	ABC,
	abstractmethod
)

from sqlalchemy import (
	create_engine,
	Column,
	Integer,
	String
)
from sqlalchemy.orm import (
	sessionmaker,
	declarative_base
)
from telebot import types

# Use your own Telegram Bot API!
with open( "APIKEY" ) as API:
	API_KEY: str = API.readline()

class Config:
	"""
	Configuration for the application.

	Attributes:
		now( str ): The current datetime.
	Methods:
		...
	"""
	
	now: str = datetime.now().strftime( "%m/%d/%Y %I:%M:%S %p" )

Conf: Config = Config()

class Logger:
	"""
	User activities logger.

	Methods:
		Log()
	"""

	def Log( Message: str ) -> None:
		"""
		Args:
			Message( str ): ...
		"""

		index: int = 0

		with open( f"./logs/log-{index + 1}.log", "a" ) as LOG:
			LOG.write( f"{Conf.now} - {Message}\n" )

# Set up logging (RUNTIME logger)
logging.basicConfig(
	filename = "./logs/Bot.log",
	level = logging.DEBUG,
	format = "%(asctime)s - %(message)s",
	datefmt = "%Y-%m-%d %H:%M:%S"
)

def initialSetup( Obj ) -> None:
	"""
	Run this to setup the Bot correctly (first time use).

	Args:
		Obj: The bot constructor object.
	"""

	try:
		# Customize the bot
		Obj.set_my_name( "JEGOL DeFi Research ~ Proof-of-Concept: Source 0.1" )
		Obj.set_my_description("""
			HELLO WORLD!\n
			Welcome to JEGOL!
		""")

		default_permissions = types.ChatPermissions( # Customize chat permissions
			can_send_messages = True,
			can_send_media_messages = True,
			can_send_polls = True,
			can_send_other_messages = True,
			can_add_web_page_previews = True,
			can_change_info = False,
			can_invite_users = True,
			can_pin_messages = True # !
		)

		Obj.set_my_default_administrator_rights( default_permissions )

		# Customize the commands
		Bot.set_my_commands([
			types.BotCommand( "start", "Start the Bot." ),
			types.BotCommand( "help", "Get this help." )
			# ...
		])
	except Exception as e:
		print ( f"[-] An unexpected error occurred: {e}" ); exit()

# Set up the SQLAlchemy database
Base = declarative_base()

class BlockModel( Base ):
	"""
	Define the Block model that will be stored in the Blockchain DB.

	Attributes:
		...
	"""

	__tablename__ = "blocks"

	Id = Column( Integer, primary_key = True )
	Index = Column( Integer )
	timestamp = Column( String )
	_Username = Column( String )
	Username = Column( String )
	# Password = Column( String )
	Hash = Column( String )
	prevHash = Column( String )

@dataclass
class BlockData:
	"""
	Representation class for the data stoed in a Block.

	Attributes:
		...
	"""
	
	Index: int
	timestamp: str
	_Username: str
	Username: str
	Hash: str
	prevHash: str

class absBlock( ABC ):
	"""
	Abstract Block class.
	Provides the common methods for all types of Blocks.

	Attributes:
		...

	Methods:
		computeHash()
		saveBlock()
		loadBlock()
	"""

	def __init__( self, Data: BlockData ): # Construct the Block with a data input*
		self.Data = Data

	def computeHash( self ):
		"""
		Compute the hash of the Block based on the given data.
		"""

		# !
		Block_str: str = f"{self.Data.timestamp}{self.Data._Username}{self.Data.Hash}{self.Data.prevHash}"

		return hashlib.sha256( Block_str.encode() ).hexdigest()

	@abstractmethod
	def saveBlock( self, Session ) -> None:
		"""
		Save the Block into the DB.

		Attributes:
			Session
		"""

		... # ...

	@abstractmethod
	def loadBlock(
		self,
		Session,
		Index: int
	):
		"""
		Query the Block from the DB.

		Attributes:
			Session
			Index( int ): ...
		"""

		... # ...

class Block( absBlock ):
	"""
	Block class.
	Saves and loads Blocks to/from the DB.
	"""

	def saveBlock( self, Session ) -> None:
		blockModel = BlockModel(
			Index = self.Data.Index,
			timestamp = self.Data.timestamp,
			_Username = self.Data._Username,
			Username = self.Data.Username,
			Hash = self.Data.Hash,
			prevHash = self.Data.prevHash
		)

		Session.add( blockModel )
		Session.commit()

	def loadBlock(
		self,
		Session,
		Index: int
	) -> object: # !
		blockModel = Session.query( BlockModel ).filter_by( Index = Index ).first()

		if blockModel:
			return Block( BlockData(
				Index = blockModel.Index,
				timestamp = blockModel.timestamp,
				_Username = blockModel._Username,
				Username = blockModel.Username,
				Hash = blockModel.Hash,
				prevHash = blockModel.prevHash
			))
		else:
			return None

class Blockchain:
	"""
	Blockchain class.
	Manages the chain of Blocks.

	Attributes:
		...

	Methods:
		createGenesisBlock()
		...
	"""

	def __init__( self ):
		self.Engine = create_engine( "sqlite:///blocks.db" ) # Use "blocks.db"
		Base.metadata.create_all( self.Engine ) # If the DB doesn't exist, create it

		self.Session = sessionmaker( bind = self.Engine ); self.SESSION = self.Session()

		self.Chain = self.loadChain()

	def createGenesisBlock( self ) -> None:
		"""
		Creates the first Block in the chain, with null values (except the Block.Hash to be used as a ref).
		"""

		genesisData = BlockData(
			Index = 0,
			timestamp = Conf.now,
			_Username = "Genesis Block",
			Username = "Genesis Block",
			Hash = "0",
			prevHash = "0"
		)
		genesisBlock = Block( genesisData )
		genesisBlock.Data.Hash = genesisBlock.computeHash()
		genesisBlock.saveBlock( self.SESSION )

		self.Chain.append( genesisBlock )

	def addBlock( self, _Username: str, Username: str ) -> None:
		"""
		Add a Block into the chain.
		"""

		prevBlock = self.getLastBlock()

		newData = BlockData(
			prevBlock.Data.Index + 1,
			Conf.now,
			_Username,
			Username,
			"",
			prevBlock.Data.Hash
		)
		newBlock = Block( newData )
		newBlock.Data.Hash = newBlock.computeHash()
		newBlock.saveBlock( self.SESSION )

		self.Chain.append( newBlock )
	
	def getLastBlock( self ):
		"""
		...
		"""

		if not self.Chain:
			self.createGenesisBlock()

		return self.Chain[-1]

	# Add more functionality (more than just the name)
	def checkBlock( self, _Username: str ) -> bool:
		"""
		...
		"""

		# Query the DB for any Blokcs with the given username
		BLOCK = self.SESSION.query( BlockModel ).filter_by( _Username = _Username ).first()

		return BLOCK is not None

	def loadChain( self ):
		"""
		...
		"""

		Chain = []
		Blocks = self.SESSION.query( BlockModel ).all()

		for blockModel in Blocks:
			BLOCK = Block( BlockData(
				Index = blockModel.Index,
				timestamp = blockModel.timestamp,
				_Username = blockModel._Username,
				Username = blockModel.Username,
				Hash = blockModel.Hash,
				prevHash = blockModel.prevHash
			))

			Chain.append( BLOCK )

		return Chain

	# ...
	def validateChain( self ) -> bool:
		"""
		Validate the integrity of the chain by cross-checking the hashes and previous hashes of each Block.
		"""

		Blocks = self.SESSION.query( BlockModel ).all()

		for i in range( 1, len( Blocks ) ):
			for j in range( 1, len( self.Chain ) ):
				currBlockX = Blocks[i]
				prevBlockX = Blocks[i - 1]

				currBlockY = self.Chain[i]
				prevBlockY = self.Chain[i - 1]

				# DB to chain
				if currBlockX.Hash != currBlockY.Data.Hash:
					return False
				
				if currBlockX.prevHash != currBlockY.Data.prevHash:
					return False

		return True

	def to_DataFrame( self ) -> pd.DataFrame:
		"""
		Convert the Block's data to a DataFrame, making it presentable.
		"""

		DATA = [
			[BLOCK.Data.Index, BLOCK.Data.timestamp, BLOCK.Data._Username, BLOCK.Data.Username, BLOCK.Data.Hash, BLOCK.Data.prevHash] for BLOCK in self.Chain
		]

		Col = ["Index", "Timestamp", "_Username", "Username", "Hash", "Previous Hash"]

		return pd.DataFrame( DATA, columns = Col )

# Initiatlize the Telegram bot
Bot = telebot.TeleBot( API_KEY )

# Enclave into a class to add more connected features and events
@Bot.message_handler( commands = ["start"] )
def Start( MSG: str ) -> None:
	"""
	Command handler for the '/start' command.

	Args:
		MSG( str ): ...
	"""

	# Check if user has a username (program will terminate session if not)
	_USR = MSG.from_user.username

	if not _USR:
		Bot.send_message( chat_id = MSG.chat.id, text = "Can't use this bot if you don't have a username!" )
	else:
		first_name = MSG.from_user.first_name

		# Check if the user has a first name
		if first_name:
			Greeting: str = f"Welcome, {first_name}! Please choose an option:"
		else:
			Greeting: str = "Welcome! Please choose an option:"

		# Create the Keyboard
		Keyboard = types.ReplyKeyboardMarkup( resize_keyboard = True )
		Btn_createAccount = types.KeyboardButton( "Create Account" )
		Bt_Login = types.KeyboardButton( "Login" )

		Keyboard.add( Btn_createAccount, Bt_Login )

		# Indented
		print (
			f"\nBot accessed @ {Conf.now}\n"
			f"\tChat ID: {MSG.from_user.id}\n"
			f"\tFirst Name: {MSG.from_user.first_name}\n"
			f"\tLast Name: {MSG.from_user.last_name}\n"
			f"\tUsername: {MSG.from_user.username}\n"
			f"---\n"
		)

		# ...
		Logger.Log(
			f"Bot accessed @ {Conf.now} w/\n"
			f"\tChat ID: {MSG.from_user.id}\n"
			f"\tFirst Name: {MSG.from_user.first_name}\n"
			f"\tLast Name: {MSG.from_user.last_name}\n"
			f"\tUsername: {MSG.from_user.username}"
		)

		# Send the initial welcome message
		Bot.send_message(
			chat_id = MSG.chat.id,
			text = Greeting,
			reply_markup = Keyboard
		)

BC = Blockchain()

@Bot.message_handler( content_types = ["text"] )
def Account( MSG ) -> None:
	"""
	...

	Args:
		MSG( str ): ...
	"""

	if MSG.text == "Create Account":
		# Check if the user already exists
		USR = MSG.from_user.username

		if USR is None: # !
			raise Exception

		if BC.checkBlock( USR ):
			print ( "\n[-] Account already exists in the chain!" )

			Bot.send_message( chat_id = MSG.chat.id, text = f"An account already exists under this username '{MSG.from_user.username}'! Please login with your credentials instead!" )
		else:
			# Check if the user has a last name
			last_name = MSG.chat.last_name

			if last_name:
				_USR = str( f"{MSG.chat.first_name} {MSG.chat.last_name}" )

				BC.addBlock( USR, _USR )
			else:
				BC.addBlock( MSG.chat.first_name )

			# ...
			df = BC.to_DataFrame()

			# Gets last edited data entry from the specific DB column. Change this too (has issues when multiple users use the network at the same time)!
			print (
				f"[+] Block created w/\n"
				f"\tUsername: {df['Username'].iloc[-1]} - @ {df['_Username'].iloc[-1]}\n"
				f"\tHash: {df['Hash'].iloc[-1]} // Previous Hash: {df['Previous Hash'].iloc[-1]}\n"
				f"---\n"
			)

			# Send 200 message
			Bot.send_message( chat_id = MSG.chat.id, text = f"Your account has been created!" )

	if MSG.text == "Login":
		print ( "\n[*] User logging in..." )

		# ...

if __name__ == "__main__":
	# A simple parser (convert into a class too)
	Parser = argparse.ArgumentParser(
		prog = "JEGOL",
		usage = "Run the bot handler on the local machine, making the bot and the chain accessible online.",
		description = "Proof-of-Concept source code for JEGOL DeFi research project.",
		epilog = "Ver 0.1" # *
	); Parser.add_argument(
		"-i",
		help = "Run the setup func for initial, first time usage setup of the bot (don't run it more than once or twice!!!).",
		choices = ["True", "False"],
		required = False
	); Parser.add_argument(
		"-db",
		help = """
		Interact with the Blockchain's DB.
		[sh: Shows all the 'Blocks' inside the DB (CAUTION: if the 'blocks.db' file doesn't exist, it will create it).]
		""",
		choices = ["sh"],
		required = False
	); Args = Parser.parse_args()

	# Active method for proper handling of events
	if Args.i == "True":
		print ( "\n[*] Running first time setup...\n" )

		if initialSetup( Bot ): # Call the func, print then exit
			print ( "[+] First time setup completed successfully! Run the bot in normal mode to start network" ); exit()
		else:
			print ()

			# ...
	elif Args.db == "sh":
		print ( "[*] Showing DB entries (Blocks)...\n---\n" )

		for BLOCK in BC.Chain: 
			print (
				f"-BLOCK{BLOCK.Data.Index}-\n"
				f"BLOCK Created on: {BLOCK.Data.timestamp}\n"
				f"BLOCK Header:\n"
				f"\tLegacy Data: {BLOCK.Data.Username} @ {BLOCK.Data._Username}\n" # *
				f"\tHash: {BLOCK.Data.Hash}\n"
				f"\tPrevioud Hash: {BLOCK.Data.prevHash}\n***\n"
			)
	else:
		# Start the bot
		print ( f"[+] Bot started on {Conf.now}.\n\n{Bot.get_me()}" ); Logger.Log( "Bot started!" )

		Bot.polling()

		if Bot.stop_polling: # Events after bot is stopped
			print ( "\n[-] Exiting..." )

			if BC.validateChain():
				print ( "\n[+] Chain is valid!" )
			else:
				print ( "\n[-] Chain is invalid!" )

				# DEBUG. Identify
				for BLOCK in BC.Chain:
					print (
						f"\n[+] Check the Block Hash-Block prevHash assocations: (Manual Debug):\n"
						f"{BLOCK.Data.Hash} - {BLOCK.Data.prevHash}"
					)
