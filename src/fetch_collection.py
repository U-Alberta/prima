#!/usr/bin/python
import internetarchive
import sys
import time

COLLECTIONFOLDER = "source/"
ERRLOG = "fetch_collection_errors.log"

def fetch():
    error_log = open(ERRLOG ,"a")
    errors = 0
    collection = sys.argv[1]
    search = internetarchive.search_items("collection:"+collection)
    for result in search:
        itemid = result["identifier"]
        item = internetarchive.get_item(itemid)
        try:
            item.download(destdir=COLLECTIONFOLDER)
        except Exception as e:
            error_log.write("Could not download "+itemid+" because of error: %s\n" % e)
            errors+=1
            print "There was an error; writing to log."
        else:
            time.sleep(1)

if __name__ == '__main__':
    fetch()