#!/usr/bin/env python3

import requests

token = ''
url = f'https://api.telegram.org/bot{token}/sendMessage'
url2 = 'https://www.figma.com/file/7zBxsNv8giffJpKbeIwHTB/UTOR'

FIGMA_TOKEN = ''
head = {'X-Figma-Token': FIGMA_TOKEN}

r = requests.get(url2, headers=head)
print(r)
print(r.content)


