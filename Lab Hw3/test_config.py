import paramiko
import time

ip = "192.168.1.10"
username = "exam"
password = "exam"
handler = paramiko.SSHClient()
handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    handler.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False)
except Exception as e:
    print("\nException: ", str(e))

shell = handler.invoke_shell()

shell.send("terminal length 0\n")  # forces terminal to print everything; no space needed
time.sleep(1)

shell.send("en\n")
time.sleep(1)

shell.send("exam\n")  # assume enable password is "exam"
time.sleep(1)

shell.send("show int trunk\n")
time.sleep(2)

'''
shell.send("conf t\n")
time.sleep(1)

shell.send("spanning-tree vlan 1\n")
time.sleep(3)

shell.send("end\n")
time.sleep(1)
'''

output = shell.recv(65535)
output = output.decode("utf-8")
output = str(output)
output.strip("\r\n")
#print(output)

if "Vlans allowed on trunk" in output:
    vlans = output.split("Vlans allowed on trunk")

#print(vlans[1])
x = str(vlans[1])
x = x.strip("\r\n")
#print(x)

print("##")
vlans = x.split("\r\n\r\nPort")
#print(vlans[0])
y = str(vlans[0])
print("##")
y = y.split("\r\n")
#print(y)
q = []
for z in y:
    z = z.split("       ")
    #print(z)
    q.append(z)
print(q)