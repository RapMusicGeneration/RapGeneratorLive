import sys, os
import string
import nltk
import re

class SongTokenizer:
	def songTokenize(self, title, baseDir='TrainingData'):
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
		return nltk.word_tokenize(re.sub(r'([^\s\w]|_)+', '', line).lower())
