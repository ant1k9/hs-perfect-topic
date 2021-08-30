#!/usr/bin/env python

import bs4
import glob
import json
import os
import requests
import time


API_KEY = os.getenv('ANTIPLAGIAT_API_KEY')
TOOL = 'antiplagiat-online'

reports = [f.replace('./report/', '') for f in glob.glob('./report/*.json')]
topics = [f.replace('./data/', '') for f in glob.glob('./data/*.json')]


def validate(topic: str) -> None:
    start = time.time()

    text: str
    with open(f'./data/{topic}', 'r') as rfile:
        content = json.load(rfile)['steps'][0]['block']['text']
        text = bs4.BeautifulSoup(content, features='lxml').text
        text = text[4:] if text.startswith('</p>') else text
        text = text[5:] if text.startswith('</ul>') else text

    response = requests.post(
        f'https://be1.ru/api/tools/add-task?apikey={API_KEY}',
        data={'tool': TOOL, 'text': text[:10000]}
    )
    print(response.json())
    slug = response.json()['slug']

    print(f'time spent to get slug={slug}: {time.time() - start}')

    for _ in range(100):
        result = requests.get(
            f'https://be1.ru/api/tools/get-result?apikey={API_KEY}&tool={TOOL}&slug={slug}',
        )
        if not result.json().get('result'):
            print(f'time spent position={result.json().get("position")}: {time.time() - start}')
            time.sleep(.2)
            continue
        print(f'time spent to get final result: {time.time() - start}')
        with open(f'./report/{topic}', 'wb') as out:
            out.write(result.content)
        break


for topic in [topic for topic in topics if topic not in reports][:85]:
    validate(topic)
