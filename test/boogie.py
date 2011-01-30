import httplib2

id = '4454'
data = 'hello worlddd'
database = 'canonicalbucket'
action = 'GET'
base_url = 'http://localhost:8080'

def url(id):
    return '/'.join([base_url, database, id])
#
"NOT FOUND"
h = httplib2.Http()
resp, content = h.request(url(id), action, data)
print resp
print content

"ALL KEYS"
resp, content = h.request(url(''), action, data)
print resp
print content

"GET 555"
resp, content = h.request(url(id), action, data)
print resp
print content

"PUT 555"
id = '555'
resp, content = h.request(url(id), 'PUT', 'hello')
print resp
print content

"GET 555"
resp, content = h.request(url(id), action, data)
print resp
print content

"""delete"""
id = "555"
resp, content = h.request(url(id), 'DELETE', 'hello')
print resp
print content

"""bad request"""
id = "".join(map(str, range(40)))
resp, content = h.request(url(id), 'PUT', 'hello')
print resp
print content
        
"""delete, not found"""
id = "551"
resp, content = h.request(url(id), 'DELETE', 'hello')
print resp
print content
        
