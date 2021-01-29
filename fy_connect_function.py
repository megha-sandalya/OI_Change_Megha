"""
Author      : Ajay A U [ajay@fyers.in]
Version     : 2.0
Copyright   : Fyers Securities
Web         : fyers.in
"""
#!/usr/bin/env python
import sys
# sys.path.append(r"../")

import elasticache_auto_discovery
from pymemcache.client.hash import HashClient
import redis

import fy_connect_defines as connDef
import fy_comn_def as comnDef

def connElasticCache(cacheNumber = connDef.FY_CACHE_NUM_1, numberOfConn = 1):
    """
    ## *********************** This is not used anymore since we shifted to redis. ***********************
    [Function]  :   This will connect to elastic cache end point and return the connection object to elastic cahce
    [Input]     :   cacheNumber     -> The elastic cache to which it has to connect to.
                    numberOfConn    -> Number of connections required. Max number will be 10
    [Output]    :   Fail: {comnDef.K_FUNCT_STAT : comnDef.V_FUNCT_FAIL_N_1, comnDef.K_FUN_DATA:[], comnDef.K_ERR_MSG:"Error message"}
                    Success: {comnDef.K_FUNCT_STAT : comnDef.V_FUNCT_SUCCESS_1, , comnDef.K_FUN_DATA:[], comnDef.K_ERR_MSG:"name of the service connected"}
    """
    retDict = {comnDef.K_FUNCT_STAT: comnDef.V_FUNCT_FAIL_N_1, comnDef.K_FUN_DATA:[], comnDef.K_ERR_MSG:"ERR : connElasticCache()->Unknown error."}
    if cacheNumber == connDef.FY_CACHE_NUM_1:   
        try:
            if numberOfConn < 10:

                nodesList = elasticache_auto_discovery.discover(connDef.ELASTCACHE_END_POINT, time_to_timeout=5.0)
                # print help(nodesList)
                # print "nodesList:", nodesList
                # print "cloudMemory:",cloudMemory
                nodesList = map(lambda x: (x[1], int(x[2])), nodesList)
                connList = []
                for eachConn in range(0, numberOfConn):
                    connList.append(HashClient(nodesList))
                retDict = {comnDef.K_FUNCT_STAT: comnDef.V_FUNCT_SUCCESS_1, comnDef.K_FUN_DATA:connList, comnDef.K_ERR_MSG:"Connected to %s"%(connDef.FY_CACHE_NUM_1)}
            else:
                retDict = {comnDef.K_FUNCT_STAT: comnDef.V_FUNCT_FAIL_N_1, comnDef.K_FUN_DATA:[], comnDef.K_ERR_MSG:"ERR : connElasticCache()->Cannot create more than 10 connection at a time."}
        except Exception, e:
            retDict = {comnDef.K_FUNCT_STAT: comnDef.V_FUNCT_FAIL_N_1, comnDef.K_FUN_DATA:[], comnDef.K_ERR_MSG:"ERR : connElasticCache()->Exception %s."%(e)}
            # functComn.LogError("ERROR", "connElasticCache", CONST_function_unknownError, "", e,cacheNumber)
    return retDict

def connectRedis(redisEP = connDef.REDIS_END_POINT_MASTER, port=6379, db=0):
    """
    [Function]  :   This will connect to redis instance and return radis_instance 
    [Input]     :   redisEP     -> End point of redis cluster.
                    port        -> Port of radis cluster
                    db          -> Db ssociated with it.
    [Output]    :   Fail: {comnDef.K_FUNCT_STAT : comnDef.V_FUNCT_FAIL_N_1, comnDef.K_FUN_DATA:[], comnDef.K_ERR_MSG:"Error message"}
                    Success: {comnDef.K_FUNCT_STAT : comnDef.V_FUNCT_SUCCESS_1, , comnDef.K_FUN_DATA:[], comnDef.K_ERR_MSG:"name of the service connected"}
    """
    retDict = {comnDef.K_FUNCT_STAT: comnDef.V_FUNCT_FAIL_N_1, comnDef.K_FUN_DATA:[], comnDef.K_ERR_MSG:"ERR : connectRedis()->Unknown error."}
    try:
        r = redis.StrictRedis(host=connDef.REDIS_END_POINT_MASTER, port=port, db=db)
        retDict = {comnDef.K_FUNCT_STAT: comnDef.V_FUNCT_SUCCESS_1, comnDef.K_FUN_DATA:[r], comnDef.K_ERR_MSG:"Connected to %s"%(connDef.REDIS_END_POINT_MASTER)}
    except Exception, e:
        retDict = {comnDef.K_FUNCT_STAT: comnDef.V_FUNCT_FAIL_N_1, comnDef.K_FUN_DATA:[], comnDef.K_ERR_MSG:"ERR : connectRedis()->Exception %s."%(e)}
    return retDict


if __name__ == "__main__":
    print "Your are not allowed."
    sys.exit()