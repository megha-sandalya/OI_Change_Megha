"""
Author 		: Ajay A U [ajay@fyers.in]
Version 	: 2.0
Copyright 	: Fyers Securities
Web			: fyers.in
"""
#!/usr/bin/env python

TIMEOUT_MEMC_THREAD			= 0.3
TIMEOUT_MIN_THREAD_MEMC		= 70 #5 # ## 5 for testing

EXPIRT_TIME_MEMC_TOKENS 	= 46800

K_FY_MEMC_TOKEN_RT_DATA 	= 2001
K_FY_MEMC_TOK_VOL			= 2002
K_FY_TV_ALL_DATA 			= 2003
K_FY_TICK_DATA				= 2004 ## Ajay 2019-05-20 For tick data
K_FY_MEMC_TOKEN_OI_DATA 	= 2005

## New 7202 Token
#K_FY_MEMC_TOKEN_OI_DATA		= 9003


## Msg Cache - Palash
K_FY_MSG_TOKEN              = 5001


## *************** Memcache JSON value Keys ***************
# {201:lastTradedPrice, 202:lastTradeQty, 203:lastTradeTime, 204:netPChangeFromClosePrice, 205:netChangeIndicator, 206:avgTradePrice, 207:volTradedToday, 211:totalBuyQty, 212:totalSellQty, 213:bookType, 214:tradingStatus, 220:closingPrice, 221:openPrice, 222:highPrice, 223:lowPrice, 301:bidAskList[0], 302:bidAskList[2], 303:bidAskList[4], 304:bidAskList[6], 305:bidAskList[8], 401:bidAskList[1], 402:bidAskList[3], 403:bidAskList[5], 404:bidAskList[7], 405:bidAskList[9], 501:bidAskList[10], 502:bidAskList[12], 503:bidAskList[14], 504:bidAskList[16], 505:bidAskList[18], 601:bidAskList[11], 602:bidAskList[13], 603:bidAskList[15], 604:bidAskList[17], 605:bidAskList[19]}
K_MEMC_LTP 				= 201 ##: inputDict[eachToken][K_LTP],
K_MEMC_LTQ 				= 202 ##: inputDict[eachToken][K_LTQ],
K_MEMC_LTT 				= 203 ##: inputDict[eachToken][K_LTT],
K_MEMC_CHANGE_P 		= 204 ##: inputDict[eachToken][K_NPC_FROM_CP],
### 205: netChangeIndicator,

K_MEMC_ATP 				= 206 ##: inputDict[eachToken][K_ATP],
K_MEMC_VTT 				= 207 ##: inputDict[eachToken][K_VTT],
K_MEMC_TOT_BUY_Q 		= 211 ##: inputDict[eachToken][K_TOT_BUY_Q],
K_MEMC_TOT_SELL_Q 		= 212 ##: inputDict[eachToken][K_TOT_SELL_Q],
### 213: bookType,
### 214: tradingStatus,
K_MEMC_PCT_CHANGE		= 215 ## New addition percentage change

K_MEMC_CLOSING_P 		= 220 ##: inputDict[eachToken][K_CLOSING_P], ##closingPrice, 
K_MEMC_OPEN_P 			= 221 ##: inputDict[eachToken][K_OPEN_P], ##openPrice, 
K_MEMC_HIGH_P 			= 222 ##: inputDict[eachToken][K_HIGH_P], ##highPrice, 
K_MEMC_LOW_P 			= 223 ##: inputDict[eachToken][K_LOW_P], ##lowPrice,
K_MEMC_SPREAD 			= 224 ## 601-401
K_MEMC_TODAY_TS			= 225 ## Today timestamp

K_MEMC_BID_QTY_START 	= 301
K_MEMC_BID_P_START 		= 401
K_MEMC_ASK_QTY_START 	= 501
K_MEMC_ASK_P_START 		= 601
K_MEMC_TS_BCH 			= 226 ## New for stream
K_MEMC_TRANS_CODE		= 227 ## New for stream
K_MEMC_RT_TICK_TS		= 228 ## New change Ajay 2019-05-20 For tick data
K_MEMC_RT_TICK_VOL		= 229
## New Ajay 2019-05-13
K_MEMC_BID_NUM_START		= 800
K_MEMC_ASK_NUM_START		= 900
K_MEMC_IMPL_BID_QTY_START	= 1000
K_MEMC_IMPL_ASK_QTY_START	= 1100

## 700:open, 701:close, 702:high, 703:low, 704:vol, 705: minTimestamp
K_MEMC_RT_OPEN			= 700
K_MEMC_RT_CLOSE			= 701
K_MEMC_RT_HIGH			= 702
K_MEMC_RT_LOW			= 703
K_MEMC_RT_VOL			= 704
K_MEMC_RT_TS			= 705
K_MEMC_IST_MIN_TS		= 706

##800:token, 801 fillp . 802 fillVol, 803 oi, 804 dayHiOI , 805 
#{'token': 2169, 'fillP': 350000, 'fillVol': 5, 'oi': 129683, 'dayHiOI': 132555, 201: 1608528507, 'dayLoOi': 109869, 'mktType': 1}
##New Megha/Vishal 1/05/2021
K_OI_RT_TOKEN 			= 810
K_OI_RT_FILLP 			= 811
K_OI_RT_FILLVOL 		= 812
K_OI_RT_OI 				= 813
K_OI_RT_DAY_HI_OI 		= 814
K_OI_RT_DAY_LO_OI 		= 815
K_MEMC_Change_OI		= 816  ##: inputDict[eachToken][K_OI_CLOSING_P]

# *************** Trading view keys ***************
K_MEMC_TV_OPEN			= "o"
K_MEMC_TV_HIGH			= "h"
K_MEMC_TV_LOW			= "l"
K_MEMC_TV_CLOSE			= "c"
K_MEMC_TV_VOL			= "v"
K_MEMC_TV_TIME			= "t"
K_MEMC_FY_DAY_H			= "dh"
K_MEMC_FY_DAY_L			= "dl"
K_MEMC_FY_VTT			= "vtt"
K_MEMC_FY_TOKEN			= "ft"


# ************** Trading view keys for oi ***********
##New Megha/Vishal 1/05/2021
K_MEMC_OI_TOKEN			= "ft"
K_MEMC_OI_FILLP 		= "fp"
K_MEMC_OI_FILLVOL		= "fv"
K_MEMC_OI 				= "oi"
K_MEMC_OI_DAYHI			= "dhi"
K_MEMC_OI_DAYLO			= "dlo"
K_MEMC_OI_Change		= "ch"
K_MEMC_OI_Prev			= "pv"


# LIST_TV_KEYS = [K_MEMC_TV_OPEN, K_MEMC_TV_HIGH, K_MEMC_TV_LOW, K_MEMC_TV_CLOSE, K_MEMC_TV_VOL, K_MEMC_TV_TIME, K_MEMC_FY_DAY_H, K_MEMC_FY_DAY_L]
# LIST_TV_KEYS = [x.decode("utf-8") for x in LIST_TV_KEYS] ## JSON dumps gives up the unicode values so this is converted to unicode
# LIST_TV_KEYS.sort()
