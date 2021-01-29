"""
Author 		: Ajay A U [ajay@fyers.in]
Version 	: 2.2
Copyright 	: Fyers Securities
Web			: fyers.in
"""
#!/usr/bin/python
# from pytz import timezone

from datetime import datetime
## program version that is running
_NSE_PROG_VERSION	= "2.2"

## These are the names that are called in the arguments while calling the program
EXCHANGE_NAME_NSE 	= "NSE"
EXCHANGE_CODE_NSE 	= 10

SEG_NAME_CM_LIVE	= "CM"
SEG_NAME_FO_LIVE	= "FO"
SEG_NAME_CD_LIVE	= "CD"
SEG_NAME_CM_TEST	= "CMTEST"
SEG_NAME_FO_TEST	= "FOTEST"
SEG_NAME_CD_TEST	= "CDTEST"

SEG_CODE_CM_LIVE	= 10
SEG_CODE_FO_LIVE	= 11
SEG_CODE_CD_LIVE	= 12

## ******************* BSE *******************
EXCHANGE_NAME_BSE 		= "BSE"
EXCHANGE_CODE_BSE 		= 12

SEG_NAME_CM_LIVE_BSE	= "CM"
SEG_NAME_FO_LIVE_BSE	= "FO"
SEG_NAME_CD_LIVE_BSE	= "CD"
SEG_NAME_CM_TEST_BSE	= "CMTEST"
SEG_NAME_FO_TEST_BSE	= "FOTEST"
SEG_NAME_CD_TEST_BSE	= "CDTEST"

SEG_CODE_CM_LIVE_BSE	= 10
SEG_CODE_FO_LIVE_BSE	= 11
SEG_CODE_CD_LIVE_BSE	= 12
## ******************* BSE *******************

## ******************* MCX *******************
EXCHANGE_NAME_MCX 		= "MCX"
EXCHANGE_CODE_MCX 		= 20
SEG_NAME_COM_LIVE_MCX	= "COM"
SEG_NAME_COM_TEST_MCX	= "COMTEST"
SEG_CODE_COM_LIVE_MCX	= 11

## Debug Flags
DEBUG_TEST 			= "testenv"
DEBUG_ADDITNL_PRINT = "extra"
DEBUG_TIME 			= "time"

##TABLE Name
TBL_SYMBOL_MASTER =   "symbol_master" ## "symbol_master_v2"# For testing 

## Log File
# LOG_PATH_VAR		= "E:\\Fyers\\var"
# LOG_PATH_LOGS		= "E:\\Fyers\\var\\logs"
# LOG_PATH_NSE_DF		= "E:\\Fyers\\var\\logs\\nse_datafeed"

# LOG_FILE_PATH		= "E:\\Fyers\\var\\logs\\nse_datafeed\\"

#New Code MCX 20181019 - Palash
TEMP_DATA_FILE_PATH_MCX = "/home/ec2-user/fy_var/temp_mcx_init/"
LOG_FILE_PATH_EC2_RS_MCX= "/home/ec2-user/fy_var/log/mcx_init/"
MSG_FILE_PATH = "exchange_messages/"


TEMP_DATA_FILE_PATH	= "/home/ec2-user/fy_var/temp_nse_init/"
LOG_FILE_PATH_EC2_RS_NSE= "/home/ec2-user/fy_var/log/nse_init/"

## Change Ajay 2019-01-16
TEMP_DATA_FILE_PATH_BSE	= "/home/ec2-user/fy_var/temp_bse_init/"
LOG_FILE_PATH_EC2_RS_BSE= "/home/ec2-user/fy_var/log/bse_init/"

LOG_FILE_EXT		= ".txt"

## ******************* String constants *******************
## ************* Error strings 
ERROR_processFyPacket   = "ERR : processFyPacket()->"

ERROR_initNSEProcessing = "ERR : initNSEProcessing()->"
ERROR_initExcProcessing = "ERR : initExcProcessing()->"
ERROR_newDayTrigger 	= "ERR : newDayTrigger()->"

