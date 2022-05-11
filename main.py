# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
#TODO: Download images for faster use
#TODO: Add functions "Add combo" / "View Combos" / "Add Bricks" / "Add Handtraps"
import os
import webbrowser
from io import BytesIO
import PySimpleGUI as sg
from PIL import ImageQt

import requests

def image_to_data(im):
    """
    Image object to bytes object.
    : Parameters
      im - Image object
    : Return
      bytes object.
    """
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data




if __name__ == '__main__':
    fname = "deck/RealDeck.ydk"
    main = []
    maind = False
    mainReady = {}
    images = {}

    bdurl = "https://db.ygoprodeck.com/api/v7/cardinfo.php?id="

    if (os.path.isfile(fname)):
        with open(fname) as f:
            for line in f:
                if(line.startswith('#')):
                    if "main" in line:
                        maind = True
                    if "extra" in line:
                        maind = False
                else:
                    if (maind):

                        main.append(line.strip())
        f.close()
        for x in main:
            try:
                first_response = requests.get(bdurl + x, timeout=5)
            except (requests.ConnectionError, requests.Timeout) as exception:
                print("No internet connection and pack not in files. Aborting")
                break;
            response_list = first_response.json()
            cardname = response_list["data"][0]['name']
            if cardname in mainReady:
                mainReady[cardname] = mainReady[cardname]+1
            else:
                mainReady[cardname] = 1
                images[cardname] = "https://storage.googleapis.com/ygoprodeck.com/pics_small/" + x + ".jpg"
        print(main)
        print(len(main))
        print(mainReady)
        sg.theme('DarkBlue')
        layout = [[]]
        n = 0
        c = 0
        for i, card in enumerate(mainReady):
            # print(card)
            sg.one_line_progress_meter('Downloading card pictures', i + 1, len(mainReady))
            url = images[card]
            response = requests.get(url, stream=True)
            response.raw.decode_content = True

            box = (19, 43, 150, 173)
            img = ImageQt.Image.open(response.raw).crop(box)
            data = image_to_data(img)
            titletxt = card + " - " + str(mainReady[card])

            layout[c].append(sg.Frame(title=titletxt, title_location='s', relief='ridge',
                                      layout=[[sg.Image(data=data, size=(131, 130), enable_events=True,
                                                        k='SC-' + card + '-' + str(c) + str(n),
                                                        tooltip=mainReady[card])]]))

            n += 1
            if (n == 8):
                n = 0
                layout.append([])
                c += 1

        layout[c].append(sg.Button('Quit', enable_events=True, key='Q'))
        window = sg.Window('Card Display', layout, finalize=True)

        while True:  # Event Loop
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Q':
                quit = True
                window.close()
                break
            if event.startswith('SC-'):
                split = event.split('-')
                webbrowser.open('https://db.ygoprodeck.com/card/?search=' + split[1], 2)


