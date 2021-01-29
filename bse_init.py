#!/usr/bin/env python

import sys, os, time, json
sys.path.append("c:\python27\lib\site-packages")
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
from fy_global_vars import SetGlobalVars
import fy_send_packet as sendPkt
import fy_send_pkt_def as sendDef

import nse_init
import fy_BSE_config as bseConf
import fy_BSE_packetFunct as bseFunct
## Set the timezone to IST ## This is critical
os.environ["TZ"] = "Asia/Kolkata" ## This is critical
time.tzset() ## This is critical

def initBSEProcessing(inputExchange, inputSegment, debugDict):
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
	# global global_rxPackets, global_packetProcess, global_marketStat, global_timeStamp, global_FailedTokenDict, global_7208Count, global_minSetFlag, global_newDayFlag, global_tradingStat, global_rejected
	if inputExchange != fyCmnDef.EXCHANGE_NAME_BSE:
		return {fyCmnDef.K_FUNCT_STAT:fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA:"", fyCmnDef.K_ERR_MSG: "%sInvalid exchange %s"%(fyCmnDef.ERROR_initNSEProcessing, inputExchange)}

	listenPort, priceConv, roundoff = 0, 0, 0
	multiSendPort, sendThreadCount = 0, 0 ## Added for stream sents 20181031 - Palash
	if 	 inputSegment == fyCmnDef.SEG_NAME_CM_LIVE:
		listenPort			= bseConf.BSE_INP_PORT_LIVE_CM
		priceConv 			= nseConf.PRICE_CONV_100
		roundoff			= 2
		multiSendPort 		= sendDef.MULTICAST_PORT_CM_BSE
		sendThreadCount 	= sendDef.CM_SEND_THREADS
	elif inputSegment == fyCmnDef.SEG_NAME_FO_LIVE:
		listenPort			= bseConf.BSE_INP_PORT_LIVE_FO
		priceConv 			= nseConf.PRICE_CONV_100
		roundoff			= 2
		multiSendPort 		= sendDef.MULTICAST_PORT_FO_BSE
		sendThreadCount 	= sendDef.FO_SEND_THREADS
	elif inputSegment == fyCmnDef.SEG_NAME_CD_LIVE:
		listenPort			= bseConf.BSE_INP_PORT_LIVE_CD
		priceConv 			= nseConf.PRICE_CONV_10000000
		roundoff			= 4
		multiSendPort 		= sendDef.MULTICAST_PORT_CD_BSE
		sendThreadCount 	= sendDef.CD_SEND_THREADS
	elif inputSegment == fyCmnDef.SEG_NAME_CM_TEST:
		listenPort			= bseConf.BSE_INP_PORT_TEST_CM
		priceConv 			= nseConf.PRICE_CONV_100
		roundoff			= 2
		multiSendPort 		= sendDef.MULTICAST_PORT_CM_TEST_BSE
		sendThreadCount 	= sendDef.CM_SEND_THREADS_TEST
	elif inputSegment == fyCmnDef.SEG_NAME_FO_TEST:
		listenPort			= bseConf.BSE_INP_PORT_TEST_FO
		priceConv 			= nseConf.PRICE_CONV_100
		roundoff			= 2
		multiSendPort 		= sendDef.MULTICAST_PORT_FO_TEST_BSE
		sendThreadCount 	= sendDef.FO_SEND_THREADS_TEST
	elif inputSegment == fyCmnDef.SEG_NAME_CD_TEST:
		listenPort			= bseConf.BSE_INP_PORT_TEST_CD
		priceConv 			= nseConf.PRICE_CONV_10000000
		roundoff			= 4
		multiSendPort 		= sendDef.MULTICAST_PORT_CD_TEST_BSE
		sendThreadCount 	= sendDef.CD_SEND_THREADS_TEST
	else:
		return {fyCmnDef.K_FUNCT_STAT:fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA:"", fyCmnDef.K_ERR_MSG: "%sInvalid segment:'%s' exchange:'%s'."%(fyCmnDef.ERROR_initNSEProcessing, inputSegment, inputExchange)}
	
	if listenPort == 0 or priceConv == 0 or roundoff == 0:
		return {fyCmnDef.K_FUNCT_STAT:fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA:"", fyCmnDef.K_ERR_MSG: "%sInvalid init parameters listenPort:%s, priceConv:%s, roundoff:%s for segment:'%s' exchange:'%s'."%(fyCmnDef.ERROR_initNSEProcessing, listenPort, priceConv, roundoff, inputSegment, inputExchange)}
	
	##New Code for time str - Palash // 2018-10-05
	timeStr = fyCmnDef.NSE_NEW_DAY_TIME
	##END

	priceConv 		= float(priceConv) ## Decimals. Just in case if the value is int 
	
	dateTimeNow 	= datetime.datetime.now()
	dateStr 		= dateTimeNow.strftime('%Y%m%d')
	
	packetInfoDict 	= {
						"priceConv"			:priceConv,
					} ## This dict will be sent to all the functions

	logFilePtr 			= None
	logErr_inst 		= fyCmnFunct.FYLog()
	fyTokenDict 		= {}
	tokenPrevValDict	= {} ## Dict containing token and previous day values. This will be used during premarket session. ## New addition Ajay 2018-04-05
	exceptTokenDict 	= {} ## These are the tokens which will be traded after market hours. ## New addition Ajay 2018-04-10
	tempDirectoryPath 	= ''
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
		fyCmnFunct.FYLog.changeLogFP(logFilePtr)
	
	if len(fyTokenDict) <= 0 or len(tempDirectoryPath) == 0:
		print "%sERROR init.."%(fyCmnDef.ERROR_initNSEProcessing)
		print "Program halted."
		sys.exit()
	
	logErr_inst.LogError(None, "Started for exchange %s and segment:%s listening to port %s"%(inputExchange, inputSegment,listenPort), printFlag=True)

	recv_sock = None
	try:
		recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
		recv_sock.bind(("", listenPort))
		recv_sock.setblocking(0)
		recv_sock.settimeout(fyDef.SOCK_RECV_TIMEOUT_SEC) ## Since socket receive is blocking we set timeout for the receive
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Socket connection failed. Except:%s"%(fyCmnDef.ERROR_initNSEProcessing, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag=True)
		print "Program halted."
		sys.exit()
	logErr_inst.LogError(None, "Socket connection successful", printFlag=True)

	redisRet = fyConn.connectRedis()
	if redisRet[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1 or redisRet[fyCmnDef.K_FUN_DATA] == []:
		logErr_inst.LogError(None, "%s Cannot create Radis connection. Error:%s"%(fyCmnDef.ERROR_initNSEProcessing, redisRet[fyCmnDef.K_ERR_MSG]), printFlag=True)
		print "Program halted."
		sys.exit()

	## ****** Multicast group send socket ## Ajay 2018-06-29 ******
	sendThEvent 	= threading.Event()
	sendThEvent.clear()
	try:
		sendPkt.SendPacket.listenEvent 		= sendThEvent
		sendPkt.SendPacket.thTimeout 		= sendDef.SEND_PACKET_TIMEOUT
		sendPkt.SendPacket.priceConv 		= priceConv
		sendPkt.SendPacket.sendPort 		= multiSendPort

		sendPkt.SendPacket.logErr_inst 		= logErr_inst ## For logs
		sendPkt.SendPacket.printFlag 		= debugDict["print"] ## For printing errors

	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Multicast socket connection failed. Except:%s"%(fyCmnDef.ERROR_initNSEProcessing, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag=True)
		sys.exit()
	logErr_inst.LogError(None, "Multicast group connection successful. sending IP: %s, port:%s"%(sendDef.MULTICAST_IP, multiSendPort), printFlag=True)

	sendPktQ = Queue.Queue(maxsize=sendDef.SEND_QUEUE_MAX_LEN) ## This queue is used to put the custom Fyers packet
	sendPkt.SendPacket.sendPktQ = sendPktQ
	sendPkt.SendPacket.inputExchange = inputExchange
	sendPkt.SendPacket.inputSegment = inputSegment
	sendThList = []
	if debugDict['nosend'] == False:
		for sendTh in range(0,sendThreadCount):
			sendPkt_inst = sendPkt.SendPacket()
			thSend = threading.Thread(name = 'sendThread%s'%(sendTh), target = sendPkt_inst.sendThread, args = (debugDict["print"], )) ## This thread is used to send the packets
			thSend.setDaemon(True) ## Daemon mode because once main thrad ends this thread will die 
			thSend.start()
			sendThList.append(thSend)
		logErr_inst.LogError(None, "Send threads created.", printFlag=True)
	## ****** END: Multicast group send socket ******

	print "Connecting to Redis............"
	radisConn = None
	## Commented for testing
	# radisConn = redisRet[fyCmnDef.K_FUN_DATA].pop()
	# redisStat = False
	# try:
	# 	redisStat = radisConn.set("testKey","test value", ex=10) ## This is needed to test the connection.
	# except Exception,e:
	# 	logErr_inst.LogError(None, "%s Redis status check failed. Error:%s"%(fyCmnDef.ERROR_initNSEProcessing, redisRet[fyCmnDef.K_ERR_MSG]), printFlag=True)
	# 	print "Program halted."
	# 	sys.exit()
	# if redisStat == False:
	# 	logErr_inst.LogError(None, "%s Redis set failed. Error:%s"%(fyCmnDef.ERROR_initNSEProcessing, redisRet[fyCmnDef.K_ERR_MSG]), printFlag=True)
	# 	print "Program halted."
	# 	sys.exit()
	# logErr_inst.LogError(None, "Connecting to cache success.", printFlag=True)

	timeStampNow = time.time()
	## Global variables init
	## Always starting with market status as on. So care should be taken when starting the program after market hours.
	## 2018-02-23: Lets start the global market sttatus as false and change when traing status changes in 7208. 
	## 2018-03-12 Global market status will be selected manually when we start the function. Initially global status are set to true and if the function is successful then the status is changed accordingly.
	SetGlobalVars.global_marketStat = True
	SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_NORMAL_OPEN ## This is used to set the min data candles. Ajay 2018-02-23 ## New change Ajay 2018-04-10
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
	devFlagAjay = False ## This is used for testing
	if inputSegment in [fyCmnDef.SEG_NAME_CM_TEST, fyCmnDef.SEG_NAME_FO_TEST, fyCmnDef.SEG_NAME_CD_TEST]:
		# global_marketStat = global_minSetFlag = False ## This is for testing comment it in **LIVE**
		SetGlobalVars.global_marketStat, SetGlobalVars.global_minSetFlag = True, fyCmnDef.MKT_F_NORMAL_OPEN
		# global_marketStat, global_minSetFlag = False, fyCmnDef.MKT_F_CLOSED
		print "*************************** Market stat manually changed comment line 817 in LIVE***************************"
		devFlagAjay = True


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
	# cacheFunct.SetValToMemc.setFlag = False ## This line is for testing and should be commented in ** LIVE **
	cacheSetThRT = threading.Thread(name = 'CacheThreadRT', target = setMemc_inst.setMemcThread, args = (cacheThEvent, fyMemC.TIMEOUT_MEMC_THREAD, devFlagAjay)) ## This thread is used to send the packets
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
	minSetThread = threading.Thread(name = "minSetCache", target = minSet_inst.minThreadFunct, args=(inputExchange, inputSegment, minEventTh, fyMemC.TIMEOUT_MIN_THREAD_MEMC, devFlagAjay))
	minSetThread.setDaemon(True) ## This one is to stop the thread when the program is started
	minSetThread.start()
	logErr_inst.LogError(None, "Cache Min thread created.", printFlag=True)
	## ********* End: Memcache min write thread *********

	## ********* Print packet count *********
	## This thread writes the packet count to the file and hence useful to track the packet parameters.
	countThread = threading.Thread(name = 'printThread', target = nse_init.printPacketCount, args=(logErr_inst, 5, inputExchange, inputSegment, setMemc_inst,debugDict["print"], debugDict['nowrite']))
	countThread.setDaemon(True)
	countThread.start()
	## ********* End: Print packet count *********

	## ********* Check the market status *********
	## This will check the market status every min 
	mktStatTh = threading.Thread(name = 'checkMarketStat', target = nse_init.th_marketStatCheck, args=(logErr_inst, inputExchange, inputSegment))
	mktStatTh.setDaemon(True)
	mktStatTh.start() ## This is comment for testing. Uncomment in **LIVE**
	# print "****************** mkt stat thread commented ******************"
	logErr_inst.LogError(None, "Market status check thread created.", printFlag=True)
	## ********* End:Check the market status *********

	## ********* New day check tread *********
	## The wait time is 600 sec it was made 6 sec for testing make it 600 for ** LIVE **
	newDayThread = threading.Thread(name = 'newDayThread', target = nse_init.checkNewDate, args=(logErr_inst, 600, inputExchange, SetGlobalVars, timeStr)) ## which will check for the new day trigger 
	newDayThread.setDaemon(True) ## Daemon mode because once main thrad ends this thread will die 
	newDayThread.start()
	## ********* End: New day check tread *********
	## **************************** End: Threads **************************** 

	headerCheck_Q 	= deque(maxlen = fyDef.LENGTH_UDPH_CHECK_BUF) ##This queue will contain checksum that are sent in the UDP-Header
	cacheConn 		= radisConn
	minValDict 		= {} ## This will contain current min values of all the tokens
	curMinValDict 	= {} ## Only current min val dict
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
							logErr_inst.LogError(None, "%s Line:%s. Failed to close previous day file. Except:%s"%(fyCmnDef.ERROR_initNSEProcessing, exc_tb.tb_lineno, str(e)), debugDict["print"])
						logFilePtr 			= newDayRet[fyCmnDef.K_FUN_DATA]["logFilePtr"]
						fyCmnFunct.FYLog.changeLogFP(logFilePtr)
						logErr_inst.LogError(None, "%s New day log file creation success."%(fyCmnDef.ERROR_initNSEProcessing), debugDict["print"])
					else:
						logErr_inst.LogError(None, "%s New day log file creation failed."%(fyCmnDef.ERROR_initNSEProcessing), debugDict["print"])
						
					if len(newDayRet[fyCmnDef.K_FUN_DATA]["fyTokenDict"]) > 100: ##There should atleast 100 tokens.
						## Change to flush old values - Palash
						del fyTokenDict
						fyTokenDict 		= {}
						## Test for mem
						fyTokenDict 		= newDayRet[fyCmnDef.K_FUN_DATA]["fyTokenDict"]
						logErr_inst.LogError(None, "%s New day fy tokens were loaded successfully. Length of dict:%s"%(fyCmnDef.ERROR_initNSEProcessing, len(fyTokenDict)), debugDict["print"])
					else:
						logErr_inst.LogError(None, "%s New day fy tokens were not loaded. Length of dict:%s"%(fyCmnDef.ERROR_initNSEProcessing, len(fyTokenDict)), debugDict["print"])

					if len(tempDirectoryPath) > 0:
						tempDirectoryPath 	= newDayRet[fyCmnDef.K_FUN_DATA]["tempDirectoryPath"]
						logErr_inst.LogError(None, "%s New day temp file changed successfully. Path:%s"%(fyCmnDef.ERROR_initNSEProcessing, tempDirectoryPath), debugDict["print"])
						cacheFunct.MinDataOperation.changeTempFPath(tempDirectoryPath)
					else:
						logErr_inst.LogError(None, "%s New day temp file failed."%(fyCmnDef.ERROR_initNSEProcessing), debugDict["print"])

					try:
						tokenPrevValDict	= newDayRet[fyCmnDef.K_FUN_DATA]["tokenPrevValDict"] ## new Ajay 2018-04-05
						exceptTokenDict		= newDayRet[fyCmnDef.K_FUN_DATA]["exceptTokenDict"] ## New Ajay 2018-04-10
						cacheFunct.MinDataOperation.changeExceptTokens(exceptTokenDict)## New Ajay 2018-04-19
					except Exception,e:
						exc_type, exc_obj, exc_tb = sys.exc_info()
						logErr_inst.LogError(None, "%s Line:%s. Previous and exception token load failed. Except:%s"%(fyCmnDef.ERROR_initNSEProcessing, exc_tb.tb_lineno, str(e)), debugDict["print"])

			recvData, recvAddr = recv_sock.recvfrom(1516) # buffer size is 1024 bytes ## 1050 is sent by RS and this is a constant.
			# print len(recvData), recvAddr
			# continue
			# print ' '.join(binascii.hexlify(recvData)[i:i+2] for i in xrange(0,len(binascii.hexlify(recvData)),2))
			(srcPort_UH, dstPort_UH, lenMsg_UH, check_UH) = nseConf.UDP_HEADER_STRUCT_P.unpack(recvData[nseConf.UDP_HEADER_OFFSET:nseConf.UDP_HEADER_OFFSET + nseConf.UDP_H_SIZE])
			# print srcPort_UH, dstPort_UH
			
			if listenPort != dstPort_UH:
				continue
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
			# print "len(recvData):",len(recvData)
			# print "len(recvData):",len(recvData)
			SetGlobalVars.global_rxPackets += 1
			recvData = recvData[nseConf.UDP_HEADER_OFFSET + nseConf.UDP_H_SIZE:] # UDP-Header is removed
			# sys.exit()
			if inputExchange == fyCmnDef.EXCHANGE_NAME_BSE:
				ret_bseFunct = bseFunct.processBSEPackets(logErr_inst, recvData, fyTokenDict, SetGlobalVars.global_FailedTokenDict, SetGlobalVars.global_tradingStat, packetInfoDict, debugDict["print"], debugDict["debugFlag"])
				# print "ret_bseFunct:", ret_bseFunct
				continue

			(cNetId_Recv,) = nseConf.NSE_CNET_ID_PACKET_STRUCT.unpack(recvData[:nseConf.NSE_CNET_ID_PACKET_SIZE])
			# print "cNetId_Recv:", cNetId_Recv
			if cNetId_Recv != expectedCnetId:
				logErr_inst.LogError(None, "%s cnet ID do not match. cNetId_Recv:%s, expectedCnetId:%s"%(fyCmnDef.ERROR_initNSEProcessing, cNetId_Recv, expectedCnetId), debugDict["print"])
				continue
			
			retValPacket = nsePktFunc.processNSEPacket(logErr_inst, recvData, fyTokenDict, packetInfoDict, SetGlobalVars.global_FailedTokenDict, SetGlobalVars.global_tradingStat, debugDict["print"], debugDict["debugFlag"])
			if retValPacket[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
				logErr_inst.LogError(None, retValPacket[fyCmnDef.K_ERR_MSG], debugDict["print"])
				continue
			else:
				for eachPacket in retValPacket[fyCmnDef.K_FUN_DATA]:
					# print "eachPacket:", eachPacket
					packetDict = retValPacket[fyCmnDef.K_FUN_DATA][eachPacket]
					if retValPacket[fyCmnDef.K_FUN_DATA][eachPacket][fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
						# print "packetDict:",packetDict
						logErr_inst.LogError(None, "Failed %s"%(fyCmnDef.ERROR_initNSEProcessing, str(packetDict), debugDict["print"]))

					# print "tcode:",packetDict["tcode"]
					SetGlobalVars.global_packetProcess += 1
					if packetDict["tcode"] == nseConf.NSE_T_CODE_7207:
						# None
						# for eachValue in packetDict[fyCmnDef.K_FUN_DATA]:
						# 	print eachValue,packetDict[fyCmnDef.K_FUN_DATA][eachValue]
						setToMemc(logErr_inst, inputExchange, inputSegment, roundoff, tempDirectoryPath, cacheConn, packetDict[fyCmnDef.K_FUN_DATA], cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, sendThEvent, sendPktQ, printFlag = debugDict["print"], debugFlag = debugDict["debugFlag"], nocache = debugDict["nocache"], develFlag = debugDict["develFlag"], nosend = debugDict['nosend']) ## commented for testing on 2018-01-16
					# elif packetDict["tcode"] == nseConf.NSE_T_CODE_7216: ## Not tested yet 
					# 	setToMemc(logErr_inst, inputExchange, inputSegment, roundoff, tempDirectoryPath, cacheConn, packetDict[fyCmnDef.K_FUN_DATA], cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, printFlag = debugDict["print"], debugFlag = debugDict["debugFlag"], nocache = debugDict["nocache"], develFlag = debugDict["develFlag"]) ## new addition Ajay 2018-03-16
					elif packetDict["tcode"] == nseConf.NSE_T_CODE_7208:
						SetGlobalVars.global_7208Count += 1
						# for eachToken in packetDict[fyCmnDef.K_FUN_DATA]:
						# 	print eachToken, packetDict[fyCmnDef.K_FUN_DATA][eachToken]
						setToMemc(logErr_inst, inputExchange, inputSegment, roundoff, tempDirectoryPath, cacheConn, packetDict[fyCmnDef.K_FUN_DATA], cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, sendThEvent, sendPktQ, printFlag = debugDict["print"], debugFlag = debugDict["debugFlag"], nocache = debugDict["nocache"], develFlag = debugDict["develFlag"], nosend = debugDict['nosend']) ## commented for testing on 

					elif packetDict["tcode"] in nseConf.NSE_STAT_TCODE_LIST:
						# print packetDict["tcode"], "packetDict:",packetDict
						## Instead of setting the market status on transaction codes we can set it on trading status sent in 7208 which can haandle pre-market and after-market data also.

						# print "packetDict[tcode]", packetDict["tcode"]
						if packetDict["tcode"] == 6511 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
							## BC_OPEN_MESSAGE (6511). This is sent when the market is opened.
							SetGlobalVars.global_marketStat = True
							SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_NORMAL_OPEN ## New change Ajay 2018-04-10 
							logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s"%(fyCmnDef.ERROR_initNSEProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511]))
						elif packetDict["tcode"] == 6521 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
							## BC_CLOSE_MESSAGE (6521). This is sent when the market is closed.
							SetGlobalVars.global_marketStat = False
							SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_CLOSED ## New change Ajay 2018-04-10
							logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s"%(fyCmnDef.ERROR_initNSEProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511]))
						elif   packetDict["tcode"] == 6531 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
							## BC_PREOPEN_SHUTDOWN_MSG (6531). This is sent when the market is preopened.
							SetGlobalVars.global_tradingStat = 1 ## Added by Ajay 2018-03-19 ## 1 is for preopen
							SetGlobalVars.global_marketStat = False
							SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_PREOP ## New change Ajay 2018-04-10
							logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s, global_tradingStat:%s"%(fyCmnDef.ERROR_initNSEProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511], SetGlobalVars.global_tradingStat))
						elif   packetDict["tcode"] == 6571 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
							SetGlobalVars.global_marketStat = False
							SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_CLOSED
							logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s, global_tradingStat:%s"%(fyCmnDef.ERROR_initNSEProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511], SetGlobalVars.global_tradingStat))
						elif packetDict["tcode"] == 6583 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
							## BC_CLOSING_START(6583). This is sent when closing session is opened.
							SetGlobalVars.global_marketStat = False
							SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_CLOSED ## New change Ajay 2018-04-10
							logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s"%(fyCmnDef.ERROR_initNSEProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511]))
						elif packetDict["tcode"] == 6584 and packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511] == 1:
							SetGlobalVars.global_marketStat = False #True ## This was changed to False on 2018-02-21 by Ajay. Sice we are updating min candles and we shouldnot update those after the market closing session has been closed.
							SetGlobalVars.global_minSetFlag = fyCmnDef.MKT_F_CLOSED ## New change Ajay 2018-04-10
							logErr_inst.LogError(None, "%s global_marketStat:%s for Tcode:%s, market type:%s"%(fyCmnDef.ERROR_initNSEProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511]))
						else:
							logErr_inst.LogError(None, "%s No action global_marketStat:%s for Tcode:%s, market type:%s"%(fyCmnDef.ERROR_initNSEProcessing, SetGlobalVars.global_marketStat, packetDict["tcode"], packetDict[fyCmnDef.K_FUN_DATA][fyCmnDef.K_MKT_TYPE_6511]))

						# cacheFunct.MinDataOperation.changeSetFlag(global_minSetFlag) ## When the market closes we should stop updating the min values ## Commented by Ajay 2018-03-12. The min data itself wont be sent to the thread instead of stopping te thread to set.
					else:
						## We dont need other transaction codes
						None

		except socket.timeout: ## This is normal error 
			# print "sock Timeout"
			continue
		except Exception,e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			logErr_inst.LogError(None, "%s Line:%s. Receive failed. Except:%s"%(fyCmnDef.ERROR_initNSEProcessing, exc_tb.tb_lineno, str(e)), debugDict["print"])
			
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
	if len(inputSegment) <= 0:
		print "******************************"
		print "ERR : Please specify the valid segment"
		print "******************************"
		nseParser.print_help()
		sys.exit(2)
	if inputExchange == fyCmnDef.EXCHANGE_NAME_NSE:
		if inputSegment not in [fyCmnDef.SEG_NAME_CM_LIVE, fyCmnDef.SEG_NAME_FO_LIVE, fyCmnDef.SEG_NAME_CD_LIVE, fyCmnDef.SEG_NAME_CM_TEST, fyCmnDef.SEG_NAME_FO_TEST, fyCmnDef.SEG_NAME_CD_TEST]:
			print "******************************"
			print "ERR : Invalid segment:'%s' for the exchange %s"%(inputSegment, inputExchange)
			print "******************************"
			nseParser.print_help()
			sys.exit(2)

		debugDict = {
						"sendOption"	: nseArgs.sendOption, 
						"pdb"			: nseArgs.pdbFlag, 
						"print"			: nseArgs.printFlag, 
						"debugFlag"		: nseArgs.debugFlag,
						"nocache"		: nseArgs.nocache,
						"develFlag"		: nseArgs.develFlag,
						"nowrite"       : nseArgs.nowrite,
						"nosend"        : nseArgs.nosend
					}
		# returninitNSE = initNSEProcessing(inputExchange, inputSegment, debugDict = debugDict)
		# if returninitNSE[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
		# 	print returninitNSE[fyCmnDef.K_ERR_MSG]
		# 	nseParser.print_help()
		# 	sys.exit(2)

	elif inputExchange == fyCmnDef.EXCHANGE_NAME_BSE:
		if inputSegment not in [fyCmnDef.SEG_NAME_CM_LIVE, fyCmnDef.SEG_NAME_FO_LIVE, fyCmnDef.SEG_NAME_CD_LIVE, fyCmnDef.SEG_NAME_CM_TEST, fyCmnDef.SEG_NAME_FO_TEST, fyCmnDef.SEG_NAME_CD_TEST]:
			print "******************************"
			print "ERR : Invalid segment:'%s' for the exchange %s"%(inputSegment, inputExchange)
			print "******************************"
			nseParser.print_help()
			sys.exit(2)

		debugDict = {
						"sendOption"	: nseArgs.sendOption, 
						"pdb"			: nseArgs.pdbFlag, 
						"print"			: nseArgs.printFlag, 
						"debugFlag"		: nseArgs.debugFlag,
						"nocache"		: nseArgs.nocache,
						"develFlag"		: nseArgs.develFlag,
						"nowrite"       : nseArgs.nowrite,
						"nosend"        : nseArgs.nosend
					}
		returninitNSE = initBSEProcessing(inputExchange, inputSegment, debugDict = debugDict)
		if returninitNSE[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
			print returninitNSE[fyCmnDef.K_ERR_MSG]
			nseParser.print_help()
			sys.exit(2)
	else:
		print "******************************"
		print "Invalid Exchange %s"%(inputExchange) 
		print "******************************"
		nseParser.print_help()
		sys.exit(2)

if __name__ == "__main__":
	main()