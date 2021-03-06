# Character-Level Language Modeling
# -*- coding: utf-8 -*-

import os
import re
import sys
import math
import random
import argparse

"""Get all files name under path

Args:
    path: folder path to retrieve files' name.
    ratio: propotion of training data. Default value is 1 (100%).
    shuffle: a boolean value. TRUE: shuffle list; False: order list.

Returns:
    filesName[:train]: a list of all files end with ".txt" for training set. For example:

    ["dir/a.txt", "dir/b.txt"].

    filesName[train:]: a list of all files end with ".txt" for held-out set. For example:

    ["dir/a.txt", "dir/b.txt"].
"""
def getFilesName( path, ratio = 1, shuffle = False ):
    print( "Retrieving files name from folder %s..." % ( path ) )
    filesName = []
    files = os.listdir( path )
    for file in files:
        name = '/'.join( [path, file] )
        filesName.append( name )
    if shuffle:
        random.shuffle( filesName )
    else:
        filesName.sort()
    total = len( filesName )
    train = int( total * ratio )
    return filesName[:train], filesName[train:]

"""Preprocess data

1. Remove blank lines from each file.
2. Replace newline characters with spaces.
3. Remove duplicate spaces.

Args:
    fileName: fileName indicating which file that need to be processed.
    encoding: the encoding of inputing file. Default value is "Latin-1".

Returns:
    content: a string containing processed content from file. For example:
    
    "A cat"
"""
def preprocess( fileName, encoding = "Latin-1" ):
    print( "Preprocessing file %s..." % ( fileName ) )
    content = ""
    with open( fileName, 'r', encoding = encoding ) as f:
        line = f.readline()
        while line:
            line = re.sub( "\s", " ", line )
            line = re.sub( "_", "", line )
            line = re.sub( "[^\w\s]", "", line )
            content += line
            line = f.readline()
        content = re.sub( "\s+", " ", content ).strip()
    return content

"""Preprocess data

4. Replace characters in training set that appear ≤ 5 times as “UNK”.

Note: The function will figure out all characters which are need to be replaced by "UNK"
      and they will be replaced when building n-gram character-level language model.

Args:
    content: string to be processed.

Returns:
    repc: a string of characters that need to be replaced with "UNK". For example:
    
    "[abc]"
"""
def unk( content ):
    d = {}
    for c in content:
        if c not in d:
            d[c] = 0
        d[c] += 1
    repc = []
    for ( k, v ) in d.items():
        if v <= 5:
            repc.append( k )
    repc = '[' + "".join( repc ) + ']'
    return repc

# Build Character-Level Language Model
"""Generate n-gram dictionary.

Generate n-gram dictionary based on fed string and n.

Note: replace characters in content with "?" which represents "UNK" in character-level.

Args:
    content: content used to calculate ngrams.
    n: n-gram.
    d: dictionary correspond to n-gram.

Returns:
    None.
"""
def ngrams( content, n, d ):
    length = len( content )
    for i in range( 0, length - n + 1 ):
        k = content[i:i + n]
        if k not in d:
            d[k] = 0
        d[k] += 1

"""Build language model

Preprocess files and across all files in the directory (counted together), report the 
unigram, bigram, and trigram character counts.

Args:
    content: a list contains content needed to be processed.

Returns:
    lm: a dictionary of language model when savePath equals empty string. Its structure is:
    
    {"unigram": {"c": unigram, "t": total unigram characters},
     "bigram" : {"c": bigram,  "t": total bigram  characters},
     "trigram": {"c": trigram, "t": total trigram characters}}.
"""
def LM( contents ):
    print( "Building language modeling..." )
    lm = {"unigram": {"c": {}, "t": 0},
          "bigram" : {"c": {}, "t": 0},
          "trigram": {"c": {}, "t": 0}}
    ngram = ["unigram", "bigram", "trigram"]
    
    # Calculate unigram, bigram, and trigram
    print( "Calculating n-grams..." )
    for content in contents:
        ngrams( content, 1, lm["unigram"]["c"] )
        ngrams( content, 2, lm["bigram" ]["c"] )
        ngrams( content, 3, lm["trigram"]["c"] )
    for name in ngram:
        lm[name]["t"] = sum( lm[name]["c"].values() )
    return lm

