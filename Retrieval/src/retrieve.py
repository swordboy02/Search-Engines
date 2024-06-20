# import package ...
from collections import defaultdict
import sys
import gzip
import json
import math

def run_queries(index, queries_file, output_file):
    with open(output_file, 'w') as f:
        f.write('')

    def writeToFile(index, query, output_file):

        def ql(index, qText):
            docIDs = []
            smPr = 300

            totDocLength = sum(len(doc[1]) for doc in index.documents)

            for docID, text in index.documents:
                if all(term not in text for term in qText):
                    continue

                score = 0
                txtLen = len(text)
                for term in qText:
                    fqiD = index.getDocTermFrequency(term, docID)
                    cqi = len(index.index[term]) if term in index.index else 0
                    num = fqiD + (smPr * (cqi/totDocLength))
                    score += math.log(num/(txtLen + smPr)) if num != 0 else 0

                if(score != 0):
                    docIDs.append((docID, score))

            return docIDs
        
        def bm25(index, qText):
            docIDs = []
            k1 = 1.8
            k2 = 5
            b = 0.75

            docCount = index.getDocumentCount()
            for docID, text in index.documents:
                if not any(term in text for term in qText):
                    continue

                score = 0
                dl = len(index.index[docID])
                for term in qText:
                    ni = index.getTermCount(term)
                    ni = min(ni, docCount)
                    fi = index.getDocTermFrequency(term, docID) if term in index.index else 0
                    qfi = qText.count(term)
                    avgdl = len(index.index[term]) / docCount

                    K = k1 * (0.25 + b * (dl/avgdl))
                    idf = math.log((docCount - ni + 0.5) / (ni + 0.5))
                    tf = ((k1 + 1) * fi) / (K + fi)
                    qf = ((k2 + 1) * qfi) / (k2 + qfi)

                    score = idf * tf * qf
                
                if(score != 0):
                    docIDs.append((docID, score))

            return docIDs
        
        qList = query.split('\t')
        if len(qList) < 3:
            return

        qType = qList[0].lower()
        qName = qList[1]
        qText = qList[2:]

        docIDs = []
        for term in qText:
            docIDs.append(index.getDocIds(term))

        if qType == 'and':
            docIDs = [(docID, 1.000) for docID in set(docIDs[0]).intersection(*docIDs)]
            docIDs = sorted(docIDs)
        elif qType == 'or':
            docIDs = [(docID, 1.000) for docID in set(docIDs[0]).union(*docIDs)]
            docIDs = sorted(docIDs)
        else:
            if qType == 'ql':
                docIDs = ql(index, qText)
            if qType == 'bm25':
                docIDs = bm25(index, qText)

            docIDs = sorted(docIDs, key=lambda docID: (-docID[1], docID[0]))

        with open(output_file, 'a') as f:
            for i, docID in enumerate(docIDs):
                f.write('{:<11} skip {:<20} {:<2} {:.4f} ktalwar\n'.format(qName, docID[0], str(i+1), docID[1]))
        return
    
    with open(queries_file, 'r') as f:
        queries = f.read().split("\n")
        for query in queries:
            writeToFile(index, query, output_file)
    return

class InvIndex:
    def __init__(self, inputFile):
        self.documents = []
        self.index = defaultdict(list)
        self.inputFile = gzip.open(inputFile, 'r')

    def buildIndex(self):
        documentData = json.load(self.inputFile)

        for story in documentData['corpus']:
            storyId = story['storyID']
            textTerms = story['text'].split()

            self.documents.append((storyId, textTerms))
            for position, term in enumerate(textTerms):
                self.index[term].append((storyId, position))

        self.inputFile.close()

    # APIs
    def getDocIds(self, term):
        return [doc[0] for doc in self.index[term]]
    
    def getTermCount(self, term):
        return len(self.index[term]) if term in self.index else 0
    
    def getDocTermFrequency(self, term, docId):
        return sum(1 for doc in self.index[term] if doc[0] == docId)

    def getVocabulary(self):
        return self.index.keys()
    
    def getDocumentCount(self):
        return len(self.documents)

if __name__ == '__main__':
    # Read arguments from command line, or use sane defaults for IDE.
    argv_len = len(sys.argv)
    inputFile = sys.argv[1] if argv_len >= 2 else "sciam.json.gz"
    queriesFile = sys.argv[2] if argv_len >= 3 else "P3train.tsv"
    #outputFile = sys.argv[3] if argv_len >= 4 else "amherst-ktalwar.qrels"
    outputFile = sys.argv[3] if argv_len >= 4 else "P3train.trecrun"

    index = InvIndex(inputFile)
    index.buildIndex()
    run_queries(index, queriesFile, outputFile)