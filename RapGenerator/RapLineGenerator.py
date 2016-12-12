from LanguageModel import LanguageModel
from LyricScrapper import LyricScrapper
from ParseTreeGenerator import ParseTreeGenerator
from Rhymer import Rhymer
from SentenceLengthIdentifier import SentenceLengthIdentifier
from SongTokenizer import SongTokenizer
from SyllableIdentifier import SyllableIdentifier
import os
from nltk import pos_tag, map_tag
import random

class RapLineGenerator:
    """
    This class incorporates a 4-gram language model and a grammar parser
    to generate rap lyrics.

    The most important method within this class is RapLineGenerator.generateVerse
    """
    def __init__(self):
        self.model = LanguageModel()
        self.scrapper = LyricScrapper()
        self.treeGenerator = ParseTreeGenerator()
        self.rhymer = Rhymer()
        self.lengthIdentifier = SentenceLengthIdentifier()
        self.tokenizer = SongTokenizer()
        self.syllableIdentifier = SyllableIdentifier()
        self.progressEnabled = True
        try:
            from progressbar import ProgressBar, Percentage, Bar
            self.pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=3).start()
        except ImportError:
            self.progressEnabled = False


    def generateVerse(self, seedLine='real gs move in silence like lasagna', numVerses=4):
        """
        seedLine: line to generate a verse from
        numLines: number of lines to generate

        This method generates a verse of rap using the seed line. It calls
        RapLineGenerator.pickBestLine to pick the next line given the previous.
        """
        finishedPhrase = []
        seedLine = self.tokenizer.lineTokenize(seedLine)
        print(' '.join(seedLine))
        previousLine = seedLine
        for i in range(numVerses):
            for dopeRhyme in range(4):
                nextLine = self.pickBestLine(previousLine)
                print(' '.join(nextLine))
                finishedPhrase.append(' '.join(nextLine))
                previousLine = nextLine
            if i != numVerses - 1:
                finishedPhrase.append("---")

        return finishedPhrase

    def pickBestLine(self, previousLine, numTrials=30):
        """
        previousLine: the previous line in the generated verse
        numTrials: number of different candidate lines to generate and rank

        This method generates numTrials different candidate lines using
        RapLineGenerator.generateCandidateLine. It then uses a domain-specific
        scoring metric to pick the highest-scored line out of the generated lines.

        The scoring metrics include:
            - The sum of probabilites of the words in the line normalized
                by the length of the line.
            - The individual probability of the length of the line.
            - The probability of the length of the line given the length
                previous line.
            - The absolute value of the difference of the number of syllables
                between the line and the previous line
            - Whether or not this line rhymes with the previous
            - How many words within the line the last word of the line rhymes with
            - The number of repeated words in the line
        """

        bestScore = 0
        bestLine = []
        for i in range(numTrials):
            generatedLine = self.generateCandidateLine(previousLine)
            score = 0
            score += 2.0 * self.lengthIdentifier.PLengthUnigram(len(generatedLine))
            score += 2.0 * self.lengthIdentifier.PLengthBigram(len(generatedLine), len(previousLine))
            absDiff = self.syllableIdentifier.absoluteSyllableDifference(generatedLine, previousLine)
            score += 1 / float(absDiff + 2)

            interRhymeRank = 0
            repeatedPairs = 0
            for i in range(len(generatedLine)):
                if self.rhymer.doesRhyme(generatedLine[i], generatedLine[-1]):
                    interRhymeRank += 1.3
                for j in range(i + 1, len(generatedLine)):
                    if generatedLine[i] == generatedLine[j]:
                        repeatedPairs += 1

            score += interRhymeRank / float(len(generatedLine))
            score -= repeatedPairs / float(len(generatedLine))

            additiveLineProb = 100 * self.model.additiveLineProb(generatedLine, previousLine)
            score += additiveLineProb

            if self.rhymer.doesRhyme(generatedLine[-1], previousLine[-1]):
                score *= 1.8

            if score > bestScore:
                bestScore = score
                bestLine = generatedLine

        return bestLine


    def generateCandidateLine(self, previousLine):
        """
        previousLine: the previous line in the generated verse

        This method generates a line of part of speech tags using
        ParseTreeGenerator.generateRandomGrammarLine.

        It then fills in each part of speech with a word using
        LanguageModel.returnCandidateWords.

        It iterates through the candidate words in order of decreasing probability
        and takes the current candidate word with 0.5 probability. It picks the last
        word with 1.0 probability if it reaches it.
        """
        if len(previousLine) < 3:
            raise RuntimeError("Seed lines must be at least 3 words long.")

        madlib = self.treeGenerator.generateRandomGrammarLine()
        line = []
        index = 0
        for tag in madlib:
            previousThreeWords = []
            if index < 3:
                previousThreeWords = previousLine[index - 3:] + line[:index]
            else:
                previousThreeWords = line[(index - 3):index]

            allCandidateWords = self.model.returnCandidateWords(previousThreeWords, previousLine[-1])

            def correctTag(word):
                sentence = previousThreeWords + [word]
                for i in range(len(sentence)):
                    if sentence[i] == 'i':
                        sentence[i] = 'I'

                pos_tags = pos_tag(sentence)

                wordTag = str(map_tag('en-ptb', 'universal', pos_tags[-1][1]))
                return (wordTag == tag)

            foundNoWords = True
            for word, prob in allCandidateWords:
                randomZeroOne = random.uniform(0,1)
                if randomZeroOne < 0.5 and correctTag(word):
                    line.append(word)
                    foundNoWords = False
                    break

            if foundNoWords:
                if allCandidateWords:
                    line.append(allCandidateWords[-1][0])
                else:
                    for word in self.model.unigrams:
                        if self.rhymer.doesRhyme(word, previousThreeWords[-1]):
                            line.append(word)
                            break

            index += 1
        return line

    def readAll(self):
        """
        This method reads in the pre-trained model that this library provides.
        This model includes a language model, a grammar model, and a line-length model
        trained on ~1000 of the most popular rap songs.
        """
        print("Reading data from files...")
        if self.progressEnabled:
            self.pbar.maxval = 3
        self.readParseTreeFromFile()

        if self.progressEnabled:
            self.pbar.update(1)
        self.readModelFromFile()

        if self.progressEnabled:
            self.pbar.update(2)
        self.readLengthsFromFile()

        if self.progressEnabled:
            self.pbar.finish()
        print('The system is ready to spit fire.')

    def __writeAll(self):
        print("Writing data to files...")
        if self.progressEnabled:
            self.pbar.maxval = 3
        self.writeParseTreeToFile()

        if self.progressEnabled:
            self.pbar.update(1)
        self.writeModelToFile()

        if self.progressEnabled:
            self.pbar.update(2)
        self.writeLengthsToFile()

        if self.progressEnabled:
            self.pbar.finish()
        print('\n')

    def __writeParseTreeToFile(self, filename="ModelData/grammarRules.txt"):
        self.treeGenerator.writeGrammarRulesToFile(filename)

    def readParseTreeFromFile(self, filename="ModelData/grammarRules.txt"):
        """
        This method reads a trained grammar model from a specific file. Unless
        you have trained a specific model on your own data, call RapLineGenerator.readAll
        to use the provided models.
        """
        self.treeGenerator.readGrammarRulesFromFile(filename)

    def __writeModelToFile(self, f1='ModelData/unigrams.txt', f2='ModelData/bigrams.txt', f3='ModelData/trigrams.txt', f4='ModelData/quadgrams.txt', f5='ModelData/linegrams.txt'):
        self.model.writeGramsToFile(f1, f2, f3, f4, f5)

    def readModelFromFile(self, f1='ModelData/unigrams.txt', f2='ModelData/bigrams.txt', f3='ModelData/trigrams.txt', f4='ModelData/quadgrams.txt', f5='ModelData/linegrams.txt'):
        """
        This method reads a trained language model from a specific file. Unless
        you have trained a specific model on your own data, call RapLineGenerator.readAll
        to use the provided models.
        """
        self.model.readGramsFromFile(f1, f2, f3, f4, f5)

    def __writeLengthsToFile(self, f1="ModelData/lengthUnigrams.txt", f2="ModelData/lengthBigrams.txt"):
        self.lengthIdentifier.writeLengthsToFile(f1, f2)

    def readLengthsFromFile(self, f1="ModelData/lengthUnigrams.txt", f2="ModelData/lengthBigrams.txt"):
        """
        This method reads a trained line-length from a specific file. Unless
        you have trained a specific model on your own data, call RapLineGenerator.readAll
        to use the provided models.
        """
        self.lengthIdentifier.readLengthsFromFile(f1, f2)

    def downloadSongs(self):
        """
        Download the top 10 songs from each artist in self.scrapper.artists. Unless
        you want to train the model on your own data, call RapLineGenerator.readAll
        to use the provided models.
        """
        print("Downloading song data...")
        self.scrapper.scrapArtists()

    def trainModel(self, baseDir="TrainingData"):
        """
        Trains the language model from the .txt files in the directory baseDir. Unless
        you want to train the model on your own data, call RapLineGenerator.readAll
        to use the provided models.
        """
        print("Training language model...")
        files = os.listdir(baseDir)
        if self.progressEnabled:
            self.pbar.maxval = self.scrapper.numSongs
        progress = 1
        for title in files:
            if title.endswith('.txt'):
                if self.progressEnabled:
                    self.pbar.update(progress)
                progress += 1
                self.model.fillGramCountsFromSong(self.tokenizer.songTokenize(title))
        if self.progressEnabled:
            self.pbar.finish()
        print('\n')

    def learnGrammars(self, baseDir="TrainingData"):
        """
        Trains the grammar model from the .txt files in the directory baseDir. Unless
        you want to train the model on your own data, call RapLineGenerator.readAll
        to use the provided models.
        """
        print("Learning grammar rules...")
        files = os.listdir(baseDir)
        if self.progressEnabled:
            self.pbar.maxval = self.scrapper.numSongs
        progress = 1
        for title in files:
            if title.endswith('.txt'):
                if self.progressEnabled:
                    self.pbar.update(progress)
                progress += 1
                self.treeGenerator.addToRulesFromSong(self.tokenizer.songTokenize(title))
        if self.progressEnabled:
            self.pbar.finish()
        print('\n')

    def agglutinateLengths(self, baseDir="TrainingData"):
        """
        Trains the line-length model from the .txt files in the directory baseDir. Unless
        you want to train the model on your own data, call RapLineGenerator.readAll
        to use the provided models.
        """
        print("Tracking line lengths...")
        files = os.listdir(baseDir)
        if self.progressEnabled:
            self.pbar.maxval = self.scrapper.numSongs
        progress = 1
        for title in files:
            if title.endswith('.txt'):
                if self.progressEnabled:
                    self.pbar.update(progress)
                progress += 1
                self.lengthIdentifier.agglutinateSentenceLengths(self.tokenizer.songTokenize(title))
        if self.progressEnabled:
            self.pbar.finish()
        print('\n')

    def __learnAndStoreModels(self):
        self.trainModel()
        self.learnGrammars()
        self.agglutinateLengths()
        self.writeAll()
