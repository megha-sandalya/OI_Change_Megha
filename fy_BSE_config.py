#!/usr/bin/env python

## Long is considered 4 bytes and shot is considered as 2 bytes.

import sys
from struct import Struct

BSE_INP_PORT_LIVE_CM							= 2001
BSE_INP_PORT_LIVE_FO							= 2002
BSE_INP_PORT_LIVE_CD							= 2003
BSE_INP_PORT_TEST_CM							= 2001#2008
BSE_INP_PORT_TEST_FO							= 2009
BSE_INP_PORT_TEST_CD							= 2010

## *********************** Packet struct ***********************
BSE_ENDIAN 										= '<'

## *********************** Header ***********************
BSE_CONST_HEADER_FMT 							= "%s4s h h"%(BSE_ENDIAN)
BSE_CONST_HEADER_STRUCT							= Struct(BSE_CONST_HEADER_FMT)
BSE_CONST_HEADER_SIZE 							= 8
## These are the common fields in all packet format. So we will consider this as header.
## (msgType,) ## This will contain the transaction code. 
BCAST_HEADER_MSG_TYPE_FMT						= "%sL"%(BSE_ENDIAN)
BCAST_HEADER_MSG_TYPE_STRUCT 					= Struct(BCAST_HEADER_MSG_TYPE_FMT)
BCAST_HEADER_MSG_TYPE_SIZE 						= 4
## (res1, res2, res3, hour, minute, second, milliSec)
BSE_BCAST_HEADER_FMT 							= "%s2L H 4H"%(BSE_ENDIAN)
BSE_BCAST_HEADER_STRUCT 						= Struct(BSE_BCAST_HEADER_FMT)
BSE_BCAST_HEADER_LEN							= 18
BSE_TOTAL_BCAST_HEADER_LEN 						= BCAST_HEADER_MSG_TYPE_SIZE + BSE_BCAST_HEADER_LEN
## *********************** END : Header ***********************

## 1.1.112 : Time Broadcast [2001]
BSE_TIME_BROADCAST_CODE_2001					= 2001
## (msgType, res1, res2, res3, hour, minute, second, milliSec, res4, res5, res6, res7, res8, res9)
BSE_TIME_BROADCAST_FMT_2001						= "%s3H c c 2s"%(BSE_ENDIAN)
BSE_TIME_BROADCAST_STRUCT_2001					= Struct(BSE_TIME_BROADCAST_FMT_2001)
BSE_TIME_BROADCAST_LEN_2001						= 10 #32

## 1.1.113 Session Change Broadcast [2002] or [2003]
BSE_SESSION_CHANGE_CODE_2002					= 2002
BSE_SESSION_CHANGE_CODE_2003					= 2003
## (msgType, res1, res2, res3, hour, minute, second, milliSec, prodId, res4, filler, mktType, sessnNum, res5, startEndFlag, res6, res7)
BSE_SESSION_CHANGE_FMT_2002						= "%s5H L c c 2s"%(BSE_ENDIAN)
BSE_SESSION_CHANGE_STRUCT_2002					= Struct(BSE_SESSION_CHANGE_FMT_2002)
BSE_SESSION_CHANGE_LEN_2002						= 18 #40

## 1.1.114 Market Picture Broadcast [2020]
BSE_MKT_PIC_CODE_2020							= 2020
## (msgType, res1, res2, res3, hour, minute, second, milliSec, res4, res5, numRecord)
BSE_MKT_PIC_FMT_2020_HEAD						= "%s3H"%(BSE_ENDIAN)
BSE_MKT_PIC_STRUCT_2020_HEAD					= Struct(BSE_MKT_PIC_FMT_2020_HEAD)
BSE_MKT_PIC_LEN_2020_HEAD						= 6
## (instrCode, openRate, prevCloseRate, highRate, lowRate, noOfTrades, volume, value, lastTradeQty, lastTradeP, closeRate, blockDealRefP, indicativeEqlibmP, indicativeEqbmQty, timestamp, totalBidQty, totalOfferQty, tradeValFlag, filler, res1, res2, lowCktLim, upperCktLim, weightAvg, mktType, sessionNum, htpHour, ltpMin, ltpSec, ltpMillSec, res3, res4, noPricePts)
# Following is a market picture structure appearing repeatedly (Max 6 times)
BSE_MKT_PIC_2020_BODY_MAX_NUM_REC				= 6
BSE_MKT_PIC_FMT_2020_BODY						= "%s 14L q 2L c c c c 3L 2H B B B 3s 2s 2H"%(BSE_ENDIAN)
BSE_MKT_PIC_STRUCT_2020_BODY 					= Struct(BSE_MKT_PIC_FMT_2020_BODY)		
BSE_MKT_PIC_LEN_2020_BODY						= 104
## Following sub-structure will repeat number of times as specified in the 'No. of Price points'(noPricePts) field above
## Bid-Ask-Struct. Currently n = 5
## (bestBidRate, totBidQty, noOfBid, implBuyQty, bestOfferRate, totOfferQty, noOfAsk, implSellQty)
BSE_MKT_PIC_FMT_2020_BID_ASK					= "%s 8L"%(BSE_ENDIAN)
BSE_MKT_PIC_STRUCT_2020_BID_ASK					= Struct(BSE_MKT_PIC_FMT_2020_BID_ASK)
BSE_MKT_PIC_LEN_2020_BID_ASK					= 32

