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
    '/bucket/(.*)', 'BucketController'
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
    def GET(self, name):
        """Get the value if key is provided, otherwise return list of keys
        """
        if len(name) <= 0:            
            result = self.datastore.get_keys()                
        else:
            result = self.datastore.get_value(str(name))
        return {'message' : result}

    @mimerender(
        default = 'html',
        html = render_html,
        xml  = render_xml,
        json = render_json,
        txt  = render_txt
    )        
    def PUT(self, name):
        self.datastore.set_value(str(name), web.data())
        web.created()
        web.header('Location', '/bucket/{0}'.format(str(name)))
        return {'message' : str(name)}

    @mimerender(
        default = 'html',
        html = render_html,
        xml  = render_xml,
        json = render_json,
        txt  = render_txt
    )        
    def DELETE(self, name):
        self.datastore.delete(str(name))
        return {'message' : 'deleted'}
        
if (not is_test()) and __name__ == "__main__":   
    app.run()
