import base64
#Define your keys from the developer portal
client_key = "eqLHuY0uTBa0rCfnwUlfheGPc"
client_secret = "2BqhyDJwdg2K6DWzcSEX6OKDOExiS5zv2p1inA0lcNDvQT7GzL"
#Reformat the keys and encode them
key_secret = '{}:{}'.format(client_key, client_secret).encode('ascii')
print(key_secret)

# Transform from bytes to bytes that can be printed
b64_encoded_key = base64.b64encode(key_secret)
#Transform from bytes back into Unicode
b64_encoded_key = b64_encoded_key.decode('ascii')

import requests
base_url = 'https://api.twitter.com/'
auth_url = '{}oauth2/token'.format(base_url)
auth_headers = {
    'Authorization': 'Basic {}'.format(b64_encoded_key),
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
}
auth_data = {
    'grant_type': 'client_credentials'
}
auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)
print(auth_resp.status_code)
access_token = auth_resp.json()['access_token']

import json
search_headers = {
    'Authorization': 'Bearer {}'.format(access_token)
}
search_params = {
    'locations': '-74,40,-73,41',
    'language': 'en',
    'result_type': 'recent',
    'count': 10
}
# Create the URL
search_url = '{}1.1/search/tweets.json'.format(base_url)
print(search_url)
# Execute the get request
search_resp = requests.get(search_url, headers=search_headers, params=search_params)
# Get the data from the request
Data = json.loads(search_resp.content )
# Print out the data!
print(Data['statuses'])