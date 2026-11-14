import requests
URL_TPINFO='https://ipinfo.io'

def get_location(ip):
    response=requests.get(URL_TPINFO+'/'+ip+'/json')
    if response.status_code == 200:
        return response.json()
if __name__ == '__main__':
   print(get_location('45.148.10.147'))