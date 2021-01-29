#!/usr/bin/env python
import time
import sys
import binascii
import socket

import fy_comn_def as fyCmnDef
import fy_send_pkt_def as sendDef
import fy_comn_memc_def as fyMemC
import fy_NSE_Config as nseConf
import fy_connect_function as fyConn

ERR_createFyersPacket 	= "createFyersPacket"
ERR_sendThread 			= "sendThread"
ERR_connRedisPub 		= "connRedisPub"

def createFyersPacket(fyToken, priceConv, payloadData, printFlag = False):
	"""
	[Function]  : Create fyers packet and compress the payload of the packet
	
	[Input] 	: fyToken 			-> Fyers Token
				  timestamp2_BCH 	-> Timestamp that is sent in the packet header of the NSE packet
				  packetCode 		-> Fyers transaction code.
				  packetFlag 		-> Flag that will be sent in the packet.
				  payloadData 		-> This is a List which contain dictionary of all the packet information
	[Output]	: Entire packet containing Fyers_Header + Compressed_Payload
	"""
	completeNetPacket = ''
	try:
		priceConv = int(priceConv)
		# print "%s fyToken:%s tcode:%s, payloadData:"%(ERR_createFyersPacket, fyToken, payloadData[fyMemC.K_MEMC_TRANS_CODE]), payloadData
		# print priceConv, int(payloadData[fyMemC.K_MEMC_LTP]*priceConv), int(payloadData[fyMemC.K_MEMC_OPEN_P]*priceConv), int(payloadData[fyMemC.K_MEMC_HIGH_P]*priceConv), int(payloadData[fyMemC.K_MEMC_LOW_P]*priceConv), int(payloadData[fyMemC.K_MEMC_CLOSING_P]*priceConv), int(payloadData[fyMemC.K_MEMC_CHANGE_P]*priceConv), int(payloadData[fyMemC.K_MEMC_PCT_CHANGE]*100)
		if int(payloadData[fyMemC.K_MEMC_TRANS_CODE]) == int(nseConf.NSE_T_CODE_7207) or int(payloadData[fyMemC.K_MEMC_TRANS_CODE]) == int(nseConf.NSE_T_CODE_7208):
			# completeNetPacket += sendDef.FY_P_NET_COMN_PAYLOAD.pack(priceConv, int(payloadData[fyMemC.K_MEMC_LTP]*priceConv), int(payloadData[fyMemC.K_MEMC_OPEN_P]*priceConv), int(payloadData[fyMemC.K_MEMC_HIGH_P]*priceConv), int(payloadData[fyMemC.K_MEMC_LOW_P]*priceConv), int(payloadData[fyMemC.K_MEMC_CLOSING_P]*priceConv), int(payloadData[fyMemC.K_MEMC_CHANGE_P]*priceConv), int(payloadData[fyMemC.K_MEMC_PCT_CHANGE]*100))
			## Change Ajay 2018-10-10
			completeNetPacket += sendDef.FY_P_NET_COMN_PAYLOAD.pack(
				priceConv, 
				int(round(payloadData[fyMemC.K_MEMC_LTP]*priceConv)), 
				int(round(payloadData[fyMemC.K_MEMC_OPEN_P]*priceConv)), int(round(payloadData[fyMemC.K_MEMC_HIGH_P]*priceConv)), int(round(payloadData[fyMemC.K_MEMC_LOW_P]*priceConv)), int(round(payloadData[fyMemC.K_MEMC_CLOSING_P]*priceConv)), ## Day open, high, low, close
				int(round(payloadData[fyMemC.K_MEMC_RT_OPEN]*priceConv)), int(round(payloadData[fyMemC.K_MEMC_RT_HIGH]*priceConv)), int(round(payloadData[fyMemC.K_MEMC_RT_LOW]*priceConv)), int(round(payloadData[fyMemC.K_MEMC_RT_CLOSE]*priceConv)), ## Min opnen, high low, close
				# int(round(payloadData[fyMemC.K_MEMC_CHANGE_P]*priceConv)), int(round(payloadData[fyMemC.K_MEMC_PCT_CHANGE]*100)), ## Change Ajay 2018-11-05
				# payloadData[fyMemC.K_MEMC_RT_TS],  ## Timestamp of this min
				int(payloadData[fyMemC.K_MEMC_RT_VOL])
			)
		
			if int(payloadData[fyMemC.K_MEMC_TRANS_CODE]) == int(nseConf.NSE_T_CODE_7208):
				completeNetPacket += sendDef.FY_P_NET_7208.pack(
					int(payloadData[fyMemC.K_MEMC_LTQ]), int(payloadData[fyMemC.K_MEMC_LTT]), 
					int(round(payloadData[fyMemC.K_MEMC_ATP]*priceConv)), int(payloadData[fyMemC.K_MEMC_VTT]), 
					int(payloadData[fyMemC.K_MEMC_TOT_BUY_Q]), int(payloadData[fyMemC.K_MEMC_TOT_SELL_Q]))

				##test
				# if int(fyToken) == 10100000003045:
				# 	d_open = payloadData[fyMemC.K_MEMC_HIGH_P]*priceConv
				# 	print "d_open : %s d_high: %s nd_high: %s LTT: %s  ATP: %s"%(payloadData[fyMemC.K_MEMC_OPEN_P], payloadData[fyMemC.K_MEMC_HIGH_P]*priceConv, int(round(d_open)), payloadData[fyMemC.K_MEMC_LTT], payloadData[fyMemC.K_MEMC_ATP])
					# a = sendDef.FY_P_NET_7208.pack(
					# 	payloadData[fyMemC.K_MEMC_LTQ], payloadData[fyMemC.K_MEMC_LTT], 
					# 	payloadData[fyMemC.K_MEMC_ATP]*priceConv, payloadData[fyMemC.K_MEMC_VTT], 
					# 	payloadData[fyMemC.K_MEMC_TOT_BUY_Q], payloadData[fyMemC.K_MEMC_TOT_SELL_Q])
				# print "A:\n"
					# print ''.join(binascii.hexlify(a)[i:i+2] for i in xrange(0,len(binascii.hexlify(a)),2))


				for i in range(0,sendDef.FY_P_BID_ASK_CNT/2):
					completeNetPacket += sendDef.FY_P_NET_BID_ASK.pack(payloadData[fyMemC.K_MEMC_BID_P_START +i]*priceConv, payloadData[fyMemC.K_MEMC_BID_QTY_START + i], payloadData[fyMemC.K_MEMC_BID_NUM_START + i])
				for i in range(0,sendDef.FY_P_BID_ASK_CNT/2):
					completeNetPacket += sendDef.FY_P_NET_BID_ASK.pack(payloadData[fyMemC.K_MEMC_ASK_P_START +i]*priceConv, payloadData[fyMemC.K_MEMC_ASK_QTY_START + i], payloadData[fyMemC.K_MEMC_ASK_NUM_START + i])

			##Testing 2018-10-11 Palash
			# if int(fyToken) == 10100000001363:
			# 	if int(payloadData[fyMemC.K_MEMC_LTT]) == 1539071160:
			# print "\nB:\n"
			# print ''.join(binascii.hexlify(completeNetPacket)[i:i+2] for i in xrange(0,len(binascii.hexlify(completeNetPacket)),2))
		elif int(payloadData[fyMemC.K_MEMC_TRANS_CODE]) in nseConf.NSE_STAT_TCODE_LIST:
			print int(payloadData[K_MKT_TYPE_6511]), int(payloadData[K_BCAST_MSG_L_6511]), payloadData[K_BCAST_MSG_6511]
			completeNetPacket += sendDef.FY_P_NET_6511.pack(int(payloadData[K_MKT_TYPE_6511]), int(payloadData[K_BCAST_MSG_L_6511]), payloadData[K_BCAST_MSG_6511])
		elif int(payloadData[fyMemC.K_MEMC_TRANS_CODE]) == int(nseConf.NSE_T_CODE_7202):
			completeNetPacket += sendDef.FY_P_EXTRA_OI_7202.pack(int(payloadData[fyMemC.K_MEMC_OI]))
		else:
			print "%s : unknown tcode %s"%(ERR_createFyersPacket, int(payloadData[fyMemC.K_MEMC_TRANS_CODE]))
		
		# print "without compress len:",len(completeNetPacket)
		# completeNetPacket = lzo.compress(completeNetPacket)
		# print "compressed p len:",len(completeNetPacket)
		
		## Header
		# compressedPacket 	= lzo.compress(json.dumps(payloadData))
		# print ' '.join(binascii.hexlify(headerPacked)[i:i+2] for i in xrange(0,len(binascii.hexlify(headerPacked)),2))
		# print "headerPacked:%s, Normal:%s,"%(len(headerPacked),len(headerPacked + compressedPacket))
		# valueHeader 		= (int(fyToken), payloadData[fyCmnDef.K_BCH_TS], int(packetCode), int(packetFlag), len(completeNetPacket))
		headerPacked = sendDef.FY_P_HEADER.pack(int(fyToken), payloadData[fyMemC.K_MEMC_TS_BCH], int(payloadData[fyMemC.K_MEMC_TRANS_CODE]), int(payloadData["tradeStat"]), len(completeNetPacket))
		completeNetPacket = headerPacked + completeNetPacket
		# if int(fyToken) == 101118112947201:
		# 	print ' '.join(binascii.hexlify(completeNetPacket)[i:i+2] for i in xrange(0,len(binascii.hexlify(completeNetPacket)),2))
		return {fyCmnDef.K_FUNCT_STAT: fyCmnDef.V_FUNCT_SUCCESS_1, fyCmnDef.K_FUN_DATA: completeNetPacket, fyCmnDef.K_ERR_MSG: ''}
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info() 
		return {fyCmnDef.K_FUNCT_STAT: fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA: '', fyCmnDef.K_ERR_MSG: "ERR : %s-> Line:%s .Cannot create fyers packet. Exception:%s"%(ERR_createFyersPacket, exc_tb.tb_lineno, str(e))}
	finally:
		None
	return {fyCmnDef.K_FUNCT_STAT: fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA: '', fyCmnDef.K_ERR_MSG: "ERR : %s->Unknown error"}

