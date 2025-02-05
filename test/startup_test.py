import unittest

import semantic_version

from biokbase.catalog.Impl import Catalog
from catalog_test_util import CatalogTestUtil


# tests all the basic get methods
class StartupTest(unittest.TestCase):

    def test_startups(self):
        # Test normal startup, should work
        self.cUtil.setUp()
        catalog = Catalog(self.cUtil.getCatalogConfig())
        self.assertTrue(semantic_version.validate(catalog.version(self.cUtil.anonymous_ctx())[0]))

        # Test empty startup without DB version should work
        self.cUtil.setUpEmpty()
        catalog = Catalog(self.cUtil.getCatalogConfig())
        self.assertTrue(semantic_version.validate(catalog.version(self.cUtil.anonymous_ctx())[0]))

        # Test empty startup with several different valid versions should work
        self.cUtil.setUpEmpty(db_version=3)
        catalog = Catalog(self.cUtil.getCatalogConfig())
        self.assertTrue(semantic_version.validate(catalog.version(self.cUtil.anonymous_ctx())[0]))

        self.cUtil.setUpEmpty(db_version=4)
        catalog = Catalog(self.cUtil.getCatalogConfig())
        self.assertTrue(semantic_version.validate(catalog.version(self.cUtil.anonymous_ctx())[0]))

        # Startup with version that is too high should fail
        self.cUtil.setUpEmpty(db_version=2525)

        catalog = None
        ctx = self.cUtil.user_ctx()
        user = ctx['user_id']
        with self.assertRaises(IOError) as e:
            catalog = Catalog(self.cUtil.getCatalogConfig())
            # Trigger the lazy load collection, which will call the check_db_schema() method.
            catalog.list_favorites(ctx, user)[0]
        self.assertEqual(str(e.exception),
                         'Incompatible DB versions.  Expecting DB V4, found DV V2525. You are '
                         'probably running an old version of the service.  Start up failed.')

    @classmethod
    def setUpClass(cls):
        print('++++++++++++ RUNNING startup_test.py +++++++++++')
        cls.cUtil = CatalogTestUtil('.')  # TODO: pass in test directory from outside

    @classmethod
    def tearDownClass(cls):
        pass
