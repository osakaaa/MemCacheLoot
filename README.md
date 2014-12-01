MemCacheLoot
============

Simple utility to perform some looting (and also write/rewrite) operations on memcached services

###Usage:
python mcloot.py [-h] -t TARGET [-p PORT] [-m {info,loot,write}] [-k KEY]
                 [-v VALUE] [-o OUTPUT]

Optional arguments:
  -h, --help            show this help message and exit
  
  -t TARGET, --target TARGET
  
                        Specify target. It can be single host, or range of hosts, separated by hyphen. For now, only /24 nets are supported
                        
  -p PORT, --port PORT  
  
                        Specify target port. By default 11211 is used
  
  -m {info,loot,write}, --mode {info,loot,write}
  
                        info - Reads stats on specified memcached servers
                      
                        loot - Reads all the key:value pairs from specified memcached servers
                      
                        write - Tries to write arbitrary data to memcached data store
                      
                        By default loot will be used
                      
  -k KEY, --key KEY     
  
                        Required only for write mode. Key to write data to
                        
  -v VALUE, --value VALUE
  
                        Required only for write mode. Data to write for specified key
                        
  -o OUTPUT, --output OUTPUT
  
                        File to write the output
                        
###Requirements
It requires the following python modules to work:
- IPy (Can be installed with PIP)
