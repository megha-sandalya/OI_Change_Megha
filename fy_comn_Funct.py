"""
Author 		: Ajay A U [ajay@fyers.in]
Version 	: 2.0
Copyright 	: Fyers Securities
Web			: fyers.in
"""
#!/usr/bin/python
import os
import sys
import time
import datetime
import pytz
import json
import MySQLdb
import pdb

# sys.path.append("../")
import fy_NSE_Config as NSEConf
# from fyComn_def import EXCHANGE_NAME_NSE, SEG_NAME_CM_LIVE, SEG_NAME_FO_LIVE,SEG_NAME_CD_LIVE, SEG_NAME_CM_TEST, SEG_NAME_FO_TEST, SEG_NAME_CD_TEST, LOG_FILE_PATH

import MCX_config as MCXConf
import fy_comn_def as cDef
import fy_connect_defines as connDef

def dbConnect(dbType=0, exchange=0, segment=0, readOnly=1):
	"""
	dbType == 1 => eodData
	dbType == 2 => 1minData
	dbType == 3 => tradingApi
	readOnly == 1 => Connect to read-replica
	readOnly == 0 => Connect to normal DB
	"""
	# print "dbConnect() : Connected"
	try:
		if dbType == 0:
			return {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: [None, None], cDef.K_ERR_MSG:"%s Invalid dbType:%s."%(cDef.ERROR_dbConnect, dbType)}

		dbName = ''

		if dbType == 1:
			if exchange == cDef.EXCHANGE_CODE_NSE:
				if segment == cDef.SEG_CODE_CM_LIVE:
					# dbName = "fyers_eod_data_nse_cm_v1" ## Name changed while migrating
					dbName = connDef.DB_NAME_NSE_CM_EOD#"fyers_eod_data_nse_cm_v2"
				elif segment == cDef.SEG_CODE_FO_LIVE:
					dbName = connDef.DB_NAME_NSE_FO_EOD#"fyers_eod_data_nse_fo_v1"
				elif segment == cDef.SEG_CODE_CD_LIVE:
					dbName = connDef.DB_NAME_NSE_CD_EOD#"fyers_eod_data_nse_cd_v1"
				else:
					return {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: [None, None], cDef.K_ERR_MSG:"%s Unknown segment '%s' for dbType:%s readOnly:%s."%(cDef.ERROR_dbConnect, segment, dbType, readOnly)}
			else:
				return {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: [None, None], cDef.K_ERR_MSG:"%s Unknown exchange '%s' for dbType:%s readOnly:%s"%(cDef.ERROR_dbConnect, exchange, dbType, readOnly)}
		elif dbType == 2:
			if exchange == cDef.EXCHANGE_CODE_NSE:
				if segment == cDef.SEG_CODE_CM_LIVE:
					# dbName = "fyers_1min_data_nse_cm_v1" ## Name changed while migrating
					dbName = connDef.DB_NAME_NSE_CM_1MIN#"fyers_1min_data_nse_cm_v4"
				elif segment == cDef.SEG_CODE_FO_LIVE:
					dbName = connDef.DB_NAME_NSE_FO_1MIN#"fyers_1min_data_nse_fo_v1"
				elif segment == cDef.SEG_CODE_CD_LIVE:
					dbName = connDef.DB_NAME_NSE_CD_1MIN#"fyers_1min_data_nse_cd_v1"
				else:
					return {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: [None, None], cDef.K_ERR_MSG:"%s Unknown segment '%s' for dbType:%s readOnly:%s"%(cDef.ERROR_dbConnect, segment, dbType,readOnly)}
			else:
				return {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: [None, None], cDef.K_ERR_MSG:"%s Unknown exchange '%s' for dbType:%s readOnly:%s"%(cDef.ERROR_dbConnect, exchange, dbType, readOnly)}
		elif dbType == 3:
			dbName = connDef.DB_NAME_TRADING_BRIDGE##"fyers_trading_bridge"
		else:
			return {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: [None, None], cDef.K_ERR_MSG:"%s Unknown dbType '%s' readOnly:%s."%(cDef.ERROR_dbConnect, dbType, readOnly)}

		connection = ''
		if readOnly == 1:
			connection 	= connDef.DB_END_POINT_READER
		else:
			connection 	= connDef.DB_ENDPOINT_WRITER
		connectionPort 	= connDef.DB_PORT #3306
		uName 			= connDef.DB_UNAME #""
		passwd 			= connDef.DB_PASS #""

		# print "connection:%s, uName:%s, passwd:%s"%(connection, uName, passwd)
		try:
			db = MySQLdb.connect(host=connection, user=uName, passwd=passwd, db=dbName, port=connectionPort)
			cursor = db.cursor()
			# print "Successfully connected to the %s"%(dbName)
			return {cDef.K_FUNCT_STAT:cDef.V_FUNCT_SUCCESS_1, cDef.K_FUN_DATA: [db, cursor], cDef.K_ERR_MSG:"Success."%()}
		except Exception, e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			return {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: [None, None], cDef.K_ERR_MSG:"%s Line:%s. Unknow exception while connectiong to DB. Except:%s"%(cDef.ERROR_dbConnect, exc_tb.tb_lineno, str(e))}
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		return {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: [None, None], cDef.K_ERR_MSG:"%s Line:%s. Unknow exception. Except:%s"%(cDef.ERROR_dbConnect, exc_tb.tb_lineno, str(e))}

def getExSegCodeFromName(exchangeName, segmentName):
	"""
	[Function]  : 	This function should take exchange and segment name and return back number associated with them.
	[Input] 	: 	exchangeName 	-> NSE,     	MCX,	BSE 
				  	segmentName 	-> CM/FO/CD, 	COM,	CM/FO/CD
				  
	[Output]	: 	Dict {cDef.K_FUNCT_STAT: cDef.V_FUNCT_SUCCESS_1 ,cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: ''}
					cDef.K_FUNCT_STAT 	-> cDef.V_FUNCT_SUCCESS_1 / cDef.V_FUNCT_FAIL_N_1
					cDef.K_FUN_DATA 	-> Dict which contain exchange and segment codes mapped to give exchange and segment names.
					cDef.K_ERR_MSG		-> Error message
	"""
	returnDict = {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG:"ERR : %s Unknown error."%(cDef.LOG_getExSegCodeFromName)}
	
	try:
		exCode, segCode = 0, 0
		exchangeName 	= exchangeName.upper()
		segmentName 	= segmentName.upper()
		
		if exchangeName == cDef.EXCHANGE_NAME_NSE:
			exCode = cDef.EXCHANGE_CODE_NSE
			if 	 segmentName == cDef.SEG_NAME_CM_LIVE or segmentName == cDef.SEG_NAME_CM_TEST:
				segCode = cDef.SEG_CODE_CM_LIVE
			elif segmentName == cDef.SEG_NAME_FO_LIVE or segmentName == cDef.SEG_NAME_FO_TEST:
				segCode = cDef.SEG_CODE_FO_LIVE
			elif segmentName == cDef.SEG_NAME_CD_LIVE or segmentName == cDef.SEG_NAME_CD_TEST:
				segCode = cDef.SEG_CODE_CD_LIVE
			else:
				returnDict[cDef.K_ERR_MSG] = "ERR : %s Invalid segment: '%s' for exchange: '%s'"%(cDef.LOG_getExSegCodeFromName, segmentName, exchangeName)
		elif exchangeName == MCXConf.MCX_EXCHANGE_NAME:
			exCode = MCXConf.MCX_EXCHANGE_CODE
			if segmentName == MCXConf.SYM_SEGMENT_COM_NAME_LIVE or segmentName == MCXConf.SYM_SEGMENT_COM_NAME_TEST:
				segCode = MCXConf.SYM_SEGMENT_COM_CODE
			else:
				returnDict[cDef.K_ERR_MSG] = "ERR : %s Invalid segment: '%s' for exchange: '%s'"%(cDef.LOG_getExSegCodeFromName, segmentName, exchangeName)
				return returnDict
		elif exchangeName == cDef.EXCHANGE_NAME_BSE:
			exCode = cDef.EXCHANGE_CODE_BSE
			if 	 segmentName == cDef.SEG_NAME_CM_LIVE_BSE or segmentName == cDef.SEG_NAME_CM_TEST_BSE:
				segCode = cDef.SEG_CODE_CM_LIVE_BSE
			elif segmentName == cDef.SEG_NAME_FO_LIVE_BSE or segmentName == cDef.SEG_NAME_FO_TEST_BSE:
				segCode = cDef.SEG_CODE_FO_LIVE_BSE
			elif segmentName == cDef.SEG_NAME_CD_LIVE_BSE or segmentName == cDef.SEG_NAME_CD_TEST_BSE:
				segCode = cDef.SEG_CODE_CD_LIVE_BSE
			else:
				returnDict[cDef.K_ERR_MSG] = "ERR : %s Invalid segment: '%s' for exchange: '%s'"%(cDef.LOG_getExSegCodeFromName, segmentName, exchangeName)
		else:
			returnDict[cDef.K_ERR_MSG] = "ERR : %s Invalid exchange name: '%s'."%(cDef.LOG_getExSegCodeFromName, exchangeName)
			return returnDict
		# print "exCode:%s, segCode:%s"%(exCode, segCode) 	
		if exCode != 0 and segCode != 0:
			returnDict = {
						cDef.K_FUNCT_STAT: cDef.V_FUNCT_SUCCESS_1, 
						cDef.K_FUN_DATA: {exchangeName: exCode, segmentName: segCode}, 
						cDef.K_ERR_MSG:""
						}
		return returnDict
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		returnDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s Exception for segment: '%s' exchange: '%s'. Excpet:%s"%(cDef.LOG_getExSegCodeFromName, exc_tb.tb_lineno, segmentName, exchangeName, str(e))
	return returnDict

