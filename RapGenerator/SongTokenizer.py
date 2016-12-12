import sys, os
import string
import nltk
import re

class SongTokenizer:
	def songTokenize(self, title, baseDir='TrainingData'):
		"""
		title: the name of the file that the song appears in
		baseDir: the directory that the file containing the song appears in

		Returns a tokenized version of the song in the directory
		'baseDir/title'

		This strips punctuation and turns all characters to lower case. It
		also ignores all verses in the song that don't begin with '[Verse <rapper name>]'
		It returns the song as a list of list, where each list represents a line
		in the song.
		"""
		f = open(baseDir + '/' + title, 'r')
		content = f.readlines()
		f.close()

		tokenized_song = []
		skip = True
		for line in content:
			if not line.startswith('[') and not skip and not line.strip() == "":
					sentence = nltk.word_tokenize(re.sub(r'([^\s\w]|_)+', '', line).lower())
					tokenized_song.append(sentence)

			if '[Verse' in line or '(Verse' in line:
				skip = False

			if line.strip() == "":
				skip = True

		return tokenized_song

	def lineTokenize(self, line):
		"""
		line: a string representing a line of rap.

		Returns a tokenized version of the line; see SongTokenizer.songTokenize

		lineTokenize("I'm not a businessman. I'm a business, man.") would return
		["im", "not", "a", "businessman", "im", "a", "business", "man"]
		"""
		return nltk.word_tokenize(re.sub(r'([^\s\w]|_)+', '', line).lower())
