"""
Author 		: Ajay A U [ajay@fyers.in]
Version 	: 2.0
Copyright 	: Fyers Securities
Web			: fyers.in
"""
#!/usr/bin/env python

FY_CACHE_NUM_1 					= 1
ELASTCACHE_END_POINT 			= "" #"fyers-trade.jb5agw.cfg.aps1.cache.amazonaws.com:11211"## Shifted to Redis

AWS_REDIS_END_POINT				= "127.0.0.1"
LOCAL_REDIS_END_POINT			= "127.0.0.1"
REDIS_END_POINT_MASTER			= AWS_REDIS_END_POINT
#REDIS_END_POINT_MASTER		= "127.0.0.1"

## AWS
#DB_ENDPOINT_AWS_READER 			= "fyers-trading-db-cluster.cluster-ro-cvghve20lauv.ap-south-1.rds.amazonaws.com"
DB_ENDPOINT_AWS_READER 			= "127.0.0.1"
#DB_ENDPOINT_AWS_WRITER 			= "fyers-trading-db-cluster.cluster-cvghve20lauv.ap-south-1.rds.amazonaws.com"
DB_ENDPOINT_AWS_WRITER 			= "127.0.0.1"
DB_PORT_AWS						= 3306
DB_UNAME_AWS					= "root"
DB_PASS_AWS						= ""

DB_NAME_NSE_CM_EOD_AWS			= "fyers_eod_data_nse_cm_v2"
DB_NAME_NSE_FO_EOD_AWS			= "fyers_eod_data_nse_fo_v1"
DB_NAME_NSE_CD_EOD_AWS			= "fyers_eod_data_nse_cd_v1"
DB_NAME_NSE_CM_1MIN_AWS			= "fyers_1min_data_nse_cm_v4"
DB_NAME_NSE_FO_1MIN_AWS			= "fyers_1min_data_nse_fo_v1"
DB_NAME_NSE_CD_1MIN_AWS			= "fyers_1min_data_nse_cd_v1"
DB_NAME_TRADING_BRIDGE_AWS		= "fyers_trading_bridge"

##LOCAL
DB_ENDPOINT_LOCAL_READER		= "127.0.0.1"
DB_ENDPOINT_LOCAL_WRITER		= "127.0.0.1"
DB_PORT_LOCAL					= 3306
DB_UNAME_LOCAL					= "root"
DB_PASS_LOCAL					= ""

DB_NAME_NSE_CM_EOD_LOCAL		= "fyers_eod_data_nse_cm_v2"
DB_NAME_NSE_FO_EOD_LOCAL		= "fyers_eod_data_nse_fo_v1"
DB_NAME_NSE_CD_EOD_LOCAL		= "fyers_eod_data_nse_cd_v1"
DB_NAME_NSE_CM_1MIN_LOCAL		= "fyers_1min_data_nse_cm_v4"
DB_NAME_NSE_FO_1MIN_LOCAL		= "fyers_1min_data_nse_fo_v1"
DB_NAME_NSE_CD_1MIN_LOCAL		= "fyers_1min_data_nse_cd_v1"
DB_NAME_TRADING_BRIDGE_LOCAL	= "fyers_trading_bridge"

## Selected DB
DB_END_POINT_READER				= "127.0.0.1"
DB_ENDPOINT_WRITER				= "127.0.0.1"
DB_PORT 						= 3306
DB_UNAME 						= "root"
DB_PASS 						= ""

DB_NAME_NSE_CM_EOD				= DB_NAME_NSE_CM_EOD_AWS
DB_NAME_NSE_FO_EOD				= DB_NAME_NSE_FO_EOD_AWS
DB_NAME_NSE_CD_EOD				= DB_NAME_NSE_CD_EOD_AWS
DB_NAME_NSE_CM_1MIN				= DB_NAME_NSE_CM_1MIN_AWS
DB_NAME_NSE_FO_1MIN				= DB_NAME_NSE_FO_1MIN_AWS
DB_NAME_NSE_CD_1MIN				= DB_NAME_NSE_CD_1MIN_AWS
DB_NAME_TRADING_BRIDGE			= DB_NAME_TRADING_BRIDGE_AWS
