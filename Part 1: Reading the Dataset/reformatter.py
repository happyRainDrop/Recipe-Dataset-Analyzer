import json
import nltk
from nltk.tokenize import word_tokenize

def getTools(digrams):
  tools = []
  for k, v in digrams.items():
    for i in v:
      if i not in tools:
        tools.append(i)
  return tools 

def getBinaryPhrases(words):
  newWords = []
  for i in range(0, len(words)-1):
    s = words[i]+" "+words[i+1]
    newWords.append(s)
  return newWords

# digramsActionTool - a dictionary of existing action-tool digrams. An action-tool digram pairs verbs with tools
digramsActionTool = {'cut': ["knife", "food processor", "pizza cutter"], 'stir': ["spoon", "spatula", "whisk"], 'pour': ["cup", "bowl", "colander"], 'wrap': ["towel", "paper towel", "plastic wrap"], 'heat': ["stove", "oven", "microwave"], 'squeeze': ["blender", "lemonade squeezer", "gloves"], 'sprinkle': ["spoon", "spice grinder", "cheese grinder"], 'roll': ["rolling pin", "pin", "bottle"], 'fry': ["frying pan", "oven", "stove"], 'bake': ["microwave", "oven", "stove"], 'insert': ["toothpick", "tongs", "fork"], 'coat': ["coating pan", "cake pan", "pan"], 'roast': ["stove", "oven", "grill"]}
newDigramsActionTool = digramsActionTool

# Tools - a list of all objects that are tools
tools = getTools(digramsActionTool)

# Obects - a list of all objects that are not tools
objects = ['beef', 'tortilla', 'lemon', 'chicken', 'onion',
           'tomato', 'spice', 'mushroom', 'meat', 'garlic',
           'tomato sauce', 'sauce', 'pasta', 'bacon', 'sausage', 'fish',
           'cabbage', 'potato', 'butter', 'water', 'bread',
           'flour', 'nutmeg', 'parsley', 'dough', 'egg', 'black olive', 'olive',
           'gyoza filling', 'patty', 'jelly', 'fruit', 'strawberry', 'pineapple',
           'kiwi', 'orange', 'clams', 'cilantro', 'rice', 'celery',
           'carrots', 'beef stock', 'sour cream', 'vegetables', 'green onion', 'bread crumbs', 'crumbs', 'wine',
           'filling', 'stock', 'cream', 'oil', 'jelly roll',
           'lemon juice', 'lemon sauce', 'milk mixture', 'broth', 'beef broth', 'lemon glaze', 'red pepper']

with open("updatedTrigrams.json") as json_file: 
  trigramDict = json.load(json_file) 
trigrams = {}
for trigram in trigramDict:
  # get index of first two spaces
  space1 = trigram.find(" ")
  space2 = trigram[space1+1:].find(" ")+space1+1
  startSearch = 0
  # find the index where the verb ends
  if (trigram[0:space1] in tools): startSearch = space2+1
  elif (trigram[0:space1] in digramsActionTool): startSearch = space1+1
  else: startSearch = trigram[space2+1:].find(" ")+space2+2
  objs = trigram[startSearch:]
  currentIndex = 0
  while (currentIndex<len(objs)):
    w = ""
    w1 = ""
    firstSpace = len(objs)
    secondSpace = -1
    if (" " in objs[currentIndex: ]):
      firstSpace = objs[currentIndex: ].find(" ")+currentIndex
      if (objs[currentIndex:firstSpace] in objects): 
        w = objs[currentIndex:firstSpace]
      if (" " in objs[firstSpace+1:]): secondSpace = objs[firstSpace+1: ].find(" ")+firstSpace+1
      if (secondSpace>currentIndex and objs[currentIndex: secondSpace] in objects): 
        w1 = objs[currentIndex: secondSpace]
    else: w = objs[currentIndex:]
    initialKey = trigram[0: startSearch]
    key = initialKey+w
    key1 = initialKey+w1
    if (len(key1)>len(initialKey)):
      if (key1 not in trigrams):
        trigrams[key1] = trigramDict[trigram]
      else: trigrams[key1]+=trigramDict[trigram]
    elif (len(key)>len(initialKey)):
      if (key not in trigrams):
        trigrams[key] = trigramDict[trigram]
      else: trigrams[key]+=trigramDict[trigram]
    currentIndex = (firstSpace+1)

with open("correctedTrigrams.json", "w") as outfile: 
    json.dump(trigrams, outfile)
print("done!")
