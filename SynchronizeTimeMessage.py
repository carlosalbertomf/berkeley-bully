from Message import Message

class SynchronizeTimeMessage(Message):
  def __init__(self, sourceId, destinationId):
    self.sourceId = sourceId
    self.destinationId = destinationId
    self.subject = 'synchronization'
    
  def getMessage(self):
    return 'Sincronizando a requisicao de ' + str(self.sourceId)
