from urlparse import urljoin
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import requests, csv, os

SLEEPER = True
BASE_URL = "http://genius.com"

artist_urls = [#'http://genius.com/artists/Ab-soul', 
               #'http://genius.com/artists/Action-bronson',
               #'http://genius.com/artists/Aesop-rock',
               #'http://genius.com/artists/Anderson-paak',
               #'http://genius.com/artists/A-ap-ferg',
               #'http://genius.com/artists/A-ap-mob',
               #'http://genius.com/artists/A-ap-rocky',
               #'http://genius.com/artists/Akon',
               # 'http://genius.com/artists/Apollo-brown',
               # 'http://genius.com/artists/Azizi-gibson',
               # 'http://genius.com/artists/Big-sean',
               # 'http://genius.com/artists/Boosie-badazz',
               # 'http://genius.com/artists/Bet-hip-hop-awards',
               # 'http://genius.com/artists/Busta-rhymes',
               # 'http://genius.com/artists/Chance-the-rapper',
               # 'http://genius.com/artists/Chief-keef',
               # 'http://genius.com/artists/Childish-gambino',
               # 'http://genius.com/artists/Curren-y',
               # 'http://genius.com/artists/Casey-veggies',
               # 'http://genius.com/artists/Denzel-curry',
               # 'http://genius.com/artists/Drake',
               # 'http://genius.com/artists/Drake-and-future',
               # 'http://genius.com/artists/Dr-dre',
               # 'http://genius.com/artists/E-40',
               # 'http://genius.com/artists/Earl-sweatshirt',
               # 'http://genius.com/artists/Eminem',
               # 'http://genius.com/artists/Eazy-e',
               # 'http://genius.com/artists/Fetty-wap',
               # 'http://genius.com/artists/Flatbush-zombies',
               # 'http://genius.com/artists/Freddie-gibbs',
               # 'http://genius.com/artists/Future',
               # 'http://genius.com/artists/Gucci-mane',
               # 'http://genius.com/artists/G-unit',
               # 'http://genius.com/artists/Gza',
               # 'http://genius.com/artists/Iamsu',
               # 'http://genius.com/artists/Ilovemakonnen',
               # 'http://genius.com/artists/Jay-z',
               # 'http://genius.com/artists/Jay-electronica',
               # 'http://genius.com/artists/Joey-bada',
               # 'http://genius.com/artists/Juicy-j',
               # 'http://genius.com/artists/J-dilla',
               # 'http://genius.com/artists/J-kwon',
               # 'http://genius.com/artists/Kanye-west',
               # 'http://genius.com/artists/Kendrick-lamar',
               # 'http://genius.com/artists/Lil-wayne',
               # 'http://genius.com/artists/Logic',
               # 'http://genius.com/artists/Migos',
               # 'http://genius.com/artists/Nas',
               # 'http://genius.com/artists/The-notorious-big',
               # 'http://genius.com/artists/Nwa',
               # 'http://genius.com/artists/Odd-future',
               # 'http://genius.com/artists/Oddisee',
               'http://genius.com/artists/Pusha-t',
               'http://genius.com/artists/Rae-sremmurd',
               'http://genius.com/artists/Rich-homie-quan',
               'http://genius.com/artists/Rich-gang',
               'http://genius.com/artists/Rick-ross',
               'http://genius.com/artists/Rza',
               'http://genius.com/artists/Schoolboy-q',
               'http://genius.com/artists/Snoop-dogg',
               'http://genius.com/artists/Tech-n9ne',
               'http://genius.com/artists/Tory-lanez',
               'http://genius.com/artists/Ty-dolla-sign',
               'http://genius.com/artists/Tyler-the-creator',
               'http://genius.com/artists/Tyga',
               'http://genius.com/artists/Wiz-khalifa',
               'http://genius.com/artists/Wu-tang-clan',
               'http://genius.com/artists/Yg',
               'http://genius.com/artists/Young-thug']

for artist_url in artist_urls:
    print_all = False

    num_pages = 50

    artist_name = artist_url.split('/')[-1].replace('/','')

    artist_dir = artist_name.replace(' ', '_')

    if not os.path.isdir(artist_dir):
        os.mkdir(artist_dir)
        print "Created directory for current artist: {}".format(artist_dir)

    print "Crawling {}'s song list...".format(artist_name)


    for page_num in range(1,num_pages):
        print "_______PAGE {}________".format(page_num) * 10
        #artist_url = "http://genius.com/artists/songs?for_artist_page=556&id=Tony-yayo&page={}".format(page_num)

        response = requests.get(artist_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'})
        soup = BeautifulSoup(response.text, "lxml")

        artist_id = soup.select('form.edit_artist')[0]['id'].split('_')[-1]

        artist_page_url = "http://genius.com/artists/songs?for_artist_page={}&id={}&page={}".format(artist_id, artist_name, page_num)

        sleep(randint(10,100)/100.0)

        response = requests.get(artist_page_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'})
        soup = BeautifulSoup(response.text, "lxml")


        if len(soup.select('ul.song_list > li > a')) < 1:
            break

        # For each song by the given artist 
        for song_link in soup.select('ul.song_list > li > a'):
            song_title = song_link['title'].encode('ascii', 'ignore')
            print "Scraping {}".format(song_title)
            
            link = urljoin(BASE_URL, song_link['href'])

            response = requests.get(link)
            soup = BeautifulSoup(response.text)

            all_lyrics = soup.find('lyrics').text.encode('ascii', 'ignore').strip()

            referent_links = [urljoin(BASE_URL, x['href']) for x in soup.find('lyrics').find_all('a', class_='referent')]

            song_title = song_title.replace('.', '').replace(' ', '_').replace('"','\'').replace('/','_').replace('(','').replace(')','').strip()
            
            if len(song_title) > 200:
                song_title = song_title[0:200]

            file_name = artist_dir + "/" + song_title
            # while os.path.isfile(file_name):
            #     file_name += '_new'

            lyric_file_name = file_name + "_LYRICS.txt"
            file_name += '.csv'
                
            if os.path.isfile(file_name):
                continue

            print "Writing lyrics to: {}".format(lyric_file_name)
            
            with open(lyric_file_name, "w") as text_file:
                text_file.write(all_lyrics)


            print "Created a file for the song references: {}".format(file_name)
            fieldnames = ['Lyric', 'Ref']

            with open(file_name, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
                writer.writeheader()
            
                for ref_link in referent_links:

                    if SLEEPER:
                        sleep(randint(1,15)/100.0)

                    #print ref_link
                    response = requests.get(ref_link)
                    soup = BeautifulSoup(response.text)
                    #print soup
                    try:
                        lyric = soup.find('meta', property="rap_genius:referent")['content'].encode('ascii', 'ignore').replace('\n', ' ')
                        annot = soup.find('meta', property="rap_genius:body")['content'].encode('ascii', 'ignore').replace('\n',' ')
                    except TypeError:
                        continue

                    lyric = lyric.replace('|', '')
                    annot = annot.replace('|', '')

                    writer.writerow({'Lyric': lyric, 'Ref': annot})
                    
                    if print_all:
                        print "Lyric: {}".format(lyric)
                        print "Annot: {}".format(annot)
                        print "--"*20