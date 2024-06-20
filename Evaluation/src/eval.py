# import package ...
import sys
import math

def eval(runfile, qrelsfile, outputFile):

    runfile = open(runFile, 'r').readlines()
    qrelsfile = open(qrelsFile, 'r').readlines()

    qrelDict = {}
    for line in qrelsfile:
        if line.split()[0] in qrelDict:
            qrelDict[line.split()[0]].append(line)
        else:
            qrelDict[line.split()[0]] = [line]

    runfileDict = {}
    for line in runfile:
        if line.split()[0] in runfileDict:
            runfileDict[line.split()[0]].append(line)
        else:
            runfileDict[line.split()[0]] = [line]

    for key in qrelDict.keys():
        if key in runfileDict:
            ndcg20 = ndcgAtnum(runfileDict[key], qrelDict[key], 20)
            numRel = numRelavent(qrelDict[key])
            relFound = relevantFound(runfileDict[key], qrelDict[key])
            rr = reciprocalRank(runfileDict[key], qrelDict[key])
            p10 = precisionAtnum(runfileDict[key], qrelDict[key], 10)
            r10 = recallAtnum(runfileDict[key], qrelDict[key], 10)
            f1_10 = f1At10(runfileDict[key], qrelDict[key])
            ap = avgPrecision(runfileDict[key], qrelDict[key])

            with open(outputFile, 'a') as f:
                f.write('NDCG@20  {:<8} {:6.4f}\n'.format(str(key), ndcg20))
                f.write('numRel   {:<8} {:d}\n'.format(str(key), numRel))
                f.write('relFound {:<8} {:d}\n'.format(str(key), relFound))
                f.write('RR       {:<8} {:6.4f}\n'.format(str(key), rr))
                f.write('P@10     {:<8} {:6.4f}\n'.format(str(key), p10))
                f.write('R@10     {:<8} {:6.4f}\n'.format(str(key), r10))
                f.write('F1@10    {:<8} {:6.4f}\n'.format(str(key), f1_10))
                f.write('AP       {:<8} {:6.4f}\n'.format(str(key), ap))

    with open(outputFile, 'a') as f:
        ndcg20, numRel, relFound, mrr, p10, r10, f1_10, map, cnt = 0, 0, 0, 0, 0, 0, 0, 0, 0
        for key in qrelDict.keys():
            if key in runfileDict:
                cnt += 1
                ndcg20 += ndcgAtnum(runfileDict[key], qrelDict[key], 20)
                numRel += numRelavent(qrelDict[key])
                relFound += relevantFound(runfileDict[key], qrelDict[key])
                mrr += reciprocalRank(runfileDict[key], qrelDict[key])
                p10 += precisionAtnum(runfileDict[key], qrelDict[key], 10)
                r10 += recallAtnum(runfileDict[key], qrelDict[key], 10)
                f1_10 += f1At10(runfileDict[key], qrelDict[key])
                map += avgPrecision(runfileDict[key], qrelDict[key])
        ndcg20 /= cnt
        mrr /= cnt
        p10 /= cnt
        r10 /= cnt
        f1_10 /= cnt
        map /= cnt
        f.write('numRel   {:<8} {:d}\n'.format('all', numRel))
        f.write('relFound {:<8} {:d}\n'.format('all', relFound))
        f.write('NDCG@20  {:<8} {:6.4f}\n'.format('all', ndcg20))
        f.write('MRR      {:<8} {:6.4f}\n'.format('all', mrr))
        f.write('P@10     {:<8} {:6.4f}\n'.format('all', p10))
        f.write('R@10     {:<8} {:6.4f}\n'.format('all', r10))
        f.write('F1@10    {:<8} {:6.4f}\n'.format('all', f1_10))
        f.write('MAP      {:<8} {:6.4f}\n'.format('all', map))
        
    f.close()


            
def numRelavent(queryList):
    cnt = 0
    for query in queryList:
        if int(query[-2]) > 0:
            cnt += 1
    return cnt

