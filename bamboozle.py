# Author: Tim Kinneen
# Version: 1.0.1
# e-mail: kinneen@gmail.com
#
# Description:
#
# This program connects to the HTML5 courseware page on Bamboo and checks
# every 10 minutes for a new build. If it finds one, it plays a notification
# sound and downloads it.  It also extracts the file automatically. While it
# is currently formatted for this specific courseware, it could easily be
# modifed for other software.  Comments or suggestions are welcome. 

# Imports
import time, os, sys, winsound, zipfile
from urllib.request import urlretrieve
from urllib.request import urlopen

# This function will unzip the compressed build file
def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)

def bamboo_checker():
    
    # Variable initialization
    current_available = ""
    last_downloaded = 0

    # Here are a few options for new build notification sounds
    # Uncomment the sound you want to play
    #soundfile = "one.wav"
    #soundfile = "throw.wav"
    #soundfile = "bonus.wav"
    #soundfile = "pipe.wav"
    soundfile = "powerup.wav"

    while True:
    
        # Opens "Latest Build" page on Bamboo, reads source code, saves it
        # as an object, then converts it to a string for parsing
        page = urlopen("http://cd0:8080/bamboo/browse/WELD-CWCLIENT2/latest")
        contents = page.read()
        source = contents.decode(encoding = 'UTF-8')

        # Finds index positon of the build number in string, parses that
        # number and saves to variable
        dex = source.find('Build #')
        current_build = source[dex + 7] + source[dex + 9] + source[dex + 10] + source[dex + 11]
        current_int = int(current_build)

        # Inserts build number into the URL template of the download page
        artifact = 'http://cd0:8080/bamboo/browse/WELD-CWCLIENT2-1355/artifact'
        artifact = artifact[:45] + current_build + artifact[49:]

        # Opens artifact page and saves the page source to string
        page = urlopen(artifact)
        contents = page.read()
        source = contents.decode(encoding = 'UTF-8')

        # Finds full build number in string, parses it, then inserts the
        # last four digits of the latest build at the end
        dex = source.find('2.4.')
        full_build = source[dex] + source[dex + 1] + source[dex + 2] + source[dex + 3] + source[dex + 4] + source[dex + 5] + source[dex + 6] + source[dex + 7]  + source[dex + 8]  + source[dex + 9]  + source[dex + 10]
        full_build = full_build[:7] + current_build + full_build[12:]

        # This string is a template for the download link that the new
        # build info is parsed into
        template = "http://cd0:8080/bamboo/browse/WELD-CWCLIENT2-1343/artifact/JOB1/CW2-ALL/cw2-2.4.62.1343.zip"
        
        # Searches download link for a position close to the build number,
        # then inserts the updated number over the outdated one
        dex = template.find('T2-')
        dl_link = template[:dex + 3] + current_build + template[dex + 7:]

        # This does the same as above, with the full build number
        dex = dl_link.find('ALL')
        dl_link_final = dl_link[:dex + 8] + full_build + dl_link[dex + 19:]

        # Welcomes user to program (if this is the first time through)
        if last_downloaded == 0:
            print('Welcome to the Courseware Downloader application')
            print()
            last_downloaded = 1

        # Checks the last downloaded build and downloads a new one if available
        if current_int > last_downloaded:
            last_downloaded = current_int
            print('There is a new build available!')
            new_page = urlopen(artifact)
            print('Downloading Build#: ', full_build)
            print()
            latest_download = urlretrieve(dl_link_final, "latest_build.zip")
            
            # Updates the last download logged
            last_downloaded = current_int

            # Plays notification sound
            winsound.PlaySound(soundfile, winsound.SND_FILENAME|winsound.SND_ASYNC)

            # Creates a folder to extract build into
            newpath = './'
            newpath = newpath + full_build
            if not os.path.exists(newpath): os.makedirs(newpath)

            # Calls the unzip function and extracts build
            unzip("latest_build.zip", newpath)

            # Gets rid of the already-extracted zip file
            os.remove('latest_build.zip')

        # If user has the latest build, this lets them know
        else:
            print('', end='')

        # Pauses the loop for 5 minutes before it starts over and
        # re-checks for a new build
        time.sleep(600)

bamboo_checker()
