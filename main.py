from riotwatcher import LolWatcher, ApiError
import time
import datetime
import csv
import os
import json

try:
	keyfile = open("key.txt", "r")
	key = keyfile.read().rstrip()
	print(f"Key loaded !")
except : 
	print("File 'key.txt' containing API key missing.")
	exit()

try:
	usernames = []
	userfile = open("usernames.txt","r")
	for user in userfile : 
		usernames.append(user)
	print(f"{len(usernames)} Usernames loaded !")
except:
	print("File 'usernames.txt' containing One username per line is missing.")
	exit()


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


print("New pass : retrieving last 100 games for every user in the file. This could take a while.")
a = input("Press enter to confirm")

while True :
	print("NEW PASS")
	for name in usernames :

		now = int(datetime.datetime.now().timestamp())
		
		#exit()
		requests = 0
		try :
			summoner = lol_watcher.summoner.by_name(my_region, name)
			requests+=1
			print(f"Found summoner of name {summoner['name']} and level {summoner['summonerLevel']}.")
			
			OldFile = os.path.exists(f'output/{name}.csv')
			csv_file = open(f'output/{name}.csv',mode='a+', encoding='utf-8', newline="") #a+ = appending and reading
			csv_writer = csv.writer(csv_file, delimiter=';')
			csv_file.seek(0)
			csv_reader = csv.reader(csv_file, delimiter=";")
			if not OldFile :
				print("CSV file not found. Creating one for you.")
				csv_writer.writerow(["Game ID", "Participants", "Game Duration", "Game Creation"])
			else :
				print("A file for this user already exists. Appening to the file...")
			ReaderIDs = [row[0] for row in csv_reader]
			
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
		if not os.path.exists(f'output/{name}.json'):
			print("JSON file not found. Creating one for you.")
			with open(f'output/{name}.json', mode='w', encoding = 'utf-8') as json_file:
				json_file.write('[]')

		
		with open(f'output/{name}.json', mode = 'r+', encoding = 'utf-8') as json_file :
			wholeList = json.load(json_file)

				
		for match in matchlist['matches']:
			firstID = match['gameId']
			try : 
				if str(firstID) in ReaderIDs :
					pass
				else :
					match = lol_watcher.match.by_id(my_region, match['gameId'])
					requests+=1
					
					participants = match['participantIdentities']
					partListScraped= []
					for i in participants :
						partListScraped.append(i['player']['summonerName'])
					gameDuration = match['gameDuration']
					gameCreation = match['gameCreation']
					gameId = match['gameId']
					csv_writer.writerow([gameId, str(partListScraped), gameDuration, gameCreation])
					#saving everything in a json file.		
					wholeList.append(match)
					


					print(f"Found new game of id {match['gameId']} and saved it successfully.")
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
		with open(f'output/{name}.json', mode='w', encoding = 'utf-8') as json_file:
			json.dump(wholeList, json_file)
			print("Saved all informations to json file.")
		print(f"INFORMATION GATHERING FOR USER {name} DONE. {requests} operations done in {int(datetime.datetime.now().timestamp()) - now} seconds.")
		csv_file.close()
		
		if name != usernames[-1]:
			print("Sleeping two minutes before fetching another user.")
			print(f"Please wait...")
			time.sleep(125)
		else : 
			print("All the users have been fetched. This program will Run again in an hour.\n")
	time.sleep(3600)#sleeping one hour before starting again.