def relevantFound(runfileList, queryList):
    relevantQList = []
    cnt = 0

    for query in queryList:
        if int(query[-2]) > 0:
            relevantQList.append(query)
    
    docidList = []
    for query in relevantQList:
        docidList.append(query.split()[2])

    for i in runfileList:
        if i.split()[2] in docidList:
            cnt += 1

    return cnt

def ndcgAtnum(runfileList, queryList, num):
    relevantQList = []
    dcg = 0
    idcg = 0

    for query in queryList:
        if int(query[-2]) > 0:
            relevantQList.append(query)
    
    docidList = []
    for query in relevantQList:
        id = query.split()[2]
        rel = query.split()[3]
        docidList.append((id, rel))

    for i in runfileList[:num]:
        for tuple in docidList:
            if i.split()[2] == tuple[0]:
                pos = i.split()[3]
                if pos == "1":
                    dcg += int(tuple[1])
                else:
                    dcg += int(tuple[1]) / math.log2(int(pos))

    docidList.sort(key=lambda tuple: tuple[1], reverse=True)
    
    if num > len(docidList):
        num = len(docidList)

    for i in range(num):
        if i == 0:
            idcg += int(docidList[i][1])
        else:
            idcg += int(docidList[i][1]) / math.log2(i+1)
    
    if idcg == 0:
        return 0
    ndcg = dcg / idcg
    return ndcg

def reciprocalRank(runfileList, queryList):
    relevantQList = []

    for query in queryList:
        if int(query[-2]) > 0:
            relevantQList.append(query)

    
    docidList = []
    for query in relevantQList:
        docidList.append(query.split()[2])

    for i in runfileList :
        if i.split()[2] in docidList:
            return 1 / int(i.split()[3])
    return 0

def precisionAtnum(runfileList, queryList, num):
    relevantQList = []

    for query in queryList:
        if int(query[-2]) > 0:
            relevantQList.append(query)
    
    cnt = 0
    docidList = []
    for res in runfileList[:num]:
        docidList.append(res.split()[2])

    for query in relevantQList:
        if query.split()[2] in docidList:
            cnt += 1
    
    return cnt / num

def recallAtnum(runfileList, queryList, num):
    relevantQList = []
    for query in queryList:
        if int(query[-2]) > 0:
            relevantQList.append(query)

    if len(relevantQList) == 0:
        return 0
    
    cnt = 0
    docidList = []
    for i in runfileList[:num]:
        docidList.append(i.split()[2])

    for query in relevantQList:
        if query.split()[2] in docidList:
            cnt += 1

    return cnt / len(relevantQList)

def f1At10(runfileList, queryList):
    precision = precisionAtnum(runfileList, queryList, 10)
    recall = recallAtnum(runfileList, queryList, 10)
    if precision == 0 and recall == 0:
        return 0
    
    return 2 * (precision*recall) / (precision+recall)

def avgPrecision(runfileList, queryList):
    relevantQList = []
    for i in range(len(queryList)):
        if int(queryList[i][-2]) > 0:
            relevantQList.append((queryList[i], i+1))

    if len(relevantQList) == 0:
        return 0

    docidList = []
    for query, index in relevantQList:
        docidList.append((query.split()[2], index))

    sum = 0
    for i in runfileList:
        for tuple in docidList:
            if i.split()[2] == tuple[0]:
                sum += precisionAtnum(runfileList, queryList, int(i.split()[3]))
    
    return sum / len(relevantQList)

if __name__ == '__main__':
    argv_len = len(sys.argv)
    runFile = sys.argv[1] if argv_len >= 2 else "P2train/msmarcosmall-bm25.trecrun"
    qrelsFile = sys.argv[2] if argv_len >= 3 else "P2train/msmarco.qrels"
    outputFile = sys.argv[3] if argv_len >= 4 else "msmarcosmall-bm25.eval"

    eval(runFile, qrelsFile, outputFile)