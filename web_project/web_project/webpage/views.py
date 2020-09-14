from django.shortcuts import render, redirect
import requests
import re
from isodate import parse_duration
from django.conf import settings
# Create your views here.
from django.http import HttpResponse
from django.template import  loader
from django.template import RequestContext
import json as simplejson
import pymongo
from pprint import pprint




def index(request):
  return render(request,'index.html')

def youtube_search(request):
  videos = []

  if request.method == 'POST':
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

    search_params = {
      'part': 'snippet',
      'q': request.POST['search'],
      'key': settings.YOUTUBE_DATA_API_KEY,
      'maxResults': 9,
      'type': 'video'
    }

    r = requests.get(search_url, params=search_params)

    results = r.json()['items']

    video_ids = []
    for result in results:
      video_ids.append(result['id']['videoId'])

    if request.POST['submit'] == 'lucky':
      return redirect(f'https://www.youtube.com/watch?v={video_ids[0]}')

    video_params = {
      'key': settings.YOUTUBE_DATA_API_KEY,
      'part': 'snippet,contentDetails',
      'id': ','.join(video_ids),
      'maxResults': 9
    }

    r = requests.get(video_url, params=video_params)

    results = r.json()['items']

    for result in results:
      video_data = {
        'title': result['snippet']['title'],
        'id': result['id'],
        'url': f'https://www.youtube.com/watch?v={result["id"]}',
        'duration': int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
        'thumbnail': result['snippet']['thumbnails']['high']['url']
      }

      videos.append(video_data)

  context = {
    'videos': videos
  }
  print(context)
  return render(request,'search/youtube_search.html',context)

def word_fliter(data, name, count):
  stopwords_list = open('stopwords.txt', 'r').read().split('\n')
  stopwords_list = list(set(stopwords_list))

  xAxisLabels = []
  yAxisValues = []
  for item in data:
    if item[count] == None:
      pass
    elif item[name] in stopwords_list:
      pass
    elif re.findall('[a-zA-Z0-9]{3,}', item[name]) != []:
      xAxisLabels.append(item[name])
      yAxisValues.append(float(item[count]))
  return xAxisLabels, yAxisValues

def tag_fliter(data, name, count):
  stopwords_list = open('stopwords.txt', 'r').read().split('\n')
  stopwords_list = list(set(stopwords_list))

  xAxisLabels = []
  yAxisValues = []
  for item in data:
    if item[count] == None:
      pass
    elif item[name] in stopwords_list:
      pass
    elif re.findall('^#[a-zA-Z0-9]{3,}', item[name]) != []:
      xAxisLabels.append(item[name])
      yAxisValues.append(float(item[count]))
  return xAxisLabels, yAxisValues

def category_fliter(data, category):
  xAxisLabels = ['tech', 'sports', 'TVshow', 'business', 'politics', 'entertainment']
  result = {'tech': 0, 'sports': 0, 'TVshow': 0, 'business': 0, 'politics': 0, 'entertainment': 0}

  yAxisValues = []
  for item in data:
    # print(item[category],result[item[category]])
    result[item[category]] = result[item[category]] + 1
  for i in xAxisLabels:
    yAxisValues.append(result[i])
  return xAxisLabels, yAxisValues

def sentiment_fliter(data, sentiment):
  xAxisLabels = ['postive', 'negative', 'neutral']
  result = {'postive': 0, 'negative': 0, 'neutral': 0}
  yAxisValues = []
  for item in data:
    # print(item[category],result[item[category]])
    result[item[sentiment]] = result[item[sentiment]] + 1
  for i in xAxisLabels:
    yAxisValues.append(result[i])
  return xAxisLabels, yAxisValues


