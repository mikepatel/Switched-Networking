# James Cross, Michael Patel
# ECE 577
# Lab Hw1
# Question 6

# Input:
#	- IP address
#	- number of hosts

# Output:
#	- first available subnet address

# Notes:

############################################################
import numpy as np
import sys


############################################################
def get_mask(x):
    x = np.ceil(np.log2(int(x)))  # return number of bits
    x = 32 - int(x)
    return int(x)


def get_ip(x):
    x = x.split("/")
    return x[0]


############################################################
if __name__ == "__main__":
    args = sys.argv
    # print(args)
    ip_addr = args[1]
    num_hosts = args[2]
    ip_addr = get_ip(ip_addr)
    mask = get_mask(num_hosts)
    print(ip_addr + "/" + str(mask))