## 1.1.115 Close Price Broadcast
BSE_CLOSE_P_BCAST_CODE_2014 					= 2014
## (msgType, res1, res2, res3, hour, minute, second, milliSec, res4, res5, numRecords)
BSE_CLOSE_P_BCAST_FMT_2014_HEAD					= "%s3H"%(BSE_ENDIAN)
BSE_CLOSE_P_BCAST_STRUCT_2014_HEAD 				= Struct(BSE_CLOSE_P_BCAST_FMT_2014_HEAD)
BSE_CLOSE_P_BCAST_LEN_2014_HEAD					= 6
## There can be as many as 80 occurrences of this substructure. Each occurrence of the substructure contains close price for Instrument.
## (instrCode, price, res1, traded, precisionIndi, res2)
BSE_CLOSE_P_BCAST_2014_MAX_NUM_REC				= 80
BSE_CLOSE_P_BCAST_FMT_2014_BODY					= "%s 2L c c c c"%(BSE_ENDIAN)
BSE_CLOSE_P_BCAST_STRUCT_2014_BODY 				= Struct(BSE_CLOSE_P_BCAST_FMT_2014_BODY)
BSE_CLOSE_P_BCAST_LEN_2014_BODY					= 12

## 1.1.116 Sensex Broadcast [2011]
BSE_SENSEX_BCAST_CODE_2011						= 2011
##  (msgType, res1, res2, res3, hour, minute, second, milliSec, res4, res5, numRecord)
BSE_SENSEX_BCAST_FMT_2011_HEAD 					= "%s 3H"%(BSE_ENDIAN)
BSE_SENSEX_BCAST_STRUCT_2011_HEAD				= Struct(BSE_SENSEX_BCAST_FMT_2011_HEAD)
BSE_SENSEX_BCAST_LEN_2011_HEAD					= 6
## The following details will be repeated (Max 24 times)
## (indexCode, indexHigh, indexLow, indexOpen, indexPrevClose, indexVal, indexID, res1, res2, res3, res4, res5, res6)
BSE_SENSEX_BCAST_2011_MAX_NUM_REC				= 24
BSE_SENSEX_BCAST_FMT_2011_BODY 					= "%s6L 7s c c c 2s 2H"%(BSE_ENDIAN)
BSE_SENSEX_BCAST_STRUCT_2011_BODY 				= Struct(BSE_SENSEX_BCAST_FMT_2011_BODY)
BSE_SENSEX_BCAST_LEN_2011_BODY					= 40

## 1.1.117 All Indices Broadcast [2012]
BSE_SENSEX_INDEX_BCAST_CODE_2012				= 2012
##  (msgType, res1, res2, res3, hour, minute, second, milliSec, res4, res5, numRecord)
BSE_SENSEX_INDEX_BCAST_FMT_2012_HEAD			= "%s 3H"%(BSE_ENDIAN)
BSE_SENSEX_INDEX_BCAST_STRUCT_2012_HEAD			= Struct(BSE_SENSEX_INDEX_BCAST_FMT_2012_HEAD)
BSE_SENSEX_INDEX_BCAST_LEN_2012_HEAD			= 6
## The following details will be repeated. (Max 24 times)
## (indexCode, indexHigh, indexLow, indexOpen, indexPrevClose, indexVal, indexID, res1, res2, res3, res4, res5, res6)
BSE_SENSEX_INDEX_BCAST_2012_MAX_NUM_REC 		= 24
BSE_SENSEX_INDEX_BCAST_FMT_2012_BODY 			= "%s6L 7s c c c 2s 2H"%(BSE_ENDIAN)
BSE_SENSEX_INDEX_BCAST_STRUCT_2012_BODY			= Struct(BSE_SENSEX_INDEX_BCAST_FMT_2012_BODY)
BSE_SENSEX_INDEX_BCAST_LEN_2012_BODY			= 40

