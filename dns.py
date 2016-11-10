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
		dig_host = {}
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

				answer.append({UT.QUERIED_NAME_KEY:q[0], UT.ANSWER_DATA_KEY:q[4], UT.TYPE_KEY: q[3], UT.TTL_KEY: q[1]})


			Query_dict = {UT.TIME_KEY:time,UT.ANSWERS_KEY:answer}

			dig_host[UT.QUERIES_KEY] = Query_dict

			low_index = high_index+2


		dig_output.append(dig_host)

	
	with open(output_filename, 'w') as rpo:
		json.dump(dig_output, rpo)



	 

#run_dig(top_100,"bleh")


