"""
Author 		: Ajay A U [ajay@fyers.in]
Version 	: 2.1
Copyright 	: Fyers Securities
Web			: fyers.in
"""

import sys
sys.path.append('c:/python27/lib/site-packages') ##Comment in live
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
import pdb

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

import fy_BSE_config as bseConf
import fy_BSE_packetFunct as bseFunct

def printPacketCount(logErr_inst, intervalSeconds, inputExchange, inputSegment, setCache_inst, printFlag = False, nowrite = False):
	"""
	[Function]  : 	This is a thread that prints number of packets sent/received/totalPackets for a perticular durations.
	
	[Input] 	: 	intervalSeconds -> Interval for the prints
					inputSegment 	-> CM/FO/CD 
					setCache_inst 	-> This is the get the number of sets to cache.
					printFlag		-> True/False = print/no_Print
	[Output]	: 	None.
	"""
	# global global_marketStat, global_rxPackets, global_packetProcess, global_7208Count, global_tradingStat, global_minSetFlag, global_rejected
	try:
		count 		= 0
		procCount 	= 0
		setMC_Count = 0
		prev7208Cnt = 0
		rejected 	= 0
		sentCount   = 0 # stream 20181031 - Palash
		inputExchange, inputSegment = inputExchange.upper(), inputSegment.upper() 
		#New change for mcx 20181019 - Palash
		if   inputExchange == fyCmnDef.EXCHANGE_NAME_NSE:
			countDirPath 	= fyCmnDef.LOG_FILE_PATH_EC2_RS_NSE + inputSegment + '/' + "packetCounRT"
		elif inputExchange == mcx_conf.MCX_EXCHANGE_NAME:
			countDirPath 	= fyCmnDef.LOG_FILE_PATH_EC2_RS_MCX + inputSegment + '/' + "packetCounRT"
		elif inputExchange == fyCmnDef.EXCHANGE_NAME_BSE:
			countDirPath 	= fyCmnDef.LOG_FILE_PATH_EC2_RS_BSE + inputSegment + '/' + "packetCounRT"
		else:
			errMsg = "%s Invalid exchange:'%s'"%(fyCmnDef.ERROR_printPacketCount, inputExchange)
			logErr_inst.LogError(None, errMsg, printFlag)
			countDirPath 	= ""
		# print "countDirPath:", countDirPath
		
		countFP = None
		try:
			countFP = open(countDirPath + fyCmnDef.LOG_FILE_EXT, "w+", buffering = 0)
		except Exception,e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			errMsg = "%s Line:%s. Opening file exception:%s"%(fyCmnDef.ERROR_printPacketCount, exc_tb.tb_lineno, str(e))
			logErr_inst.LogError(None, errMsg, printFlag)
			countFP = None

		while True:
			try:
				time.sleep(intervalSeconds)
				timeStruct = time.localtime(time.time())
				setCntRet = setCache_inst.getSetCount()
				rxDelta = (SetGlobalVars.global_rxPackets-count)
				if rxDelta < 0: rxDelta = 0
				procDelta = (SetGlobalVars.global_packetProcess - procCount)
				if procDelta < 0: procDelta = 0
				setDelta = (setCntRet - setMC_Count)
				if setDelta < 0: setDelta = 0
				delta7208 = (SetGlobalVars.global_7208Count - prev7208Cnt)
				if delta7208 < 0: delta7208 = 0
				deltaRejct = SetGlobalVars.global_rejected - rejected ## New Ajay 2018-06-01
				if deltaRejct < 0: deltaRejct = 0
				deltaSent = sendPkt.SendPacket.sentCount - sentCount ## stream 20181031 - Palash
				if deltaSent < 0: deltaSent = 0

				##New change MCX 20181019 - Palash
				excTimeStr = ''
				if   inputExchange == fyCmnDef.EXCHANGE_NAME_NSE:
					excTimeStr = "NSE_TIME:%10s"%(SetGlobalVars.global_TS_NSE)
				elif inputExchange == mcx_conf.MCX_EXCHANGE_NAME:
					excTimeStr = "MCX_TIME:%10s"%(SetGlobalVars.global_TS_NSE)
				elif inputExchange == fyCmnDef.EXCHANGE_NAME_BSE:
					excTimeStr = "BSE_TIME:%10s"%(SetGlobalVars.global_TS_NSE)
				else:
					excTimeStr = "Invalid exchange %s"%(inputExchange)
				countStr = "%2s:%2s:%2s-> mkt:%5s minF:%s mkt_Stat:%s, rx:%4d, proc:%4s, set:%4s, data_pkt:%4s, rej:%4s, sent:%4s, Total:%8s, %s"%(timeStruct.tm_hour, timeStruct.tm_min, timeStruct.tm_sec, SetGlobalVars.global_marketStat, SetGlobalVars.global_minSetFlag, SetGlobalVars.global_tradingStat, rxDelta, procDelta, setDelta, delta7208, deltaRejct, deltaSent, SetGlobalVars.global_rxPackets, excTimeStr)
				##END
				# if nowrite == False:
				if countFP != None:
					countFP.seek(0, 0)
					countFP.write(countStr)
				if printFlag == True:
					print countStr
				# logErr_inst.LogError(countFP, countStr, printFlag)

				procCount 	= SetGlobalVars.global_packetProcess
				count 		= SetGlobalVars.global_rxPackets
				setMC_Count = setCntRet
				prev7208Cnt = SetGlobalVars.global_7208Count
				rejected 	= SetGlobalVars.global_rejected ## New Ajay 2018-06-01
				sentCount 	= sendPkt.SendPacket.sentCount # New Stream 20181031 - Palash
			except Exception,e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				errMsg = "%s Line:%s. Loop except:%s"%(fyCmnDef.ERROR_printPacketCount, exc_tb.tb_lineno, str(e))
				logErr_inst.LogError(None, errMsg, printFlag)
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Exception: %s"%(fyCmnDef.ERROR_printPacketCount, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag)
	try:
		countFP.close()
	except:
		None