##1.1.118 Var Percentage Broadcast [2016]
BSE_VAR_PCT_BCAST_CODE_2016						= 2016
## (msgType, res1, res2, res3, hour, minute, second, milliSec, res4, res5, numRecord)
BSE_VAR_PCT_BCAST_FMT_2016_HEAD					= "%s3H"%(BSE_ENDIAN)					
BSE_VAR_PCT_BCAST_STRUCT_2016_HEAD				= Struct(BSE_VAR_PCT_BCAST_FMT_2016_HEAD)
BSE_VAR_PCT_BCAST_LEN_2016_HEAD					= 6
## The following details will be repeated. (Max 40 Instruments VAR and ELM VAR Percentages).
## (instrCode, varIMPct, elmVarPct, res1, res2, res3, res4, ident, res5)
BSE_VAR_PCT_BCAST_2016_MAX_NUM_REC				= 40
BSE_VAR_PCT_BCAST_FMT_2016_BODY 				= "%s4L 2H c c 2s"%(BSE_ENDIAN)
BSE_VAR_PCT_BCAST_STRUCT_2016_BODY				= Struct(BSE_VAR_PCT_BCAST_FMT_2016_BODY)
BSE_VAR_PCT_BCAST_LEN_2016_BODY					= 24

## 1.1.119 Open Interest Broadcast
BSE_OPEN_INT_BCAST_CODE_2015					= 2015
## (msgType, res1, res2, res3, hour, minute, second, milliSec, res4, res5, numRecord)
BSE_OPEN_INT_BCAST_FMT_2015_HEAD 				= "%s3H"%(BSE_ENDIAN)
BSE_OPEN_INT_BCAST_STRUCT_2015_HEAD 			= Struct(BSE_OPEN_INT_BCAST_FMT_2015_HEAD)
BSE_OPEN_INT_BCAST_LEN_2015_HEAD				= 6
## The following details will be repeated. (Max 26 times)
## (instrId, openInstrQty, openInstrVal, openInstrChng, re1, res2, res3, res4, res5, res6, res7)
BSE_OPEN_INT_BCAST_2015_MAX_NUM_REC				= 26
BSE_OPEN_INT_BCAST_FMT_2015_BODY 				= "%s2L Q L 4s L 2H c c 2s"%(BSE_ENDIAN)
BSE_OPEN_INT_BCAST_STRUCT_2015_BODY 			= Struct(BSE_OPEN_INT_BCAST_FMT_2015_BODY)
BSE_OPEN_INT_BCAST_LEN_2015_BODY				= 36

## 1.1.120 RBI Reference Rate
BSE_RBI_REF_RATE_CODE_2022						= 2022
## (msgType, res1, res2, res3, hour, minute, second, milliSec, res4, res5, numRecord) 
BSE_RBI_REF_RATE_FMT_2022_HEAD 					= "%s3H"%(BSE_ENDIAN)
BSE_RBI_REF_RATE_STRUCT_2022_HEAD 				= Struct(BSE_RBI_REF_RATE_FMT_2022_HEAD)
BSE_RBI_REF_RATE_LEN_2022_HEAD					= 6
## The following sub-structure will repeat no. of times as specified in the number of records field above
## (underAssetId, rbiRate, res1, res2, date, filler)
# BSE_RBI_REF_RATE_2022_MAX_NUM_REC				= -1
BSE_RBI_REF_RATE_FMT_2022_BODY					= "%s2L 2H 11s c"%(BSE_ENDIAN)
BSE_RBI_REF_RATE_STRUCT_2022_BODY				= Struct(BSE_RBI_REF_RATE_FMT_2022_BODY)
BSE_RBI_REF_RATE_LEN_2022_BODY 					= 24

