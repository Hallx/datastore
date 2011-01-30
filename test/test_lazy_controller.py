from paste.fixture import TestApp
from nose.tools import *
from controller import app

#TODO: fix this test controller
lazy_controller = '/bucket/'
canonical_controller = '/canonicalbucket/'

class TestGET():
    def setUp(self):
        middleware = []
        self.client = TestApp(app.wsgifunc(*middleware))

        self.lazy_url_2 = ''.join([lazy_controller, 'l222'])
        self.lazy_url_3 = ''.join([lazy_controller, 'l223'])     
        canonical_url_1 = ''.join([canonical_controller, 'l221'])
        canonical_url_2 = ''.join([canonical_controller, 'l222'])
        
        self.client.post(canonical_url_1, 'test')   #Propagated to all nodes
        self.client.post(canonical_url_2, 'test')   #Propagated to all nodes

    def test_get_with_no_key_should_return_all_keys_present_in_any_node(self):
        r = self.client.get(lazy_controller)
        assert_equal(r.status, 200)
        r.mustcontain('l222')
        r.mustcontain('l221')

    def test_get_with_valid_key_present_in_all_nodes(self):
        r = self.client.get(self.lazy_url_2)
        assert_equal(r.status, 200)
        r.mustcontain('test')
    
    def test_get_with_invalid_key(self):
        """No Assertion required
        """
        self.client.get(self.lazy_url_3, status=404)

class TestPOST():
    def setUp(self):
        middleware = []
        self.client = TestApp(app.wsgifunc(*middleware))

    def test_set_a_key_value(self):
        lazy_post_url = ''.join([lazy_controller, 'l555'])
        canonical_get_url = ''.join([canonical_controller, 'l555'])
        
        r = self.client.post(lazy_post_url, "testing post method: newly created value")
        assert_equal(r.status, 201)
        r2 = self.client.get(canonical_get_url)
        r2.mustcontain("testing post method: newly created value")

    def test_set_a_key_value_where_key_exists(self):        
        lazy_post_url = ''.join([lazy_controller, 'l655'])
        canonical_url = ''.join([canonical_controller, 'l655'])
        self.client.post(canonical_url, "value exists. over written on canonical. Can be visible in others")
        r2 = self.client.get(canonical_url)
        
        r3 = self.client.post(lazy_post_url, "overwritten the existing value")
        assert_equal(r3.status, 201)
        r4 = self.client.get(canonical_url)
        r4.mustcontain("overwritten the existing value")
    
    def test_long_key_results_error(self):
        """No Assertion required
        """
        key = "".join(map(str, range(40)))
        url_too_long_key = ''.join([lazy_controller, key])
        self.client.post(url_too_long_key, "very very long. longer key than in database. should not get inserted", status=400)
        self.client.get(url_too_long_key, status=404)
        
class TestDELETE():
    def setUp(self):
        middleware = []
        self.client = TestApp(app.wsgifunc(*middleware))

    def test_delete_a_key_value(self):
        lazy_url = ''.join([lazy_controller, 'l777'])
        canonical_url = ''.join([canonical_controller, 'l777'])
        self.client.post(canonical_url, "should have a deleted flag")
        
        self.client.delete(lazy_url, status=202)
        self.client.get(canonical_url, status=404)
        
    def test_cannot_delete_a_non_existing_key_value(self):
        url_xyz = ''.join([lazy_controller, 'lxyz'])
        self.client.delete(url_xyz, status=404)
                
    def test_delete_existing_and_immediately_insert_a_key_value(self):
        lazy_url = ''.join([lazy_controller, 'l737'])
        canonical_url = ''.join([canonical_controller, 'l737'])        
        self.client.post(canonical_url, "will be deleted and over written on canonical. Can be visible in others.")
        
        self.client.delete(lazy_url, status=202)
        self.client.post(lazy_url, "deleted existing. and written a new value")
        r2 = self.client.get(canonical_url)
        r2.mustcontain("deleted existing. and written a new value")
