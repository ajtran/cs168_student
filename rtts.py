#git commands
#git branch -b [name]
#git add [file]
#git commit -m "[message]"
#git push origin master

import json
import subprocess

def run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename):
	"""
	outputs two json files: 

		1) dictionary of hostnames : [RTTs]

		2) dictionary of hostnames : {“drop_rate”: drop_rate1, “max_rtt”: max_rtt1, “median_rtt”: median_rtt1}

	"""

	raw_file = {}
	aggr_file = {}

	for host in hostnames:

		#send a ping to host
		ping = subprocess.Popen(
		    ["ping", "-c", str(num_packets), host],
		    stdout = subprocess.PIPE,
		    stderr = subprocess.PIPE
		)

		out, error = ping.communicate()
		data = out.decode("utf-8") 
		parse = data.split('\n')


		ind=parse.index("--- www.google.com ping statistics ---")
		sublist1 = parse[1:ind-1] #use this to extract times
		sublist1 = [x for x in sublist1 if not x.startswith("Request timeout for")]
		sublist2 = parse[ind:][1].split() #use this to extract drop rate

		print(sublist1)
		print(sublist2)

		#calculate drop rate ****NEED CASE IF DROP_RATE = 100%*** make MAX = -1.0, and MEDIAN = -1.0
		drop_rate = sublist2[len(sublist2)-3] 
		drop_rate = float(drop_rate[:len(drop_rate)-1])

		if drop_rate = 100.0:

			aggr = {"drop_rate": drop_rate, "max_rtt": -1.0, "median_rtt": -1.0}
			aggr_file[host] = aggr
			raw_file[host] =[]
			continue


		#parse times to float
		times = [float(x.split()[len(x.split())-2][5:]) for x in sublist1]

		#add times to first file host:[RTTs]
		raw_file[host] = times

		#sort time to extract MAX later and Median
		times.sort()

		#find median
		if len(times) % 2 != 0:
			#if there are an odd number of times
			split = int(len(times)/2)
			median = times[split]

		else:
			#if even number of times
			split = int(len(times)/2)
			upper_middle = times[split]
			lower_middle = times[split-1]
			median = (upper_middle + lower_middle)/2

		#create second file datastruct
		aggr = {"drop_rate": drop_rate, "max_rtt": MAX, "median_rtt": median}

		#add data to the second file
		aggr_file[host] = aggr





def plot_median_rtt_cdf(agg_ping_results_filename, output_cdf_filename):

	"""
	this function should take in a filename with the json formatted 
	aggregated ping data and plot a CDF of the median RTTs for each 
	website that responds to ping

	"""
	pass

def plot_ping_cdf(raw_ping_results_filename, output_cdf_filename):

	"""
	this function should take in a filename with the json formatted 
	raw ping data for a particular hostname, and plot a CDF of the RTTs
	"""
	pass