def getFyTokenDict(exchangeName, segmentName, exchangeType, segmentType):
	"""
	[Function]  : 	Gets the fyers token mapping with the exchange tokens.
	[Input] 	: 	exchangeName 	-> NSE,     	MCX,	BSE 
				  	segmentName 	-> CM/FO/CD, 	COM,	CM/FO/CD
	[Output]	:  	Dict {cDef.K_FUNCT_STAT: cDef.V_FUNCT_SUCCESS_1 ,cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: ''}
					cDef.K_FUNCT_STAT 	-> cDef.V_FUNCT_SUCCESS_1 / cDef.V_FUNCT_FAIL_N_1
					cDef.K_FUN_DATA 	-> Return dict which will contain exchange_token as key and fy_token as value. Return empty dict will indicate an error.
					cDef.K_ERR_MSG		-> Error message
	"""
	tokenDict 	= {}
	try:
		#pdb.set_trace()
		exchangeName, segmentName = exchangeName.upper(), segmentName.upper()
		returnDict = {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: tokenDict, cDef.K_ERR_MSG:"%s Unknown error."%(cDef.ERROR_getFyTokenDict)}
		retDbConn = dbConnect(dbType=3, readOnly=1)
		if retDbConn[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
			return retDbConn
		[db, cursor] = retDbConn[cDef.K_FUN_DATA]
		
		print "********************* trade status commented for testing *********************"
		#getTokensSQL = "SELECT FY_TOKEN, EX_TOKEN FROM `%s` WHERE EX=%s and EX_SEGMENT=%s and TRADE_STATUS= 1;"%(cDef.TBL_SYMBOL_MASTER, exchangeType, segmentType)
		#print("segmentName ",segmentName)
		if segmentName == 'CM' or segmentName == 'CMTEST':
			getTokensSQL = "SELECT FY_TOKEN, EX_TOKEN FROM `%s` WHERE EX=%s and EX_SEGMENT=%s and TRADE_STATUS= 1;"%(cDef.TBL_SYMBOL_MASTER, exchangeType, segmentType)
		elif segmentName == 'FO' or segmentName == 'CD' or segmentName == 'COM' or segmentName == 'FOTEST' or segmentName == 'CDTEST' or segmentName == 'COMTEST':
			getTokensSQL = "SELECT FY_TOKEN, EX_TOKEN, OI FROM `%s` WHERE EX=%s and EX_SEGMENT=%s and TRADE_STATUS= 1;"%(cDef.TBL_SYMBOL_MASTER, exchangeType, segmentType)
			#getTokensSQL = "SELECT FY_TOKEN, EX_TOKEN FROM `%s` WHERE EX=%s and EX_SEGMENT=%s and TRADE_STATUS= 1;"%(cDef.TBL_SYMBOL_MASTER, exchangeType, segmentType)

		# getTokensSQL = "SELECT FY_TOKEN, EX_TOKEN FROM `%s` WHERE EX=%s and EX_SEGMENT=%s ;"%(cDef.TBL_SYMBOL_MASTER, exchangeType, segmentType)
		sqlRet = ()
		try:
			cursor.execute(getTokensSQL)
			sqlRet = cursor.fetchall()
		except Exception,e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			returnDict[cDef.K_ERR_MSG] = "%s Line:%s. SQL failed. Except:%s"%(cDef.ERROR_getFyTokenDict, exc_tb.tb_lineno, str(e))
			return returnDict
		finally:
			db.close()
		if len(sqlRet) <= 0:
			returnDict[cDef.K_ERR_MSG] = "%s SQL query return is empty"%(cDef.ERROR_getFyTokenDict)
			# if segmentName.endswith("TEST"):
			# 	print "%s appending dummy tokens"%(cDef.ERROR_getFyTokenDict)
			# 	for i in range(200):
			# 		tokenDict[str(i)] = str(i)
			# 	return {cDef.K_FUNCT_STAT: cDef.V_FUNCT_SUCCESS_1, cDef.K_FUN_DATA: tokenDict, cDef.K_ERR_MSG:"errStr" }
			return returnDict
		# print("sqlRet-->198 ", sqlRet)
		# ('10128001014880', 4880L, 0.0)
		errStr = ""
		for eachItem in sqlRet:
			try:
				tokenDict[str(eachItem[1])] = str(eachItem[0])
				# OI data
				if len(eachItem) == 3:
					tokenDict[str(eachItem[1])+'_oi'] = str(eachItem[2])

			except Exception,e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				errStr +="%s %s"%(cDef.ERROR_getFyTokenDict, str(e))
			# numbers
		return {cDef.K_FUNCT_STAT: cDef.V_FUNCT_SUCCESS_1, cDef.K_FUN_DATA: tokenDict, cDef.K_ERR_MSG:errStr }
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		returnDict = {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: tokenDict, cDef.K_ERR_MSG:"%s Line:%s Unknown exception:%s"%(cDef.ERROR_getFyTokenDict, exc_tb.tb_lineno, str(e))}
	return returnDict

def newDayTrigger(logErr_inst, inputExchange, inputSegment, printFlag = False, debugFlag =0):
	"""
	[Function] 	: 	Function create new day files.
					Create new temp directory.
					Create new log file.
					Get new tokens.
	[Input]		: 	logErr_inst 	-> log file pointer
				  	inputExchange 	-> NSE,     	MCX,	BSE 
				  	inputSegment 	-> CM/FO/CD, 	COM,	CM/FO/CD
	[Output]	: 	Dict {cDef.K_FUNCT_STAT: cDef.V_FUNCT_SUCCESS_1 ,cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: ''}
					cDef.K_FUNCT_STAT 	-> cDef.V_FUNCT_SUCCESS_1 / cDef.V_FUNCT_FAIL_N_1
					cDef.K_FUN_DATA 	-> Dict contain the information
					cDef.K_ERR_MSG		-> Error message
	"""
	newLogFilePtr = None
	try:
		dateTimeNow 	= datetime.datetime.now()
		# if debugFlag == 1: ## This is for testing comment it in  ** LIVE **
		# 	dateTimeNow 			= dateTimeNow.replace(day=15)
		# 	print "dateTimeNow:",dateTimeNow
		dateStr 		= dateTimeNow.strftime('%Y%m%d')

		inputExchange, inputSegment = inputExchange.upper(), inputSegment.upper()
		# print cDef.ERROR_newDayTrigger, inputExchange, segmentName
		retFyCodes = getExSegCodeFromName(inputExchange, inputSegment)
		if retFyCodes[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
			return retFyCodes
		if cDef.K_FUN_DATA not in retFyCodes:
			returnDict[cDef.K_ERR_MSG] = "%s 1.Inconsisty finding exchange segment code."%(cDef.ERROR_newDayTrigger)
			return returnDict
		if inputExchange not in retFyCodes[cDef.K_FUN_DATA] or inputSegment not in retFyCodes[cDef.K_FUN_DATA]:
			returnDict[cDef.K_ERR_MSG] = "%s 2.Inconsisty finding exchange segment code."%(cDef.ERROR_newDayTrigger)
			return returnDict
		
		exCode, segCode = retFyCodes[cDef.K_FUN_DATA][inputExchange], retFyCodes[cDef.K_FUN_DATA][inputSegment]

		##New code MCX 20181019 - Palash
		if inputExchange == cDef.EXCHANGE_NAME_NSE:
			logDirPath 	        = cDef.LOG_FILE_PATH_EC2_RS_NSE + inputSegment + '/'
			retLogDir 	        = createDirectory(logDirPath)
			tempDirectoryPath 	= cDef.TEMP_DATA_FILE_PATH + inputSegment + '/' + dateStr + '/'
			retCreateDir 		= createDirectory(tempDirectoryPath)
			msgDirPath          = cDef.TEMP_DATA_FILE_PATH + cDef.MSG_FILE_PATH + inputSegment + '/' + dateStr + '/'
			retMsgDir           = createDirectory(msgDirPath)
		elif inputExchange == MCXConf.MCX_EXCHANGE_NAME: ## Change Ajay 2019-01-16
			logDirPath 	        = cDef.LOG_FILE_PATH_EC2_RS_MCX + inputSegment + '/'
			retLogDir 	        = createDirectory(logDirPath)
			tempDirectoryPath 	= cDef.TEMP_DATA_FILE_PATH_MCX + inputSegment + '/' + dateStr + '/'
			retCreateDir 		= createDirectory(tempDirectoryPath)
			msgDirPath          = cDef.TEMP_DATA_FILE_PATH_MCX + cDef.MSG_FILE_PATH + inputSegment + '/' + dateStr + '/'
			retMsgDir           = createDirectory(msgDirPath)
		##END
		## ************** Change Ajay 2019-01-16 **************
		elif inputExchange == cDef.EXCHANGE_NAME_BSE:
			logDirPath 	        = cDef.LOG_FILE_PATH_EC2_RS_BSE + inputSegment + '/'
			retLogDir 	        = createDirectory(logDirPath)
			tempDirectoryPath 	= cDef.TEMP_DATA_FILE_PATH_BSE + inputSegment + '/' + dateStr + '/'
			retCreateDir 		= createDirectory(tempDirectoryPath)
			msgDirPath          = cDef.TEMP_DATA_FILE_PATH_BSE + cDef.MSG_FILE_PATH + inputSegment + '/' + dateStr + '/'
			retMsgDir           = createDirectory(msgDirPath)
		else:
			errMsg = "%s Invalid input exchange:%s"%(cDef.ERROR_newDayTrigger, inputExchange)
			logErr_inst.LogError(None, errMsg, printFlag=printFlag)
			return {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1 ,cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: errMsg}
		## ************** Change Ajay 2019-01-16 **************

		if retLogDir[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
			print "%s Cannot create log file directory: %s"%(cDef.ERROR_newDayTrigger, logDirPath)
		else:
			try:
				newLogFilePtr = open(logDirPath + dateStr + cDef.LOG_FILE_EXT, "ab+", buffering = 0)
				newLogFilePtr.write("***************************************************************\n") 
			except Exception,e:
				newLogFilePtr = None
				exc_type, exc_obj, exc_tb = sys.exc_info()
				errMsg = "%s Line:%s. Cannot create log file. Except:%s"%(cDef.ERROR_newDayTrigger, exc_tb.tb_lineno, str(e))
				logErr_inst.LogError(None, errMsg, printFlag=printFlag)

		logErr_inst.LogError(newLogFilePtr, "Log file %s created successfully."%(logDirPath + dateStr + cDef.LOG_FILE_EXT), printFlag=printFlag)
			
		if retCreateDir[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
			tempDirectoryPath = ""
			errMsg = "%s Creating temp dir %s failed. Error:%s"%(cDef.ERROR_newDayTrigger, tempDirectoryPath, retCreateDir[cDef.K_ERR_MSG])
			logErr_inst.LogError(newLogFilePtr, errMsg, printFlag=printFlag)
		else:
			logErr_inst.LogError(newLogFilePtr, "Success creating temp dir:%s"%(tempDirectoryPath), printFlag=printFlag)

		##New Code MCX 20181019 - PALASH
		if retMsgDir[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
			msgDirPath = ""
			errMsg = "%s Creating exchange message dir %s failed. Error:%s"%(cDef.ERROR_newDayTrigger, msgDirPath, retMsgDir[cDef.K_ERR_MSG])
			logErr_inst.LogError(newLogFilePtr, errMsg, printFlag=printFlag)
		else:
			logErr_inst.LogError(newLogFilePtr, "Success creating exchange message dir:%s"%(msgDirPath), printFlag=printFlag)

		## Get tokens from DB
		fyTokenDict = {}
		ret_fyTokenDict = getFyTokenDict(inputExchange, inputSegment, exCode, segCode)## Change Ajay 2019-01-16
		#print("ret_fyTokenDict--> ", ret_fyTokenDict)
		if ret_fyTokenDict[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
			logErr_inst.LogError(newLogFilePtr, "%s Getting token failed with error:%s"%(cDef.ERROR_newDayTrigger, ret_fyTokenDict[cDef.K_ERR_MSG]), printFlag=printFlag)
		else:
			fyTokenDict = ret_fyTokenDict[cDef.K_FUN_DATA]
			logErr_inst.LogError(newLogFilePtr, "Number of tokens loaded from DB:%s"%(len(fyTokenDict)), printFlag=printFlag)
			if len(ret_fyTokenDict[cDef.K_ERR_MSG]) > 0:
				logErr_inst.LogError(newLogFilePtr, "%s getFyTokenDict error mess:%s"%(cDef.ERROR_newDayTrigger, ret_fyTokenDict[cDef.K_ERR_MSG]), printFlag=printFlag) ## new addition Ajay 2018-04-10
		#print("ret_fyTokenDict--> ", fyTokenDict)
		#print all numbers
		## New addition Ajay 2018-04-05
		## Get Previous close price for index tokens
		tokenPrevValDict = {}
		ret_prevVal = getPreviousValforTokens(inputExchange, inputSegment, exCode, segCode)## Change Ajay 2019-01-16

		if ret_prevVal[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
			logErr_inst.LogError(newLogFilePtr, "%s Getting exception tokens failed with error:%s"%(cDef.ERROR_newDayTrigger, ret_prevVal[cDef.K_ERR_MSG]), printFlag=printFlag)
		else:
			tokenPrevValDict = ret_prevVal[cDef.K_FUN_DATA]
			logErr_inst.LogError(newLogFilePtr, "Number of prev val tokens loaded from DB:%s"%(len(tokenPrevValDict)), printFlag=printFlag)
			if len(ret_prevVal[cDef.K_ERR_MSG]) > 0:
				logErr_inst.LogError(newLogFilePtr, "%s::%s"%(cDef.ERROR_newDayTrigger, ret_prevVal[cDef.K_ERR_MSG]), printFlag=printFlag)

		## New change Ajay 2018-04-10. To get the exception tokens which will be traded after market hours.
		## Get exception tokens from DB
		exceptTokenDict = {}
		ret_exceptToken = getExceptionTokens(inputExchange, inputSegment, exCode, segCode)## Change Ajay 2019-01-16

		if ret_exceptToken[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
			logErr_inst.LogError(newLogFilePtr, "%s Getting exception tokens failed with error:%s"%(cDef.ERROR_newDayTrigger, ret_exceptToken[cDef.K_ERR_MSG]), printFlag=printFlag)
		else:
			exceptTokenDict = ret_exceptToken[cDef.K_FUN_DATA]
			logErr_inst.LogError(newLogFilePtr, "Number of exception tokens loaded from DB:%s"%(len(exceptTokenDict)), printFlag=printFlag)
			if len(ret_exceptToken[cDef.K_ERR_MSG]) > 0:
				logErr_inst.LogError(newLogFilePtr, "%s::%s"%(cDef.ERROR_newDayTrigger, ret_exceptToken[cDef.K_ERR_MSG]), printFlag=printFlag)
		#print("exceptTokenDict--> ", exceptTokenDict)
		dataDict = 	{
						"logFilePtr"		: newLogFilePtr,
						"fyTokenDict"		: fyTokenDict,
						"exceptTokenDict"	: exceptTokenDict,
						"tokenPrevValDict"	: tokenPrevValDict,
						"tempDirectoryPath"	: tempDirectoryPath,
						"msgDirPath"        : msgDirPath
					}
		return {cDef.K_FUNCT_STAT: cDef.V_FUNCT_SUCCESS_1 ,cDef.K_FUN_DATA: dataDict, cDef.K_ERR_MSG: ''}
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Unknow exception. Except:%s"%(cDef.ERROR_newDayTrigger, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(newLogFilePtr, errMsg, printFlag = printFlag)
		return {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1 ,cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: errMsg}
	finally:
		None
	return {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1 ,cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "%s Unknown error"%(cDef.ERROR_newDayTrigger)}

def printProgUsage(progName):
	print "Usage : 'python %s %s [%s/%s/%s/%s/%s/%s]' "%(progName, cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_CM_LIVE, cDef.SEG_NAME_FO_LIVE, cDef.SEG_NAME_CD_LIVE, cDef.SEG_NAME_CM_TEST, cDef.SEG_NAME_FO_TEST, cDef.SEG_NAME_CD_TEST)

class FYLog(object):
	logFilePtr  = None ## This will have a file pointer which will be used to write logs 
	@classmethod
	def changeLogFP(cls, logFilePtr):
		cls.logFilePtr 	= logFilePtr
	
	def LogError(self, fileObj, writeString, printFlag = False): ## printFlag is made true for testing in prod make this false
		if fileObj == None:
			fileObj = FYLog.logFilePtr
		try:
			if printFlag == True:
				print writeString
			fileObj.write(str(time.time())+" : "+str(writeString)+'\n')
		except Exception,e:
			print "ERR : writeToErrFile() Exception:%s"%(str(e))

def createDirectory(directoryPath):
	returnDict = {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_ERR_MSG: "%s Unknown error"%(cDef.ERROR_createDirectory), cDef.K_FUN_DATA:''}
	try:
		if not os.path.exists(directoryPath):
			print "creating dir:", directoryPath
			os.makedirs(directoryPath)
			(returnDict[cDef.K_FUNCT_STAT], returnDict[cDef.K_ERR_MSG], returnDict[cDef.K_FUN_DATA]) = (cDef.V_FUNCT_SUCCESS_1, "Successfully created %s"%(directoryPath), directoryPath)
		else:
			(returnDict[cDef.K_FUNCT_STAT], returnDict[cDef.K_ERR_MSG], returnDict[cDef.K_FUN_DATA]) = (cDef.V_FUNCT_SUCCESS_1, "Dir %s already exists."%(directoryPath), directoryPath)
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		(returnDict[cDef.K_FUNCT_STAT], returnDict[cDef.K_ERR_MSG], returnDict[cDef.K_FUN_DATA]) = (cDef.V_FUNCT_FAIL_N_1, "%s Line:%s. Socket connection failed. Except:%s"%(cDef.ERROR_createDirectory, exc_tb.tb_lineno, str(e)), "") 
	finally:
		None
	return returnDict

## New Addition Ajay 2018-04-05
def getPreviousValforTokens(exchangeName, segmentName, exchangeType, segmentType):
	"""
	Note : Do not send input tokens as dictonary values this is causing problem if you run the function multiple times.
	
	[Function]  :	Get previous close values for the given exchange and segment tokens.
	
	[Input] 	: 	exchangeName 	-> NSE, MCX
				  	segmentName 	-> CM/FO/CD, COM/COMTEST
	[Output]	: 	Dict {cDef.K_FUNCT_STAT: cDef.V_FUNCT_SUCCESS_1 ,cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: ''}
					cDef.K_FUNCT_STAT 	-> cDef.V_FUNCT_SUCCESS_1 / cDef.V_FUNCT_FAIL_N_1
					cDef.K_FUN_DATA 	-> Dict contain the information
					cDef.K_ERR_MSG		-> Error message

	"""
	inputTokens = {}
	tokenDict 	= {}
	returnDict = {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: tokenDict, cDef.K_ERR_MSG:"%s Unknown error."%(cDef.ERROR_getPreviousValforTokens)}
	
	try:
		db, cursor = None, None
		nameTokenDict = {}
		if exchangeName == cDef.EXCHANGE_NAME_NSE and len(inputTokens) <= 0 and (segmentName == cDef.SEG_NAME_CM_LIVE or segmentName == cDef.SEG_NAME_CM_TEST):
			# print "here"
			# sys.exit()
			SQL_getIndexTokens = """SELECT FY_TOKEN,UNDERLYING_SYM FROM fyers_trading_bridge.`symbol_master` WHERE EX=10 and EX_SEGMENT=10 and EX_INST_TYPE=10;"""
			retDbConn = dbConnect(dbType=1, exchange=exchangeType, segment=segmentType, readOnly=1)
			if retDbConn[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
				return retDbConn
			[db, cursor] = retDbConn[cDef.K_FUN_DATA]
			try:
				cursor.execute(SQL_getIndexTokens)
				retSQLVal = cursor.fetchall()
				if len(retSQLVal) > 0:
					for eachEntry in retSQLVal:
						tokenName = eachEntry[1].replace(' ', '').lower() 
						nameTokenDict[tokenName] = int(eachEntry[0])
						if tokenName in cDef.FY_SYMBOL_MAPPING:
							inputTokens[cDef.FY_SYMBOL_MAPPING[tokenName]] = ''
						else:
							inputTokens[tokenName] = ''

			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				returnDict[cDef.K_ERR_MSG] = "%s Line:%s Failed to get index tokens.Except: %s"%(cDef.ERROR_getPreviousValforTokens, exc_tb.tb_lineno, str(e))

			## Cannot use this anymore. because of DB migration
			# inputTokens = NSEConf.FY_TOKEN_7207_DICT.values()
			# for eachKey in NSEConf.FY_TOKEN_7207_DICT.keys():
			# 	inputTokens[eachKey.replace(' ', '').lower()] = ''
			# print "inputTokens:", inputTokens
			# print "nameTokenDict:", nameTokenDict
			# sys.exit()
			# print NSEConf.FY_TOKEN_7207_DICT
		## ********** New Change Ajay 2019-01-16 **********
		#Commenting for testing
		if len(inputTokens) <= 0:
			returnDict[cDef.K_FUNCT_STAT] = cDef.V_FUNCT_SUCCESS_1
			returnDict[cDef.K_ERR_MSG] = "%s No tokens given for market:%s, segment:%s"%(cDef.ERROR_getPreviousValforTokens, exchangeType, segmentType)
			return returnDict

		if db == None or cursor == None:
			retDbConn = dbConnect(dbType=1, exchange=exchangeType, segment=segmentType, readOnly=1)
			if retDbConn[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
				return retDbConn
			[db, cursor] = retDbConn[cDef.K_FUN_DATA]

		errStr = ''
		for eachToken in inputTokens: 
			SQL_closeP = """SELECT round(CLOSE,2) FROM `%s` order by IDATE_TIMESTAMP desc limit 1;"""%(eachToken)
			# print "SQL_closeP:", SQL_closeP
			try:
				cursor.execute(SQL_closeP)
				sqlFetch = cursor.fetchall()
				if len(sqlFetch)> 0:
					# print sqlFetch[0][0]
					## This has to be changed.
					# tokenDict[sqlFetch[0][1]] = {cDef.K_CLOSING_P: sqlFetch[0][0]}
					if eachToken in nameTokenDict:
						tokenDict[nameTokenDict[eachToken]] = {cDef.K_CLOSING_P: sqlFetch[0][0]}
					else:
						errStr += "%s Fyers token mapping for %s not found.\n"%(cDef.ERROR_getPreviousValforTokens, eachToken)
			except Exception,e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				errStr += "%s Line:%s. SQL failed. Except:%s \n"%(cDef.ERROR_getPreviousValforTokens, exc_tb.tb_lineno, str(e))
		try:
			db.close()
			#print("tokenDict488--> ", tokenDict) --> empty
		except:
			None			
		return {cDef.K_FUNCT_STAT: cDef.V_FUNCT_SUCCESS_1, cDef.K_FUN_DATA: tokenDict, cDef.K_ERR_MSG: errStr }
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		returnDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1
		returnDict[cDef.K_ERR_MSG] = "%s Line:%s. Unknown except:%s"%(cDef.ERROR_getPreviousValforTokens, exc_tb.tb_lineno, str(e))
		return returnDict
	return returnDict

## New change Ajay 2018-04-10
def getExceptionTokens(exchangeName, segmentName, exchangeType, segmentType):
	"""
	[Function]  :	Get exception tokens for the exchange and the segment given. For example CD segment some tokens will be traded after 5:00PM IST. For those we still have to set 1min data.
	
	[Input] 	: 	exchangeName 	-> NSE
				  	segmentName 	-> CM/FO/CD
	[Output]	: 	Dict {cDef.K_FUNCT_STAT: cDef.V_FUNCT_SUCCESS_1 ,cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: ''}
					cDef.K_FUNCT_STAT 	-> cDef.V_FUNCT_SUCCESS_1 / cDef.V_FUNCT_FAIL_N_1
					cDef.K_FUN_DATA 	-> Dict contain the information
					cDef.K_ERR_MSG		-> Error message
	"""
	tokenDict 	= {}
	returnDict = {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: tokenDict, cDef.K_ERR_MSG:"%s Unknown error."%(cDef.ERROR_getExceptionTokens)}
	exceptConditn = ""
	try:
		if exchangeName == cDef.EXCHANGE_NAME_NSE:
			if 	 segmentName == cDef.SEG_NAME_CM_LIVE or segmentName == cDef.SEG_NAME_CM_TEST:
				exceptConditn = cDef.EXCEPT_TOKEN_CONDI_CM
			elif segmentName == cDef.SEG_NAME_FO_LIVE or segmentName == cDef.SEG_NAME_FO_TEST:
				exceptConditn = cDef.EXCEPT_TOKEN_CONDI_FO
			elif segmentName == cDef.SEG_NAME_CD_LIVE or segmentName == cDef.SEG_NAME_CD_TEST:
				exceptConditn = cDef.EXCEPT_TOKEN_CONDI_CD
			else:
				returnDict[cDef.K_ERR_MSG] = "%s Invalid segment:%s for exchange:%s"%(cDef.ERROR_getExceptionTokens, segmentName, exchangeName)
				return returnDict
		elif exchangeName == MCXConf.MCX_EXCHANGE_NAME:
			if segmentName == MCXConf.SYM_SEGMENT_COM_NAME_LIVE or segmentName == MCXConf.SYM_SEGMENT_COM_NAME_TEST:
				exceptConditn = cDef.EXCEPT_TOKEN_CONDI_MCX_COM
			else:
				returnDict[cDef.K_ERR_MSG] = "%s Invalid segment:%s for exchange:%s"%(cDef.ERROR_getExceptionTokens, segmentName, exchangeName)
				return returnDict
		elif exchangeName == cDef.EXCHANGE_NAME_BSE:
			if 	 segmentName == cDef.SEG_NAME_CM_LIVE_BSE or segmentName == cDef.SEG_NAME_CM_TEST_BSE:
				exceptConditn = cDef.EXCEPT_TOKEN_CONDI_CM_BSE
			elif segmentName == cDef.SEG_NAME_FO_LIVE_BSE or segmentName == cDef.SEG_NAME_FO_TEST_BSE:
				exceptConditn = cDef.EXCEPT_TOKEN_CONDI_FO_BSE
			elif segmentName == cDef.SEG_NAME_CD_LIVE_BSE or segmentName == cDef.SEG_NAME_CD_TEST_BSE:
				exceptConditn = cDef.EXCEPT_TOKEN_CONDI_CD_BSE
			else:
				returnDict[cDef.K_ERR_MSG] = "%s Invalid segment:%s for exchange:%s"%(cDef.ERROR_getExceptionTokens, segmentName, exchangeName)
				return returnDict
		else:
			returnDict[cDef.K_ERR_MSG] = "%s Invalid exchangeName: %s"%(cDef.ERROR_getExceptionTokens, exchangeName)
			return returnDict
		## ********** New Change Ajay 2019-01-16 **********
		
		if len(exceptConditn) == 0:
			returnDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_SUCCESS_1
			returnDict[cDef.K_FUN_DATA]		= {}
			returnDict[cDef.K_ERR_MSG]		= "%s No exception condition found for exchange:%s segment:%s."%(cDef.ERROR_getExceptionTokens, exchangeName, segmentName)
			return returnDict

		retDbConn = dbConnect(dbType=3, readOnly=1)
		if retDbConn[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
			return retDbConn
		[db, cursor] = retDbConn[cDef.K_FUN_DATA]
		getExceptTokensSQL = "SELECT FY_TOKEN FROM `%s` WHERE EX=%s and EX_SEGMENT=%s and %s;"%(cDef.TBL_SYMBOL_MASTER, exchangeType, segmentType, exceptConditn)
		# print "getExceptTokensSQL:", getExceptTokensSQL
		sqlRet = ()
		try:
			cursor.execute(getExceptTokensSQL)
			sqlRet = cursor.fetchall()
			# print len(sqlRet)
		except Exception,e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			returnDict[cDef.K_ERR_MSG] = "%s Line:%s. SQL failed. Except:%s"%(cDef.ERROR_getFyTokenDict, exc_tb.tb_lineno, str(e))
			db.close()
			return returnDict
		finally:
			db.close()

		for eachItem in sqlRet:
			tokenDict[eachItem[0]] = None
		return {cDef.K_FUNCT_STAT:cDef.V_FUNCT_SUCCESS_1, cDef.K_FUN_DATA: tokenDict, cDef.K_ERR_MSG:""}

	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		eturnDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1
		returnDict[cDef.K_ERR_MSG] = "%s Line:%s. SQL failed. Except:%s"%(cDef.ERROR_getFyTokenDict, exc_tb.tb_lineno, str(e))
		return returnDict
	#print("572returnDict--> ", returnDict)
	return returnDict

def checkMktHours(inputExchange, inputSegment, dateTimeNow):
	"""
	## These two lines need to be called before starting the function.
	# os.environ["TZ"] = "Asia/Kolkata" ## This is critical
	# time.tzset() ## This is critical
	[Function]	: 	Check if the current time is between 9:00AM and 3:30PM
	[Output]	: 	Success : {cmnDef.K_FUNCT_STAT:cmnDef.V_FUNCT_SUCCESS_1, cmnDef.K_FUN_DATA: maket_status, cmnDef.K_ERR_MSG:message}
					Fail 	: {cmnDef.K_FUNCT_STAT:cmnDef.V_FUNCT_FAIL_N_1, cmnDef.K_FUN_DATA: maket_status, cmnDef.K_ERR_MSG:message}
					maket_status : 	True 	: If time is within market hours.
									False	: If time is not within market hours.
					maket_status : 	Pre Open:
									1-> pre_market
									4-> pre_market_extended
									6-> pre_market price_discovery
									Open:
									2-> market_open
									3-> Suspended
									7-> Partially traded.
									Close:
									9-> Closed
	"""
	retDict = {cDef.K_FUNCT_STAT:cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: cDef.MKT_F_NORMAL_OPEN, cDef.K_ERR_MSG:"%sunknown"%(cDef.ERROR_checkMktHours)} ## Just in case if all the above case failed return True

	try:
		inputExchange, inputSegment = inputExchange.upper(), inputSegment.upper()
		dateTimeNow = datetime.datetime.fromtimestamp(int(dateTimeNow))
		# print "dateTimeNow:", dateTimeNow
		startTimeNormal, endTimeNormal, exptnTimeDict = None, None, {}
		preMktStart, preMktEnd, extStart, extEnd = None, None, None, None

		if inputExchange == cDef.EXCHANGE_NAME_NSE:
			if 	 inputSegment == cDef.SEG_NAME_CM_LIVE or inputSegment == cDef.SEG_NAME_CM_TEST:
				startTimeNormal, endTimeNormal, exptnTimeDict = cDef.CM_NORMAL_START_TIME, cDef.CM_NORMAL_END_TIME, cDef.CM_EXCEPTION_TIME_DICT
				preMktStart, preMktEnd, extStart, extEnd = cDef.CM_PRE_MKT_START_TIME, cDef.CM_PRE_MKT_END_TIME, cDef.CM_EXTEND_START_TIME, cDef.CM_EXTEND_END_TIME
			elif inputSegment == cDef.SEG_NAME_FO_LIVE or inputSegment == cDef.SEG_NAME_FO_TEST:
				startTimeNormal, endTimeNormal, exptnTimeDict = cDef.FO_NORMAL_START_TIME, cDef.FO_NORMAL_END_TIME, cDef.FO_EXCEPTION_TIME_DICT
				preMktStart, preMktEnd, extStart, extEnd = cDef.FO_PRE_MKT_START_TIME, cDef.FO_PRE_MKT_END_TIME, cDef.FO_EXTEND_START_TIME, cDef.FO_EXTEND_END_TIME
			elif inputSegment == cDef.SEG_NAME_CD_LIVE or inputSegment == cDef.SEG_NAME_CD_TEST:
				startTimeNormal, endTimeNormal, exptnTimeDict = cDef.CD_NORMAL_START_TIME, cDef.CD_NORMAL_END_TIME, cDef.CD_EXCEPTION_TIME_DICT
				preMktStart, preMktEnd, extStart, extEnd = cDef.CD_PRE_MKT_START_TIME, cDef.CD_PRE_MKT_END_TIME, cDef.CD_EXTEND_START_TIME, cDef.CD_EXTEND_END_TIME
			# elif inputSegment == cDef.SEG_NAME_CM_TEST or inputSegment == cDef.SEG_NAME_FO_TEST or inputSegment == cDef.SEG_NAME_CD_TEST:
			# 	retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_SUCCESS_1
			# 	retDict[cDef.K_ERR_MSG]	 	= "For test market open/close timings are not defined."
			# 	retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN
			else:
				retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1
				retDict[cDef.K_ERR_MSG]	 	= "%s Unknown segment:%s for exchange:%s"%(cDef.ERROR_checkMktHours, inputSegment, inputExchange)
				retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN ## This is made success because incase if we send any other data it should not stop setting the data
				return retDict

		elif inputExchange == MCXConf.MCX_EXCHANGE_NAME:
			if inputSegment == MCXConf.SYM_SEGMENT_COM_NAME_LIVE or inputSegment == MCXConf.SYM_SEGMENT_COM_NAME_TEST:
				startTimeNormal, endTimeNormal = MCXConf.MCX_NORMAL_START_TIME, MCXConf.MCX_NORMAL_END_TIME
				exptnTimeDict = cDef.COM_EXCEPTION_TIME_DICT_MCX
				## THis doesnot matter because MCX status will always be on
				preMktStart, preMktEnd, extStart, extEnd = cDef.COM_PRE_MKT_START_TIME_MCX, cDef.COM_PRE_MKT_END_TIME_MCX, cDef.COM_EXTEND_START_TIME_MCX, cDef.COM_EXTEND_END_TIME_MCX
			else:
				retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1
				retDict[cDef.K_ERR_MSG]	 	= "%s Unknown segment:%s for exchange:%s"%(cDef.ERROR_checkMktHours, inputSegment, inputExchange)
				retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN ## This is made success because incase if we send any other data it should not stop setting the data
				return retDict
		
		elif inputExchange == cDef.EXCHANGE_NAME_BSE:
			if 	 inputSegment == cDef.SEG_NAME_CM_LIVE_BSE or inputSegment == cDef.SEG_NAME_CM_TEST_BSE:
				startTimeNormal, endTimeNormal, exptnTimeDict = cDef.CM_NORMAL_START_TIME_BSE, cDef.CM_NORMAL_END_TIME_BSE, cDef.CM_EXCEPTION_TIME_DICT_BSE
				preMktStart, preMktEnd, extStart, extEnd = cDef.CM_PRE_MKT_START_TIME_BSE, cDef.CM_PRE_MKT_END_TIME_BSE, cDef.CM_EXTEND_START_TIME_BSE, cDef.CM_EXTEND_END_TIME_BSE
			elif inputSegment == cDef.SEG_NAME_FO_LIVE_BSE or inputSegment == cDef.SEG_NAME_FO_TEST_BSE:
				startTimeNormal, endTimeNormal, exptnTimeDict = cDef.FO_NORMAL_START_TIME_BSE, cDef.FO_NORMAL_END_TIME_BSE, cDef.FO_EXCEPTION_TIME_DICT_BSE
				preMktStart, preMktEnd, extStart, extEnd = cDef.FO_PRE_MKT_START_TIME_BSE, cDef.FO_PRE_MKT_END_TIME_BSE, cDef.FO_EXTEND_START_TIME_BSE, cDef.FO_EXTEND_END_TIME_BSE
			elif inputSegment == cDef.SEG_NAME_CD_LIVE_BSE or inputSegment == cDef.SEG_NAME_CD_TEST_BSE:
				startTimeNormal, endTimeNormal, exptnTimeDict = cDef.CD_NORMAL_START_TIME_BSE, cDef.CD_NORMAL_END_TIME_BSE, cDef.CD_EXCEPTION_TIME_DICT_BSE
				preMktStart, preMktEnd, extStart, extEnd = cDef.CD_PRE_MKT_START_TIME_BSE, cDef.CD_PRE_MKT_END_TIME_BSE, cDef.CD_EXTEND_START_TIME_BSE, cDef.CD_EXTEND_END_TIME_BSE
			else:
				retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1
				retDict[cDef.K_ERR_MSG]	 	= "%s Unknown segment:%s for exchange:%s"%(cDef.ERROR_checkMktHours, inputSegment, inputExchange)
				retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN## This is made success because incase if we send any other data it should not stop setting the data
				return retDict

		else:
			retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1
			retDict[cDef.K_ERR_MSG]	 	= "%s Unknown exchange:%s, segment:%s"%(cDef.ERROR_checkMktHours, inputExchange, inputSegment)
			retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN ## This is made success because incase if we send any other data it should not stop setting the data
			return retDict
		# print "preMktStart, preMktEnd, extStart, extEnd", preMktStart, preMktEnd, extStart, extEnd
		if startTimeNormal != None and endTimeNormal != None or exptnTimeDict != None:
			dateTodayStr 	= dateTimeNow.strftime('%Y-%m-%d')
			startT 			= dateTimeNow.replace(hour=startTimeNormal.hour, minute=startTimeNormal.minute, second=startTimeNormal.second)
			endT 			= dateTimeNow.replace(hour=endTimeNormal.hour, minute=endTimeNormal.minute, second=endTimeNormal.second)
			preOpenStartT, preOpenEndT 	= None, None
			extStartT, extEndT 			= None, None 
			if preMktStart != None and preMktEnd != None:
				preOpenStartT 	= dateTimeNow.replace(hour=preMktStart.hour, minute=preMktStart.minute, second=preMktStart.second)
				preOpenEndT		= dateTimeNow.replace(hour=preMktEnd.hour, minute=preMktEnd.minute, second=preMktEnd.second)
			if extStart != None and extEnd != None:
				extStartT 	= dateTimeNow.replace(hour=extStart.hour, minute=extStart.minute, second=extStart.second)
				extEndT 	= dateTimeNow.replace(hour=extEnd.hour, minute=extEnd.minute, second=extEnd.second)
			# print "startT, endT:", startT, endT
			if dateTimeNow.isoweekday() in range(1,6): ##from Monday to friday
				if dateTimeNow >= startT and dateTimeNow < endT:
					retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_SUCCESS_1
					retDict[cDef.K_ERR_MSG]	 	= "Market is open on weekdays for time:%s"%(dateTimeNow.strftime("%Y-%m-%d %H:%M:%S"))
					retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN 
				else:
					retDict[cDef.K_FUNCT_STAT]  = cDef.V_FUNCT_SUCCESS_1
					retDict[cDef.K_ERR_MSG]	 	= "Market is closed on weekday for time:%s"%(dateTimeNow.strftime("%Y-%m-%d %H:%M:%S"))
					retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_CLOSED
				
				if preOpenStartT != None and preOpenEndT != None and retDict[cDef.K_FUN_DATA] == cDef.MKT_F_CLOSED:
					if dateTimeNow >= preOpenStartT and dateTimeNow < preOpenEndT:
						retDict[cDef.K_FUNCT_STAT]  = cDef.V_FUNCT_SUCCESS_1
						retDict[cDef.K_ERR_MSG]	 	= "Market is preopened on weekday for time:%s"%(dateTimeNow.strftime("%Y-%m-%d %H:%M:%S"))
						retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_PREOP

				# print "stat:%s"%(retDict[cDef.K_FUN_DATA])
				if extStartT != None and extEndT != None and retDict[cDef.K_FUN_DATA] == cDef.MKT_F_CLOSED:
					# print "dateTimeNow:%s extStartT:%s, extEndT:%s"%(dateTimeNow, extStartT, extEndT)
					if dateTimeNow >= extStartT and dateTimeNow < extEndT:
						retDict[cDef.K_FUNCT_STAT]  = cDef.V_FUNCT_SUCCESS_1
						retDict[cDef.K_ERR_MSG]	 	= "Market is partially trading on weekday for time:%s"%(dateTimeNow.strftime("%Y-%m-%d %H:%M:%S"))
						retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_PARTIAL
			else:
				retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_SUCCESS_1
				retDict[cDef.K_ERR_MSG]	 	= "Market is closed its a weekend for time:%s"%(dateTimeNow.strftime("%Y-%m-%d %H:%M:%S"))
				retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_CLOSED ## Its a weekend

			if dateTodayStr in exptnTimeDict:# and retDict[cDef.K_FUN_DATA] == cDef.MKT_F_CLOSED: ## This is when we have normal market closed and there is an exception time in the dict
				try:
					exceptStartT 	= datetime.datetime.strptime(dateTodayStr+exptnTimeDict[dateTodayStr][0], "%Y-%m-%d%H:%M:%S")
					exceptEndT 		= datetime.datetime.strptime(dateTodayStr+exptnTimeDict[dateTodayStr][1], "%Y-%m-%d%H:%M:%S")
					if dateTimeNow >= exceptStartT and dateTimeNow < exceptEndT:
						retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_SUCCESS_1
						retDict[cDef.K_ERR_MSG]	 	= "Market is open on exception date for time:%s"%(dateTimeNow.strftime("%Y-%m-%d %H:%M:%S"))
						retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN
				except Exception,e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1
					retDict[cDef.K_ERR_MSG]	 	= "%s Line:%s. Exception while calc exception time. Except:%s"%(cDef.ERROR_checkMktHours, exc_tb.tb_lineno, str(e))
					retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN
		else:
			# print "startTimeNormal:%s, endTimeNormal:%s, exptnTimeDict:%s"%(startTimeNormal, endTimeNormal, exptnTimeDict)
			retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1 ## This is made success because incase if we send any other data it should not stop setting the data
			retDict[cDef.K_ERR_MSG]	 	= "%s Invalid input parameters found."%(cDef.ERROR_checkMktHours)
			retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN
		# print("retDict in fy_comn_funct--> ", retDict)
		# ('retDict in fy_comn_funct--> ', {100: 1, 101: 'Market is open on weekdays for time:2020-12-21 10:56:44', 102: 2})

		return retDict
		# ##**********************New code MCX 20181019 - Palash*************************##
		# elif inputExchange == MCXConf.MCX_EXCHANGE_NAME:
		# 	startTimeNormal, endTimeNormal = None, None
		# 	if inputSegment == MCXConf.SYM_SEGMENT_COM_NAME_LIVE or inputSegment == MCXConf.SYM_SEGMENT_COM_NAME_TEST:
		# 		startTimeNormal, endTimeNormal = MCXConf.MCX_NORMAL_START_TIME, MCXConf.MCX_NORMAL_END_TIME
		# 		if startTimeNormal != None and endTimeNormal != None:
		# 			dateTodayStr 	= dateTimeNow.strftime('%Y-%m-%d')
		# 			startT 			= dateTimeNow.replace(hour=startTimeNormal.hour, minute=startTimeNormal.minute, second=startTimeNormal.second)
		# 			endT 			= dateTimeNow.replace(hour=endTimeNormal.hour, minute=endTimeNormal.minute, second=endTimeNormal.second)
		# 			if dateTimeNow.isoweekday() in range(1,6): ##from Monday to friday
		# 				if dateTimeNow >= startT and dateTimeNow < endT:
		# 					retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_SUCCESS_1
		# 					retDict[cDef.K_ERR_MSG]	 	= "Market is open on weekdays for time:%s"%(dateTimeNow.strftime("%Y-%m-%d %H:%M:%S"))
		# 					retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN 
		# 				else:
		# 					retDict[cDef.K_FUNCT_STAT]  = cDef.V_FUNCT_SUCCESS_1
		# 					retDict[cDef.K_ERR_MSG]	 	= "Market is closed on weekday for time:%s"%(dateTimeNow.strftime("%Y-%m-%d %H:%M:%S"))
		# 					retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_CLOSED
		# 			else:
		# 				retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_SUCCESS_1
		# 				retDict[cDef.K_ERR_MSG]	 	= "Market is closed its a weekend for time:%s"%(dateTimeNow.strftime("%Y-%m-%d %H:%M:%S"))
		# 				retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_CLOSED ## Its a weekend
		# 		else:
		# 			# print "startTimeNormal:%s, endTimeNormal:%s, exptnTimeDict:%s"%(startTimeNormal, endTimeNormal, exptnTimeDict)
		# 			retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1 ## This is made success because incase if we send any other data it should not stop setting the data
		# 			retDict[cDef.K_ERR_MSG]	 	= "%s Invalid input parameters found."%(cDef.ERROR_checkMktHours)
		# 			retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN
		# 	else:
		# 		retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1 ## This is made success because incase if we send any other data it should not stop setting the data
		# 		retDict[cDef.K_ERR_MSG]	 	= "%s Unknown segment:%s"%(cDef.ERROR_checkMktHours, inputSegment)
		# 		retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN
		# ##END
		# else:
		# 	retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1 ## This is made success because incase if we send any other data it should not stop setting the data
		# 	retDict[cDef.K_ERR_MSG]	 	= "%s Unknown exchange:%s"%(cDef.ERROR_checkMktHours, inputExchange)
		# 	retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN

	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_FUNCT_STAT] 	= cDef.V_FUNCT_FAIL_N_1
		retDict[cDef.K_ERR_MSG]	 	= "%s Line:%s. Unknow exception. Except:%s"%(cDef.ERROR_checkMktHours, exc_tb.tb_lineno, str(e))
		retDict[cDef.K_FUN_DATA] 	= cDef.MKT_F_NORMAL_OPEN
	return retDict

if __name__ == "__main__":

	
	normalTimeList = [
					# Normal day
					"2018-03-09 08:00:00",
					"2018-03-09 08:59:59",
					"2018-03-09 09:00:00",
					"2018-03-09 09:05:00",
					"2018-03-09 09:07:10",
					"2018-03-09 09:10:00",
					"2018-03-09 09:14:59",
					"2018-03-09 09:15:00",
					"2018-03-09 10:30:00",
					"2018-03-09 14:30:00",
					"2018-03-09 14:59:59",
					"2018-03-09 15:00:00",
					"2018-03-09 15:29:59",
					"2018-03-09 15:30:00",
					"2018-03-09 15:30:01",
					"2018-03-09 16:30:01",
					"2018-03-09 16:59:59",
					"2018-03-09 17:00:00",
					"2018-03-09 17:30:59",
					"2018-03-09 19:00:59",
					"2018-03-09 19:29:59",
					"2018-03-09 19:30:00",
					"2018-03-09 19:31:00",
					"2018-03-09 21:01:00",
					# Weekend
					"2018-03-10 08:00:00",
					"2018-03-10 09:00:00",
					"2018-03-10 09:14:59",
					"2018-03-10 09:15:00",
					"2018-03-10 10:30:00",
					"2018-03-10 14:30:00",
					"2018-03-10 14:59:59",
					"2018-03-10 15:00:00",
					"2018-03-10 15:30:00",
					"2018-03-10 15:30:01",
					"2018-03-10 16:30:01",
					"2018-03-10 21:01:00"
				]

	excptTimeList = [
						"2017-10-17 05:00:00",
						"2017-10-17 08:30:00",
						"2017-10-17 08:59:59",
						"2017-10-17 09:00:00",
						"2017-10-17 09:07:00",
						"2017-10-17 09:14:59",
						"2017-10-17 09:15:00",
						"2017-10-17 09:30:00",
						"2017-10-17 15:29:00",
						"2017-10-17 15:30:01",
						"2017-10-17 17:00:00",
						"2017-10-17 17:30:00",
						"2017-10-17 19:00:00",
						"2017-10-17 19:01:00",
						"2017-10-17 19:59:59",
						"2017-10-17 20:00:00",
						"2017-10-17 20:30:00",
						"2017-10-17 20:59:59",
						"2017-10-17 21:00:00",
						"2017-10-17 21:00:01",
						"2017-10-17 22:00:00",
					]

	os.environ["TZ"] = "Asia/Kolkata" ## This is critical
	time.tzset() ## This is critical
	# print "*************************** CM:Normal day validation ***************************"
	# time8AM = 1520562600
	# st = time.time()
	# a= checkMktHours(cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_CM_LIVE, time8AM)
	# print "time:", time.time()-st
	# print checkMktHours(cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_FO_LIVE, time8AM)
	# print checkMktHours(cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_CD_LIVE, time8AM)
	# sys.exit()
	# # print time.mktime(time.strptime(normalTimeList[0], "%Y-%m-%d %H:%M:%S"))
	# for eachTime in normalTimeList:
	# 	print checkMktHours(cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_CM_LIVE, time.mktime(time.strptime(eachTime, "%Y-%m-%d %H:%M:%S")))
		
	# print "*************************** CM:Exception time validation ***************************"
	# for eachTime in excptTimeList:
	# 	print checkMktHours(cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_CM_LIVE, time.mktime(time.strptime(eachTime, "%Y-%m-%d %H:%M:%S")))

	# print "*************************** FO:Normal day validation ***************************"
	# for eachTime in normalTimeList:
	# 	print checkMktHours(cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_FO_LIVE, time.mktime(time.strptime(eachTime, "%Y-%m-%d %H:%M:%S")))
	# print "*************************** FO:Exception time validation ***************************"
	# for eachTime in excptTimeList:
	# 	print checkMktHours(cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_FO_LIVE, time.mktime(time.strptime(eachTime, "%Y-%m-%d %H:%M:%S")))
	
	# print "*************************** CD:Normal day validation ***************************"
	# for eachTime in normalTimeList:
	# 	print checkMktHours(cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_CD_LIVE, time.mktime(time.strptime(eachTime, "%Y-%m-%d %H:%M:%S")))
	# print "*************************** CD:Exception time validation ***************************"
	# for eachTime in excptTimeList:
	# 	print checkMktHours(cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_CD_LIVE, time.mktime(time.strptime(eachTime, "%Y-%m-%d %H:%M:%S")))
	# # print cDef.CM_NORMAL_START_TIME

	## *************************************************************Test 2*************************************************************
	# print getExceptionTokens(cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_CD_LIVE)
	# retDbConn = dbConnect(dbType=3, readOnly=1)
	# print retDbConn
	# print NSEConf.FY_TOKEN_7207_DICT.values()
	# print getPreviousValforTokens(cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_FO_TEST, NSEConf.FY_TOKEN_7207_DICT.values())
	ret_newDay = newDayTrigger(FYLog(), cDef.EXCHANGE_NAME_NSE, cDef.SEG_NAME_CD_TEST, printFlag = False, debugFlag =0)
	# print ret_newDay[cDef.K_FUNCT_STAT]
	if ret_newDay[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
		print "function fail", ret_newDay[cDef.K_ERR_MSG]
	else:
		None
		print "exceptTokenDict",ret_newDay[cDef.K_FUN_DATA]["exceptTokenDict"]
		print "tokenPrevValDict",ret_newDay[cDef.K_FUN_DATA]["tokenPrevValDict"]
