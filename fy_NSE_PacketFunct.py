"""
Author 		: Ajay A U [ajay@fyers.in]
Version 	: 2.0
Copyright 	: Fyers Securities
Web			: fyers.in
"""
#!/usr/bin/env python
import sys
import binascii
import time
import lzoz
# sys.path.append(r"../") # All the defines are kept in here

from fy_NSE_Config import *
import fy_comn_Funct as fyCmnFunct
from fy_comn_def import *
from fy_comn_memc_def import *

def process7207(logErr_inst, inputData, fyTokenDict, timestamp2_BCH, packetInfoDict, failedTokenDict, tradeStat, printFlag = False, debugFlag = False):
	"""
	[Function]  : Process 7207 only for CM segment (Index data).
	
	[Input] 	: 	logFilePtr 		-> Log file pointer (In case any logs are written)
				  	inputData 		-> Input data which will contain of 7207 packet.
				  	packetInfoDict	-> Will contain structure and length of the packet to be processed
				  	failedTokenDict -> Contain the dict for which fy tokens are not mapped.
				  	tradeStat		-> This is necessary because trading status is sent only whith 7208 data and we need to calculate min candles depending upon the market status.
				  	printFlag 		-> True/False= print/No_print
				  	debugFlag 		-> To print the error messages
	[Output]	: 	Returns a list of dict which will contain all the the index data.
	"""
	try:
		dataDict 	= {}
		numOfRecords = 0
		try:
			(numOfRecords,) = NSE_P_NUM_PACK_STRUCT.unpack(inputData[:NSE_P_NUM_PACK_SIZE])
		except Exception,e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			errMsg = "%s Line:%s. Cannont decode number of packets. Except:%s"%(ERROR_process7207, exc_tb.tb_lineno, str(e))
			logErr_inst.LogError(None, errMsg, printFlag)
			return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:dataDict, K_ERR_MSG:errMsg}
		if numOfRecords > 20: ## **IMP** If the number of packets in the payload exceed this number it will return an error.
			errMsg = "%s Number of packets found to be '%s' which exceeds the limit."%(ERROR_process7207, numOfRecords)
			logErr_inst.LogError(None, errMsg, printFlag)
			return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:dataDict, K_ERR_MSG:errMsg}
			
		inputData 		= inputData[NSE_P_NUM_PACK_SIZE:] ## increase buffer by the size of number of records
		pointerIncri = 0
		for everyRecord in range(0, numOfRecords):
			inputData = inputData[pointerIncri:] ## This is done at the begining since any continue statements make to loop on the same packet
			pointerIncri = NSE_P_7207_SIZE
			indexName_7207, unknown_7207, indexValue_7207, highIndexValue_7207, lowIndexValue_7207, openingIndex_7207, closingIndex_7207, percentChange_7207, yearlyHigh_7207, yearlyLow_7207, noOfUpmoves_7207, noOfDownmoves_7207, marketCapitalisation_7207, netChangeIndicator_7207, filler_7207 = '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', 0 
			try:
				(indexName_7207, unknown_7207, indexValue_7207, highIndexValue_7207, lowIndexValue_7207, 
				openingIndex_7207, closingIndex_7207, percentChange_7207, yearlyHigh_7207, yearlyLow_7207, 
				noOfUpmoves_7207, noOfDownmoves_7207, marketCapitalisation_7207, netChangeIndicator_7207,
				filler_7207) = NSE_P_7207_STRUCT.unpack(inputData[:NSE_P_7207_SIZE])
				# struct.unpack_from("%s%s"%(NSE_PACKET_ENDIANNESS, NSE_P_7207), inputData, 0)
				# print ' '.join(binascii.hexlify(inputData)[i:i+2] for i in xrange(0,len(binascii.hexlify(inputData)),2))
			except Exception,e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				errMsg = "%s Line:%s. While unpacking data. Except:%s"%(ERROR_process7207, exc_tb.tb_lineno, str(e))
				logErr_inst.LogError(None, errMsg, printFlag)
				continue
			## Testing with network packets so commented this. This is added in the network packet in special field called divide by
			# indexValue_7207, highIndexValue_7207, lowIndexValue_7207, openingIndex_7207, closingIndex_7207 , yearlyHigh_7207, yearlyLow_7207= indexValue_7207/PRICE_CONV_100, highIndexValue_7207/PRICE_CONV_100, lowIndexValue_7207/PRICE_CONV_100, openingIndex_7207/PRICE_CONV_100, closingIndex_7207/PRICE_CONV_100, yearlyHigh_7207/PRICE_CONV_100, yearlyLow_7207/PRICE_CONV_100
			
			# print "indexName_7207:", indexName_7207
			if openingIndex_7207 <= 0: ## This happens during pre market session
				highIndexValue_7207 = lowIndexValue_7207 = openingIndex_7207 = closingIndex_7207 = indexValue_7207
			fyToken = 0
			if indexName_7207 in FY_TOKEN_7207_DICT:
				fyToken = FY_TOKEN_7207_DICT[indexName_7207]
			else:
				if not(indexName_7207 in failedTokenDict):
					failedTokenDict[indexName_7207] = None
					logErr_inst.LogError(None, "%s index name %s not found in fyTokenDict."%(ERROR_process7207, indexName_7207), printFlag)
				continue
			
			# cls_P = (indexValue_7207*100)/(percentChange_7207+100)
			# print "cls_P:",cls_P
			# if cls_P <= 0:
				# continue
			# if str(fyToken) == "101000000026000":
			# 	ErrMsg = "%s token:%s, timestamp2_BCH:%s, ltp:%s, day_high:%s day_low:%s day_open:%s volume:%s, closingPrice:%s"%(ERROR_process7208, fyToken, timestamp2_BCH, indexValue_7207, highIndexValue_7207, lowIndexValue_7207, openingIndex_7207, 0, closingIndex_7207)
			# 	logErr_inst.LogError(None, ErrMsg, printFlag)

			if tradeStat == 0: ## this is done because if we start after market hour when we dont get 7208 data 
				tradeStat = 2
			
			valDict = {
					K_TOKEN 		: fyToken, 
					K_LTP 			: indexValue_7207/float(packetInfoDict["priceConv"]), 
					K_HIGH_P		: highIndexValue_7207/float(packetInfoDict["priceConv"]), 
					K_LOW_P 		: lowIndexValue_7207/float(packetInfoDict["priceConv"]), 
					K_OPEN_P 		: openingIndex_7207/float(packetInfoDict["priceConv"]),
					K_CLOSING_P 	: closingIndex_7207/float(packetInfoDict["priceConv"]), 
					K_NPC_FROM_CP 	: (indexValue_7207-closingIndex_7207),
					K_BID_ASK_DICT	: {K_BID:[], K_ASK:[]} ,
					K_PERCENT_CHNG	: percentChange_7207/100.00, ## This should allways be 100.00
					# K_PERCENT_CHNG 	: int(round((indexValue_7207 - closingIndex_7207)*100 / closingIndex_7207, 2) * PRICE_CONV_100), ## This should not be calcu;ated in here because after market close price changes and we have to chaculate depending on close price
					K_PRICE_CONV 	: PRICE_CONV_100, 
					K_BCH_TS 		: timestamp2_BCH,
					K_BCH_PACKT_CODE: NSE_T_CODE_7207,
					K_VTT 			: 0,
					K_TRADIN_STAT 	: tradeStat
			}
			dataDict[fyToken] = valDict
			## debug Info
			# if fyToken == 101000000026000:
			# 	print "%s ltp:%s, closing:%s"%(ERROR_process7207, valDict[K_LTP], valDict[K_CLOSING_P])
			# print ' '.join(binascii.hexlify(inputData)[i:i+2] for i in xrange(0,len(binascii.hexlify(inputData)),2))
			# print "indexName_7207:%s, percentChange_7207:%s, K_LTP:%s, K_CLOSING_P:%s"%(indexName_7207, percentChange_7207, valDict[K_LTP], valDict[K_CLOSING_P])
			# print "valDict:", valDict
			# sys.exit()
			# if indexName_7207.lower().startswith("nifty 50 tr 2x lev"):
				# None
				# print "indexValue_7207 :%s, percentChange_7207:%s, cls_P:%s"%(indexValue_7207, percentChange_7207, cls_P)
				# print "valDict:%s"%(valDict)
				# print
			#print("dataDict-->7202 ", dataDict)
			# print binascii.hexlify(filler_7207)
		return {K_FUNCT_STAT: V_FUNCT_SUCCESS_1, K_FUN_DATA: dataDict, K_ERR_MSG: numOfRecords}
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Unknown. Except:%s"%(ERROR_process7207, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag)
		return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA:dataDict, K_ERR_MSG:errMsg}
	return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA:{}, K_ERR_MSG: "%s Unknown error"%(ERROR_process7207)}

