import nltk
import re

class Rhymer:
	def __init__(self):
		self.pronDict = nltk.corpus.cmudict.dict()
		self.vowelSet = ('a', 'i', 'e', 'o', 'u', 'A', 'I', 'E', 'O', 'U')
		self.mappingDictionary = {
			'a': 'AE',
			'e': 'EH',
			'i': 'IH',
			'o': 'OW',
			'u': 'AH',
			'A': 'AE',
			'E': 'EH',
			'I': 'IH',
			'O': 'OW',
			'U': 'AH'
		}

	def doesRhyme(self, word1, word2):
		if word1 == word2:
			return 0
		
		pron1 = []
		pron2 = []
		if word1 in self.pronDict:
			pron1 = self.pronDict[word1][0]
			pron1 = [filter(lambda x: re.sub("[^a-zA-Z]", '', x), str(lex)) for lex in pron1]
		else:
			i = 0
			while i < len(word1):
				if word1[i] in self.vowelSet:
					pron1.append(self.mappingDictionary[word1[i]])
					while i < len(word1) and word1[i] in self.vowelSet:
						i += 1
				else:
					j = i + 1
					while j < len(word1) and word1[j] not in self.vowelSet:
						j += 1
					pron1.append(word1[i:j].upper())
					i = j

		if word2 in self.pronDict:
			pron2 = self.pronDict[word2][0]
			pron2 = [filter(lambda x: re.sub("[^a-zA-Z]", '', x), str(lex)) for lex in pron2]
		else:
			i = 0
			while i < len(word2):
				if word2[i] in self.vowelSet:
					pron2.append(self.mappingDictionary[word2[i]])
					while i < len(word2) and word2[i] in self.vowelSet:
						i += 1
				else:
					j = i + 1
					while j < len(word2) and word2[j] not in self.vowelSet:
						j += 1
					pron2.append(word2[i:j].upper())
					i = j

		numMatchingVowelSyllables = 0
		if not pron1 or not pron2:
			return numMatchingVowelSyllables

		reverseIndex = -1
		while abs(reverseIndex) <= len(pron1) and abs(reverseIndex) <= len(pron2):
			if pron1[reverseIndex] != pron2[reverseIndex]:
				break
			numMatchingVowelSyllables += 1
			reverseIndex -= 1

		return numMatchingVowelSyllables
		#rhymes = pronouncing.rhymes(word1)
		#return word2 in rhymes
