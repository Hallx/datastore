import httplib2

id = '4454'
data = 'hello world'
#database = 'shelve'
database = 'bucket'
#database = 'memory'
#action = 'POST'
action = 'GET'
#action = 'DELETE'
base_url = 'http://localhost:8080'

def url(id):
    return '/'.join([base_url, database, id])
#
h = httplib2.Http()
resp, content = h.request(url(id), action, data)
print resp
print content

resp, content = h.request(url(''), action, data)
print resp
print content


id = '555'
resp, content = h.request(url(id), 'PUT', 'hello')
print resp
print content

id = '555'
resp, content = h.request(url(id), action, data)
print resp
print content


"""bad request"""
id = "".join(map(str, range(40)))
resp, content = h.request(url(id), 'PUT', 'hello')
print resp
print content
        
"""delete"""
id = "551"
resp, content = h.request(url(id), 'DELETE', 'hello')
print resp
print content
        