##1.1.121 News Headline Broadcast (2004)
BSE_NEWS_HEAD_BCAST_CODE_2004					= 2004
## (msgType, res1, res2, res3, hour, minute, second, milliSec, res4, res5, res6, newsCat, res7, newsId, newsHead, res8, res9, res10)
BSE_NEWS_HEAD_BCAST_FMT_2004					= "%s5H L 40s c c 2s"%(BSE_ENDIAN)
BSE_NEWS_HEAD_BCAST_STRUCT_2004					= Struct(BSE_NEWS_HEAD_BCAST_FMT_2004)
BSE_NEWS_HEAD_BCAST_LEN_2004					= 58

BSE_BCAST_VALID_TRANS_CODE 						= [BSE_TIME_BROADCAST_CODE_2001, BSE_SESSION_CHANGE_CODE_2002, BSE_SESSION_CHANGE_CODE_2003, BSE_NEWS_HEAD_BCAST_CODE_2004, BSE_SENSEX_BCAST_CODE_2011, BSE_SENSEX_INDEX_BCAST_CODE_2012, BSE_CLOSE_P_BCAST_CODE_2014, BSE_OPEN_INT_BCAST_CODE_2015, BSE_VAR_PCT_BCAST_CODE_2016, BSE_MKT_PIC_CODE_2020, BSE_RBI_REF_RATE_CODE_2022]

BSE_INDEX_CODES = {
		1 	: "SENSEX", ##BSE sensitive index
		2 	: "BSE100", ## BSE 100 scrips index
		3 	: "BSE200", ## BSE 200 scrips index
		4 	: "BSE500", ## BSE 500 scrips index
		34 	: "BSE IT", ## S&P BSE Information Technology
		32 	: "BSEFMC", ## S&P BSE Fast Moving Consumer Goods
		7 	: "BSE CG", ## BSE Capital Goods Index
		8 	: "BSE CD", ## BSE Consumer Durables index
		33 	: "BSE HC", ## S&P BSE Healthcare
		10 	: "BSE PSU", ## BSE Public Sector Unit Index
		11 	: "TECK", ## BSE Teck Index
		12 	: "BANKEX", ## BSE Bank Index
		13 	: "AUTO", ## BSE AUTO index
		14 	: "METAL", ## BSE METAL index
		15 	: "OILGAS", ## BSE OIL&GAS index
		30 	: "MIDCAP", ## S&P BSE MidCap
		31 	: "SMLCAP", ## S&P BSE SmallCap
		18 	: "DOL30", ## Dollex-30
		19 	: "DOL100", ## Dollex-100
		20 	: "DOL200", ## Dollex-200
		21 	: "REALTY", ## BSE Realty Index
		22 	: "POWER", ## BSE Power Index
		23 	: "BSEIPO", ## BSE IPO Index
		25 	: "GREENX", ## BSE GREENEX
		26 	: "CARBON", ## BSE CARBON
		27 	: "SMEIPO", ## BSE SME IPO
		28 	: "INFRA", ## S&P BSE India Infrastructure Index
		29 	: "CPSE", ## S&P BSE CPSE
		35 	: "MFG", ## S&P BSE MFG
		36 	: "ALLCAP", ## S&P BSE AllCap
		37 	: "BASMTR", ## S&P BSE Basic Matrl
		38 	: "CDGS", ## S&P BSE Cons Discr
		39 	: "ENERGY", ## S&P BSE Energy
		40 	: "FIN", ## S&P BSE Finance
		41 	: "INDSTR", ## S&P BSE Industrials
		42 	: "LRGCAP", ## S&P BSE LargeCap
		43 	: "MIDSEL", ## S&P BSE MidCap Sel
		44 	: "SMLSEL", ## S&P BSE SmallCapSel
		45 	: "TELCOM", ## S&P BSE Telecom
		46 	: "UTILS", ## S&P BSE Utilities
		47 	: "SNSX50", ## S&P BSE SENSEX 50
		48 	: "SNXT50", ## S&P BSE SENSEX Next 50
		49 	: "BHRT22", ## S&P BSE Bharat 22
		50 	: "ESG100" ## S&P BSE 100 ESG Index
}

def main():
	print "You are not allowed to run this file"
	sys.exit()

if __name__ == "__main__":
	main()