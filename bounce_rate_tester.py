import requests
import json
from secret import API_KEY, API_BASE_URL

def get_bounces():
    return requests.get(
        API_BASE_URL,
        auth=("api", API_KEY))

bounce_list = get_bounces()
print(bounce_list)
#with open("./bounce_list.json", "r", encoding="utf8") as f:
#    json.dump(bounce_list, f, indent=4)

