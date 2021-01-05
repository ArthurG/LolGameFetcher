# LolGameFetcher
A python script allowing the user to store the game history of Lol players, as well as the teammates, games duration and games creation date.

## How to use ? 
Simply download the python script

make sure to have the riotwatcher module installed : 
`pip install riotwatcher`

then create two files in the directory :
- One file named "key.txt", in which you will paste your riot games API Key
- One file named "usernames.txt", in which you will enter the usernames you want to fetch. Write every username on a new line.

The script will now parse all the information and store everything in a newly created "output" folder.
the file will have this form : 
`<pseudo>_<date>.csv`
It will also create a JSON file containing ALL the informations about the games if you want to parse it yourself later on. The file has the same format as the csv file. This file is very large and your text editor will probably crash if you try open it as it.

The program will run again every single hour.
## Important notice

The riot API keys are limited in the number of requests you can do by second and minute.
The basic, temporary API key is limited to:
- 20 requests every 1 seconds(s)
- 100 requests every 2 minutes(s)

For this reason, I volontarly slowed down the process (`time.sleep(125)` between two users) to avoid errors because of this limitation.
You can manually change this if you own a less limited API key.

I did my best to add error handling in case of API failure, so the program should wait by himself if the limit is reached, and/or skip the current operation if an Unknown API error is raised.