def process7208(logErr_inst, inputData, fyTokenDict, timestamp2_BCH, packetInfoDict, failedTokenDict, printFlag=False, debugFlag = False):
	"""
	[Function] 	: Process 7208 for all the segments[CM/FO/CD].
	
	[Input] 	: logFilePtr 	-> Log file pointer (In case any logs are written)
				  inputData 	-> Input data which will contain of 7208 packet.
				  fyTokenDict	-> Dictionary containing  all the NSE tokens mapped to Fyers tokens
				  timestamp2_BCH-> Timestamp that is sent by NSE in the header
				  packetInfoDict-> Will contain structure and length of the packet to be processed
				  failedTokenDict-> contians tokens for which fyers token were not found
	[Output]	: Returns a list which contain dict of all the the paackets that are unpacked.
	[Devel]		:
					# {K_TOKEN:token, K_BOOK_T:bookType, K_TRADING_STAT:tradingStatus, K_VTT:volTradedToday, K_LTP:lastTradedPrice, K_NET_CHANGE_I:netChangeIndicator, K_NPC_FROM_CP:netPChangeFromClosePrice, K_LTQ:lastTradeQty, K_LTT:lastTradeTime, K_ATP:avgTradePrice, K_AUCT_N:auctionNumber, K_AUCT_STAT:auctionStatus, K_INITR_T:initiatorType, K_INITR_P:initiatorPrice, K_INITR_Q:initiatorQty, K_AUCT_P:auctionPrice, K_AUCT_Q:auctionQty, K_BB_TOT_BUY_F:bbTotalBuyFlag, K_BB_TOT_SELL_F:bbTotalSellFlag, K_TOT_BUY_Q:totalBuyQty, K_TOT_SELL_Q:totalSellQty, K_MBP_INDIC_BIT:MbpIndicatorBits, K_MBP_INDIC_RES:MbpIndicatorReserved, K_CLOSING_P:closingPrice, K_OPEN_P:openPrice, K_HIGH_P:highPrice, K_LOW_P:lowPrice, K_BID_ASK_DICT:{K_BID:bidList, K_ASK:askList}, K_PERCENT_CHNG : netPChangeFromClosePrice / closingPrice }
	"""
	try:
		#print("packetInfoDict7208--> ", packetInfoDict)
		#('packetInfoDict7208--> ', {'packetStruct_7208': <Struct object at 0x7fdbd1897ed8>, 'listenPort': 1982, 'secInfoSize_6511': 34, 'timestr': datetime.datetime(1900, 1, 1, 8, 0), 'packetSize_7208': 214, 'packetStruct_7208_NEW': <Struct object at 0x7fdbd1897f10>, 'packetSize_7208_NEW': 214, 'procThreadCount': 1, 'inputSegment': 'CD', 'sendThreadCount': 2, 'multiSendPort': 10002, 'roundoff': 4, 'priceConv': 10000000.0, 'expectedCnetId': 6})
		dataDict = {}
		# print ' '.join(binascii.hexlify(inputData)[i:i+2] for i in xrange(0,len(binascii.hexlify(inputData)),2))
		numOfRecords = 0
		try:
			(numOfRecords,) = NSE_P_NUM_PACK_STRUCT.unpack(inputData[:NSE_P_NUM_PACK_SIZE])
		except Exception,e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			errMsg = "%s Line:%s .Cannot decode number of records. Exception:%s"%(ERROR_process7208, exc_tb.tb_lineno, str(e))
			return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:dataDict, K_ERR_MSG:errMsg}
		finally:
			None
		## debug Info
		# print "cnetId_rx_NH:%s"%(packetInfoDict["expectedCnetId"])
		# print ' '.join(binascii.hexlify(inputData)[i:i+2] for i in xrange(0,len(binascii.hexlify(inputData)),2))
		# print "numOfRecords:%s, packetInfoDict['packetSize_7208']:%s"%(numOfRecords, packetInfoDict["packetSize_7208"])
		# sys.exit()
		
		if numOfRecords > 5: ## **IMP** If the number of packets in the payload exceed this number it will return an error.
			errMsg = "%s Number of records found to be '%s'. which exceeds the limit."%(ERROR_process7208, numOfRecords)
			return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:dataDict, K_ERR_MSG:errMsg}
		
		inputData 		= inputData[NSE_P_NUM_PACK_SIZE:] ## increase buffer by the size of number of records
		
		incrementPtr = 0
		for everyRecord in range(0, numOfRecords):
			# print ' '.join(binascii.hexlify(inputData[:packetInfoDict["packetSize_7208"]])[i:i+2] for i in xrange(0,len(binascii.hexlify(inputData[:packetInfoDict["packetSize_7208"]])),2))
			inputData = inputData[incrementPtr:] ## This is done at the begining since any continue statements make to loop on the same packet
			incrementPtr = packetInfoDict["packetSize_7208"] ## This is new code added on 2017-12-15 and has to be tested
			token, bookType, tradingStatus, volTradedToday, lastTradedPrice, netChangeIndicator, unknown_extra, netPChangeFromClosePrice, lastTradeQty, lastTradeTime, avgTradePrice, auctionNumber, auctionStatus, initiatorType, initiatorPrice, initiatorQty, auctionPrice, auctionQty, MBP_INFO_7208, bbTotalBuyFlag, bbTotalSellFlag, extraBuy4_, totalBuyQty, tBuyExtra, extraSell4_, totalSellQty, tSellExtra, MbpIndicatorBits, MbpIndicatorReserved, closingPrice, openPrice, highPrice, lowPrice = 0, 0, 0, 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
			try:
				(token, bookType, tradingStatus, volTradedToday, lastTradedPrice, netChangeIndicator, unknown_extra,
				netPChangeFromClosePrice, lastTradeQty, lastTradeTime, avgTradePrice, auctionNumber, auctionStatus, 
				initiatorType, initiatorPrice, initiatorQty, auctionPrice, auctionQty, MBP_INFO_7208, bbTotalBuyFlag, 
				bbTotalSellFlag, totalBuyQty,  totalSellQty,MbpIndicatorBits, closingPrice, openPrice, highPrice, 
				lowPrice) = packetInfoDict["packetStruct_7208_NEW"].unpack(inputData[:packetInfoDict["packetSize_7208"]])