## ************* Common_funct *************
ERROR_createDirectory 	= "ERR : createDirectory()->"
ERROR_checkMktHours 	= "ERR : checkMktHours()->"
ERROR_dbConnect 		= "ERR : dbConnect()->"
ERROR_getFyTokenDict	= "ERR : getFyTokenDict()->"
ERROR_getExceptionTokens= "ERR : getExceptionTokens()->" ## New ajay 2018-04-10
ERROR_getPreviousValforTokens = "ERR : getPreviousCloseforTokens->" ## New Ajay 2018-04-05

ERROR_initProcess 		= "ERR : initProcess()->"
ERROR_setToMemc 		= "ERR : setToMemc->"
ERROR_setOiToThread		= "ERR : setOiToThread"
ERROR_getPrevMinVal		= "ERR : getPrevMinVal()->"
ERROR_th_marketStatCheck= "ERR : th_marketStatCheck()->"
ERROR_printPacketCount 	= "ERR : printPacketCount()->"

ERROR_setMemcThread 	= "ERR : setMemcThread->"
ERROR_initRecvNSE 		= "ERR : initRecvNSE->"

ERROR_minThreadFunct 	= "ERR : minThreadFunct()->"

ERROR_processNSEPacket	= "ERR : processNSEPacket()->"
ERROR_process7208		= "ERR : process7208()->"
ERROR_process7207 		= "ERR : process7207->"
ERROR_process6511 		= "ERR : process6511()->"
ERROR_process6501 		= "ERR : process6501()->"
ERROR_process7202 		= "ERR : process7202()->" ## New Ajay 2019-06-24

LOG_getExSegCodeFromName= "getExSegCodeFromName"
ERROR_setMsgToCache		= "ERROR_setMsgToCache()->"

## JSON-Keys
K_TOKEN 		= 0 #token#
K_BOOK_T 		= 1 #bookType#
K_TRADING_STAT 	= 2 #tradingStatus#
K_VTT 			= 3 #volTradedToday#
K_LTP 			= 4 #lastTradedPrice#
K_NET_CHANGE_I 	= 5 #netChangeIndicator#
#unknown_extra#
K_NPC_FROM_CP 	= 6  #netPChangeFromClosePrice#
K_LTQ 			= 7  #lastTradeQty#
K_LTT 			= 8  #lastTradeTime#
K_ATP 			= 9  #avgTradePrice#
K_AUCT_N 		= 10 #auctionNumber#
K_AUCT_STAT 	= 11 #auctionStatus#
K_INITR_T 		= 12 #initiatorType#
K_INITR_P 		= 13 #initiatorPrice#
K_INITR_Q 		= 14 #initiatorQty#
K_AUCT_P  		= 15 #auctionPrice#
K_AUCT_Q 		= 16 #auctionQty#
#MBP_INFO_7208#:MBP_INFO_7208,
K_BB_TOT_BUY_F 	= 17 #bbTotalBuyFlag#
K_BB_TOT_SELL_F = 18 #bbTotalSellFlag#
#extraBuy4_#
K_TOT_BUY_Q 	= 19 #totalBuyQty#
#tBuyExtra#
#extraSell4_#
K_TOT_SELL_Q 	= 20 #totalSellQty#
#tSellExtra#
K_MBP_INDIC_BIT = 21 #MbpIndicatorBits#
K_MBP_INDIC_RES = 22 #MbpIndicatorReserved#
K_CLOSING_P 	= 23 #closingPrice#
K_OPEN_P 		= 24 #openPrice#
K_HIGH_P 		= 25 #highPrice#
K_LOW_P 		= 26 #lowPrice##lowPrice#

K_BID_ASK_DICT 	= 27
K_BID 			= 28
K_ASK 			= 29
K_BID_ASK_QTY	= 30
K_BID_ASK_P		= 31
K_PERCENT_CHNG	= 32

K_PRICE_CONV	= 33
K_TRADIN_STAT 	= 34

## New Ajay 2019-05-13
K_NUM_BID_ASK	= 35
K_IMPL_QTY		= 36

##New Megha/Vishal 1/05/2021
K_TOKEN_OI		= 37
K_FILLP_OI		= 38
K_FILLVOL_OI 	= 39
K_OI 			= 40
K_DAYHI_OI		= 41
K_DAYLO_OI		= 42
K_MKT_TYPE_0I	= 43
K_OI_CLOSING_P	= 44

