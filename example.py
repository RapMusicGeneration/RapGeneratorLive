import RapGenerator
rlg = RapGenerator.RapLineGenerator()
rlg.readAll() #Before generating lines, you need to set up the model. This method uses our built-in, pre-trained model.
seedLine = "I'm not a businessman, I'm a business, man." #You need to give the generator a seed line to rap off of.
numLinesToGenerate = 16 #Tell the model how many lines to generate.
rlg.generateVerse(seedLine, numLinesToGenerate)
