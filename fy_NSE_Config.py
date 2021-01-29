"""
Author 		: Ajay A U [ajay@fyers.in]
Version 	: 2.0
Copyright 	: Fyers Securities
Web			: fyers.in
"""
# !/usr/bin/python
# from struct import calcsize
import struct

## **************************** RECV PORTS FOR INTERNAL BROADCAST ****************************
## These are the ports that will be used for testing purpose. These ports should only be used for loopback interface.
INTERNAL_LOOPBACK_IP_127 	= "127.0.0.1"
INTERNAL_BC_SEND_CM 		= 1980
INTERNAL_BC_SEND_FO 		= 1981
#INTERNAL_BC_SEND_CD 		= 1982
INTERNAL_BC_SEND_CD 		= 1984
INTERNAL_BC_RECV_CM 		= 1983
#INTERNAL_BC_RECV_FO 		= 1984
INTERNAL_BC_RECV_FO 		= 1982
INTERNAL_BC_RECV_CD 		= 1985

##PCAP file names
# PCAP_FILE_PATH 				= "E:\\Fyers\\Ganga\\Wireshark Data\\"
# PCAP_FILE_PATH 				= "E:\\Fyers\\wireshark\\nse_data\\"
PCAP_MAIN_FILE				= "E:\\Fyers\\wireshark\\nse_data\\cd\\nse_20170118_20minV1.pcapng"
PCAP_FILE_PATH 				= "E:\\Fyers\\wireshark\\nse_data\\"
# INTERNAL_PCAP_FILE_CM		= "cd\\nsecds_20180110_2hours.pcapng"
INTERNAL_PCAP_FILE_CM		= "NSE_CM.pcap"
INTERNAL_PCAP_FILE_FO		= "NSE_FO.pcap"
INTERNAL_PCAP_FILE_CD		= "NSE_CD.pcap"
# INTERNAL_PCAP_FILE_CD		= "cd\\nsecds_20180110_2hours.pcapng"
# INTERNAL_PCAP_FILE_FO		= "cd\\nsecds_20180110_2hours.pcapng"
# INTERNAL_PCAP_FILE_CM		= "20170214 Morning.pcapng"
# INTERNAL_PCAP_FILE_FO		= "20170214 Morning.pcapng"
# INTERNAL_PCAP_FILE_CD		= "20170214 Morning.pcapng"

## **************************** END: RECV PORTS FOR INTERNAL BROADCAST ****************************

## **************************** RECV PORTS ****************************
## LIVE
LIVE_RECV_PORT_CM 			= 1980 #1947#34074
LIVE_RECV_PORT_FO 			= 1981 #1948#34330
LIVE_RECV_PORT_CD 			= 1982 #1949#34586
## TEST
TEST_RECV_PORT_CM 			= 1980# 1993#1980##37146
TEST_RECV_PORT_FO 			= 1981#1994###37402
TEST_RECV_PORT_CD 			= 1982#1995 #1982##37658 ## For testing
## **************************** End RECV PORTS ****************************

## **************************** CNET_ID Sent by exchange ****************************
CNET_ID_CM 					= 4
CNET_ID_FO 					= 2
CNET_ID_CD 					= 6

## **************************** Process Thread Counts ****************************
THREADS_PROC_CM				= 1
THREADS_PROC_FO				= 2
THREADS_PROC_CD				= 1

## **************************** Price conversion ****************************
PRICE_CONV_100				= 100.0
PRICE_CONV_10000 			= 10000.0
PRICE_CONV_10000000 		= 10000000.0

## **************************** Time Adjustment ****************************
SECONDS_1970TO1980 			= 315532800 #315513000
## SECONDS_1970TO1980 315532799 /* 315513000*/ ## This is for testing. Added on 2017-05-18:This is not working

## **************************** Threading ****************************
SEND_PACKET_TIMEOUT 		= 0.3 ## This is in seconds
SEND_QUEUE_MAX_LEN			= 2000 ## Max length of the send queue