# Header values
K_BCH_TS				= 201
K_BCH_PACKT_CODE		= 202
K_BCH_PACKT_FLAG		= 203



#K_BID_ASK_START = 50

## for 6511, 6521, 6531, 6571, 6583, 6584
K_MKT_TYPE_6511 	= 50#mktType, 
K_BCAST_DEST_6511 	= 51#broadcastDest
K_BCAST_MSG_L_6511 	= 52#broadCastMsgLen
K_BCAST_MSG_6511 	= 53#broadCastMsg

## Function status JSON key-values
## These will be used to chaeck the function status
K_FUNCT_STAT 		= 100
K_ERR_MSG 			= 101
K_FUN_DATA			= 102

V_FUNCT_SUCCESS_1	= 1
V_FUNCT_FAIL_N_1	= -1



## ***************** Marking trading timings *****************
## **************** Nont : All the times are in 24 hour format ****************
## For the exception timing time format should be
## exception Dict: 	{"YYYY-MM-DD":[START_TIME,END_TIME], "YYYY-MM-DD":["HH:MM:SS","HH:MM:SS"]}
## 					START_TIME and END_TIME are in the format HH:MM:SS 24 hour format
## 					{"2017-10-17":["03:45:00","14:00:00"],"2017-10-19":["12:00:00","14:00:00"]}

# GMT = timezone("GMT")
# IST = timezone("Asia/Kolkata")

## Market status flags
## These indicate if the market open/close/preopen/extended etc
## New addition Ajay 2018-04-10
MKT_F_PREOP 			= 1 ## 1-> pre_market
MKT_F_PREOP_EXT 		= 4 ## 4-> pre_market_extended
MKT_F_PREOP_PRICE_DISC	= 6 ## 6-> pre_market price_discovery

MKT_F_NORMAL_OPEN		= 2 ## 2-> market_open
MKT_F_SUSPENDED			= 3 ## 3-> Suspended
MKT_F_PARTIAL			= 7 ## 7-> Partially traded.
MKT_F_CLOSED			= 9 ## 9-> Closed

