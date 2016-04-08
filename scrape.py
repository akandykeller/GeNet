from urlparse import urljoin
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import numpy as np
import requests, csv, os, string, pickle, re

SLEEPER = True  # Enable sleep between requests to slow crawler
BASE_URL = "http://genius.com"
all_artists_file = 'hiphop_artists.txt'  # File which contains plaintext names of all desired artists
artist_url_file = 'artist_urls.p'  # File name to save scraped list of all artists
max_letter_pages = 100
artist_urls = []

# If we've already scraped the list of artist URLS for all desired artists, just load it
if os.path.isfile(artist_url_file):
    with open(artist_url_file, 'r') as a_file:
        artist_urls = pickle.load(a_file)
# Otherwise re-scrape it
else:
    for letter in string.lowercase + '0':
        for page in range(1,max_letter_pages):
            page_url = "http://genius.com/artists-index/{}/all?page={}".format(letter, page)

            print "_______LETTER {}__**__PAGE {}________".format(letter,page) * 10
            
            if SLEEPER:
                sleep(randint(100,200)/100.0)

            response = requests.get(page_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'})
            soup = BeautifulSoup(response.text, "lxml")

            # Move to the next letter if there are no more artists on this page (meaning letter is done)
            if len(soup.select('ul.artists_index_list > li > a')) < 1:
                break

            for song_link in soup.select('ul.artists_index_list > li > a'):
                artist_urls.append(song_link['href'])

    with open(artist_url_file, 'w') as a_file:
        pickle.dump(artist_urls, a_file)

# Read the names of all artists 
with open(all_artists_file, 'r') as f: 
  names = f.read().split('\n')

  # Filter names to remove items in parenthesis and brackets
  names_filt =  [re.sub(r'\[.*\]', '', n) for n in names]
  hiphop_artists =  [re.sub(r'\(.*\)', '', n) for n in names_filt]
  # Get the final list of names which match the format of the URL names
  hiphop_artists = [h.replace('-', ' ').replace('.', '').lower() for h in hiphop_artists]

# Convert the artist names from the URL to a free text name in the same format as hiphop_artists
url_names = [(i, a.split('/')[-1].replace('-', ' ').replace('.','').lower()) for i, a in enumerate(artist_urls)]
# Only save urls for artists that are in our list
hiphop_artist_urls = [artist_urls[i] for i, n in url_names if n in hiphop_artists]

# For each artist, scan over their song list and scrape all Lyrics along with all
# lyric <-> annotation pairs. Lyrics are saved to $SONG_NAME + _LYRICS.txt, annotation
# lyric pairs are saved to $SONG_NAME.csv. All artists are saved to their own directories. 
for artist_url in hiphop_artist_urls:
    print_all = False

    num_pages = 50 # Maximum number of pages to scrape for each artist 

    artist_name = artist_url.split('/')[-1].replace('/','')
    artist_dir = artist_name.replace(' ', '_')

    # Define the default starting page for the artist to be 1
    start_page = 1

    if not os.path.isdir(artist_dir):
        os.mkdir(artist_dir)
        print "Created directory for current artist: {}".format(artist_dir)
    else:
        print "Artist dir {} exists".format(artist_dir)

        # Check if the .artist_done file has been added, meaning we can skip to the next artist
        if os.path.isfile(artist_dir + '/.artist_done'):
            print "Artist Complete. Skipping."
            continue

        # There are 20 songs max per page, so we can get a rough estimate of the page number 
        # by dividing number of files by 20... problem is we dont make a file for every song
        start_page = int(np.ceil(len([x for x in os.listdir(artist_dir) if 'LYRICS' in x]) / 20.0))
        print "Found {} full pages, starting at {}".format(start_page - 1, start_page)

    print "Crawling {}'s song list...".format(artist_name)

    # Keep making page requests until there are no more songs on a given page
    for page_num in range(start_page,num_pages):
        print "_______PAGE {}________".format(page_num) * 10

        response = requests.get(artist_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'})
        soup = BeautifulSoup(response.text, "lxml")
        # Extract artist id from page
        artist_id = soup.select('form.edit_artist')[0]['id'].split('_')[-1]
        # Formulate request url
        artist_page_url = "http://genius.com/artists/songs?for_artist_page={}&id={}&page={}".format(artist_id, artist_name, page_num)

        if SLEEPER:
            sleep(randint(50,150)/100.0)

        response = requests.get(artist_page_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'})
        soup = BeautifulSoup(response.text, "lxml")

        # Quit looking for more songs when you've reached the last page 
        # (as signled by the song list being empty)
        if len(soup.select('ul.song_list > li > a')) < 1:
            break

        # For each song by the given artist 
        for song_link in soup.select('ul.song_list > li > a'):
            song_title = song_link['title'].encode('ascii', 'ignore')
            print "Scraping {}".format(song_title)
            
            link = urljoin(BASE_URL, song_link['href'])

            response = requests.get(link)
            soup = BeautifulSoup(response.text)

            # Try to scrape all lyrics and encode as ascii
            try:
                all_lyrics = soup.find('lyrics').text.encode('ascii', 'ignore').strip()
            except AttributeError:
                continue

            # Get list of all links for annotations
            referent_links = [urljoin(BASE_URL, x['href']) for x in soup.find('lyrics').find_all('a', class_='referent')]
            song_title = song_title.replace('.', '').replace(' ', '_').replace('"','\'').replace('/','_').replace('(','').replace(')','').strip()
            
            # Clip song title length to reasonable file name length
            if len(song_title) > 200:
                song_title = song_title[0:200]

            file_name = artist_dir + "/" + song_title

            # Uncomment below if you dont want to overwrite files
            # while os.path.isfile(file_name):
            #     file_name += '_new'

            lyric_file_name = file_name + "_LYRICS.txt"
            file_name += '.csv'
                
            # If the file already a file, dont create any new files
            if len(referent_links) == 0 or os.path.isfile(file_name):
                continue

            print "Writing lyrics to: {}".format(lyric_file_name)
            
            with open(lyric_file_name, "w") as text_file:
                text_file.write(all_lyrics)

            print "Created a file for the song references: {}".format(file_name)
            fieldnames = ['Lyric', 'Ref']

            with open(file_name, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
                writer.writeheader()
            
                # Loop over all annotation links and write a line to the csv file with 
                # both the annotation and the lyric
                for ref_link in referent_links:

                    if SLEEPER:
                        sleep(randint(1,15)/100.0)

                    response = requests.get(ref_link)
                    soup = BeautifulSoup(response.text)
                    try:
                        lyric = soup.find('meta', property="rap_genius:referent")['content'].encode('ascii', 'ignore')
                        annot = soup.find('meta', property="rap_genius:body")['content'].encode('ascii', 'ignore')
                    except TypeError:
                        continue

                    # Since we use | as csv delimiter, remove it from text
                    lyric = lyric.replace('|', '')
                    annot = annot.replace('|', '')

                    writer.writerow({'Lyric': lyric, 'Ref': annot})
                    
                    if print_all:
                        print "Lyric: {}".format(lyric)
                        print "Annot: {}".format(annot)
                        print "--"*20
    # Create the .artist_done file in the artists directory when we are done so we dont
    # loop again
    with open(artist_dir + '/.artist_done','w') as f:
        f.write(' ')