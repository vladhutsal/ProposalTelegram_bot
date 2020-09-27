#!/usr/bin/env python3

import requests
import re

token = '64066-66f0e1aa-db0b-4ade-80b5-e7da3e6dd74f'
url = 'https://api.figma.com/v1/files/7zBxsNv8giffJpKbeIwHTB/?node-id=0%3A1'

head = {'X-Figma-Token': token}

r = requests.get(url, headers=head)

with open('figma_info.txt', 'w+') as response:
    response.write(r.text)
