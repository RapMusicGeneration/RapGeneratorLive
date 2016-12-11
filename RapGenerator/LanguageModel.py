from ast import literal_eval
import operator
from Rhymer import Rhymer

class LanguageModel:
	def __init__(self):
		self.unigrams = {}
		self.bigrams = {}
		self.trigrams = {}
		self.quadgrams = {}
		self.linegrams = {}
		self.weightUni = 0
		self.weightBi = 2
		self.weightTri = 10
		self.weightQuad = 50
		self.weightLine = 2

	def readGramsFromFile(self, f1='ModelData/unigrams.txt', f2='ModelData/bigrams.txt', f3='ModelData/trigrams.txt', f4='ModelData/quadgrams.txt', f5='ModelData/linegrams.txt'):
		f = open(f1, 'r')
		uniString = f.read()
		self.unigrams = literal_eval(uniString)
		f.close()

		f = open(f2, 'r')
		biString = f.read()
		self.bigrams = literal_eval(biString)
		f.close()

		f = open(f3, 'r')
		triString = f.read()
		self.trigrams = literal_eval(triString)
		f.close()

		f = open(f4, 'r')
		quadString = f.read()
		self.quadgrams = literal_eval(quadString)
		f.close()

		f = open(f5, 'r')
		lineString = f.read()
		self.linegrams = literal_eval(lineString)
		f.close()

	def writeGramsToFile(self, f1='ModelData/unigrams.txt', f2='ModelData/bigrams.txt', f3='ModelData/trigrams.txt', f4='ModelData/quadgrams.txt', f5='ModelData/linegrams.txt'):
		f = open(f1, 'w')
		f.write(str(self.unigrams))
		f.close()

		f = open(f2, 'w')
		f.write(str(self.bigrams))
		f.close()

		f = open(f3, 'w')
		f.write(str(self.trigrams))
		f.close()

		f = open(f4, 'w')
		f.write(str(self.quadgrams))
		f.close()

		f = open(f5, 'w')
		f.write(str(self.linegrams))
		f.close()

	def ngrams(self, songArray, n):
		output = []
		for i in range(len(songArray)-n+1):
			output.append(songArray[i:i+n])
		return output

	def fillGramCountsFromSong(self, song):
		songArray = list(word for line in song for word in line)
		index = 0
		biArray = self.ngrams(songArray, 2)
		triArray = self.ngrams(songArray, 3)
		quadArray = self.ngrams(songArray, 4)
		r = Rhymer()

		previousLine = []
		for line in song:
			if len(previousLine) > 0 and len(line) > 0:
				previousWord = previousLine[-1]
				thisWord = line[-1]
				if previousWord in self.linegrams:
					if thisWord in self.linegrams[previousWord]:
						self.linegrams[previousWord][thisWord] += 1
					else:
						self.linegrams[previousWord][thisWord] = 1
				else:
					self.linegrams[previousWord] = {thisWord: 1}

				if r.doesRhyme(previousWord, thisWord):
					self.linegrams[previousWord][thisWord] += 5

			previousLine = line

		for unigram in songArray:
			if unigram in self.unigrams:
				self.unigrams[unigram] += 1
			else:
				self.unigrams[unigram] = 1

		for bigram in biArray:
			[first, second] = bigram
			if first in self.bigrams:
				if second in self.bigrams[first]:
					self.bigrams[first][second] += 1
				else:
					self.bigrams[first][second] = 1
			else:
				self.bigrams[first] = {second: 1}

			if r.doesRhyme(first, second):
				self.bigrams[first][second] += 1

		for trigram in triArray:
			[first, second, third] = trigram
			if first in self.trigrams:
				if second in self.trigrams[first]:
					if third in self.trigrams[first][second]:
						self.trigrams[first][second][third] += 1
					else:
						self.trigrams[first][second][third] = 1
				else:
					self.trigrams[first][second] = {third: 1}
			else:
				self.trigrams[first] = {second: {third: 1}}

		for quadgram in quadArray:
			[first, second, third, fourth] = quadgram
			if first in self.quadgrams:
				if second in self.quadgrams[first]:
					if third in self.quadgrams[first][second]:
						if fourth in self.quadgrams[first][second][third]:
							self.quadgrams[first][second][third][fourth] += 1
						else:
							self.quadgrams[first][second][third][fourth] = 1
					else:
						self.quadgrams[first][second][third] = {fourth: 1}
				else:
					self.quadgrams[first][second]  = {third: {fourth : 1}}
			else:
				self.quadgrams[first] = {second: {third: {fourth : 1}}}

			if r.doesRhyme(first, fourth):
				self.quadgrams[first][second][third][fourth] += 5

	def additiveLineProb(self, line, previousLine):
		if not self.unigrams:
			raise RuntimeError("Unigrams dictionary is empty")

		if not self.bigrams:
			raise RuntimeError("Bigrams dictionary is empty")

		if not self.trigrams:
			raise RuntimeError("Trigrams dictionary is empty")

		if not self.quadgrams:
			raise RuntimeError("Quadgrams dictionary is empty")

		if not self.linegrams:
			raise RuntimeError("Linegrams dictionary is empty")

		prob = 0
		i = 0
		lastPrevLine = previousLine[-1]
		while i < len(line):
			previousThreeWords = []
			if i < 3:
				previousThreeWords = previousLine[i - 3:] + line[:i]
			else:
				previousThreeWords = line[(i - 3):i]
			[first, second, third] = previousThreeWords
			unigram = line[i]

			vquad = len(self.quadgrams)
			vtri = len(self.trigrams)
			vbi = len(self.bigrams)
			vline = len(self.linegrams)

			quadProb = 1
			if first in self.quadgrams:
				if second in self.quadgrams[first]:
					if third in self.quadgrams[first][second]:
						if unigram in self.quadgrams[first][second][third]:
							quadProb += self.quadgrams[first][second][third][unigram]
			denom = float(vquad)
			if first in self.trigrams:
				if second in self.trigrams[first]:
					if third in self.trigrams[first][second]:
						denom += float(self.trigrams[first][second][third])
			quadProb /= float(denom)

			triProb = 1
			if second in self.trigrams:
				if third in self.trigrams[second]:
					if unigram in self.trigrams[second][third]:
						triProb += self.trigrams[second][third][unigram]
			denom = float(vtri)
			if second in self.bigrams:
				if third in self.bigrams[second]:
					denom += float(self.bigrams[second][third])
			triProb /= float(denom)

			biProb = 1
			if third in self.bigrams:
				if unigram in self.bigrams[third]:
					biProb += self.bigrams[third][unigram]
			denom = float(vbi)
			if third in self.unigrams:
				denom += float(self.unigrams[third])
			biProb /= float(denom)

			lineProb = 1
			denom = float(vline)
			if lastPrevLine in self.linegrams:
				if unigram in self.linegrams[lastPrevLine]:
					lineProb += self.linegrams[lastPrevLine][unigram]
					denom += sum(self.linegrams[lastPrevLine].values())
			lineProb /= float(denom)

			prob += self.weightQuad * quadProb + self.weightTri * triProb + self.weightBi * biProb + self.weightLine * lineProb
			i += 1
		return prob / float(len(line))


	def returnCandidateWords(self, previous, lastPrevLine):
		if not self.unigrams:
			raise RuntimeError("Unigrams dictionary is empty")

		if not self.bigrams:
			raise RuntimeError("Bigrams dictionary is empty")

		if not self.trigrams:
			raise RuntimeError("Trigrams dictionary is empty")

		if not self.quadgrams:
			raise RuntimeError("Quadgrams dictionary is empty")

		if not self.linegrams:
			raise RuntimeError("Linegrams dictionary is empty")

		#feed in previous 3 words as an array
		allProbs = {}
		[first, second, third] = previous
		#TODO: Add lambdas
		vquad = len(self.quadgrams)
		vtri = len(self.trigrams)
		vbi = len(self.bigrams)
		vuni = len(self.unigrams)
		vline = len(self.linegrams)
		totalUnigrams = sum(self.unigrams.values())

		wordsToTry = []
		if third in self.bigrams:
			wordsToTry = self.bigrams[third].keys()
		if lastPrevLine in self.linegrams:
			wordsToTry.extend(self.linegrams[lastPrevLine].keys())

		for unigram in wordsToTry:
			quadProb = 1
			if first in self.quadgrams:
				if second in self.quadgrams[first]:
					if third in self.quadgrams[first][second]:
						if unigram in self.quadgrams[first][second][third]:
							quadProb += self.quadgrams[first][second][third][unigram]
			denom = float(vquad)
			if first in self.trigrams:
				if second in self.trigrams[first]:
					if third in self.trigrams[first][second]:
						denom += float(self.trigrams[first][second][third])
			quadProb /= float(denom)

			triProb = 1
			if second in self.trigrams:
				if third in self.trigrams[second]:
					if unigram in self.trigrams[second][third]:
						triProb += self.trigrams[second][third][unigram]
			denom = float(vtri)
			if second in self.bigrams:
				if third in self.bigrams[second]:
					denom += float(self.bigrams[second][third])
			triProb /= float(denom)

			biProb = 1
			if third in self.bigrams:
				if unigram in self.bigrams[third]:
					biProb += self.bigrams[third][unigram]
			denom = float(vbi)
			if third in self.unigrams:
				denom += float(self.unigrams[third])
			biProb /= float(denom)

			lineProb = 1
			denom = float(vline)
			if lastPrevLine in self.linegrams:
				if unigram in self.linegrams[lastPrevLine]:
					lineProb += self.linegrams[lastPrevLine][unigram]
					denom += sum(self.linegrams[lastPrevLine].values())
			lineProb /= float(denom)

			uniProb = 1
			if unigram in self.unigrams:
				uniProb += self.unigrams[unigram]
			denom = float(vuni + totalUnigrams)

			allProbs[unigram] = self.weightQuad * quadProb + self.weightTri * triProb + self.weightBi * biProb + self.weightUni * uniProb + self.weightLine * lineProb

		return sorted(allProbs.iteritems(), key=operator.itemgetter(1), reverse=True)