"""Main function of problem 3.1

Across all files in the directory (counted together), report the unigram, bigram, and trigram
character counts and save them in seperate files.

Args:
    trainDataPath: train data path.
    encoding: train data files' encoding
    savePath: path to save language model.
    ratio: the proportion of the real training set comparing to whole training set

Returns:
    None
"""
def buildLM( trainDataPath = "./train", encoding = "Latin-1", savePath = "./lm", ratio = 1 ):
    ngram = ["unigram", "bigram", "trigram"]
    trainFiles, heldOutFiles = getFilesName( trainDataPath )
    # preprocess data and find UNK
    print( "Counting for finding UNK.")
    content = ""
    contents = []
    for fileName in trainFiles:
        content += preprocess( fileName, encoding )
        contents.append( content )
    repc = unk( content )
    if len( repc ) > 2:
        for i in range( len( contents ) ):
            contents[i] = re.sub( repc, "?", contents[i] )
    lm = LM( contents )
    for name in ngram:
        with open( savePath + "/" + name, "w" ) as f:
            f.write( str( lm[name]["t"] ) + "\n" )
            for ( k, v ) in lm[name]["c"].items():
                f.write( k + " " + str( v ) + "\n" )

# Apply Linear Interplotation smoothing function on language model.
"""Linear Interplotation Smoothing

P(w_{n}|w_{n-2}w_{n-1}) = lambda3 * P(w_{n}|w_{n-2}w_{n-1}) +
                          lambda2 * P(w_{n}|w_{n-1}) +
                          lambda1 * P(w_{n})
    where lambda1 + lambda2 + lambda3 = 1.

Args:
    lm: a dictionary contains language model. Its structure is:
    
    {"unigram": {"c": unigram, "t": total unigram characters},
     "bigram" : {"c": bigram,  "t": total bigram  characters},
     "trigram": {"c": trigram, "t": total trigram characters}}.

    lambdas: a dictionary of lambda for interplotation or addLambda. Its structure is:
    
    {1: lambdaForUnigram, 2: lambdaForBigram, 3: lambdaForTrigram}.

    s: string wating for calculating unigram, bigram, and trigram.

Returns:
    p: a double number represents the final probability of P(w_{n}|w_{n-2}w_{n-1}).
"""
def interplotation( lm, lambdas, s ):
    s1 = s[2:]
    s2 = s[1:]
    s3 = s[0:]
    if s1 not in lm["unigram"]["c"]:
        p1 = lm["unigram"]["c"]["?"] / lm["unigram"]["t"]
    else:
        p1 = lm["unigram"]["c"][s1] / lm["unigram"]["t"]
    if s2 not in lm["bigram"]["c"] or s1 not in lm["unigram"]["c"]:
        p2 = 0
    else:
        p2 = lm["bigram" ]["c"][s2] / lm["unigram" ]["c"][s1]
    if s3 not in lm["trigram"]["c"] or s2 not in lm["bigram"]["c"]:
        p3 = 0
    else:
        p3 = lm["trigram"]["c"][s3] / lm["bigram"]["c"][s2]
    p = lambdas[1] * p1 + lambdas[2] * p2 + lambdas[3] * p3
    return p

"""Calculate perplexity

PP(W) = P(w_1w_2 ... w_n)^(-1/n)
      = 2^{-1 / n * sum_{i=1:n}(log2(LM(w_i|w_{i-2}w_{i-1})))}

Note: Since here is no <SOS> and <EOS> in language model, n would be the length of
      the content - 2.

Args:
    content: string content.
    lm: a dictionary contains language model. Its structure is:
    
    {"unigram": {"c": unigram, "t": total unigram characters},
     "bigram" : {"c": bigram,  "t": total bigram  characters},
     "trigram": {"c": trigram, "t": total trigram characters}}.

    **kwargs:
        func: smoothing function name on calculating P(w_i|w_{i-2}w_{i-1}), including
              func = "Interplotation" and func = "AddLambda".
        
        lambdas: a dictionary of lambda for interplotation or addLambda. Its structure is:
    
        {1: lambdaForUnigram, 2:lambdaForBigram, 3:lambdaForTrigram}
        
        When using addLambda function, only need to feed one specific lambda.
    
Returns:
    ppw: a double number represents the perplexity of the content.

Raise:
    KeyError: an error when trying to find smoothing function.
"""
def perplexity( content, lm, **kwargs ):
    length = len( content )
    log2p = 0
    if( length <= 2 ):
        raise Exception( "Too short content." )
    if "func" in kwargs:
        if kwargs["func"] == "Interplotation":
            for i in range( length - 1 ):
                p = interplotation( lm, kwargs["lambdas"], content[i:i + 3] )
                log2p += math.log2( p )
        elif kwargs["func"] == "AddLambda":
            for i in range( length - 1 ):
                p = addLambda( lm, kwargs["lambdas"], content[i:i + 3] )
                log2p += math.log2( p )
        else:
            raise Exception( "Cannot find the smoothing function." )
    else:
        raise Exception( "No smoothing function." )
    log2p *= -1 / ( length - 2 )
    ppw = 2 ** log2p
    return ppw

