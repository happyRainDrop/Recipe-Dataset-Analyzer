import json
import nltk
import math
import random
import re
from tqdm import tqdm
from nltk.tokenize import sent_tokenize, word_tokenize
from string import punctuation
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
nltk.download("wordnet")
nltk.download("punkt")
nltk.download("universal_tagset")
nltk.download("stopwords")


''' ********************** Start of helper functions ********************** '''

def getTools(digrams):
  tools = []
  for k, v in digrams.items():
    for i in v:
      if i not in tools:
        tools.append(i)
  return tools 

def makeListLowercase(l):
  li = []
  for w in l:
    li.append(w.lower())
  return li

def getBinaryPhrases(words):
  newWords = []
  for i in range(0, len(words)-1):
    s = words[i]+" "+words[i+1]
    newWords.append(s)
  return newWords

def getWordLem(word):
  newWords = ""
  wn1 = WordNetLemmatizer()
  newWords = wn1.lemmatize(word)
  return newWords

def getWordStem(word):
  newWords = []
  st = PorterStemmer()
  newWords = st.stem(word)
  return newWords

''' ********************** End of helper functions ********************** '''


# trigrams - a dictionary of existing trigrams. The key is a string representing the trigram. The number is the number of times this trigram has occured. I assume we want to keep track of how many times a trigram has occured so that the robot knows which trigrams are most common and therefore most likely to work.
trigrams = {"knife cut meat": 1, "spoon mix soup": 2}

# digramsActionTool - a dictionary of existing action-tool digrams. An action-tool digram pairs verbs with tools
digramsActionTool = {'cut': ["knife", "food processor", "pizza cutter"], 'stir': ["spoon", "spatula", "whisk"], 'pour': ["cup", "bowl", "colander"], 'wrap': ["towel", "paper towel", "plastic wrap"], 'heat': ["stove", "oven", "microwave"], 'squeeze': ["blender", "lemonade squeezer", "gloves"], 'sprinkle': ["spoon", "spice grinder", "cheese grinder"], 'roll': ["rolling pin", "pin", "bottle"], 'fry': ["frying pan", "oven", "stove"], 'bake': ["microwave", "oven", "stove"], 'insert': ["toothpick", "tongs", "fork"], 'coat': ["coating pan", "cake pan", "pan"], 'roast': ["stove", "oven", "grill"]}
newDigramsActionTool = []

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


#######################################################################################
#######################################################################################


