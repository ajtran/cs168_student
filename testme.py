# # testing....

# import subprocess

# host = "www.google.com"

# ping = subprocess.Popen(
#     ["ping", "-c", "10", host],
#     stdout = subprocess.PIPE,
#     stderr = subprocess.PIPE
# )

# out, error = ping.communicate()

# data = out.decode("utf-8") 
# parse = data.split('\n')

# print(data)


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

with open("alexa_top_100") as f:
  content = f.read()

print(content.split())