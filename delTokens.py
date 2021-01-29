#!/usr/bin/env python

import sys
import os
import json

import fy_comn_Funct as cmnFun
import fy_connect_function as fyConn
import fy_comn_def as cDef
def main():
	print "You are not allowed run this program. Please contact sys-admin."
	sys.exit()
	tokenList = [101000000020532, 101000000025640, 101000000023804, 101000000020532, 101000000019679, 101000000019543, 101000000018292, 101000000017272, 101000000015330, 101000000014858, 101000000014535, 101000000014428]
	print "total tokens:%s"%(len(tokenList))
	# sys.exit()
	retRedisConn = fyConn.connectRedis()
	if retRedisConn[cDef.K_FUNCT_STAT] !=  cDef.V_FUNCT_SUCCESS_1:
		print "ERR : connect to redis failed"
		sys.exit()
	# print retRedisConn[cDef.K_FUN_DATA]
	redisConn = retRedisConn[cDef.K_FUN_DATA][0]
	print redisConn
	# setRet = redisConn.set("test", "testVal", ex=10)
	# print "setRet:%s"%(setRet)
	# print redisConn.get("test")
	# sys.exit()
	for eachToken in tokenList:
		tokenSym = "%s-%s"%(eachToken, 1027)
		print "tokenSym:%s val:%s"%(tokenSym, redisConn.get(tokenSym))
		# print redisConn.get(tokenSym)
	# "token-1027"



if __name__ == "__main__":
	main()