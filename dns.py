# -*- coding: utf-8 -*-
import re
import json
import subprocess
import numpy as np
import matplotlib.pyplot as plot
from matplotlib.backends import backend_pdf
import utils as UT

with open("alexa_top_100") as filename:
	top_100 = filename.read().split()

"""
resolves IP addresses and generates json output summarizing the results. 
Your script should have several functions for running dig, as well as 
processing the dig outputs

"""


def run_dig(hostname_filename, output_filename, dns_query_server=None):

	"""
	runs dig command on hostname

	"""
	dig_output = []

	hostnames = hostname_filename

	for host in hostnames:
		for _ in range(5):
			dig_host = {}
			if dns_query_server:
				dig = subprocess.Popen(
						["dig", host, "@" + dns_query_server],
						stdout = subprocess.PIPE,
						stderr = subprocess.PIPE
						)
			else:
				dig = subprocess.Popen(
			  	  ["dig", "+trace", "+tries=1", "+nofail", host],
			   		stdout = subprocess.PIPE,
			      stderr = subprocess.PIPE
						)

			out, error = dig.communicate()
			data = out.decode("utf-8")
			parse = data.split('\n')

			queries = parse[3:]

			dig_host[UT.NAME_KEY] = host
			dig_host[UT.SUCCESS_KEY] = True
			dig_host[UT.QUERIES_KEY] = []

			markers = re.findall(";;\sReceived\s\d+\sbytes\sfrom\s.+\sin\s\d+\sms", data)

			low_index = 0
			
			for mark in markers:

				high_index = queries.index(mark)
				Query = queries[low_index:high_index]
				Query = [filter(None, re.split("[ \t]+", x)) for x in Query]

				time = mark.split()
				time = int(time[len(time)-2])
				
			
				answer = []

				for q in Query:
				
					answer.append({UT.QUERIED_NAME_KEY:q[0], UT.ANSWER_DATA_KEY:q[4], UT.TYPE_KEY: q[3], UT.TTL_KEY: int(q[1])})


				# for i in answer:

				# 	print(i)

				Query_dict = {UT.TIME_KEY:time,UT.ANSWERS_KEY:answer}

				if UT.QUERIES_KEY not in dig_host.keys():
					dig_host[UT.QUERIES_KEY] = [Query_dict]
				else:
					dig_host[UT.QUERIES_KEY].append(Query_dict)

				low_index = high_index+2

			# print(dig_host)


			dig_output.append(dig_host)

	
	with open(output_filename, 'w') as rpo:
		json.dump(dig_output, rpo)


def get_average_ttls(filename):

	"""
	It should return a 4-item list that contains the following averages, in this order:
	What’s the average TTL of the root servers?
	What’s the average TTL for the tld servers?
	What’s the average TTL for any other name servers? (e.g., for google.com, this includes the google.com name server).
	What’s the average TTL for the terminating CNAME or A entry?

	"""
	root_servers, tld_servers, other_servers, A_CN_servers = [], [], [], []
	rs, tld, A, CN = ".", "com.", "A", "cname"


	with open(filename) as rpr:
		data = json.load(rpr)

	
	for queries in data:

		for q_list in queries[UT.QUERIES_KEY]:

			for query in q_list[UT.ANSWERS_KEY]:

				if query[UT.QUERIED_NAME_KEY] == rs:
					root_servers.append(query[UT.TTL_KEY])
				elif query[UT.QUERIED_NAME_KEY] == tld:
					tld_servers.append(query[UT.TTL_KEY])
				elif query[UT.TYPE_KEY] == A or query[UT.TYPE_KEY] == CN:
					A_CN_servers.append(query[UT.TTL_KEY])
				else:
					other_servers.append(query[UT.TTL_KEY])

	# print(root_servers)
	# print(tld_servers)
	# print(other_servers)
	# print(A_CN_servers)

	average_root_ttl = reduce(lambda x, y: x + y, root_servers)/len(root_servers)
	average_TLD_ttl = reduce(lambda x, y: x + y, tld_servers)/len(tld_servers)
	average_other_ttl = reduce(lambda x, y: x + y, other_servers)/len(other_servers)
	average_terminating_ttl = reduce(lambda x, y: x + y, A_CN_servers)/len(A_CN_servers)

	rtn = [average_root_ttl, average_TLD_ttl, average_other_ttl, average_terminating_ttl]
	# print(rtn)

	return rtn

def get_average_times(filename):

	site_rslv_times = []
	site_final_req_times = []

	with open(filename) as rpr:
		data = json.load(rpr)

	
	for queries in data:

		for q_list in queries[UT.QUERIES_KEY]:

			site_rslv_times.append(q_list[UT.TIME_KEY])

			for query in q_list[UT.ANSWERS_KEY]:

				if query[UT.TYPE_KEY] == "A" or query[UT.TYPE_KEY] == "cname":

					site_final_req_times.append(q_list[UT.TIME_KEY])

	# print(site_rslv_times)
	# print(site_final_req_times)

	avg_rslv_time = reduce(lambda x, y: x + y, site_rslv_times)/len(site_rslv_times)
	avg_final_req_time = reduce(lambda x, y: x + y, site_rslv_times)/len(site_rslv_times)

	# print ([avg_rslv_time,avg_final_req_time])
	return [avg_rslv_time,avg_final_req_time]
	

