from paste.fixture import TestApp
from nose.tools import *
from controller import app

controller = '/canonicalbucket/'

class TestGET():
    def setUp(self):
        self.url_1 = ''.join([controller, 'c221'])
        self.url_2 = ''.join([controller, 'c222'])
        
        middleware = []
        self.client = TestApp(app.wsgifunc(*middleware))
        self.client.post(self.url_1, 'test')
        self.client.post(self.url_2, 'test')

    def test_get_with_no_key_should_return_all_keys(self):
        r = self.client.get(controller)
        assert_equal(r.status, 200)
        r.mustcontain('c222')
        r.mustcontain('c221')

    def test_get_with_valid_key(self):
        r = self.client.get(self.url_2)
        assert_equal(r.status, 200)
        r.mustcontain('test')
    
    def test_get_with_invalid_key(self):
        """No Assertion required
        """
        self.url_3 = ''.join([controller, 'c223'])
        self.client.get(self.url_3, status=404)

class TestPOST():
    def setUp(self):
        middleware = []
        self.client = TestApp(app.wsgifunc(*middleware))

    def test_set_a_key_value(self):
        url_225 = ''.join([controller, 'c225'])
        r = self.client.post(url_225, "testing post method:newly set key")
        assert_equal(r.status, 201)
        r.mustcontain("c225")
        r2 = self.client.get(url_225)
        r2.mustcontain("testing post method:newly set key")

    def test_set_a_key_value_where_key_exists(self):
        url_335 = ''.join([controller, 'c335'])
        self.client.post(url_335, "value exists. should have been overwritten.")
        r2 = self.client.get(url_335)
        r2.mustcontain("value exists. should have been overwritten.")
        
        r3 = self.client.post(url_335, "overwritten the existing value")
        assert_equal(r3.status, 201)
        r4 = self.client.get(url_335)
        r4.mustcontain("overwritten the existing value")
    
    def test_long_key_results_error(self):
        """No Assertion required
        """
        key = "".join(map(str, range(40)))
        url_too_long_key = ''.join([controller, key])
        self.client.post(url_too_long_key, "very very long. longer key than in database. should not get inserted", status=400)
        self.client.get(url_too_long_key, status=404)
        
class TestDELETE():
    def setUp(self):
        middleware = []
        self.client = TestApp(app.wsgifunc(*middleware))

    def test_delete_a_key_value(self):
        url_995 = ''.join([controller, 'c995'])        
        self.client.post(url_995, "should have a deleted flag")
        self.client.delete(url_995, status=202)
        self.client.get(url_995, status=404)
        
    def test_cannot_delete_a_non_existing_key_value(self):
        url_xyz = ''.join([controller, 'cxyz'])
        self.client.delete(url_xyz, status=404)
                
    def test_delete_and_immediately_insert_a_key_value(self):
        url_885 = ''.join([controller, 'c885'])
        self.client.post(url_885, "will be deleted and over written")
        self.client.delete(url_885, status=202)
        
        self.client.post(url_885, "deleted existing. and written a new value")
        r2 = self.client.get(url_885)
        r2.mustcontain("deleted existing. and written a new value")
