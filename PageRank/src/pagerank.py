from numbers import Number
import sys
import gzip
from collections import Counter

def convergence(dist1, dist2):
    diffrence = 0
    for key in dist1.keys():
        diffrence += (dist1[key]-dist2[key]) ** 2
    return diffrence ** 0.5

def do_pagerank_to_convergence(input_file: str, lamb: float, tau: Number,
                               inlinks_file: str, pagerank_file: str, k: int):
    """Iterates the PageRank algorithm until convergence."""
    
    uniquePages = dict()
    allWords = []

    with gzip.open(input_file) as input_file:
        lines = input_file.readlines()
        for line in lines:
            line = line.decode()
            for word in line.rstrip().split(" "):
                res = word.split("\t")
                for wrd in res:
                    if wrd not in uniquePages.keys():
                        uniquePages[wrd] = 0
                allWords.append(res)

    rank = 1
    top = []
    for word in allWords:
        if len(word) == 2:
            top.append(word[1])
    top_terms = Counter(top).most_common(k)

    inlinkFile = open(inlinks_file, 'w')
    for words in top_terms:
        inlinkFile.write(f"{words[0]}")
        inlinkFile.write("\t" + '%d' % rank + "\t")
        inlinkFile.write(f"{words[1]}" + "\n")
        rank += 1
    inlinkFile.close()


    oldRank = dict()
    newRank = dict()
    numUniquePages = len(uniquePages)
    newLambda = (1 - lamb)
    allEqual = lamb / numUniquePages

    for key, value in uniquePages.items():
        uniquePages[key] = lamb / numUniquePages
        oldRank[key] = 1 / numUniquePages
        newRank[key] = allEqual

    outCount = dict()
    for t in allWords:
        if t[0] not in outCount.keys():
            outCount[t[0]] = 1
        else:
            outCount[t[0]] += 1

    noOutlinks = dict()
    for i in uniquePages.keys():
        if i not in outCount.keys():
            noOutlinks[i] = 0

    while True:
        for page, rank in newRank.items():
            newRank[page] = allEqual

        for wordTuple in allWords:
            if len(wordTuple) == 2:
                newRank[wordTuple[1]] += (newLambda * oldRank[wordTuple[0]] / outCount[wordTuple[0]])

        accumulation = 0
        for term in noOutlinks.keys():
            accumulation += (newLambda * oldRank[term])

        for pageKey in newRank.keys():
            newRank[pageKey] += accumulation / numUniquePages

        if convergence(oldRank, newRank) <= tau:
            break
        oldRank = newRank.copy()

    first100 = Counter(newRank).most_common(k)

    rankFile = open(pagerank_file, 'w')
    rank = 1
    for tup in first100:
        rankFile.write(f"{tup[0]}")
        rankFile.write("\t" + '%d' % rank + "\t")
        rankFile.write(f"{tup[1]:12f}" + "\n")
        rank += 1
    rankFile.close()

    return


def do_pagerank_n_times(input_file: str, N: int, inlinks_file: str,
                        pagerank_file: str, k: int):
    """Iterates the PageRank algorithm N times."""
    lamb = 0.2
    tau = 0.005
    cnt = 0

    while cnt < N:
        do_pagerank_to_convergence(input_file, lamb, tau, inlinks_file, pagerank_file, k)
        cnt += 1

    return


def main():
    argc = len(sys.argv)
    input_file = sys.argv[1] if argc > 1 else 'links.srt.gz'
    lamb = float(sys.argv[2]) if argc > 2 else 0.2
    
    tau = 0.005
    N = -1  # signals to run until convergence
    if argc > 3:
        arg = sys.argv[3]
        if arg.lower().startswith('exactly'):
            N = int(arg.split(' ')[1])
        else:
            tau = float(arg)
    
    inlinks_file = sys.argv[4] if argc > 4 else 'inlinks.txt'
    pagerank_file = sys.argv[5] if argc > 5 else 'pagerank.txt'
    k = int(sys.argv[6]) if argc > 6 else 100
    
    if N == -1:
        do_pagerank_to_convergence(input_file, lamb, tau, inlinks_file, pagerank_file, k)
    else:
        do_pagerank_n_times(input_file, N, inlinks_file, pagerank_file, k)
    
    # ...


if __name__ == '__main__':
    main()
