from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import geckodriver_autoinstaller
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import time

#CONFIGURATION
config = {
    "FirefoxProfilePath" : "",
    "region" : "EU",
    "mumble" : 0,
    "gameType" : "6v6"
}
classes_to_play = ['roamer' , 'pocket']
maps_to_play = []

def load_selenium_geckodriver(firefox_profile_path):
	profile = webdriver.FirefoxProfile(firefox_profile_path)

	profile.set_preference("dom.webdriver.enabled", False)
	profile.set_preference('useAutomationExtension', False)
	profile.update_preferences()
	desired = DesiredCapabilities.FIREFOX

	driver = webdriver.Firefox(firefox_profile=profile, desired_capabilities=desired)
	return driver

blu_scout1 = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[1]/div[2]/div"
blu_scout2 = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[1]/div[3]/div"
blu_roamer = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[1]/div[4]/div"
blu_pocket = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[1]/div[5]/div"
blu_demo = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[1]/div[6]/div"
blu_med = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[1]/div[7]/div"

red_scout1 = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[3]/div[2]/div"
red_scout2 = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[3]/div[3]/div"
red_roamer = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[3]/div[4]/div"
red_pocket = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[3]/div[5]/div"
red_demo = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[3]/div[6]/div"
red_med = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/div/div/div[3]/div[7]/div"

def class_to_xpath(team, user_class):
	xpath = ""
	if (team == "blue"):
		if (user_class == "scout"):
			xpath = blu_scout1
		elif (user_class == "roamer"):
			xpath = blu_roamer
		elif (user_class == "pocket"):
			xpath = blu_pocket
		elif (user_class == "demo"):
			xpath = blu_demo
		elif (user_class == "med"):
			xpath = red_med
	else:
		if (user_class == "scout"):
			xpath = red_scout1
		elif (user_class == "roamer"):
			xpath = red_roamer
		elif (user_class == "pocket"):
			xpath = red_pocket
		elif (user_class == "demo"):
			xpath = red_demo
		elif (user_class == "med"):
			xpath = red_med
	return xpath

def load_lobby(lobbyid, team, tf2class, tf2map):
	driver.get('https://tf2center.com/lobbies/' + str(lobbyid))
	
	xpath = class_to_xpath(team, tf2class)

	driver.find_element_by_xpath(xpath).click()
	print ("Obtained spot on " + tf2map + " as " + team + " " + tf2class)

def search_lobbies(json, hours_played, lobbies_played):
	global lobbyid
	global team
	global tf2class
	global tf2map
	restricted = False
	playable_map = True

	for x in json:
		if (x["gameType"] == config["gameType"] and x["region"] == config["region"] and x["mumbleRequired"] == config["mumble"] and x["advanced"] == 0):
			if maps_to_play:
				playable_map = any(maptf2 in x["map"] for maptf2 in maps_to_play)

			if (playable_map == False):
				continue

			for c in x["slots"]:
				if (c["tf2Class"] in classes_to_play):
					for z in c["availableSlots"]:
						if (z["reserved"] == False):
							for n in z["restrictions"]:
								if (int(n["games"]) > lobbies_played or int(n["hours"]) > hours_played):
									restricted = True
						if (restricted == False):
							lobbyid = x["no"]
							team = z["team"]
							tf2class = c["tf2Class"]
							tf2map = x["map"]
							return

def get_data_between(data, start, end):
	result = ""
	start = current_src.partition(start)[-1]
	result = start.partition(end)[0]
	return result

driver = load_selenium_geckodriver(config["FirefoxProfilePath"])
driver.get("https://tf2center.com/lobbies/")

if "const mySteamId='';" in driver.page_source:
    input("Log in to steam to continue.")
else:
    print("Logged in.")

input("Enter to start searching...")

while(1):
	lobbyid = 0

	time.sleep(5)
	driver.refresh()
	current_src = driver.page_source

	if "replaceAllLobbies" in current_src:
		raw_json = get_data_between(current_src, "replaceAllLobbies(", ");</script>")
		lobbies_played = get_data_between(current_src, "const myLobbiesPlayed=", ";")
		hours_played = get_data_between(current_src, "const myTotalHoursPlayed=", ";")

		data = json.loads(raw_json)
	
		search_lobbies(data, hours_played, lobbies_played)

		if (lobbyid != 0):
			print("Lobby found.")
			load_lobby(lobbyid, team, tf2class, tf2map)
			input("Enter to requeue")
			driver.get("https://tf2center.com/lobbies/")