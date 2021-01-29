#!/usr/bin/env python

## Long is considered 4 bytes and shot is considered as 2 bytes.

import time
import sys
import json
import struct
import binascii
import datetime
import fy_comn_def as cDef
import fy_BSE_config as bse_conf
import fy_NSE_Config as nseConf

## Defines
LOG_processBSEPackets 	= "processBSEPackets"
LOG_unPack_2001 		= "unPack_2001"
LOG_unPack_2002			= "unPack_2002"
LOG_unPack_2020 		= "unPack_2020"
LOG_unPack_2014			= "unPack_2014"
LOG_unPack_2011			= "unPack_2011"
LOG_unPack_2012			= "unPack_2012"
LOG_unPack_2016 		= "unPack_2016"
LOG_unPack_2015 		= "unPack_2015"
LOG_unPack_2022 		= "unPack_2022"
LOG_unPack_2004			= "unPack_2004"

class BSE_T(object):
	"""
	In the broadcast header BSE doesnot send the date so we take the date from market pic and store it in this variable.
	"""
	BSE_DATE = datetime.datetime.now()

def mktStatCheck(logFP_inst, mktType, sessionNum, printFlag = False):
	"""
	[Function]	:	Check the market status depending on the market type and the session number.
	[Input]		:	mktType		-> For the info in the packet 
					sessionNum	-> For the info in the packet
	"""
	tradingStatus = cDef.MKT_F_NORMAL_OPEN ## Default
	if mktType == 0 and sessionNum == 0: ## Logon
		tradingStatus = cDef.MKT_F_CLOSED
	elif mktType == 0 and sessionNum == 1: ## Order entry session start
		tradingStatus = cDef.MKT_F_PREOP
	elif mktType == 0 and sessionNum == 2: ## End matching session
		tradingStatus = cDef.MKT_F_PREOP
	elif mktType == 0 and sessionNum == 3: ## Continuous session
		tradingStatus = cDef.MKT_F_NORMAL_OPEN
	elif mktType == 20 and sessionNum == 1: ## PCAS session 1 Order Entry Session
		tradingStatus = cDef.MKT_F_NORMAL_OPEN
	elif mktType == 0 and sessionNum == 10: ## Random End of SPOS Order Entry Session [Freeze Session]
		tradingStatus = cDef.MKT_F_NORMAL_OPEN
	elif mktType == 0 and sessionNum == 13: ## Continuous Session for SPOS
		tradingStatus = cDef.MKT_F_NORMAL_OPEN
	elif mktType == 20 and sessionNum == 1: ## Random End of PCAS session 1 Order Entry Session
		tradingStatus = cDef.MKT_F_NORMAL_OPEN
	elif mktType == 20 and sessionNum == 2: ## End of Matching Session of PCAS session 1
		tradingStatus = cDef.MKT_F_NORMAL_OPEN
	elif mktType == 0 and sessionNum == 4: ## Closing
		tradingStatus = cDef.MKT_F_CLOSED
	elif mktType == 0 and sessionNum == 5: ## Post Closing session
		tradingStatus = cDef.MKT_F_CLOSED
	elif mktType == 0 and sessionNum == 7: ## Member Query Session
		tradingStatus = cDef.MKT_F_CLOSED
	elif mktType == 0 and sessionNum == 6: ## End of day
		tradingStatus = cDef.MKT_F_CLOSED
	else:
		logFP_inst.LogError(None, "ERR : mktStatCheck-> Unknown mktType:%s sessionNum:%s"%(mktType, sessionNum), printFlag)
	# print "tradingStatus:", tradingStatus
	return tradingStatus

def unPack_2001(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = False):
	"""
	BSE	: This message is sent by the BOLTPLUS to the TPS after every 1 minute. Multiple packets for the same time are sent to compensate the loss of packets.
	Same for CM, FO and CD
	## This is just to update the timestamp. Other than that this does not have any useful data.
	"""
	try:
		retDict = {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "ERR : %s Unknown error."%(LOG_unPack_2001)}

		if len(inputPkt) < bse_conf.BSE_TIME_BROADCAST_LEN_2001:
			retDict[cDef.K_ERR_MSG] = "ERR : %s input packet length:%s is less than required length:%s."%(LOG_unPack_2001, len(inputPkt), bse_conf.BSE_TIME_BROADCAST_LEN_2001)
			return retDict
		try:
			(res4, res5, res6, res7, res8, res9) = bse_conf.BSE_TIME_BROADCAST_STRUCT_2001.unpack(inputPkt[:bse_conf.BSE_TIME_BROADCAST_LEN_2001])

			retDict = {
						cDef.K_FUNCT_STAT 	: cDef.V_FUNCT_SUCCESS_1,
						cDef.K_FUN_DATA		: {
												"res4": res4, 
												"res5": res5, 
												"res6": res6, 
												"res7": res7, 
												"res8": res8, 
												"res9": res9
												},
						cDef.K_ERR_MSG		: ""
					}
			return retDict
		except Exception, e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack1 exception:%s"%(LOG_unPack_2001, exc_tb.tb_lineno, str(e))
			return retDict

	except Exception, e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unknown exception:%s"%(LOG_unPack_2001, exc_tb.tb_lineno, str(e))
	return retDict

