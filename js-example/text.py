import requests

for i in range(0,10):
    res = requests.post('http://localhost:5003/data',data={'user':'u1','req' : 'HELLO','ticket' : 'HI'},timeout=2)
    print(res.content)