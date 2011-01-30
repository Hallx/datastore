import web
import inspect
import ConfigParser
import uuid
import random
from MySQLdb import OperationalError


def retry_decorator(fn):
        """Decorator for methods that needs to be retried with different 
        back-end servers if the original one goes away        
        """
        def new_function(*args):
            #TODO: get this value from config - partitions
            tries = 5
            while True:
                try:
                    if tries <= 0:
                        raise web.internalerror()               
                    return fn(*args)
                except OperationalError, e:
                    if e[0] == 2006:    #In case, server has gone away, retry with another server
                        tries -= 1
                        continue
        new_function.__name__ = fn.__name__
        return new_function

class DataStore:
    """DataStore handles the communication with nodes
    
    
    Update flag has three values
        0: The data row is all synced
        1: The data row is updated and waiting to be synced
        2: The data row is marked to be deleted
    """
    def __init__(self, test_env=0):
        config = ConfigParser.SafeConfigParser()
        config.read('configuration.cfg')
        
        self.key_length = config.getint('store', 'key_length')
        self.table_name = config.get('store', 'table_name')
        self.partitions = config.getint('store', 'partitions')       
        self.index = 0 
        
        if test_env:
            web.config.debug = False
            base_name = 'test_'
        else:
            base_name = ''
        self.databases = self.connect_to_databases(config, base_name)
        
    def connect_to_databases(self, config, base_name):
        databases = []
        for id in range(self.partitions):
            section = 'partition-' + str(id)
            database_name = ''.join([base_name, config.get(section, 'name')])            
            database = web.database(dbn='mysql', host=config.get(section, 'host'), 
                                     user=config.get(section, 'user'), 
                                     pw=config.get(section, 'password'), 
                                     db=database_name)
            databases.append(database)
        return databases

    def get_canonical_database(self, uuid):
        """Get the canonical database handler for the uuid 
        """
        index = int(int(uuid, 16) % self.partitions)
        return self.databases[index]
    
    def get_random_database(self):
        """Get a random database handler on the first invocation.
        Subsequent calling of the method returns next database handler.
        Raises internal error on exhaustion of handlers. 
        """
        if not self.index:
            self.index = random.randint(0, self.partitions-1)
        else:
            self.index = int((self.index + 1) % self.partitions)
        return self.databases[self.index]

    def get_unique_identifier(self, key):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, key).hex)
            
    def check_key_length(self, key):
        if len(key) > self.key_length:
            raise web.badrequest() 
    
    def is_key(self, database, key):
        result = database.select(self.table_name, what='id', 
                                 where='id = $key and update_flag<>2', limit=1, vars=locals())
        for r in result:
            return r.id
            
    @retry_decorator
    def get_keys(self):
        database = self.get_random_database()
        keys = []
        for key in database.select(self.table_name, what='id', where='update_flag<>2'):
            keys.append(str(key.id))    
        #TODO: Need to put this in an after-decorator
        self.index = 0      
        return keys
    
    def get_keys_from_all(self):
        keys = set()
        for database in self.databases:
            for key in database.select(self.table_name, what='id', where='update_flag<>2'):
                keys.add(str(key.id))
        return list(keys)
        
    @retry_decorator
    def get_value(self, key):
        database = self.get_random_database()
        result = database.select(self.table_name, what='value', 
                                 where='id = $key and update_flag<>2', limit=1, vars=locals())    
        #TODO: Need to put this in an after-decorator
        self.index = 0
        #TODO: remove loop and just get the first value                
        for r in result:
            return r.value
        raise web.notfound()
        
    def get_canonical_value(self, key):
        uuid = self.get_unique_identifier(key)
        database = self.get_canonical_database(uuid)
        result = database.select(self.table_name, what='value', 
                                 where='id = $key and update_flag<>2', limit=1, vars=locals())
        for r in result:    
            return r.value
        raise web.notfound()
        
    def set_value(self, key, value):
        self.check_key_length(key)
        uuid = self.get_unique_identifier(key)
        database = self.get_canonical_database(uuid)
        try:
            #Update flag = 1 depicts that value has been updated but not synced yet 
            database.delete(self.table_name, where='id = $key', vars=locals())
            return database.insert(self.table_name, id=key, value=value, uuid=uuid, update_flag=1,
                                            updated_at=web.SQLLiteral('NOW()'))            
        except:
            raise web.internalerror()
    
    def set_value_in_all(self, key, value):
        self.set_value(key, value)
        uuid = self.get_unique_identifier(key)
        try:
            for database in self.databases:
                database.delete(self.table_name, where='id = $key', vars=locals())
                database.insert(self.table_name, id=key, value=value, uuid=uuid, update_flag=0,
                                            updated_at=web.SQLLiteral('NOW()'))
        except:
                raise web.internalerror()
        return
    
    def delete(self, key):
        self.check_key_length(key)
        uuid = self.get_unique_identifier(key)
        database = self.get_canonical_database(uuid)
        if not self.is_key(database, key):
            raise web.notfound()
        try:
            #Update flag = 2 depicts that value has been marked as delete but not synced yet
            database.update(self.table_name, where='id = $key', update_flag= 2, 
                            updated_at=web.SQLLiteral('NOW()'), vars=locals())
            return
        except:
            raise web.internalerror()

    def delete_in_all(self, key):
        self.delete(key)
        try:
            for database in self.databases:
                #Update flag = 2 depicts that value has been marked as delete but not synced yet
                database.update(self.table_name, where='id = $key', update_flag= 2, 
                            updated_at=web.SQLLiteral('NOW()'), vars=locals())
        except:
                raise web.internalerror()
        return
