#!/usr/bin/env python

import urllib2
import urllib
import json

#stock_quote = urllib2.urlopen('https://query.yahooapis.com/v1/public/yql?q=SELECT%20*%20FROM%20pm.finance%20WHERE%20symbol%3D%22HLIT%22&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys').read()

#print(quote_request)

baseurl = "https://query.yahooapis.com/v1/public/yql?"
yql_query = "select * from pm.finance where symbol='GOOG'"
#yql_query = "select wind from weather.forecast where woeid=2460286"
yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
print(yql_url)
result = urllib2.urlopen(yql_url).read()
data = json.loads(result)

print data['query']['results']