import sys
import json
import math
import time

if len(sys.argv) > 1:
	tulokset = sys.argv[1].split(",")
else:
	tulokset = []
uusi_lelo = 1500
K = 20
#30 paivaa sekunteina
passiivisuusaika = 30 * 24 * 60 * 60

with open("lelolista.json") as json_file:
	lelolista = json.load(json_file)
	for n in range(len(tulokset)):
		uusi_pelaaja = True
		for pelaaja in lelolista["pelaajat"]:
			if pelaaja["nimi"] == tulokset[n].split("-")[0]:
				pelaaja["tulos"] = len(tulokset)-n-1
				uusi_pelaaja = False
		if uusi_pelaaja and len(tulokset[n].split("-"))==2 and tulokset[n].split("-")[1] == "uusi":
			lisatty_pelaaja = {}
			lisatty_pelaaja["nimi"] = tulokset[n].split("-")[0]
			lisatty_pelaaja["lelo"] = uusi_lelo
			lisatty_pelaaja["muuttuva_lelo"] = uusi_lelo
			lisatty_pelaaja["aktiivisuus"] = 0 #lasketaan myohemmin
			lisatty_pelaaja["tulos"] = len(tulokset)-n-1
			lelolista["pelaajat"].append(lisatty_pelaaja)
		elif uusi_pelaaja:
			raise Exception("Kirjoitusvirhe nimessä tai joku on uusi pelaaja")
    	  
def probability(rating1, rating2):
	#returns the expected score
	return 1 - 1.0 / (1 + math.pow(10, (rating1 - rating2) / 400.0))

#returns rating gained (or lost) by player1	rounded to 2 decimals
#result is the score of player1 (1, 1/2 or 0)
def calculate(rating1, rating2, result):
	expected_score = probability(rating1, rating2)
	return round(K * (result - expected_score), 2)

#seconds since the unix epoch (1970)
timestamp = time.time()
timestamp = round(timestamp)

for pelaaja1 in lelolista["pelaajat"]:
	for pelaaja2 in lelolista["pelaajat"]:
		if int(pelaaja1["tulos"]) != -1 and int(pelaaja2["tulos"] != -1):
			if int(pelaaja1["tulos"]) == int(pelaaja2["tulos"]):
				continue
			if int(pelaaja1["tulos"]) > int(pelaaja2["tulos"]):
				print("suurempi")
				muutos = calculate(float(pelaaja1["lelo"]), float(pelaaja2["lelo"]), 1)
				print(muutos)
				pelaaja1["muuttuva_lelo"] = round(float(pelaaja1["muuttuva_lelo"]) + muutos, 2)
				pelaaja2["muuttuva_lelo"] = round(float(pelaaja2["muuttuva_lelo"]) - muutos, 2)
				
				pelaaja1["aktiivisuus"] = timestamp
				pelaaja2["aktiivisuus"] = timestamp
			print("\n")

for pelaaja in lelolista["pelaajat"]:
	pelaaja["lelo"] = pelaaja["muuttuva_lelo"]
	pelaaja["tulos"] = -1
	
#clears the file
open('lelolista.json', 'w').close()

#writes to the file
json_object = json.dumps(lelolista, indent=4)

with open("lelolista.json", "w") as f:
    f.write(json_object)
    
#clears the file
open('index.html', 'w').close()

strHTML = '<head><link rel="stylesheet" type="text/css" href="main.css"></head><div class="main-container"><div class="title-container"><div class="title"></div></div>'

aktiivilista = []
passiivilista = []

strHTML = strHTML + '<div>Aktiiviset</div>'
for pelaaja in lelolista["pelaajat"]:
	aikaa_kulunut = timestamp - int(pelaaja["aktiivisuus"])
	if aikaa_kulunut < passiivisuusaika:
		aktiivilista.append(pelaaja)
	else:
		passiivilista.append(pelaaja)

strHTML = strHTML + '<div class="aktiivilista">'
for pelaaja in aktiivilista:
	strHTML = strHTML + '<div>' + pelaaja["nimi"] + ': ' + str(pelaaja["lelo"]) + '</div>'
strHTML = strHTML + '</div>'

strHTML = strHTML + '<div class="passiivilista">'
strHTML = strHTML + '<div>Epäaktiiviset</div>'
for pelaaja in passiivilista:
	strHTML = strHTML + '<div>' + pelaaja["nimi"] + ': ' + str(pelaaja["lelo"]) + '</div>'
strHTML = strHTML + '</div>'
#closes the main container div
strHTML = strHTML + '</div>'

with open("index.html", "a") as f:
	f.write(strHTML)
