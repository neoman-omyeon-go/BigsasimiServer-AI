import requests
import random

url = "http://127.0.0.1:8000/test/5"

res = requests.get(url)

print("status : ", res.status_code)
print(res.json())