class SendPacket(object):
	"""
	[Input]	: 	logFD 	-> This is the file pointer in which the logs will be written
	"""
	# sendSockTuple 		= () ## This should contain destination ip address and destination port number.
	# sendLocalBindPort 	= 0 ## This should contain the local port to which socket will be bind to
	sentCount 			= 0
	debugFlag 			= 3 ## This is stop send
	# serverSocket 		= None
	sendPktQ 			= None
	listenEvent 		= None
	thTimeout 			= 0
	priceConv 			= 0
	sendPort 			= 0 ## The port on which the data has to be sent
	logErr_inst 		= None
	printFlag 			= False
	inputExchange       = ''
	inputSegment        = ''
	# redisConn			= None ## Change Ajay 2019-02-08

	@classmethod
	def changeClsFile(cls, newFd, createSockFlag = False):
		cls.sentCount 	= 0

	def __init__(self):
		super(SendPacket,self).__init__()
		self._sockInf = {} ## Sock-> sendAddr
		self.connSub(("127.0.0.1", SendPacket.sendPort), SendPacket.printFlag) ## The sender address has to be set here # Changed frpm 172.31.10.5 to 172.31.14.242 for higher instance upgrade.
		self.chnlName = '' ## Change Ajay 2019-02-08
		self.redisPub = None
		self.connRedisPub()

	def connRedisPub(self):
		## Change Ajay 2019-02-08
		## **************** Redis pub/sub connection ****************
		redisRetPub = fyConn.connectRedis()
		if redisRetPub[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1 or redisRetPub[fyCmnDef.K_FUN_DATA] == []:
			SendPacket.logErr_inst.LogError(None, "%s Cannot create Radis pub/sub connection. Error:%s"%(ERR_connRedisPub, redisRetPub[fyCmnDef.K_ERR_MSG]), printFlag=True)
			print "Program halted."
		
		radisConnPub = redisRetPub[fyCmnDef.K_FUN_DATA].pop()
		redisStat = False
		try:
			redisStat = radisConnPub.set("testKey","test value", ex=10) ## This is needed to test the connection.
		except Exception,e:
			SendPacket.logErr_inst.LogError(None, "%s Redis pub/sub status check failed. Error:%s"%(ERR_connRedisPub, redisRetPub[fyCmnDef.K_ERR_MSG]), printFlag=True)
			print "Program halted."
			
		if redisStat == False:
			SendPacket.logErr_inst.LogError(None, "%s Redis pub/sub set failed. Error:%s"%(ERR_connRedisPub, redisRetPub[fyCmnDef.K_ERR_MSG]), printFlag=True)
			print "Program halted."
			
		SendPacket.logErr_inst.LogError(None, "Connecting to pub/sub cache success.", printFlag=True)
		self.redisPub = radisConnPub
	
	def getSentCount(self):
		return SendPacket.sentCount

	def connSub(self, sendTuple, printFlag=False):
		try:
			sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self._sockInf[sendSock] = sendTuple
		except Exception,e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			errMsg = "ERR : %s-> Line:%s Creating connection failed. Exception:%s"%("SendPacket.connSub", exc_tb.tb_lineno, str(e))
			if SendPacket.logErr_inst != None: 
				SendPacket.logErr_inst(None, errMsg, printFlag=printFlag)

	def sendThread(self, printFlag=False):
		"""
		[Function] 	: This is a thread which will read packets from the queue and send packet if queue length is greater then 3
					 (i.e., there are 3 packets already in the queue) or if the timeout happen and there are less than 3 packets it will send them.
		
		[Input]		: 
		"""
		# if len(SendPacket.sendSockTuple) != 2 or not isinstance(SendPacket.sendSockTuple, tuple):
		# 	SendPacket.logErr_inst.LogError(None, "ERR : %s-> Invalid sendSockTuple:'%s'. Killing send thread."%(ERR_sendThread, str(SendPacket.sendSockTuple)), printFlag=printFlag)
		# 	return
		# if SendPacket.serverSocket == None:
		# 	SendPacket.logErr_inst.LogError(None, "ERR : %s-> Server socket is none. Killing send thread."%(ERR_sendThread), printFlag=printFlag)
			
		if SendPacket.sendPktQ == None or SendPacket.listenEvent == None or SendPacket.thTimeout == 0 or SendPacket.priceConv == 0:
			if SendPacket.logErr_inst:
				SendPacket.logErr_inst.LogError(None, "ERR : %s-> Invalid init of class variables. Killing send thread."%(ERR_sendThread), printFlag=printFlag)
			return

		## Change Ajay 2019-02-08
		if self.redisPub == None: 
			SendPacket.logErr_inst.LogError(None, "ERR : %s-> Redis connection found None. Killing send thread."%(ERR_sendThread), printFlag=printFlag)
			return

		## Change Ajay 2019-02-08
		self.chnlName = SendPacket.inputExchange + ':' + SendPacket.inputSegment
		SendPacket.logErr_inst.LogError(None, "ERR : %s-> Redis pub channel:%s"%(ERR_sendThread, self.chnlName), printFlag=printFlag)
		
		redisPub = self.redisPub.pubsub()
		# print "redisPub:", dir(redisPub)
		
		SendPacket.listenEvent.clear()
		instanceSentCnt = 0
		pktSize = 878 ## 512-144-2 => 512:max packet len, 144: max len of 7208, 2:len of num packets  
	
		if SendPacket.inputExchange ==  fyCmnDef.EXCHANGE_NAME_NSE:
			if SendPacket.inputSegment ==  fyCmnDef.SEG_NAME_FO_LIVE or SendPacket.inputSegment ==  fyCmnDef.SEG_NAME_FO_TEST:
				pktSize = 862 ##1024-160-2
		while True:
			instanceSentCnt += 1
			if SendPacket.sendPktQ.qsize() < 3:
				# if SendPacket.logErr_inst:
				# 	SendPacket.logErr_inst.LogError(None, "%s->Thread waiting"%(ERR_sendThread), printFlag=printFlag)
				event_is_set = SendPacket.listenEvent.wait(SendPacket.thTimeout)

			packetCount 	= 0 ## Number of packets combined in a single send
			packetToSend 	= '' ## combined packets
			for i in range(0,10):
				sizeQ = SendPacket.sendPktQ.qsize()
				if len(packetToSend) > pktSize: 
					break
				if sizeQ <= 0:
					break
				elif sizeQ >= sendDef.SEND_QUEUE_MAX_LEN:
					if SendPacket.logErr_inst: 
						SendPacket.logErr_inst.LogError(None, "%s Buffer overflow. sizeQ:%s"%(ERR_sendThread, sizeQ), printFlag=printFlag)
				# else:
				# 	if SendPacket.logErr_inst:
				# 		SendPacket.logErr_inst.LogError(None, "%s Unknown q size. sizeQ:%s"%(ERR_sendThread, sizeQ), printFlag=printFlag)
					
				infoDict = SendPacket.sendPktQ.get()
				for eachToken in infoDict:
					retFyPkt = createFyersPacket(eachToken, SendPacket.priceConv, infoDict[eachToken], printFlag = printFlag)
					if retFyPkt[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
						if SendPacket.logErr_inst:
							SendPacket.logErr_inst.LogError(None, retFyPkt[fyCmnDef.K_ERR_MSG], printFlag=printFlag)
						continue
					else:
						packetCount += 1
						packetToSend += retFyPkt[fyCmnDef.K_FUN_DATA]
						# channelName = eachToken
						# if SendPacket.inputSegment.endswith("TEST"):
						# 	channelName = str(eachToken)+"TEST"
						# countPackNet 	= sendDef.FY_P_NET_NUM_PACT.pack(*(1,))
						# publishPkt 		= countPackNet + retFyPkt[fyCmnDef.K_FUN_DATA]
						# self.redisPub.publish(channelName, publishPkt)
						# SendPacket.sentCount += 1

			if packetCount > 0:
				countPacketNet 	= sendDef.FY_P_NET_NUM_PACT.pack(*(packetCount,))
				packetToSend 	= countPacketNet + packetToSend ## number of packets is added at the begining of the entire packet struct
				# if len(packetToSend) < 512:
				# 	packetToSend = packetToSend + ' '*(512-len(packetToSend))

				try:
					# SendPacket.serverSocket.sendto(packetToSend, SendPacket.sendSockTuple)
					self.redisPub.publish(self.chnlName, packetToSend)
					# print "self.chnlName:", self.chnlName
					# for eachSock in self._sockInf:
					# 	# print "packetCount:%s"%(packetCount)
					# 	eachSock.sendto(packetToSend, self._sockInf[eachSock])
					SendPacket.sentCount += 1
					# sys.exit()
					# logErr_inst.LogError(None, "%s packet sent"%(ERR_sendThread), printFlag=printFlag)
				except Exception,e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					errMsg = "ERR : %s-> Line:%s Sending failed. Exception:%s"%(ERR_sendThread, exc_tb.tb_lineno, str(e))
					if SendPacket.logErr_inst:
						SendPacket.logErr_inst.LogError(None, errMsg, printFlag=printFlag)
