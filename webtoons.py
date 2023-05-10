import lxml
import requests as http
from bs4 import BeautifulSoup as xml
import os
import sys

def htmlContent( link:str, headers={} ):
	return xml( http.get( link, headers=headers ).content, 'lxml' )

if len( sys.argv ) == 3:
	webtoonURL = sys.argv[2].replace("www.webtoons.com","m.webtoons.com")
else:
	webtoonURL = input("Webtoon URL : ").replace("www.webtoons.com","m.webtoons.com")
	print()

document = htmlContent( webtoonURL, {
	'user-agent': 'Mozilla/5.0 (Linux; Android 11.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
	'referer': webtoonURL
})

episodeList = [ {
	'title': li.find("a").find(class_="ellipsis").text[1 : : ] if li.find("a").find(class_="ellipsis").text.startswith(" ") else li.find("a").find(class_="ellipsis").text,
	'link': li.find("a")['href']
} for li in document.find(id="_episodeList").findAll(class_="_episodeItem") ]

episodeList.reverse()

for i, obj in enumerate( episodeList ):
	index = str(i+1).zfill( len( str( len(episodeList) ) ) )
	episodeList[i]['log'] = f" #{ index } | { obj['title'] }"
	episodeList[i]['name'] = f"#{ index } { obj['title'] }"
	print( episodeList[i]['log'] )

allEpisode = input("\nDo you want to download all episodes? ( y|n default=y ) : ")
isDownloadAll = False

if allEpisode.lower() == "n":
	chapter = input(f"Enter the episode you want to download ( 1-{ len(episodeList) } ) : ")
	if "-" in chapter:
		isDownloadAll = {
			'start': int( chapter.split("-")[0].replace(" ","") ) - 1,
			'end': int( chapter.split("-")[1].replace(" ","") )
		}
	else:
		isDownloadAll = {
			'start': int( chapter ) - 1,
			'end': int( chapter )
		}
	episodeList = episodeList[ isDownloadAll['start'] : isDownloadAll['end'] ]

for episode in episodeList:

	chapterPage = htmlContent( episode['link'], {
		'user-agent': 'Mozilla/5.0 (Linux; Android 11.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
		'referer': episode['link']
	})

	for script in chapterPage.findAll("script"):
		if "var imageList = [" in script.text:
			scriptText = script.text
	listen = [ linkModel.split('"')[0] for linkModel in scriptText[ scriptText.find('['):scriptText.find(']') + 1 ].split('url : "') ]
	listen.pop(0)
	episode['images'] = listen
	
	
for obj in episodeList:
	title = webtoonURL.split("/")[5]
	folder = f"{os.getcwd()}/Webtoons/{title}/{obj['name']}"
	if not os.path.exists( folder ):
	    os.makedirs( folder, 0o755 )
	print()
	for i, image in enumerate( obj['images'] ):
	    i+=1
	    img = http.get( image, headers = {
	        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
		    'referer': obj['link']
	    })
	    file = f"{folder}/{ str(i).zfill( len(str(len(obj['images']))) ) }.jpeg"
	    
	    with open( file, "wb" ) as fs:
	        fs.write( img.content )
	    print( f" { obj['log'] }  [ { i } / { len(obj['images']) } ]    ", end="\r" )
