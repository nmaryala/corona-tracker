import datetime
import json
import requests
import argparse
import logging
from bs4 import BeautifulSoup
from tabulate import tabulate
from slack_client import slacker

FORMAT = '[%(asctime)-15s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG, filename='bot.log', filemode='a')

URL = 'https://www.worldometers.info/coronavirus/country/us/'
SHORT_HEADERS = [ 'State','Total','New','Death','NewDeath','Act']
FILE_NAME = 'corona_us_data.json'
extract_contents = lambda row: [x.text.replace('\n', '') for x in row]


def save(x):
    with open(FILE_NAME, 'w') as f:
        json.dump(x, f)


def load():
    res = {}
    with open(FILE_NAME, 'r') as f:
        res = json.load(f)
    return res
    

if __name__ == '__main__':
   
    parser  = argparse.ArgumentParser()
    parser.add_argument('--states', default=',')
    args = parser.parse_args()
    interested_states = args.states.split(',')
    
    current_time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    info = []

    try:
        response = requests.get(URL).content
        soup = BeautifulSoup(response, 'html.parser')
        header = extract_contents(soup.tr.find_all('th'))
        header = header[:-1]

        stats = []
        all_rows = soup.find_all('tr')
        visited = set()
        for row in all_rows[:63]:
            stat = extract_contents(row.find_all('td'))
            if stat:
                if any([s.lower() in stat[0].lower() for s in interested_states]):
                    if stat[0] not in visited:
                        visited.add(stat[0])
                        stats.append(stat[:6])
        
        past_data = load()
        for xi in stats:
            for i in range(len(xi)):
                xi[i] = xi[i].strip()



        cur_data = {x[0] : {current_time: x[1:]} for x in stats}
        # print(stats[1])
   
        changed = False

        for state in cur_data:
            if state not in past_data:
                # new state has emerged
                info.append(f'NEW_STATE {state} got corona virus: {cur_data[state][current_time]}')
                past_data[state] = {}
                changed = True
            else:
                past = past_data[state]['latest']
                cur = cur_data[state][current_time]
                if past != cur:
                    changed = True
                    info.append(f'Change for {state}: {past}->{cur}')
        
        events_info = ''
        for event in info:
            logging.warning(event)
            events_info += '\n - ' + event.replace("'", "")

        if changed:
            # override the latest one now
            for state in cur_data:
                past_data[state]['latest'] = cur_data[state][current_time]
            save(past_data)

            table = tabulate(stats, headers=SHORT_HEADERS, tablefmt='psql')
            slack_text = f'Please find CoronaVirus Summary for the United States below:\n{events_info}\n```{table}```'
            print(slack_text)
            slacker()(slack_text)
    except Exception as e:
        logging.exception('oops, corono script failed.')
        # slacker()(f'Exception occured: [{e}]')
        print(e)