#				if token == 1899:
#					print "totalBuyQty  ==========  %s" %(totalBuyQty)
#					print "totalSellQty =========== %s" %(totalSellQty)
#					print "MbpIndicatorBits ========= %s" %(MbpIndicatorBits)
##					print "closingPrice =========== %s" %(closingPrice)
##					print "openPrice ================== %s"  %(openPrice)
##					print "closingPrice =========== %s"  %(highPrice)
##					print "lowPrice ================= %s" %(lowPrice)
#					print "lastTradedPrice ========== %s" %(lastTradedPrice)
				## Debug info
				# if token == 3045:
				# 	hexdata = ' '.join(binascii.hexlify(inputData[:packetInfoDict["packetSize_7208"]])[i:i+2] for i in xrange(0,len(binascii.hexlify(inputData[:packetInfoDict["packetSize_7208"]])),2))
				# 	print ERROR_process7208, hexdata
				# 	print "%s totalBuyQty:%s, totalSellQty:%s"%(ERROR_process7208, totalBuyQty, totalSellQty)
				# 	reqPack = inputData[178: 178+8]
				# 	totBuy = ' '.join(binascii.hexlify(reqPack)[i:i+2] for i in xrange(0,len(binascii.hexlify(reqPack)),2))
				# 	print "%s totBuy:%s"%(ERROR_process7208, totBuy)
				# 	s = struct.Struct('>L')
				# 	unpacked_data = s.unpack(reqPack[1:5])
				# 	print "%s unpacked_data:%s"%(ERROR_process7208, unpacked_data)

				# tradingStatus=6 at 9:05
				if lastTradeTime > 0: ## New change Ajay 2018-06-01
					lastTradeTime += SECONDS_1970TO1980
					lastTradeTime = int(time.mktime(time.localtime(time.mktime(time.gmtime(lastTradeTime)))))

				if timestamp2_BCH < lastTradeTime: ## New change Ajay 2018-06-01
					timestamp2_BCH = lastTradeTime
				# print "tradingStatus:%s, lastTradeTime:%s, auctionQty:%s for token:%s"%(tradingStatus, lastTradeTime, auctionQty, token)
				# lastTradeTime = int(time.mktime(time.gmtime(lastTradeTime))) ## This is necessary because NSE sends the timestamp which is in IST and chart wants the timestamp in GMT
				# print lastTradeTime
				# sys.exit()
			except Exception,e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				errMsg = "%s Line:%s, Cannot decode values. Except:%s"%(ERROR_process7208, exc_tb.tb_lineno, str(e))
				logErr_inst.LogError(None, errMsg, printFlag)
				continue
			finally:
				None
			
			## Testing with network packets so commented this. This in included in special field called devide by in network packet.
			# lastTradedPrice, netPChangeFromClosePrice, closingPrice, openPrice, highPrice, lowPrice, avgTradePrice = lastTradedPrice/packetInfoDict["priceConv"], netPChangeFromClosePrice/packetInfoDict["priceConv"], closingPrice/packetInfoDict["priceConv"], openPrice/packetInfoDict["priceConv"], highPrice/packetInfoDict["priceConv"], lowPrice/packetInfoDict["priceConv"], avgTradePrice/packetInfoDict["priceConv"]
			
			fyToken = str(token)
			try:
				fyToken = fyTokenDict[str(token)]
			except Exception,e:
				if str(token) not in failedTokenDict:
					failedTokenDict[str(token)] = None ## we can put the error count here if needed.
					logErr_inst.LogError(None, "%s token %s not found in fyDict no errors will be logged for this again. Except:%s"%(ERROR_process7208, token, e), printFlag) ## Commented for testing on 2018-06-01. Uncomment in ** LIVE ** 
				else:
					None
				continue
			finally:
				None

			## **************** New code Palash 2018-08-31 ****************
			## LTP can be zero if there are no trades and the bid/ask hand othere values have changed.
			## If previous close is also zero along with the OHLCV the script is discarded.
			if lastTradedPrice <= 0:
				if openPrice <= 0 and lowPrice <= 0 and highPrice <= 0 and volTradedToday <= 0:
					if closingPrice <= 0:
						ErrMsg = "%s Packet discarded for token:%s, timestamp2_BCH:%s, ltp:%s, day_high:%s day_low:%s day_open:%s volume:%s, closingPrice:%s"%(ERROR_process7208, fyToken, timestamp2_BCH, lastTradedPrice, highPrice, lowPrice, openPrice, volTradedToday, closingPrice)
						logErr_inst.LogError(None, ErrMsg, printFlag)
						continue
			## **************** END: New code Palash 2018-08-31 ****************
			
			bidList = []
			incriMBP = 0
			for eachItem in range(0, NSE_P_7208_MBP_COUNT/2):
				qtyMBP, priceMBP, numOrdersMBP, bbBuySellFalgMBP = 0, 0, 0, ''
				try:
					MBP_INFO_7208 = MBP_INFO_7208[incriMBP:]
					incriMBP 	= NSE_P_7208_MBP_INF_SIZE
				except Exception,e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					errMsg = "%s Line:%s. Cannot move bid pointer. Except:%s"%(ERROR_process7208, exc_tb.tb_lineno, str(e))
					logErr_inst.LogError(None, errMsg, printFlag)
					continue
				finally:
					None
				try:
					(qtyMBP, priceMBP, numOrdersMBP, bbBuySellFalgMBP) = NSE_P_7208_MBP_INF_STRUCT.unpack(MBP_INFO_7208[:NSE_P_7208_MBP_INF_SIZE])
					# priceMBP = priceMBP/packetInfoDict["priceConv"]
					bidList.append({K_BID_ASK_QTY:qtyMBP, K_BID_ASK_P:priceMBP/float(packetInfoDict["priceConv"]), K_NUM_BID_ASK: numOrdersMBP})
				except Exception,e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					errMsg = "%s Line:%s. Cannot decode bid val. Except:%s"%(ERROR_process7208, exc_tb.tb_lineno, str(e))
					logErr_inst.LogError(None, errMsg, printFlag)
					continue
				finally:
					None
			
