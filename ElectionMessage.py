from Message import Message

class ElectionMessage(Message):
	def __init__(self, sourceId, destinationId):
		self.sourceId = sourceId
		self.destinationId = destinationId
		self.subject = 'election'

	def getMessage(self):
		return 'Eleicao - ' + str(self.sourceId) 
