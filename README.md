MemCacheLoot
============

Simple utility to check  memcached services for anonymous read/write access and performing some looting operations

###Usage:
mcloot.py [-h] -t TARGET [-p PORT] [-m {info,loot,write}] [-o OUTPUT]

optional arguments:

  -h, --help            show this help message and exit
  
  -t TARGET, --target TARGET
  
                        Specifies target. It can be single host, or range of hosts, separated by hyphen. 
                        For now, only /24 net will be scanned
                        
  -p PORT, --port PORT  Specifies target port. By default 11211 is used
  
  -m {info,loot,write}, --mode {info,loot,write}
                          Specifies working mode.
                          
                          info - Reads stats on specified memcached servers
                          
                          loot - Reads all the key:value pairs from specified memcached servers
                          
                          write - Tries to write arbitrary data to memcached data store (NOT IMPLEMENTED!!)
                          
                          By default loot will be used
                          
  -o OUTPUT, --output OUTPUT
  
                          File to write output to.
                        
###Requirements
It requires the following python modules to work:
- IPy

Both can be installed with PIP