#			print "qtyMBP ============= %s" %(qtyMBP)
#			print "priceMBP ============= %s " %(priceMBP)
#			print "numOrdersMBP =========== %s" %(numOrdersMBP)
#			print "bbBuySellFalgMBP ========== %s" %(bbBuySellFalgMBP)
			askList = []
			incriMBP = 0
			for eachItem in range(0, NSE_P_7208_MBP_COUNT/2):
				qtyMBP, priceMBP, numOrdersMBP, bbBuySellFalgMBP = 0, 0, 0, ''
				try:
					MBP_INFO_7208 = MBP_INFO_7208[NSE_P_7208_MBP_INF_SIZE:]
					incriMBP = NSE_P_7208_MBP_INF_SIZE
				except Exception,e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					errMsg = "%s Line:%s. Cannot move ask val. Except:%s"%(ERROR_process7208, exc_tb.tb_lineno, str(e))
					logErr_inst.LogError(None, errMsg, printFlag)
					continue
				finally:
					None
				try:
					(qtyMBP, priceMBP, numOrdersMBP, bbBuySellFalgMBP) = NSE_P_7208_MBP_INF_STRUCT.unpack(MBP_INFO_7208[:NSE_P_7208_MBP_INF_SIZE])
					# priceMBP = priceMBP/packetInfoDict["priceConv"]
					askList.append({K_BID_ASK_QTY:qtyMBP, K_BID_ASK_P:priceMBP/float(packetInfoDict["priceConv"]), K_NUM_BID_ASK: numOrdersMBP})
				except Exception,e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					errMsg = "%s Line:%s. Cannot decode ask val. Except:%s"%(ERROR_process7208, exc_tb.tb_lineno, str(e))
					logErr_inst.LogError(None, errMsg, printFlag)
					continue
				finally:
					None
			
			## debug Info
			# print "everyRecord:%s, token:%s"%(everyRecord, token)
			
			# cls_P = (lastTradedPrice*100)/(netPChangeFromClosePrice+100)
			# print "K_PERCENT_CHNG:%s"%(int(round((lastTradedPrice - closingPrice)*100 / closingPrice, 2)* PRICE_CONV_100))
			# print "K_NPC_FROM_CP:%s"%(netPChangeFromClosePrice)
			## New Change Ajay 2018-04-02. We should not do this because preopen of CM and normal market of FO/CD will be rejected.
			# if lastTradedPrice <=0 or lastTradeQty <= 0 or closingPrice <=0 or openPrice <=0 or highPrice <= 0 or lowPrice <=0:
			# 	errMsg = "%s token:%s, lastTradedPrice:%s ,lastTradeQty:%s, closingPrice:%s, openPrice:%s, highPrice:%s,lowPrice:%s"%(ERROR_process7208, token, lastTradedPrice ,lastTradeQty ,closingPrice ,openPrice ,highPrice ,lowPrice)
			# 	# logErr_inst.LogError(None, errMsg, printFlag)
			# 	continue ## we need to verify this
			# pctChange = 0
			# if closingPrice > 0:
			# 	int(round((lastTradedPrice - closingPrice)*100 / closingPrice, 2) * PRICE_CONV_100)
#			if token == 6109:
#				print("closing === " ,  closingPrice/float(packetInfoDict["priceConv"]))
#				print("Opening === " ,  openPrice/float(packetInfoDict["priceConv"]))
#				print("highPrice === " ,  highPrice/float(packetInfoDict["priceConv"]))
#				print("lowPrice === " ,  lowPrice/float(packetInfoDict["priceConv"]))
			valDict = {
						K_TOKEN 		: token, 
						K_LTP 			: lastTradedPrice/float(packetInfoDict["priceConv"]), 
						K_LTQ 			: lastTradeQty, 
						K_LTT			: lastTradeTime, 
						K_NPC_FROM_CP 	: netPChangeFromClosePrice/float(packetInfoDict["priceConv"]),
						K_ATP 			: avgTradePrice/float(packetInfoDict["priceConv"]), 
						K_VTT			: volTradedToday, 
						K_TOT_BUY_Q		: totalBuyQty, 
						K_TOT_SELL_Q	: totalSellQty, 
						K_CLOSING_P		: closingPrice/float(packetInfoDict["priceConv"]),
						K_OPEN_P		: openPrice/float(packetInfoDict["priceConv"]),
						K_HIGH_P		: highPrice/float(packetInfoDict["priceConv"]),
						K_LOW_P			: lowPrice/float(packetInfoDict["priceConv"]), 
						K_BID_ASK_DICT	: {K_BID:bidList, K_ASK:askList} ,
						# K_PERCENT_CHNG 	: int(round((lastTradedPrice - closingPrice)*100 / closingPrice, 2) * PRICE_CONV_100), ## This should not be calculated in here because after market close price changes and we have to caculate depending on close price.
						K_PRICE_CONV	: packetInfoDict["priceConv"],
						K_BCH_TS		: timestamp2_BCH, 
						K_BCH_PACKT_CODE: NSE_T_CODE_7208,
						K_TRADIN_STAT 	: tradingStatus
						}
			dataDict[fyToken] = valDict
			# print "valDict:", valDict[K_LOW_P], valDict[K_HIGH_P]
			# print("7208 dics--> ",dataDict)
			# ('7208 dics--> ', {'10122101275532': {0: 5532, 33: 10000000.0, 34: 2, 3: 0, 4: 1.0825, 6: 1.0825, 7: 1, 8: 1608290975, 9: 0.0, 202: 7208, 201: 1608528390, 19: 106.0, 20: 631.0, 23: 1.0825, 24: 0.0, 25: 0.0, 26: 0.0, 27: {28: [{35: 1, 30: 1, 31: 0.95}, {35: 1, 30: 85, 31: 0.9475}, {35: 1, 30: 20, 31: 0.9325}, {35: 0, 30: 0, 31: 0.0}, {35: 0, 30: 0, 31: 0.0}], 29: [{35: 2, 30: 111, 31: 0.995}, {35: 1, 30: 20, 31: 1.035}, {35: 1, 30: 500, 31: 1.05}, {35: 0, 30: 0, 31: 0.0}, {35: 0, 30: 0, 31: 0.0}]}}})

		return {K_FUNCT_STAT : V_FUNCT_SUCCESS_1, K_FUN_DATA:dataDict, K_ERR_MSG:''}
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Unknown. Except:%s"%(ERROR_process7208, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag)
		return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:dataDict, K_ERR_MSG:errMsg}
	finally:
		None
	return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:{}, K_ERR_MSG:"%s Unknown error"%(ERROR_process7208)}

