#!/usr/bin/python3
import getopt
import json
import os
import string
import sys
import time

import requests
from ftntlib import FortiOSREST
from tabulate import tabulate

hostname = ''
username = 'admin'
password = ''
serial = ''
version = ''
build = ''
clr_bg_red = '\033[0;37;41m'
clr_bg_green = '\033[0;30;42m'
clr_bg_yellow = '\033[0;30;43m'
clr_fg_yellow = '\033[1;33;40m'
clr_fg_white = '\033[1;37;40m'
clr_fg_green = '\033[1;32;40m'
clr_fg_grey = '\033[1;30;40m'
clr_fg_red = '\033[1;31;40m'
clr_fg_purple = '\033[1;35;40m'
clr_fg_blue = '\033[1;34;40m'
clr_reset = '\033[0m'


if len(sys.argv) < 1:
	print ('monitor_fos_ts.py -i <ipaddress> -u <username> -p <password>')
	sys.exit(2)
try:
	opts, args = getopt.getopt(sys.argv[1:],'hi:u:p:')
except getopt.GetoptError:
		print ('monitor_fos_ts.py -i <ipaddress> -u <username> -p <password>')
		sys.exit(2)
for opt, arg in opts:
	if opt in ('-h','--help'):
		print ('monitor_fos_ts.py -i <ipaddress> -u <username> -p <password>')
		sys.exit()
	elif opt in ('-i'):
		hostname = arg
	elif opt in ('-u'):
		username = arg
	elif opt in ('-p'):
		password = str(arg)

#print ('monitor_fos_ts.py -i' , hostname, ' -u ', username, ' -s ', password)
#exit()
#{
#  "http_method":"GET",
#  "results":[
#	  {
#      "interface":"OLTS_MPLS_0_0",
#      "parent":"OLTS_MPLS_0", <-- solo tunnel
#      "remote_gateway":"172.16.3.2", <-- solo tunnel
#      "network_id":10, <-- solo tunnel
#      "bandwidth":3998093,
#      "default_class":2,
#      "active_classes":[
#        {
#          "class_id":2,
#          "class_name":"DC_HUB",
#          "allocated_bandwidth":799618,
#          "guaranteed_bandwidth":799618,
#          "max_bandwidth":1999046,
#          "current_bandwidth":1,
#          "priority":"low",
#          "forwarded_bytes":8100144,
#          "dropped_packets":0,
#          "dropped_bytes":0
#        }]
#	  }
#  ]
#  }

fgt = FortiOSREST()   
try:
	#fgt.debug('on')    
	fgt.login(hostname, username, password)
	
	while True:  
		data = fgt.get('monitor', 'firewall', 'shaper', 'multi-class-shaper')
		shaper = json.loads(data)
		serial = shaper['serial']
		version = shaper['version']
		build = shaper['build']
		os.system('clear')
		print ('%sTime : %s\033[0m  %sHostname: %s (%s) Version %s build%s' % (clr_bg_red, time.ctime(), clr_bg_yellow, hostname, serial, version, build))
		for results in shaper['results']:
			interface = results['interface']
			bandwidth = results['bandwidth']
			default_class = results['default_class']
			if 'parent' in results.keys() and 'peer_id' in results.keys() and 'remote_gateway' in results.keys() :
				parent = results['parent']
				peer_id = results['peer_id']
				remote_gateway = results['remote_gateway']
				print('\n%sInterface: %s bandwidth: %s  default class_id: %s\033[0m  %sParent: %s Peer: %s Remote gateway: %s%s' % (
                    clr_bg_yellow, interface, bandwidth, default_class, clr_bg_green, parent, peer_id, remote_gateway, clr_fg_blue))
			else:
				print ('\n%sInterface: %s bandwidth: %s  default class_id: %s%s' % (clr_bg_yellow, interface, bandwidth, default_class, clr_fg_blue) )
			headers = [clr_fg_blue + 'id','name','allocated_bandwidth','max_bandwidth','guaranteed_bandwidth','priority','current_bandwidth','drop_bytes','forwarded_bytes']
			table = []
			for active_classes in results['active_classes']:
				if active_classes['current_bandwidth'] != 0:
					color_cb = clr_fg_green
				else:
					color_cb = clr_fg_grey
				table.append([
					clr_fg_yellow + str(active_classes['class_id']),
					clr_fg_yellow + active_classes['class_name'],
					clr_fg_white + str(active_classes['allocated_bandwidth']),
                    clr_fg_white + str(active_classes['max_bandwidth']),
					clr_fg_white + str(active_classes['guaranteed_bandwidth']),
					clr_fg_white + str(active_classes['priority']),
                    color_cb + str(active_classes['current_bandwidth']),
                    clr_fg_red + str(active_classes['dropped_bytes']),
                    clr_fg_purple + str(active_classes['forwarded_bytes'])
				])
				
			print(tabulate(table, headers, numalign="right"))

		time.sleep(2)

except KeyboardInterrupt:
	print ('%sInterrupt by user %s' % (clr_bg_yellow, clr_reset))
	
except json.decoder.JSONDecodeError: 
	print ('%sLogin failed to %s' % (clr_bg_red, hostname))

except (requests.exceptions.ConnectionError, OSError):
	print ('%sFailed to establish a connection to %s' % (clr_bg_red, hostname))

finally:
	fgt.logout()
	print("Exit")
	
	