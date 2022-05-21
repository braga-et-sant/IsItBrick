# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# DONE: Download images for faster use
# DONE: Add functions "Add combo" / "View Combos" / "Add Handtraps"
# DONE: Add the actual maths behind it now
# TODO: Bug when only 1 combo is selected
# DONE: Add custom tag menu, improve UI a bit
# TODO: Save custom tags system
import os
import webbrowser
from io import BytesIO
import PySimpleGUI as sg
from PIL import ImageQt
from PIL import Image

import requests
import basicsim

htlist = ["D.D. Crow", "Ghost Reaper & Winter Cherries", "Chaos Hunter", "Effect Veiler", "Ghost Ogre & Snow Rabbit", "Nibiru, the Primal Being", "PSY-Framegear Gamma", "Ash Blossom & Joyous Spring", "Droll & Lock Bird", "Ghost Belle & Haunted Mansion", "Artifact Lancea", "Infinite Impermanence", "Skull Meister", "Dimension Shifter", "Token Collector"]
seclist =htlist.copy()
seclist += ("Forbidden Droplets", "Lightning Storm", "Super Polymerization", "Kaiju", "The Winged Dragon Of Ra – Sphere Mode", "Red Reboot", "Evenly Matched", "Dark Ruler No More", "Alpha, the Master of Beasts")
protlist = ["Called by the Grave", "Crossout Designator", "Instant Fusion", "Branded Lost"]

combos = []

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

def makeComboWindow():
    """
    Creates a layout file with all the sets available as globals.
    Basically just executes createChecks multiple times in a row
    :return: sg.Window
    """
    layout = []
    layout.append([[sg.InputText(key="COMBO", default_text="Combo goes here")]])
    layout.append([])
    layout.append([
        [sg.Button('Add card', key='-AddC-'), sg.Button('Add tag', key='-AddT-'),
         sg.Button('Add AND', key='-AddA-'),  sg.Button('Done', key='-AddD-'),
         sg.Button('Clear', key='-AddClear-'), sg.Button('Exit', key='-SEXIT-'),
         sg.Button('+', key='-AddPlus-'),
         sg.Button('-', key='-AddMinus-'),
         sg.Button('=', key='-AddEqual-'),
         sg.InputCombo(([1, 2, 3]), readonly=False, key='-AddNumber-', default_value=1)]
    ])

    #
    layout.append([sg.Text('Monster Cards:')])
    layout.append([])
    c = 4
    r = 0
    for card in allcards:
        layout[c].append(sg.Button(button_text=card, key='CARD-' + card))
        if (r < 6):
            r += 1
        else:
            r = 0
            c += 1
            layout.append([])

    #
    layout.append([sg.Text('Tags:')])
    layout.append([])
    c += 2
    r = 0
    for tag in alltags:
        layout[c].append(sg.Button(button_text=tag, key='TAG-' + tag))
        if (r < 6):
            r += 1
        else:
            r = 0
            c += 1
            layout.append([])

    layout.append([sg.Text('___________')])
    layout.append([
        [sg.Button('Add Tag', key='-AddTag-'), sg.Button('Add Tag to cards', key='-AddTagC-')]
    ])

    return sg.Window('Add combo', layout, finalize=True)

def makeAddTagsWindow():
    layout = []
    layout.append([sg.Text('Monster Cards to add tags to')])
    layout.append([])
    c = 1
    r = 0
    for card in allcards:
        #layout[c].append(sg.Text(text=card, key='CARD-' + card))
        layout[c].append(sg.Checkbox(text=card, key="CHECKCard-" + card))
        if (r < 6):
            r += 1
        else:
            r = 0
            c += 1
            layout.append([])

    #
    layout.append([sg.Text('Tags to add to monster cards:')])
    layout.append([])
    c += 2
    r = 0
    for tag in alltags:
        #layout[c].append(sg.Text(text=tag, key='TAG-' + tag))
        layout[c].append(sg.Checkbox(text=tag, key="CHECKTag-" + tag))
        if (r < 6):
            r += 1
        else:
            r = 0
            c += 1
            layout.append([])
    layout.append([
        [sg.Button('Done', key='-MatchTagsDone-')]
    ])
    return sg.Window('Add tags to cards', layout, finalize=True)
