import fy_comn_Funct as fyCmnFunct
import fy_comn_def as fyCmnDef

class SetGlobalVars():
	"""Class for setting global variables to be used across modules"""
	global_timeStamp	= 0 ## This will contain begining of the min eg: 15:30:00 hours 
	global_TS_NSE 		= 0 ## this will contain the actual time stamp sent by NSE eg; 15:30:05
	global_rxPackets, global_packetProcess = 0, 0
	global_rejected		= 0 ## New Ajay 2018-06-01
	global_FailedTokenDict = {}
	global_newDayFlag 	= 0
	global_7208Count	= 0
	global_7202Count	= 0
	global_tradingStat 	= 1 ## We should start like premarket. Otherwise is we restart the program at 8:00 AM IST it will create 1 min candle for index tokens

	global_marketStat	= True ## This will be False at the begining and it changes according to 7208 packet trading status.
	global_minSetFlag 	= fyCmnDef.MKT_F_NORMAL_OPEN ## New change Ajay 2018-04-10

	global_checkMktStat = False ## Not used

		