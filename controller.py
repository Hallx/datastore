import os
import web
import json
from datastore import DataStore
from mimerender import mimerender

render_xml = lambda message: '<message>%s</message>'%message
render_json = lambda **args: json.dumps(args)
render_html = lambda message: '<html><body>%s</body></html>'%message
render_txt = lambda message: message

urls = (
    '/lazybucket/(.*)', 'LazyBucketController',
    '/canonicalbucket/(.*)', 'CanonicalBucketController'
)
app = web.application(urls, globals())

def is_test():
    if 'WEBPY_ENV' in os.environ:
        return os.environ['WEBPY_ENV'] == 'test'
    
class BucketController:
    """Bucket controller processes HTTP verbs
    """
    datastore = DataStore(test_env=is_test())
    @mimerender(
        default = 'html',
        html = render_html,
        xml  = render_xml,
        json = render_json,
        txt  = render_txt
    )
    def _GET(self, key, forceful=False):
        """Get the value if key is provided, otherwise return list of keys
        """
        if len(key) <= 0:
            if forceful:
                result = self.datastore.get_keys_from_all()
                pass
            else:
                result = self.datastore.get_keys()                                
        else:
            if forceful:
                result = self.datastore.get_canonical_value(str(key))
            else:
                result = self.datastore.get_value(str(key))
        return {'message' : result}

    @mimerender(
        default = 'html',
        html = render_html,
        xml  = render_xml,
        json = render_json,
        txt  = render_txt
    )        
    def _PUT(self, key, forceful=False):
        if forceful:
            self.datastore.set_value_in_all(str(key), web.data())
        else:
            self.datastore.set_value(str(key), web.data())
        web.created()
        web.header('Location', '/bucket/{0}'.format(str(key)))
        return {'message' : str(key)}

    @mimerender(
        default = 'html',
        html = render_html,
        xml  = render_xml,
        json = render_json,
        txt  = render_txt
    )        
    def _DELETE(self, key, forceful=False):
        if forceful:
            self.datastore.delete_in_all(str(key))
        else:
            self.datastore.delete(str(key))
        return {'message' : 'deleted'}
    
class LazyBucketController(BucketController):
    """Does not try to get precise read or propagate the writes
    a read can be done on any node. can be slightly stale
    a write to canonical node will propagated lazily
    """
    def GET(self, key):
        return self._GET(key)
    
    def PUT(self, key):
        return self._PUT(key)
    
    def DELETE(self, key):
        return self._DELETE(key)
        
class CanonicalBucketController(BucketController):
    """Every write is propagated to all nodes
    Every read is read from canonical node
    """
    def GET(self, key):
        return self._GET(key, forceful = True)
    
    def PUT(self, key):
        return self._PUT(key, forceful = True)
    
    def DELETE(self, key):
        return self._DELETE(key, forceful = True)    
        
if (not is_test()) and __name__ == "__main__":   
    app.run()
