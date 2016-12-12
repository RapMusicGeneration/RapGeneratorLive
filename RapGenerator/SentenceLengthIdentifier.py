from ast import literal_eval

class SentenceLengthIdentifier:
    def __init__(self):
        self.sentenceLengthUnigrams = {}
        self.sentenceLengthBigrams = {}

    def readLengthsFromFile(self, f1="ModelData/lengthUnigrams.txt", f2="ModelData/lengthBigrams.txt"):
        """
        f1: file containing length unigrams
		f2: file containing length bigrams

		Read stored length uni- and bigrams from the files. The unigrams, and bigrams
        must be a literal dictionary of the following respective forms:
        unigrams[length] = count
        bigrams[prevLength][length] = count
        """
        f = open(f1, 'r')
        stringDict = f.read()
        self.sentenceLengthUnigrams = literal_eval(stringDict)
        f.close()

        f = open(f2, 'r')
        stringDict = f.read()
        self.sentenceLengthBigrams = literal_eval(stringDict)
        f.close()

    def writeLengthsToFile(self, f1="ModelData/lengthUnigrams.txt", f2="ModelData/lengthBigrams.txt"):
        """
        Write unigrams and bigrams to files. See SentenceLengthIdentifier.readLengthsFromFile.
        """
        f = open(f1, 'w')
        f.write(str(self.sentenceLengthUnigrams))
        f.close()

        f = open(f2, 'w')
        f.write(str(self.sentenceLengthBigrams))
        f.close()

    def agglutinateSentenceLengths(self, lineArray):
        """
        lineArray: a list of lists representing a song, where each list is a line

        Count sentence length unigrams and bigrams from
        lineArray. Meant to be called in sequence on multiple songs.
        """
        prevSentenceLength = 0
        for line in lineArray:
            if prevSentenceLength in self.sentenceLengthBigrams:
                if len(line) in self.sentenceLengthBigrams[prevSentenceLength]:
                    self.sentenceLengthBigrams[prevSentenceLength][len(line)] += 1
                else:
                    self.sentenceLengthBigrams[prevSentenceLength][len(line)] = 1
            else:
                self.sentenceLengthBigrams[prevSentenceLength] = {}
                self.sentenceLengthBigrams[prevSentenceLength][len(line)] = 1

            if len(line) in self.sentenceLengthUnigrams:
                self.sentenceLengthUnigrams[len(line)] += 1
            else:
                self.sentenceLengthUnigrams[len(line)] = 1

            prevSentenceLength = len(line)

    def PLengthUnigram(self, length):
        """
        length: the length of a line

        Returns the probability that a line of length 'length' occurs.
        """
        numerator = 1
        if length in self.sentenceLengthUnigrams:
            numerator += self.sentenceLengthUnigrams[length]

        denominator = len(self.sentenceLengthUnigrams)
        for l in self.sentenceLengthUnigrams:
            denominator += self.sentenceLengthUnigrams[l]

        return float(numerator) / float(denominator)

    def PLengthBigram(self, length, prevLength):
        """
        length: the length of a line
        prevLength: the lenth of the previous line

        Returns the probability that a line of length 'length' occurs
        given that the previous line was of length 'prevLength'.
        """
        numerator = 1
        if prevLength in self.sentenceLengthBigrams:
            if length in self.sentenceLengthBigrams[prevLength]:
                numerator += self.sentenceLengthBigrams[prevLength][length]

        denominator = len(self.sentenceLengthUnigrams)
        if prevLength in self.sentenceLengthUnigrams:
            denominator += self.sentenceLengthUnigrams[prevLength]

        return float(numerator) / float(denominator)
