"""
Author 		: Ajay A U [ajay@fyers.in]
Version 	: 2.0
Copyright 	: Fyers Securities
Web			: fyers.in
"""
#!/usr/bin/python
import struct

## ******************* Network connections *******************
FY_RECV_LOCAL_IP_BIND 	= ""
# FY_RECV_IP_ADDR			= "45.112.18.3" ## The IP of the data-center from which we receive the data
FY_RECV_IP_ADDR			= "203.112.146.243" ## The IP of the data-center from which we receive the data. This is IP of RS server.

## Multicast details
FY_MULTIC_SEND_GROUP_IP 	= "239.10.0.100"
FY_MULTIC_SEND_PORT_NSE_CM	= 1970
FY_MULTIC_SEND_PORT_NSE_FO	= 1971
FY_MULTIC_SEND_PORT_NSE_CD	= 1972
#FY_MULTIC_SEND_PORT_NSE_CD	= 1982
FY_MULTIC_SEND_PORT_NSE_CM_T= 1973
FY_MULTIC_SEND_PORT_NSE_FO_T= 1974
FY_MULTIC_SEND_PORT_NSE_CD_T= 1975

## ******************* END : Network connections *******************

SOCK_RECV_TIMEOUT_SEC 	= 5.0
## *******************  Network packet struct *******************

LENGTH_UDPH_CHECK_BUF	= 30
## *******************  End: Network packet struct *******************

LEN_Q_MIN_DATA 			= 100

## ******************* END : String constants *******************

def main():
	print "You should not run this file"

if __name__ == "__main__":
	main()