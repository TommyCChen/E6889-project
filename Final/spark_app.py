from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext
from pyspark.mllib.clustering import LDA, LDAModel
from pyspark.mllib.linalg import Vectors
import nltk
from send_mongo import monsendmany
from nltk.corpus import stopwords
import pyspark.sql.functions as sf
import json
import pymongo


from pyspark.sql import Row,SQLContext
import sys
import requests
import time

english_stopwords = stopwords.words("english")
# create spark configuration

conf = SparkConf()
conf.setAppName("TwitterStreamApp")
# create spark instance with the above configuration
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
# creat the Streaming Context from the above spark context with window size 2 seconds
ssc = StreamingContext(sc, 60)
# setting a checkpoint to allow RDD recovery
ssc.checkpoint("checkpoint_TwitterApp")
# read data from port 9009
dataStream = ssc.socketTextStream("localhost",9009)


def countWords(newValues, lastSum):
    if lastSum is None:
        lastSum = 0
    return sum(newValues, lastSum)


def get_sql_context_instance(spark_context):
    if ('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(spark_context)
    return globals()['sqlContextSingletonInstance']



def process_rdd(rdd):
    sql_context = get_sql_context_instance(rdd.context)
    # convert the RDD to Row RDD
    row_rdd = rdd.map(lambda w: Row(tag=w[0], tag_count=w[1]))
    print(row_rdd.collect())
    # create a DF from the Row RDD
    hashtags_df = sql_context.createDataFrame(row_rdd)
    # Register the dataframe as table
    hashtags_df.registerTempTable("hashtags")
    # get the top 10 hashtags from the table using SQL and print them
    hashtag_counts_df = sql_context.sql("select tag, tag_count from hashtags order by tag_count desc limit 50")
    hashtag_counts_df.show()
    pd_hashtag_counts_df = hashtag_counts_df.toPandas()
    monsendmany(pd_hashtag_counts_df,"Newyork")


def empty_rdd():
    print("###The current RDD is empty. Wait for the next complete RDD ###")

def count_num(rdd):
    print(rdd.map(lambda x: x[0]).collect())
    return rdd.map(lambda x: x[0]).collect()

def filter_content(content):
    content_old = content
    content = content.split("%#%")[-1]
    sentences = nltk.sent_tokenize(content)  # 句子化，sent_tokenize的输入是一段文字，返回的是标准化的句子列表
    words = [word.lower() for sentence in sentences for word in nltk.word_tokenize(sentence)]  # 单词化
    words = [word for word in words if word not in english_stopwords]  # 去除停用词
    #words = [word for word in words if wordnet.synsets(word)]#去除非英文词，报错

    words = [word for word in words if word not in ['http','https']]
    words = [word for word in words if '//' not in word]
    words = [word for word in words if
             word not in ['/', '^', '-', '+', '<', '>', '{', '}', '*', '//', ',', '.', ':', ';', '?', '(', ')', '[',
                          ']', '&', '!', '*', '@', '|', '#', '$', '%', '"', "'", "''", '""', '`', '``']]  # 去除标点和空字符

    return words

def array_to_string(arr):
    out=''
    for ele in arr:
        out=out+' '+str(ele)
    return out

def procontent_rdd(rdd):
    # Get spark sql singleton context from the current context
    sql_context = get_sql_context_instance(rdd.context)
    # convert the RDD to Row RDD
    row_rdd = rdd.map(lambda w: Row(content=w[0], content_count=w[1]))
    print(row_rdd.collect())
    # create a DF from the Row RDD
    content_df = sql_context.createDataFrame(row_rdd)
    content_df = content_df.filter('content not in (" ","rt","\'","n\'t")')
    # Register the dataframe as table
    content_df.registerTempTable("content")
    # get the top 10 hashtags from the table using SQL and print them
    content_counts_df = sql_context.sql("select content, content_count from content order by content_count desc limit 50")
    content_counts_df.show()
    pd_content_counts_df = content_counts_df.toPandas()

    monsendmany(pd_content_counts_df,"Newyork_realtime")





# split each tweet into words
words = dataStream.flatMap(lambda line: line.split(" "))
# words.pprint()
# filter the words to get only hashtags, then map each hashtag to be a pair of (hashtag,1)

hashtags = words.filter(lambda w: '#' in w).map(lambda x: (x, 1))
hashtags.pprint()

# adding the count of each hashtag to its last count
tags_totals = hashtags.updateStateByKey(countWords)
tags_totals.pprint()
# do processing for each RDD generated in each interval
# process_rdd(time.time(),tags_totals)
# tags_totals.foreachRDD(process_rdd)
tags_totals.foreachRDD(lambda rdd: empty_rdd() if rdd.count() == 0 else process_rdd(rdd))

# Process with the content
content = dataStream.map(lambda line: filter_content(line))
content_str = content.map(lambda line: array_to_string(line))
words_content = content_str.flatMap(lambda line: line.split(" ")).map(lambda x: (x,1))
words_content_totals = words_content.updateStateByKey(countWords)
words_content_totals.foreachRDD(lambda rdd: empty_rdd() if rdd.count() == 0 else procontent_rdd(rdd))

# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()