# Fetching data for a country/metric
def fetch_and_draw_data(request):
  country = request.GET.get('country','Newyork')
  metric = request.GET.get('metric', 'Trending')
  print(country)


  client = pymongo.MongoClient("mongodb+srv://Melody:Password1@group6-wwzz1.mongodb.net/test?retryWrites=true&w=majority")
  db = client.Twitter
  record = db[country]
  print('Total Record for the collection: ' + str(record.count()))
  data = record.find()

  record = db[country]
  print('Total Record for the collection: ' + str(record.count()))
  data = record.find()
  graphTitle = "Trending Topics in %s" % (country)
  xAxisTitle = "Topics"
  yAxisTitle = "Value"
  xAxisLabels, yAxisValues = tag_fliter(data, "tag", "tag_count")

  data_list = {"country": "%s" % (country), "graphTitle": graphTitle, "xAxisLabels": xAxisLabels,
               "xAxisTitle": xAxisTitle, "yAxisTitle": yAxisTitle, "yAxisValues": yAxisValues}

  if metric == 'Trending':
    record = db[country]
    print('Total Record for the collection: ' + str(record.count()))
    data = record.find()
    graphTitle = "Trending Topics in %s" % (country)
    xAxisTitle = "Topics"
    yAxisTitle = "Value"
    xAxisLabels, yAxisValues = tag_fliter(data, "tag", "tag_count")

    data_list = {"country": "%s"%(country),"graphTitle": graphTitle, "xAxisLabels": xAxisLabels,
                "xAxisTitle": xAxisTitle, "yAxisTitle": yAxisTitle, "yAxisValues": yAxisValues}

  if metric == 'Bubble':
    record = db[country]
    print('Bubble Total Record for the collection: ' + str(record.count()))
    data = record.find()
    graphTitle = "Bubble Trending Topics in %s" % (country)

    name, value = tag_fliter(data, "tag", "tag_count")

    data_list = {"graphTitle": graphTitle,"location": "%s"%(country), "name": name,
                  "value": value}
    print(data_list)

  if metric == 'HotWords':
    collect_name = "%s"%(country) + "_realtime"
    record = db[collect_name]
    print('Total Record for the collection: ' + str(record.count()))
    print(collect_name)
    data = record.find()
    graphTitle = "HotWords in %s" % (country)
    xAxisTitle = "HotWords"
    yAxisTitle = "Value"
    xAxisLabels, yAxisValues = word_fliter(data, "content", "content_count")

    data_list = {"country": "%s" % (country), "graphTitle": graphTitle, "xAxisLabels": xAxisLabels,
                 "xAxisTitle": xAxisTitle, "yAxisTitle": yAxisTitle, "yAxisValues": yAxisValues}

  if metric == 'Topcontent':
    collect_name = "%s"%(country) + "_tophash"
    record = db[collect_name]
    print('Total Record for the collection: ' + str(record.count()))
    print(collect_name)
    data = record.find()
    graphTitle = "Tophashtag's top content in %s" % (country)
    xAxisTitle = "HotWords"
    yAxisTitle = "Value"
    xAxisLabels, yAxisValues = word_fliter(data, "content", "content_count")

    data_list = {"country": "%s" % (country), "graphTitle": graphTitle, "xAxisLabels": xAxisLabels,
                 "xAxisTitle": xAxisTitle, "yAxisTitle": yAxisTitle, "yAxisValues": yAxisValues}

  if metric == "Sentiment":
    collect_name = "sentiment"
    record = db[collect_name]
    print('Total Record for the collection: ' + str(record.count()))
    print(collect_name)
    data = record.find()
    graphTitle = "Sentiment %s" % (country)
    name, value = sentiment_fliter(data, "sentiment")
    print(name,value)
    data_list = {"graphTitle": graphTitle,"location": "%s"%(country), "name": name,
                  "value": value}
    print("ss",data_list["value"])

  if metric == "Category":
    collect_name = "sentiment"
    record = db[collect_name]
    print('Total Record for the collection: ' + str(record.count()))
    print(collect_name)
    data = record.find()
    graphTitle = "Category %s" % (country)
    name, value = category_fliter(data, "category")
    print(name,value)
    data_list = {"graphTitle": graphTitle,"location": "%s"%(country), "name": name,
                  "value": value}


  return HttpResponse(simplejson.dumps(data_list))





