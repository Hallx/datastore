#!/usr/bin/env python

import os
import sys
import MySQLdb
import ConfigParser
import fcntl

class SyncMysql:
    def __init__(self, test_env=0):
        config = ConfigParser.SafeConfigParser()
        config.read('configuration.cfg')
        
        self.table_name = config.get('store', 'table_name')
        self.partitions = config.getint('store', 'partitions')       
        
        if len(sys.argv) > 1 and sys.argv[1] == "test":
            base_name = 'test_'
        else:
            base_name = ""
        self.databases, self.cursors = self.get_database_cursors(config, base_name)
        
    def get_database_cursors(self, config, base_name):
        cursors = []
        databases = []
        for id in range(self.partitions):
            section = 'partition-' + str(id)
            database_name = ''.join([base_name, config.get(section, 'name')])                        
            database = MySQLdb.connect(host=config.get(section, 'host'), 
                                     user=config.get(section, 'user'), 
                                     passwd=config.get(section, 'password'), 
                                     db=database_name)
            database.autocommit(True)
            databases.append(database)
            cursor = database.cursor()
            cursors.append(cursor)
        return databases, cursors
    
    def find_all_keys_with_delete_flag(self, cursor):
        keys = []
        cursor.execute("select id from data where update_flag=2")
        for row in cursor.fetchall():
            keys.append(row[0])
        return keys
    
    def delete_in_all(self, keys):
        for cursor in self.cursors:
            #Instead of loop. It can be much better if one delete statement takes care of it
            for key in keys:
                print "deleting %s in %s" % (key, str(cursor))
                statement = 'DELETE FROM data WHERE id IN (%s)'
                cursor.execute(statement, key)
    
    def get_all_updated_data(self, cursor):
        keys = []
        cursor.execute("select * from data where update_flag=1")
        data = cursor.fetchall()
        for row in data:
            keys.append(row[0])
        return keys, data
    
    def update_data_in_all(self, keys, data):
        for cursor in self.cursors:
            #Instead of loop. It can be much better if one update statement takes care of it
            for row in data:
                print row
                statement = "REPLACE INTO data VALUES %s" % '(%s, %s, %s, %s, %s)'
                cursor.execute(statement, row)
            for key in keys:
                print key
                statement = "UPDATE data SET update_flag=0 WHERE id IN (%s)"
                cursor.execute(statement, key)
        
    def run(self):
        while True:
            pass
        try:
            for cursor in self.cursors:
                keys = self.find_all_keys_with_delete_flag(cursor)
                self.delete_in_all(keys)
                
                keys, data = self.get_all_updated_data(cursor)
                self.update_data_in_all(keys, data)
        except MySQLdb.Error, e:
             print "Error %d: %s" % (e.args[0], e.args[1])
             sys.exit (1)

    def cleanup(self):
        try:
            for cursor in self.cursors:
                cursor.close()
            for database in self.databases:
                database.close()  
        except MySQLdb.Error, e:
             print "Error %d: %s" % (e.args[0], e.args[1])
             sys.exit (1)

def lock_file(lockfile):
    """Make sure only one instance runs
    """
    fp = open(lockfile, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return False
    return True

if __name__ == "__main__":
    if not lock_file(".lock.pid"):
        print "An instance is already running."
        sys.exit(0)
    sync = SyncMysql()
    sync.run() 
    sync.cleanup()
            