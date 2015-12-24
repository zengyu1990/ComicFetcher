from urllib import request, parse
import re, time, json, os


def getData(url):
    webheader = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'}
    req = request.Request(url=url, headers=webheader)
    webPage = request.urlopen(req)
    data = webPage.read()
    return data


def getImage(refnum, pagenum):
    url = 'http://m.comic.ck101.com/vols/%s/%s' % (refnum, pagenum)
    data = getData(url)
    data = data.decode('utf-8')
    imgmatch = re.compile(r'img src\=\"(http:[^\s]*?(jpg|png|gif))')
    for link, t in imgmatch.findall(str(data)):
        return link


def getLink(url, RegEx):
    global refBox
    data = getData(url)
    data = data.decode('utf-8')
    match = re.compile(regEx)
    for episode, refnum in match.findall(str(data)):
        if episode not in refBox:
            refBox[int(episode)] = int(refnum)


def getPage(refnum):
    url = 'http://comic.ck101.com/vols/%s/1' % refnum
    data = getData(url)
    data = data.decode('utf-8')
    pageMatch = re.compile(r'\第(\d+)\頁')
    return int(pageMatch.findall(str(data))[-1])


def getPath(episode, page, imgLink):
    ext = os.path.splitext(os.path.basename(parse.urlparse(imgLink)[2]))[1]
    filename = str(page) + ext
    path = os.path.join(os.environ['PWD'], str(episode))
    return path, os.path.join(path, filename)


def down(episode, page, imgLink):
    path, fullpath = getPath(episode, page, imgLink)
    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        imgData = getData(imgLink)
        try:
            with open(fullpath, 'wb') as imgFile:
                imgFile.write(imgData)
            print('Page %s downloaded.' % page)
        except:
            print('Failed to download page %s' % page)


def getAuth():
    global linkBox
    auth = input('All finished. Start downloading? (y/n)')
    if auth is not 'y':
        raise PermissionError
    for ep, value in linkBox.items():
        print('Start downloading episode %s' % ep)
        for pg, url in value.items():
            down(ep, pg, url)
            if pg % 5 == 0:
                print('Delay for 5 seconds.')
                time.sleep(5)


refBox = {}
linkBox = {}
print('A script used to fetch comics from comic.ck101.com')
regEx = input('Regular Expression?')
coverLink = input('Cover Link?')
jsonPath = os.path.join(os.environ['PWD'], 'ComicLinks.json')
print('Automatically save session to', jsonPath)

if __name__ == '__main__':
    getLink(coverLink, regEx)
    for episode in range(1, max(refBox.keys()) + 1):
        if episode in refBox.keys():
            pagenum = getPage(refBox[episode])
            print('Episode %s, total %s pages.' % (episode, pagenum))
            linkBox[episode] = {}
            for page in range(1, pagenum + 1):
                imgLink = getImage(refBox[episode], page)
                linkBox[episode][page] = imgLink
                print('Episode %s Page %s: %s' % (episode, page, imgLink))
                if page % 5 == 0:
                    print('Delay for 5 seconds.')
                    time.sleep(5)
            with open(jsonPath, 'w') as file:
                json.dump(linkBox, file)
            print('All page links in episode %s have been analyzed.' % episode)
        else:
            print('Episode %s not found.' % episode)
    getAuth()