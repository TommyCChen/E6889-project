import pymongo
import numpy as np
import re
#
# def word_fliter(data,name,count):
#     stopwords_list = open('stopwords.txt', 'r').read().split('\n')
#     stopwords_list = list(set(stopwords_list))
#
#     xAxisLabels = []
#     yAxisValues = []
#     for item in data:
#         if item[count] == None:
#             pass
#         elif item[name] in stopwords_list:
#             pass
#         elif re.findall('[a-zA-Z0-9]{3,}',item[name]) != []:
#             xAxisLabels.append(item[name])
#             yAxisValues.append(float(item[count]))
#     return xAxisLabels,yAxisValues


client = pymongo.MongoClient("mongodb+srv://Melody:Password1@group6-wwzz1.mongodb.net/test?retryWrites=true&w=majority")
db = client.Twitter
country = "sentiment"
record = db[country]
print('Total Record for the collection: ' + str(record.count()))
data = record.find()

def sentiment_fliter(data,category):
    xAxisLabels = ['tech', 'sports', 'TVshow', 'business', 'politics', 'entertainment']
    result = {'tech':0, 'sports':0, 'TVshow':0, 'business':0, 'politics':0, 'entertainment':0}


    yAxisValues = []
    for item in data:
        # print(item[category],result[item[category]])
        result[item[category]] = result[item[category]] + 1
    for i in xAxisLabels:
        yAxisValues.append(result[i])
    return xAxisLabels,yAxisValues
xAxisLabels,yAxisValues = sentiment_fliter(data,"category")
# print(xAxisLabels,yAxisValues)




# xAxisLabels = []
# yAxisValues = []
# xAxisLabels, yAxisValues = word_fliter(data,"content","content_count")
# print(xAxisLabels)




