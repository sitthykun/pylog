"""
Author: masakokh
Version: 1.0.0
Note: Controller
"""
# built-in
import datetime
import glob
import os


class Controller:
	"""

	"""
	def __init__(self):
		"""

		"""
		# private
		self.__path = ''

	def __setPath(self, path: str) -> None:
		"""

		:param path:
		:return:
		"""
		#
		if path:
			self.__path = path

		#
		self.__path = os.path.join(self.__path, '')

	def cleanupByDate(self, num: int, path: str= '') -> None:
		"""

		:param num:
		:param path:
		:return:
		"""
		#
		self.__setPath(path)

		# get file list by pattern via glob function
		fileList    = glob.glob(f'{self.__path}')

		# iterate over the list of filepath and remove each file
		for fileItem in fileList:
			# remove one by one
			try:
				os.remove(fileItem)

			except OSError as e:
				print(f'Controller.cleanupByDate {str(e)}')

			except Exception as e:
				print(f'Controller.cleanupByDate {str(e)}')

	def deleteByDate(self, startDate: str, endDate: str, path: str= '') -> None:
		"""

		:param startDate:
		:param endDate:
		:param path:
		:return:
		"""
		pass

	def deleteByPattern(self, pattern: str, path: str= '') -> None:
		"""

		:param pattern: *abac*.txt, *.log, *.*
		:param path:
		:return:
		"""
		#
		self.__setPath(path)

		# get file list by pattern via glob function
		fileList    = glob.glob(f'{self.__path}{pattern}')

		# iterate over the list of filepath and remove each file
		for fileItem in fileList:
			# remove one by one
			try:
				os.remove(fileItem)

			except OSError as e:
				print(f'Controller.deleteByPattern {str(e)}')

			except Exception as e:
				print(f'Controller.deleteByPattern {str(e)}')
