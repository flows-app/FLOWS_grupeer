from bs4 import BeautifulSoup
import urllib.request
import http.cookiejar
import json
import datetime
from urllib.request import Request, urlopen

def handler(event, context):
    username = event['account']['username']
    password = event['account']['password']

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPRedirectHandler(),
        urllib.request.HTTPHandler())
    opener.addheaders = [('User-agent', "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36")]

    req = Request('https://www.grupeer.com/login', headers={'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36"})
    html = opener.open(req).read()
    soup = BeautifulSoup(html, 'html.parser')
    csrf=soup.form.input['value']
    postdata = urllib.parse.urlencode({"_token":csrf,
                                       "email":username,
                                       "password":password}).encode("utf-8")
    
    req = Request('https://www.grupeer.com/login',
                data=postdata,
                method='POST')
    
    response = opener.open(req)
    html = response.read()
    
    # data extraction
    soup = BeautifulSoup(html, 'html.parser')
    balanceStr = soup.select("div[class=overview-block] div[class=block-value]")[0].string
    balance = balanceStr.replace("€","").replace(',','')
    
    investedStr = soup.select("div[class=overview-block] div[class='col-6 block-info-value']")[1].string
    invested = investedStr.replace("€","").replace(',','')
    
    availableStr = soup.select("div[class=overview-block] div[class='col-6 block-info-value']")[0].string
    available = availableStr.replace("€","").replace(',','')
    
    result = {"balance":balance,"available":available,"invested":invested}
    
    resultStr = json.dumps(result)
    customcontext = context.client_context.custom
    if "lastvalue" in customcontext and resultStr == customcontext['lastvalue']:
      return
    else:
      result['dedupid']=resultStr
      return result
