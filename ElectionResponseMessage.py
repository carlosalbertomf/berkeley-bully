from Message import Message

class ElectionResponseMessage(Message):
	def __init__(self, sourceId, destinationId):
		self.sourceId = sourceId
		self.destinationId = destinationId
		self.subject = 'election response'

	def getMessage(self):
		return 'Eleicao iniciado por ' + str(self.sourceId) 
