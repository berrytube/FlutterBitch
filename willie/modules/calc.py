# coding=utf-8
"""
calc.py - Willie Calculator Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://willie.dfbta.net
"""

import re
import willie.web as web
from socket import timeout
import string
import HTMLParser
import random

def calculate(q):
    q = q.encode('utf8')
    q = q.replace('\xcf\x95', 'phi')  # utf-8 U+03D5
    q = q.replace('\xcf\x80', 'pi')  # utf-8 U+03C0
    uri = 'http://www.google.com/ig/calculator?q='
    bytes = web.get(uri + web.quote(q))
    parts = bytes.split('",')
    answer = [p for p in parts if p.startswith('rhs: "')][0][6:]
    if answer:
        answer = answer.decode('unicode-escape')
        answer = ''.join(chr(ord(c)) for c in answer)
        answer = answer.decode('utf-8')
        answer = answer.replace(u'\xc2\xa0', ',')
        answer = answer.replace('<sup>', '^(')
        answer = answer.replace('</sup>', ')')
        answer = web.decode(answer)
        return answer
    else:
        return 'No result.'


def c(willie, trigger):
    """Google calculator."""
    if not trigger.group(2):
        return willie.reply("Hmph. Garbage.")
    result = calculate(trigger.group(2))
    if result == 'No result.':
        willie.reply("Hmph. Garbage.")
    else:
        responses = [
            "It's %s. You should really go back and finish your GED.",
            "%s, stupidhead",
            "Really? It's %s.",
            "%s. Now leave me alone.",
            "%s, obviously.",
            "%s. Literally third grade math.",
            "%s, I didn't even have to look that one up.",
            "Seriously? %s. Wow.",
            "%s. I'd explain to you how I got that result, but neither one of us would survive the attempt."
        ]
        willie.reply(random.choice(responses) % result)
c.commands = ['c', 'calc']
c.example = '.c 5 + 3'

def wa(willie, trigger):
    """Wolfram Alpha calculator"""
    if not trigger.group(2):
        return willie.reply("No search term.")
    query = trigger.group(2)
    uri = 'http://tumbolia.appspot.com/wa/'
    try:
        answer = web.get(uri + web.quote(query.replace('+', '%2B')), 45)
    except timeout as e:
        return willie.say('Request timed out')
    if answer:
        answer = answer.decode('string_escape')
        answer = HTMLParser.HTMLParser().unescape(answer)
        #This might not work if there are more than one instance of escaped
        #unicode chars But so far I haven't seen any examples of such output
        #examples from Wolfram Alpha
        match = re.search('\\\:([0-9A-Fa-f]{4})', answer)
        if match is not None:
            char_code = match.group(1)
            char = unichr(int(char_code, 16))
            answer = answer.replace('\:' + char_code, char)
        waOutputArray = string.split(answer, ";")
        if(len(waOutputArray) < 2):
            willie.say('[Wolfram Error]' + answer)
        else:

            willie.say('[Wolfram] ' + waOutputArray[0] + " = "
                       + waOutputArray[1])
        waOutputArray = []
    else:
        willie.reply('No result, jerkface.')
wa.commands = ['wa', 'wolfram', 'wolf']
wa.example = '.wa circumference of the sun * pi'

if __name__ == '__main__':
    print __doc__.strip()
