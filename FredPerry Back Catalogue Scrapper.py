#Imports Required Modules
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import re
import smtplib, ssl
import pickle

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#Adds variables for the Fred Perry site and for parsing it
url = "https://www.fredperry.com/back-catalogue-men"
html = urllib.request.urlopen(url, context=ctx).read()
soup = BeautifulSoup(html, "html.parser")

# Retrieve all previous Dict
try :
    with open("PickledURLDIC.txt", "rb") as myFile:
        pickledict = dict(pickle.load(myFile))
except :
    print("Failed to Open Previous dic")

#Starts Creating a Dictionary for the sites current state
count = 0
urldict = {}
diffdict = {}
#Finds all links on the back catalogue page
for link in soup.find_all("a"):
    linkstr = str(link)
    if count == 1:
        if re.findall("title=", linkstr):
            url = link.get("href")
            urldict[url] = 0
    elif re.findall(".a href=.#. id=.product-start.><.a>", linkstr):
        count = 1
count = 0
#Goes and finds the price for every link found in the previous step.
for urls in urldict:
    #Used for speeding up testing
    if count < 1:
        htmls = urllib.request.urlopen(urls, context=ctx).read()
        soups = BeautifulSoup(htmls, "html.parser")
        soups = str(soups)
        price = re.findall('<meta\scontent="(\d{1,10}[.\d]{0,3})"\sproperty="product:price:amount"\/>',soups,)
        price = float(price[0])
        urldict[urls] = price
        #Used for testing count=count+1
#Makes sure that even if there isn't a previous dictionary the comparison can happen later on.
try : type(pickledict)
except : pickledict={}
#Checks if the previous dictionary and the new dictionary match.
if pickledict == urldict :
    print("Dic do match")
else :
    print("Dic Don't Match")
    with open("PickledURLDIC.txt", "wb") as myFile:
        pickle.dump(urldict, myFile)
    diffstring="Changes are \n"
    for (link,value) in urldict.items() :
        if ((link,value) in pickledict.items() ) == False :
            diffdict[link]=value
    for (url,price) in diffdict.items() :
        url=str(url)
        price=str(price)
        diffstring=diffstring+url+" Price is "+price+"\n"
    port = 587  # For starttls
    smtp_server = ""
    sender_email = ""
    receiver_email = ""
    password = ""
    message = """\
    #Subject: The Fred Perry Back Catalogue has changed.

    """ + diffstring + "\n" + "#This message is sent from Python."

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)