"""Grid search

Using grid search and held-out data set find the best lambdas for
linear interplotation smoothing.

Args:
    lambdas: a generator of lambdas which generate a dictionary of lambdas
             for unigram, bigram, trigram each time. For example:
    
    {1:0.1, 2:0.1, 3:0.8}
    
    lm: a dictionary of language model. Its structure is:
    
    {"unigram": {"c": unigram, "t": total unigram characters},
     "bigram" : {"c": bigram,  "t": total bigram  characters},
     "trigram": {"c": trigram, "t": total trigram characters}}.
    
    heldOutFiles: files name belongs to held-out data set.

Returns:
    lambdas: the best lambdas combination.
"""
def gridSearch( lambdas, lm, heldOutFiles ):
    print( "Applying grid search..." )
    minAvg = float( "inf" )
    for lambd in lambdas:
        avg = 0
        for name in heldOutFiles:
            content = preprocess( name )
            avg += perplexity( content, lm, func = "Interplotation", lambdas = lambd )
        if( avg < minAvg ):
            minAvg = avg
            bestLambda = lambd
    return bestLambda

"""Main function for Problem 3.2

Calculate the perplexity for each 
le in the test set using linear interpolation smoothing
method.

Note: Here I sperate the training data and held-out data by seperating number of files rather
      than seperating all content after concatenating all together and then dividing them.
      
      There are two reasons to divide data in this way
      1. It is hard and cumbersome to measure 80% of the content just on name list.
      2. If loading all content into memory at the same time, it is too time consuming and
         wastes time without obviously improvment on final language model.

Args:
    trainDataPath: train data path.
    encoding: train data files' encoding
    savePath: path to save language model. If it equals to empty string, the function returns
              language model.
    testDataPath: test data path.
    ratio: the proportion of the real training set comparing to whole training set.

Returns:
    None.
"""
def interplotationPPW( trainDataPath = "./train", encoding = "Latin-1", savePath = "./save",
                       testDataPath = "./test", ratio = 0.8 ):
    # Get new language model
    trainFiles, heldOutFiles = getFilesName( trainDataPath, ratio = ratio, shuffle = True )
    content = ""
    contents = []
    for fileName in trainFiles:
        content += preprocess( fileName, encoding )
        contents.append( content )
    repc = unk( content )
    if len( repc ) > 2:
        for i in range( len( contents ) ):
            contents[i] = re.sub( repc, "?", contents[i] )
    lm = LM( contents )

    # Choose lambdas by grid search and perplexity
    lambdas = ( {1: x / 10, 2: y / 10, 3: ( 10 - x - y ) / 10}
                   for x in range( 1, 10, 1 ) for y in range( 1, 10 - x, 1 ) )
    lambdas = gridSearch( lambdas, lm, heldOutFiles )

    # File-PPW pair dictionary
    dfp = {}
    filesName, _ = getFilesName( testDataPath )
    for fileName in filesName:
        content = preprocess( fileName )
        ppw = perplexity( content, lm, func = "Interplotation", lambdas = lambdas )
        dfp[fileName] = ppw
    fps = sorted( dfp.items(), key = lambda x: x[1], reverse = True )
    with open( savePath + "/" + "filesPerplexity-interplotation.txt", 'w' ) as f:
        for fp in fps:
            f.write( fp[0].split( '/' )[-1] + ", " + str( fp[1] ) + "\n" )

# Apply Add-Lambda smoothing function on language model.
"""Load language model

Load language model from folder "lm" and save them into dictionary "lm".

Args:
    loadPath: language model load path.
    encoding: language model files' encoding

Returns:
    lm: a dictionary of language model. Its structure is:
    
    {"unigram": {"c": unigram, "t": total unigram characters},
     "bigram" : {"c": bigram,  "t": total bigram  characters},
     "trigram": {"c": trigram, "t": total trigram characters}}.
"""
def loadLM( loadPath = "./lm", encoding = "utf-8" ):
    lm = {}
    ngram = ["unigram", "bigram", "trigram"]
    n = 0
    # load unigram, bigram, and trigram
    for name in ngram:
        n += 1
        with open( loadPath + "/" + name, "r", encoding = encoding ) as f:
            ngram = {}
            total = 0
            line = f.readline()
            while line:
                kv = line.split( ' ' )
                if len( kv ) > 1:
                    kv[0] = line[:n]
                    kv[1] = line[n + 1:]
                    ngram[kv[0]] = int( kv[1] )
                else:
                    total = int( kv[0] )
                line = f.readline()
            lm[name] = {"c": ngram, "t": total}
    return lm