## **************************** Network Connection ****************************
NSE_MULTICAST_GROUP 		= "233.1.2.5" ## IP of multicast group that we have to hook.

LENGTH_UDPH_CHECK_BUF 		= 30 ## Length of queue that contian Header Checksum to remove duplicate packets
LENGTH_SOCK_RECV_BUF 		= 5000

## **************************** Packet Structure ****************************

## UDP-Header contain sourcePort(2-Byte)-destPort(2-Byte)-messageLength(2-Byte)-headerCheckSum(2-Byte)
## **************************** NOTE:Calc size is giving us improper results so do not use it ****************************
"""
	Note: Since calcsize is not working properly when the structure of the packet is changed the length will change accordingly.
	Length of the structures are hardcoded.
"""
UDP_HEADER_ENDINESS 		= ">"
UDP_HEADER_STRUCT_STR 		= "HHHH" #(srcPort_UH, dstPort_UH, lenMsg_UH, check_UH)
UDP_HEADER_STRUCT_P 		= struct.Struct(UDP_HEADER_ENDINESS + UDP_HEADER_STRUCT_STR)
UDP_HEADER_OFFSET			= 20
UDP_H_SIZE 					= 8 ##calcsize(UDP_HEADER_STRUCT_P)

UNUSED_BYTES_BC_H 			= 8

NSE_PACKET_ENDIANNESS		= ">"

# CNET_ID_PACKET_STRUCT		= "B"
NSE_CNET_ID_PACKET_STR		= "B"
NSE_CNET_ID_PACKET_STRUCT 	= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_CNET_ID_PACKET_STR) ## cNetId_Recv only one byte indicating the CNET ID of the segment type
NSE_CNET_ID_PACKET_SIZE 	= 1

NSE_P_COMPRSN_STR 			= "H"
NSE_P_COMPRSN_STRUCT		= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_P_COMPRSN_STR)
NSE_P_COMPRSN_SIZE 			= 2 ##calcsize('H')

NSE_P_NUM_PACK_STR 			= "H"
NSE_P_NUM_PACK_STRUCT 		= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_P_NUM_PACK_STR)
NSE_P_NUM_PACK_SIZE			= 2 ##calcsize('H')

NSE_PACKET_HEARER 			= "2BH"
NSE_PACKET_HEARER_STRUCT	= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_PACKET_HEARER)
NSE_PACKET_HEARER_SIZE		=  4 ##calcsize(NSE_PACKET_HEARER)

NSE_BC_HEADER_STRUCT_STR	= "4sI2sHhI4s2sIH8sH"
NSE_BC_HEADER_STRUCT 		= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_BC_HEADER_STRUCT_STR)
NSE_BC_HEADER_SIZE			= 40 ##calcsize(NSE_BC_HEADER_STRUCT)
# print "UDP_H_SIZE:%s, NSE_PACKET_HEARER_SIZE:%s, NSE_BC_HEADER_SIZE:%s"%(UDP_H_SIZE, NSE_PACKET_HEARER_SIZE, NSE_BC_HEADER_SIZE)

## **************************** 7208 ****************************
# (token, bookType, tradingStatus, volTradedToday, lastTradedPrice, netChangeIndicator, unknown_extra,
# netPChangeFromClosePrice, lastTradeQty, lastTradeTime, avgTradePrice, auctionNumber,
# auctionStatus, initiatorType, initiatorPrice, initiatorQty, auctionPrice, auctionQty, MBP_INFO_7208,
# bbTotalBuyFlag, bbTotalSellFlag, extraBuy4_, totalBuyQty, tBuyExtra,
# extraSell4_, totalSellQty, tSellExtra, MbpIndicatorBits, MbpIndicatorReserved, closingPrice,
# openPrice, highPrice, lowPrice)
UNUSED_BYTES_7208_BEGIN 	= 8
NSE_P_7208_CM 				= "HHHIIssIIIIHHHIIII120sHHsI3ssI3sssIIII" ## CM
NSE_P_7208_CM_NEW 			= "HHHIIssIIIIHHHIIII120sHHdd2sIIII"
NSE_P_7208_CM_STRUCT 		= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_P_7208_CM)
NSE_P_7208_CM_STRUCT_NEW 		= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_P_7208_CM_NEW)
NSE_P_7208_CM_SIZE			= 211 + 1 ##calcsize(NSE_PACKET_7208_CM) ## there is an additional byte that is there in the struct

