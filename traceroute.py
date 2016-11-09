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
  timestamp = str(time.time())
  output = {"timestamp": timestamp}

  for hostname in hostnames:
    output[hostname] = []

    traceroute = subprocess.Popen(
      ["traceroute", "-a", "-q", str(num_packets), hostname],
      stdout = subprocess.PIPE,
      stderr = subprocess.PIPE
    )

    out, error = traceroute.communicate()

    for line in out.split('\n'):
      print(line)
      splitted = line.split()
      if splitted:
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

  with open(output_filename, "a") as filename:
    json.dump(output, filename)

# test with one packet on google.com -- works
exper_a = ["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp", "www.vutbr.cz", "zanvarsity.ac.tz"]
run_traceroute(exper_a, 5, "tr_a.json")

def parse_traceroute(raw_traceroute_filename, output_filename):
  """
  This function should be able to take in outputs from a traceroute run 
  (either from TRACEROUTE or from a separate run) and write out json data.
  """
  pass