def unPack_2002(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = False):
	"""
	BSE	: This broadcast is sent by the BOLTPLUS whenever there is a change in session.Each session is represented using a unique session number. The session number is specific to a market type. The session broadcast message will be sent multiple times to compensate the loss of packet if any.
	"""
	try:
		retDict = {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "ERR : %s Unknown error."%(LOG_unPack_2002)}

		if len(inputPkt) < bse_conf.BSE_SESSION_CHANGE_LEN_2002:
			retDict[cDef.K_ERR_MSG] = "ERR : %s input packet length:%s is less than required length:%s."%(LOG_unPack_2002, len(inputPkt), bse_conf.BSE_SESSION_CHANGE_LEN_2002)
			return retDict
		try:
			(prodId, res4, filler, mktType, sessnNum, res5, startEndFlag, res6, res7) = bse_conf.BSE_SESSION_CHANGE_STRUCT_2002.unpack(inputPkt[:bse_conf.BSE_SESSION_CHANGE_LEN_2002])
			mktStat = mktStatCheck(logFP_inst, mktType, sessnNum, printFlag)
			retDict = {
						cDef.K_FUNCT_STAT 	: cDef.V_FUNCT_SUCCESS_1,
						cDef.K_FUN_DATA		: {
												"prodId"		: prodId, ## Applicable for Currency Derivatives segment only
												"res4"			: res4,
												"filler"		: filler, 
												"mktType"		: mktType,
												"sessnNum"		: sessnNum,
												"res5"			: res5, 
												"startEndFlag"	: startEndFlag, 
												"res6"			: res6,
												"res7"			: res7,
												"mktStat"		: mktStat ## This will contain the actual market status depending on the session number
											},
						cDef.K_ERR_MSG		: ""
					}
			return retDict
		
		except Exception, e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack1 exception:%s"%(LOG_unPack_2002, exc_tb.tb_lineno, str(e))
			return retDict
		
	except Exception, e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unknown exception:%s"%(LOG_unPack_2002, exc_tb.tb_lineno, str(e))
	return retDict

