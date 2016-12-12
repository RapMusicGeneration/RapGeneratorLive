import nltk
from ast import literal_eval
import random

class ParseTreeGenerator:
    def __init__(self):
        self.grammarRules = {}
        self.terminalTagSet = ('ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM', 'PRT', 'PRON', 'VERB')
        self.maxRuleProd = 4
        self.smallestLineSize = 3
        self.canParse = False

    def generateRandomGrammarLine(self):
        """
        Returns an array of part of speech tags that represents the grammar structure
        of a valid line.

        The returned array is probabilistically generated from the grammar parse trees
        that appeared in the training set. To call this method, the grammarRules
        dictionary must not be empty. The grammarRules dictionary can be filled
        using ParseTreeGenerator.readGrammarRulesFromFile.
        """
        if not self.grammarRules:
            raise RuntimeError("grammarRules dictionary is empty")

        grammarLine = []
        while True:
            symbolStack = []
            symbolStack.append('L')

            while symbolStack:
                currentSymbol = symbolStack.pop()
                if currentSymbol in self.grammarRules:
                    symbolChildren = self.returnWeightedChoice(currentSymbol)
                    symbolChildren = symbolChildren.split()
                    symbolChildren.reverse()
                    symbolStack.extend(symbolChildren)
                else:
                    grammarLine.append(currentSymbol)

            if ('NOUN' in grammarLine) and ('VERB' in grammarLine) and len(grammarLine) >= self.smallestLineSize:
                return grammarLine
            grammarLine = []


    def returnWeightedChoice(self, nonTerminal):
        """
        nonTerminal: A non-terminal grammar symbol that appeared in the training data.
        Throws an error if nonTerminal has not appeared in the training data.

        Given that nonTerminal has a set of production rules, returns one of the production
        rules probabilistically.

        For example, given the production rules and associated frequencies:
        L -> NP VP      count: 5
        L -> PP NP VP   count: 2
        L -> Det NP     count: 3
                        total: 10

        Calling ParseTreeGenerator.returnWeightedChoice('L') would return:
            "NP VP"     with probability 5 / 10
            "PP NP VP"  with probability 2 / 10
            "Det NP"    with probability 3 / 10
        """
        if nonTerminal not in self.grammarRules:
            raise ValueError('Attempted to return a weighted choice for a symbol without production rules')
            return

        total = 0
        for key in self.grammarRules[nonTerminal]:

            total += self.grammarRules[nonTerminal][key]

        randomChoice = random.uniform(0, total)

        upto = 0
        for key in self.grammarRules[nonTerminal]:
            if upto + self.grammarRules[nonTerminal][key] >= randomChoice:
                return key
            upto += self.grammarRules[nonTerminal][key]

        assert False


    def readGrammarRulesFromFile(self, filename="ModelData/grammarRules.txt"):
        """
        filename: the name of a file containing a grammar rules dictionary

        Read a dictionary of grammar rules from filename. The grammar rules dictionary
        must be formatted as follows:

        grammarRules[start][children] = count

        Where:
        start:      is a string representing a non-terminal symbol
        children:   is a space-separated string of symbols that result from a
                    production rule of the form: start -> children
        count:      is an integer representing the number of times the rule
                    start -> children has been seen in the training data

        For example, given the production rules and associated frequencies:
        L -> NP VP      count: 5
        L -> PP NP VP   count: 2
        L -> Det NP     count: 3

        grammarRules = {
            'L': {
                'NP VP': 5,
                'PP NP VP': 2,
                'Det NP': 3
            }
        }
        """
        f = open(filename, 'r')
        stringDict = f.read()
        self.grammarRules = literal_eval(stringDict)
        f.close()

    def writeGrammarRulesToFile(self, filename="ModelData/grammarRules.txt"):
        """
        Write the current grammarRules dictionary to filename.
        """
        f = open(filename, 'w')
        f.write(str(self.grammarRules))
        f.close()

    def addToRulesFromSong(self, song):
        """
        song: a list of lists, where each list within the list represents a line
        in the song, and each line is a list of strings that represent words in the line.

        This method trains the grammarRules dictionary on the input song. It does
        not erase the grammarRules dictionary - rather, it adds to the currently
        existing one; this method is meant to be called multiple times in sequence
        on several songs.

        This requires the pyStatParser library.
        """
        if not self.canParse:
            raise ImportError("The pyStatParser library is unavailable. You cannot learn new grammar rules without this library.")

        for line in song:
            if line and line[0].strip() != "":
                try:
                    lineTree = self.parser.parse(' '.join(line))
                    self.getRulesFromTree(lineTree, True)
                except:
                    continue

    def getRulesFromTree(self, tree, isRoot = False):
        """
        tree: the head of an nltk.tree.Tree object, return from pyStatParser.Parser.parse

        isRoot: whether or not the current input is the root

        A helper function of ParseTreeGenerator.addToRulesFromSong. This function
        adds all of the gramarRules found in tree to self.grammarRules. It does
        so using a depth-first traversal of the parse tree.
        """
        if not isinstance(tree, nltk.tree.Tree):
            return
        numTreeChildren = 0
        for child in tree:
            if isinstance(child, nltk.tree.Tree):
                numTreeChildren += 1

        rootLabel = str(tree.label())
        if numTreeChildren == 0 or rootLabel in self.terminalTagSet:
            return

        if isRoot or rootLabel[0] == "S":
            parentLabel = "L"
        else:
            if "+" in rootLabel:
                rootLabel = rootLabel.split("+")[-1]
            parentLabel = rootLabel

        children = []
        skipRule = False
        if len(tree) > self.maxRuleProd:
            skipRule = True
        else:
            for child in tree:
                childLabel = str(child.label())
                if childLabel[0] == "S":
                    skipRule = True
                    break

                hasOnlyStrings = True
                for grandChild in child:
                    if isinstance(grandChild, nltk.tree.Tree):
                        hasOnlyStrings = False
                        break

                if hasOnlyStrings:
                    children.append(str(nltk.map_tag('en-ptb', 'universal', childLabel)))
                else:
                    if "+" in childLabel:
                        childLabel = childLabel.split("+")[-1]
                    children.append(childLabel)

        if not skipRule:
            childrenString = ' '.join(children)
            if parentLabel in self.grammarRules:
                if childrenString in self.grammarRules[parentLabel]:
                    self.grammarRules[parentLabel][childrenString] += 1
                else:
                    self.grammarRules[parentLabel][childrenString] = 1
            else:
                self.grammarRules[parentLabel] = {childrenString: 1}

        for child in tree:
            self.getRulesFromTree(child)
