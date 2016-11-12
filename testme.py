# # testing....

import subprocess
import time
import re
import json

# hostname = "google.com"

# timestamp = str(time.time())
# traceroute = subprocess.Popen(
#   ["traceroute", "-a", "-q", "5", hostname],
#   stdout = subprocess.PIPE,
#   stderr = subprocess.PIPE
# )

# out, error = traceroute.communicate()

# with open("google_test.txt", "w") as filename:
#   filename.write(timestamp + '\n')
#   for line in out.split('\n')
#     filename.write(out)

with open("google_facebook.txt") as filename:
  timestamp = filename.readline().strip()
  content = filename.readlines()

for line in content:
  if re.match("^[a-zA-Z]+(\.[a-zA-Z]+)+$", line):
    hostname = line.strip()

def yes(query, data):
  if re.findall(query, data):
    print("yes")
  else:
    print("no")


# output = {"timestamp":timestamp, hostname:[]}
# for line in out.split('\n'):
#   # name, ip, ASN
#   print(line)
#   splitted = line.split()
#   if splitted:
#   #   hop = splitted[0]
#     if re.match('^\d+$', splitted[0]):
#       # new hop
#       ASN = splitted[1][3:len(splitted[1])-1]

#       name = splitted[2]
#       ip = splitted[3][1:len(splitted[3])-1]
#       if ASN == "0" or ASN == "*":
#         ASN == "None"
#       if ip == "*":
#         ip = "None"
#       if name == "*":
#         name = "None"
#       name = splitted[2]

#       hops = [{"ip": ip, "name": name, "ASN": ASN}]
#       output[hostname].append(hops)
#     else:
#       ASN = splitted[0][3:len(splitted[0])-1]
#       if ASN == "0" or ASN == "*":
#         ASN == None
#       name = splitted[1]
#       if name == "*":
#         name = "None"
#       ip = splitted[2][1:len(splitted[2])-1]
#       if ip == "*":
#         ip = "None"
#       hops.append({"ip": ip, "name": name, "ASN": ASN})

# with open("google_route.json", "w") as gr:
#   json.dump(output, gr)