def unPack_2020(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = False):
	"""
	BSE	: This message is used to inform about the detailed market picture of Instruments during continuous trading sessions.
	"""
	try:
		retDict = {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "ERR : %s Unknown error."%(LOG_unPack_2020)}

		if len(inputPkt) < bse_conf.BSE_MKT_PIC_LEN_2020_HEAD:
			retDict[cDef.K_ERR_MSG] = "ERR : %s input packet length:%s is less than required length:%s."%(LOG_unPack_2020, len(inputPkt), bse_conf.BSE_MKT_PIC_LEN_2020_HEAD)
			return retDict
		# print ' '.join(binascii.hexlify(inputPkt)[i:i+2] for i in xrange(0,len(binascii.hexlify(inputPkt)),2))
		
		try:
			(res4, res5, numRecord) = bse_conf.BSE_MKT_PIC_STRUCT_2020_HEAD.unpack(inputPkt[:bse_conf.BSE_MKT_PIC_LEN_2020_HEAD])
		except Exception, e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack1 exception:%s"%(LOG_unPack_2020, exc_tb.tb_lineno, str(e))
			return retDict
		# print "%s: numRecord:%s"%(LOG_unPack_2020, numRecord)
		if numRecord <= 0 or numRecord > bse_conf.BSE_MKT_PIC_2020_BODY_MAX_NUM_REC:
			retDict[cDef.K_ERR_MSG] = "ERR : %s Invalid number of records:%s max limit:%s."%(LOG_unPack_2020, numRecord, bse_conf.BSE_MKT_PIC_2020_BODY_MAX_NUM_REC)
			return retDict
		
		pointerIncri = bse_conf.BSE_MKT_PIC_LEN_2020_HEAD ## Counter to increment when there are multiple records
		
		# valList = [] ## This is made as list because incase BSE sends two values for the same script then the old values are getting overwritten in the dict. This should be implemented later
		valDict = {}
		for eachRec in range(0, numRecord):
			try:
				(instrCode, openRate, prevCloseRate, highRate, lowRate, noOfTrades, volume, value, lastTradeQty, lastTradeP, closeRate, blockDealRefP, indicativeEqlibmP, indicativeEqbmQty, timestamp, totalBidQty, totalOfferQty, tradeValFlag, filler, res6, res7, lowCktLim, upperCktLim, weightAvg, mktType, sessionNum, htpHour, ltpMin, ltpSec, ltpMillSec, res3, res4, noPricePts) = bse_conf.BSE_MKT_PIC_STRUCT_2020_BODY.unpack(inputPkt[pointerIncri:pointerIncri + bse_conf.BSE_MKT_PIC_LEN_2020_BODY])

				# timestampPacket = inputPkt[pointerIncri+56:pointerIncri+98]
				# print ' '.join(binascii.hexlify(timestampPacket)[i:i+2] for i in xrange(0,len(binascii.hexlify(timestampPacket)),2))
				pointerIncri += bse_conf.BSE_MKT_PIC_LEN_2020_BODY ## Offset increment
				
				## ltpMillSec is not required since we are considering unix timestamp as int
				# print "%s:htpHour:%s, ltpMin:%s, ltpSec:%s, ltpMillSec:%s, "%(LOG_unPack_2020, htpHour, ltpMin, ltpSec, ltpMillSec)
				## LTT
				dateTimeNow = datetime.datetime.now()
				LTT = datetime.datetime.strptime("%s-%s-%s"%(htpHour, ltpMin, ltpSec), "%H-%M-%S")
				dateTimeLTT = dateTimeNow.replace(hour=LTT.hour, minute=LTT.minute, second=LTT.second, microsecond=0)
				## TODO : Review before deployment
				# timestampBCH = time.mktime(dateTimeBCH.timetuple())
				# print "timestampBCH: before :", timestampBCH
				timestampLTT = int(time.mktime(time.localtime(time.mktime(time.gmtime(time.mktime(dateTimeLTT.timetuple())))))) ## Since the machine is running in UTC converting time to localtime wont give you IST
				# print "instrCode:", instrCode
				fyToken = str(instrCode)
				try:
					fyToken = fyTokenDict[str(instrCode)]
				except Exception,e:
					if str(instrCode) not in failedTokenDict:
						failedTokenDict[str(instrCode)] = None ## we can put the error count here if needed.
						logFP_inst.LogError(None, "%s token %s not found in fyDict no errors will be logged for this again. Except:%s"%(LOG_unPack_2020, instrCode, e), printFlag)
					else:
						None
					continue
				finally:
					None

				# openRate, prevCloseRate, highRate, lowRate = openRate/100.0, prevCloseRate/100.0, highRate/100.0, lowRate/100.0
				# lastTradeP = lastTradeP/100.0
				# if str(instrCode) == "500112":
				# 	print "SBIN lastTradeP:%s, timestampLTT:%s"%(lastTradeP, timestampLTT)
				# print "timestamp before:%s, mktType:%s, sessionNum:%s, totalBidQty:%s"%(timestamp, mktType, sessionNum, totalBidQty)
				## This timestamp is 2 sec ahead
				timestamp = timestamp/1000000000
				picDate = datetime.datetime.fromtimestamp(timestamp)
				# print "timestamp:%s, picDate:%s"%(timestamp, picDate)
				BSE_T.BSE_DATE = picDate
				# tradeValFlag -> l for lacs, c for crores
				# print "instrCode:%s timestamp:%s, tradeValFlag:%s"%(instrCode, timestamp, tradeValFlag)
				# print "noPricePts:", noPricePts
				bidList, askList = [], []
				## n Number of Price points. Currently n = 5
				for eachPoint in range(0, noPricePts):
					try:
						(bestBidRate, totBidQty, noOfBid, implBuyQty, bestOfferRate, totOfferQty, noOfAsk, implSellQty) = bse_conf.BSE_MKT_PIC_STRUCT_2020_BID_ASK.unpack(inputPkt[pointerIncri: pointerIncri+bse_conf.BSE_MKT_PIC_LEN_2020_BID_ASK])
						# bestBidRate, bestOfferRate = bestBidRate/100.0, bestOfferRate/100.0
						# print "bestBidRate:%s"%(bestBidRate)
						bidList.append({cDef.K_BID_ASK_QTY:totBidQty, cDef.K_BID_ASK_P:bestBidRate/float(packetInfoDict["priceConv"]), cDef.K_NUM_BID_ASK: noOfBid, cDef.K_IMPL_QTY: implBuyQty})
						askList.append({cDef.K_BID_ASK_QTY:totOfferQty, cDef.K_BID_ASK_P:bestOfferRate/float(packetInfoDict["priceConv"]), cDef.K_NUM_BID_ASK:noOfAsk, cDef.K_IMPL_QTY: implSellQty})
						# print "noOfBid:%s, implBuyQty:%s"%(noOfBid, implBuyQty,)
						# print askList
					except Exception, e:
						exc_type, exc_obj, exc_tb = sys.exc_info()
						retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack2 exception:%s"%(LOG_unPack_2020, exc_tb.tb_lineno, str(e))
						return retDict
					pointerIncri += bse_conf.BSE_MKT_PIC_LEN_2020_BID_ASK

				tradingStatus = mktStatCheck(logFP_inst, mktType, sessionNum, printFlag)
				# print "tradingStatus:", tradingStatus
				eachInstrVal = {
									cDef.K_TOKEN 		: instrCode, 
									cDef.K_LTP 			: lastTradeP/float(packetInfoDict["priceConv"]),
									cDef.K_LTQ 			: lastTradeQty, 
									cDef.K_LTT			: timestampLTT,
									cDef.K_NPC_FROM_CP 	: (lastTradeP-prevCloseRate),
									cDef.K_ATP 			: 0, 
									cDef.K_VTT			: volume, 
									cDef.K_TOT_BUY_Q	: totalBidQty, 
									cDef.K_TOT_SELL_Q	: totalOfferQty, 
									cDef.K_CLOSING_P	: prevCloseRate/float(packetInfoDict["priceConv"]),
									cDef.K_OPEN_P		: openRate/float(packetInfoDict["priceConv"]),
									cDef.K_HIGH_P		: highRate/float(packetInfoDict["priceConv"]),
									cDef.K_LOW_P		: lowRate/float(packetInfoDict["priceConv"]), 
									cDef.K_BID_ASK_DICT	: {cDef.K_BID:bidList, cDef.K_ASK:askList} ,
									# K_PERCENT_CHNG 	: int(round((lastTradedPrice - closingPrice)*100 / closingPrice, 2) * PRICE_CONV_100), ## This should not be calculated in here because after market close price changes and we have to caculate depending on close price.
									cDef.K_PRICE_CONV	: packetInfoDict["priceConv"],
									cDef.K_BCH_TS		: timestamp, 
									cDef.K_BCH_PACKT_CODE: nseConf.NSE_T_CODE_7208,
									cDef.K_TRADIN_STAT 	: tradingStatus
								}
				# valList.append({instrCode: eachInstrVal})
				# print fyToken, eachInstrVal[cDef.K_LTP], eachInstrVal[cDef.K_BID_ASK_DICT]
				valDict[fyToken] = eachInstrVal
			except Exception, e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack3 exception:%s"%(LOG_unPack_2020, exc_tb.tb_lineno, str(e))
				return retDict
				# break ## Incase there is an exception you should not go further with invalid data

		retDict = {
					cDef.K_FUNCT_STAT 	: cDef.V_FUNCT_SUCCESS_1,
					cDef.K_FUN_DATA		: valDict,
					cDef.K_ERR_MSG		: ""
		}
		return retDict

	except Exception, e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unknown exception:%s"%(LOG_unPack_2020, exc_tb.tb_lineno, str(e))
	return retDict

