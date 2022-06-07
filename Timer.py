import time
import threading

class Timer:
	def __init__(self, time=0, increment=1, secondsToUpdate=1):
		self.time = time
		self.increment = increment
		self.secondsToUpdate = secondsToUpdate

		time_thread = threading.Thread(target=self.__start)
		time_thread.start()

	def getTime(self):
		return self.time

	def setTime(self, time):
		self.time = time

	def updateTime(self):
		self.time += self.increment

	def __start(self):
		while(True):
			self.updateTime()
			time.sleep(self.secondsToUpdate)