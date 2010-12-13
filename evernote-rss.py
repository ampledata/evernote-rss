#!/usr/bin/env python
# $Id$

import sys
import hashlib
import time
import copy
from string import Template

import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types

from twodo_conf import *

def getTODOnotesFromEvernote( todoNotebook=TODO_NOTEBOOK ):
    userStoreHttpClient = THttpClient.THttpClient( USERSTOREURI )
    userStoreProtocol   = TBinaryProtocol.TBinaryProtocol( userStoreHttpClient )
    userStore           = UserStore.Client( userStoreProtocol )
    authResult          = userStore.authenticate( username=USERNAME, password=PASSWORD, consumerKey=CONSUMER_KEY, consumerSecret=CONSUMER_SECRET )
    user                = authResult.user
    authToken           = authResult.authenticationToken
    noteStoreUri        =  NOTESTOREURIBASE + user.shardId
    noteStoreHttpClient = THttpClient.THttpClient( noteStoreUri )
    noteStoreProtocol   = TBinaryProtocol.TBinaryProtocol( noteStoreHttpClient )
    noteStore           = NoteStore.Client( noteStoreProtocol )
    notebooks           = noteStore.listNotebooks( authToken )
    for notebook in notebooks:
        if notebook.name == todoNotebook:
            _filter = NoteStore.NoteFilter( notebookGuid=notebook.guid )
            return noteStore.findNotes( authenticationToken=authToken, filter=_filter, offset=0,maxNotes=100 ).notes

if __name__ == '__main__':
    todoNotes = getTODOnotesFromEvernote()
    rss_out = open('gba.rss','w')
    rss_header = """
<rss version="2.0">
    <channel>
        <title>A Hacker(s) News</title>
        <link>http://gregalbrecht.com/</link>
        <description>Links for me.</description>
"""
    rss_item = """
        <item>
            <title>$title</title>
            <link>$sourceURL</link>
            <comments>$sourceURL</comments>
            <description>
                <![CDATA[<a href="$sourceURL">source URL</a>]]>
            </description>
        </item>
"""
    rss_footer = """
    </channel>
</rss>
"""
    rss_out.write( rss_header )
    for td in todoNotes:
        rss_template = Template( rss_item )
        rss_out.write( rss_template.safe_substitute( title=td.title, sourceURL=td.attributes.sourceURL ) )
    rss_out.write( rss_footer )
    rss_out.close()
