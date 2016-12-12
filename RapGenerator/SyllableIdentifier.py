import nltk
class SyllableIdentifier:
    def __init__(self):
        self.dictionary = nltk.corpus.cmudict.dict()

    def numberOfSyllables(self, word):
        """
        word: a string of english characters

        Returns the number of syllables in word. Not guaranteed to work
        if word is not in the CMU pronouncing dictionary.

        Requires the CMU pronouncing dictionary.
        """
        word = word.lower()
        if word in self.dictionary:
            syllableArray = [len(list(y for y in x if y[-1].isdigit())) for x in self.dictionary[word]]
            return int(reduce(lambda x, y: x + y, syllableArray) / len(syllableArray))
        else:
            #heuristic to identify number of syllables in a word not in the cmu dictionary
            #Syllables = number of isolated vowel groups
            vowels = ('a', 'i', 'e', 'o', 'u', 'y')
            syllables = 0
            index = 0
            while index < len(word):
                if word[index] in vowels:
                    syllables += 1
                    index += 1
                    while index < len(word) and word[index] in vowels:
                        index += 1
                else:
                    index += 1
            return syllables

    def numberOfSyllablesInLine(self, line):
        """
        line: an array of strings made up of english characters

        Returns the sum of syllables for each string in line
        """
        syllables = 0
        for word in line:
            syllables += self.numberOfSyllables(word)
        return syllables

    def syllableDifference(self, line1, line2):
        """
        Returns self.numberOfSyllablesInLine(line1) - self.numberOfSyllablesInLine(line2)
        """
        return self.numberOfSyllablesInLine(line1) - self.numberOfSyllablesInLine(line2)

    def absoluteSyllableDifference(self, line1, line2):
        """
        Returns abs(self.syllableDifference(line1, line2))
        """
        return abs(self.syllableDifference(line1, line2))