def makeTagsWindow():
    layout = []
    layout.append([])
    c = 0
    r = 0
    for tag in alltags:
        layout[c].append(sg.Button(button_text=tag, key='TAG-' + tag))
        if (r < 6):
            r += 1
        else:
            r = 0
            c += 1
            layout.append([])
    return sg.Window('Add tag to combo', layout, finalize=True, location=(0, 50))

if __name__ == '__main__':
    fname = "deck/RealDeck2LessDoll.ydk"
    fnameImg = "img/"
    main = []
    maind = False
    mainReady = {}
    images = {}
    tags = {}
    combos = []
    prot = []
    ht = []
    cardnum = 0
    combosofar = ""
    alltags = []
    allcards = []

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
            datalist = response_list["data"][0]
            cardname = datalist['name'].replace(" ", "")
            if cardname in mainReady:
                mainReady[cardname] = mainReady[cardname] + 1
            else:
                mainReady[cardname] = 1
                images[cardname] = x
                tags[cardname] = datalist['type']
                if 'attribute' in datalist:
                    tags[cardname] += " " + datalist['attribute']
                if 'archetype' in datalist:
                    tags[cardname] += " " + datalist['archetype']
                    if 'Monster' in datalist['type']:
                        tags[cardname] += " " + datalist['archetype']+"Monster"
                    if 'Spell' in datalist['type']:
                        tags[cardname] += " " + datalist['archetype']+"Spell"
                    if 'Trap' in datalist['type']:
                        tags[cardname] += " " + datalist['archetype']+"Trap"
                if cardname in htlist:
                    tags[cardname] += " Handtrap"
                if cardname in seclist:
                    tags[cardname] += " GoingSecond"
                if cardname in protlist:
                    tags[cardname] += " Prot"

        for key in tags:
            all = tags[key].split()
            for a in all:
                if not (a in alltags):
                    alltags.append(a)
        print(alltags)
        for card in mainReady:
            allcards.append(card.replace(" ", ""))
        print(allcards)
        # print(main)
        # + response_list["data"][0]['race'] + response_list["data"][0]['attribute'] + response_list["data"][0]['archetype']
        # print(len(main))
        # print(mainReady)
        print(tags)
        cardnum = len(main)
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
            #layout[c].append(sg.Checkbox(text="", default=False, key="CB-" + card, tooltip=card))

            n += 1
            if (n == 8):
                n = 0
                layout.append([])
                c += 1


        layout[c].append(sg.Button('Add Combo', enable_events=True, key='-SETLAUNCHER-'))
        layout[c].append(sg.Button('Show Combos', enable_events=True, key='S'))
        layout[c].append(sg.Button('Remove Newest Combo', enable_events=True, key='R'))
        #layout.append([])
        #layout[c+1].append(sg.Button('Add protection cards', enable_events=True, key='P'))
        #layout[c+1].append(sg.Button('Show protection cards', enable_events=True, key='SR'))
        #layout[c+1].append(sg.Button('Remove protection cards', enable_events=True, key='PR'))
        #layout.append([])
        #layout[c + 2].append(sg.Button('Add Handtraps', enable_events=True, key='HT'))
        #layout[c + 2].append(sg.Button('Show Handtraps', enable_events=True, key='SHT'))
        #layout[c + 2].append(sg.Button('Remove Handtraps', enable_events=True, key='RHT'))
        layout.append([])
        layout[c+1].append(sg.Button('Execute', enable_events=True, key='EXEC'))
        layout.append([])
        layout[c+2].append(sg.Button('Quit', enable_events=True, key='Q'))
        window = sg.Window('Card Display', layout, finalize=True)
        cwindow = None
        cwindowCombo = None
        cwindowTag = None


        while True:  # Event Loop
            window, event, values = sg.read_all_windows()
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
            if event == 'HT':
                for row in layout:
                    for element in row:
                        if (element.key):
                            if (element.key).startswith("CB-"):
                                #print(element.key + str(element.get()))
                                if element.get():
                                    if (element.key[3:]) not in ht:
                                        ht.append(element.key[3:])
                                    element.update(value=False)
            if event == 'SHT':
                print(ht)
            if event == 'RHT':
                ht = []
            if event == 'EXEC':
                print(cardnum)
                cards = "\n"
                poss = "\n"
                protec = "\n"
                handtr = "\n"
                for comb in combos:
                    poss += comb + "\n"
                for pr in prot:
                    protec += pr.replace(" ", "") + "\n"
                for h in ht:
                    handtr += h.replace(" ", "") + "\n"
                for c in mainReady:
                    cards += (c.replace(" ", "") + " " + str(mainReady[c])) + " " + tags[c]
                    cards += "\n"
                print("Your chance of opening a starter:")
                #print(cards)
                basicsim.run_sim(cardnum, 5, cards, poss, 10000)
                withht = ""
                withpt = ""
                withboth = ""
                tmp = 0
                for line in poss.splitlines():
                    if(tmp == 0):
                        tmp+=1
                    else:
                        withht += line.rstrip() + " AND GoingSecond\n"
                        withpt += line.rstrip() + " AND Prot\n"
                        withboth += line.rstrip() + " AND Prot AND GoingSecond\n"
                #print(cards)
                #print(withht)
                print("Your chance of opening a starter and a going second:")
                basicsim.run_sim(cardnum, 5, cards, withht, 10000)
                print("Your chance of opening a starter and a protection card:")
                basicsim.run_sim(cardnum, 5, cards, withpt, 10000)
                print("Your chance of opening a starter and a going second and a protection card:")
                basicsim.run_sim(cardnum, 5, cards, withboth, 10000)
            elif event == '-SETLAUNCHER-' and not cwindow:
                cwindow = makeComboWindow()
                combosofar = ""
            elif event == '-SEXIT-':
                cwindow = None
            elif event == '-AddC-':
                cwindowCombo = makeCardsWindow()
            elif event == '-AddT-':
                cwindowTag = makeTagsWindow()
            elif event == '-AddA-':
                combosofar += "AND "
                cwindow.Element('COMBO').update(combosofar)
            elif event == '-AddD-':
                if(len(combosofar) > 0):
                    combos.append(combosofar)
                    combosofar = ""
                    cwindow.Element('COMBO').update(combosofar)
            elif event == '-AddClear-':
                combosofar = ""
                cwindow.Element('COMBO').update(combosofar)
            elif event.startswith('TAG-'):
                combosofar += event.replace('TAG-', "") + " "
                cwindowTag = None
                cwindow.Element('COMBO').update(combosofar)
            elif event.startswith('CARD-'):
                combosofar += event.replace('CARD-', "") + " "
                cwindowCombo = None
                cwindow.Element('COMBO').update(combosofar)
            elif event == '-AddPlus-':
                combosofar += str(cwindow.Element('-AddNumber-').get()) + " + "
                cwindow.Element('COMBO').update(combosofar)
            elif event == '-AddMinus-':
                combosofar += str(cwindow.Element('-AddNumber-').get()) + " - "
                cwindow.Element('COMBO').update(combosofar)
            elif event == '-AddEqual-':
                combosofar += str(cwindow.Element('-AddNumber-').get()) + " = "
                cwindow.Element('COMBO').update(combosofar)
            elif event == '-AddTag-':
                newtag = sg.popup_get_text('New tag name:')
                alltags.append(newtag)
                cwindow = makeComboWindow()
            elif event == '-AddTagC-':
                cwindowCombo = makeAddTagsWindow()
            elif event == '-MatchTagsDone-':
                tagTemp = []
                cardTemp = []
                for e in cwindowCombo.element_list():
                    if isinstance(e, sg.Checkbox):
                        if e.get():
                            if('CHECKCard' in e.key):
                                print(e.Text)
                                cardTemp.append(e.Text)
                            if ('CHECKTag' in e.key):
                                print(e.Text)
                                tagTemp.append(e.Text)
                print(tagTemp)
                print(cardTemp)

                for card in cardTemp:
                    for tag in tagTemp:
                        if not tag in tags[card]:
                            tags[card] += " " + tag

                print(tags)