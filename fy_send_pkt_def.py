#!/usr/bin/env python
from struct import Struct

## ***************** Multicast Send IP and Ports ***************** 
MULTICAST_IP 					= '224.1.1.10'
MULTICAST_PORT_CM 				= 10000
MULTICAST_PORT_FO 				= 10001
MULTICAST_PORT_CD 				= 10002
MULTICAST_PORT_CM_TEST			= 10003
MULTICAST_PORT_FO_TEST			= 10004
MULTICAST_PORT_CD_TEST			= 10005
MULTICAST_PORT_MCX_COM          = 10010
MULTICAST_PORT_MCX_COM_TEST     = 10012
## BSE
MULTICAST_PORT_CM_BSE			= 10015
MULTICAST_PORT_FO_BSE 			= 10016
MULTICAST_PORT_CD_BSE 			= 10017
MULTICAST_PORT_CM_TEST_BSE		= 10018
MULTICAST_PORT_FO_TEST_BSE		= 10019
MULTICAST_PORT_CD_TEST_BSE		= 10020


SEND_QUEUE_MAX_LEN				= 2000
SEND_PACKET_TIMEOUT 			= 0.3
## ******* Number of threads to send packets *******
CM_SEND_THREADS				= 3
FO_SEND_THREADS				= 5
CD_SEND_THREADS				= 2
COM_SEND_THREADS            = 3
CM_SEND_THREADS_TEST		= 1
FO_SEND_THREADS_TEST		= 5
CD_SEND_THREADS_TEST		= 2
COM_SEND_THREADS_TEST       = 5

CM_SEND_THREADS_BSE			= 3
FO_SEND_THREADS_BSE			= 5
CD_SEND_THREADS_BSE			= 2
CM_SEND_THREADS_TEST_BSE	= 5
FO_SEND_THREADS_TEST_BSE	= 5
CD_SEND_THREADS_TEST_BSE	= 2


## **************************** Fy_Packet Struct ****************************
FY_P_ENDIAN				= '>'
FY_P_STRUCT 			= "%s Q L H H H 6x"%(FY_P_ENDIAN) ## FY_TOKEN, Timestamp, FY_CODE, FY_FLAG, COMPRESSTION_LEN, 6-Reserved_Bytes
FY_P_HEADER 			= Struct(FY_P_STRUCT)
FY_P_CODE_7208 			= 1
FY_P_CODE_7207 			= 2
FY_P_CODE_6511 			= 3 ## 6511, 6521, 6531, 6571, 6583, 6584 have similar struct as 6511

# FY_P_STRUCT_NET_PAYLOAD	= "%sI I I I I I I I I I Q Q"%(FY_P_ENDIAN)
# FY_P_NET_PAYLOAD		= Struct(FY_P_STRUCT_NET_PAYLOAD)
## For 7207 and 7208 its the same values at the begining. It should contain 8*(4 byte data)
# FY_P_COMN_STRUCT_7_8 	= "%s 6I 2i"%(FY_P_ENDIAN) 
# FY_P_COMN_STRUCT_7_8 	= "%s 10I 2i L Q"%(FY_P_ENDIAN) ## New change Ajay 2018-10-10
FY_P_COMN_STRUCT_7_8 	= "%s 10I Q"%(FY_P_ENDIAN) ## New change Ajay 2018-11-05
FY_P_NET_COMN_PAYLOAD 	= Struct(FY_P_COMN_STRUCT_7_8)
FY_P_NET_7208_STRUCT	= "%s 4I 2Q"%(FY_P_ENDIAN) ## only for 7208 we have the extra values and bid ask list which will be appended to the payload.
FY_P_NET_7208			= Struct(FY_P_NET_7208_STRUCT)
FY_P_NET_6511_STRUCT 	= "%s 2H 239s"%(FY_P_ENDIAN)
FY_P_NET_6511 			= Struct(FY_P_NET_6511_STRUCT)

# FY_P_NET_BID_ASK_STRUCT	= "%s 2I"%(FY_P_ENDIAN)
FY_P_NET_BID_ASK_STRUCT	= "%s 3I"%(FY_P_ENDIAN) ## Change Ajay 2019-06-27 num order added
FY_P_NET_BID_ASK 		= Struct(FY_P_NET_BID_ASK_STRUCT)

FY_P_NET_NUM_PACT_STRUCT= "%s H"%(FY_P_ENDIAN)
FY_P_NET_NUM_PACT		= Struct(FY_P_NET_NUM_PACT_STRUCT)

## OI Struct changes 20190916 Palash
FY_P_EXTRA_OI_7202_STRUCT = "%s 7I"%(FY_P_ENDIAN)
FY_P_EXTRA_OI_7202        = Struct(FY_P_EXTRA_OI_7202_STRUCT)

FY_P_LEN_NUM_PACKET 	= 2
FY_P_LEN_HEADER 		= 24
# FY_P_LEN_COMN_PAYLOAD	= 32 ## 6 *4 + 4*2
# FY_P_LEN_COMN_PAYLOAD	= 60 ## 10*4 + 4*2 + 1*4 + 1*8 ## New change Ajay 2018-10-10
FY_P_LEN_COMN_PAYLOAD	= 48 ## 10*4 + 1*8 ## New change Ajay 2018-11-05
FY_P_LEN_EXTRA_7208		= 32 ## 4*4 + 2*8
# FY_P_LEN_BID_ASK 		= 8 ## 2*4
FY_P_LEN_BID_ASK		= 12 ## 3*4 ## Change Ajay 2019-06-27 num order added
FY_P_BID_ASK_CNT 		= 10
## **************************** End: Fy_Packet Struct ****************************
