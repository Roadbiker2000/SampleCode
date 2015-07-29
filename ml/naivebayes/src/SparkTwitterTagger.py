"""
Author: Matthew Hauser
JHED: mhauser5
Name: SparkTwitterTagger.py

Tag a Twitter Tweet based on its content

"""

from operator import add
from pyspark import SparkContext
from time import time
import sys, os
import math

def naiveBayes(trainfile, testfile, master="local[2]"):

    sc = SparkContext(master, "Triangle Count")
    start = time()
    ###############  END NO EDITS HERE  ################

    ############### START M. Hauser     ################

    # print '----------STARTING----------'

    def count(_data):
        if "#" not in _data:
            return []

        tokens = _data.strip().split()
        tags = []
        words = []
        if len(tokens) > 0:
            tags = [token.lower().encode('utf-8') for token in tokens if token[0] == "#" and len(token)>1]
            words = [token.lower().encode('utf-8') for token in tokens if token[0] != "#" and token[0] != "@" and len(token)>1]

        word_tags = [ ( (tag), 1) for tag in tags]

        word_tags.append( (("#TOTALWORDS"), len(words)) )
        word_tags.append( (("#TOTALTAGS"), len(tags)) )
        
        for tag in tags:
            for word in words: 
                word_tags.append( ((tag, word),1) )

        return word_tags

    def listTags(_data):
        if "#" not in _data:
            return []

        tokens = _data.strip().split()
        tags = []
        if len(tokens) > 0:
            tags = [token.lower().encode('utf-8') for token in tokens if token[0] == "#" and len(token) > 1]
        return tags        
    
    def evaluate(_data):

        weight = math.log( float(bc_tags.value[(_data)])/float(bc_tags.value[("#TOTALTAGS")]) )
        for token in bc_tweet.value:
            if (_data,token) in bc_tags.value:
                weight+=math.log(float(bc_tags.value[(_data,token)])/float(bc_tags.value[(_data)]))
            else:
                weight+=math.log(1.0/float(bc_tags.value["#TOTALWORDS"]))

        return [(_data,weight)]

    train = sc.textFile(trainfile).flatMap(count).reduceByKey(add).collectAsMap()
    tags = sc.textFile(trainfile).flatMap(listTags).distinct().collect()

    bc_tags = sc.broadcast(train)

    rdd = sc.parallelize(tags)

    total=1.0
    correct=0.0

    logfile = open("logfile", "w+")
    with open(testfile) as testfile:
        count = 0
        for tweet in testfile:
            print count
            count += 1

            if "#" in tweet and len(tweet) > 1:
                tokens = tweet.strip().split()

                tagsi = [token.lower().encode('utf-8') for token in tokens if token[0] == "#" and len(token)>2]
                words = [token.lower().encode('utf-8') for token in tokens if token[0] != "#" and token[0] != "@" and len(token)>1]

                bc_tweet = sc.broadcast(tokens)
                
                prediction = rdd.flatMap(evaluate).max(lambda x: x[1])
                

                if prediction[0] in tagsi:
                    correct+=1
                    logfile.write("RIGHT\t" + tweet + "  " + str(prediction)+"\t"+str(correct/total)+"\n")
                    print "RIGHT\t"+tweet+"\t" + str(prediction)+"\t"+str(correct/total)
                else:
                    logfile.write("WRONG\t"+tweet+"  " + str(prediction)+"\t"+str(correct/total)+"\n")
                    print "WRONG\t"+tweet+"\t" + str(prediction)+"\t"+str(correct/total)
                total+=1


    logfile.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "Usage:"
        print "python testingfile.py train test local[x]"
    else:
        naiveBayes(sys.argv[1], sys.argv[2], sys.argv[3])
