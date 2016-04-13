# -*- coding: utf-8 -*-
from selenium import webdriver
import time
import pandas

def format_df(df, cat):
    'helper function to drop some useless columns and group other columns'
    # first drop Gem, Level, Time, and Combat specs
    df = df.drop(['Gem', 'Level', 'Combat', 'Time'], 1)

    # get the rest of the column names & make a list of tuples needed in
    # multi-indexing
    columns = [(cat, col) for col in df.columns]

    # group the columns into the category
    df.columns = pandas.MultiIndex.from_tuples(columns)

    return df

def reset_page(page, url):
    page.get(url)
    time.sleep(.2)
    page.find_element_by_class_name('scroll').click()
    time.sleep(.2)
    page.find_element_by_class_name('ion-eye').click()
    time.sleep(.2)
    return page.find_elements_by_class_name('my-largeText')

def get_tank_specs(tanks, browser, path='', driver_path=''):
    '''
    Navigate to ironforcemods.com & scrape website using selenium.
    Store the specs of the desired tank(s) in an excel spreadsheet which will
    be named "TANK_NAME.xls"
    tanks = string name of tank or list eg "VULPECULA" or ["DORADO", "PAVO"]
    browser = "firefox" or "chrome"
    path = directory path to save spreadsheets
    driver_path = path of chrome driver if using chrome
    '''
    if type(tanks) == str:
        tanks = [tanks]

    if browser == 'firefox':
        page = webdriver.Firefox()
    elif browser == 'chrome':
        page = webdriver.Chrome(driver_path)

    url = 'http://ironforcemods.com/IFTUC/#/tankList'

    # navigate to web page and get list of clickable pages
    tank_pages = reset_page(page, url)

    # links to click on in the tank page
    upgrades = ['turret', 'barrel', 'armor', 'engine', 'tracks']

    for t in range(len(tanks)):
        # dictionary that holds the specs
        specs_data = {'turret': {'Level': [], 'Attack': [], 'FS': [], 'Combat': [], 'Price': [], 'Time': [], 'Gem': []},
                      'barrel': {'Level': [], 'Attack': [], 'FS': [], 'Combat': [], 'Price': [], 'Time': [], 'Gem': []},
                      'armor': {'Level': [], 'Armor': [], 'Move.': [], 'Combat': [], 'Price': [], 'Time': [], 'Gem': []},
                      'engine': {'Level': [], 'Move.': [], 'Combat': [], 'Price': [], 'Time': [], 'Gem': []},
                      'tracks': {'Level': [], 'Armor': [], 'Move.': [], 'Combat': [], 'Price': [], 'Time': [], 'Gem': []}}

        # get a new list of tank_pages, cuz this shit page is lame
        i = 1
        while i < len(tank_pages):
            # list of clickable pages, most are tanks some aren't
            tank_page = tank_pages[i]

            # For some reason the S-Mono page doesn't want to be clicked, use a try
            # statement
            try:
                tank_page.click()
                page_text = tank_page.text
                #print page_text

            except:
                page_text = 'error'

            if page_text in tanks:
                # Since we're iterating through a list of pages, check to see
                # if the page text exists in the desired list of tanks then
                # remove that item from the list as the list of desired tanks
                # may not match the order of the list of webpages.
                tanks.remove(page_text)
                print 'found specs for', page_text

                for upgrade_link in upgrades:
                    print 'getting specs for %s' % upgrade_link

                    # click on upgrade link
                    page.find_element_by_class_name(upgrade_link).click()

                    # get text of specs from page, it is the 1st item in the list
                    page_data = page.find_elements_by_class_name('list-inset')
                    for j in page_data:
                        if '1' in j.text:
                            raw_specs = j.text
                            break

                    # split by next line delimiter & start at 7th item, first 7
                    # items are the table header, for engine it's 6
                    if upgrade_link == 'engine':
                        headers = raw_specs.split('\n')[:6]
                        raw_specs = raw_specs.split('\n')[6:]
                    else:
                        headers = raw_specs.split('\n')[:7]
                        raw_specs = raw_specs.split('\n')[7:]

                    # turret spces: level, attack, fs, combat, price, time, gem
                    # barrel specs: level, attack, fs, combat, price, time, gem
                    # armor specs: level, armor, move., combat, price, time, gem
                    # engine spces: level, move., combat, price, time, gem
                    # tracks specs: level, armor, move., combat, price, time, gem
                    for data, header in zip(raw_specs, headers*(len(raw_specs)/len(headers))):
                        specs_data[upgrade_link][header].append(data)

                break

            # The list of tanks needs to be refreshed every time or else an error comes back
            tank_pages = reset_page(page, url)
            i += 1

        print 'making %s spreadsheet' % page_text

        turret = pandas.DataFrame(specs_data['turret'],
                                  index=specs_data['turret']['Level'])
        barrel = pandas.DataFrame(specs_data['barrel'],
                                  index=specs_data['turret']['Level'])
        armor = pandas.DataFrame(specs_data['armor'],
                                 index=specs_data['turret']['Level'])
        engine = pandas.DataFrame(specs_data['engine'],
                                  index=specs_data['turret']['Level'])
        tracks = pandas.DataFrame(specs_data['tracks'],
                                  index=specs_data['turret']['Level'])

        upgrade_time = turret.Time
        upgrade_time = upgrade_time.to_frame('Time')
        upgrade_time.columns = pandas.MultiIndex.from_tuples([('Upgrade Time',
                                                               'Time')])

        turret = format_df(turret, 'turret')
        barrel = format_df(barrel, 'barrel')
        armor  = format_df(armor, 'armor')
        engine = format_df(engine, 'engine')
        tracks = format_df(tracks, 'tracks')

        specs_df = pandas.concat([turret, barrel, armor, engine, tracks, upgrade_time], axis=1)
        specs_df.to_excel('%s%s.xls' % (path, page_text))

    page.close()
    print 'done.'


# testing
if 0:
    # get one tank
    get_tank_specs('CENTAURUS', 'chrome', 'test/', 'C:\Users\mdegaetano\Desktop\chromedriver.exe')

if 0:
    # get two tanks
    get_tank_specs(['PAVO', 'DORADO'], 'chrome',
                   driver_path='C:\Users\mdegaetano\Desktop\chromedriver.exe')

if 1:
    # get all tank spreadsheets
    # this is a list of pages that should not be included in the tanks list
    crap = ['Tank List', 'Technology', 'Maps', 'Ranks']

    page = webdriver.Chrome('C:\Users\mdegaetano\Desktop\chromedriver.exe')
    url = 'http://ironforcemods.com/IFTUC/#/tankList'
    tank_pages = reset_page(page, url)

    tanks = [p.text for p in tank_pages if p.text not in crap]

    # need to figure out why the S MONO page won't work
    tanks.remove('S.MONOCEROS')
    page.close()

    get_tank_specs(tanks, 'chrome', 'tank_spreadsheets/',
                   driver_path='C:\Users\mdegaetano\Desktop\chromedriver.exe')


