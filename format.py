import pandas, sys

# Iterates through real estate listings, determines agents with three or more total listings,
# and summarizes listing information about each

def reformat_agent(gb_object):

	# Called on each part of the groupby object returned by pandas.DataFrame.groupby object
	# Clusters properties represented by single agent

	name = gb_object[0]
	dataframe = gb_object[1]
	a=pandas.DataFrame(dataframe.apply(func=process_row, axis=1))
	indx = [ 'ou/hc', 'inv/hc', 'ou/sp', 'inv/sp', 'ou/hospit', 'inv/hospit', 'ou/special', 'inv/special', 'ou/mixed', 'inv/mixed']
	a2 = pandas.Series(a.sum(axis=0))
	agent = {'name': str(name), 'company': pandas.unique(dataframe['company'])[0]}
	for num,thing in zip(list(a2),indx):
		agent[thing]=num
	print(agent)
	return agent


def process_row(row):

	# treats a property of each kind as a one-hot vector so summing them is easier
	
	pt = row['property_type']
	oui = row['ou_or_inv']
	if pt == "Health Care" and oui == "Owner/User":	
		return pandas.Series([1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	if pt == "Health Care" and oui == "Investment":
		return pandas.Series([0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
	if pt == "Sports & Entertainment" and oui == "Owner/User":
		return pandas.Series([0, 0, 1, 0, 0, 0, 0, 0, 0, 0])
	if pt == "Sports & Entertainment" and oui == "Investment":
		return pandas.Series([0, 0, 0, 1, 0, 0, 0, 0, 0, 0])
	if pt == "Hospitality" and oui == "Owner/User":
		return pandas.Series([0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
	if pt == "Hospitality" and oui == "Investment":
		return pandas.Series([0, 0, 0, 0, 0, 1, 0, 0, 0, 0])
	if pt == "Specialty" and oui == "Owner/User":
		return pandas.Series([0, 0, 0, 0, 0, 0, 1, 0, 0, 0])
	if pt == "Specialty" and oui == "Investment":
		return pandas.Series([0, 0, 0, 0, 0, 0, 0, 1, 0, 0])
	if pt == "Mixed" and oui == "Owner/User":
		return pandas.Series([0, 0, 0, 0, 0, 0, 0, 0, 1, 0])
	if pt == "Mixed" and oui == "Investment":
		return pandas.Series([0, 0, 0, 0, 0, 0, 0, 0, 0, 1])

def format_file(filename):
	try:
		df = pandas.read_csv(filename)
	except FileNotFoundError:
		print("Can't find file!")
		exit(1)
	agents = [name for name,df in list(df.groupby('listing_agent')) if df.shape[0] > 2]
	print(agents)	
	tree_or_more = df.loc[df['listing_agent'].apply(lambda x: str(x) in agents)]	
	tree_or_more.loc[tree_or_more['ou_or_inv'].apply(lambda x: str(x).lower() != "owner/user" and str(x).lower() != 
"investment"), 'ou_or_inv'] = "Owner/User"
	new_filename = 'new_{}'.format(filename)
	print(tree_or_more)

	print("saved in {}".format(new_filename))

	three_or_more.to_csv(new_filename)
	return three_or_more

def main(filename):	
	df = format_file(filename)
	items = [reformat_agent(agent) for agent in list(df.groupby('listing_agent'))]
	pandas.DataFrame(items).to_csv("data/{}".format(filename))
	print('done')

if __name__ == "__main__":
	try:
		filename = sys.argv[1]
	except:
		print("Enter valid filename!")
		exit(1)

	main(filename)	

