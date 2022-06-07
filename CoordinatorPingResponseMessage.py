from Message import Message

class CoordinatorPingResponseMessage(Message):
	def __init__(self, sourceId, destinationId):
		self.sourceId = sourceId
		self.destinationId = destinationId
		self.subject = 'coordinator ping response'

	def getMessage(self):
		return 'Ping de resposta recebido do coordenador ' + str(self.sourceId) 
