import pickle
import threading
from socket import *
from random import randint
from Timer import Timer
from functools import reduce
from PingMessage import PingMessage
from ElectionMessage import ElectionMessage
from ElectionResponseMessage import ElectionResponseMessage
from SynchronizeTimeMessage import SynchronizeTimeMessage
from UpdateTimeMessage import UpdateTimeMessage
from SynchronizeTimeResponseMessage import SynchronizeTimeResponseMessage
from CoordinatorPingMessage import CoordinatorPingMessage
from CoordinatorPingResponseMessage import CoordinatorPingResponseMessage

class Process:
	DEFAULT_PORT = 37022
	ELECTION_PORT = 37023
	SYNCHRONIZE_TIME_PORT = 37024
	PING_COORDINATOR_PORT = 37025
	SYNCHRONIZATION_TIME = 4
	COORDINATOR_PING_TIME = 15

	def __init__(self):
		self.isCoordinator = False
		self.pid = randint(0,1000)
		self.timer = Timer(increment=randint(1, 5))
		self.__initSockets()
		
		print('Meu ID eh: %s' %str(self.pid))
		listener = threading.Thread(target=self.__listenMessages)
		election = threading.Thread(target=self.__startElection)
		pingToCoordinator = threading.Timer(self.COORDINATOR_PING_TIME, self.__pingCoordinator)
		input('Press Enter para continuar...')
		listener.start()
		election.start()
		pingToCoordinator.start()
		self.__randomPing(randint(10, 20))

	def __str__(self):
		return 'pid: ' + str(self.pid)

	def __listenMessages(self):
		print('Aguardando mensagens...')
		client = socket(AF_INET, SOCK_DGRAM)
		client.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		client.bind(("", self.DEFAULT_PORT))

		while(True):
			print('Coordenador: ' + str(self.isCoordinator))
			print('Timer: ' + str(self.timer.getTime()))
			data, addr = client.recvfrom(1024)
			message = pickle.loads(data)
			if(message.sourceId != self.pid):
				self.__handleMessage(message, addr)
			
	def __handleMessage(self, message, addr):
		print('Mensagem Recebida: %s' %message.subject)				
		if (message.subject == "ping"):
			print(message.getMessage())
		elif (message.subject == "election"):
			self.isCoordinator = False
			if (self.pid > message.sourceId):
				self.__electionResponse(addr)					
				election = threading.Thread(target=self.__startElection)
				election.start()
		elif (message.subject == "synchronization"):
			self.__SyncTimeRequest(addr)
		elif (message.subject == "time update"):
			print("Timer atualizado para " + str(message.getMessage()))
			self.timer.setTime(message.getMessage())
		elif (message.subject == "coordinator ping"):
			if (self.isCoordinator):
				print(message.getMessage())
				message = CoordinatorPingResponseMessage(self.pid, message.sourceId)
				self.__sendMessage(message, addr[0], self.PING_COORDINATOR_PORT)

	def __sendBroadcastMessage(self, message):
		data = pickle.dumps(message)
		self.broadcastSocket.sendto(data, ('<broadcast>', self.DEFAULT_PORT))

	def __sendMessage(self, message, address,  port):
		data = pickle.dumps(message)
		self.udpSocket.sendto(data, (address, port))

	def __initSockets(self):
		self.udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self.broadcastSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self.broadcastSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		
	def __randomPing(self, interval):
		message = PingMessage(self.pid, 0)
		self.__sendBroadcastMessage(message)
		threading.Timer(interval, self.__randomPing, args=[interval]).start()

	def __electionResponse(self, address):
		message = ElectionResponseMessage(self.pid, 0)
		self.__sendMessage(message, address[0], self.ELECTION_PORT)
		
	def __startElection(self):
		print('\nInicializando eleicao...\n')
		electionSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		electionSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		electionSocket.settimeout(0.5)
		try:
			electionSocket.bind(("", self.ELECTION_PORT))
		except:
			electionSocket.close()
			return
		
		messages = []
		message = ElectionMessage(self.pid, 0)
		self.__sendBroadcastMessage(message)

		try:
			while(True):
				data, addr = electionSocket.recvfrom(1024)
				messages.append(pickle.loads(data))
		except timeout:
			print('Foi recebido %s mensagens de resposta da eleicao' %(len(messages)))

		print('messages:')
		print(messages)
		if len(messages) == 0:
			self.isCoordinator = True
			print('Eu sou o novo coordenador')
			threading.Timer(self.SYNCHRONIZATION_TIME, self.__synchronizeTimer).start()
		else:
			self.isCoordinator = False
			print('Eu perdi a eleicao')

		electionSocket.close()

	def __synchronizeTimer(self, interval=SYNCHRONIZATION_TIME):
		if self.isCoordinator:
			print('Inicializando a sincronizacao...')
			timerSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
			timerSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
			timerSocket.settimeout(0.5)
			timerSocket.bind(("", self.SYNCHRONIZE_TIME_PORT))
			
			time_list = [self.timer.getTime()]
			message = SynchronizeTimeMessage(self.pid, 0)
			self.__sendBroadcastMessage(message)

			try:
				while(True):
					data, addr = timerSocket.recvfrom(1024)
					time_list.append(pickle.loads(data).getMessage())
			except timeout:
				print('Foi recebido %s mensagens de resposta da eleicao' %( len(time_list) - 1 ))
			
			updatedTime = reduce(lambda x, y: x + y, time_list) / len(time_list)
			message = UpdateTimeMessage(self.pid, 0, updatedTime)
			print("Timer atualizado para " + str(updatedTime))
			print("\n")
			self.timer.setTime(updatedTime)
			self.__sendBroadcastMessage(message)
			threading.Timer(self.SYNCHRONIZATION_TIME, self.__synchronizeTimer).start()
			timerSocket.close()

	def __SyncTimeRequest(self, addr):
		message = SynchronizeTimeResponseMessage(self.pid, 0, self.timer.getTime())
		self.__sendMessage(message, addr[0], self.SYNCHRONIZE_TIME_PORT)

	def __initBroadcastSocket(self, port):
		broadcastSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		broadcastSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		broadcastSocket.bind(("", port))
		return broadcastSocket

	def __pingCoordinator(self):
		if (not self.isCoordinator):
			print('Pingando o coordenador...')
			pingSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
			pingSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
			pingSocket.bind(("", self.PING_COORDINATOR_PORT))
			pingSocket.settimeout(1)
			message = CoordinatorPingMessage(self.pid, 0)
			self.__sendBroadcastMessage(message)

			try:
				data, addr = pingSocket.recvfrom(1024)
				print('Coordinator esta ativo')
			except timeout:
				print('Coordinator caiu')
				election = threading.Thread(target=self.__startElection)
				election.start()

			pingSocket.close()

		threading.Timer(self.COORDINATOR_PING_TIME, self.__pingCoordinator).start()

