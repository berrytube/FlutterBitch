# coding=utf-8
"""
admin.py - Willie Bugzilla Module
Copyright © 2013, Edward Powell, embolalia.net
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net/
"""
from lxml import etree
import re
from willie import web
import urllib
import urllib2


def configure(config):
    """

    | [bugzilla] | example | purpose |
    | ---- | ------- | ------- |
    | domains | bugzilla.redhat.com,bugzilla.mozilla.org | A list of Bugzilla issue tracker domains |
    """
    if config.option('Show extra information about Bugzilla issues', False):
        config.add_section('bugzilla')
        config.add_list('bugzilla', 'domains',
                        'Enter the domains of the Bugzillas you want extra '
                        'information from. (e.g. bugzilla.mozilla.org)',
                        'Domain:')


def setup(willie):
    regexes = []
    if not (willie.config.has_option('bugzilla', 'domains')
            and willie.config.bugzilla.get_list('domains')):
        return
    if not willie.memory.contains('url_callbacks'):
        willie.memory['url_callbacks'] = {}

    domains = '|'.join(willie.config.bugzilla.get_list('domains'))
    regex = re.compile((r'https?://(%s)'
                         '(/show_bug.cgi\?\S*?)'
                         '(id=\d+)')
                       % domains)
    willie.memory['url_callbacks'][regex] = show_bug


def show_bug(willie, trigger, match=None):
    """Show information about a Bugzilla bug."""
    match = match or trigger
    domain = match.group(1)
    if domain not in willie.config.bugzilla.get_list('domains'):
        return
    url = 'https://%s%sctype=xml&%s' % match.groups()
    data = web.get(url)
    bug = etree.fromstring(data).find('bug')

    message = ('[BUGZILLA] %s | Product: %s | Component: %s | Version: %s | ' +
               'Importance: %s |  Status: %s | Assigned to: %s | ' +
               'Reported: %s | Modified: %s')

    resolution = bug.find('resolution')
    if resolution is not None and resolution.text:
        status = bug.find('bug_status').text + ' ' + resolution.text
    else:
        status = bug.find('bug_status').text

    message = message % (
        bug.find('short_desc').text, bug.find('product').text,
        bug.find('component').text, bug.find('version').text,
        (bug.find('priority').text + ' ' + bug.find('bug_severity').text),
        status, bug.find('assigned_to').text, bug.find('creation_ts').text,
        bug.find('delta_ts').text)
    willie.say(message)
show_bug.rule = (r'.*https?://(\S+?)'
                  '(/show_bug.cgi\?\S*?)'
                  '(id=\d+).*')