def unPack_2014(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = False):
	"""
	BSE	: This message is used to inform the Closing Prices of Instrument during the Closing Price calculation sessions.
	"""
	try:
		retDict = {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "ERR : %s Unknown error."%(LOG_unPack_2014)}

		if len(inputPkt) < bse_conf.BSE_CLOSE_P_BCAST_LEN_2014_HEAD:
			retDict[cDef.K_ERR_MSG] = "ERR : %s input packet length:%s is less than required length:%s."%(LOG_unPack_2014, len(inputPkt), bse_conf.BSE_CLOSE_P_BCAST_LEN_2014_HEAD)
			return retDict
		
		try:
			(res4, res5, numRecord) = bse_conf.BSE_CLOSE_P_BCAST_STRUCT_2014_HEAD.unpack(inputPkt[:bse_conf.BSE_CLOSE_P_BCAST_LEN_2014_HEAD])
		except Exception, e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack1 exception:%s"%(LOG_unPack_2014, exc_tb.tb_lineno, str(e))
			return retDict
		
		if numRecord <= 0 or numRecord > bse_conf.BSE_CLOSE_P_BCAST_2014_MAX_NUM_REC:
			retDict[cDef.K_ERR_MSG] = "ERR : %s Invalid number of records:%s max limit:%s."%(LOG_unPack_2014, numRecord, bse_conf.BSE_CLOSE_P_BCAST_2014_MAX_NUM_REC)
			return retDict
		
		pointerIncri = bse_conf.BSE_CLOSE_P_BCAST_LEN_2014_HEAD ## Counter to increment when there are multiple records
		valList = []
		for eachRec in range(0, numRecord):
			try:
				(instrCode, price, res6, traded, precisionIndi, res7) = bse_conf.BSE_CLOSE_P_BCAST_STRUCT_2014_BODY.unpack(inputPkt[pointerIncri:pointerIncri+bse_conf.BSE_CLOSE_P_BCAST_LEN_2014_BODY])
				pointerIncri += bse_conf.BSE_CLOSE_P_BCAST_LEN_2014_BODY

				valList.append({
						instrCode: {
							cDef.K_TOKEN 		: instrCode,
							cDef.K_CLOSING_P	: price, 
							cDef.K_TRADIN_STAT	: traded ## TODO: check this
						}
					})
			except Exception, e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack2 exception:%s"%(LOG_unPack_2014, exc_tb.tb_lineno, str(e))
				return retDict
				# break ## Incase there is an exception you should not go further with invalid data

			
		retDict = {
					cDef.K_FUNCT_STAT 	: cDef.V_FUNCT_SUCCESS_1,
					cDef.K_FUN_DATA		: valList,
					cDef.K_ERR_MSG		: ""
		}
		return retDict

	except Exception, e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unknown exception:%s"%(LOG_unPack_2014, exc_tb.tb_lineno, str(e))
	return retDict
	
def unPack_2011(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = False):
	"""
	BSE : All indices information is broadcasted using the message 2011 or 2012. The indices sent in message type 2011 will not be sent in 2012 and vice-versa during a trading day.
	"""
	try:
		retDict = {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "ERR : %s Unknown error."%(LOG_unPack_2011)}

		if len(inputPkt) < bse_conf.BSE_SENSEX_BCAST_LEN_2011_HEAD:
			retDict[cDef.K_ERR_MSG] = "ERR : %s input packet length:%s is less than required length:%s."%(LOG_unPack_2011, len(inputPkt), bse_conf.BSE_SENSEX_BCAST_LEN_2011_HEAD)
			return retDict
		
		try:
			(res4, res5, numRecord) = bse_conf.BSE_SENSEX_BCAST_STRUCT_2011_HEAD.unpack(inputPkt[:bse_conf.BSE_SENSEX_BCAST_LEN_2011_HEAD])
		except Exception, e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack1 exception:%s"%(LOG_unPack_2011, exc_tb.tb_lineno, str(e))
			return retDict
		
		if numRecord <= 0 or numRecord > bse_conf.BSE_SENSEX_BCAST_2011_MAX_NUM_REC:
			retDict[cDef.K_ERR_MSG] = "ERR : %s Invalid number of records:%s max limit:%s."%(LOG_unPack_2011, numRecord, bse_conf.BSE_SENSEX_BCAST_2011_MAX_NUM_REC)
			return retDict
		
		pointerIncri = bse_conf.BSE_SENSEX_BCAST_LEN_2011_HEAD ## Counter to increment when there are multiple records
		# valList = []
		valDict = {}
		for eachRec in range(0, numRecord):
			try:
				(indexCode, indexHigh, indexLow, indexOpen, indexPrevClose, indexVal, indexID, res6, res7, res8, res9, res10, res11) = bse_conf.BSE_SENSEX_BCAST_STRUCT_2011_BODY.unpack(inputPkt[pointerIncri:pointerIncri+bse_conf.BSE_SENSEX_BCAST_LEN_2011_BODY])
				pointerIncri += bse_conf.BSE_SENSEX_BCAST_LEN_2011_BODY
				tradeStat = 0
				if tradeStat == 0: ## TODO: Validate this
					tradeStat = 2
				## This is mapping of exchange token to fyers token
				indexCode = "%s%s000000%s"%(cDef.EXCHANGE_CODE_BSE, cDef.SEG_CODE_CM_LIVE_BSE, indexCode)
				# print "indexID:%s indexCode:%s, indexVal:%s"%(indexID, indexCode, indexVal)
				valDict[indexCode] = {
					cDef.K_TOKEN 		: indexCode, 
					cDef.K_LTP 			: indexVal/float(packetInfoDict["priceConv"]), 
					cDef.K_HIGH_P		: indexHigh/float(packetInfoDict["priceConv"]), 
					cDef.K_LOW_P 		: indexLow/float(packetInfoDict["priceConv"]), 
					cDef.K_OPEN_P 		: indexOpen/float(packetInfoDict["priceConv"]),
					cDef.K_CLOSING_P 	: indexPrevClose/float(packetInfoDict["priceConv"]), 
					cDef.K_NPC_FROM_CP 	: (indexVal-indexPrevClose),
					cDef.K_BID_ASK_DICT	: {cDef.K_BID:[], cDef.K_ASK:[]} ,
					cDef.K_PERCENT_CHNG	: ((indexVal-indexPrevClose)/indexPrevClose) * 100, ## This should allways be 100.00
					# cDef.K_PERCENT_CHNG 	: int(round((indexValue_7207 - closingIndex_7207)*100 / closingIndex_7207, 2) * PRICE_CONV_100), ## This should not be calcu;ated in here because after market close price changes and we have to chaculate depending on close price
					cDef.K_PRICE_CONV 	: packetInfoDict["priceConv"], 
					cDef.K_BCH_TS 		: timestampBCH,
					cDef.K_BCH_PACKT_CODE: nseConf.NSE_T_CODE_7207,
					cDef.K_VTT 			: 0,
					cDef.K_TRADIN_STAT 	: tradeStat
			}

			except Exception, e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack2 exception:%s"%(LOG_unPack_2011, exc_tb.tb_lineno, str(e))
				return retDict
				# break ## Incase there is an exception you should not go further with invalid data
			
		retDict = {
					cDef.K_FUNCT_STAT 	: cDef.V_FUNCT_SUCCESS_1,
					cDef.K_FUN_DATA		: valDict,
					cDef.K_ERR_MSG		: ""
		}
		return retDict

	except Exception, e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unknown exception:%s"%(LOG_unPack_2011, exc_tb.tb_lineno, str(e))
	return retDict

