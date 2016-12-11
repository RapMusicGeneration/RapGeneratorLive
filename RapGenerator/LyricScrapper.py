from urlparse import urljoin
from bs4 import BeautifulSoup
import requests
import random
import os

class LyricScrapper:
	def __init__(self):
		self.BASE_URL = "http://genius.com"
		self.artists = ["50 Cent", "2Pac", "A$AP Rocky", "Azealia Banks", "Atmosphere", "AZ", "Baby Bash", "Beastie Boys", "Big Daddy Kane",
					"Big L", "Big Punisher", "Big Sean", "Black Eyed Peas", "Bone Thugs", "Busta Rhymes", "Chief Keef", "Common",
					"Cypress Hill", "Drake", "DJ Khaled", "Dr Dre", "Eminem", "Flo Rida", "French Montana", "Future", "The Game",
					"Gucci Mane", "Gym Class Heroes", "Ice Cube", "Iggy Azalea", "Jay Z", "J Cole", "Kid Cudi", "Kendrick Lamar",
					"Lil Kim", "Lil Wayne", "Lil Dicky", "LMFAO", "LL Cool J", "Ludacris", "Macklemore", "Mac Miller", "Method Man",
					"Missy Elliot", "Nas", "The Notorious Big", "Odd Future", "Outkast", "Run DMC", "The Roots", "Snoop Dogg", "Soulja Boy",
					"Schoolboy Q", "Slick Rick", "Will Smith", "Nicki Minaj", "Timbaland", "A Trible Called Quest", "Tyga", "Wale",
					"Kanye West", "Wiz Khalifa", "Wu-Tang Clan", "21 Savage", "Fetty Wap", "Lil Yachty", "Ja Rule", "Rakim",
					"Talib Kweli", "Lupe Fiasco", "Mf Doom", "Andre 3000", "Jadakiss", "Nwa", "Too short", "G Eazy", "Eazy E",
					"Above the law", "E 40", "Nate Dogg", "Scarface", "Cypress Hill", "Quavo", "2 Chainz", "A ap rocky", "Trey songs",
					"Yelawolf", "Rich Homie Quan", "Jeezy", "Logic", "Fabolous", "Lil B", "Yo gotti", "Pro era", "Wyclef Jean",
					"Killa Kyleon", "Maino"]
		self.numSongs = len(self.artists * 10)
		self.progressEnabled = True
		try:
			from progressbar import ProgressBar, Percentage, Bar
		except ImportError:
			self.progressEnabled = False

	def scrapArtists(self, baseDir="TrainingData"):
		if not os.path.exists(baseDir):
			os.makedirs(baseDir)

		newArtists = []
		for artist in self.artists:
			artist_name = "-".join(artist.split())
			if not os.path.exists(baseDir + '/' + artist_name + '-0.txt'):
				newArtists.append(artist)

		if self.progressEnabled:
			pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=len(newArtists)).start()

		progress = 0
		for artist in newArtists:
			progress += 1

			if self.progressEnabled:
				pbar.update(progress)

			artist_name = "-".join(artist.split())

			artist_url = "http://genius.com/artists/" + artist_name

			response = requests.get(artist_url)
			soup = BeautifulSoup(response.text, "lxml")

			index = 0
			for song_link in soup.find_all(class_='mini_card'):
				link = urljoin(self.BASE_URL, song_link['href'])
				response = requests.get(link)
				soup = BeautifulSoup(response.text, "lxml")
				lyrics = soup.find("lyrics").get_text().strip().encode('utf8')

				f = open(baseDir+'/'+artist_name+'-'+str(index)+'.txt', 'w')
				f.write(lyrics)
				f.close()
				index += 1
				self.numSongs += 1