def process6511(logErr_inst, inputData, packetInfoDict, printFlag = False, debugFlag = False):
	"""
	[Function]  : Process market open/close packets
	
	[Input] 	: logFilePtr 	-> log file pointer
				  packetInfoDict-> Will contain structure and length of the packet to be processed
				  inputData 	-> data sent in NSE packet.
				  debugFlag 	-> To print debug messages
	[Output]	: dictionary containing the info.
	"""
	try:
		(mktType, broadcastDest, broadCastMsgLen, broadCastMsg) = NSE_P_6511_STRUCT.unpack(inputData[packetInfoDict["secInfoSize_6511"]:packetInfoDict["secInfoSize_6511"] + NSE_P_6511_SIZE])
		broadCastMsg = broadCastMsg[:broadCastMsgLen] ## New line Ajay 2018-02-22
		logErr_inst.LogError(None, "LOG: Mkt stat- mktType:%s, broadcastDest:%s, broadCastMsgLen:%s, broadCastMsg:%s"%(mktType, broadcastDest, broadCastMsgLen, broadCastMsg.rstrip()), printFlag)
		dataDict = {K_MKT_TYPE_6511:mktType, K_BCAST_DEST_6511:broadcastDest, K_BCAST_MSG_L_6511:broadCastMsgLen, K_BCAST_MSG_6511:broadCastMsg.rstrip(), K_BCH_PACKT_CODE: NSE_T_CODE_6511}
		return {K_FUNCT_STAT : V_FUNCT_SUCCESS_1, K_FUN_DATA:dataDict, K_ERR_MSG:''}
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Unknown. Except:%s"%(ERROR_process6511, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag)
		return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:{}, K_ERR_MSG:errMsg}
	return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:{}, K_ERR_MSG:"%s Unknown error"%(ERROR_process6511)}

def process6501(logErr_inst, inputData, packetInfoDict, printFlag = False, debugFlag = False):
	"""
	********************** This function is not yet implimented properly ********************** 
	[Function]  : Process market open/close packets
	
	[Input] 	: logFilePtr 	-> log file pointer
				  packetInfoDict-> Will contain structure and length of the packet to be processed
				  inputData 	-> data sent in NSE packet.
				  debugFlag 	-> To print debug messages
	[Output]	: dictionary containing the info.
	"""
	try:
		# inputData = inputData[:packetInfoDict["secInfoSize_6511"]]
		# print "process6511()-> len inputData:%s" %(len(inputData))
		# rawPacket6501 = ' '.join(binascii.hexlify(inputData)[i:i+2] for i in xrange(0,len(binascii.hexlify(inputData)),2))## For testing 2018-03-09
		# logErr_inst.LogError(None, "6501:%s"%(rawPacket6501), printFlag) ## For testing 2018-03-09
		(branchNum, brokerNum, actionCode, Reserved, broadcastDest, broadCastMsgLen, broadCastMsg) = NSE_P_6501_STRUCT.unpack(inputData[:NSE_P_6501_SIZE-40]) ## removed 40 because we removed broadcast header
		# broadCastMsg = broadCastMsg[:broadCastMsgLen] ## New line Ajay 2018-02-22 ## Commented on 2018-03-09
		# logErr_inst.LogError(None, "LOG: branchNum:%s, brokerNum:%s, actionCode:%s, Reserved:%s, broadcastDest:%s, broadCastMsgLen:%s, broadCastMsg:%s"%(branchNum, brokerNum, actionCode, Reserved, broadcastDest, broadCastMsgLen, broadCastMsg), printFlag)
		dataDict = {K_MKT_TYPE_6511:branchNum, K_BCAST_DEST_6511:broadcastDest, K_BCAST_MSG_L_6511:broadCastMsgLen, K_BCAST_MSG_6511:broadCastMsg.rstrip(), K_BCH_PACKT_CODE: NSE_T_CODE_6501}
		return {K_FUNCT_STAT : V_FUNCT_SUCCESS_1, K_FUN_DATA:dataDict, K_ERR_MSG:''}
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Unknown. Except:%s"%(ERROR_process6501, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag)
		return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:{}, K_ERR_MSG:errMsg}
	return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:{}, K_ERR_MSG:"%s Unknown error"%(ERROR_process6501)}