def unPack_2012(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = False):
	"""
	BSE : All indices information is broadcasted using the message 2011 or 2012. The indices sent in message type 2011 will not be sent in 2012 and vice-versa during a trading day.
	"""
	try:
		retDict = {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "ERR : %s Unknown error."%(LOG_unPack_2012)}

		if len(inputPkt) < bse_conf.BSE_SENSEX_INDEX_BCAST_LEN_2012_HEAD:
			retDict[cDef.K_ERR_MSG] = "ERR : %s input packet length:%s is less than required length:%s."%(LOG_unPack_2012, len(inputPkt), bse_conf.BSE_SENSEX_INDEX_BCAST_LEN_2012_HEAD)
			return retDict
		
		try:
			(res4, res5, numRecord) = bse_conf.BSE_SENSEX_INDEX_BCAST_STRUCT_2012_HEAD.unpack(inputPkt[:bse_conf.BSE_SENSEX_INDEX_BCAST_LEN_2012_HEAD])
		except Exception, e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack1 exception:%s"%(LOG_unPack_2012, exc_tb.tb_lineno, str(e))
			return retDict
		
		if numRecord <= 0 or numRecord > bse_conf.BSE_SENSEX_INDEX_BCAST_2012_MAX_NUM_REC:
			retDict[cDef.K_ERR_MSG] = "ERR : %s Invalid number of records:%s max limit:%s."%(LOG_unPack_2012, numRecord, bse_conf.BSE_SENSEX_INDEX_BCAST_2012_MAX_NUM_REC)
			return retDict
		
		pointerIncri = bse_conf.BSE_SENSEX_INDEX_BCAST_LEN_2012_HEAD ## Counter to increment when there are multiple records
		# print "%s pointerIncri:%s len inp:%s bodyLen:%s"%(LOG_unPack_2012, pointerIncri, len(inputPkt), bse_conf.BSE_SENSEX_INDEX_BCAST_LEN_2012_BODY)
		# valList = []
		valDict = {}
		for eachRec in range(0, numRecord):
			try:
				(indexCode, indexHigh, indexLow, indexOpen, indexPrevClose, indexVal, indexID, res6, res7, res8, res9, res10, res11) = bse_conf.BSE_SENSEX_INDEX_BCAST_STRUCT_2012_BODY.unpack(inputPkt[pointerIncri:pointerIncri+bse_conf.BSE_SENSEX_INDEX_BCAST_LEN_2012_BODY])

				pointerIncri += bse_conf.BSE_SENSEX_INDEX_BCAST_LEN_2012_BODY
				# print "%s indexCode:%s, indexID:%s"%(LOG_unPack_2012, indexCode, indexID)
				tradeStat = 0
				if tradeStat == 0: ## TODO: Validate this
					tradeStat = 2
				indexCode = "%s%s000000%s"%(cDef.EXCHANGE_CODE_BSE, cDef.SEG_CODE_CM_LIVE_BSE, indexCode)
				valDict[indexCode] = {
					cDef.K_TOKEN 		: indexCode, 
					cDef.K_LTP 			: indexVal/float(packetInfoDict["priceConv"]), 
					cDef.K_HIGH_P		: indexHigh/float(packetInfoDict["priceConv"]), 
					cDef.K_LOW_P 		: indexLow/float(packetInfoDict["priceConv"]), 
					cDef.K_OPEN_P 		: indexOpen/float(packetInfoDict["priceConv"]),
					cDef.K_CLOSING_P 	: indexPrevClose/float(packetInfoDict["priceConv"]), 
					cDef.K_NPC_FROM_CP 	: (indexVal-indexPrevClose),
					cDef.K_BID_ASK_DICT	: {cDef.K_BID:[], cDef.K_ASK:[]} ,
					cDef.K_PERCENT_CHNG	: ((indexVal-indexPrevClose)/indexPrevClose) * 100, ## This should allways be 100.00
					# cDef.K_PERCENT_CHNG 	: int(round((indexValue_7207 - closingIndex_7207)*100 / closingIndex_7207, 2) * PRICE_CONV_100), ## This should not be calcu;ated in here because after market close price changes and we have to chaculate depending on close price
					cDef.K_PRICE_CONV 	: packetInfoDict["priceConv"], 
					cDef.K_BCH_TS 		: timestampBCH,
					cDef.K_BCH_PACKT_CODE: nseConf.NSE_T_CODE_7207,
					cDef.K_VTT 			: 0,
					cDef.K_TRADIN_STAT 	: tradeStat
			}

			except Exception, e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack2 exception:%s"%(LOG_unPack_2012, exc_tb.tb_lineno, str(e))
				return retDict
				# break ## Incase there is an exception you should not go further with invalid data
			
		retDict = {
					cDef.K_FUNCT_STAT 	: cDef.V_FUNCT_SUCCESS_1,
					cDef.K_FUN_DATA		: valDict,
					cDef.K_ERR_MSG		: ""
		}
		return retDict

	except Exception, e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unknown exception:%s"%(LOG_unPack_2012, exc_tb.tb_lineno, str(e))
	return retDict