NSE_P_7208_FO 				= "IHHIIssIIIIHHHIIII120sHHsI3ssI3sssIIII" ## FO/CD
NSE_P_7208_FO_NEW 			= "IHHIIssIIIIHHHIIII120sHHdd2sIIII" ## FO/CD
NSE_P_7208_FO_STRUCT 		= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_P_7208_FO)
NSE_P_7208_FO_STRUCT_NEW 		= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_P_7208_FO_NEW)
NSE_P_7208_FO_SIZE			= 213 + 1 ##calcsize(NSE_PACKET_7208_FO) ## there is an additional byte that is there in the struct
NSE_P_7208_FO_SIZE_NEW = 213 + 1 ##calcsize there is an additional byte because of the char of length 1 is present in the body structures so padded with an extra bytes


NSE_P_7208_MBP_INF 			= "I I H H"
NSE_P_7208_MBP_INF_STRUCT 	= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_P_7208_MBP_INF)
NSE_P_7208_MBP_INF_SIZE 	= 12
NSE_P_7208_MBP_COUNT		= 10

## New Ajay 2019-06-24
NSE_P_7202_INF				= "I H I I I I I"
NSE_P_7202_INF_STRUCT		= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_P_7202_INF)
NSE_P_7202_INF_SIZE			= 26

## 2:Open 3:Suspended
NSE_P_TRADIN_STAT_OPEN		= ["2", "3"]
## 1:Preopen 4:Preopen Extended 6->Price Discovery
NSE_P_TRADIN_STAT_CLOSE		= ["1", "4", "6"]
NSE_P_TRADIN_STAT_PREOPEN 	= ["1", "6"] ## New Change Ajay 2018-04-02 4 is not tested hence not included.
## **************************** End 7208 ****************************


## **************************** 7207 ****************************
NSE_P_7207					= "21s s I I I I I i I I I I Q s s" ## Change Ajay 2018-03-19 
NSE_P_7207_STRUCT 			= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_P_7207)
NSE_P_7207_SIZE				= 71 + 1 ## One unknown extra byte in the packet

