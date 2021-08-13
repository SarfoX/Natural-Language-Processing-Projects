import numpy as np
import gensim
from nltk.tokenize import word_tokenize, sent_tokenize
from gensim.test.utils import get_tmpfile
from os import listdir
from os.path import isfile, join


def compareTwoFiles(queryFileName, subFileName):
    
    file_docs = []
    with open (subFileName) as f:
        tokens = sent_tokenize(f.read())
        for line in tokens:
            file_docs.append(line)

    gen_docs = [[w.lower() for w in word_tokenize(text)] for text in file_docs]
    dictionary = gensim.corpora.Dictionary(gen_docs)

    corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]
    tf_idf = gensim.models.TfidfModel(corpus)

    # building the index
    index_temp = get_tmpfile("index")
    sims = gensim.similarities.Similarity(index_temp,tf_idf[corpus],num_features=len(dictionary))

    file2_docs = []
    with open (queryFileName) as f:
        tokens = sent_tokenize(f.read())
        for line in tokens:
            file2_docs.append(line)

    avg_sims = [] # array of averages

    # for line in query documents
    for line in file2_docs:
        
        query_doc = [w.lower() for w in word_tokenize(line)]    # tokenize words
        
        query_doc_bow = dictionary.doc2bow(query_doc)           # create bag of words
        
        query_doc_tf_idf = tf_idf[query_doc_bow]                # find similarity for each document
        
        sum_of_sims =(np.sum(sims[query_doc_tf_idf], dtype=np.float32))     # calculate sum of similarities for each query doc
        
        avg = sum_of_sims / len(file_docs)                      # calculate average of similarity for each query doc

        avg_sims.append(avg)                                    # add average values into array

    total_avg = np.sum(avg_sims, dtype=np.float)                # calculate total average
    
    percentage_of_similarity = round(float(total_avg) * 100)    # round the value and multiply by 100 to format it as percentage
    
    # if percentage is greater than 100
    # that means documents are almost same
    # if percentage_of_similarity >= 100:
    #     percentage_of_similarity = 100

    return percentage_of_similarity


def compareQueryToFiles(queryFileName, subFileNames, ext = "", removeFileExt = True):
    if removeFileExt:
        similarityDic = dict(zip([queryFileName.replace(ext,"")+"_AND_"+subFileNames[i].replace(ext,"") for i in range(len(subFileNames))], [compareTwoFiles(queryFileName, subFileName) for subFileName in subFileNames])) 
    else:
        similarityDic = dict(zip([queryFileName+"_AND_"+subFileNames[i] for i in range(len(subFileNames))], [compareTwoFiles(queryFileName, subFileName) for subFileName in subFileNames])) 
    
    return similarityDic


def compareFilesList(dirPathList, ext = "", removeFileExt = True):
    startDict = {}
    
    [startDict.update(compareQueryToFiles(dirPathList[i], dirPathList[i+1:], ext=ext, removeFileExt=removeFileExt)) for i in range(0, len(dirPathList)-1)]
    
    return startDict


def compareQueriesToFile(queryFileNames, subFileName, ext = "", removeFileExt = True):
    if removeFileExt:
        similarityDic = dict(zip([queryFileNames[i].replace(ext,"")+"_AND_"+subFileName.replace(ext,"") for i in range(len(queryFileNames))], [compareTwoFiles(queryFileName, subFileName) for queryFileName in queryFileNames]))
    else:
        similarityDic = dict(zip([queryFileNames[i]+"_AND_"+subFileName for i in range(len(queryFileNames))], [compareTwoFiles(queryFileName, subFileName) for queryFileName in queryFileNames]))
        
    return similarityDic


def listFilesInDir(dirPath, ext=""):
    #Specify the directory with double back-slash
    if ext == "":
        fileList = [f for f in listdir(dirPath) if isfile(join(dirPath, f))]
    else:
        fileList = [f for f in listdir(dirPath) if f.endswith(ext)]
        
    return fileList


def listFilesInDir_Full(dirPath, ext=""):
    #Specify the directory with double back-slash
    if ext == "":
        fileList = [dirPath+"\\"+f for f in listdir(dirPath) if isfile(join(dirPath, f))]
    else:
        fileList = [dirPath+"\\"+f for f in listdir(dirPath) if f.endswith(ext)]
    
    return fileList 


def compareFilesInDir(dirPath, ext="", removeFileExt = True):
    
    dirPathList = listFilesInDir_Full(dirPath, ext=ext)
    
    return compareFilesList(dirPathList, ext=ext, removeFileExt=removeFileExt)


def getCopiedFiles(dirPath, copyPercent=100, ext = "", removeFileExt = True):
    
    similarities = compareFilesInDir(dirPath, ext=ext, removeFileExt=removeFileExt)
        
    return [fileKey.replace(dirPath+"\\", "") for fileKey in similarities.keys() if similarities[fileKey] >= copyPercent]


def getGenuineFiles(dirPath, copyPercent=100, ext = "", removeFileExt = True):
    
    similarities = compareFilesInDir(dirPath, ext=ext, removeFileExt=removeFileExt)
        
    return [fileKey.replace(dirPath+"\\", "") for fileKey in similarities.keys() if similarities[fileKey] < copyPercent]

out = getCopiedFiles("C:\\Users\\LENOVO\\Desktop\\Python Programming CE 257\\Assignment (Intro to Python)\\Assignment One", copyPercent=100, ext=".py")
print(out)