def unPack_2016(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = False):
	"""
	BSE : VAR Percentages Broadcast message will be sent by CTE in a specific interval. The latest Instrument wise VAR and ELM VAR Percentages will be sent by CTE
	"""
	try:
		retDict = {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "ERR : %s Unknown error."%(LOG_unPack_2016)}

		if len(inputPkt) < bse_conf.BSE_VAR_PCT_BCAST_LEN_2016_HEAD:
			retDict[cDef.K_ERR_MSG] = "ERR : %s input packet length:%s is less than required length:%s."%(LOG_unPack_2016, len(inputPkt), bse_conf.BSE_VAR_PCT_BCAST_LEN_2016_HEAD)
			return retDict
		
		try:
			(res4, res5, numRecord) = bse_conf.BSE_VAR_PCT_BCAST_STRUCT_2016_HEAD.unpack(inputPkt[:bse_conf.BSE_VAR_PCT_BCAST_LEN_2016_HEAD])
		except Exception, e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack1 exception:%s"%(LOG_unPack_2016, exc_tb.tb_lineno, str(e))
			return retDict
		
		if numRecord <= 0 or numRecord > bse_conf.BSE_VAR_PCT_BCAST_2016_MAX_NUM_REC:
			retDict[cDef.K_ERR_MSG] = "ERR : %s Invalid number of records:%s max limit:%s."%(LOG_unPack_2016, numRecord, bse_conf.BSE_VAR_PCT_BCAST_2016_MAX_NUM_REC)
			return retDict
		
		pointerIncri = bse_conf.BSE_VAR_PCT_BCAST_LEN_2016_HEAD ## Counter to increment when there are multiple records
		valList = []
		for eachRec in range(0, numRecord):
			try:
				(instrCode, varIMPct, elmVarPct, res6, res7, res8, res9, ident, res10) = bse_conf.BSE_VAR_PCT_BCAST_STRUCT_2016_BODY.unpack(inputPkt[pointerIncri:pointerIncri+bse_conf.BSE_VAR_PCT_BCAST_LEN_2016_BODY])

				pointerIncri += bse_conf.BSE_VAR_PCT_BCAST_LEN_2016_BODY
				valList.append({
						instrCode:
						{
							cDef.K_TOKEN 	: instrCode,
							"varIMPct"		: varIMPct,
							"elmVarPct"		: elmVarPct
						}
					})
			except Exception, e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack2 exception:%s"%(LOG_unPack_2016, exc_tb.tb_lineno, str(e))
				return retDict
				# break ## Incase there is an exception you should not go further with invalid data
			
		retDict = {
					cDef.K_FUNCT_STAT 	: cDef.V_FUNCT_SUCCESS_1,
					cDef.K_FUN_DATA		: valList,
					cDef.K_ERR_MSG		: ""
		}
		return retDict

	except Exception, e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unknown exception:%s"%(LOG_unPack_2016, exc_tb.tb_lineno, str(e))
	return retDict

def unPack_2015(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = False):
	"""
	BSE : Open Interests Broadcast message will be sent by BOLTPLUS in a specific interval for the Derivatives instrument listed in the Exchange. The broadcast will be sent whenever there is change in the OI of an instrument. The OI will be additionally sent for all contracts multiple times during the day irrespective if there was any change in the OI. The Open Interest Value, and Change in Open Interest fields of respective derivatives instrument will be sent with other following details.
	"""
	try:
		retDict = {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "ERR : %s Unknown error."%(LOG_unPack_2015)}

		if len(inputPkt) < bse_conf.BSE_OPEN_INT_BCAST_LEN_2015_HEAD:
			retDict[cDef.K_ERR_MSG] = "ERR : %s input packet length:%s is less than required length:%s."%(LOG_unPack_2015, len(inputPkt), bse_conf.BSE_OPEN_INT_BCAST_LEN_2015_HEAD)
			return retDict
		
		try:
			(res4, res5, numRecord) = bse_conf.BSE_OPEN_INT_BCAST_STRUCT_2015_HEAD.unpack(inputPkt[:bse_conf.BSE_OPEN_INT_BCAST_LEN_2015_HEAD])
		except Exception, e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack1 exception:%s"%(LOG_unPack_2015, exc_tb.tb_lineno, str(e))
			return retDict
		
		if numRecord <= 0 or numRecord > bse_conf.BSE_OPEN_INT_BCAST_2015_MAX_NUM_REC:
			retDict[cDef.K_ERR_MSG] = "ERR : %s Invalid number of records:%s max limit:%s."%(LOG_unPack_2015, numRecord, bse_conf.BSE_OPEN_INT_BCAST_2015_MAX_NUM_REC)
			return retDict
		
		pointerIncri = bse_conf.BSE_OPEN_INT_BCAST_LEN_2015_HEAD ## Counter to increment when there are multiple records
		valList = []
		for eachRec in range(0, numRecord):
			try:
				(instrId, openInstrQty, openInstrVal, openInstrChng, res6, res7, res8, res9, res10, res11, res12) = bse_conf.BSE_OPEN_INT_BCAST_STRUCT_2015_BODY.unpack(inputPkt[pointerIncri:pointerIncri+bse_conf.BSE_OPEN_INT_BCAST_LEN_2015_BODY])

				pointerIncri += bse_conf.BSE_OPEN_INT_BCAST_LEN_2015_BODY

				valList.append({
						instrId:
						{
							cDef.K_TOKEN 	: instrId,
							"OIQty" 	: openInstrQty,
							"OIVal" 	: openInstrVal,
							"OIChng"	: openInstrChng
						}
					})
			except Exception, e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack2 exception:%s"%(LOG_unPack_2015, exc_tb.tb_lineno, str(e))
				return retDict
				# break ## Incase there is an exception you should not go further with invalid data
			
		retDict = {
					cDef.K_FUNCT_STAT 	: cDef.V_FUNCT_SUCCESS_1,
					cDef.K_FUN_DATA		: valList,
					cDef.K_ERR_MSG		: ""
		}
		return retDict

	except Exception, e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unknown exception:%s"%(LOG_unPack_2015, exc_tb.tb_lineno, str(e))
	return retDict

