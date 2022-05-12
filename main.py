# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# DONE: Download images for faster use
# DONE: Add functions "Add combo" / "View Combos" / "Add Handtraps"
# TODO: Add bricks function maybe?
# TODO: Add the actual maths behind it now
import os
import webbrowser
from io import BytesIO
import PySimpleGUI as sg
from PIL import ImageQt
from PIL import Image

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
    fnameImg = "img/"
    main = []
    maind = False
    mainReady = {}
    images = {}
    combos = []
    prot = []

    bdurl = "https://db.ygoprodeck.com/api/v7/cardinfo.php?id="

    if os.path.isfile(fname):
        with open(fname) as f:
            for line in f:
                if (line.startswith('#')):
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
                mainReady[cardname] = mainReady[cardname] + 1
            else:
                mainReady[cardname] = 1
                images[cardname] = x
        # print(main)
        # print(len(main))
        # print(mainReady)
        sg.theme('DarkBlue')
        layout = [[]]
        n = 0
        c = 0
        for i, card in enumerate(mainReady):
            # print(card)
            data = ""
            if os.path.isfile(fnameImg + str(images[card] + ".jpg")):
                img = ImageQt.Image.open(fnameImg + str(images[card] + ".jpg"))
                data = image_to_data(img)
            else:
                sg.one_line_progress_meter('Downloading card pictures', i + 1, len(mainReady))
                url = "https://storage.googleapis.com/ygoprodeck.com/pics_small/" + str(images[card]) + ".jpg"
                response = requests.get(url, stream=True)
                response.raw.decode_content = True

                box = (19, 43, 150, 173)
                img = Image.open(response.raw).crop(box)

                data = image_to_data(img)

                img = img.save(fnameImg + str(images[card]) + ".jpg")

            if len(card) <= 20:
                titletxt = card + " - " + str(mainReady[card])
            else:
                titletxt = card[0:20] + " - " + str(mainReady[card])

            layout[c].append(sg.Frame(title=titletxt, title_location='s', relief='ridge',
                                      layout=[[sg.Image(data=data, size=(131, 130), enable_events=True,
                                                        k='SC-' + card + '-' + str(c) + str(n),
                                                        tooltip="Click to open on ygoprodeck")]]))
            layout[c].append(sg.Checkbox(text="", default=False, key="CB-" + card, tooltip=card))

            n += 1
            if (n == 8):
                n = 0
                layout.append([])
                c += 1


        layout[c].append(sg.Button('Add Combo', enable_events=True, key='C'))
        layout[c].append(sg.Button('Show Combos', enable_events=True, key='S'))
        layout[c].append(sg.Button('Remove Newest Combo', enable_events=True, key='R'))
        layout.append([])
        layout[c+1].append(sg.Button('Add protection cards', enable_events=True, key='P'))
        layout[c+1].append(sg.Button('Show protection cards', enable_events=True, key='SR'))
        layout[c+1].append(sg.Button('Remove protection cards', enable_events=True, key='PR'))
        layout.append([])
        layout[c+2].append(sg.Button('Quit', enable_events=True, key='Q'))
        window = sg.Window('Card Display', layout, finalize=True)


        while True:  # Event Loop
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Q':
                quit = True
                window.close()
                break
            if event.startswith('SC-'):
                print(event)
                split = event.split('-')
                # webbrowser.open('https://db.ygoprodeck.com/card/?search=' + split[1], 2)
            if event == 'C':
                combo = []
                for row in layout:
                    for element in row:
                        if (element.key):
                            if (element.key).startswith("CB-"):
                                #print(element.key + str(element.get()))
                                if element.get():
                                    combo.append(element.key[3:])
                                    element.update(value=False)
                if(len(combo) > 0 and combo not in combos):
                    combos.append(combo)
            if event == 'S':
                print(combos)
            if event == 'R':
                if (len(combos) > 0):
                    combos.pop()
            if event == 'P':
                for row in layout:
                    for element in row:
                        if (element.key):
                            if (element.key).startswith("CB-"):
                                #print(element.key + str(element.get()))
                                if element.get():
                                    if (element.key[3:]) not in prot:
                                        prot.append(element.key[3:])
                                    element.update(value=False)
            if event == 'SR':
                print(prot)
            if event == 'PR':
                prot = []
