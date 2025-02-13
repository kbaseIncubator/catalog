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

    @classmethod
    def setUpClass(cls):
        print('++++++++++++ RUNNING startup_test.py +++++++++++')
        cls.cUtil = CatalogTestUtil('.')  # TODO: pass in test directory from outside

    @classmethod
    def tearDownClass(cls):
        pass