def unPack_2022(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = False):
	"""
	BSE : This message is used to disseminate the reference rate published by RBI for foreign exchange. The rate is published multiple times during the day. The date field specifies the date for which the rate is applicable. This field can be used to identify if the new rate is published by RBI.
	"""
	try:
		retDict = {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "ERR : %s Unknown error."%(LOG_unPack_2022)}

		if len(inputPkt) < bse_conf.BSE_RBI_REF_RATE_LEN_2022_HEAD:
			retDict[cDef.K_ERR_MSG] = "ERR : %s input packet length:%s is less than required length:%s."%(LOG_unPack_2022, len(inputPkt), bse_conf.BSE_RBI_REF_RATE_LEN_2022_HEAD)
			return retDict
		
		try:
			(res4, res5, numRecord) = bse_conf.BSE_RBI_REF_RATE_STRUCT_2022_HEAD.unpack(inputPkt[:bse_conf.BSE_RBI_REF_RATE_LEN_2022_HEAD])
		except Exception, e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack1 exception:%s"%(LOG_unPack_2022, exc_tb.tb_lineno, str(e))
			return retDict
		
		if numRecord <= 0 or numRecord > 100: ## This is to make sure it should not go to infinite loop incase we get invalid record.
			retDict[cDef.K_ERR_MSG] = "ERR : %s Invalid number of records:%s max limit:%s."%(LOG_unPack_2022, numRecord, 100)
			return retDict
		
		pointerIncri = bse_conf.BSE_RBI_REF_RATE_LEN_2022_HEAD ## Counter to increment when there are multiple records
		valList = []
		for eachRec in range(0, numRecord):
			try:
				(underAssetId, rbiRate, res6, res7, date, filler) = bse_conf.BSE_RBI_REF_RATE_STRUCT_2022_BODY.unpack(inputPkt[pointerIncri:pointerIncri+bse_conf.BSE_RBI_REF_RATE_LEN_2022_BODY])

				pointerIncri += bse_conf.BSE_RBI_REF_RATE_LEN_2022_BODY

				if   underAssetId == 600:
					None ## USD
				elif underAssetId == 601:
					None ## GBP
				elif underAssetId == 602:
					None ## JPY
				elif underAssetId == 603:
					None ## EUR
				else:
					None

				rbiRate = rbiRate/10000.0

				valList.append({
						underAssetId:{
							"rbiRate" 	: rbiRate
						}
					})
			except Exception, e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack2 exception:%s"%(LOG_unPack_2022, exc_tb.tb_lineno, str(e))
				return retDict
				# break ## Incase there is an exception you should not go further with invalid data
			
		retDict = {
					cDef.K_FUNCT_STAT 	: cDef.V_FUNCT_SUCCESS_1,
					cDef.K_FUN_DATA		: valList,
					cDef.K_ERR_MSG		: ""
		}
		return retDict

	except Exception, e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unknown exception:%s"%(LOG_unPack_2022, exc_tb.tb_lineno, str(e))
	return retDict

def unPack_2004(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = False):
	"""
	BSE : This message informs about the News entered at the CTE(Announcement Data or notices)
	"""
	try:
		retDict = {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "ERR : %s Unknown error."%(LOG_unPack_2004)}

		if len(inputPkt) < bse_conf.BSE_NEWS_HEAD_BCAST_LEN_2004:
			retDict[cDef.K_ERR_MSG] = "ERR : %s input packet length:%s is less than required length:%s."%(LOG_unPack_2004, len(inputPkt), bse_conf.BSE_NEWS_HEAD_BCAST_LEN_2004)
			return retDict
		
		try:
			(res4, res5, res6, newsCat, res7, newsId, newsHead, res8, res9, res10) = bse_conf.BSE_NEWS_HEAD_BCAST_STRUCT_2004.unpack(inputPkt[:bse_conf.BSE_NEWS_HEAD_BCAST_LEN_2004])
		except Exception, e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unpack1 exception:%s"%(LOG_unPack_2004, exc_tb.tb_lineno, str(e))
			return retDict
			
		retDict = {
					cDef.K_FUNCT_STAT 	: cDef.V_FUNCT_SUCCESS_1,
					cDef.K_FUN_DATA		: {
						"res4"		: res4, 
						"res5"		: res5,
						"res6"		: res6,
						"newsCat"	: newsCat,
						"res7"		: res7,
						"newsId"	: newsId,
						"newsHead"	: newsHead,
						"res8"		: res8,
						"res9"		: res9,
						"res10"		: res10
					},
					cDef.K_ERR_MSG		: ""
		}
		return retDict

	except Exception, e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unknown exception:%s"%(LOG_unPack_2004, exc_tb.tb_lineno, str(e))
	return retDict

