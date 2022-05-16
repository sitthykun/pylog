"""
Author: masakokh
Version: 4.0.0
"""
import datetime
import os
from datetime import datetime, timedelta
from typing import Any
# internal
# from FCMLib import FCMLib
from RedisLib import RedisLib


class Logger:
	"""

	"""
	# hide all numbers that added
	hide    = []
	# index of output
	id      = 0

	def __init__(self, path: str= 'log', filename: str= 'access', extension: str= '.log', enableLog: bool= True, enableConsole: bool= True, line: bool= True, color: bool= True):
		"""

		:param path:
		:param filename:
		:param extension:
		:param enableLog:
		:param enableConsole:
		:param line:
		:param color:
		"""
		# datetime format
		# ex: 2020-05-18
		self.__formatFileName   = '%Y-%m-%d'
		# full datetime format
		# ex: 2022-05-12 21:40:20.345
		self.__dateTimeFormat   = f'{self.__formatFileName} %H:%M:%S.%f'
		# set color
		self.__color            = color
		self.__line             = line
		# config
		self.__enableConsole    = enableConsole
		self.__enableLog        = enableLog
		# redis
		self.__enableRedis			= False
		self.__enableRedisError		= False
		self.__enableRedisFail		= False
		self.__enableRedisInfo		= False
		self.__enableRedisSuccess	= False
		self.__enableRedisTrack		= False
		self.__enableRedisWarning	= False
		#
		self.__extension        = extension
		# path + /
		self.__path             = path
		# compute
		self.__filename         = os.path.join(self.__path, f'{filename}{self.__extension}')
		# static datetime
		self.__datetime         = datetime.now().strftime(self.__dateTimeFormat)
		# series
		self.__keySeries        = ''
		# session as uuid or md5
		self.__keySession       = ''
		# pub/sub
		# self.__fcm				= FCMLib()
		self.__redis			= RedisLib()
		# load

	def __createNewBackupFile(self) -> None:
		"""

		:return:
		"""
		# backup the yesterday content and use the yesterday as name of the backup file
		yesterdayFileName       = self.__getBackupFileName()

		# check yesterday file with len of current file
		if not os.path.exists(yesterdayFileName) and len(self.__getContentFile(self.__filename)) > 0:
			# rename current file to do backup
			# that will move content too
			os.rename(
				self.__filename
				, yesterdayFileName
			)

	def __getBackupFileName(self) -> str:
		"""

		:return:
		"""
		# generate a filename
		return f'{self.__path}{(datetime.now() - timedelta(1)).strftime(self.__formatFileName)}{self.__extension}'

	def __getContentBody(self, typeName: str, title: str, content: Any, color: str) -> str:
		"""

		:param typeName:
		:param title:
		:param content:
		:param color:
		:return:
		"""
		lineStart   = ''
		lineEnd     = ''
		cHead       = ''
		cBody       = f'[{typeName}] '
		cFoot       = ''

		# add line to content
		if bool(self.__line):
			lineStart   = '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
			lineEnd     = '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
			# update
			cHead       = lineStart
			cFoot       = lineEnd

		# add color, style
		if bool(self.__color):
			# update
			cHead       = f'{color}{cHead}{self.__StyleModifier.ENDC}'
			cFoot       = f'{color}{cFoot}{self.__StyleModifier.ENDC}'
			cBody       = f'{color}{cBody}{self.__StyleModifier.ENDC}{self.__StyleModifier.TEXT_BOLD}{title}{self.__StyleModifier.ENDC}'

		else:
			cBody       = f'{cBody}{title}'

		# final content
		# f"{cBody}{self.__getStr(content)} \n{datetime.now().strftime(self.__dateTimeFormat)}" \
		return f'\n{cHead}\n{cBody}{self.__getStr(content)} \n{cFoot}\n\n' if bool(self.__line) else f'\n{cBody}\n'

	def __getContentFile(self, fileName: str) -> str:
		"""

		:param fileName:
		:return:
		"""
		try:
			# init
			content	= ''

			# read file
			with open(fileName) as f:
				content = f.read()

			# final
			return content

		except IOError:
			return ''

		except Exception:
			return ''

	def __getContentHead(self, logId: int) -> str:
		"""

		:param logId:
		:return:
		"""
		# final data
		if self.__keySeries:
			return f'{self.__datetime} <id: {logId}> {self.__keySeries}\n'

		else:
			return f'{self.__datetime} <id: {logId}>\n'

	def __getStr(self, content: Any) -> str:
		"""

		:param content:
		:return:
		"""
		if isinstance(content, dict):
			return str(content)

		elif isinstance(content, str) or type(content) == str:
			return content

		else:
			return ''

	async def __msgRedis(self, channel: str= None) -> None:
		"""

		:param channel:
		:return:
		"""
		self.__redis.messageGet()

	# def __pushFCM(self, title: str, body: str) -> None:
	# 	"""
	#
	# 	:param title:
	# 	:param body:
	# 	:return:
	# 	"""
	# 	pass

	async def __pushRedis(self, title: str, body: str, channel: str= None) -> None:
		"""

		:param title:
		:param body:
		:param channel:
		:return:
		"""
		#
		notification	= self.__redis.messagePush(
			title		= title
			, body		= body
			, channel	= channel
		)

		#
		print(notification)

	def __setNewId(self, id: int) -> None:
		"""

		:param id:
		:return:
		"""
		if id > Logger.id:
			Logger.id   = id

	def __write(self, typeName: str = '', title: str = '', color: str = '', content: Any = None, logId: int = None) -> None:
		"""

		:param typeName:
		:param title:
		:param content:
		:param color:
		:param logId:
		:return:
		"""
		# create file
		self.__createNewBackupFile()

		# validate log Id
		if logId:
			# Reset log id
			self.__setNewId(logId)

		else:
			# increase index first
			Logger.id += 1

		# do filter
		if Logger.id not in Logger.hide:
			# update content
			contentBody = self.__getContentBody(typeName= typeName, title= title, content= self.__getStr(content= content), color= color)
			contentHead = self.__getContentHead(logId= Logger.id)

			# enable file log
			if bool(self.__enableLog):
				# write to file
				self.__writeFile(content= f'{contentHead}{contentBody}')

				# verify first
				if self.__keySession:
					# output content to specific file via session's
					self.__writeSessionFile(content= f'{contentHead}{contentBody}')

			# enable console
			if bool(self.__enableConsole):
				# console
				print(f'{contentHead}{contentBody}')

	def __writeFile(self, content: str) -> None:
		"""

		:note: final written file
		:param content:
		:return:
		"""
		try:
			# open log file, if not exist will create
			with open(self.__filename, 'a+', encoding= 'utf-8') as f:
				f.write(content)

		except FileNotFoundError as e:
			print(f'Logger.__writeFile output file FileNotFoundError: open file {e.errno} {e.strerror}({self.__filename}), {str(e)}')

		except IOError as e:
			print(f'Logger.__writeFile output file IOError: open file {e.errno} {e.strerror}({self.__filename}), {str(e)}')

		except Exception as e:
			print(f'Logger.__writeFile output file Exception: open file({self.__filename}), {str(e)}')

	def __writeSessionFile(self, content: Any) -> None:
		"""

		:param content:
		:return:
		"""
		try:
			# open log file, if not exist will create
			with open(f'{self.__path}{self.__keySession}{self.__extension}', 'a+', encoding= 'utf-8') as fs:
				fs.write(content)

		except FileNotFoundError as e:
			print(f'Logger.__writeSessionFile output file FileNotFoundError: open file {e.errno} {e.strerror}({self.__path}{self.__keySession}{self.__extension}), {str(e)}')

		except IOError as e:
			print(f'Logger.__writeSessionFile output file IOError: open file {e.errno} {e.strerror}({self.__path}{self.__keySession}{self.__extension}), {str(e)}')

		except Exception as e:
			print(f'Logger.__writeSessionFile output file Exception: open file ({self.__path}{self.__keySession}{self.__extension}), {str(e)}')

	def disableIds(self, numbers: list = None) -> None:
		"""

		:param numbers:
		:return:
		"""
		if numbers:
			Logger.hide     = numbers

	def error(self, title: str = '', content: Any = None, id: int = None) -> None:
		"""

		:param title:
		:param content:
		:param id:
		:return:
		"""
		self.__write(
			typeName    = 'ERROR'
			, title     = title
			, content   = content
			, color     = self.__StyleModifier.RED
			, logId     = id
		)

	def fail(self, title: str = '', content: Any= None, id: int = None) -> None:
		"""

		:param title:
		:param content:
		:param id:
		:return:
		"""
		self.__write(
			typeName    = 'FAIL'
			, title     = title
			, content   = content
			, color     = self.__StyleModifier.MAGENTA
			, logId     = id
		)

		#
		if self.__enableRedis and self.__redis.enableFail:
			#
			self.__redis.messagePush(
				title	= title
				, body	= content
			)

	def info(self, title: str = '', content: Any = None, id: int = None) -> None:
		"""

		:param title:
		:param content:
		:param id:
		:return:
		"""
		self.__write(
			typeName    = 'INFO'
			, title     = title
			, content   = content
			, color     = self.__StyleModifier.BLUE
			, logId     = id
		)

		#
		if self.__enableRedis and self.__redis.enableInfo:
			#
			self.__redis.messagePush(
				title	= title
				, body	= content
			)

	# def setFCM(self, config: dict) -> None:
	# 	"""
	#
	# 	:param config:
	# 	:return:
	# 	"""
	# 	self.__fcm.setConfig(config)

	def setKeySeries(self, series: str = None) -> None:
		"""

		:param series:
		:return:
		"""
		self.__keySeries    = series

	def setKeySession(self, sessionKey: str= None) -> None:
		"""

		:note: set session filename
		:param sessionKey:
		:return:
		"""
		if sessionKey and len(sessionKey) > 32:
			# start 0 to 31st of string
			self.__keySession       = sessionKey[0:31]

		else:
			# accept even empty or none
			# empty or none won't able this feature
			self.__keySession       = sessionKey

	def setRedis(self, enable: bool, host: str, port: int, db: int= 0, password: str= None, enableFail: bool= False, enableInfo: bool= False, enableTrack: bool= False, enableSuccess: bool= False, enableWarning: bool= False, channel: str= None) -> None:
		"""

		:param enable:
		:param host:
		:param port:
		:param db:
		:param password:
		:param channel:
		:return:
		"""
		# assign value
		self.__enableRedis		= enable

		# config the redis property to connect to the server
		self.__redis.config(
			host		= host
			, port		= port
			, db		= db
			, password	= password
		)

		# enable level of pub/sub
		self.__redis.enableFail		= enableFail
		self.__redis.enableInfo		= enableInfo
		self.__redis.enableTrack	= enableTrack
		self.__redis.enableSuccess	= enableSuccess
		self.__redis.enableWarning	= enableWarning

		# set channel name
		self.__redis.channelSet(channel= channel)

	def success(self, title: str = '', content: Any = None, id: int = None) -> None:
		"""
		:param title:
		:param content:
		:param id:
		:return:
		"""
		self.__write(
			typeName    = 'SUCCESS'
			, title     = title
			, content   = content
			, color     = self.__StyleModifier.GREEN
			, logId     = id
		)

		#
		if self.__enableRedis and self.__redis.enableSuccess:
			#
			self.__redis.messagePush(
				title	= title
				, body	= content
			)

	def track(self, title: str = '', content: Any = None, id: int = None) -> None:
		"""

		:param title:
		:param content:
		:param id:
		:return:
		"""
		self.__write(
			typeName    = 'TRACK'
			, title     = title
			, content   = content
			, logId     = id
		)

		#
		if self.__enableRedis and self.__redis.enableTrack:
			#
			self.__redis.messagePush(
				title	= title
				, body	= content
			)

	def warning(self, title: str = '', content: Any = None, id: int = None) -> None:
		"""

		:param title:
		:param content:
		:param id:
		:return:
		"""
		self.__write(
			typeName    = 'WARNING'
			, title     = title
			, content   = content
			, color     = self.__StyleModifier.YELLOW
			, logId     = id
		)

		#
		if self.__enableRedis and self.__redis.enableWarning:
			#
			self.__redis.messagePush(
				title	= title
				, body	= content
			)

	class __StyleModifier:
		# Foreground
		BLUE            = '\033[94m'
		BLACK           = '\033[90m'
		CYAN            = '\033[96m'
		GREEN           = '\033[92m'
		GREY            = '\033[90m'
		MAGENTA         = '\033[95m'
		RED             = '\033[91m'
		WHITE           = '\033[97m'
		YELLOW          = '\033[93m'
		# Text style
		TEXT_BOLD       = '\033[1m'
		TEXT_UNDERLINE  = '\033[4m'
		# End up color
		ENDC            = '\033[0m'
