"""
Author 		: Ajay A U [ajay@fyers.in]
Version 	: 2.1
Copyright 	: Fyers Securities
Web			: fyers.in
"""
#!/usr/bin/env python
import sys
sys.path.append('C://Users//comp//Python27//Lib//site-packages') ##Comment in live
import os
import json
import time
import datetime
import argparse
import socket
import threading
import Queue
import struct
import binascii
from collections import deque

import fy_def as fyDef
import fy_comn_def as fyCmnDef
import fy_comn_Funct as fyCmnFunct
import fy_NSE_Config as nseConf
import fy_NSE_PacketFunct as nsePktFunc
import fy_connect_function as fyConn
import fy_connect_defines as fyConnDef
import fy_comn_memc_def as fyMemC
import memc_funct as cacheFunct
import MCX_config as mcx_conf
import MCX_packet_funct as mcxPktFunc
from fy_global_vars import SetGlobalVars
import fy_send_packet as sendPkt
import fy_send_pkt_def as sendDef

import fy_BSE_config as bseConf
import fy_BSE_packetFunct as bseFunct

import fy_util as fyUtil
## Set the timezone to IST ## This is critical
os.environ["TZ"] = "Asia/Kolkata" ## This is critical
time.tzset() ## This is critical

def initExcProcessing(inputExchange, inputSegment, debugDict):
	"""
	[Function] 	: 	Function create new day files.
					Initiate packet receive for the specific exchange and the segment.
					Create log files to write.
					Create temp directory to write data.
					Initiliaze all the other parameters required for processing.
	[Input]		: 	inputExchange 	-> NSE
				  	inputSegment 	-> CM/FO/CD
				  	debugDict 		-> Dict containing the debug info.
	[Output]	: 	Receive loops forever.
	"""
	inputExchange, inputSegment = inputExchange.upper(), inputSegment.upper()
	exchangeInfoDict = {}
	if inputExchange == fyCmnDef.EXCHANGE_NAME_NSE:
		## ********************** NSE **********************
		exchangeInfoDict["timestr"] = fyCmnDef.NSE_NEW_DAY_TIME
		if 	 inputSegment == fyCmnDef.SEG_NAME_CM_LIVE or inputSegment == fyCmnDef.SEG_NAME_CM_TEST:
			exchangeInfoDict["listenPort"] 			= nseConf.LIVE_RECV_PORT_CM
			exchangeInfoDict["sendThreadCount"] 	= sendDef.CM_SEND_THREADS
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_CM
			exchangeInfoDict["priceConv"] 			= nseConf.PRICE_CONV_100
			exchangeInfoDict["expectedCnetId"] 		= nseConf.CNET_ID_CM
			exchangeInfoDict["procThreadCount"] 	= nseConf.THREADS_PROC_CM
			exchangeInfoDict["packetStruct_7208"] 	= nseConf.NSE_P_7208_CM_STRUCT
			exchangeInfoDict["packetSize_7208"] 	= nseConf.NSE_P_7208_CM_SIZE
			exchangeInfoDict["packetStruct_7208_NEW"] = nseConf.NSE_P_7208_CM_STRUCT_NEW
			exchangeInfoDict["secInfoSize_6511"] 	= nseConf.NSE_SEC_INFO_SIZE_CM
			exchangeInfoDict["roundoff"] 			= 2
			exchangeInfoDict["inputSegment"]		= inputSegment
		elif inputSegment == fyCmnDef.SEG_NAME_FO_LIVE or inputSegment == fyCmnDef.SEG_NAME_FO_TEST:
			exchangeInfoDict["listenPort"] 			= nseConf.LIVE_RECV_PORT_FO
			exchangeInfoDict["sendThreadCount"] 	= sendDef.FO_SEND_THREADS
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_FO
			exchangeInfoDict["priceConv"] 			= nseConf.PRICE_CONV_100
			exchangeInfoDict["expectedCnetId"] 		= nseConf.CNET_ID_FO
			exchangeInfoDict["procThreadCount"] 	= nseConf.THREADS_PROC_FO
			exchangeInfoDict["packetStruct_7208"] 	= nseConf.NSE_P_7208_FO_STRUCT
			exchangeInfoDict["packetSize_7208"] 	= nseConf.NSE_P_7208_FO_SIZE
			exchangeInfoDict["packetStruct_7208_NEW"] 	= nseConf.NSE_P_7208_FO_STRUCT_NEW
			exchangeInfoDict["packetSize_7208_NEW"] 	= nseConf.NSE_P_7208_FO_SIZE_NEW
			exchangeInfoDict["secInfoSize_6511"] 	= nseConf.NSE_SEC_INFO_SIZE_FO + 4 ## Same for FO/CD
			exchangeInfoDict["roundoff"] 			= 2
			exchangeInfoDict["inputSegment"]		= inputSegment
		elif inputSegment == fyCmnDef.SEG_NAME_CD_LIVE or inputSegment == fyCmnDef.SEG_NAME_CD_TEST:
			exchangeInfoDict["listenPort"] 			= nseConf.LIVE_RECV_PORT_CD
			exchangeInfoDict["sendThreadCount"] 	= sendDef.CD_SEND_THREADS
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_CD
			exchangeInfoDict["priceConv"] 			= nseConf.PRICE_CONV_10000000
			exchangeInfoDict["expectedCnetId"] 		= nseConf.CNET_ID_CD
			exchangeInfoDict["procThreadCount"] 	= nseConf.THREADS_PROC_CD
			exchangeInfoDict["packetStruct_7208"] 	= nseConf.NSE_P_7208_FO_STRUCT
			exchangeInfoDict["packetSize_7208"] 	= nseConf.NSE_P_7208_FO_SIZE
			exchangeInfoDict["packetStruct_7208_NEW"] 	= nseConf.NSE_P_7208_FO_STRUCT_NEW
			exchangeInfoDict["packetSize_7208_NEW"] 	= nseConf.NSE_P_7208_FO_SIZE_NEW
			exchangeInfoDict["secInfoSize_6511"] 	= nseConf.NSE_SEC_INFO_SIZE_FO + 4 ## Same for FO/CD
			exchangeInfoDict["roundoff"] 			= 4
			exchangeInfoDict["inputSegment"]		= inputSegment
		else:
			## Error: Invalid segment
			return {fyCmnDef.K_FUNCT_STAT:fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA:"", fyCmnDef.K_ERR_MSG: "%sInvalid segment:'%s' exchange:'%s'."%(fyCmnDef.ERROR_initExcProcessing, inputSegment, inputExchange)}

		## Data changes only for test market data
		if inputSegment == fyCmnDef.SEG_NAME_CM_TEST:
			exchangeInfoDict["listenPort"] 			= nseConf.TEST_RECV_PORT_CM
			exchangeInfoDict["sendThreadCount"] 	= sendDef.CM_SEND_THREADS_TEST
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_CM_TEST
		elif inputSegment == fyCmnDef.SEG_NAME_FO_TEST:
			exchangeInfoDict["listenPort"] 			= nseConf.TEST_RECV_PORT_FO
			exchangeInfoDict["sendThreadCount"] 	= sendDef.FO_SEND_THREADS_TEST
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_FO_TEST
		elif inputSegment == fyCmnDef.SEG_NAME_CD_TEST:
			exchangeInfoDict["listenPort"] 			= nseConf.TEST_RECV_PORT_CD
			exchangeInfoDict["sendThreadCount"] 	= sendDef.CD_SEND_THREADS_TEST
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_CD_TEST
		else:
			None
		## ********************** END NSE **********************

	elif inputExchange == mcx_conf.MCX_EXCHANGE_NAME:
		exchangeInfoDict["roundoff"] 	= 2
		exchangeInfoDict["timestr"] 	= fyCmnDef.MCX_NEW_DAY_TIME
		## ********************** MCX **********************
		if   inputSegment == mcx_conf.SYM_SEGMENT_COM_NAME_LIVE:
			exchangeInfoDict["priceConv"] 			= mcx_conf.MCX_PRICE_CONV
			exchangeInfoDict["listenPort"] 			= mcx_conf.MCX_LISTEN_PORT
			exchangeInfoDict["sendThreadCount"] 	= sendDef.COM_SEND_THREADS
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_MCX_COM
		elif inputSegment == mcx_conf.SYM_SEGMENT_COM_NAME_TEST:
			exchangeInfoDict["priceConv"] 			= mcx_conf.MCX_PRICE_CONV
			exchangeInfoDict["listenPort"] = mcx_conf.INTERNAL_BC_RECV_MCX
			exchangeInfoDict["sendThreadCount"] 	= sendDef.COM_SEND_THREADS_TEST
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_MCX_COM_TEST
		else:
			## Error: Invalid segment
			return {fyCmnDef.K_FUNCT_STAT:fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA:"", fyCmnDef.K_ERR_MSG: "%sInvalid segment:'%s' exchange:'%s'."%(fyCmnDef.ERROR_initExcProcessing, inputSegment, inputExchange)}

		## ********************** END MCX **********************

	elif inputExchange == fyCmnDef.EXCHANGE_NAME_BSE:
		exchangeInfoDict["timestr"] = fyCmnDef.BSE_NEW_DAY_TIME
		## ********************** BSE **********************
		if 	 inputSegment == fyCmnDef.SEG_NAME_CM_LIVE_BSE or inputSegment == fyCmnDef.SEG_NAME_CM_TEST_BSE:
			exchangeInfoDict["listenPort"] 			= bseConf.BSE_INP_PORT_LIVE_CM
			exchangeInfoDict["sendThreadCount"] 	= sendDef.CM_SEND_THREADS_BSE
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_CM_BSE
			exchangeInfoDict["priceConv"] 			= nseConf.PRICE_CONV_100
			exchangeInfoDict["roundoff"] 			= 2
		elif inputSegment == fyCmnDef.SEG_NAME_FO_LIVE_BSE or inputSegment == fyCmnDef.SEG_NAME_FO_TEST_BSE:
			exchangeInfoDict["listenPort"] 			= bseConf.BSE_INP_PORT_LIVE_FO
			exchangeInfoDict["sendThreadCount"] 	= sendDef.FO_SEND_THREADS_BSE
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_FO_BSE
			exchangeInfoDict["priceConv"] 			= nseConf.PRICE_CONV_100
			exchangeInfoDict["roundoff"] 			= 2
		elif inputSegment == fyCmnDef.SEG_NAME_CD_LIVE_BSE or inputSegment == fyCmnDef.SEG_NAME_CD_TEST_BSE:
			exchangeInfoDict["listenPort"] 			= bseConf.BSE_INP_PORT_LIVE_CD
			exchangeInfoDict["sendThreadCount"] 	= sendDef.CD_SEND_THREADS_BSE
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_CD_BSE
			exchangeInfoDict["priceConv"] 			= nseConf.PRICE_CONV_10000000
			exchangeInfoDict["roundoff"] 			= 4
		else:
			## Error: Invalid segment
			return {fyCmnDef.K_FUNCT_STAT:fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA:"", fyCmnDef.K_ERR_MSG: "%sInvalid segment:'%s' exchange:'%s'."%(fyCmnDef.ERROR_initExcProcessing, inputSegment, inputExchange)}

		## Data changes only for test market data
		if inputSegment == fyCmnDef.SEG_NAME_CM_TEST_BSE:
			exchangeInfoDict["listenPort"] 			= bseConf.BSE_INP_PORT_TEST_CM
			exchangeInfoDict["sendThreadCount"] 	= sendDef.CM_SEND_THREADS_TEST_BSE
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_CM_TEST_BSE
		elif inputSegment == fyCmnDef.SEG_NAME_FO_TEST_BSE:
			exchangeInfoDict["listenPort"] 			= bseConf.BSE_INP_PORT_TEST_FO
			exchangeInfoDict["sendThreadCount"] 	= sendDef.FO_SEND_THREADS_TEST_BSE
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_FO_TEST_BSE
		elif inputSegment == fyCmnDef.SEG_NAME_CD_TEST_BSE:
			exchangeInfoDict["listenPort"] 			= bseConf.BSE_INP_PORT_TEST_CD
			exchangeInfoDict["sendThreadCount"] 	= sendDef.CD_SEND_THREADS_TEST_BSE
			exchangeInfoDict["multiSendPort"] 		= sendDef.MULTICAST_PORT_CD_TEST_BSE
		else:
			None
		## ********************** END BSE **********************
	else:
		## Invalid exchange
		return {fyCmnDef.K_FUNCT_STAT:fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA:"", fyCmnDef.K_ERR_MSG: "%s Invalid exchange:'%s'."%(fyCmnDef.ERROR_initExcProcessing, inputExchange)}

	if "priceConv" in exchangeInfoDict:
		## Decimals. Just in case if the value is int/
		exchangeInfoDict["priceConv"] = float(exchangeInfoDict["priceConv"])

	# print "cache:%s, DB:%s"%(debugDict["cache"], debugDict["db"])
	if debugDict["cache"].upper() == "LOCAL":
		## Change the defines if connecting to the local Redis server
		fyConnDef.REDIS_END_POINT_MASTER = fyConnDef.LOCAL_REDIS_END_POINT
	if debugDict["db"].upper() == "LOCAL":
		## Change the defines if connecting to the local DB server
		fyConnDef.DB_END_POINT_READER	= fyConnDef.DB_ENDPOINT_LOCAL_READER
		fyConnDef.DB_ENDPOINT_WRITER	= fyConnDef.DB_ENDPOINT_LOCAL_WRITER
		fyConnDef.DB_PORT 				= fyConnDef.DB_PORT_LOCAL
		fyConnDef.DB_UNAME 				= fyConnDef.DB_UNAME_LOCAL
		fyConnDef.DB_PASS 				= fyConnDef.DB_PASS_LOCAL


	dateTimeNow 	= datetime.datetime.now()
	dateStr 		= dateTimeNow.strftime('%Y%m%d')

	logFilePtr 			= None
	logErr_inst 		= fyCmnFunct.FYLog()
	fyTokenDict 		= {}
	tokenPrevValDict	= {} ## Dict containing token and previous day values. This will be used during premarket session. ## New addition Ajay 2018-04-05
	exceptTokenDict 	= {} ## These are the tokens which will be traded after market hours. ## New addition Ajay 2018-04-10
	tempDirectoryPath 	= ''
	exMsgDirPath 		= ''
	newDayRet = fyCmnFunct.newDayTrigger(logErr_inst, inputExchange, inputSegment, True)
	if newDayRet[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
		print newDayRet[fyCmnDef.K_ERR_MSG]
		print "Program halted."
		sys.exit()
	else:
		tokenPrevValDict	= newDayRet[fyCmnDef.K_FUN_DATA]["tokenPrevValDict"] ## new Ajay 2018-04-05
		exceptTokenDict		= newDayRet[fyCmnDef.K_FUN_DATA]["exceptTokenDict"] ## new Ajay 2018-04-10
		logFilePtr 			= newDayRet[fyCmnDef.K_FUN_DATA]["logFilePtr"]
		fyTokenDict 		= newDayRet[fyCmnDef.K_FUN_DATA]["fyTokenDict"]
		tempDirectoryPath 	= newDayRet[fyCmnDef.K_FUN_DATA]["tempDirectoryPath"]
		exMsgDirPath        = newDayRet[fyCmnDef.K_FUN_DATA]["msgDirPath"]
		fyCmnFunct.FYLog.changeLogFP(logFilePtr)
	
	if len(fyTokenDict) <= 0 or len(tempDirectoryPath) == 0:
		print "%sERROR init.."%(fyCmnDef.ERROR_initExcProcessing)
		print "Program halted."
		sys.exit()

	logErr_inst.LogError(None, "Started for exchange:%s, segment:%s listen_port:%s, send_port:%s"%(inputExchange, inputSegment, exchangeInfoDict["listenPort"], exchangeInfoDict["multiSendPort"]), printFlag=True)

	recv_sock = None
	try:
		recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
		recv_sock.bind(("", exchangeInfoDict["listenPort"]))
		recv_sock.setblocking(0)
		recv_sock.settimeout(fyDef.SOCK_RECV_TIMEOUT_SEC) ## Since socket receive is blocking we set timeout for the receive
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Socket connection failed. Except:%s"%(fyCmnDef.ERROR_initExcProcessing, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag=True)
		print "Program halted."
		sys.exit()
	logErr_inst.LogError(None, "Socket connection successful", printFlag=True)
	
	redisRet = fyConn.connectRedis()
	if redisRet[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1 or redisRet[fyCmnDef.K_FUN_DATA] == []:
		logErr_inst.LogError(None, "%s Cannot create Radis connection. Error:%s"%(fyCmnDef.ERROR_initExcProcessing, redisRet[fyCmnDef.K_ERR_MSG]), printFlag=True)
		print "Program halted."
		sys.exit()

	## ****** send socket ## Ajay 2018-06-29 ******
	sendThEvent 	= threading.Event()
	sendThEvent.clear()
	try:
		sendPkt.SendPacket.listenEvent 		= sendThEvent
		sendPkt.SendPacket.thTimeout 		= sendDef.SEND_PACKET_TIMEOUT
		sendPkt.SendPacket.priceConv 		= exchangeInfoDict["priceConv"]
		sendPkt.SendPacket.sendPort 		= exchangeInfoDict["multiSendPort"]

		sendPkt.SendPacket.logErr_inst 		= logErr_inst ## For logs
		sendPkt.SendPacket.printFlag 		= debugDict["print"] ## For printing errors

	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Send socket connection failed. Except:%s"%(fyCmnDef.ERROR_initExcProcessing, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag=True)
		sys.exit()
	logErr_inst.LogError(None, "Send group connection successful. sending IP: %s, port:%s"%(sendDef.MULTICAST_IP, exchangeInfoDict["multiSendPort"]), printFlag=True)

	sendPktQ = Queue.Queue(maxsize=sendDef.SEND_QUEUE_MAX_LEN) ## This queue is used to put the custom Fyers packet
	sendPkt.SendPacket.sendPktQ 		= sendPktQ
	sendPkt.SendPacket.inputExchange 	= inputExchange
	sendPkt.SendPacket.inputSegment 	= inputSegment
	sendThList = []
	if debugDict['nosend'] == False:
		for sendTh in range(0, exchangeInfoDict["sendThreadCount"]):
			sendPkt_inst = sendPkt.SendPacket()
			thSend = threading.Thread(name = 'sendThread%s'%(sendTh), target = sendPkt_inst.sendThread, args = (debugDict["print"], )) ## This thread is used to send the packets
			thSend.setDaemon(True) ## Daemon mode because once main thrad ends this thread will die
			thSend.start()
			sendThList.append(thSend)
		logErr_inst.LogError(None, "Send threads created.", printFlag=True)
	## ****** END: Multicast group send socket ******

	print "Connecting to Redis............"
	radisConn = redisRet[fyCmnDef.K_FUN_DATA].pop()
	redisStat = False
	try:
		redisStat = radisConn.set("testKey","test value", ex=10) ## This is needed to test the connection.
	except Exception,e:
		logErr_inst.LogError(None, "%s Redis status check failed. Error:%s"%(fyCmnDef.ERROR_initExcProcessing, redisRet[fyCmnDef.K_ERR_MSG]), printFlag=True)
		print "Program halted."
		sys.exit()
	if redisStat == False:
		logErr_inst.LogError(None, "%s Redis set failed. Error:%s"%(fyCmnDef.ERROR_initExcProcessing, redisRet[fyCmnDef.K_ERR_MSG]), printFlag=True)
		print "Program halted."
		sys.exit()
	logErr_inst.LogError(None, "Connecting to cache success.", printFlag=True)

	timeStampNow = time.time()
	## Global variables init
	## Always starting with market status as on. So care should be taken when starting the program after market hours.
	## 2018-02-23: Lets start the global market sttatus as false and change when traing status changes in 7208. 
	## 2018-03-12 Global market status will be selected manually when we start the function. Initially global status are set to true and if the function is successful then the status is changed accordingly.
	SetGlobalVars.global_marketStat = True
	SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_NORMAL_OPEN ## This is used to set the min data candles. Ajay 2018-02-23 ## New change Ajay 2018-04-10
	## This is not needed for MCX
	if inputExchange == fyCmnDef.EXCHANGE_NAME_NSE or inputExchange == fyCmnDef.EXCHANGE_NAME_BSE:
		retCheckMktStat = fyCmnFunct.checkMktHours(inputExchange, inputSegment, time.time())
		if retCheckMktStat[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
			logErr_inst.LogError(None, "Unable to verify market open status. Error:%s"%(retCheckMktStat[fyCmnDef.K_ERR_MSG]), printFlag=True)
		else:
			SetGlobalVars.global_minSetFlag = retCheckMktStat[fyCmnDef.K_FUN_DATA]
			if SetGlobalVars.global_minSetFlag in [fyCmnDef.MKT_F_NORMAL_OPEN, fyCmnDef.MKT_F_PARTIAL]:
				SetGlobalVars.global_marketStat = True
			else:
				SetGlobalVars.global_marketStat = False
			logErr_inst.LogError(None, "Market status is %s. Message:%s"%(retCheckMktStat[fyCmnDef.K_FUN_DATA], retCheckMktStat[fyCmnDef.K_ERR_MSG]), printFlag=True)
	# print "global_marketStat:%s global_minSetFlag:%s"%(global_marketStat, global_minSetFlag)
	# sys.exit()
	if inputExchange == fyCmnDef.EXCHANGE_NAME_BSE:
		SetGlobalVars.global_tradingStat = SetGlobalVars.global_minSetFlag ## Chang eAjay 2019-05-30
	if inputSegment in [fyCmnDef.SEG_NAME_CM_TEST, fyCmnDef.SEG_NAME_FO_TEST, fyCmnDef.SEG_NAME_CD_TEST]:
		# global_marketStat = global_minSetFlag = False ## This is for testing comment it in **LIVE**
		SetGlobalVars.global_marketStat, SetGlobalVars.global_minSetFlag = True, fyCmnDef.MKT_F_NORMAL_OPEN
		# global_marketStat, global_minSetFlag = False, fyCmnDef.MKT_F_CLOSED
		print "*************************** Market stat manually changed comment line 817 in LIVE***************************"

	SetGlobalVars.global_timeStamp  = 0 #int(timeStampNow - (timeStampNow % 60)) ## Current min timestamp ## This is made 0 for testing 2016-01-16
	SetGlobalVars.global_rxPackets, SetGlobalVars.global_packetProcess = 0, 0
	SetGlobalVars.global_rejected	  = 0 ## New Ajay 2018-06-01
	SetGlobalVars.global_newDayFlag = 0
	SetGlobalVars.global_7208Count  = 0

	## **************************** Start: Threads **************************** 
	## ********* Memcache real-time write thread ********* 
	cacheThEvent 	= threading.Event()
	cacheThEvent.clear()
	cacheQueue 		= Queue.Queue() ## This queue is used to put the Json values that has to be put into memcache
	setMemcKwargs 	= {"cacheConnectn": radisConn, "cacheQ": cacheQueue}
	setMemc_inst 	= cacheFunct.SetValToMemc(setMemcKwargs)
	cacheFunct.SetValToMemc.changeLogFInst(logErr_inst)
	cacheFunct.SetValToMemc.printFlag = debugDict["print"]
	cacheFunct.SetValToMemc.debugFlag = debugDict["debugFlag"]
	cacheFunct.SetValToMemc.inpExchange = inputExchange ## Change Ajay 2019-07-03
	cacheFunct.SetValToMemc.inpSegment 	= inputSegment ## Change Ajay 2019-07-03
	# cacheFunct.SetValToMemc.setFlag = False ## This line is for testing and should be commented in ** LIVE **
	cacheSetThRT = threading.Thread(name = 'CacheThreadRT', target = setMemc_inst.setMemcThread, args = (cacheThEvent, fyMemC.TIMEOUT_MEMC_THREAD)) ## This thread is used to send the packets
	cacheSetThRT.setDaemon(True) ## Daemon mode because once main thrad ends this thread will die 
	cacheSetThRT.start()
	logErr_inst.LogError(None, "Cache RT thread created.", printFlag=True)
	## ********* END: Memcache real-time write thread ********* 

	## ********* Memcache min write thread. This thread will keep setting for every new min *********
	minEventTh  = threading.Event()
	minEventTh.clear() ## start with clearing the event
	minQueue	= Queue.Queue(maxsize = fyDef.LEN_Q_MIN_DATA)
	minKwargs 	= {"cacheConnectn": radisConn, "cacheQ": minQueue}
	minSet_inst	= cacheFunct.MinDataOperation(minKwargs)
	cacheFunct.MinDataOperation.changeTempFPath(tempDirectoryPath)
	cacheFunct.MinDataOperation.changeLogFInst(logErr_inst)
	cacheFunct.MinDataOperation.changeSetFlag(True) ## Never set this to False. If set to False this will not set min values.
	cacheFunct.MinDataOperation.changeExceptTokens(exceptTokenDict)## New Ajay 2018-04-19
	if debugDict["develFlag"]:
		cacheFunct.MinDataOperation.changeSetFlag(False) ## Will not set the values if devel version
	cacheFunct.MinDataOperation.printFlag = debugDict["print"]
	cacheFunct.MinDataOperation.debugFlag = debugDict["debugFlag"]
	##New code to set nocache value 20181025 - Palash
	cacheFunct.MinDataOperation.nocache   = debugDict['nocache']
	##END
	##New Code for write flag 20181031 - Palash
	cacheFunct.MinDataOperation.nowrite   = debugDict['nowrite']
	##END
	# cacheFunct.MinDataOperation.setFlag = False ## This line is for testing and should be commented in ** LIVE **
	minSetThread = threading.Thread(name = "minSetCache", target = minSet_inst.minThreadFunct, args=(inputExchange, inputSegment, minEventTh, fyMemC.TIMEOUT_MIN_THREAD_MEMC))
	minSetThread.setDaemon(True) ## This one is to stop the thread when the program is started
	minSetThread.start()
	logErr_inst.LogError(None, "Cache Min thread created.", printFlag=True)
	## ********* End: Memcache min write thread *********

	## ********* Print packet count *********
	## This thread writes the packet count to the file and hence useful to track the packet parameters.
	countThread = threading.Thread(name = 'printThread', target = fyUtil.printPacketCount, args=(logErr_inst, 5, inputExchange, inputSegment, setMemc_inst, debugDict["print"], debugDict['nowrite']))
	countThread.setDaemon(True)
	countThread.start()
	## ********* End: Print packet count *********

	if inputExchange == fyCmnDef.EXCHANGE_NAME_NSE or inputExchange == fyCmnDef.EXCHANGE_NAME_BSE:
		## Not needed for MCX
		## ********* Check the market status *********
		## This will check the market status every min 
		mktStatTh = threading.Thread(name = 'checkMarketStat', target = fyUtil.th_marketStatCheck, args=(logErr_inst, inputExchange, inputSegment))
		mktStatTh.setDaemon(True)
		mktStatTh.start() ## This is comment for testing. Uncomment in **LIVE**
		# print "****************** mkt stat thread commented ******************"
		logErr_inst.LogError(None, "Market status check thread created.", printFlag=True)
		## ********* End:Check the market status *********

	## ********* New day check tread *********
	## The wait time is 600 sec it was made 6 sec for testing make it 600 for ** LIVE **
	newDayThread = threading.Thread(name = 'newDayThread', target = fyUtil.checkNewDate, args=(logErr_inst, 600, inputExchange, SetGlobalVars, exchangeInfoDict["timestr"])) ## which will check for the new day trigger 
	newDayThread.setDaemon(True) ## Daemon mode because once main thrad ends this thread will die 
	newDayThread.start()
	## ********* End: New day check tread *********
	## **************************** End: Threads **************************** 

	headerCheck_Q 	= deque(maxlen = fyDef.LENGTH_UDPH_CHECK_BUF) ##This queue will contain checksum that are sent in the UDP-Header
	cacheConn 		= radisConn
	minValDict 		= {} ## This will contain current min values of all the tokens
	curMinValDict 	= {} ## Only current min val dict
	oiTokenDict     = {} ## Oi changes 20190916 Palash
	while True:
		try:
			## Chaeck for new day and change the file pointers accordingly
			if SetGlobalVars.global_newDayFlag == 1:
				SetGlobalVars.global_newDayFlag = 0
				
				logErr_inst.LogError(None, "Failed tokens: %s"%(str(SetGlobalVars.global_FailedTokenDict)), debugDict["print"]) ## If the program is restarted after market this will be empty for new day trigger.
				## Reset the following dicts to flush old day data.
				del SetGlobalVars.global_FailedTokenDict, minValDict, curMinValDict, tokenPrevValDict, exceptTokenDict #New Change - Palash
				SetGlobalVars.global_FailedTokenDict = {}				
				minValDict 		= {} 
				curMinValDict 	= {} ##
				oiTokenDict     = {}
				tokenPrevValDict, exceptTokenDict 	= {}, {} ## New change Ajay 2018-04-10
				SetGlobalVars.global_rxPackets, SetGlobalVars.global_packetProcess, SetGlobalVars.global_7208Count, SetGlobalVars.global_rejected = 0, 0, 0, 0 ## Reset the counters
				logErr_inst.LogError(None, "New day trigger new files will be created", debugDict["print"])
				newDayRet = fyCmnFunct.newDayTrigger(logErr_inst, inputExchange, inputSegment, debugDict["print"]) ## Made True for testing change it in ** LIVE **
				# cacheFunct.MinDataOperation.changeSetFlag(global_minSetFlag) ## New day we should start this## Commente by Ajay 2018-03-12 since we should not change the set flag and stop sending the data to cache.
				if newDayRet[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
					logErr_inst.LogError(None, newDayRet[fyCmnDef.K_ERR_MSG], debugDict["print"])
				else:
					if newDayRet[fyCmnDef.K_FUN_DATA]["logFilePtr"] != None:
						try:
							logFilePtr.close() ## Close old file on new day trigger
						except Exception,e:
							exc_type, exc_obj, exc_tb = sys.exc_info()
							logErr_inst.LogError(None, "%s Line:%s. Failed to close previous day file. Except:%s"%(fyCmnDef.ERROR_initExcProcessing, exc_tb.tb_lineno, str(e)), debugDict["print"])
						logFilePtr 			= newDayRet[fyCmnDef.K_FUN_DATA]["logFilePtr"]
						fyCmnFunct.FYLog.changeLogFP(logFilePtr)
						logErr_inst.LogError(None, "%s New day log file creation success."%(fyCmnDef.ERROR_initExcProcessing), debugDict["print"])
					else:
						logErr_inst.LogError(None, "%s New day log file creation failed."%(fyCmnDef.ERROR_initExcProcessing), debugDict["print"])
						
					if len(newDayRet[fyCmnDef.K_FUN_DATA]["fyTokenDict"]) > 100: ##There should atleast 100 tokens.
						## Change to flush old values - Palash
						del fyTokenDict
						fyTokenDict 		= {}
						## Test for mem
						fyTokenDict 		= newDayRet[fyCmnDef.K_FUN_DATA]["fyTokenDict"]
						logErr_inst.LogError(None, "%s New day fy tokens were loaded successfully. Length of dict:%s"%(fyCmnDef.ERROR_initExcProcessing, len(fyTokenDict)), debugDict["print"])
					else:
						logErr_inst.LogError(None, "%s New day fy tokens were not loaded. Length of dict:%s"%(fyCmnDef.ERROR_initExcProcessing, len(fyTokenDict)), debugDict["print"])

					if len(newDayRet[fyCmnDef.K_FUN_DATA]["tempDirectoryPath"]) > 0: ## Change Ajay 2019-07-06
						tempDirectoryPath 	= newDayRet[fyCmnDef.K_FUN_DATA]["tempDirectoryPath"]
						logErr_inst.LogError(None, "%s New day temp file changed successfully. Path:%s"%(fyCmnDef.ERROR_initExcProcessing, tempDirectoryPath), debugDict["print"])
						cacheFunct.MinDataOperation.changeTempFPath(tempDirectoryPath)
					else:
						logErr_inst.LogError(None, "%s New day temp file failed."%(fyCmnDef.ERROR_initExcProcessing), debugDict["print"])

					## New Ajay 2019-07-06
					try:
						if len(newDayRet[fyCmnDef.K_FUN_DATA]["msgDirPath"]) > 0:
							exMsgDirPath        = newDayRet[fyCmnDef.K_FUN_DATA]["msgDirPath"]
						else:
							logErr_inst.LogError(None, "%s New day creating folder exMsgDirPath file failed."%(fyCmnDef.ERROR_initExcProcessing), debugDict["print"])
					except Exception,e:
						exc_type, exc_obj, exc_tb = sys.exc_info()
						logErr_inst.LogError(None, "%s Line:%s. New day creating folder exMsgDirPath file failed. Except:%s"%(fyCmnDef.ERROR_initExcProcessing, exc_tb.tb_lineno, str(e)), debugDict["print"])

					try:
						tokenPrevValDict	= newDayRet[fyCmnDef.K_FUN_DATA]["tokenPrevValDict"] ## new Ajay 2018-04-05
						exceptTokenDict		= newDayRet[fyCmnDef.K_FUN_DATA]["exceptTokenDict"] ## New Ajay 2018-04-10
						cacheFunct.MinDataOperation.changeExceptTokens(exceptTokenDict)## New Ajay 2018-04-19
					except Exception,e:
						exc_type, exc_obj, exc_tb = sys.exc_info()
						logErr_inst.LogError(None, "%s Line:%s. Previous and exception token load failed. Except:%s"%(fyCmnDef.ERROR_initExcProcessing, exc_tb.tb_lineno, str(e)), debugDict["print"])

			## TODO : We need to test the max length of the data for the exchanges
			recvData, recvAddr = recv_sock.recvfrom(2048) # buffer size is 1024 bytes ## 1050 is sent by RS and this is a constant.
			# print len(recvData), recvAddr
			# continue
			# print ' '.join(binascii.hexlify(recvData)[i:i+2] for i in xrange(0,len(binascii.hexlify(recvData)),2))
			(srcPort_UH, dstPort_UH, lenMsg_UH, check_UH) = nseConf.UDP_HEADER_STRUCT_P.unpack(recvData[nseConf.UDP_HEADER_OFFSET:nseConf.UDP_HEADER_OFFSET + nseConf.UDP_H_SIZE])
			# print srcPort_UH, dstPort_UH
			
			if exchangeInfoDict["listenPort"] != dstPort_UH:
				continue
			# print "inp port :", exchangeInfoDict["listenPort"]
			## This is to reject the duplicate packets. Not verified yet. 2018-03-16
			# try:
			# 	## If the checksum value is found in the queue then disguard the packet since it is duplicated
			# 	list(headerCheck_Q).index(check_UH)
			# 	print "duplicate"
			# 	continue
			# except ValueError:
			# 	headerCheck_Q.append(check_UH)
			# except Exception,e:
			# 	headerCheck_Q.append(check_UH)
			SetGlobalVars.global_rxPackets += 1
			recvData = recvData[nseConf.UDP_HEADER_OFFSET + nseConf.UDP_H_SIZE:] # UDP-Header is removed

			# continue ## For testing
			# *********************************** NSE ***********************************
			if inputExchange == fyCmnDef.EXCHANGE_NAME_NSE:
				(cNetId_Recv,) = nseConf.NSE_CNET_ID_PACKET_STRUCT.unpack(recvData[:nseConf.NSE_CNET_ID_PACKET_SIZE])
				# print "cNetId_Recv:", cNetId_Recv
				if cNetId_Recv != exchangeInfoDict["expectedCnetId"]:
					logErr_inst.LogError(None, "%s cnet ID do not match. cNetId_Recv:%s, expectedCnetId:%s"%(fyCmnDef.ERROR_initExcProcessing, cNetId_Recv, exchangeInfoDict["expectedCnetId"]), debugDict["print"])
					continue
				
				retValPacket = nsePktFunc.processNSEPacket(logErr_inst, recvData, fyTokenDict, exchangeInfoDict, SetGlobalVars.global_FailedTokenDict, SetGlobalVars.global_tradingStat, debugDict["print"], debugDict["debugFlag"])
				if retValPacket[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
					logErr_inst.LogError(None, retValPacket[fyCmnDef.K_ERR_MSG], debugDict["print"])
					continue
				else:
					for eachPacket in retValPacket[fyCmnDef.K_FUN_DATA]:
						# print "eachPacket:", eachPacket
						packetDict = retValPacket[fyCmnDef.K_FUN_DATA][eachPacket]
						if retValPacket[fyCmnDef.K_FUN_DATA][eachPacket][fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
							# print "packetDict:",packetDict
							logErr_inst.LogError(None, "%s Failed %s"%(fyCmnDef.ERROR_initExcProcessing, str(packetDict)), debugDict["print"])

						# print "tcode:",packetDict["tcode"]
						SetGlobalVars.global_packetProcess += 1
						if packetDict["tcode"] == nseConf.NSE_T_CODE_7207:
							# None
							# for eachValue in packetDict[fyCmnDef.K_FUN_DATA]:
							# 	print eachValue,packetDict[fyCmnDef.K_FUN_DATA][eachValue]
							fyUtil.setToMemc(logErr_inst, inputExchange, inputSegment, exchangeInfoDict["roundoff"], tempDirectoryPath, cacheConn, packetDict[fyCmnDef.K_FUN_DATA], cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, sendThEvent, sendPktQ, printFlag = debugDict["print"], debugFlag = debugDict["debugFlag"], nocache = debugDict["nocache"], develFlag = debugDict["develFlag"], noSend = debugDict['nosend']) ## commented for testing on 2018-01-16
						# elif packetDict["tcode"] == nseConf.NSE_T_CODE_7216: ## Not tested yet 
						# 	fyUtil.setToMemc(logErr_inst, inputExchange, inputSegment, exchangeInfoDict["roundoff"], tempDirectoryPath, cacheConn, packetDict[fyCmnDef.K_FUN_DATA], cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, printFlag = debugDict["print"], debugFlag = debugDict["debugFlag"], nocache = debugDict["nocache"], develFlag = debugDict["develFlag"]) ## new addition Ajay 2018-03-16
						elif packetDict["tcode"] == nseConf.NSE_T_CODE_7208:
							SetGlobalVars.global_7208Count += 1
							# for eachToken in packetDict[fyCmnDef.K_FUN_DATA]:
							# 	print eachToken, packetDict[fyCmnDef.K_FUN_DATA][eachToken]
							fyUtil.setToMemc(logErr_inst, inputExchange, inputSegment, exchangeInfoDict["roundoff"], tempDirectoryPath, cacheConn, packetDict[fyCmnDef.K_FUN_DATA], cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, sendThEvent, sendPktQ, printFlag = debugDict["print"], debugFlag = debugDict["debugFlag"], nocache = debugDict["nocache"], develFlag = debugDict["develFlag"], noSend = debugDict['nosend']) ## commented for testing on 

						elif packetDict["tcode"] in nseConf.NSE_STAT_TCODE_LIST:
							# print packetDict["tcode"], "packetDict:",packetDict
							## Instead of setting the market status on transaction codes we can set it on trading status sent in 7208 which can haandle pre-market and after-market data also.

							# print "packetDict[tcode]", packetDict["tcode"]
							if packetDict["tcode"] == 6511 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
								## BC_OPEN_MESSAGE (6511). This is sent when the market is opened.
								SetGlobalVars.global_marketStat = True
								SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_NORMAL_OPEN ## New change Ajay 2018-04-10 
								logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s"%(fyCmnDef.ERROR_initExcProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511]))
							elif packetDict["tcode"] == 6521 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
								## BC_CLOSE_MESSAGE (6521). This is sent when the market is closed.
								SetGlobalVars.global_marketStat = False
								SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_CLOSED ## New change Ajay 2018-04-10
								logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s"%(fyCmnDef.ERROR_initExcProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511]))
							elif   packetDict["tcode"] == 6531 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
								## BC_PREOPEN_SHUTDOWN_MSG (6531). This is sent when the market is preopened.
								SetGlobalVars.global_tradingStat = 1 ## Added by Ajay 2018-03-19 ## 1 is for preopen
								SetGlobalVars.global_marketStat = False
								SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_PREOP ## New change Ajay 2018-04-10
								logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s, global_tradingStat:%s"%(fyCmnDef.ERROR_initExcProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511], SetGlobalVars.global_tradingStat))
							elif   packetDict["tcode"] == 6571 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
								SetGlobalVars.global_marketStat = False
								SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_CLOSED
								logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s, global_tradingStat:%s"%(fyCmnDef.ERROR_initExcProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511], SetGlobalVars.global_tradingStat))
							elif packetDict["tcode"] == 6583 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
								## BC_CLOSING_START(6583). This is sent when closing session is opened.
								SetGlobalVars.global_marketStat = False
								SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_CLOSED ## New change Ajay 2018-04-10
								logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s"%(fyCmnDef.ERROR_initExcProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511]))
							elif packetDict["tcode"] == 6584 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
								SetGlobalVars.global_marketStat = False #True ## This was changed to False on 2018-02-21 by Ajay. Sice we are updating min candles and we shouldnot update those after the market closing session has been closed.
								SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_CLOSED ## New change Ajay 2018-04-10
								logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s"%(fyCmnDef.ERROR_initExcProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511]))
							else:
								logErr_inst.LogError(None, "%s No action global_marketStat:%s for Tcode:%s, market type:%s"%(fyCmnDef.ERROR_initExcProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511]))

							# cacheFunct.MinDataOperation.changeSetFlag(global_minSetFlag) ## When the market closes we should stop updating the min values ## Commented by Ajay 2018-03-12. The min data itself wont be sent to the thread instead of stopping te thread to set.
						## Oi Addition 20190916 Palash
						elif packetDict["tcode"] == nseConf.NSE_T_CODE_7202 and inputSegment not in (fyCmnDef.SEG_NAME_CM_LIVE , fyCmnDef.SEG_NAME_CM_TEST):
							fyUtil.setOiToThread(logErr_inst, cacheConn, inputExchange, inputSegment, packetDict[fyCmnDef.K_FUN_DATA], cacheQueue, sendPktQ, oiTokenDict, printFlag = debugDict["print"], debugFlag = debugDict["debugFlag"], nocache = debugDict["nocache"], noSend = debugDict["nosend"])
						else:
							## We dont need other transaction codes
							None
			# *********************************** END : NSE ***********************************
			elif inputExchange == mcx_conf.MCX_EXCHANGE_NAME:
				# Function to process mcx packets
				retValPacket = mcxPktFunc.processMCXPacket(logErr_inst, recvData, fyTokenDict, SetGlobalVars.global_FailedTokenDict, SetGlobalVars.global_tradingStat, SetGlobalVars.global_TS_NSE, debugDict["print"], debugDict["debugFlag"])
				if retValPacket[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
					logErr_inst.LogError(None, retValPacket[fyCmnDef.K_ERR_MSG], debugDict["print"])
					continue
				else:
					for eachPacket in retValPacket[fyCmnDef.K_FUN_DATA]:
						packetDict = retValPacket[fyCmnDef.K_FUN_DATA][eachPacket]
						if retValPacket[fyCmnDef.K_FUN_DATA][eachPacket][fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
							logErr_inst.LogError(None, "Failed %s"%(ERROR_initMCXProcessing, str(packetDict), debugDict["print"]))

						SetGlobalVars.global_packetProcess += 1
						# Sets value to cache and creates one minute candles
						# fyUtil.setToMemc(logErr_inst, SetGlobalVars, inputExchange, inputSegment, exchangeInfoDict["roundoff"], tempDirectoryPath, cacheConn, packetDict[fyCmnDef.K_FUN_DATA], cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, printFlag = debugDict["print"], debugFlag = debugDict["debugFlag"], nocache = debugDict["nocache"], develFlag = debugDict["develFlag"]) ## commented for testing on 2018-01-16
						#testing - palash
						# print 'tcode' in packetDict
						if 'tcode' in packetDict:
							if packetDict['tcode'] == nseConf.NSE_T_CODE_7208:
								SetGlobalVars.global_7208Count  += 1
								fyUtil.setToMemc(logErr_inst, inputExchange, inputSegment, exchangeInfoDict["roundoff"], tempDirectoryPath, cacheConn, packetDict[fyCmnDef.K_FUN_DATA], cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, sendThEvent, sendPktQ, printFlag = debugDict["print"], debugFlag = debugDict["debugFlag"], nocache = debugDict["nocache"], develFlag = debugDict["develFlag"], noSend = debugDict['nosend']) ## commented for testing on 2018-01-16
							elif packetDict['tcode'] == mcx_conf.MCX_P_CODE_EXC_MSG:
								fyUtil.setMsgToCache(logErr_inst, SetGlobalVars, inputExchange, inputSegment, packetDict[fyCmnDef.K_FUN_DATA], packetDict['timeStamp'], cacheConn, exMsgDirPath, printFlag = debugDict["print"])
						# else:
						# 	logErr_inst.LogError(None, str(packetDict[fyCmnDef.K_FUN_DATA]), False)

			elif inputExchange == fyCmnDef.EXCHANGE_NAME_BSE:
				ret_bseFunct = bseFunct.processBSEPackets(logErr_inst, recvData, fyTokenDict, SetGlobalVars.global_FailedTokenDict, SetGlobalVars.global_tradingStat, exchangeInfoDict, debugDict["print"], debugDict["debugFlag"])
				# print "ret_bseFunct:", ret_bseFunct
				SetGlobalVars.global_packetProcess += 1
				if ret_bseFunct[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
					logErr_inst.LogError(None, ret_bseFunct[fyCmnDef.K_ERR_MSG], debugDict["print"])
					continue
				else:
					##There are no multiple packets for BSE in same payload. 
					tCode = ret_bseFunct["tcode"]
					if tCode == bseConf.BSE_MKT_PIC_CODE_2020:
						## Market Pic
						# print "tCode:", tCode
						# print "ret_bseFunct[fyCmnDef.K_FUN_DATA]:", ret_bseFunct[fyCmnDef.K_FUN_DATA]
						# continue
						SetGlobalVars.global_7208Count += 1
						# for eachToken in ret_bseFunct[fyCmnDef.K_FUN_DATA]:
						# 	print eachToken, ret_bseFunct[fyCmnDef.K_FUN_DATA][eachToken]
						# print "mkt pic:",ret_bseFunct[fyCmnDef.K_FUN_DATA]
						# SetGlobalVars.global_tradingStat = SetGlobalVars.global_minSetFlag ## Chang eAjay 2019-05-30

						fyUtil.setToMemc(logErr_inst, inputExchange, inputSegment, exchangeInfoDict["roundoff"], tempDirectoryPath, cacheConn, ret_bseFunct[fyCmnDef.K_FUN_DATA], cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, sendThEvent, sendPktQ, printFlag = debugDict["print"], debugFlag = debugDict["debugFlag"], nocache = debugDict["nocache"], develFlag = debugDict["develFlag"], noSend = debugDict['nosend']) ## commented for testing on 
						# ret_bseFunct[fyCmnDef.K_FUN_DATA][fyCmnDef.K_TRADIN_STAT]
					elif tCode == bseConf.BSE_SENSEX_BCAST_CODE_2011 or tCode == bseConf.BSE_SENSEX_INDEX_BCAST_CODE_2012:
						# SetGlobalVars.global_tradingStat = SetGlobalVars.global_minSetFlag ## Chang eAjay 2019-05-30
						# None
						# print "bse pic:",ret_bseFunct[fyCmnDef.K_FUN_DATA]
						fyUtil.setToMemc(logErr_inst, inputExchange, inputSegment, exchangeInfoDict["roundoff"], tempDirectoryPath, cacheConn, ret_bseFunct[fyCmnDef.K_FUN_DATA], cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, sendThEvent, sendPktQ, printFlag = debugDict["print"], debugFlag = debugDict["debugFlag"], nocache = debugDict["nocache"], develFlag = debugDict["develFlag"], noSend = debugDict['nosend']) ## commented for testing on 
						
					elif tCode == bseConf.BSE_SESSION_CHANGE_CODE_2002 or tCode == bseConf.BSE_SESSION_CHANGE_CODE_2003:
						logErr_inst.LogError(None, "%s tCode:%s Market stat changed :%s"%(fyCmnDef.ERROR_initExcProcessing, tCode, str(ret_bseFunct[fyCmnDef.K_FUN_DATA])), debugDict["print"])
						if ret_bseFunct[fyCmnDef.K_FUN_DATA]["mktStat"] != None:
							SetGlobalVars.global_minSetFlag = ret_bseFunct[fyCmnDef.K_FUN_DATA]["mktStat"]
							SetGlobalVars.global_tradingStat = SetGlobalVars.global_minSetFlag
							if ret_bseFunct[fyCmnDef.K_FUN_DATA]["mktStat"] == fyCmnDef.MKT_F_NORMAL_OPEN:
								SetGlobalVars.global_marketStat = True
							else:
								SetGlobalVars.global_marketStat = False

					elif tCode == bseConf.BSE_CLOSE_P_BCAST_CODE_2014:
						None
						# print "tCode:", tCode
						# SetGlobalVars.global_tradingStat = fyCmnDef.MKT_F_CLOSED ## Change Ajay 2019-05-30

			else:
				logErr_inst.LogError(None, "%s Invalid exchnage:%s"%(fyCmnDef.ERROR_initExcProcessing, inputExchange), debugDict["print"])
		except socket.timeout: ## This is normal error 
			# print "sock Timeout"
			continue
		except Exception,e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			logErr_inst.LogError(None, "%s Line:%s. Receive failed. Except:%s"%(fyCmnDef.ERROR_initExcProcessing, exc_tb.tb_lineno, str(e)), debugDict["print"])
			
	time.sleep(6) ## This is for testing

	return {fyCmnDef.K_FUNCT_STAT:fyCmnDef.V_FUNCT_SUCCESS_1, fyCmnDef.K_FUN_DATA:"", fyCmnDef.K_ERR_MSG: ""} ## This is for testing and we won't be returning from here

def main():
	## Argument Parser
	nseParser = argparse.ArgumentParser(description="NSE argument parser.")
	nseParser.add_argument("-ex"	, action = "store", dest="exchangeType", default = "NSE", help = "Exchange type. Eg: %s"%(fyCmnDef.EXCHANGE_NAME_NSE)) 
	nseParser.add_argument("-seg"	, action = "store", dest="segmentType", default = "", help = "segment type. Eg: [%s/%s/%s/%s/%s/%s]"%(fyCmnDef.SEG_NAME_CM_LIVE, fyCmnDef.SEG_NAME_FO_LIVE, fyCmnDef.SEG_NAME_CD_LIVE, fyCmnDef.SEG_NAME_CM_TEST, fyCmnDef.SEG_NAME_FO_TEST, fyCmnDef.SEG_NAME_CD_TEST))
	nseParser.add_argument("-send"	, action = "store", dest="sendOption", default = "slow", help = "Send option. Eg: ['fast'->To send all data, 'slow'->To send slow data, 'no'-> To stop sending data.]")
	nseParser.add_argument("-pdb"	, action = "store_true", dest="pdbFlag", default = False,  help = "Start the program with PDB.")
	# nseParser.add_argument("-debug"	, action = "store_true", dest="debugFlag", default = False,  help = "Prints additional debug information") ## this will help in debuging the program with additional prints
	nseParser.add_argument("-debug"	, action = "store", dest="debugFlag", default = "", help = "Additional debug options.[Options]: [%s/%s/%s]"%(fyCmnDef.DEBUG_TEST, fyCmnDef.DEBUG_ADDITNL_PRINT, fyCmnDef.DEBUG_TIME)) ## this will help in debuging the program with additional prints
	nseParser.add_argument("-nocache"		, action = "store_true", dest="nocache", default = False,  help = "In case of restart try to to get previous values from cahche. Do not use it in live. If you are running with test data this will be helpful.") ## Default is set to False. This should be only used for testing and ** DO NOT USE IT ON LIVE **
	nseParser.add_argument("-nowrite"		, action = "store_true", dest="nowrite", default = False,  help = "If true, does not write to files.")
	nseParser.add_argument("-nosend"		, action = "store_true", dest="nosend", default = False,  help = "If this flag is set, packets won't be sent to streaming server.")
	nseParser.add_argument("-cache"	, action = "store", dest="cache", default = "", help = "Set cache to local when you wast to access local redis.")
	nseParser.add_argument("-db"	, action = "store", dest="db", default = "", help = "Set cache to local when you wast to access local DB.")
	nseParser.add_argument("-p"		, action = "store_true", dest="printFlag", default = False,  help = "Start printing the packet count.") ## Default is set to true for testing purpose it should be set to False to stop printing the packets received.
	nseParser.add_argument("-devel"		, action = "store_true", dest="develFlag", default = False,  help = "Starting under devel env which won't set to cache or write to files. Not implemented yet.") ## Default is set to true for testing purpose it should be set to False to stop printing the packets received.
	
	nseParser.add_argument("-v"		, action = "version", version="%(prog)s {version}".format(version = fyCmnDef._NSE_PROG_VERSION))
	nseParser.add_argument("--version", action = "version", version="%(prog)s {version}".format(version = fyCmnDef._NSE_PROG_VERSION))
	nseArgs = nseParser.parse_args()
	
	# print "nseArgs.exchangeType:", nseArgs.exchangeType
	# print "nseArgs.nocache:%s"%nseArgs.nocache
	# sys.exit()

	inputExchange 	= nseArgs.exchangeType.upper()
	inputSegment 	= nseArgs.segmentType.upper()
	
	debugDict = {
					"sendOption"	: nseArgs.sendOption, 
					"pdb"			: nseArgs.pdbFlag, 
					"print"			: nseArgs.printFlag, 
					"debugFlag"		: nseArgs.debugFlag,
					"nocache"		: nseArgs.nocache,
					"develFlag"		: nseArgs.develFlag,
					"nowrite"		: nseArgs.nowrite,
					"nosend"		: nseArgs.nosend,
					"cache"			: nseArgs.cache,
					"db"			: nseArgs.db,
				}
	returninitNSE = initExcProcessing(inputExchange, inputSegment, debugDict = debugDict)
	if returninitNSE[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
		print returninitNSE[fyCmnDef.K_ERR_MSG]
		nseParser.print_help()
		sys.exit(2)
	# else:
	# 	print "******************************"
	# 	print "Invalid Exchange %s"%(inputExchange) 
	# 	print "******************************"
	# 	nseParser.print_help()
	# 	sys.exit(2)

if __name__ == "__main__":
	main()
