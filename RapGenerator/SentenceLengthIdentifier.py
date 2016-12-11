from ast import literal_eval

class SentenceLengthIdentifier:
    def __init__(self):
        self.sentenceLengthUnigrams = {}
        self.sentenceLengthBigrams = {}

    def readLengthsFromFile(self, f1="ModelData/lengthUnigrams.txt", f2="ModelData/lengthBigrams.txt"):
        f = open(f1, 'r')
        stringDict = f.read()
        self.sentenceLengthUnigrams = literal_eval(stringDict)
        f.close()

        f = open(f2, 'r')
        stringDict = f.read()
        self.sentenceLengthBigrams = literal_eval(stringDict)
        f.close()

    def writeLengthsToFile(self, f1="ModelData/lengthUnigrams.txt", f2="ModelData/lengthBigrams.txt"):
        f = open(f1, 'w')
        f.write(str(self.sentenceLengthUnigrams))
        f.close()

        f = open(f2, 'w')
        f.write(str(self.sentenceLengthBigrams))
        f.close()

    def agglutinateSentenceLengths(self, lineArray):
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
        numerator = 1
        if length in self.sentenceLengthUnigrams:
            numerator += self.sentenceLengthUnigrams[length]

        denominator = len(self.sentenceLengthUnigrams)
        for l in self.sentenceLengthUnigrams:
            denominator += self.sentenceLengthUnigrams[l]

        return float(numerator) / float(denominator)

    def PLengthBigram(self, length, prevLength):
        numerator = 1
        if prevLength in self.sentenceLengthBigrams:
            if length in self.sentenceLengthBigrams[prevLength]:
                numerator += self.sentenceLengthBigrams[prevLength][length]

        denominator = len(self.sentenceLengthUnigrams)
        if prevLength in self.sentenceLengthUnigrams:
            denominator += self.sentenceLengthUnigrams[prevLength]

        return float(numerator) / float(denominator)
