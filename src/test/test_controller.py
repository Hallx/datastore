from paste.fixture import TestApp
from nose.tools import *
from controller import app

class TestGET():
    def setUp(self):
        middleware = []
        self.client = TestApp(app.wsgifunc(*middleware))
        self.client.put('/bucket/221', 'test')
        self.client.put('/bucket/222', 'test')

    def test_get_with_no_key_should_return_all_keys(self):
        "Extra functionality for now"      
        r = self.client.get('/bucket/')
        assert_equal(r.status, 200)
        r.mustcontain('222')
        r.mustcontain('221')

    def test_get_with_valid_key(self):
        r = self.client.get('/bucket/222')
        assert_equal(r.status, 200)
        r.mustcontain('test')
    
    def test_get_with_invalid_key(self):
        """No Assertion required
        """
        self.client.get('/bucket/223', status=404)

class TestPUT():
    def setUp(self):
        middleware = []
        self.client = TestApp(app.wsgifunc(*middleware))

    def test_set_a_key_value(self):
        r = self.client.put('/bucket/555',"boogie-boo")
        assert_equal(r.status, 201)
        r2 = self.client.get('/bucket/555')
#        assert_equal(r.headers['location'], '/bucket/555')
        r2.mustcontain('boogie-boo')

    def test_set_a_key_value_where_key_exists(self):
        self.client.put('/bucket/555',"boogie-boo")
        r2 = self.client.get('/bucket/555')
        r2.mustcontain('boogie-boo')
        
        r3 = self.client.put('/bucket/555',"noogie-noo")
        assert_equal(r3.status, 201)
        r4 = self.client.get('/bucket/555')        
        r4.mustcontain('noogie-noo')
    
    def test_long_key_results_error(self):
        """No Assertion required
        """
        key = "".join(map(str, range(40)))
        self.client.put('/bucket/'+key,"very very long. longer key than in database", status=400)
        self.client.get('/bucket/'+key, status=404)
        
class TestDELETE():
    def setUp(self):
        middleware = []
        self.client = TestApp(app.wsgifunc(*middleware))

    def test_delete_a_key_value(self):
        self.client.put('/bucket/555',"boogie-boo")
        self.client.delete('/bucket/555')
        self.client.get('/bucket/555', status=404)
        
    def test_cannot_delete_a_non_existing_key_value(self):
        self.client.delete('/bucket/xyz', status=404)
                
    def test_delete_and_immediately_insert_a_key_value(self):
        self.client.put('/bucket/555',"boogie-boo")
        self.client.delete('/bucket/555')
        self.client.put('/bucket/555',"boogie-boo2")
        r2 = self.client.get('/bucket/555')
        r2.mustcontain('boogie-boo2')