## CM
CM_START_TIME_STR		= "09:15:00"
CM_END_TIME_STR			= "15:30:00"
## Extended LIVE trading on 2018-04-18 FROM 16:30:00 to 19:00:00
CM_EXTEND_START_T_STR 	= "00:00:00" ## New addition Ajay 2018-04-10 ## change Ajay on 2018-04-18
CM_EXTEND_END_T_STR 	= "00:00:00" ## New addition Ajay 2018-04-10 ## change Ajay on 2018-04-18
CM_PRE_MKT_START_T_STR 	= "09:00:00" ## New addition Ajay 2018-04-10
CM_PRE_MKT_END_T_STR 	= "09:07:59" ## Usually the normal market will close at 09:07 IST ## New addition Ajay 2018-04-10
CM_NORMAL_START_TIME	= datetime.strptime(CM_START_TIME_STR, "%H:%M:%S")
CM_NORMAL_END_TIME		= datetime.strptime(CM_END_TIME_STR, "%H:%M:%S")
CM_EXTEND_START_TIME	= None ##datetime.strptime(CM_EXTEND_START_T_STR, "%H:%M:%S") ## There is no extened trading time for CM. ## New addition Ajay 2018-04-10 change Ajay on 2018-04-18
CM_EXTEND_END_TIME		= None ##datetime.strptime(CM_EXTEND_END_T_STR, "%H:%M:%S") ## There is no extened trading time for CM.## New addition Ajay 2018-04-10 change Ajay on 2018-04-18
CM_PRE_MKT_START_TIME 	= datetime.strptime(CM_PRE_MKT_START_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
CM_PRE_MKT_END_TIME 	= datetime.strptime(CM_PRE_MKT_END_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
CM_EXCEPTION_TIME_DICT 	= {"2017-10-17":["17:00:00","19:00:00"],"2017-10-19":["12:00:00","14:00:00"], "2018-11-05":["16:30:00","19:00:00"], "2018-11-07":["17:30:00","18:30:00"], "2019-10-25":["17:00:00", "19:00:00"], "2019-10-27":["18:15:00", "19:15:00"]} # 

##FO
FO_START_TIME_STR		= "09:15:00"
FO_END_TIME_STR			= "15:30:00"
FO_EXTEND_START_T_STR 	= "00:00:00" ## No extended trading hours for FO. ## New addition Ajay 2018-04-10
FO_EXTEND_END_T_STR 	= "00:00:00" ## No extended trading hours for FO. ## New addition Ajay 2018-04-10
FO_PRE_MKT_START_T_STR 	= "00:00:00" ## No premarket trading hours for FO. ## New addition Ajay 2018-04-10
FO_PRE_MKT_END_T_STR 	= "00:00:00" ## No premarket trading hours for FO. ## New addition Ajay 2018-04-10
FO_NORMAL_START_TIME	= datetime.strptime(FO_START_TIME_STR, "%H:%M:%S")
FO_NORMAL_END_TIME		= datetime.strptime(FO_END_TIME_STR, "%H:%M:%S")
FO_EXTEND_START_TIME	= None ## There is no extened trading time for FO. datetime.strptime(FO_EXTEND_START_T_STR, "%H:%M:%S") ## New addition Ajay 2018-04-10
FO_EXTEND_END_TIME		= None ## There is no extened trading time for FO. datetime.strptime(FO_EXTEND_END_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
FO_PRE_MKT_START_TIME 	= None ## There is no premarket trading time for FO. datetime.strptime(FO_PRE_MKT_START_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
FO_PRE_MKT_END_TIME 	= None ## There is no premarket trading time for FO. datetime.strptime(FO_PRE_MKT_END_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
FO_EXCEPTION_TIME_DICT 	= {"2017-10-17":["17:00:00","19:00:00"],"2017-10-19":["12:00:00","14:00:00"], "2018-11-07":["17:30:00","18:30:00"], "2019-10-27":["18:15:00", "19:15:00"]} # 

##CD
CD_START_TIME_STR		= "09:00:00"
CD_END_TIME_STR			= "17:00:00" ## New change Ajay 2018-04-10 
CD_EXTEND_START_T_STR 	= "17:00:00" ## New addition Ajay 2018-04-10
CD_EXTEND_END_T_STR 	= "19:30:00" ## New addition Ajay 2018-04-10
CD_PRE_MKT_START_T_STR 	= "00:00:00" ## No premarket trading hours for CD. ## New addition Ajay 2018-04-10
CD_PRE_MKT_END_T_STR 	= "00:00:00" ## No premarket trading hours for CD. ## New addition Ajay 2018-04-10
CD_NORMAL_START_TIME	= datetime.strptime(CD_START_TIME_STR, "%H:%M:%S")
CD_NORMAL_END_TIME		= datetime.strptime(CD_END_TIME_STR, "%H:%M:%S")
CD_EXTEND_START_TIME	= datetime.strptime(CD_EXTEND_START_T_STR, "%H:%M:%S") ## New addition Ajay 2018-04-10 
CD_EXTEND_END_TIME		= datetime.strptime(CD_EXTEND_END_T_STR, "%H:%M:%S") ## New addition Ajay 2018-04-10
CD_PRE_MKT_START_TIME 	= None ## There is no premarket trading time for CD. datetime.strptime(CD_PRE_MKT_START_T_STR, "%H:%M:%S") ## New addition Ajay 2018-04-10
CD_PRE_MKT_END_TIME 	= None ## There is no premarket trading time for CD. datetime.strptime(CD_PRE_MKT_END_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
CD_EXCEPTION_TIME_DICT 	= {"2017-10-17":["17:00:00","19:00:00"],"2017-10-19":["12:00:00","14:00:00"], "2018-11-07":["17:30:00","18:30:00"], "2019-10-27":["18:15:00", "19:15:00"]} # 

## ***************************** BSE TIME *****************************
## BSE CM
CM_START_TIME_STR_BSE		= "09:15:00"
CM_END_TIME_STR_BSE			= "15:30:00"
## Extended LIVE trading on 2018-04-18 FROM 16:30:00 to 19:00:00
CM_EXTEND_START_T_STR_BSE 	= "00:00:00" ## New addition Ajay 2018-04-10 ## change Ajay on 2018-04-18
CM_EXTEND_END_T_STR_BSE 	= "00:00:00" ## New addition Ajay 2018-04-10 ## change Ajay on 2018-04-18
CM_PRE_MKT_START_T_STR_BSE 	= "09:00:00" ## New addition Ajay 2018-04-10
CM_PRE_MKT_END_T_STR_BSE 	= "09:07:59" ## Usually the normal market will close at 09:07 IST ## New addition Ajay 2018-04-10
CM_NORMAL_START_TIME_BSE	= datetime.strptime(CM_START_TIME_STR_BSE, "%H:%M:%S")
CM_NORMAL_END_TIME_BSE		= datetime.strptime(CM_END_TIME_STR_BSE, "%H:%M:%S")
CM_EXTEND_START_TIME_BSE	= None ##datetime.strptime(CM_EXTEND_START_T_STR, "%H:%M:%S") ## There is no extened trading time for CM. ## New addition Ajay 2018-04-10 change Ajay on 2018-04-18
CM_EXTEND_END_TIME_BSE		= None ##datetime.strptime(CM_EXTEND_END_T_STR, "%H:%M:%S") ## There is no extened trading time for CM.## New addition Ajay 2018-04-10 change Ajay on 2018-04-18
CM_PRE_MKT_START_TIME_BSE 	= datetime.strptime(CM_PRE_MKT_START_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
CM_PRE_MKT_END_TIME_BSE 	= datetime.strptime(CM_PRE_MKT_END_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
CM_EXCEPTION_TIME_DICT_BSE 	= {"2017-10-17":["17:00:00","19:00:00"],"2017-10-19":["12:00:00","14:00:00"], "2018-11-05":["16:30:00","19:00:00"], "2018-11-07":["17:30:00","18:30:00"]} # 

## BSE FO
FO_START_TIME_STR_BSE		= "09:15:00"
FO_END_TIME_STR_BSE			= "15:30:00"
FO_EXTEND_START_T_STR_BSE 	= "00:00:00" ## No extended trading hours for FO. ## New addition Ajay 2018-04-10
FO_EXTEND_END_T_STR_BSE 	= "00:00:00" ## No extended trading hours for FO. ## New addition Ajay 2018-04-10
FO_PRE_MKT_START_T_STR_BSE 	= "00:00:00" ## No premarket trading hours for FO. ## New addition Ajay 2018-04-10
FO_PRE_MKT_END_T_STR_BSE 	= "00:00:00" ## No premarket trading hours for FO. ## New addition Ajay 2018-04-10
FO_NORMAL_START_TIME_BSE	= datetime.strptime(FO_START_TIME_STR_BSE, "%H:%M:%S")
FO_NORMAL_END_TIME_BSE		= datetime.strptime(FO_END_TIME_STR_BSE, "%H:%M:%S")
FO_EXTEND_START_TIME_BSE	= None ## There is no extened trading time for FO. datetime.strptime(FO_EXTEND_START_T_STR, "%H:%M:%S") ## New addition Ajay 2018-04-10
FO_EXTEND_END_TIME_BSE		= None ## There is no extened trading time for FO. datetime.strptime(FO_EXTEND_END_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
FO_PRE_MKT_START_TIME_BSE 	= None ## There is no premarket trading time for FO. datetime.strptime(FO_PRE_MKT_START_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
FO_PRE_MKT_END_TIME_BSE 	= None ## There is no premarket trading time for FO. datetime.strptime(FO_PRE_MKT_END_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
FO_EXCEPTION_TIME_DICT_BSE 	= {"2017-10-17":["17:00:00","19:00:00"],"2017-10-19":["12:00:00","14:00:00"], "2018-11-07":["17:30:00","18:30:00"]} # 

## BSE CD
CD_START_TIME_STR_BSE		= "09:00:00"
CD_END_TIME_STR_BSE			= "17:00:00" ## New change Ajay 2018-04-10 
CD_EXTEND_START_T_STR_BSE 	= None#"17:00:00" ## New addition Ajay 2018-04-10
CD_EXTEND_END_T_STR_BSE 	= None#"19:30:00" ## New addition Ajay 2018-04-10
CD_PRE_MKT_START_T_STR_BSE 	= "00:00:00" ## No premarket trading hours for CD. ## New addition Ajay 2018-04-10
CD_PRE_MKT_END_T_STR_BSE 	= "00:00:00" ## No premarket trading hours for CD. ## New addition Ajay 2018-04-10
CD_NORMAL_START_TIME_BSE	= datetime.strptime(CD_START_TIME_STR_BSE, "%H:%M:%S")
CD_NORMAL_END_TIME_BSE		= datetime.strptime(CD_END_TIME_STR_BSE, "%H:%M:%S")
CD_EXTEND_START_TIME_BSE	= None#datetime.strptime(CD_EXTEND_START_T_STR_BSE, "%H:%M:%S") ## New addition Ajay 2018-04-10 
CD_EXTEND_END_TIME_BSE		= None#datetime.strptime(CD_EXTEND_END_T_STR_BSE, "%H:%M:%S") ## New addition Ajay 2018-04-10
CD_PRE_MKT_START_TIME_BSE 	= None ## There is no premarket trading time for CD. datetime.strptime(CD_PRE_MKT_START_T_STR, "%H:%M:%S") ## New addition Ajay 2018-04-10
CD_PRE_MKT_END_TIME_BSE 	= None ## There is no premarket trading time for CD. datetime.strptime(CD_PRE_MKT_END_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
CD_EXCEPTION_TIME_DICT_BSE 	= {"2017-10-17":["17:00:00","19:00:00"],"2017-10-19":["12:00:00","14:00:00"], "2018-11-07":["17:30:00","18:30:00"]} # 

## **************** MCX ****************
COM_EXTEND_START_TIME_MCX	= None ## There is no extened trading time for FO. datetime.strptime(FO_EXTEND_START_T_STR, "%H:%M:%S") ## New addition Ajay 2018-04-10
COM_EXTEND_END_TIME_MCX		= None ## There is no extened trading time for FO. datetime.strptime(FO_EXTEND_END_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
COM_PRE_MKT_START_TIME_MCX 	= None ## There is no premarket trading time for FO. datetime.strptime(FO_PRE_MKT_START_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
COM_PRE_MKT_END_TIME_MCX 	= None ## There is no premarket trading time for FO. datetime.strptime(FO_PRE_MKT_END_T_STR, "%H:%M:%S")## New addition Ajay 2018-04-10
COM_EXCEPTION_TIME_DICT_MCX = {"2019-10-27":["18:15:00", "19:15:00"]}
## Exception token condition. Tokens that will be traded after market hours.
## CM
## Extended trading sessipon on 2018-04-18
# EXCEPT_TOKEN_CONDI_CM 	= r'ex_inst_type=4 and trade_status=1 and ex_symbol_name like "%gold%"' ## change ajay 2018-04-18
EXCEPT_TOKEN_CONDI_CM 	= ""
## FO
EXCEPT_TOKEN_CONDI_FO 	= ""
## CD
EXCEPT_TOKEN_CONDI_CD 	= "TRADE_STATUS=1 AND (UNDERLYING_SYM='eurusd' or UNDERLYING_SYM='gbpusd' or UNDERLYING_SYM='usdjpy' )"

## MCX
EXCEPT_TOKEN_CONDI_MCX_COM 	= ""

## BSE
EXCEPT_TOKEN_CONDI_CM_BSE 	= ""
EXCEPT_TOKEN_CONDI_FO_BSE 	= ""
EXCEPT_TOKEN_CONDI_CD_BSE 	= ""

## NSE New Day Trigger Time
NSE_NEW_DAY_TIME_STR = "08:00:00"
NSE_NEW_DAY_TIME     = datetime.strptime(NSE_NEW_DAY_TIME_STR, "%H:%M:%S")

# MCX - COM
NEW_DAY_TIME_MCX_STR = "09:00:00"
MCX_NEW_DAY_TIME     = datetime.strptime(NEW_DAY_TIME_MCX_STR, "%H:%M:%S")

##BSE
BSE_NEW_DAY_TIME_STR = "08:00:00"
BSE_NEW_DAY_TIME     = datetime.strptime(BSE_NEW_DAY_TIME_STR, "%H:%M:%S")

# Redis Exchange Messages Expire time
REDIS_EXPIRE_TIME = 43200

## New Ajay 2019-01-16. Used to get previous close values which is used for pre market
FY_SYMBOL_MAPPING = {"nifty50" : "nifty", "niftybank" : "banknifty", "niftymidcap50":"niftymid50"}

