# James Cross, Michael Patel
# ECE 577
# Lab Hw1
# Question 5

# Input: (prompted)
#   - IP
#   - MAC
#   - Type
#
# Output:
#   - Interface name
#   - Interface type
#   - MAC address
#   - IP address

# Notes:
#   - use Linux system to run
#	- https://pypi.org/project/netifaces/

############################################################
import netifaces as ni
from netifaces import AF_INET  # IPv4
from netifaces import AF_LINK  # Ethernet


############################################################
def get_ip_info():
    # print(socket.gethostname())
    # print(socket.gethostbyaddr(socket.gethostname()))
    # print(socket.gethostbyname_ex(socket.gethostname()))
    #print(ni.interfaces())
    print("\nInterface : IP Address")
    for i in ni.interfaces():
        print(i + " : " + ni.ifaddresses(i)[AF_INET][0]["addr"])
        #print(ni.ifaddresses(i))


def get_mac_info():
    print("\nInterface : MAC Address")
    for i in ni.interfaces():
        print(i + " : " + ni.ifaddresses(i)[AF_LINK][0]["addr"])


def get_type_info():
    print("\nInterface : Type")
    for i in ni.interfaces():
        if "eth" in i:
            print(i + " : Ethernet")
        if "lo" in i:
            print(i + " : Loopback")
        if "fw" in i:
            print(i + " : Firewire")
        if "wlan" in i:
            print(i + " : Wireless")


############################################################
if __name__ == "__main__":
    i = input("Enter interface detail you would like (IP, MAC, Type): ")
    args = i.split()
    # print(args)
    if args.__contains__("IP"):
        get_ip_info()

    if args.__contains__("MAC"):
        get_mac_info()

    if args.__contains__("Type"):
        get_type_info()


