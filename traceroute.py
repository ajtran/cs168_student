import json
import re
import subprocess
import time


def run_traceroute(hostnames, num_packets, output_filename):
  """
  Used to run the traceroute command on a list of hostnames.
  """
  # does not account for edge case like when there is no name,
  # ip address, ASN, or just *'s or even duplicate routers
  content = ""

  timestamp = str(time.time())
  content += timestamp + '\n'

  for hostname in hostnames:
    print(hostname)
    content += hostname + '\n'

    traceroute = subprocess.Popen(
      ["traceroute", "-a", "-q", str(num_packets), hostname],
      stdout = subprocess.PIPE,
      stderr = subprocess.PIPE
    )

    out, error = traceroute.communicate()

    content += out

  with open(output_filename, "w") as filename:
    filename.write(content)

# experiment a - 5 @ 6:00
# exper_a = ["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp", "www.vutbr.cz", "zanvarsity.ac.tz"]
# run_traceroute(exper_a, 5, "tr_a_test.txt")

def parse_traceroute(raw_traceroute_filename, output_filename):
  """
  This function should be able to take in outputs from a traceroute run 
  (either from TRACEROUTE or from a separate run) and write out json data.
  """
  with open(raw_traceroute_filename) as filename:
    timestamp = filename.readline().strip()
    hostname = filename.readline().strip()
    content = filename.readlines()

  output = {"timestamp": timestamp, hostname: []}
  ips = set()

  for line in content:
    if re.match("^[a-zA-Z]+(\.[a-zA-Z]+)+$", line):
      hostname = line.strip()
      output[hostname] = []
      # just in case
      continue

    ASN = re.findall("\[AS\s*\d+\]", line) # gonna have to strip "ASN "
    ip = re.findall("\d+\.\d+\.\d+\.\d+", line) # does this work for all cases?
    name = re.findall("\s[0-9a-zA-Z-._]+\s\(", line) # need to find pattern for name... if no name use ip

    ## if statements ## ### I think we need another check for duplicates...
    if ASN and ASN[0].strip("[ASN ]") != "0":
      ASN = ASN[0].strip("[ASN ]")
    else:
      ASN = "None"

    if ip:
      ip = ip[0]
    else:
      ip = "None"

    if name:
      name = name[0].strip(" (")
    else:
      name = ip

    # if there is a damn number
    if re.match("^\s*\d+\s", line):
      ips = set() # deduplication
      hops = [{"ip": ip, "name": name, "ASN": ASN}]
      output[hostname].append(hops)
      ips.add(ip)
    else:
      if ip == "None":
        hops.append({"ip": ip, "name": name, "ASN": ASN})
      else:
        if ip not in ips: # deduplication
          hops.append({"ip": ip, "name": name, "ASN": ASN})
          ips.add(ip)

  with open(output_filename, "a") as filename:
    json.dump(output, filename)
    filename.write('\n')

# experiment a
# parse_traceroute("tr_a_1.txt", "tr_a.json")
# parse_traceroute("tr_a_2.txt", "tr_a.json")
# parse_traceroute("tr_a_3.txt", "tr_a.json")
# parse_traceroute("tr_a_4.txt", "tr_a.json")
# parse_traceroute("tr_a_5.txt", "tr_a.json")

# experiment b
# parse_traceroute("tr_to.txt", "tr_b.json")
# parse_traceroute("tr_from.txt", "tr_b.json")