def process7202(logErr_inst, inputData, fyTokenDict, timestamp2_BCH, packetInfoDict, failedTokenDict, tradeStat, printFlag=False, debugFlag = False):
	"""
	[Function]  : 
	
	[Input] 	: 	logFilePtr 		-> Log file pointer (In case any logs are written)
				  	inputData 		-> Input data which will contain of 7207 packet.
				  	packetInfoDict	-> Will contain structure and length of the packet to be processed
				  	failedTokenDict -> Contain the dict for which fy tokens are not mapped.
				  	tradeStat		-> This is necessary because trading status is sent only whith 7208 data and we need to calculate min candles depending upon the market status.
				  	printFlag 		-> True/False= print/No_print
				  	debugFlag 		-> To print the error messages
	[Output]	: 	Returns a list of dict which will contain all the the index data.
	"""
	try:
		#print("inputData--> ", inputData)
		dataDict 	= {}
		numOfRecords = 0
		try:
			(numOfRecords,) = NSE_P_NUM_PACK_STRUCT.unpack(inputData[:NSE_P_NUM_PACK_SIZE])
		except Exception,e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			errMsg = "%s Line:%s. Cannont decode number of packets. Except:%s"%(ERROR_process7202, exc_tb.tb_lineno, str(e))
			logErr_inst.LogError(None, errMsg, printFlag)
			return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:dataDict, K_ERR_MSG:errMsg}
		finally: 
			None
		if numOfRecords > 17: ## **IMP** If the number of packets in the payload exceed this number it will return an error.
			errMsg = "%s Number of packets found to be '%s' which exceeds the limit."%(ERROR_process7202, numOfRecords)
			logErr_inst.LogError(None, errMsg, printFlag)
			return {K_FUNCT_STAT : V_FUNCT_FAIL_N_1, K_FUN_DATA:dataDict, K_ERR_MSG:errMsg}
			
		inputData 		= inputData[NSE_P_NUM_PACK_SIZE:] ## increase buffer by the size of number of records
		pointerIncri = 0
		for everyRecord in range(0, numOfRecords):
			inputData = inputData[pointerIncri:] ## This is done at the begining since any continue statements make to loop on the same packet
			pointerIncri = packetInfoDict["packetSize_7208"]
			if len(inputData) < NSE_P_7202_INF_SIZE:
				errMsg = "%s Length less than expected. Input len:%s, expected len:%s"%(ERROR_process7202, len(inputData), NSE_P_7202_INF_SIZE)
				logErr_inst.LogError(None, errMsg, printFlag)
				continue
				
			token, mktType, fillP, fillVol, oi, dayHiOI, dayLoOi = 0, 0, 0, 0, 0, 0, 0
			try:
				(token, mktType, fillP, fillVol, oi, dayHiOI, dayLoOi) = NSE_P_7202_INF_STRUCT.unpack(inputData[:NSE_P_7202_INF_SIZE])

			except Exception,e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				errMsg = "%s Line:%s. While unpacking data. Except:%s"%(ERROR_process7202, exc_tb.tb_lineno, str(e))
				logErr_inst.LogError(None, errMsg, printFlag)
				continue
			# print(token, mktType, fillP, fillVol, oi, dayHiOI, dayLoOi)
			# (2169, 1, 350000, 25, 130072, 132555, 109869)
			# (2850000, 0, 327681, 2764898305, 2764898305, 1981808640, 601686017)

			fyToken = str(token)
			try:
				fyToken = fyTokenDict[str(token)]
				#print("fyTokenDict--> ", fyTokenDict)
				#'7272_oi': '0.0', '11427_oi': '0.0', '11542': '101221010811542', '11543': '101221010811543'
				# Previous OI value updated by Megha 27-01-2020
				if str(token)+'_oi' in fyTokenDict:
					prev_oi = fyTokenDict[str(token)+'_oi']

			except Exception,e:
				if str(token) not in failedTokenDict:
					failedTokenDict[str(token)] = None ## we can put the error count here if needed.
					logErr_inst.LogError(None, "%s token %s not found in fyDict no errors will be logged for this again. Except:%s"%(ERROR_process7202, token, e), printFlag)
			if tradeStat == 0: ## this is done because if we start after market hour when we dont get 7208 data 
				tradeStat = 2
			
			valDict = {
			
						# K_TOKEN_OI		: token,
						# K_FILLP_OI		: fillP,
						# K_FILLVOL_OI 	: fillVol,
						# K_OI 			: oi,
						# K_DAYHI_OI		: dayHiOI,
						# K_DAYLO_OI 		: dayLoOi,
						# K_MKT_TYPE_0I 	: mktType,
						# #K_PRICE_CONV	: packetInfoDict["priceConv"],
						# K_BCH_TS		: timestamp2_BCH, 
						# K_BCH_PACKT_CODE: NSE_T_CODE_7202,
						#K_TRADIN_STAT 	: tradingStatus 
						K_MEMC_OI_TOKEN		: token,
						K_MEMC_OI_FILLP		: fillP,
						K_MEMC_OI_FILLVOL 	: fillVol,
						K_MEMC_OI 			: oi,
						K_MEMC_OI_DAYHI		: dayHiOI,
						K_MEMC_OI_DAYLO 		: dayLoOi,
						K_MKT_TYPE_0I 		: mktType,
						#K_PRICE_CONV		: packetInfoDict["priceConv"],
						K_BCH_TS			: timestamp2_BCH, 
						K_BCH_PACKT_CODE	: NSE_T_CODE_7202,
						K_TRADIN_STAT 		: tradeStat,
						K_MEMC_OI_Prev  	: prev_oi
			}
			dataDict[fyToken] = valDict
			# print "fyToken:%s, valDict:%s"%(fyToken, valDict)
			#print("502 7202 dics--> ",dataDict)
			# (('502 7202 dics--> ', {'10128001011487': {'fp': 737650000, 'ch': '0.0', 'ft': 1487, 'fv': 1, 201: 1608528407, 202: 7202, 34: 2, 'dhi': 4910452, 'oi': 4903203, 43: 1, 'dlo': 4867415}})

		return {K_FUNCT_STAT: V_FUNCT_SUCCESS_1, K_FUN_DATA: dataDict, K_ERR_MSG: numOfRecords}
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Unknown. Except:%s"%(ERROR_process7202, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag)
		return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA:dataDict, K_ERR_MSG:errMsg}
	return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA:{}, K_ERR_MSG: "%s Unknown error"%(ERROR_process7202)}