def generate_time_cdfs(json_filename, output_filename):
	with open(json_filename) as filename:
		data = json.load(filename)

	site_rslv_times = []
	site_final_req_times = []

	for queries in data:
		for q_list in queries[UT.QUERIES_KEY]:
			site_rslv_times.append(q_list[UT.TIME_KEY])
			for query in q_list[UT.ANSWERS_KEY]:
				if query[UT.TYPE_KEY] == "A" or query[UT.TYPE_KEY] == "cname":
					site_final_req_times.append(q_list[UT.TIME_KEY])

	site_rslv_times.sort()
	site_final_req_times.sort()

	plot.plot(site_rslv_times, np.linspace(0,1,len(site_rslv_times)), label="Time to Resolve Site") #hm... what do i plot instead?
	plot.plot(site_final_req_times, np.linspace(0,1,len(site_final_req_times)), label="Time to Resolve Final Request")
	plot.legend()
	plot.grid() # Show grid lines, which makes the plot easier to read.
 	plot.xlabel("milliseconds") # Label the x-axis.
 	plot.ylabel("Cumulative Fraction") # Label the y-axis.
 	# plot.show()
	with backend_pdf.PdfPages(output_filename) as pdf:
		pdf.savefig()


def count_different_dns_responses(filename1, filename2):

	with open(filename1) as rpr:
		file1_data = json.load(rpr)

	with open(filename2) as rpr:
		file2_data = json.load(rpr)

	differences1 = 0

	#get all the terminating queries from filename1

	hosts1 = {} #of form host: A queries 

	for queries in file1_data:

		sub_q = []

		if not queries[UT.NAME_KEY] in hosts1.keys():

			hosts1[queries[UT.NAME_KEY]] = []

		for q_data in queries[UT.QUERIES_KEY]:

			if len(q_data[UT.ANSWERS_KEY]) != 0:

				for rslv_times in q_data[UT.ANSWERS_KEY]: 

					if (rslv_times[UT.TYPE_KEY] == "A") or (rslv_times[UT.TYPE_KEY] == "cname"):

						sub_q.append(rslv_times)

		if len(sub_q) != 0:

			hosts1[queries[UT.NAME_KEY]].append(sub_q)

	# for q in hosts1.values():

	# 	print("\n")
	# 	print(q)

	for key,values in hosts1.items():

		if len(values) == 0:
			del hosts1[key]

	#convert to set:

	hosts1_set = {}

	
	for keys in hosts1.keys():

		hosts1_set[keys] = []

	for host_data in hosts1:

		data = hosts1[host_data]

		for q_info in data:

			ip_set = set()
			# print(q_info)
			for q in q_info:
				ip_set.add(q[UT.ANSWER_DATA_KEY])
			
			hosts1_set[host_data].append(ip_set)

	print(hosts1_set)


	# #get all the terminating queries from filename2

	# hosts2 = {} #of form host: A queries

	# for queries in file2_data: #queries is dictionary w/ Name, success, and Queries keys {Name: , success:, Queries: []}

	# 	if not queries[UT.NAME_KEY] in hosts2.keys():

	# 		hosts2[queries[UT.NAME_KEY]] = []

	# 	for q_data in queries[UT.QUERIES_KEY]: #q_data of form [{time in millis:, ANSWERS: []}, {}, {} ..., {}]

	# 		for rslv_times in q_data[UT.ANSWERS_KEY]: 

	# 			if (rslv_times[UT.TYPE_KEY] == "A") or (rslv_times[UT.TYPE_KEY] == "cname"):

	# 				hosts2[queries[UT.NAME_KEY]].append(rslv_times)

	# for host_data in hosts1:

	# 	data = hosts1[host_data]
		
	# 	ip = data[0][UT.ANSWER_DATA_KEY]

	# 	for req in data:

	# 		if ip != req[UT.ANSWER_DATA_KEY]:

	# 			differences1 = differences1 + 1

	# for key,values in hosts2.items():

	# 	if len(values) == 0:
	# 		del hosts2[key]

	# print(differences1)

	return differences1





count_different_dns_responses("dns_output_1.json","dns_output_2.json")

				

# run 1
# run_dig(top_100, "dns_output_1.json")

# run 2 - one hour apart
# run_dig(top_100, "dns_output_2.json")

# (a)
# print(get_average_ttls("dns_output_1.json"))

# (b)
# generate_time_cdfs("dns_output_1.json", "writeup/dns_output_1.png")

# (d) 
# run_dig(top_100, "dns_output_kor.json", "221.132.89.153")