def processBSEPackets(logFP_inst, inputPkt, fyTokenDict, failedTokenDict, tradeStat, packetInfoDict, printFlag = False, debugFlag = False):
	"""

	"""
	retDict = {cDef.K_FUNCT_STAT: cDef.V_FUNCT_FAIL_N_1, cDef.K_FUN_DATA: {}, cDef.K_ERR_MSG: "ERR : %s Unknown error."%(LOG_processBSEPackets)}

	try:
		(extra, lenData, slotNum) = bse_conf.BSE_CONST_HEADER_STRUCT.unpack(inputPkt[:bse_conf.BSE_CONST_HEADER_SIZE])
		# print "extra:%s, lenData:%s, slotNum:%s"%(extra, lenData, slotNum)
		inputPkt = inputPkt[bse_conf.BSE_CONST_HEADER_SIZE:]
		## Invalid length
		if len(inputPkt) <= bse_conf.BSE_TOTAL_BCAST_HEADER_LEN:
			retDict[cDef.K_ERR_MSG] = "ERR : %s Invalid input packet length"%(LOG_processBSEPackets)
			return retDict

		# print ' '.join(binascii.hexlify(inputPkt)[i:i+2] for i in xrange(0,len(binascii.hexlify(inputPkt)),2))
		# sys.exit()
		(msgType,) = bse_conf.BCAST_HEADER_MSG_TYPE_STRUCT.unpack(inputPkt[:bse_conf.BCAST_HEADER_MSG_TYPE_SIZE])
		if msgType not in bse_conf.BSE_BCAST_VALID_TRANS_CODE:
			retDict[cDef.K_ERR_MSG] = "ERR : %s Unknown transaction code: %s"%(LOG_processBSEPackets, msgType)
			return retDict
		inputPkt = inputPkt[bse_conf.BCAST_HEADER_MSG_TYPE_SIZE:]
		(res1, res2, res3, hour, minute, second, milliSec) = bse_conf.BSE_BCAST_HEADER_STRUCT.unpack(inputPkt[:bse_conf.BSE_BCAST_HEADER_LEN])
		inputPkt = inputPkt[bse_conf.BSE_BCAST_HEADER_LEN:]
		## Use the timestamp that is sent by the exchange as broadcast timestamp
		# print "msgType:%s, hour:%s, minute:%s, second:%s, milliSec:%s"%(msgType, hour, minute, second, milliSec)
		# dateTimeNow = datetime.datetime.now()
		## Since the date is not there in the header we are taking the date from market pic
		dateTimeNow = BSE_T.BSE_DATE
		timeBSE = datetime.datetime.strptime("%s-%s-%s-%s"%(hour, minute, second, milliSec), "%H-%M-%S-%f")
		dateTimeBCH = dateTimeNow.replace(hour=timeBSE.hour, minute=timeBSE.minute, second=timeBSE.second, microsecond=timeBSE.microsecond)
		# print "dateTimeBCH:", dateTimeBCH
		## TODO : Review before deployment
		timestampBCH = int(time.mktime(dateTimeBCH.timetuple())) ## Ajay 2019-05-09 Local this is workign good
		# timestampBCH = int(time.mktime(time.localtime(time.mktime(time.gmtime(time.mktime(dateTimeBCH.timetuple())))))) ## Since the machine is running in UTC converting time to localtime wont give you IST
		# print "timestampBCH: before :", timestampBCH
		# print "dateTimeNow, timestampBCH, dateTimeBCH:", dateTimeNow, timestampBCH, dateTimeBCH

		retdata = {}
		if msgType == bse_conf.BSE_TIME_BROADCAST_CODE_2001:
			## This is to update timestamp so unpacking is not needed.
			retdata = unPack_2001(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = printFlag)
			# print "2001: retdata", retdata
			# sys.exit()
		elif msgType == bse_conf.BSE_SESSION_CHANGE_CODE_2002 or msgType == bse_conf.BSE_SESSION_CHANGE_CODE_2003:
			retdata = unPack_2002(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = printFlag)
			# print "2002: retdata", retdata
			# sys.exit()
		elif msgType == bse_conf.BSE_MKT_PIC_CODE_2020:
			retdata = unPack_2020(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = printFlag)
			# for eachValue in retdata[cDef.K_FUN_DATA]:

			# if retdata[cDef.K_FUNCT_STAT] != cDef.V_FUNCT_SUCCESS_1:
			# 	logFP_inst.LogError(None, "%s->%s"%(LOG_processBSEPackets, retdata[cDef.K_ERR_MSG]), printFlag)
			# print "2020: retdata", retdata
		elif msgType == bse_conf.BSE_CLOSE_P_BCAST_CODE_2014:
			retdata = unPack_2014(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = printFlag)
			# print "2014: retdata", retdata
			# sys.exit()
		elif msgType == bse_conf.BSE_SENSEX_BCAST_CODE_2011:
			retdata = unPack_2011(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = printFlag)
			# print "2011: retdata", retdata
		elif msgType == bse_conf.BSE_SENSEX_INDEX_BCAST_CODE_2012:
			retdata = unPack_2012(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = printFlag)
			# print "2012: retdata", retdata
		elif msgType == bse_conf.BSE_VAR_PCT_BCAST_CODE_2016:
			retdata = unPack_2016(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = printFlag)
			# print "2016: retdata", retdata
		elif msgType == bse_conf.BSE_OPEN_INT_BCAST_CODE_2015:
			retdata = unPack_2015(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = printFlag)
			# print "2015: retdata", retdata
			# sys.exit()
		elif msgType == bse_conf.BSE_RBI_REF_RATE_CODE_2022:
			retdata = unPack_2022(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = printFlag)
			# print "2022: retdata", retdata
			# sys.exit()
		elif msgType == bse_conf.BSE_NEWS_HEAD_BCAST_CODE_2004:
			retdata = unPack_2004(logFP_inst, inputPkt, timestampBCH, fyTokenDict, failedTokenDict, packetInfoDict, printFlag = printFlag)
			# print "2004: retdata", retdata
			# sys.exit()
		else:
			# print "%s unknown msgType:%s"%(LOG_processBSEPackets, msgType)
			logFP_inst.LogError(None, "%s unknown msgType:%s"%(LOG_processBSEPackets, msgType), printFlag)
			# sys.exit()
		# print "retdata:", retdata
		# print "dateTimeBCH:", dateTimeBCH

		retdata['tcode'] = msgType
		return retdata
	except Exception, e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		retDict[cDef.K_ERR_MSG] = "ERR : %s Line:%s. Unknown exception:%s"%(LOG_processBSEPackets, exc_tb.tb_lineno, str(e))
	return retDict
	

def main():
	None

if __name__ == "__main__":
	main()