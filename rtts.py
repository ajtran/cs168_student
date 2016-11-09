#git commands
#git branch -b [name]
#git add [file]
#git commit -m "[message]"
#git push origin master
import re
import json
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends import backend_pdf

with open("alexa_top_100") as filename:
	top_100 = filename.read().split()

def run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename):
	"""
	outputs two json files: 

		1) dictionary of hostnames : [RTTs]

		2) dictionary of hostnames : {"drop_rate": drop_rate1, "max_rtt": max_rtt1, "mediam_rtt": median_rtt1}
	"""

	print("HELLLLOOOOO")

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

		print(parse)

		marker = "--- " + host + " ping statistics ---"
		ind=parse.index(marker)
		sublist1 = parse[1:ind-1] #use this to extract times
		sublist1 = [x for x in sublist1 if not x.startswith("Request timeout for")]
		sublist2 = parse[ind:][1].split() #use this to extract drop rate

		print(sublist1)
		print(sublist2)

		#calculate drop rate ****NEED CASE IF DROP_RATE = 100%*** make MAX = -1.0, and MEDIAN = -1.0
		# drop_rate = sublist2[len(sublist2)-3] 
		# drop_rate = float(drop_rate[:len(drop_rate)-1])

		substring = parse[ind:][1]

		drop_rate = re.findall(r'\d+%', substring)[0]
		drop_rate = float(drop_rate[:len(drop_rate) - 1])

		if drop_rate == 100.0:

			aggr = {"drop_rate": drop_rate, "max_rtt": -1.0, "median_rtt": -1.0}
			aggr_file[host] = aggr
			raw_file[host] = []
			continue


		#parse times to float
		times = [float(x.split()[len(x.split())-2][5:]) for x in sublist1]

		#add times to first file host:[RTTs]
		raw_file[host] = times

		#sort time to extract MAX later and Median
		times.sort()

		MAX = times[len(times)-1]

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

	with open(raw_ping_output_filename, 'w') as rpo:
		json.dump(raw_file, rpo)

	with open(aggregated_ping_output_filename, 'w') as apo:
		json.dump(aggr_file, apo)

	print("DONE")


run_ping(["amazon.com"], 10, "raw_ping.json", "aggregated_ping.json")

def plot_median_rtt_cdf(agg_ping_results_filename, output_cdf_filename):

	"""
	this function should take in a filename with the json formatted 
	aggregated ping data and plot a CDF of the median RTTs for each 
	website that responds to ping

	"""
	# with open(agg_ping_results_filename) as apr:
	# 	data = json.load(apr)
	# medians = []
	# for value in data.values():
	# 	median = value["median_rtt"]
	# 	if median >= 0:
	# 		medians.append(median)
	# medians.sort()

	# plt.plot(medians, np.linspace(0,1,len(medians)))
	# plt.grid()
	# plt.xlabel("miliseconds")
	# plt.ylabel("Cumulative Fraction")
	# plt.show()

	def cumulative_fraction(list_medians, max_time):
		count = 0.0

		for median in list_medians:
			if median <= max_time:
				count+=1.0
			else:
				break
		fraction = count/float(len(list_medians))
		return fraction


	data = None
	MEDIAN = "median_rtt"

	x_values, y_values = [],[] 
	my_filepath = output_cdf_filename + ".pdf"

	init_x_val = 0.0

	with open(agg_ping_results_filename) as apr:
		data = json.load(apr) #of form hostname : {"drop_rate": drop_rate, "max_rtt": MAX, "median_rtt": median}
	print(data)
	median_rtts_list = []

	for dr_med in data.values():
		#make sure we do not plot hosts that were not reached
		if dr_med[MEDIAN] != -1.0:
			median_rtts_list.append(dr_med[MEDIAN])

	median_rtts_list.sort()

	MAX_MED = median_rtts_list[len(median_rtts_list)-1]
	
	x_val = init_x_val

	while x_val <= MAX_MED:

		x_values,y_values = x_val, cumulative_fraction(median_rtts_list,x_val)

		x_val = x_val + 0.1

	print(x_values)
	print(y_values)

	plot.plot(x_values, y_values, label= "rtt_a_agg")
	plot.legend() # This shows the legend on the plot.
	plot.grid() # Show grid lines, which makes the plot easier to read.
	plot.xlabel("MEDIAN") # Label the x-axis.
	plot.ylabel("DROP RATE") # Label the y-axis.
	plot.show()

	with backend_pdf.PdfPages(my_filepath) as pdf:
		pdf.savefig()


def plot_ping_cdf(raw_ping_results_filename, output_cdf_filename):

	"""
	this function should take in a filename with the json formatted 
	raw ping data for a particular hostname, and plot a CDF of the RTTs
	"""
	with open(raw_ping_results_filename) as rpr:
		data = json.load(rpr)
	for hostname, pings in data.items():
		plt.plot(pings, np.linspace(0,1,len(pings)), label=hostname)
	plt.legend()
	plt.grid() # Show grid lines, which makes the plot easier to read.
 	plt.xlabel("miliseconds") # Label the x-axis.
 	plt.ylabel("Cumulative Fraction") # Label the y-axis.
	with backend_pdf.PdfPages(output_cdf_filename) as pdf:
		pdf.savefig()