## Please do not change the keys in the dict.
FY_TOKEN_7207_DICT		= {	"India VIX            ": 101000000026017,	"Nifty 100            ": 1010000000999001, 
							"Nifty 200            ": 1010000000999002, 	"Nifty 50             ": 101000000026000, 
							"Nifty 500            ": 1010000000999003,  "Nifty Auto           ": 1010000000999004,
							"Nifty Bank           ": 101000000026009,  	"Nifty Commodities    ": 1010000000999005, 
							"Nifty Consumption    ": 1010000000999006,  "Nifty CPSE           ": 101000000026041, 
							"Nifty Div Opps 50    ": 1010000000999007,  "Nifty Energy         ": 1010000000999008, 
							"Nifty Fin Service    ": 1010000000999009,  "Nifty FMCG           ": 1010000000999010, 
							"Nifty GrowSect 15    ": 1010000000999011,  "Nifty GS 10Yr        ": 1010000000999012, 
							"Nifty GS 10Yr Cln    ": 1010000000999013,  "Nifty GS 11 15Yr     ": 1010000000999014, 
							"Nifty GS 15YrPlus    ": 1010000000999015,  "Nifty GS 4 8Yr       ": 1010000000999016, 
							"Nifty GS 8 13Yr      ": 1010000000999017,  "Nifty GS Compsite    ": 1010000000999018, 
							"Nifty Infra          ": 101000000026019,  	"Nifty IT             ": 101000000026008, 
							"Nifty Media          ": 1010000000999019,  "Nifty Metal          ": 1010000000999020, 
							"Nifty Mid Liq 15     ": 1010000000999021,  
							# "Nifty MID100 Free    ": 1010000000999022, ## Name change 
							"Nifty Midcap 50      ": 101000000026014,  	"Nifty MNC            ": 1010000000999023, 
							"Nifty Next 50        ": 1010000000999024,  "Nifty Pharma         ": 1010000000999025, 
							"Nifty PSE            ": 101000000026024,  	"Nifty PSU Bank       ": 1010000000999026, 
							"Nifty Pvt Bank       ": 1010000000999027,  "Nifty Quality 30     ": 1010000000999028, 
							"Nifty Realty         ": 1010000000999029,  "Nifty Serv Sector    ": 1010000000999030, 
							# "Nifty SML100 Free    ": 1010000000999031, ## Name change  
							"Nifty100 Liq 15      ": 1010000000999032, 
							"Nifty50 Div Point    ": 1010000000999033,  "Nifty50 PR 1x Inv    ": 1010000000999034, 
							"Nifty50 PR 2x Lev    ": 1010000000999035,  "Nifty50 TR 1x Inv    ": 1010000000999036, 
							"Nifty50 TR 2x Lev    ": 1010000000999037,  "Nifty50 Value 20     ": 1010000000999038,
							"NIFTY Alpha 50       ": 1010000000999039,  "NIFTY100 EQL Wgt     ": 1010000000999040,
							"NIFTY100 LowVol30    ": 1010000000999041,  "NIFTY50 EQL Wgt      ": 1010000000999042,
							"HangSeng BeES-NAV    ": 1010000000999043,
							## Name change ## New Ajay 2018-0411
							"NIFTY MIDCAP 100     ": 1010000000999022,  "NIFTY SMLCAP 100     ": 1010000000999031,
							## Name Change ## New Ajay 2018-07-16
							"NIFTY100 Qualty30    ": 1010000000999028,
							## Change Ajay 2019-06-20
							"NIFTY200 QUALTY30    ": 1010000000999044,   "NIFTY MIDCAP 150     ": 1010000000999045,
							"NIFTY SMLCAP 50      ": 1010000000999046,   "NIFTY SMLCAP 250     ": 1010000000999047,
							"NIFTY MIDSML 400     ": 1010000000999048
							}
							
## **************************** End 7207 ****************************
## **************************** 6511, 6521, 6531, 6571, 6583, 6584 have similar struct as 6511****************************
NSE_SEC_INFO_SIZE_CM		= 12
NSE_SEC_INFO_SIZE_FO		= 30

NSE_P_6511					= "H H H 239s"
NSE_P_6511_STRUCT 			= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_P_6511)
NSE_P_6511_SIZE 			= 245
NSE_STAT_TCODE_LIST 		= [6511, 6521, 6531, 6571, 6583, 6584, 6571]
## **************************** End 6511 ****************************
## **************************** Start 6501 ****************************
NSE_P_6501					= "H 5s 3s 4s 2s H 239s"
NSE_P_6501_STRUCT 			= struct.Struct(NSE_PACKET_ENDIANNESS + NSE_P_6501)
NSE_P_6501_SIZE 			= 297

## **************************** Transaction Code ****************************
NSE_T_CODE_7207				= 7207
NSE_T_CODE_7216				= 7216
NSE_T_CODE_7208				= 7208
NSE_T_CODE_6511				= 6511
NSE_T_CODE_6501				= 6501
NSE_T_CODE_7202				= 7202 ## New Ajay 2019-06-24

## **************************** END :Transaction Code ****************************



def main():
	None


if __name__ == "__main__":
	main()
