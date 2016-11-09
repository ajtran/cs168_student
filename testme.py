# # testing....

import subprocess
import time
import re
import json

hostname = "google.com"

# ping = subprocess.Popen(
#     ["ping", "-c", "10", host],
#     stdout = subprocess.PIPE,
#     stderr = subprocess.PIPE
# )

timestamp = str(time.time())
traceroute = subprocess.Popen(
  ["traceroute", "-a", "-q", "1", hostname],
  stdout = subprocess.PIPE,
  stderr = subprocess.PIPE
)

# out, error = ping.communicate()

out, error = traceroute.communicate()

# data = out.decode("utf-8") 
# parse = data.split('\n')

# splitted = out.split('\n')


output = {"timestamp":timestamp, hostname:[]}
for line in out.split('\n'):
  # name, ip, ASN
  print(line)
  splitted = line.split()
  if splitted:
  #   hop = splitted[0]
    if re.match('^\d+$', splitted[0]):
      # new hop
      ASN = splitted[1][3:len(splitted[1])-1]
      name = splitted[2]
      ip = splitted[3][1:len(splitted[3])-1]
      hops = [{"ip": ip, "name": name, "ASN": ASN}]
      output[hostname].append(hops)
    else:
      ASN = splitted[0][3:len(splitted[0])-1]
      name = splitted[1]
      ip = splitted[2][1:len(splitted[2])-1]
      hops.append({"ip": ip, "name": name, "ASN": ASN})

with open("google_route.json", "w") as gr:
  json.dump(output, gr)

# ind=parse.index("--- www.google.com ping statistics ---")

# sublist1 = parse[1:ind-1] #times
# sublist1 = [x for x in sublist1 if not x.startswith("Request timeout for")]
# sublist2 = parse[ind:][1].split()

# print(sublist1)
# print(sublist2)



# drop_rate = sublist2[len(sublist2) -3]
# drop_rate = float(drop_rate[:len(drop_rate)-1])

# print("DROP RATE:")
# print(drop_rate)

# times = [float(x.split()[len(x.split())-2][5:]) for x in sublist1]
# times.sort()

# print("TIMES:")
# print(times)

# MAX = times[len(times)-1]
# print("MAX:")
# print(MAX)


# if len(times) % 2 != 0:

# 	split = int(len(times)/2)
# 	median = times[split]
# else:
	
# 	split = int(len(times)/2)
# 	upper_middle = times[split]
# 	lower_middle = times[split-1]
# 	median = (upper_middle + lower_middle)/2

# print("MEDIAN:")
# print(median)
