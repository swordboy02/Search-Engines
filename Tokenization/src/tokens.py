import sys
import gzip
import string

# Your function start here
vowels = ['a','e','i','o','u','y']
tokenfile, heapfile, statsfile = None, None, None
def mainTokenizer(inputFile, outputFilePrefix):
    mainCnt = 0
    uniqueCnt = 0
    allToks = []
    tokenFile = open(outputFilePrefix+"-tokens.txt","w")
    heapFile = open(outputFilePrefix+"-heaps.txt","w")
    statsFile = open(outputFilePrefix+"-stats.txt","w")
    with gzip.open(inputFile) as f:
        for lines in f:
            lines = lines.decode('utf-8')
            tokens = lines.split()
            for i in tokens:
                tokenFile.write(i+" ")
                arr = tokenizeString(i)
                for j in arr:
                    if j not in allToks:
                        uniqueCnt += 1
                    allToks.append(j)
                    mainCnt += 1
                    if mainCnt % 10 == 0:
                        heapFile.write(str(mainCnt)+" "+str(uniqueCnt)+"\n")
                    if(j == arr[-1]):
                        tokenFile.write(j)
                    else:
                        tokenFile.write(j+" ")
                tokenFile.write("\n")
    if mainCnt % 10 != 0:
        heapFile.write(str(mainCnt)+" "+str(uniqueCnt))
    statsFile.write(str(mainCnt)+"\n"+str(uniqueCnt)+"\n")
    #write code to print 100 most frequent tokens, if they are equal print in alphabetical order
    freqDict = {}
    for i in allToks:
        if i in freqDict:
            freqDict[i] += 1
        else:
            freqDict[i] = 1
    freqDict = dict(sorted(freqDict.items(), key=lambda item: (-item[1], item[0])))
    cnt = 0
    for i in freqDict:
        if cnt < 100:
            statsFile.write(i+" "+str(freqDict[i])+"\n")
            cnt += 1
        else:
            break
    tokenFile.close()
    heapFile.close()
    statsFile.close()
                

def tokenizeString(strg):
    tokens = strg.split()
    outputArr = []
    
    #Tokenize
    if tokenize_type == "fancy":
        for i in tokens:
            
            if isURL(i):
                if i[-1] == '.' or i[-1] == ')' or i[-1] == '(':
                    i = i[:-1]
                    
            if not isURL(i):
                i = i.lower()

            if i in string.punctuation:
                continue

            if isNumeric(i):
                if i[-1] in string.punctuation:
                    i = i[:-1]
                outputArr.append(i)
                continue
            
            if "'" in i or "’" in i:
                i = i.replace("'","")
                i = i.replace("’","")
                
            
            if "-" in i and (not(isURL(i)) or not(isNumeric(i))):
                tempArr = i.split('-')
                tempStr1 = ""
                tempStr2 = ""
                
                for j in tempArr:
                    tempStr1 = tempStr1+j
                    tempStr2 = tempStr2+j+" "
                    
                tempArr2 = tokenizeString(tempStr2)
                tempArr1 = tokenizeString(tempStr1)
                tempArr2.extend(tempArr1)
                outputArr.append(tempArr2)
                continue
            
            val = False
            for char in i:
                if char != "." and char != " " and char in string.punctuation and not(isURL(i)):
                    i = i.replace(char," ")
                    temp = tokenizeString(i)
                    outputArr.append(temp)
                    val = True
                    break
                continue
                
            if not(isURL(i)) and (isAlphaNumeric(i) or isAlpha(i)):
                if "." in i:
                    i = i.replace(".","")
            
            if not val:
                outputArr.append(i)

    elif tokenize_type == "spaces":
        for i in tokens:
            outputArr.append(i)

    
    
    #Stem
    newOutputArr = []
    if stemming_type == "porterStem":
        for token in outputArr:
            if isinstance(token, list):
                temp = ""
                for word in token:
                    temp = stemString(word)
                    newOutputArr.append(temp)
            else:
                token = stemString(token)
                newOutputArr.append(token)
    elif stemming_type == "noStem":
        for token in outputArr:
            if isinstance(token, list):
                newOutputArr.extend(token)
            else:
                newOutputArr.append(token)
            
    #Stop
    if stoplist_type == "yesStop":
        cnt = 0
        while cnt < len(newOutputArr):
            if newOutputArr[cnt] in stopword_lst:
                newOutputArr.remove(newOutputArr[cnt])
            else :
                cnt = cnt+1
    elif stoplist_type == "noStop":
        newOutputArr = newOutputArr
    
    cnt = 0
    while cnt < len(newOutputArr):
        if newOutputArr[cnt] == " " or newOutputArr[cnt] == "":
            newOutputArr.remove(newOutputArr[cnt])
        else:
            cnt = cnt+1
    
    return newOutputArr

    
