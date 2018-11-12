import paramiko
import time

ip = "192.168.1.2"
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

shell.send("?\n")
time.sleep(1)

shell.send("en\n")
time.sleep(1)

output = shell.recv(65535)
output = output.decode("utf-8")
print(output)