def processNSEPacket(logErr_inst, inputData, fyTokenDict, packetInfoDict, failedTokenDict, tradeStat, printFlag = False, debugFlag = False):
	"""
	[Function]  : This function will process NSE packet and process it according to transaction code.
					* Decompress the packet if Compressed. 
					* Check for the transaction code.
					* Process the packet according to transaction code.
					* Create a dict which contain all the details send by exchange and return a dict
	
	[Input] 	: logFilePtr 	-> log file pointer
				  inputData 	-> data sent in NSE packet.
				  fyTokenDict 	-> Token dict containing NSE tokens mapped to fyers tokens
				  packetInfoDict-> Will contain structure and length of the packet to be processed
				  failedTokenDict-> Dict of tokens for which fyers tokens are not mapped.
				  tradeStat 	-> Trade status will be sent in 7208 packets depending on which we have to create the min values.
				  printFlag 	-> True/False = print/no_print 
				  debugFlag 	-> To print debug messages
				   
	[Output]	: dictionary containing the info.
	"""
	dataDict = {}
	try:
		cnetId_rx_NH, unused_NH, numOfPackets_NH = 0, 0, 0
		try:
			(cnetId_rx_NH, unused_NH, numOfPackets_NH) = NSE_PACKET_HEARER_STRUCT.unpack(inputData[:NSE_PACKET_HEARER_SIZE])
			# logErr_inst.LogError(None, "cnetId_rx_NH:%s, unused_NH:%s, numOfPackets_NH:%s"%(cnetId_rx_NH, unused_NH, numOfPackets_NH), printFlag) ## This is for testing and comment in ** LIVE **
		except Exception,e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			errMsg = "%s Line:%s. Exception while decoding NSE packet header. Exception:%s"%(ERROR_processNSEPacket, exc_tb.tb_lineno, str(e))
			logErr_inst.LogError(None, errMsg, printFlag)
			return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA: dataDict, K_ERR_MSG: errMsg}
		inputData = inputData[NSE_PACKET_HEARER_SIZE:] ## Incase of multiple packets in the same payload only compression length will the there in the next packet so jump 4 byte[len(cnetId_rx_NH+unused_NH+numOfPackets_NH)]

		if numOfPackets_NH > 49:
			errMsg = "%s number of packets in same payload is %s.Which is not possible."%(ERROR_processNSEPacket, numOfPackets_NH)
			logErr_inst.LogError(None, errMsg, printFlag)
			return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA: dataDict, K_ERR_MSG: errMsg}
		
		pointerIncri = 0
		while numOfPackets_NH > 0:
			numOfPackets_NH -= 1 ## VIP to avoide infinite loop
			compressnLen_NH = 0
			inputData = inputData[pointerIncri:] ## This is to itrate to the next packe. New code added
			try:
				(compressnLen_NH,) = NSE_P_COMPRSN_STRUCT.unpack(inputData[:NSE_P_COMPRSN_SIZE])
				if compressnLen_NH > 400 and numOfPackets_NH > 1: ## Since numOfPackets_NH already decremented
					errMsg = "%s Compressn len greater than 400: %s, numOfPackets_NH:%s"%(ERROR_processNSEPacket, compressnLen_NH, numOfPackets_NH)
					logErr_inst.LogError(None, errMsg, printFlag)
					return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA: dataDict, K_ERR_MSG: errMsg} ## 'return' is prefered over 'continue' coz max paxket size itself is 512
					
			except Exception,e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				errMsg = "%s Line:%s. Exception while decoding compression length. Exception:%s"%(ERROR_processNSEPacket, exc_tb.tb_lineno, str(e))
				logErr_inst.LogError(None, errMsg, printFlag)
				return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA: dataDict, K_ERR_MSG: errMsg} ## 'return' is prefered over 'continue' coz if compresstion length itself is not found then its a waste to continue with the packet

			inputData = inputData[NSE_P_COMPRSN_SIZE:] ## skip compression len by jumping 2 bytes

			dataPacket = ''*512
			# print "compressnLen_NH:", compressnLen_NH
			if compressnLen_NH > 512 or compressnLen_NH < 0: ## The max length of the packet that is send by NSE is 512. So compression len cannot be more than 512.
				errMsg = "%s Invalid compression length '%s' found."%(ERROR_processNSEPacket, compressnLen_NH)
				logErr_inst.LogError(None, errMsg, printFlag)
				return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA: dataDict, K_ERR_MSG: errMsg} ## 'return' is prefered over 'continue' coz max paxket size itself is 512
			if compressnLen_NH > 0:
				try:
					# logErr_inst.LogError(None, "compressnLen_NH:%s"%(compressnLen_NH), printFlag) ## This is for testing and comment in ** LIVE **
					# rawPack =  ' '.join(binascii.hexlify(inputData)[i:i+2] for i in xrange(0,len(binascii.hexlify(inputData)),2))## This is for testing and comment in ** LIVE **
					# logErr_inst.LogError(None, rawPack, printFlag) ## This is for testing and comment in LIVE
					# print "rawPack:", rawPack
					# sys.exit()
					## For testig indpu data is sent from [2:]
					# print "compressed" ## For testing
					# dataPacket = lzoz.decompressLZO1z(inputData[:compressnLen_NH]) ## if the data is proper lzo bytes are not sent to this the program will crash
					dataPacket = lzoz.decompressLZO1zSafe(inputData[:compressnLen_NH]) ## Ajay 2018-04-13 decompression safe throws an error if improper data is sent to decompress
					# packRecv =  ' '.join(binascii.hexlify(dataPacket)[i:i+2] for i in xrange(0,len(binascii.hexlify(dataPacket)),2))## This is for testing and comment in LIVE
					# logErr_inst.LogError(None, packRecv, printFlag) ## This is for testing and comment in LIVE
					pointerIncri = compressnLen_NH
					if dataPacket == None:
						## Since compressed packet and LZO failed go to next one
						logErr_inst.LogError(None, "%s LZO decompression failed and return is None"%(ERROR_processNSEPacket), printFlag)
						continue
				except Exception,e:
					## Since compressed packet and LZO failed go to next one
					exc_type, exc_obj, exc_tb = sys.exc_info()
					logErr_inst.LogError(None, "%s Line:%s. LZO decompression failed with exception:%s"%(ERROR_processNSEPacket, exc_tb.tb_lineno, str(e)), printFlag)
					continue
			elif compressnLen_NH == 0:
				dataPacket = inputData
			else:
				errMsg = "%s Unknown compression length '%s' found."%(ERROR_processNSEPacket, compressnLen_NH)
				logErr_inst.LogError(None, errMsg, printFlag)
				return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA: dataDict, K_ERR_MSG: errMsg} ## 'return' is prefered over 'continue' coz bad compression length.

			reserved_BCH, logTime_BCH, alphaChar_BCH, transCode_BCH, errorCode_BCH, bcSegNo_BCH, reserved1_BCH, ts2Unknown_BCH, timestamp2_BCH, jan1_1970_BCH, filler2_BCH, messLen_BCH = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
			try:
				dataPacket = dataPacket[UNUSED_BYTES_BC_H:] ## There are 8 unused bytes at the beginig
				(reserved_BCH, logTime_BCH, alphaChar_BCH, transCode_BCH, errorCode_BCH, 
				bcSegNo_BCH, reserved1_BCH, ts2Unknown_BCH, timestamp2_BCH, jan1_1970_BCH, 
				filler2_BCH, messLen_BCH) = NSE_BC_HEADER_STRUCT.unpack(dataPacket[:NSE_BC_HEADER_SIZE]) ## unpacking of the message headers
				# print ' '.join(binascii.hexlify(dataPacket)[i:i+2] for i in xrange(0,len(binascii.hexlify(dataPacket)),2))
				## This is importamnt to itrate to next packet. New code added
				# print "transCode_BCH:",transCode_BCH
				if (transCode_BCH == 6582 or transCode_BCH == 6501) and numOfPackets_NH > 0:## New change Ajay 2018-04-02. For these two transaction code the actual packet length is more than the one which is sent by exchange.
					## Improper message length is sent for 6582 in CM segment
					messLen_BCH += 8
					# logErr_inst.LogError(None, "transCode_BCH:%s, messLen_BCH:%s, numOfPackets_NH:%s"%(transCode_BCH, messLen_BCH, numOfPackets_NH), printFlag) # change Ajay 2018-03-26 ## Commented Ajay 2018-06-01
				if compressnLen_NH == 0: ## new addition Ajay 2018-02-12
					pointerIncri = messLen_BCH
			except Exception,e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				dataDict[numOfPackets_NH + 1] = {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA: dataDict, K_ERR_MSG: "%s Line:%s. Decoding broadcast header failed.Exception:%s"%(ERROR_processNSEPacket, exc_tb.tb_lineno, str(e))}
			## Check if there is an error code from Packets
			if errorCode_BCH != 0:
				if transCode_BCH in [7208,7207]: ## If error code is found for 7207/7208 only then log it.
					logErr_inst.LogError(None, "%s error code found to be:%s for trans code:%s."%(ERROR_processNSEPacket, errorCode_BCH, transCode_BCH), printFlag)
				dataDict[numOfPackets_NH + 1] = {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA: dataDict, K_ERR_MSG: "%s error code found to be:%s for trans code:%s."%(ERROR_processNSEPacket, errorCode_BCH, transCode_BCH)}
			if transCode_BCH in [7207, 1833, 7216] : ## we should consider timestamp as logTime because timestamp2 is not proper
				timestamp2_BCH = logTime_BCH

			if timestamp2_BCH > 0: ## New change Ajay 2018-06-01
				timestamp2_BCH += SECONDS_1970TO1980
				# print timestamp2_BCH
				# timestamp2_BCH = int(time.mktime(time.gmtime(timestamp2_BCH))) ## This is necessary because NSE sends the timestamp which is in IST and chart wants the timestamp in GMT
				timestamp2_BCH = int(time.mktime(time.localtime(time.mktime(time.gmtime(timestamp2_BCH))))) ## Since the machine is running in UTC converting time to localtime wont give you IST
				# print timestamp2_BCH
				# sys.exit()
			## debug Info
			# print ' '.join(binascii.hexlify(dataPacket)[i:i+2] for i in xrange(0,len(binascii.hexlify(dataPacket)),2))
			# print "transCode_BCH:%s, messLen_BCH:%s, errorCode_BCH:%s, timestamp2_BCH:%s, jan1_1970_BCH:%s"%(transCode_BCH, messLen_BCH, errorCode_BCH, timestamp2_BCH, jan1_1970_BCH)
			# sys.exit()

			# print "transCode_BCH:", transCode_BCH
			dataPacket = dataPacket[NSE_BC_HEADER_SIZE:]
			if transCode_BCH == NSE_T_CODE_7208:
				# print ' '.join(binascii.hexlify(dataPacket)[i:i+2] for i in xrange(0,len(binascii.hexlify(dataPacket)),2))
				returnDict = process7208(logErr_inst, dataPacket, fyTokenDict, timestamp2_BCH, packetInfoDict, failedTokenDict, printFlag, debugFlag)
				#print("returnDict-->7208 ", returnDict)
				# ('returnDict-->7208 ', {100: 1, 101: '', 102: {'10122104281168': {0: 1168, 33: 10000000.0, 34: 2, 3: 1008, 4: 74.72, 6: 74.595, 7: 3, 8: 1608528170, 9: 74.7431423, 202: 7208, 201: 1608528410, 19: 2261.0, 20: 1946.0, 23: 74.595, 24: 74.69, 25: 74.7975, 26: 74.6775, 27: {28: [{35: 1, 30: 72, 31: 74.7175}, {35: 2, 30: 30, 31: 74.715}, {35: 1, 30: 200, 31: 74.7125}, {35: 1, 30: 25, 31: 74.71}, {35: 2, 30: 127, 31: 74.705}], 29: [{35: 1, 30: 4, 31: 74.735}, {35: 2, 30: 20, 31: 74.7375}, {35: 1, 30: 200, 31: 74.7475}, {35: 1, 30: 28, 31: 74.75}, {35: 1, 30: 100, 31: 74.7575}]}}}})

				returnDict["tcode"] = transCode_BCH
				dataDict[numOfPackets_NH + 1] = returnDict

			elif transCode_BCH == NSE_T_CODE_7207:
				returnDict = process7207(logErr_inst, dataPacket, fyTokenDict, timestamp2_BCH, packetInfoDict, failedTokenDict, tradeStat, printFlag, debugFlag)
				#print("returnDict nse_pctfunct7207--> ", returnDict)
				# ('retPrevVal fy_util--> ', {100: 1, 101: '', 102: {'c': 71.29, 'dl': 71.14, 't': 1608528420, 'dh': 71.39, 'v': 114, 'h': 71.29, 'ft': '10122103191486-2003-1608508800', 'l': 71.285, 'o': 71.285, 'vtt': 14038}})

				returnDict["tcode"] = transCode_BCH
				dataDict[numOfPackets_NH + 1] = returnDict
			# elif transCode_BCH == NSE_T_CODE_7216:
			# 	returnDict = process7207(logErr_inst, dataPacket, fyTokenDict, timestamp2_BCH, packetInfoDict, failedTokenDict, tradeStat, printFlag, debugFlag)
			# 	returnDict["tcode"] = transCode_BCH
			# 	# print "returnDict:", returnDict
			# 	dataDict[numOfPackets_NH + 1] = returnDict

			elif transCode_BCH in NSE_STAT_TCODE_LIST: ## 6511, 6521, 6531, 6571, 6583, 6584 have similar struct as 6511
				returnDict = process6511(logErr_inst, dataPacket, packetInfoDict, printFlag, debugFlag)
				returnDict["tcode"] = transCode_BCH
				dataDict[numOfPackets_NH + 1] = returnDict
			elif transCode_BCH == NSE_T_CODE_6501:
				returnDict = process6501(logErr_inst, dataPacket, packetInfoDict, printFlag, debugFlag)
				returnDict["tcode"] = transCode_BCH
				dataDict[numOfPackets_NH + 1] = returnDict
			elif transCode_BCH == NSE_T_CODE_7202 and packetInfoDict.get('inputSegment' , '0') not in (SEG_NAME_CM_TEST , SEG_NAME_CM_LIVE):
				returnDict = process7202(logErr_inst, dataPacket, fyTokenDict, timestamp2_BCH, packetInfoDict, failedTokenDict, tradeStat, printFlag, debugFlag)
				#print("returnDict nse_pctfunct7202--> ", returnDict)
				# ('returnDict nse_pctfunct7202--> ', {100: 1, 101: 1, 102: {'10122112292170': {201: 1608528405, 37: 2170, 38: 1075000, 39: 4, 40: 91161, 41: 91161, 42: 84125, 43: 1, 202: 7202}}})

				returnDict["tcode"] = transCode_BCH
				dataDict[numOfPackets_NH + 1] = returnDict
			else:
				returnDict = dataDict[numOfPackets_NH + 1] = {K_FUNCT_STAT: V_FUNCT_SUCCESS_1, K_FUN_DATA: {}, K_ERR_MSG:'', "tcode": transCode_BCH} ## added for testing
		return {K_FUNCT_STAT: V_FUNCT_SUCCESS_1, K_FUN_DATA:dataDict, K_ERR_MSG:''}
		
	except Exception,e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errMsg = "%s Line:%s. Unknown exception:%s"%(ERROR_processNSEPacket, exc_tb.tb_lineno, str(e))
		logErr_inst.LogError(None, errMsg, printFlag)
		return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA: {}, K_ERR_MSG: errMsg}
	return {K_FUNCT_STAT: V_FUNCT_FAIL_N_1, K_FUN_DATA: {}, K_ERR_MSG: '%sUnknown error.'%(ERROR_processNSEPacket), "tcode": 0}