def improveSemanticMemory():

  ''' ****************** Start of nested helper functions ****************** '''

  def tenthPlace(f):
    f = math.floor(10*f)
    return f%10

  def getNounIndicies(classListName):
    toolIndicies = []
    for t in classListName:
      if (" " not in t):
        for index in range(len(words)):
          w = words[index]
          if (w == t): 
            toolIndicies.append(index+0.0)
          elif (getWordLem(w)==t): 
            toolIndicies.append(index+0.1)
          elif (getWordStem(w)==t):
            toolIndicies.append(index+0.2)
      else:
        for index2 in range(len(binaryWords)):
          b = binaryWords[index2]
          if (b==t):
            toolIndicies.append(index2+0.3)
          elif (getWordLem(b)==t):
            toolIndicies.append(index2+0.4)
          elif (getWordStem(b)==t):
            toolIndicies.append(index2+0.5)
    return toolIndicies

  def getVerbIndicies():
    verbIndicies = []
    for d in digramsActionTool:
        for index in range(len(words)):
          if (words[index]==d):
            verbIndicies.append(index+0.0)
          elif (getWordLem(words[index])==d): # wordsLem
            verbIndicies.append(index+0.1) 
          elif (getWordStem(words[index])==d): # wordsStem
            verbIndicies.append(index+0.2)
    return verbIndicies

  def getToolFromIndex(i):
    w = words[math.floor(i)]
    b = binaryWords[math.floor(i)]
    if (tenthPlace(i)==0): return w
    elif (tenthPlace(i)==1): return getWordLem(w)
    elif (tenthPlace(i)==2): return getWordStem(w)
    elif (tenthPlace(i)==3): return b 
    elif (tenthPlace(i)==4): return getWordLem(b)
    else: getWordStem(b)
    
  def getVerbFromIndex(i):
    w = words[math.floor(i)]
    if (tenthPlace(i)==0): return w
    elif (tenthPlace(i)==1): return getWordLem(w)
    else: return getWordStem(w)

  def getObjectFromIndex(i):
    return getToolFromIndex(i)

  def getIndexOfClosestVerb(currentIndex):
    compareIndex = math.floor(toolIndex)
    if (tenthPlace(currentIndex)>=3): compareIndex+=0.5 # average of the indicies of each word in the binary phrase
    minDiff = 1000
    closestIndex = 0
    for verbIndex in verbIndicies:
      minDiff = min(minDiff, abs(compareIndex-math.floor(verbIndex)))
      if minDiff==abs(compareIndex-math.floor(verbIndex)): 
        closestIndex = verbIndex
    return closestIndex


  ''' ****************** End of nested helper functions ****************** '''


  d = None  
  data = None
  with open("layer1.json", "r") as f:
    d = json.load(f)
    for instruction in tqdm(d, 'Processing recipe1m+...'):
      for sent in instruction['instructions']:
          raw_sent = sent['text'].lower()
          words = nltk.word_tokenize(re.sub(r' \d+', '', raw_sent.strip()))  

          words = [w for w in words if w not in punctuation]
          sw = stopwords.words("english")

          words = [w for w in words if w not in sw] 
          words = makeListLowercase(words) # make everything lowercase
          binaryWords = getBinaryPhrases(words) # to look for binary words, like "pizza cutter"

          # FOR TESTING
          '''
          print("words: ", end = "")
          print(words)
          print("binaryWords: ", end = "")
          print(binaryWords)
          '''

        # Organize relevant words into trigrams 
          if (len(words)>=2): # sentence must contain at least a verb and a noun to be useful

          ##########################################################################
          # PART A: Find Indicies of relevant words
            verbIndicies = getVerbIndicies()
            toolIndicies = []
            objectIndicies = []
            if (len(verbIndicies)>0): 
              toolIndicies = getNounIndicies(tools)
              objectIndicies = getNounIndicies(objects)

            # Get rid of redundant verbs (for example, "slice" should not be stored as a verb if its only appearance is in the words "pepperoni slices")
            verbIndiciesToDelete = []
            for toolIndex in toolIndicies:
              if (tenthPlace(toolIndex)>=3): # binary
                binaryTool = getToolFromIndex(toolIndex)
                binaryToolSplit = word_tokenize(binaryTool)
                for i in range(len(verbIndicies)):
                  if (math.floor(verbIndicies[i])==math.floor(toolIndex) or math.floor(verbIndicies[i])==math.floor(toolIndex)+1) and i not in verbIndiciesToDelete: verbIndiciesToDelete.append(i)
            for objectIndex in objectIndicies:
              if (tenthPlace(objectIndex)>=3): # binary
                binaryObject = getObjectFromIndex(objectIndex)
                binaryObjectSplit = word_tokenize(binaryObject)
                for j in range(len(verbIndicies)):
                  if (math.floor(verbIndicies[j])==math.floor(objectIndex) or math.floor(verbIndicies[j])==math.floor(objectIndex)+1) and j not in verbIndiciesToDelete: verbIndiciesToDelete.append(j)
            for v in verbIndiciesToDelete: del verbIndicies[v]

            # FOR TESTING
            '''
            print("toolIndicies: ", end = "")
            print(toolIndicies)
            print("verbIndicies: ", end = "")
            print(verbIndicies)
            print("objectIndicies: ", end = "")
            print(objectIndicies)
            '''

          ##########################################################################
            # PART B: Matching tools, verbs, and objects. We assume that each tool and object should be paired with the verb it is closest to.

            tempTrigramString = []
            tempTrigram = []

            # match tool to verb
            for toolIndex in toolIndicies:
              verbIndex = getIndexOfClosestVerb(toolIndex)
              # add the tool and verb to tempTrigram
              tool = getToolFromIndex(toolIndex)
              verb = getVerbFromIndex(verbIndex)
              tempTrigramString.append(tool+" "+verb)
              tempTrigram.append([tool, verb])

            # match object to tool and verb
            for objectIndex in objectIndicies:
              verbIndex = getIndexOfClosestVerb(objectIndex)
              # use indexes to find object and verb strings
              Object = getObjectFromIndex(objectIndex)
              verb = getVerbFromIndex(verbIndex)
              # add the object to the appropriate tool-object phrase in tempTrigram
              for i in range(len(tempTrigramString)):
                if (verb in tempTrigramString[i]):
                  tempTrigram[i].append(Object)

            # transfer info from tempTrigram into trigams and digramsActionTool
              # FOR TESTING
              '''
              print(tempTrigram)
              print("*********************************************")
              '''
            for stringList in tempTrigram:
              if stringList[0] not in newDigramsActionTool[stringList[1]]:
                   newDigramsActionTool[stringList[1]].append(stringList[0])
              if (len(stringList)>=3):
                tri = ""
                for i in stringList:
                  tri = tri+i+" "
                if tri.strip() in trigrams:
                  trigrams[tri.strip()] = trigrams[tri.strip()]+1
                else:
                  trigrams[tri] = 1
                        
  # write it to a json file
  with open("updatedTrigrams.json", "w") as write_file:
    json.dump(trigrams, write_file)
    json.dump(newDigramsActionTool, write_file)
        
def findBestTool(givenVerb, givenObject):
  # see if an existing trigram containing the givenVerb and givenObject is in trigrams
  greatestValidTrigramFrequency = 0
  greatestValidTrigram = " "
  for t in trigram:
    if (givenVerb+" "+givenObject) in t: 
      greatestValidTrigramFrequency = max(greatestValidTrigramFrequency, trigram[t])
      greatestValidTrigram = t
  if (greatestValidTrigramFrequency>0):
    return greatestValidTrigram[0: greatestValidTrigram.find(" ")]
  else: return "N/A"



''' *****************************************************************
               ==== ||==  /== ==== ==== ||\  || ====\
                ||  ||==  ==\  ||   ||  || \ || || =|
                ||  ||==  ==/  ||  ==== ||  \|| \===|

***************************************************************** '''

print("Before: ")
print("\t trigrams: ", end = "")
print(trigrams)
print("\t digramsActionTool: ", end = "")
print(digramsActionTool)
print("")
improveSemanticMemory()
print("After: ")
print("\t trigrams: ", end = "")
print(trigrams)
print("\t digramsActionTool: ", end = "")
print(digramsActionTool)
