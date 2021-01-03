from riotwatcher import LolWatcher, ApiError
import time
import datetime
import csv
import os

try:
	keyfile = open("key.txt", "r")
	key = keyfile.read()
	print("Key loaded !")
except : 
	print("File 'key.txt' containing API key missing.")
	exit()

try:
	usernames = []
	userfile = open("usernames.txt","r")
	for user in userfile : 
		usernames.append(user)
except:
	print("File 'usernames.txt' containing One username per line is missing.")
	exit()
print("Usernames loaded !")

if not os.path.exists('output'):
	os.makedirs('output')
	print("output folder was missing so it was created.")



print("\n")
print("WARNING : THE API KEY CURRENTLY USED IS TEMPORARY AND CANNOT EXCESS 100 REQUESTS EVERY 2 MINUTES.")
print("WE CANNOT RETRIEVE MORE THAN 100 MATCHES EVERY TWO MINUTES.")
print("FOR THE MOMENT, WITH THIS API KEY, ONE USER AT THE TIME IS SUPPORTED. THE PROGRAM WILL WAIT TWO MINUTES BEFORE ANALYZING THE NEXT USER")
print("\n")
lol_watcher = LolWatcher(key)
my_region = 'na1'

for name in usernames :

	now = int(datetime.datetime.now().timestamp())
	csv_file = open(f'output/{name}_{now}.csv',mode='w', encoding='utf-8', newline="")
	csv_writer = csv.writer(csv_file, delimiter=';')
	csv_writer.writerow(["Participants", "Game Duration", "Game Creation"])
	requests = 0
	try :
		summoner = lol_watcher.summoner.by_name(my_region, name)
		requests+=1
		print(f"Found summoner of name {summoner['name']} and level {summoner['summonerLevel']}.")
		
		
		
	except ApiError as err:
		if err.response.status_code == 429:
			print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
			print('this retry-after is handled by default by the RiotWatcher library')
			print('future requests wait until the retry-after time passes')
		elif err.response.status_code == 404:
			print('Summoner with this username not found')
		else:
			print("Unknown error. Skipping username.")
	
	matchlist = lol_watcher.match.matchlist_by_account(my_region, summoner['accountId'])
	requests+=1
	print(f"{matchlist['totalGames']} games found. Retrieving the 100 last games to avoid API request overflow.")
	
	#for game in matchlist['matches']:
	#	print(lol_watcher.match.by_id(my_region, game['gameId']))
	
	for match in matchlist['matches']:

		#match = matchlist['matches'][0]['gameId']
		#print(lol_watcher.match.by_id(my_region, match)['participants'][1])
		try : 
			match = lol_watcher.match.by_id(my_region, match['gameId'])
			requests+=1
			
			participants = match['participantIdentities']
			partListScraped= []
			for i in participants :
				partListScraped.append(i['player']['summonerName'])
			gameDuration = match['gameDuration']
			gameCreation = match['gameCreation']
			csv_writer.writerow([str(partListScraped), gameDuration, gameCreation])
			
			print(f"saved game {match['gameId']} successfully.")
		except ApiError as err:
			if err.response.status_code == 429:
				print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
				print('this retry-after is handled by default by the RiotWatcher library')
				print('future requests wait until the retry-after time passes')
			elif err.response.status_code == 404:
				print('Game not found')
			else:
				print("Unknown API error. Skipping game.")
		except:
			print("Something went wrong. The match could not be saved properly.")
	
	print(f"INFORMATION GATHERING FOR USER {name} DONE. {requests} operations done in {int(datetime.datetime.now().timestamp()) - now} seconds.")
	csv_file.close()
	
	if name != usernames[-1]:
		print("Sleeping two minutes before fetching another user.")
		print(f"Please wait...")
		time.sleep(125)
	else : 
		print("All the users have been fetched.")