#!/usr/bin/env python
import sys

from download_post import download_post
if len(sys.argv)==1:
    print 'usage: vkd url'
    exit()

download_post(sys.argv[1])