def stemString(token):
    stepCheck = False
    if token.endswith("sses"):
        token = token[:-2]
    elif (token.endswith("ied") or token.endswith("ies")) and (len(token[:-3]) >= 1):
        token = token[:-2]
    elif (token.endswith("us") or token.endswith("ss")):
        token = token
    elif token.endswith("s") and hasVowel(token[:-2]):
        token = token[:-1]

    if token.endswith("eed"):
        stepCheck = True
        if hasVowel(token[:-3]):
            token = token[:-1]
    elif token.endswith("eedly"):
        stepCheck = True
        if hasVowel(token[:-5]) and len(token.split(token[-4])[0]) > 1:
            token = token[:-5]

    if stepCheck == False:
        endingsToCheck = ["ed", "edly", "ing", "ingly"]
        for ending in endingsToCheck:
            if token.endswith(ending) and hasVowel(token[:-len(ending)]):
                token = token[:-(len(ending))]
                if token.endswith("at") or token.endswith("bl") or token.endswith("iz"):
                    token = token+"e"
                elif token.endswith("bb") or token.endswith("dd") or token.endswith("ff") or token.endswith("gg") or token.endswith("mm") or token.endswith("nn") or token.endswith("pp") or token.endswith("rr") or token.endswith("tt"):
                    token = token[:-1]
                elif isShort(token):
                    token = token+"e"

    if token.endswith("y") and (token[-2] not in vowels) and (len(token)>1) and token not in stopword_lst:
        token = token[:-1]+'i'
    return token

def isShort(strg):
    if len(strg) == 2 and (strg[0] in vowels) and (strg[1] not in vowels):
        return True
    elif len(strg) > 2 and strg[-2] in vowels and strg[-1] not in vowels and strg[-1] not in ['w', 'x'] and not hasVowel(strg[:-2]):
        return True
    return False

def hasVowel(strg):
    for i in strg:
        if i in vowels:
            return True
    return False

def isURL(str):
    if str.startswith("https://") or str.startswith("http://"):
        return True
    return False

def isAlpha(str):
    for char in str:
        if char.isnumeric():
            return False
    return True

def isNumeric(str):
    for char in str:
        if char.isalpha():
            return False
    return True

def isAlphaNumeric(str):
    alph = 0
    num = 0
    for char in str:
        if char.isalpha():
            alph += 1
        if char.isnumeric():
            num += 1
    return ((alph > 0) and (num > 0))


if __name__ == '__main__':
    # Read arguments from command line; or use sane defaults for IDE.
    argv_len = len(sys.argv)
    inputFile = sys.argv[1] if argv_len >= 2 else "P1-train.gz"
    outputFilePrefix = sys.argv[2] if argv_len >= 3 else "outPrefix"
    tokenize_type = sys.argv[3] if argv_len >= 4 else "fancy"
    stoplist_type = sys.argv[4] if argv_len >= 5 else "noStop"
    stemming_type = sys.argv[5] if argv_len >= 6 else "noStem"
    stopword_lst = ["a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
                    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to",
                    "was", "were", "with"]
    mainTokenizer(inputFile, outputFilePrefix)