"""Add lambda smoothing

P(w_{n}|w_{n-1}w_{n-2}) = ( c(w_{n-1}w_{n-2}, w_{n}) + lambda ) /
                            ( c(w_{n-1}w_{n-1}) + lambda * V )

Args:
    lm: a dictionary of language model. Its structure is:
    
    {"unigram": {"c": unigram, "t": total unigram characters},
     "bigram" : {"c": bigram,  "t": total bigram  characters},
     "trigram": {"c": trigram, "t": total trigram characters}}.
    
    lambdas: a generator of lambdas which generate a dictionary of lambdas
             for unigram, bigram, trigram each time. For example:
    
    {1:0.1, 2:0.1, 3:0.8}
    
    s: string wating for calculating unigram, bigram, and trigram.

Returns:
    p: a double number represents the final probability of P(w_{n}|w_{n-2}w_{n-1}).
"""
def addLambda( lm, lambdas, s ):
    if s not in lm["trigram"]["c"]:
        cnt1 = 0
    else:
        cnt1 = lm["trigram"]["c"][s]
    if s[:2] not in lm["bigram"]["c"]:
        cnt2 = 0
    else:
        cnt2 = lm["bigram"]["c"][s[:2]]
    p = ( cnt1 + lambdas[3] ) / ( cnt2 + len( lm["bigram"]["c"] ) * lambdas[3] )
    return p

"""Main function for problem 3.3

Calculate the perplexity for each 
le in the test set using linear interpolation smoothing
method.

Args:
    trainDataPath: train data path.
    encoding: train data files' encoding
    savePath: path to save language model. If it equals to empty string, the function returns
              language model.
    testDataPath: test data path.
    ratio: the proportion of the real training set comparing to whole training set.

Returns:
    None.
"""
def addLambdaPPW( lmPath = "./lm", encoding = "Latin-1", savePath = "./3_3",
                  testDataPath = "./test" ):
    # Get new language model
    lm = loadLM( lmPath, encoding )
    lambdas = {3: 0.1}
    # File-PPW pair dictionary
    dfp = {}
    filesName, _ = getFilesName( testDataPath )
    for fileName in filesName:
        content = preprocess( fileName )
        ppw = perplexity( content, lm, func = "AddLambda", lambdas = lambdas )
        dfp[fileName] = ppw
    fps = sorted( dfp.items(), key = lambda x: x[1], reverse = True )
    with open( savePath + "/" + "filesPerplexity-addLambda.txt", 'w' ) as f:
        for fp in fps:
            f.write( fp[0].split( '/' )[-1] + ", " + str( fp[1] ) + "\n" )

# Test
def test():
    # Build Character-Level Language Model
    print( "Building Character-Level Language Model..." )
    buildLM( trainDataPath = "./train", encoding = "Latin-1", savePath = "./lm",
             ratio = 1 )
    # Apply Linear Interplotation smoothing function on language model
    print( "Applying Linear Interplotation smoothing function on language model..." )
    interplotationPPW( trainDataPath = "./train", encoding = "Latin-1",
                       savePath = "./save", testDataPath = "./test", ratio = 0.8 )
    # Apply Add-Lambda smoothing function on language model
    print( "Applying Add-Lambda smoothing function on language model..." )
    addLambdaPPW( lmPath = "./lm", encoding = "Latin-1", savePath = "./save",
                  testDataPath = "./test" )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    groupsmoothing = parser.add_mutually_exclusive_group()
    groupsmoothing.add_argument( "-t", "--test", help = "Test on all funcitions", action="store_true" )
    groupsmoothing.add_argument( "-b", "--build", help = "Build a character-level n-gram language model", 
                                 action="store_true" )
    groupsmoothing.add_argument( "-i", "--interplotation",
                                 help = "Apply Linear Interplotation smoothing function on language model",
                                 action="store_true" )
    groupsmoothing.add_argument( "-a", "--addLambda",
                                 help = "Apply Add-Lambda smoothing function on language model",
                                 action="store_true" )
    parser.add_argument( "-e", "--encoding", type = str,
                         help = "Encoding of files", default = "Latin-1" )
    parser.add_argument( "-r", "--ratio", type = float,
                         help = "proportion of real train data files in train data path",
                         default = 1.0 )
    parser.add_argument( "--trainPath", type = str, help = "Path that train data stores",
                         default = "./train" )
    parser.add_argument( "--testPath",  type = str, help = "Path that test data stores",
                         default = "./test" )
    parser.add_argument( "--savePath",  type = str, help = "Path that function result will save at",
                         default = "./save" )
    parser.add_argument( "--lmPath",    type = str, help = "Path that language model stores",
                         default = "./lm" )
    args = parser.parse_args()

    if args.test:
        test()
    if args.build:
        buildLM( args.trainPath, args.encoding, args.savePath, args.ratio )
    if args.interplotation:
        interplotationPPW( args.trainPath, args.encoding, args.savePath, args.testPath, args.ratio )
    if args.addLambda:
        addLambdaPPW( args.lmPath, args.encoding, args.savePath, args.testPath )
