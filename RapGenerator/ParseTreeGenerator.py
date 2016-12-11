import nltk
from ast import literal_eval
import random

class ParseTreeGenerator:
    def __init__(self):
        self.grammarRules = {}
        self.terminalTagSet = ('ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM', 'PRT', 'PRON', 'VERB')
        self.maxRuleProd = 4
        self.smallestLineSize = 3
        self.canParse = True

        try:
            from stat_parser import Parser
            self.parser = Parser()
        except ImportError:
            print 'pyStatParser is unavailable. The grammar training feature will be disabled.'
            self.canParse = False

    def generateRandomGrammarLine(self):
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
        f = open(filename, 'r')
        stringDict = f.read()
        self.grammarRules = literal_eval(stringDict)
        f.close()

    def writeGrammarRulesToFile(self, filename="ModelData/grammarRules.txt"):
        f = open(filename, 'w')
        f.write(str(self.grammarRules))
        f.close()

    def addToRulesFromSong(self, song):
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
