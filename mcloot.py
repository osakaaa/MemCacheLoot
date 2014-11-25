import memcache
import argparse
import sys
from IPy import IP

'''
# Parse Command line args 
'''
mode_check = "check"
mode_loot = "loot"
mode_write = "write"
LOOTMODE = [mode_check, mode_loot, mode_write]

WRITE_CHECKER = ("VERYTEST","VERY_TEST_VALUE")

def cmd():
	parser = argparse.ArgumentParser(description='Simple looting tool for memcached services')	
	parser.add_argument('-t','--target', required=True, help='Specify target. It can be single host, or range of hosts, separated by hyphen. For now, only /24 net will scan n')
	parser.add_argument('-p','--port', default ="11211", help='Specify target port. By default 11211 is used\n')
	parser.add_argument('-m','--mode', default = mode_check, choices=LOOTMODE, help='Specify working mode. By default it only checks for read/write access')

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
	print "[!] Will %s IP's %s on port %s\n\n" % (mode, target, port)

	return (ipList,port,mode)


if __name__ == "__main__":
	ipList,port,mode = cmd()

	if mode == mode_check:
		for ip in ipList:
			print "Testing IP %s" % ip
			s = memcache.Client(["%s:%s" % (ip,port)])
			#print "Trying to set and request test parameter\n"
			s.set(WRITE_CHECKER[0],WRITE_CHECKER[1])
			r = s.get(WRITE_CHECKER[0])
			if r != None:
				print "[+]Pwned\n"
			else:
				print "[-]Immune\n"
	if mode == mode_loot:
		for ip in ipList:
			print "[!?] Loot actions too be done here"


	if mode == mode_write:
		for ip in ipList:
			print "[!?] Write actions to be write here"