def setMsgToCache(logErr_inst, SetGlobalVars, inputExchange, inputSegment, inputDict, timeStamp, cacheConn, exMsgDirPath, printFlag):
	try:
		retFyCodes = fyCmnFunct.getExSegCodeFromName(inputExchange, inputSegment)
		if retFyCodes[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
			return retFyCodes
		if fyCmnDef.K_FUN_DATA not in retFyCodes:
			returnDict[fyCmnDef.K_ERR_MSG] = "%s 1.Inconsisty finding exchange segment code."%(fyCmnDef.ERROR_newDayTrigger)
			return returnDict
		if inputExchange not in retFyCodes[fyCmnDef.K_FUN_DATA] or inputSegment not in retFyCodes[fyCmnDef.K_FUN_DATA]:
			returnDict[fyCmnDef.K_ERR_MSG] = "%s 2.Inconsisty finding exchange segment code."%(fyCmnDef.ERROR_newDayTrigger)
			return returnDict
		
		ex_code, seg_code = retFyCodes[fyCmnDef.K_FUN_DATA][inputExchange], retFyCodes[fyCmnDef.K_FUN_DATA][inputSegment]
		#print("timeStamp fy_util--> ", timeStamp)
		todayStartTS	= timeStamp - (timeStamp % 86400)
		curMinTS 		= timeStamp - (timeStamp % 60)
		memTokenKey = "%s-%s-%s-%s"%(str(ex_code), str(seg_code), str(fyMemC.K_FY_MSG_TOKEN), todayStartTS)
		dataDict = {str(curMinTS): inputDict['msg']}
		fileName 	= exMsgDirPath + '/' +str(memTokenKey) + ".json"
		msgDict = {}
		if os.path.exists(fileName) == True:
			try:
				dataFP = None
				with open(fileName, "r+") as dataFP:
					fileDataTV = dataFP.read()
					if len(fileDataTV) > 0:
						print("163 msgDict--> ", msgDict)
						msgDict = json.loads(fileDataTV)
						# if debugFlag == fyCmnDef.DEBUG_TIME: ## To Debug
						# 	print "1.2:",time.time() - pointA
					else:
						msgDict = {} ## Empty file
			except Exception,e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				logErr_inst.LogError(None, "%s Line:%s. Exception for token: while getting from file system. Except:%s"%(fyCmnDef.ERROR_setMsgToCache, exc_tb.tb_lineno, str(e)), printFlag)
			finally:
				if dataFP != None:
					dataFP.close()
		# else:
		try:
			wp = None
			flag = 0
			with open(fileName, 'w+', buffering=0) as wp:
				if len(msgDict) <= 0:
					msgDict = {memTokenKey: []}
				if memTokenKey in msgDict:
					if dataDict not in msgDict[memTokenKey]:
						msgDict[memTokenKey].append(dataDict) 
						flag = 1
					print("Write is happening 189 fy_util")
					wp.write(json.dumps(msgDict))
			if flag == 1:
				#print("dataDict--> 188 ", dataDict)
				cacheConn.rpush(memTokenKey, json.dumps(dataDict))
				cacheConn.expire(memTokenKey, fyCmnDef.REDIS_EXPIRE_TIME)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			logErr_inst.LogError(None, "%s Line:%s. Exception for token: while getting from file system. Except:%s"%(fyCmnDef.ERROR_setMsgToCache, exc_tb.tb_lineno, str(e)), printFlag)
		finally:
			if wp != None:
				wp.close()
		logErr_inst.LogError(None, "%s - %s - %s"%(timeStamp, memTokenKey, inputDict['msg']), printFlag=False)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logErr_inst.LogError(None, "%s Line:%s. Unknow exception. Except:%s"%(fyCmnDef.ERROR_setMsgToCache, exc_tb.tb_lineno, str(e)), printFlag)

def checkNewDate(logErr_inst, waitTime, inputExchange, SetGlobalVars, exTime, debugFlag = False):
	"""
	[Function] 	: 	Thread.
					Check for new day after given number of seconds. 
	[Input]		: 	waitTime 		-> Number of seconds before it has to chaeck fo new day.
				  	inputSegment 	-> CM/FO/CD
	[Output]	: 	None
	"""
	# global global_newDayFlag
	try:
		# dateToday = datetime.datetime.now() - datetime.timedelta(days=3)
		dateNextday = datetime.datetime.now()
		newDayTime = exTime.time()
		if inputExchange == fyCmnDef.EXCHANGE_NAME_NSE:
			triggerTs = dateNextday.replace(hour=newDayTime.hour,minute=newDayTime.minute,second=newDayTime.second,microsecond=newDayTime.microsecond)
		elif inputExchange == mcx_conf.MCX_EXCHANGE_NAME: ## Add for mcx
			triggerTs = dateNextday.replace(hour=newDayTime.hour,minute=newDayTime.minute,second=newDayTime.second,microsecond=newDayTime.microsecond)
		elif inputExchange == fyCmnDef.EXCHANGE_NAME_BSE: ## BSE
			triggerTs = dateNextday.replace(hour=newDayTime.hour,minute=newDayTime.minute,second=newDayTime.second,microsecond=newDayTime.microsecond)
		else:
			return {fyCmnDef.K_FUNCT_STAT:fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA:"", fyCmnDef.K_ERR_MSG: "%sInvalid exchange:'%s'."%(fyCmnDef.ERROR_initExcProcessing, inputExchange)}
		# counter = 0
		if dateNextday > triggerTs:
			triggerTs = triggerTs + datetime.timedelta(days=1)
		while True:
			try:
				if debugFlag:
					# counter += 10
					print "Sleeping for %s Sec"%(waitTime)
					# dateDiff = datetime.timedelta(days = 1) ## Added for testing comment in ** LIVE **
					# newDayFile = open("./"+str(inputSegment)+"newDay.txt", "ab+", buffering = 0)## Added for testing comment in ** LIVE **
					# dateToday = dateToday + datetime.timedelta(days=int(counter/10))
				time.sleep(waitTime)
				# if counter == 10:
				# 	break
				# dateToday = dateToday + dateDiff ## Added for testing comment in ** LIVE **			
				# if counter % 10 == 0:
				if datetime.datetime.now() > triggerTs:
					if SetGlobalVars.global_newDayFlag == 0:
						SetGlobalVars.global_newDayFlag = 1
						# print "New Day"
						logErr_inst.LogError(None, "New day triggered", printFlag=True)## Added for testing comment in ** LIVE **
					triggerTs = triggerTs + datetime.timedelta(days=1)
					# print triggerTs
			except Exception as e:
				logErr_inst.LogError(None,"ERR : checkNewDate()-> Exception %s Line: %s"%(e, exc_tb.tb_lineno), printFlag=False)
		# newDayFile.close()## Added for testing comment in ** LIVE **
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logErr_inst.LogError(None,"ERR : checkNewDate()-> Exception %s Line: %s"%(e, exc_tb.tb_lineno), printFlag=False)

def th_marketStatCheck(logErr_inst, inputExchange, inputSegment):
	"""
	[Function] 	: 	Thread.
					Start at the begining of the min.
					Check if the market status every min and if the global status has not changed by the exchange. change the status manually.
	[Input]		: 	inputExchange 	-> NSE
				  	inputSegment 	-> CM/FO/CD
	[Output]	: 	None
	"""
	# global global_TS_NSE, global_marketStat, global_minSetFlag, global_checkMktStat
	
	try:
		## Waits for the start of next min. If we start with random number of seconds then there may be a possibility that we may check market status with random number of seconds like 03:30:40 HH:MM:SS within that time the close price for script have been updated and the change and percentage change will become zero.
		countLoop = 0
		while SetGlobalVars.global_TS_NSE == 0:
			countLoop += 1
			# print "%s sleeping"%(fyCmnDef.ERROR_th_marketStatCheck) ## Debug
			time.sleep(1)
			if countLoop >= 60:
				break

		# print "%s sleeping for %s sec"%(fyCmnDef.ERROR_th_marketStatCheck, int(time.time())% 60)## Debug
		time.sleep(int(time.time())% 60) ## Ensure begining of the min.
		while True:
			# print "%s Loop"%(fyCmnDef.ERROR_th_marketStatCheck) ## Debug
			# logErr_inst.LogError(None, "%s:Test"%(fyCmnDef.ERROR_th_marketStatCheck), printFlag=True) ## Debug
			try:
				timeNow = time.time()
				if SetGlobalVars.global_TS_NSE > 0:
					timeNow = SetGlobalVars.global_TS_NSE
				# print "wait for %s sec"%(60 - (timeNow%60))
				retCheckMktStat = fyCmnFunct.checkMktHours(inputExchange, inputSegment, timeNow)
				if retCheckMktStat[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
					logErr_inst.LogError(None, "%s Unable to verify market open status. Error:%s"%(fyCmnDef.ERROR_th_marketStatCheck, retCheckMktStat[fyCmnDef.K_ERR_MSG]), printFlag=True)
				else:
					if SetGlobalVars.global_minSetFlag != retCheckMktStat[fyCmnDef.K_FUN_DATA]: ## New change ajay 2019-04-10
						if retCheckMktStat[fyCmnDef.K_FUN_DATA] == fyCmnDef.MKT_F_PARTIAL: ## New addition ajay 2019-04-10
							SetGlobalVars.global_minSetFlag = retCheckMktStat[fyCmnDef.K_FUN_DATA] ## If the market is partially trading we change status without wait
							logErr_inst.LogError(None, "%s Market stat changed for partial for first attempt :%s"%(fyCmnDef.ERROR_th_marketStatCheck, SetGlobalVars.global_minSetFlag), printFlag=True)
						time.sleep(2) ## This is done to insure that we are waiting for market close status from the exchange NSE.
						## This entire code below is to make sure we do not change the market status manually even if we get the market status by the exchange NSE.
						if SetGlobalVars.global_TS_NSE > 0:
							timeNow = SetGlobalVars.global_TS_NSE
						retCheckMktStat2 = fyCmnFunct.checkMktHours(inputExchange, inputSegment, timeNow)
						if retCheckMktStat2[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
							logErr_inst.LogError(None, "%s Unable to verify market open status for the second attempt. Error:%s"%(fyCmnDef.ERROR_th_marketStatCheck, retCheckMktStat2[fyCmnDef.K_ERR_MSG]), printFlag=True)
						else:
							if SetGlobalVars.global_minSetFlag != retCheckMktStat2[fyCmnDef.K_FUN_DATA]: ## New change ajay 2019-04-10
								SetGlobalVars.global_minSetFlag = retCheckMktStat2[fyCmnDef.K_FUN_DATA] ## This is the statement which changes the status.## New change ajay 2019-04-10
								if SetGlobalVars.global_minSetFlag in [fyCmnDef.MKT_F_NORMAL_OPEN, fyCmnDef.MKT_F_PARTIAL]: ## New change ajay 2019-04-10
									SetGlobalVars.global_marketStat = True
								else:
									SetGlobalVars.global_marketStat = False
								logErr_inst.LogError(None, "%s Market status is %s. Message:%s. Changed manually for the second attempt."%(fyCmnDef.ERROR_th_marketStatCheck, retCheckMktStat2[fyCmnDef.K_FUN_DATA], retCheckMktStat2[fyCmnDef.K_ERR_MSG]), printFlag = True)
			except Exception,e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				errMsg = "%s Line:%s. Unknow exception. Except:%s"%(fyCmnDef.ERROR_th_marketStatCheck, exc_tb.tb_lineno, str(e))
				logErr_inst.LogError(None, errMsg, printFlag = True)
			finally:
				#change to wait for one min after the exception time is set 2018-10-30 - Palash
				time.sleep(60 - (timeNow%60)) ## Change Ajay 2018-04-13 wait exact 1 min
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Unknow exception. Except:%s"%(fyCmnDef.ERROR_th_marketStatCheck, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag = True)

def getPrevMinVal(logErr_inst, inputVal, memcTVKey, printFlag = False):
	"""
	[Function]  : 	This Function will take the values that will be stored in a file or the values that we get from cache and select last updated value for the timestamp and corrosponding OHLCV values.
	
	[Input] 	: 	logErr_inst		-> The instance of log_error which will log errors.
					inputVal	 	-> The value that will be read from file system or the cache.
					memcTVKey		-> This is the key of the token.
					printFlag		-> True/False = print/no_Print
	[Output]	: 	Dict 
					{fyCmnDef.K_FUNCT_STAT: fyCmnDef.V_FUNCT_SUCCESS_1, fyCmnDef.K_FUN_DATA: tokenMinDict, fyCmnDef.K_ERR_MSG: ""}
					fyCmnDef.K_FUNCT_STAT	-> fyCmnDef.V_FUNCT_SUCCESS_1/fyCmnDef.V_FUNCT_FAIL_N_1
					fyCmnDef.K_FUN_DATA 	-> Contain the data on success.
					fyCmnDef.K_ERR_MSG 		-> Error messages in case function failed.
	"""
	try:
 		#print("inputVal--> ", inputVal)
# 		print("memcTVKey--> ", memcTVKey)
# 		'inputVal--> ', '{"fp": 737650000, "201": 1608528414, "202": 7202, "ft": "10128001011487-2005-1608508800", "fv": 13, "dhi": 4910452, "dlo": 4867415, "43": 1, "34": 2, "oi": 4903203}')
# ('memcTVKey--> ', '10128001011487-2005-1608508800')

		tokenMinDict = {}
		if not isinstance(inputVal, dict):
			inputVal = json.loads(inputVal)
		inputJSKeys 	= inputVal.keys()

		if fyMemC.K_MEMC_TV_OPEN in inputJSKeys and fyMemC.K_MEMC_TV_HIGH in inputJSKeys and fyMemC.K_MEMC_TV_LOW in inputJSKeys and fyMemC.K_MEMC_TV_CLOSE in inputJSKeys and fyMemC.K_MEMC_TV_VOL in inputJSKeys and fyMemC.K_MEMC_TV_TIME in inputJSKeys and fyMemC.K_MEMC_FY_DAY_H in inputJSKeys and fyMemC.K_MEMC_FY_DAY_L in inputJSKeys and fyMemC.K_MEMC_FY_VTT in inputJSKeys:
			if len(inputVal[fyMemC.K_MEMC_TV_TIME]) > 0:
				# print "getting data from file"
				tokenMinDict = {
								fyMemC.K_MEMC_TV_TIME	: inputVal[fyMemC.K_MEMC_TV_TIME][-1], 
								fyMemC.K_MEMC_TV_OPEN	: inputVal[fyMemC.K_MEMC_TV_OPEN][-1],
								fyMemC.K_MEMC_TV_HIGH	: inputVal[fyMemC.K_MEMC_TV_HIGH][-1],
								fyMemC.K_MEMC_TV_LOW	: inputVal[fyMemC.K_MEMC_TV_LOW][-1],
								fyMemC.K_MEMC_TV_CLOSE	: inputVal[fyMemC.K_MEMC_TV_CLOSE][-1],
								fyMemC.K_MEMC_FY_DAY_H	: inputVal[fyMemC.K_MEMC_FY_DAY_H],
								fyMemC.K_MEMC_FY_DAY_L	: inputVal[fyMemC.K_MEMC_FY_DAY_L],
								fyMemC.K_MEMC_TV_VOL	: inputVal[fyMemC.K_MEMC_TV_VOL][-1],
								fyMemC.K_MEMC_FY_VTT	: inputVal[fyMemC.K_MEMC_FY_VTT],
								fyMemC.K_MEMC_FY_TOKEN	: memcTVKey,
								fyCmnDef.K_BCH_TS	: inputVal[fyCmnDef.K_BCH_TS]
								}
				return {fyCmnDef.K_FUNCT_STAT: fyCmnDef.V_FUNCT_SUCCESS_1, fyCmnDef.K_FUN_DATA: tokenMinDict, fyCmnDef.K_ERR_MSG: ""}
		#pdb.set_trace()
		if fyMemC.K_MEMC_OI_TOKEN in inputJSKeys and fyMemC.K_MEMC_OI_FILLP in inputJSKeys and fyMemC.K_MEMC_OI_FILLVOL in inputJSKeys and fyMemC.K_MEMC_OI in inputJSKeys and fyMemC.K_MEMC_OI_DAYHI in inputJSKeys and fyMemC.K_MEMC_OI_DAYLO in inputJSKeys:
			# print "getting data from file"
			#('inputVal--> ', '{"fp": 737650000, "201": 1608528414, "202": 7202, "ft": "10128001011487-2005-1608508800", "fv": 13, "dhi": 4910452, "dlo": 4867415, "43": 1, "34": 2, "oi": 4903203}')
			tokenMinDict = {
							# fyMemC.K_MEMC_OI_Change : inputDict[fyMemC.K_MEMC_OI_Change],
							fyMemC.K_MEMC_OI_TOKEN  : memcTVKey,
							fyMemC.K_MEMC_OI_FILLP  : inputVal[fyMemC.K_MEMC_OI_FILLP],
							fyMemC.K_MEMC_OI_FILLVOL: inputVal[fyMemC.K_MEMC_OI_FILLVOL],
							fyMemC.K_MEMC_OI  		: inputVal[fyMemC.K_MEMC_OI],
							fyMemC.K_MEMC_OI_DAYHI  : inputVal[fyMemC.K_MEMC_OI_DAYHI],
							fyMemC.K_MEMC_OI_DAYLO  : inputVal[fyMemC.K_MEMC_OI_DAYLO],
							fyMemC.K_MEMC_OI_DAYLO  : inputVal[fyMemC.K_MEMC_OI_DAYLO],
							# fyMemC.K_MEMC_LTQ  		: inputVal[fyMemC.K_MEMC_LTQ]
							}
			return {fyCmnDef.K_FUNCT_STAT: fyCmnDef.V_FUNCT_SUCCESS_1, fyCmnDef.K_FUN_DATA: tokenMinDict, fyCmnDef.K_ERR_MSG: ""}


		else:
			return {fyCmnDef.K_FUNCT_STAT: fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA: tokenMinDict, fyCmnDef.K_ERR_MSG: "%s Improper data found."%(fyCmnDef.ERROR_getPrevMinVal)}
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. JSON loads exception for token:%s. Except:%s"%(fyCmnDef.ERROR_getPrevMinVal, exc_tb.tb_lineno, eachToken, str(e))
		# logErr_inst.LogError(None, errMsg, printFlag)
		return {fyCmnDef.K_FUNCT_STAT: fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA: {}, fyCmnDef.K_ERR_MSG: errMsg}
	return {fyCmnDef.K_FUNCT_STAT: fyCmnDef.V_FUNCT_FAIL_N_1, fyCmnDef.K_FUN_DATA: {}, fyCmnDef.K_ERR_MSG: "%s Unknown."%(fyCmnDef.ERROR_getPrevMinVal)}

def setToMemc(logErr_inst, inputExchange, inputSegment, roundoff, tempDirectoryPath, cacheConn, inputDict, cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, sendThEvent, sendPktQ, printFlag = False, debugFlag = False, nocache = False, develFlag = False, noSend = False):
	"""
	[Function]  : 	This function does the following
					1. Update the global variable which will contain timestamp that is sent by NSE.
					2. Check for the change in trading status that will be sent with 7208 packet.
					3. If its a new minute then push the previous min data to queue(minQueue) that will set one min candles and clear the the data from the dict(curMinValDict).
					4. Try to get the the previous data if the data is not already there in the program memory(minValDict).  
					5. For each input packets received ie., for each input token calculate the OHLCV for the min depending on the day_high, day_low and vlume traded today.
					6. Update the calculated OHLCV to the current min dict(curMinValDict) and the dict that will contain all the data(minValDict)
					7. Update the realtime dict and put it into the queue(cacheQueue) which will update real-time data.
	
	[Input] 	: 	logErr_inst		-> The instance of log_error which will log errors.
					inputExchange 	-> NSE
				  	inputSegment 	-> CM/FO/CD
					roundoff 		-> Number of decimal points for calculations.
					tempDirectoryPath-> This is the file path in which temp files will be written into.
					cacheConn 		-> Contain the cache connection.
					inputDict 		-> This dictionary contain the processed data which is sent by NSE. Key inthe dict will be token_number.
					cacheQueue		-> The queue in which real time update dict has to pushed.
					minQueue		-> The queue in which min dict has to be pushed.
					minValDict 		-> The dict which will contain all keys will be tokens those are received from NSE and the corrosponding OHLCV, day_high, day_low etc.. as values.
					curMinValDict 	-> Same as minValDict but contain data only current min. 
					minEventTh 		-> To indicate the min thread to start setting the min data for the previous min when the new min starts. 
					printFlag		-> True/False = print/no_Print.
					debugFlag 		-> Contain the information that can used for debugging.
					nocache 		-> True/False used for debugging when set to True it will not take values from cache.
	[Output]	: 	None.
	"""
	# global global_marketStat, global_timeStamp, global_TS_NSE, global_tradingStat, global_minSetFlag, global_rejected
	try:
		# print "set to memc called"
		for eachToken in inputDict:
			# if eachToken == 12100000001:
			# 	print "%s: ltp:%s"%(eachToken, inputDict[eachToken][fyCmnDef.K_LTP])

			pointA = time.time()
			if debugFlag == fyCmnDef.DEBUG_TEST:
				None
				# inputDict[eachToken][K_BCH_TS] = pointA - (pointA % 60) ## This is done only for testing purpose
			## This is only to track the change in the trading status
			# print "eachToken:", eachToken
			if inputDict[eachToken][fyCmnDef.K_BCH_PACKT_CODE] == nseConf.NSE_T_CODE_7208:
				## This is needed because to process 7207 we will be sending global_tradingStat 
				if SetGlobalVars.global_tradingStat != inputDict[eachToken][fyCmnDef.K_TRADIN_STAT]:
					logErr_inst.LogError(None, "%s token:%s global_tradingStat:%s, changed_Stat:%s"%(fyCmnDef.ERROR_setToMemc, eachToken, SetGlobalVars.global_tradingStat, inputDict[eachToken][fyCmnDef.K_TRADIN_STAT]), printFlag)
					SetGlobalVars.global_tradingStat = inputDict[eachToken][fyCmnDef.K_TRADIN_STAT]
			
			timestamp_NSE 	= inputDict[eachToken][fyCmnDef.K_BCH_TS]
			if timestamp_NSE <= 0: ## New Ajay 2018-06-01
				SetGlobalVars.global_rejected += 1
				continue
			SetGlobalVars.global_TS_NSE 	= timestamp_NSE
			todayStartTS	= timestamp_NSE - (timestamp_NSE % 86400)
			curMinTS 		= timestamp_NSE - (timestamp_NSE % 60)
			setDelayedData 	= False
			if SetGlobalVars.global_timeStamp < curMinTS: ## We got new min data
				# pdb.set_trace()
				# print "push dict:", minValDict
				## VIP: This is done coz dictionary will be call by reference and the same values will be overwritten
				minDictCpy = {} #minValDict.copy()
				for eachItem in curMinValDict:
					minDictCpy[eachItem] = curMinValDict[eachItem].copy() 
				# print "id minValDict:",id(minValDict)
				# print "id minDictCpy:",id(minDictCpy)
				# print "len minDictCpy:",len(minDictCpy)
				if len(minDictCpy) > 0:#global_minSetFlag in [fyCmnDef.MKT_F_NORMAL_OPEN, fyCmnDef.MKT_F_PARTIAL]: ## New change Ajay 2018-04-17
					minQueue.put([SetGlobalVars.global_timeStamp, minDictCpy])## Commented for testing 2018-01-16
					minEventTh.set() ## Commented for testing 2018-01-16
				currKeys = curMinValDict.keys()
				for eachKey in currKeys: ## This has to be done because we must keep track of only current min data and  delete rest of the tokens of previous minute
					del curMinValDict[eachKey]
				# print "Done with the time:%s"%(global_timeStamp)
				if debugFlag == fyCmnDef.DEBUG_ADDITNL_PRINT:
					logErr_inst.LogError(None, "LOG:%s Done with the time:%s"%(fyCmnDef.ERROR_setToMemc[6:], SetGlobalVars.global_timeStamp), printFlag)
				SetGlobalVars.global_timeStamp = curMinTS

			elif SetGlobalVars.global_timeStamp == curMinTS:
				None ## This is current min repeat data
			else:## Happens when we get delayed data
				## Previous min data has to be set in this case for that token.
				setDelayedData = True
				# if debugFlag == fyCmnDef.DEBUG_ADDITNL_PRINT: ## Changed on 2018-06-01
				# 	logErr_inst.LogError(None, "%s Delayed data received for taken:%s global_timeStamp:%s, curMinTS:%s"%(fyCmnDef.ERROR_setToMemc, eachToken, global_timeStamp, curMinTS), printFlag)
				
			memcToken_RT 	= "%s-%s-%s"%(eachToken, fyMemC.K_FY_MEMC_TOKEN_RT_DATA, todayStartTS)
			memcTVKey 		= "%s-%s-%s"%(eachToken, fyMemC.K_FY_TV_ALL_DATA, todayStartTS)
			# print memcToken_RT
			## New addition Ajay 2018-04-02. In case if we are running it for test maekt segment we should not mess the live data.
			if inputSegment in [fyCmnDef.SEG_NAME_CM_TEST, fyCmnDef.SEG_NAME_FO_TEST, fyCmnDef.SEG_NAME_CD_TEST, mcx_conf.SYM_SEGMENT_COM_NAME_TEST]:
				memcToken_RT += "-test"
				memcTVKey += "-test"
			# print "memcToken_RT:%s, memcTVKey:%s"%(memcToken_RT, memcTVKey)## For testing comment it in **LIVE**
			# sys.exit()## For testing comment it in **LIVE**
			if debugFlag == fyCmnDef.DEBUG_TIME:
				print "1.1:",time.time() - pointA
			tokenMinDict = {}
			# if eachToken == "101000000026000":
			# 	print minValDict[eachToken]
			if eachToken in minValDict:
				tokenMinDict = minValDict[eachToken]
			else:
				## If we restart the program in between this will help
				fileName 	= tempDirectoryPath + str(memcTVKey) + ".json"
				# Commented below line of code for testing 2018-01-16
				## Get the data from file system
				if os.path.exists(fileName) == True:
					try:
						with open(fileName, "rb") as dataFP:
							fileDataTV = dataFP.read()
							dataFP.close()
							if len(fileDataTV) > 0:
								## print "fileDataTV:", fileDataTV
								##sys.exit() ## For testing comment it in ** LIVE **
								retPrevVal = getPrevMinVal(None, fileDataTV, memcTVKey, printFlag = printFlag)
								if retPrevVal[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
									tokenMinDict = {}
									logErr_inst.LogError(None, "%s Getting from file failed. Error:%s"%(fyCmnDef.ERROR_setToMemc, retPrevVal[fyCmnDef.K_ERR_MSG]), printFlag)
								else:
									tokenMinDict = retPrevVal[fyCmnDef.K_FUN_DATA]

								if debugFlag == fyCmnDef.DEBUG_TIME: ## To Debug
									print "1.2:",time.time() - pointA
							else:
								tokenMinDict = {} ## Empty file
					except Exception,e:
						exc_type, exc_obj, exc_tb = sys.exc_info()
						logErr_inst.LogError(None, "%s Line:%s. Exception for token:%s while getting from file system. Except:%s"%(fyCmnDef.ERROR_setToMemc, exc_tb.tb_lineno, eachToken, str(e)), printFlag)
				else:
					tokenMinDict = {} ## File does not exist

				## Try to get the token details from cache if there are no details locally present.
				##tokenMinDict = {} ## This is for testing 2018-02-22. Comment it in **LIVE**
				if len(tokenMinDict) == 0:
					## This will happen only when there in no data in program memory and no data in file system. This will try to get the data from the cache system.
					if nocache == False: ## Only is it is specified 
						try: 
							cacheVal = cacheConn.get(memcTVKey)
							if cacheVal != None:
								## print "cacheVal:", cacheVal
								## sys.exit() ## This is for testing comment it in ** LIVE **
								retPrevVal = getPrevMinVal(None, cacheVal, memcTVKey, printFlag = printFlag)
								if retPrevVal[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
									tokenMinDict = {}
									logErr_inst.LogError(None, "%s Getting from cached failed. Error:%s"%(fyCmnDef.ERROR_setToMemc, retPrevVal[fyCmnDef.K_ERR_MSG]), printFlag)
								else:
									tokenMinDict = retPrevVal[fyCmnDef.K_FUN_DATA]
									# print "Success for token:%s in cache"%(memcTVKey)
						except Exception,e:
							exc_type, exc_obj, exc_tb = sys.exc_info()
							logErr_inst.LogError(None, "%s Line:%s. Exception for token:%s while getting cache val. Except:%s"%(fyCmnDef.ERROR_setToMemc, exc_tb.tb_lineno, eachToken, str(e)), printFlag)

			if debugFlag == fyCmnDef.DEBUG_TIME:
				print "1.3:",time.time() - pointA

			## *************** New code Palash 2018-08-31 ***************
			# Check for ltp, low, high and open for zero and set it accordingly - Palash
			## This will happen when there are no trades and the bid/ask or any othere values have changed.
			## The open, high, low, ltp can be zero and close will be previous days close
			
			if inputDict[eachToken][fyCmnDef.K_LTP] <= 0:
				if eachToken in tokenMinDict:
					if fyMemC.K_MEMC_LTP in tokenMinDict:
						## This should not happen in normal market. But for slow datafeed this can happen.
						if tokenMinDict[fyMemC.K_MEMC_LTP] >= 0:
							inputDict[eachToken][fyCmnDef.K_LTP] = tokenMinDict[fyMemC.K_MEMC_LTP]
				else:
					inputDict[eachToken][fyCmnDef.K_LTP] = inputDict[eachToken][fyCmnDef.K_CLOSING_P]

			if inputDict[eachToken][fyCmnDef.K_LOW_P] <= 0:
				if fyMemC.K_MEMC_FY_DAY_L in tokenMinDict:
					if eachToken in tokenMinDict:
						if tokenMinDict[fyMemC.K_MEMC_FY_DAY_L] >= 0:
							inputDict[eachToken][fyCmnDef.K_LOW_P] = tokenMinDict[fyMemC.K_MEMC_FY_DAY_L]
						else:
							inputDict[eachToken][fyCmnDef.K_LOW_P] = inputDict[eachToken][fyCmnDef.K_LTP]
				else:
					inputDict[eachToken][fyCmnDef.K_LOW_P] = inputDict[eachToken][fyCmnDef.K_LTP]

			if inputDict[eachToken][fyCmnDef.K_HIGH_P] <= 0:
				if eachToken in tokenMinDict:
					if fyMemC.K_MEMC_FY_DAY_L in tokenMinDict:
						if tokenMinDict[fyMemC.K_MEMC_FY_DAY_H] >= 0:
							inputDict[eachToken][fyCmnDef.K_HIGH_P] = tokenMinDict[fyMemC.K_MEMC_FY_DAY_H]
						else:
							inputDict[eachToken][fyCmnDef.K_HIGH_P] = inputDict[eachToken][fyCmnDef.K_LTP]
				else:
					inputDict[eachToken][fyCmnDef.K_LOW_P] = inputDict[eachToken][fyCmnDef.K_LTP]

			if inputDict[eachToken][fyCmnDef.K_OPEN_P] <= 0:
				if eachToken in minValDict:
					if fyMemC.K_MEMC_OPEN_P in tokenMinDict:
						if tokenMinDict[fyMemC.K_MEMC_OPEN_P] >= 0:
							inputDict[eachToken][fyCmnDef.K_OPEN_P] = tokenMinDict[fyMemC.K_MEMC_OPEN_P]
						else:
							inputDict[eachToken][fyCmnDef.K_OPEN_P] = inputDict[eachToken][fyCmnDef.K_LTP]
				else:
					inputDict[eachToken][fyCmnDef.K_OPEN_P] = inputDict[eachToken][fyCmnDef.K_LTP]
			## *************** End New code Palash 2018-08-31 ***************

			# pdb.set_trace()
			# print "tokenMinDict:", tokenMinDict
			if len(tokenMinDict) > 0:
				dictKeys = tokenMinDict.keys()
				if fyMemC.K_MEMC_TV_OPEN in dictKeys and fyMemC.K_MEMC_TV_HIGH in dictKeys and fyMemC.K_MEMC_TV_LOW in dictKeys and fyMemC.K_MEMC_TV_CLOSE in dictKeys and fyMemC.K_MEMC_TV_VOL in dictKeys and fyMemC.K_MEMC_TV_TIME in dictKeys and fyMemC.K_MEMC_FY_DAY_H in dictKeys and fyMemC.K_MEMC_FY_DAY_L in dictKeys and fyMemC.K_MEMC_FY_VTT in dictKeys:
					## all the required fields are present
					# currentCandleIndex = -1 ## Do not use zero
					if debugFlag == fyCmnDef.DEBUG_TIME:
						print "1.4:",time.time()-pointA

					minVol 		= 0
					minOpen 	= minHigh = minLow = minClose = inputDict[eachToken][fyCmnDef.K_LTP] ## set to LTP by default
					currentMinFlag = -1
					# print "tokenMinDict[fyMemC.K_MEMC_TV_TIME]:", tokenMinDict[fyMemC.K_MEMC_TV_TIME]
					if   tokenMinDict[fyMemC.K_MEMC_TV_TIME] == curMinTS:
						currentMinFlag 	= 1
					elif tokenMinDict[fyMemC.K_MEMC_TV_TIME] < curMinTS:
						currentMinFlag = -1
					else:
						currentMinFlag = -1
						# logErr_inst.LogError(None, "%s Internal saved timestamp:%s > currentTime:%s"%(fyCmnDef.ERROR_setToMemc, tokenMinDict[fyMemC.K_MEMC_TV_TIME], curMinTS), printFlag) ## Commented on 2018-06-01
					
					## **************** Calcualte min low ****************
					if inputDict[eachToken][fyCmnDef.K_LOW_P] < tokenMinDict[fyMemC.K_MEMC_FY_DAY_L]:
						minLow = inputDict[eachToken][fyCmnDef.K_LOW_P]
						# tokenMinDict[fyMemC.K_MEMC_FY_DAY_L] = inputDict[eachToken][fyCmnDef.K_LOW_P] ## Commented Ajay 2018-04-11
					elif inputDict[eachToken][fyCmnDef.K_LOW_P] == tokenMinDict[fyMemC.K_MEMC_FY_DAY_L]:
						if currentMinFlag == -1: ## This the first tick of the current candle
							minLow = inputDict[eachToken][fyCmnDef.K_LTP]
						else:
							if inputDict[eachToken][fyCmnDef.K_LTP] < tokenMinDict[fyMemC.K_MEMC_TV_LOW]:
								minLow = inputDict[eachToken][fyCmnDef.K_LTP]
							else:
								minLow = tokenMinDict[fyMemC.K_MEMC_TV_LOW]
					else:
						if tokenMinDict[fyMemC.K_MEMC_FY_DAY_L] != 0: ## There might be a case where we store 0. So 0 is not an error
							if str(SetGlobalVars.global_tradingStat) not in nseConf.NSE_P_TRADIN_STAT_PREOPEN: ## This is for premarket data
								errMsg = "%s Day low value found to be greater than the one which is stored for:%s LOW::rx: %s, stored:%s, LTP:%s"%(fyCmnDef.ERROR_setToMemc, eachToken, inputDict[eachToken][fyCmnDef.K_LOW_P], tokenMinDict[fyMemC.K_MEMC_FY_DAY_L], inputDict[eachToken][fyCmnDef.K_LTP])
								logErr_inst.LogError(None, errMsg, printFlag)
						# minLow = inputDict[eachToken][fyCmnDef.K_LTP]
						minLow = inputDict[eachToken][fyCmnDef.K_LOW_P] ## New change Palash 2018-08-31
						# tokenMinDict[fyMemC.K_MEMC_FY_DAY_L] = inputDict[eachToken][fyCmnDef.K_LTP] ## Commented Ajay 2018-04-11

					if debugFlag == fyCmnDef.DEBUG_TIME:
						print "1.6:",time.time() - pointA

					## **************** Calculate high value for the min ****************
					if inputDict[eachToken][fyCmnDef.K_HIGH_P] > tokenMinDict[fyMemC.K_MEMC_FY_DAY_H]: 
						minHigh = inputDict[eachToken][fyCmnDef.K_HIGH_P]
						# tokenMinDict[fyMemC.K_MEMC_FY_DAY_H] = inputDict[eachToken][fyCmnDef.K_HIGH_P] ## Commented Ajay 2018-04-11
					elif inputDict[eachToken][fyCmnDef.K_HIGH_P] == tokenMinDict[fyMemC.K_MEMC_FY_DAY_H]:
						if currentMinFlag == -1: ## This the first tick of the current candle
							minHigh = inputDict[eachToken][fyCmnDef.K_LTP]
						else:
							if inputDict[eachToken][fyCmnDef.K_LTP] > tokenMinDict[fyMemC.K_MEMC_TV_HIGH]:
								minHigh = inputDict[eachToken][fyCmnDef.K_LTP]
							else:
								minHigh = tokenMinDict[fyMemC.K_MEMC_TV_HIGH]
					else:
						##New change Ajay 2018-04-02
						if str(SetGlobalVars.global_tradingStat) not in nseConf.NSE_P_TRADIN_STAT_PREOPEN: ## This is for premarket data
							errMsg = "%s Day high value is found to be less than the one which is stored for:%s, HIGH::rx: %s, stored:%s, LTP:%s"%(fyCmnDef.ERROR_setToMemc, eachToken, inputDict[eachToken][fyCmnDef.K_HIGH_P], tokenMinDict[fyMemC.K_MEMC_FY_DAY_H], inputDict[eachToken][fyCmnDef.K_LTP])
							logErr_inst.LogError(None, errMsg, printFlag)
						# print inputDict[eachToken]
						# minHigh = inputDict[eachToken][fyCmnDef.K_LTP]
						minHigh = inputDict[eachToken][fyCmnDef.K_HIGH_P]## New change Palash 2018-08-31
						# tokenMinDict[fyMemC.K_MEMC_FY_DAY_H] = inputDict[eachToken][fyCmnDef.K_LTP] ## Commented Ajay 2018-04-11

					## **************** Calcualte open ****************
					volumeIndex = 0 ## To calculate volumne
					if currentMinFlag == -1: ## This the first tick of the current candle
						minOpen = inputDict[eachToken][fyCmnDef.K_LTP]
						minVol 	= inputDict[eachToken][fyCmnDef.K_VTT] - tokenMinDict[fyMemC.K_MEMC_FY_VTT]
					else:
						minOpen = tokenMinDict[fyMemC.K_MEMC_TV_OPEN]
						minVol 	= inputDict[eachToken][fyCmnDef.K_VTT] - tokenMinDict[fyMemC.K_MEMC_FY_VTT] + tokenMinDict[fyMemC.K_MEMC_TV_VOL]
					if minVol < 0 :
						## New change Ajay 2018-04-02. During premarket session volume found to be negative.
						if str(SetGlobalVars.global_tradingStat) not in nseConf.NSE_P_TRADIN_STAT_PREOPEN: ## This is for premarket data
							logErr_inst.LogError(None, "%sVolume:%s found to be negative for the token:%s"%(fyCmnDef.ERROR_setToMemc, minVol, eachToken), printFlag)
						minVol = 0 ## This happens during preopen

					## ********** Start Change Ajay 2019-05-20 For tick data **********
					tickVol = 0
					tickVol = inputDict[eachToken][fyCmnDef.K_VTT] - tokenMinDict[fyMemC.K_MEMC_FY_VTT] 
					# if eachToken.startswith("1210000000500112"):
					# 	print "timestamp_NSE:%s, minVol:%s, tickVol:%s"%(timestamp_NSE, minVol, tickVol)
					if tickVol < 0:
						tickVol = 0
						# logErr_inst.LogError(None, "%sTick volume:%s found to be negative for the token:%s"%(fyCmnDef.ERROR_setToMemc, tickVol, eachToken), printFlag)
					## ********** End Change Ajay 2019-05-20 For tick data **********

					tempTvTime = tokenMinDict[fyMemC.K_MEMC_TV_TIME] ## The value will be overwritten
					tokenMinDict[fyMemC.K_MEMC_TV_TIME]  	= curMinTS
					tokenMinDict[fyMemC.K_MEMC_TV_OPEN]  	= minOpen
					tokenMinDict[fyMemC.K_MEMC_TV_HIGH]  	= minHigh
					tokenMinDict[fyMemC.K_MEMC_TV_LOW]  	= minLow
					tokenMinDict[fyMemC.K_MEMC_TV_CLOSE]  	= inputDict[eachToken][fyCmnDef.K_LTP]
					tokenMinDict[fyMemC.K_MEMC_FY_DAY_H] 	= inputDict[eachToken][fyCmnDef.K_HIGH_P] ## Uncommented Ajay 2018-04-11 for the first candle high value was wrong
					tokenMinDict[fyMemC.K_MEMC_FY_DAY_L] 	= inputDict[eachToken][fyCmnDef.K_LOW_P] ## Uncommented Ajay 2018-04-11 for the first candle high value was wrong
					tokenMinDict[fyMemC.K_MEMC_TV_VOL]  	= minVol
					tokenMinDict[fyMemC.K_MEMC_FY_VTT]  	= inputDict[eachToken][fyCmnDef.K_VTT]
					tokenMinDict[fyMemC.K_MEMC_FY_TOKEN] 	= memcTVKey
					tokenMinDict[fyMemC.K_MEMC_LTP] 		= inputDict[eachToken][fyCmnDef.K_LTP]
					tokenMinDict[fyMemC.K_MEMC_RT_TICK_VOL]	= tickVol ## New Ajay 2019-05-20
					if setDelayedData and tempTvTime == curMinTS:
						# None ## Comment this line in ** LIVE **
						if SetGlobalVars.global_minSetFlag == [fyCmnDef.MKT_F_NORMAL_OPEN, fyCmnDef.MKT_F_PARTIAL]:## New : Ajay 2018-04-10
							minQueue.put([tempTvTime, {eachToken: tokenMinDict}])## Change Ajay 2018-04-19
							minEventTh.set()## Commented for testing 2018-01-16
					
				else:
					## Special case we need to take care of this. TODO: Yet to be implemented.
					logErr_inst.LogError(None, "%sImproper JSON value found in memory for token:%s"%(fyCmnDef.ERROR_setToMemc, eachToken), printFlag)
					## There should be someone stop setting to memcache if this the case ##continue
			else:
				## First tick of the day # print "new day val"
				tokenMinDict =  {
									fyMemC.K_MEMC_TV_TIME 	: timestamp_NSE - (timestamp_NSE % 60), 
									fyMemC.K_MEMC_TV_OPEN 	: inputDict[eachToken][fyCmnDef.K_OPEN_P], 
									fyMemC.K_MEMC_TV_HIGH 	: inputDict[eachToken][fyCmnDef.K_HIGH_P], 
									fyMemC.K_MEMC_TV_LOW 	: inputDict[eachToken][fyCmnDef.K_LOW_P], 
									fyMemC.K_MEMC_TV_CLOSE 	: inputDict[eachToken][fyCmnDef.K_LTP], 
									fyMemC.K_MEMC_FY_DAY_H	: inputDict[eachToken][fyCmnDef.K_HIGH_P], 
									fyMemC.K_MEMC_FY_DAY_L	: inputDict[eachToken][fyCmnDef.K_LOW_P], 
									fyMemC.K_MEMC_TV_VOL 	: inputDict[eachToken][fyCmnDef.K_VTT],
									fyMemC.K_MEMC_FY_VTT 	: inputDict[eachToken][fyCmnDef.K_VTT],
									fyMemC.K_MEMC_FY_TOKEN 	: memcTVKey,
									fyMemC.K_MEMC_LTP 		: inputDict[eachToken][fyCmnDef.K_LTP],
									fyMemC.K_MEMC_RT_TICK_VOL: inputDict[eachToken][fyCmnDef.K_VTT] ## New Ajay 2019-05-20
								}
			
			tokenMinDict[fyCmnDef.K_TRADIN_STAT] 	= inputDict[eachToken][fyCmnDef.K_TRADIN_STAT] ## New addition Ajay 2018-02-22
			tokenMinDict[fyMemC.K_MEMC_OPEN_P] 		= inputDict[eachToken][fyCmnDef.K_OPEN_P] ##New change Ajay 2018-04-03
			minValDict[eachToken] 		= tokenMinDict
			# print "tokenMinDict:", tokenMinDict
			if SetGlobalVars.global_minSetFlag == fyCmnDef.MKT_F_NORMAL_OPEN: ## New change Ajay 2018-04-10
				curMinValDict[eachToken] 	= tokenMinDict
			elif SetGlobalVars.global_minSetFlag == fyCmnDef.MKT_F_PARTIAL: ## New addition Ajay 2018-04-10
				if eachToken in exceptTokenDict:
					# print "after market except token min push:%s"%(eachToken)
					curMinValDict[eachToken] = tokenMinDict
				else:
					## If its partially traded and the token is not there in the exception tokens then drop it
					# print "***** token %s is not partially traded.****"%(eachToken)
					None
			else: ## New addition Ajay 2018-04-10
				## If its not market open or partially traded do not set the minute data.
				None

			if int(inputDict[eachToken][fyCmnDef.K_BCH_PACKT_CODE]) == int(nseConf.NSE_T_CODE_7207) or int(inputDict[eachToken][fyCmnDef.K_BCH_PACKT_CODE]) == int(nseConf.NSE_T_CODE_7208):
				if debugFlag == fyCmnDef.DEBUG_TIME:
					print "1.14:",time.time()-pointA

				# print "stat:", inputDict[eachToken][fyCmnDef.K_TRADIN_STAT]
				# if global_minSetFlag in [fyCmnDef.MKT_F_NORMAL_OPEN, fyCmnDef.MKT_F_PARTIAL]
				if SetGlobalVars.global_minSetFlag in [fyCmnDef.MKT_F_PARTIAL, fyCmnDef.MKT_F_CLOSED]: ## New change ajay 2018-04-10
					## New change Ajay 2018-03-16 verification of trading status has been added.
					getPrevClose = False ## New addition Ajay 2018-04-10
					if SetGlobalVars.global_minSetFlag == fyCmnDef.MKT_F_CLOSED: ## New addition Ajay 2018-04-10
						getPrevClose = True
					elif SetGlobalVars.global_minSetFlag == fyCmnDef.MKT_F_PARTIAL and eachToken not in exceptTokenDict:
						getPrevClose = True
					if getPrevClose == True: ## New addition Ajay 2018-04-10
						if str(inputDict[eachToken][fyCmnDef.K_TRADIN_STAT]) in nseConf.NSE_P_TRADIN_STAT_OPEN:
							prevMemcVal = cacheConn.get(str(memcToken_RT))
							if prevMemcVal == None:
								## This may happen if the script has not traded at all for this day.
								## This did happen around 6:50 AM IST 
								logErr_inst.LogError(None, "%s. After market memc get failed for: %s. Possible reason script not traded today."%(fyCmnDef.ERROR_setToMemc, memcToken_RT), printFlag)
							else:
								try:
									if not isinstance(prevMemcVal,dict):
										prevMemcVal = json.loads(prevMemcVal)
									inputDict[eachToken][fyCmnDef.K_CLOSING_P] = prevMemcVal[str(fyMemC.K_MEMC_CLOSING_P)]
									# print "prev close from cache for %s"%(eachToken)
								except Exception,e:
									exc_type, exc_obj, exc_tb = sys.exc_info()
									errMsg = "%s Line:%s. After market JSON load failed for:%s . Except:%s"%(fyCmnDef.ERROR_setToMemc, exc_tb.tb_lineno, memcToken_RT, str(e))
									logErr_inst.LogError(None, errMsg, printFlag)
								finally:
									None
						# elif str(global_tradingStat) in nseConf.NSE_P_TRADIN_STAT_CLOSE: ## Addition Ajay 2018-03-19
						# 	## Commented because its under devel
						# 	## 1, 4, 6 will be sent for preopen
						# 	None
						else:
							None ## This will happen during preopen session 

				if debugFlag == fyCmnDef.DEBUG_TIME:
					print "1.15:",time.time()-pointA

				memcValDict = {}
				## Common fields for 7207 and 7208
				memcValDict[fyMemC.K_MEMC_LTP]			= inputDict[eachToken][fyCmnDef.K_LTP]
				memcValDict[fyMemC.K_MEMC_CHANGE_P] 	= round((inputDict[eachToken][fyCmnDef.K_LTP] - inputDict[eachToken][fyCmnDef.K_CLOSING_P]), roundoff)
				memcValDict[fyMemC.K_MEMC_VTT] 			= 0 
				memcValDict[fyMemC.K_MEMC_CLOSING_P] 	= inputDict[eachToken][fyCmnDef.K_CLOSING_P] ##closingPrice, 
				memcValDict[fyMemC.K_MEMC_OPEN_P] 		= inputDict[eachToken][fyCmnDef.K_OPEN_P] ##openPrice, 
				memcValDict[fyMemC.K_MEMC_HIGH_P] 		= inputDict[eachToken][fyCmnDef.K_HIGH_P] ##highPrice, 
				memcValDict[fyMemC.K_MEMC_LOW_P] 		= inputDict[eachToken][fyCmnDef.K_LOW_P] ##lowPrice,

				memcValDict[fyMemC.K_MEMC_ASK_P_START] 	= inputDict[eachToken][fyCmnDef.K_LTP] ##indexVal7207, 
				memcValDict[fyMemC.K_MEMC_BID_P_START] 	= inputDict[eachToken][fyCmnDef.K_LTP] ##indexVal7207, 
				
				memcValDict[fyMemC.K_MEMC_LTT] 			= inputDict[eachToken][fyCmnDef.K_BCH_TS] ## For 7207 timestamp sent in broadcast header is considered as last-traded-time
				memcValDict[fyMemC.K_MEMC_PCT_CHANGE] 	= 0 ## New addition Ajay 2018-03-19
				if fyCmnDef.K_PERCENT_CHNG in inputDict[eachToken]:## New addition Ajay 2018-03-19
					memcValDict[fyMemC.K_MEMC_PCT_CHANGE] = inputDict[eachToken][fyCmnDef.K_PERCENT_CHNG]
					## 2018-03-20: For pre-market under dev. 
					if str(SetGlobalVars.global_tradingStat) in nseConf.NSE_P_TRADIN_STAT_PREOPEN: ## Ajay 2018-03-20 For pre-market value
						# logErr_inst.LogError(None, "eachToken:%s, %s"%(eachToken,str(inputDict[eachToken])), printFlag)
						lastCloseP = inputDict[eachToken][fyCmnDef.K_LTP] *100/(100 + inputDict[eachToken][fyCmnDef.K_PERCENT_CHNG])
						## New code ajay 2018-04-05
						if eachToken in tokenPrevValDict:
							if fyCmnDef.K_CLOSING_P in tokenPrevValDict[eachToken]: 
								lastCloseP = tokenPrevValDict[eachToken][fyCmnDef.K_CLOSING_P]
								# print "proper close premarket for token:%s"%(eachToken)
							else:
								logErr_inst.LogError(None, "%s Pre_Mkt close_p of prev day not found for token:%s"%(fyCmnDef.ERROR_setToMemc, eachToken), printFlag)
						else:
							if str(eachToken) != str(1010000000999043): ## for Hang-sang There is no previous close price in DB
								logErr_inst.LogError(None, "%s Pre_Mkt token:%s not found to get previous day close."%(fyCmnDef.ERROR_setToMemc, eachToken), printFlag)
						memcValDict[fyMemC.K_MEMC_CHANGE_P] = round((inputDict[eachToken][fyCmnDef.K_LTP] - lastCloseP), roundoff)
						# print "%s eachToken:%s changing the close"%(fyCmnDef.ERROR_setToMemc, eachToken)
						memcValDict[fyMemC.K_MEMC_CLOSING_P] = lastCloseP ## Change Ajay 2019-06-20 For premarket
				spreadVal = 0.0 ## For index values this will be zero
				if int(inputDict[eachToken][fyCmnDef.K_BCH_PACKT_CODE]) == int(nseConf.NSE_T_CODE_7208):
					## Only for 7208 we have additional fields
					## Ajay new change 2018-03-19
					if inputDict[eachToken][fyCmnDef.K_CLOSING_P] > 0: ## if closing price become zero divide by 0 error. Ajay 2018-02-22
						memcValDict[fyMemC.K_MEMC_PCT_CHANGE] = round((inputDict[eachToken][fyCmnDef.K_LTP] - inputDict[eachToken][fyCmnDef.K_CLOSING_P])*100/inputDict[eachToken][fyCmnDef.K_CLOSING_P], 2) ## The roundoff should 2.
					memcValDict[fyMemC.K_MEMC_LTT] 			= inputDict[eachToken][fyCmnDef.K_LTT]
					memcValDict[fyMemC.K_MEMC_LTQ] 			= inputDict[eachToken][fyCmnDef.K_LTQ] 
	 				memcValDict[fyMemC.K_MEMC_VTT] 			= inputDict[eachToken][fyCmnDef.K_VTT]
					memcValDict[fyMemC.K_MEMC_ATP] 			= inputDict[eachToken][fyCmnDef.K_ATP]
					memcValDict[fyMemC.K_MEMC_TOT_BUY_Q] 	= inputDict[eachToken][fyCmnDef.K_TOT_BUY_Q]
					memcValDict[fyMemC.K_MEMC_TOT_SELL_Q] 	= inputDict[eachToken][fyCmnDef.K_TOT_SELL_Q]

					## New Change Ajay 2018-04-02. Added for premarket session.
					if str(SetGlobalVars.global_tradingStat) in nseConf.NSE_P_TRADIN_STAT_PREOPEN: ## This is for premarket data
						if memcValDict[fyMemC.K_MEMC_OPEN_P] <= 0:
							memcValDict[fyMemC.K_MEMC_OPEN_P] = inputDict[eachToken][fyCmnDef.K_LTP]
						if memcValDict[fyMemC.K_MEMC_HIGH_P] <= 0:
							memcValDict[fyMemC.K_MEMC_HIGH_P] = inputDict[eachToken][fyCmnDef.K_LTP]
						if memcValDict[fyMemC.K_MEMC_LOW_P] <= 0:
							memcValDict[fyMemC.K_MEMC_LOW_P] = inputDict[eachToken][fyCmnDef.K_LTP]
						if memcValDict[fyMemC.K_MEMC_CLOSING_P] <= 0:
							memcValDict[fyMemC.K_MEMC_CLOSING_P] = inputDict[eachToken][fyCmnDef.K_LTP]
					
					bidAskCnt = 0
					for eachEntry in inputDict[eachToken][fyCmnDef.K_BID_ASK_DICT][fyCmnDef.K_BID]:
						memcValDict[fyMemC.K_MEMC_BID_QTY_START + bidAskCnt] 	= eachEntry[fyCmnDef.K_BID_ASK_QTY]
						memcValDict[fyMemC.K_MEMC_BID_P_START + bidAskCnt] 		= eachEntry[fyCmnDef.K_BID_ASK_P]
						if fyCmnDef.K_NUM_BID_ASK in eachEntry: ## Change Ajay 2019-06-10
							memcValDict[fyMemC.K_MEMC_BID_NUM_START + bidAskCnt]	= eachEntry[fyCmnDef.K_NUM_BID_ASK]
							# memcValDict[fyMemC.K_MEMC_IMPL_BID_QTY_START + bidAskCnt]	= eachEntry[fyCmnDef.K_IMPL_QTY]
						bidAskCnt += 1
					bidAskCnt = 0
					for eachEntry in inputDict[eachToken][fyCmnDef.K_BID_ASK_DICT][fyCmnDef.K_ASK]:
						memcValDict[fyMemC.K_MEMC_ASK_QTY_START + bidAskCnt] 	= eachEntry[fyCmnDef.K_BID_ASK_QTY]
						memcValDict[fyMemC.K_MEMC_ASK_P_START + bidAskCnt] 		= eachEntry[fyCmnDef.K_BID_ASK_P]
						if fyCmnDef.K_NUM_BID_ASK in eachEntry: ## Change Ajay 2019-06-10
							memcValDict[fyMemC.K_MEMC_ASK_NUM_START + bidAskCnt]	= eachEntry[fyCmnDef.K_NUM_BID_ASK]
							# memcValDict[fyMemC.K_MEMC_IMPL_ASK_QTY_START + bidAskCnt]	= eachEntry[fyCmnDef.K_IMPL_QTY]
						bidAskCnt += 1

					spreadVal = memcValDict[fyMemC.K_MEMC_ASK_P_START] - memcValDict[fyMemC.K_MEMC_BID_P_START]
				try:
					memcValDict[fyMemC.K_MEMC_RT_TS] 	= tokenMinDict[fyMemC.K_MEMC_TV_TIME]
					memcValDict[fyMemC.K_MEMC_RT_OPEN] 	= tokenMinDict[fyMemC.K_MEMC_TV_OPEN]
					memcValDict[fyMemC.K_MEMC_RT_HIGH] 	= tokenMinDict[fyMemC.K_MEMC_TV_HIGH]
					memcValDict[fyMemC.K_MEMC_RT_LOW] 	= tokenMinDict[fyMemC.K_MEMC_TV_LOW]
					memcValDict[fyMemC.K_MEMC_RT_CLOSE] = tokenMinDict[fyMemC.K_MEMC_TV_CLOSE]
					memcValDict[fyMemC.K_MEMC_RT_VOL] 	= tokenMinDict[fyMemC.K_MEMC_TV_VOL]
					memcValDict[fyMemC.K_MEMC_SPREAD] 	= round(spreadVal, roundoff) ##601-401
					memcValDict[fyMemC.K_MEMC_TODAY_TS]	= todayStartTS
					memcValDict[fyMemC.K_MEMC_RT_TICK_TS]= timestamp_NSE ## Ajay 2019-05-20 for tick data
					localTimeMin = time.localtime(curMinTS)
					memcValDict[fyMemC.K_MEMC_IST_MIN_TS]= "%s:%s"%(localTimeMin.tm_hour, localTimeMin.tm_min)
					memcValDict[fyMemC.K_MEMC_RT_TICK_VOL]= tokenMinDict[fyMemC.K_MEMC_RT_TICK_VOL]## New Ajay 2019-05-20
				except Exception,e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					logErr_inst.LogError(None, "%s Line:%s. Excepton adding OHLCV to RT token. Except:%s"%(fyCmnDef.ERROR_setToMemc, exc_tb.tb_lineno, str(e)), printFlag)
				cacheQueue.put({memcToken_RT:memcValDict}) ## Commented for testing 2018-01-16

				if noSend == False:
					##Code for streaming server - 20181031 Palash
					sendDict = memcValDict.copy()
					sendDict[fyMemC.K_MEMC_TS_BCH] 		= inputDict[eachToken][fyCmnDef.K_BCH_TS]
					sendDict[fyMemC.K_MEMC_TRANS_CODE] 	= inputDict[eachToken][fyCmnDef.K_BCH_PACKT_CODE]
					sendDict['tradeStat']				= SetGlobalVars.global_minSetFlag
					sendPktQ.put({eachToken:sendDict})
					##END

				if debugFlag == fyCmnDef.DEBUG_TIME:
					print "1.16:",time.time() - pointA
		
			else:
				logErr_inst.LogError(None, "%s Unknown transaction code: '%s'"%(fyCmnDef.ERROR_setToMemc, inputDict[eachToken][fyCmnDef.K_BCH_PACKT_CODE]), printFlag)
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logErr_inst.LogError(None, "%s Line:%s. Unknow exception. Except:%s"%(fyCmnDef.ERROR_setToMemc, exc_tb.tb_lineno, str(e)), printFlag)
	finally:
		None



def setOiToThread(logErr_inst, inputExchange, inputSegment, roundoff, tempDirectoryPath, cacheConn, inputDict, cacheQueue, minQueue, minValDict, curMinValDict, minEventTh, exceptTokenDict, tokenPrevValDict, sendThEvent, sendPktQ, printFlag = False, debugFlag = False, nocache = False, develFlag = False, noSend = False):
	"""
	[Function]  : 	This function does the following
					1. Update the global variable which will contain timestamp that is sent by NSE.
					2. Check for the change in trading status that will be sent with 7202 packet.
					3. If its a new minute then push the previous min data to queue(minQueue) that will set one min candles and clear the the data from the dict(curMinValDict).
					4. Try to get the the previous data if the data is not already there in the program memory(minValDict).  
					5. For each input packets received ie., for each input token calculate the OHLCV for the min depending on the day_high, day_low and vlume traded today.
					6. Update the calculated OHLCV to the current min dict(curMinValDict) and the dict that will contain all the data(minValDict)
					7. Update the realtime dict and put it into the queue(cacheQueue) which will update real-time data.
	
	[Input] 	: 	logErr_inst		-> The instance of log_error which will log errors.
					inputExchange 	-> NSE
				  	inputSegment 	-> FO/CD
					roundoff 		-> Number of decimal points for calculations.
					tempDirectoryPath-> This is the file path in which temp files will be written into.
					cacheConn 		-> Contain the cache connection.
					inputDict 		-> This dictionary contain the processed data which is sent by NSE. Key inthe dict will be token_number.
					cacheQueue		-> The queue in which real time update dict has to pushed.
					minQueue		-> The queue in which min dict has to be pushed.
					minValDict 		-> The dict which will contain all keys will be tokens those are received from NSE and the corrosponding OHLCV, day_high, day_low etc.. as values.
					curMinValDict 	-> Same as minValDict but contain data only current min. 
					minEventTh 		-> To indicate the min thread to start setting the min data for the previous min when the new min starts. 
					printFlag		-> True/False = print/no_Print.
					debugFlag 		-> Contain the information that can used for debugging.
					nocache 		-> True/False used for debugging when set to True it will not take values from cache.
	[Output]	: 	None.
	""" 
	try:
		#print("inputDict--> ", inputDict)
		#('inputDict--> ', {'10128001011708': {'fp': 987825000, 'ft': 1708, 'fv': 7, 201: 1608529015, 202: 7202, 34: 2, 'pv': '0.0', 'dhi': 87785, 'oi': 79517, 43: 1, 'dlo': 79517}})
		#print("minValDict--> ", minValDict)
		# print("curMinValDict--> ", curMinValDict)
		# ('curMinValDict--> ', {'10128001011487': {'fp': 737650000, 34: 2, 'ft': '10128001011487-2005-1608508800', 'oi': 4903203, 'fv': 13, 'dhi': 4910452, 201: 1608528414, 202: 7202, 43: 1, 'dlo': 4867415}})
		# for tok in minValDict:
		# 	t = tok['ft']
		# 	a,b,c = t.split('-')
		# 	b = int(b)
		# 	if b == 2005 :
		# 		print("Khushi ki baaaaaaaaaaaaaaaaaaaaaaaaattttt")
		for eachToken in inputDict:
			#print("Inside for loop")
			pointA = time.time()
			if debugFlag == fyCmnDef.DEBUG_TEST:
				None
				# inputDict[eachToken][K_BCH_TS] = pointA - (pointA % 60) ## This is done only for testing purpose
			## This is only to track the change in the trading status
			# print "eachToken:", eachToken
			
			if inputDict[eachToken][fyCmnDef.K_BCH_PACKT_CODE] == nseConf.NSE_T_CODE_7202:
				## This is needed because to process 7207 we will be sending global_tradingStat 
				if SetGlobalVars.global_tradingStat != inputDict[eachToken][fyCmnDef.K_TRADIN_STAT]:
					logErr_inst.LogError(None, "%s token:%s global_tradingStat:%s, changed_Stat:%s"%(fyCmnDef.ERROR_setToMemc, eachToken, SetGlobalVars.global_tradingStat, inputDict[eachToken][fyCmnDef.K_TRADIN_STAT]), printFlag)
					SetGlobalVars.global_tradingStat = inputDict[eachToken][fyCmnDef.K_TRADIN_STAT]
						
			timestamp_NSE 	= inputDict[eachToken][fyCmnDef.K_BCH_TS]

			if timestamp_NSE <= 0:
				SetGlobalVars.global_rejected += 1
				continue
			SetGlobalVars.global_TS_NSE 	= timestamp_NSE

			todayStartTS	= timestamp_NSE - (timestamp_NSE % 86400)
			curMinTS 		= timestamp_NSE - (timestamp_NSE % 60)
			setDelayedData 	= False

			memcToken_RT 	= "%s-%s-%s"%(eachToken, fyMemC.K_FY_MEMC_TOKEN_OI_DATA, todayStartTS)
			memcTVKey 		= "%s-%s-%s"%(eachToken, fyMemC.K_FY_TV_ALL_DATA, todayStartTS)
			#inputDict[eachToken][fyMemC.K_MEMC_OI_TOKEN] = memcToken_RT

			gt= SetGlobalVars.global_timeStamp

			#if SetGlobalVars.global_timeStamp < curMinTS: ## We got new min data
			if 0 < curMinTS: #Need to be edited
				#print("the if loop")
				minDictCpy = {} #minValDict.copy()

				for eachItem in curMinValDict:
					#minDictCpy[eachItem] = minValDict[eachItem].copy() 
					minDictCpy[eachItem] = curMinValDict[eachItem].copy() 

				if len(minDictCpy) > 0:
					minQueue.put([SetGlobalVars.global_timeStamp, minDictCpy])## Commented for testing 2018-01-16

					minEventTh.set() ## Commented for testing 2018-01-16
					
				currKeys = curMinValDict.keys()
				for eachKey in currKeys: ## This has to be done because we must keep track of only current min data and  delete rest of the tokens of previous minute
					del curMinValDict[eachKey]
				# print "Done with the time:%s"%(global_timeStamp)
				if debugFlag == fyCmnDef.DEBUG_ADDITNL_PRINT:
					logErr_inst.LogError(None, "LOG:%s Done with the time:%s"%(fyCmnDef.ERROR_setOiToThread[6:], SetGlobalVars.global_timeStamp), printFlag)
				SetGlobalVars.global_timeStamp = curMinTS

			elif SetGlobalVars.global_timeStamp == curMinTS:
				None ## This is current min repeat data
			else:## Happens when we get delayed data
				## Previous min data has to be set in this case for that token.
				setDelayedData = True
				# if debugFlag == fyCmnDef.DEBUG_ADDITNL_PRINT: ## Changed on 2018-06-01
				# 	logErr_inst.LogError(None, "%s Delayed data received for taken:%s global_timeStamp:%s, curMinTS:%s"%(fyCmnDef.ERROR_setOiToThread, eachToken, global_timeStamp, curMinTS), printFlag)
				
			# memcToken_RT 	= "%s-%s-%s"%(eachToken, fyMemC.K_FY_MEMC_TOKEN_OI_DATA, todayStartTS)
			# memcTVKey 		= "%s-%s-%s"%(eachToken, fyMemC.K_FY_TV_ALL_DATA, todayStartTS)
			if inputSegment in [fyCmnDef.SEG_NAME_FO_TEST, fyCmnDef.SEG_NAME_CD_TEST, mcx_conf.SYM_SEGMENT_COM_NAME_TEST]:
				memcToken_RT += "-test"
				memcTVKey += "-test"

			# sys.exit()## For testing comment it in **LIVE**
			if debugFlag == fyCmnDef.DEBUG_TIME:
				print "1.1:",time.time() - pointA
			tokenMinDict = {}

			#if eachToken in minValDict:
			if eachToken in inputDict:
				#tokenMinDict = minValDict[eachToken]
				tokenMinDict = inputDict[eachToken]
			else:
				## If we restart the program in between this will help
				fileName 	= tempDirectoryPath + str(memcToken_RT) + ".json"
				## Get the data from file system
				# print("fileName in fy_util-> ",fileName)
				# ('fileName in fy_util-> ', '/home/ec2-user/fy_var/temp_nse_init/CD/20210125/10122112292168-2005-1608508800.json')
				if os.path.exists(fileName) == True:
					try:
						with open(fileName, "rb") as dataFP:
							fileDataTV = dataFP.read()
							dataFP.close()
							if len(fileDataTV) > 0:
								# print("fileDataTV-->1042 ", fileDataTV)
								# ('fileDataTV-->1042 ', '{"fp": 2700000, "201": 1608528419, "202": 7202, "ft": "10122112292168-2005-1608508800", "fv": 20, "dhi": 107449, "dlo": 95776, "43": 1, "34": 2, "oi": 107244}')
								#sys.exit() ## For testing comment it in ** LIVE **

								retPrevVal = getPrevMinVal(None, fileDataTV, memcToken_RT, printFlag = printFlag)
								# print("retPrevVal--> ", retPrevVal)
								# ('retPrevVal--> ', {100: 1, 101: '', 102: {'fp': 4975000, 'ft': '10122112292166-2005-1608508800', 'fv': 100, 'oi': 17837, 'dhi': 17837, 'dlo': 17249}})

								if retPrevVal[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
									tokenMinDict = {}
									logErr_inst.LogError(None, "%s Getting from file failed. Error:%s"%(fyCmnDef.ERROR_setOiToThread, retPrevVal[fyCmnDef.K_ERR_MSG]), printFlag)
								else:
									tokenMinDict = retPrevVal[fyCmnDef.K_FUN_DATA]

								if debugFlag == fyCmnDef.DEBUG_TIME: ## To Debug
									print "1.2:",time.time() - pointA
							else:
								tokenMinDict = {} ## Empty file
					except Exception,e:
						exc_type, exc_obj, exc_tb = sys.exc_info()
						logErr_inst.LogError(None, "%s Line:%s. Exception for token:%s while getting from file system. Except:%s"%(fyCmnDef.ERROR_setOiToThread, exc_tb.tb_lineno, eachToken, str(e)), printFlag)
				else:
					tokenMinDict = {} ## File does not exist

				## Try to get the token details from cache if there are no details locally present.
				if len(tokenMinDict) == 0:
					## This will happen only when there in no data in program memory and no data in file system. This will try to get the data from the cache system.
					if nocache == False: ## Only is it is specified 
						try:
							cacheVal = cacheConn.get(memcToken_RT)
							if cacheVal != None:
								## sys.exit() ## This is for testing comment it in ** LIVE **
								retPrevVal = getPrevMinVal(None, cacheVal, memcToken_RT, printFlag = printFlag)
								if retPrevVal[fyCmnDef.K_FUNCT_STAT] != fyCmnDef.V_FUNCT_SUCCESS_1:
									tokenMinDict = {}
									logErr_inst.LogError(None, "%s Getting from cached failed. Error:%s"%(fyCmnDef.ERROR_setOiToThread, retPrevVal[fyCmnDef.K_ERR_MSG]), printFlag)
								else:
									tokenMinDict = retPrevVal[fyCmnDef.K_FUN_DATA]
						except Exception,e:
							exc_type, exc_obj, exc_tb = sys.exc_info()
							logErr_inst.LogError(None, "%s Line:%s. Exception for token:%s while getting cache val. Except:%s"%(fyCmnDef.ERROR_setOiToThread, exc_tb.tb_lineno, eachToken, str(e)), printFlag)

			if debugFlag == fyCmnDef.DEBUG_TIME:
				print "1.3:",time.time() - pointA
			#print("tokenMinDict--> ", tokenMinDict)
			if len(tokenMinDict) > 0:
				dictKeys = tokenMinDict.keys()
			# if len(inputDict) > 0:
			# 	dictKeys = inputDict.keys()
				#dictKeys  = dictKeys1.keys()
				# print("inputDict--> ", inputDict)
				# ('inputDict--> ', {'10128001012172': {'fp': 375000, 34: 2, 'ft': '10128001012172-2005-1608508800', 'oi': 54718, 'fv': 8, 'dhi': 54718, 201: 1608528409, 202: 7202, 43: 1, 'dlo': 47299}})
				if fyMemC.K_MEMC_OI_TOKEN in dictKeys and fyMemC.K_MEMC_OI_FILLP in dictKeys and fyMemC.K_MEMC_OI_FILLVOL in dictKeys and fyMemC.K_MEMC_OI_DAYHI in dictKeys and fyMemC.K_MEMC_OI_DAYLO in dictKeys:
					## all the required fields are present
					# currentCandleIndex = -1 ## Do not use zero
					#pdb.set_trace()
					if debugFlag == fyCmnDef.DEBUG_TIME:
						print "1.4:",time.time()-pointA

					# currentMinFlag = -1
					# # print "tokenMinDict[fyMemC.K_MEMC_TV_TIME]:", tokenMinDict[fyMemC.K_MEMC_TV_TIME]
					# if   tokenMinDict[fyMemC.K_MEMC_TV_TIME] == curMinTS:
					# 	currentMinFlag 	= 1
					# elif tokenMinDict[fyMemC.K_MEMC_TV_TIME] < curMinTS:
					# 	currentMinFlag = -1
					# else:
					# 	currentMinFlag = -1
					if debugFlag == fyCmnDef.DEBUG_TIME:
						print "1.6:",time.time() - pointA

					tokenMinDict[fyMemC.K_MEMC_OI_TOKEN] 	= memcToken_RT
					tokenMinDict[fyMemC.K_MEMC_OI_FILLP] 	= inputDict[eachToken][fyMemC.K_MEMC_OI_FILLP]
					tokenMinDict[fyMemC.K_MEMC_OI_FILLVOL] 	= inputDict[eachToken][fyMemC.K_MEMC_OI_FILLVOL]
					tokenMinDict[fyMemC.K_MEMC_OI] 			= inputDict[eachToken][fyMemC.K_MEMC_OI]
					tokenMinDict[fyMemC.K_MEMC_OI_DAYHI] 	= inputDict[eachToken][fyMemC.K_MEMC_OI_DAYHI]
					tokenMinDict[fyMemC.K_MEMC_OI_DAYLO] 	= inputDict[eachToken][fyMemC.K_MEMC_OI_DAYLO]
					tokenMinDict[fyCmnDef.K_TRADIN_STAT] 	= inputDict[eachToken][fyCmnDef.K_TRADIN_STAT]
					tokenMinDict[fyMemC.K_MEMC_LTQ] 	= inputDict[eachToken][fyMemC.K_MEMC_LTQ]
					tokenMinDict[fyCmnDef.K_BCH_TS] 	= inputDict[eachToken][fyCmnDef.K_BCH_TS]

					if inputDict[eachToken][fyMemC.K_MEMC_OI_Prev]:
						tokenMinDict[fyMemC.K_MEMC_OI_Change] = round(float(inputDict[eachToken][fyMemC.K_MEMC_OI]) - float(inputDict[eachToken][fyMemC.K_MEMC_OI_Prev]), roundoff)


					if setDelayedData and tempTvTime == curMinTS:
						
						# None ## Comment this line in ** LIVE **
						if SetGlobalVars.global_minSetFlag == [fyCmnDef.MKT_F_NORMAL_OPEN, fyCmnDef.MKT_F_PARTIAL]:
							#print("Inside 7202 minQueue")
							minQueue.put([tempTvTime, {eachToken: tokenMinDict}])
							minEventTh.set()## Commented for testing 2018-01-16
					# print("tokenMinDict ", tokenMinDict)
					# ('tokenMinDict ', {'fp': 737700000, 'ch': 4903203.0, 'ft': '10128001011487-2005-1608508800', 'fv': 7, 201: 1608528529, 202: 7202, 34: 2, 'pv': '0.0', 'dhi': 4910452, 'oi': 4903203, 43: 1, 'dlo': 4867415})
				else:
					## Special case we need to take care of this. TODO: Yet to be implemented.
					logErr_inst.LogError(None, "%sImproper JSON value found in memory for token:%s"%(fyCmnDef.ERROR_setOiToThread, eachToken), printFlag)
					## There should be someone stop setting to memcache if this the case ##continue
			else:
				## First tick of the day # print "new day val"
				tokenMinDict =  {
									tokenMinDict[fyMemC.K_MEMC_OI_TOKEN] 	: inputDict[eachToken][fyCmnDef.K_TOKEN_OI],
									tokenMinDict[fyMemC.K_MEMC_OI_FILLP] 	: inputDict[eachToken][fyCmnDef.K_FILLP_OI],
									tokenMinDict[fyMemC.K_MEMC_OI_FILLVOL] 	: inputDict[eachToken][fyCmnDef.K_FILLVOL_OI],
									tokenMinDict[fyMemC.K_MEMC_OI] 			: inputDict[eachToken][fyCmnDef.K_OI],
									tokenMinDict[fyMemC.K_MEMC_OI_DAYHI] 	: inputDict[eachToken][fyCmnDef.K_DAYHI_OI],
									tokenMinDict[fyMemC.K_MEMC_OI_DAYLO] 	: inputDict[eachToken][fyCmnDef.K_DAYLO_OI],
									tokenMinDict[fyCmnDef.K_TRADIN_STAT] 	: inputDict[eachToken][fyCmnDef.K_TRADIN_STAT],
									tokenMinDict[fyMemC.K_MEMC_LTQ] 	    : inputDict[eachToken][fyMemC.K_MEMC_LTQ],
									tokenMinDict[fyCmnDef.K_BCH_TS] 		:inputDict[eachToken][fyCmnDef.K_BCH_TS]
									# tokenMinDict[fyMemC.K_MEMC_Change_OI]   : round((inputDict[eachToken][fyMemC.K_MEMC_OI] - lastOi), roundoff)
								}
				if inputDict[eachToken][fyMemC.K_MEMC_OI_Prev]:
					tokenMinDict[fyMemC.K_MEMC_OI_Change] = round(float(inputDict[eachToken][fyMemC.K_MEMC_OI]) - float(inputDict[eachToken][fyMemC.K_MEMC_OI_Prev]), roundoff)

			inputDict[eachToken]		= tokenMinDict

			if SetGlobalVars.global_minSetFlag == fyCmnDef.MKT_F_NORMAL_OPEN:
				curMinValDict[eachToken] 	= tokenMinDict
			elif SetGlobalVars.global_minSetFlag == fyCmnDef.MKT_F_PARTIAL:
				if eachToken in exceptTokenDict:
					# print "after market except token min push:%s"%(eachToken)
					curMinValDict[eachToken] = tokenMinDict
				else:
					## If its partially traded and the token is not there in the exception tokens then drop it
					# print "***** token %s is not partially traded.****"%(eachToken)
					None
			else: ## New addition Ajay 2018-04-10
				## If its not market open or partially traded do not set the minute data.
				None
			if int(inputDict[eachToken][fyCmnDef.K_BCH_PACKT_CODE]) == int(nseConf.NSE_T_CODE_7202):
				if debugFlag == fyCmnDef.DEBUG_TIME:
					print "1.14:",time.time()-pointA
				#print("Inside 1128")
				# if global_minSetFlag in [fyCmnDef.MKT_F_NORMAL_OPEN, fyCmnDef.MKT_F_PARTIAL]
				if SetGlobalVars.global_minSetFlag in [fyCmnDef.MKT_F_PARTIAL, fyCmnDef.MKT_F_CLOSED]:
					## Verification of trading status has been added.
					getPrevClose = False ## New addition Ajay 2018-04-10
					if SetGlobalVars.global_minSetFlag == fyCmnDef.MKT_F_CLOSED: 
						getPrevClose = True
					elif SetGlobalVars.global_minSetFlag == fyCmnDef.MKT_F_PARTIAL and eachToken not in exceptTokenDict:
						getPrevClose = True
					if getPrevClose == True: 
						if str(inputDict[eachToken][fyCmnDef.K_TRADIN_STAT]) in nseConf.NSE_P_TRADIN_STAT_OPEN:
							prevMemcVal = cacheConn.get(str(memcToken_RT))
							if prevMemcVal == None:
								## This may happen if the script has not traded at all for this day.
								## This did happen around 6:50 AM IST 
								logErr_inst.LogError(None, "%s. After market memc get failed for: %s. Possible reason script not traded today."%(fyCmnDef.ERROR_setOiToThread, memcToken_RT), printFlag)
							else:
								try:
									if not isinstance(prevMemcVal,dict):
										prevMemcVal = json.loads(prevMemcVal)
									inputDict[eachToken][fyCmnDef.K_OI_CLOSING_P] = prevMemcVal[str(fyMemC.K_MEMC_Change_OI)]
								except Exception,e:
									exc_type, exc_obj, exc_tb = sys.exc_info()
									errMsg = "%s Line:%s. After market JSON load failed for:%s . Except:%s"%(fyCmnDef.ERROR_setOiToThread, exc_tb.tb_lineno, memcToken_RT, str(e))
									logErr_inst.LogError(None, errMsg, printFlag)
								finally:
									None

						else:
							None ## This will happen during preopen session 
				if debugFlag == fyCmnDef.DEBUG_TIME:
					print "1.15:",time.time()-pointA
				# lastOi = 0.0
				# if eachToken in tokenPrevValDict:
				# 	if fyCmnDef.K_OI_CLOSING_P in tokenPrevValDict[eachToken]:
				# 		lastOi = tokenPrevValDict[eachToken][fyCmnDef.K_OI_CLOSING_P]
				# 		print("lastOi--> ", lastOi)
				# 	if lastOi == None:
				# 		logErr_inst.LogError(None, "%s lastOi value is none:%s"%(fyCmnDef.ERROR_setOiToThread, eachToken), printFlag)

				memcValDict = {}
				try:
					if inputDict[eachToken][fyMemC.K_MEMC_OI_Prev]:
						memcValDict[fyMemC.K_MEMC_Change_OI] = round(float(inputDict[eachToken][fyMemC.K_MEMC_OI]) - float(inputDict[eachToken][fyMemC.K_MEMC_OI_Prev]), roundoff)

					memcValDict[fyMemC.K_OI_RT_TOKEN] 	 = inputDict[eachToken][fyMemC.K_MEMC_OI_TOKEN]
					memcValDict[fyMemC.K_OI_RT_FILLP] 	 = inputDict[eachToken][fyMemC.K_MEMC_OI_FILLP]
					memcValDict[fyMemC.K_OI_RT_FILLVOL]  = inputDict[eachToken][fyMemC.K_MEMC_OI_FILLVOL]
					memcValDict[fyMemC.K_OI_RT_OI] 		 = inputDict[eachToken][fyMemC.K_MEMC_OI]
					memcValDict[fyMemC.K_OI_RT_DAY_HI_OI]= inputDict[eachToken][fyMemC.K_MEMC_OI_DAYHI]
					memcValDict[fyMemC.K_OI_RT_DAY_LO_OI]= inputDict[eachToken][fyMemC.K_MEMC_OI_DAYLO]
					memcValDict[fyCmnDef.K_TRADIN_STAT]  = inputDict[eachToken][fyCmnDef.K_TRADIN_STAT]
					memcValDict[fyCmnDef.K_BCH_TS]       = inputDict[eachToken][fyCmnDef.K_BCH_TS]

				except Exception,e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					logErr_inst.LogError(None, "%s Line:%s. Excepton adding OHLCV to RT token. Except:%s"%(fyCmnDef.ERROR_setOiToThread, exc_tb.tb_lineno, str(e)), printFlag)

				cacheQueue.put({memcToken_RT:memcValDict}) ## Commented for testing
				# print("memcValDict--> ", memcValDict)
				# ('memcValDict--> ', {34: 2, 201: 1608528689, 810: '10122101275521-2005-1608508800', 811: 7400000, 812: 23, 813: 31469, 814: 31469, 815: 29937, 816: -331646.0})
				if nocache == False:
					cacheConn.set(memcToken_RT , json.dumps(inputDict[eachToken]), ex=86400)

				if noSend == False:
					##Code for streaming server 
					sendDict = memcValDict.copy()
					sendDict[fyMemC.K_MEMC_TS_BCH] 		= inputDict[eachToken][fyCmnDef.K_BCH_TS]
					sendDict[fyMemC.K_MEMC_TRANS_CODE] 	= inputDict[eachToken][fyCmnDef.K_BCH_PACKT_CODE]
					sendDict['tradeStat']				= SetGlobalVars.global_minSetFlag

					sendPktQ.put({eachToken:sendDict})
					print("sendDict--> ", sendDict)
					# ('sendDict--> ', {34: 2, 227: 7202, 226: 1608528392, 201: 1608528392, 810: '10122112292169-2005-1608508800', 811: 350000, 812: 15, 813: 129683, 814: 132555, 815: 109869, 816: 129683.0, 'tradeStat': 7})
				if debugFlag == fyCmnDef.DEBUG_TIME:
					print "1.16:",time.time() - pointA
		
			else:
				logErr_inst.LogError(None, "%s Unknown transaction code: '%s'"%(fyCmnDef.ERROR_setOiToThread, inputDict[eachToken][fyCmnDef.K_BCH_PACKT_CODE]), printFlag)
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logErr_inst.LogError(None, "%s Line:%s. Unknow exception. Except:%s"%(fyCmnDef.ERROR_setOiToThread, exc_tb.tb_lineno, str(e)), printFlag)
	finally:
		None


