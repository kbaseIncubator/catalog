import unittest
from time import time, sleep

from biokbase.catalog.Impl import Catalog
from biokbase.narrative_method_store.client import NarrativeMethodStore
from catalog_test_util import CatalogTestUtil


# tests all the basic get methods
class LocalFunctionModuleTest(unittest.TestCase):

    # assumes no developers have been added yet
    def test_local_function_module(self):

        # TODO: figure out git_commit hash or branch configuration
        # assume test user is already approved as a developer
        # (1) register the test repo
        giturl = self.cUtil.get_test_repo_1()
        githash = 'a8915afe6811de9199897d710348befad8f6f7ab'  # branch local_method_module
        registration_id = self.catalog.register_repo(self.cUtil.user_ctx(),
                                                     {'git_url': giturl,
                                                      'git_commit_hash': githash})[0]
        timestamp = int(registration_id.split('_')[0])

        # (2) check state until error or complete, must be complete, and make sure this was relatively fast
        start = time()
        timeout = 6000  # seconds
        last_line = 0
        while True:
            sleep(1)
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),
                                                  {'git_url': giturl})[0]

            # log line printing:
            parsed_log = self.catalog.get_parsed_build_log(self.cUtil.anonymous_ctx(),
                                                           {
                                                               'registration_id': registration_id,
                                                               'skip': last_line,
                                                               'limit': 1000
                                                           })[0]
            for l in parsed_log['log']:
                last_line += 1
                if '- Pushing -' in l['content']:
                    continue
                print((l['content']))

            if state['registration'] in ['complete', 'error']:
                break
            self.assertTrue(time() - start < timeout,
                            'simple registration build exceeded timeout of ' + str(timeout) + 's')

        self.assertEqual(state['registration'], 'complete')

        # first try to get the spec without a release tag or commit hash, should default to latest version
        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter',
             'function_id': 'powerpoint_to_genome'}]})[0]

        self.assertEqual(len(specs), 1)
        info = specs[0]['info']
        self.assertEqual(info['function_id'], 'powerpoint_to_genome')
        self.assertEqual(info['git_commit_hash'], 'a8915afe6811de9199897d710348befad8f6f7ab')
        self.assertEqual(info['module_name'], 'GenomeToPowerpointConverter')
        self.assertEqual(info['name'], 'Powerpoint to Genome')
        self.assertEqual(info['release_tag'], ['dev'])
        self.assertIsNotNone(info['kidl'])
        self.assertIsNotNone(info['kidl']['parse'])
        self.assertEqual(specs[0]['long_description'],
                         '<b> some html here </b> <br><br> more here!')

        # trying to get the release tag should not return anything
        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter', 'function_id': 'powerpoint_to_genome',
             'release_tag': 'release'}]})[0]
        self.assertEqual(len(specs), 0)
        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter', 'function_id': 'powerpoint_to_genome',
             'release_tag': 'beta'}]})[0]
        self.assertEqual(len(specs), 0)

        # dev should work, and if we want it twice, then give it twice (right behavior?)
        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter', 'function_id': 'powerpoint_to_genome',
             'release_tag': 'dev'},
            {'module_name': 'GenomeTopowerpointConverter', 'function_id': 'powerpoint_to_genome',
             'release_tag': 'dev'},
        ]})[0]
        self.assertEqual(len(specs), 2)

        # listing released/beta functions should return nothing
        func_list = self.catalog.list_local_functions(self.cUtil.user_ctx(),
                                                      {'release_tag': 'release'})[0]
        self.assertEqual(len(func_list), 0)
        func_list = self.catalog.list_local_functions(self.cUtil.user_ctx(),
                                                      {'release_tag': 'beta'})[0]
        self.assertEqual(len(func_list), 0)
        func_list = self.catalog.list_local_functions(self.cUtil.user_ctx(),
                                                      {})[0]
        self.assertEqual(len(func_list), 0)
        func_list = self.catalog.list_local_functions(self.cUtil.user_ctx(),
                                                      {'module_names': [
                                                          'GenomeTopowerpoIntConverter']})[0]
        self.assertEqual(len(func_list), 0)

        # but listing dev should return something
        func_list = self.catalog.list_local_functions(self.cUtil.user_ctx(),
                                                      {'release_tag': 'dev'})[0]
        self.assertEqual(len(func_list), 2)
        func_list = self.catalog.list_local_functions(self.cUtil.user_ctx(),
                                                      {'release_tag': 'dev', 'module_names': [
                                                          'GenomeTopowerpoIntConverter']})[0]
        self.assertEqual(len(func_list), 2)

        # push things to beta
        self.catalog.push_dev_to_beta(self.cUtil.user_ctx(),
                                      {'module_name': 'GenomeToPowerpointConverter'})

        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter',
             'function_id': 'powerpoint_to_genome'}]})[0]

        self.assertEqual(len(specs), 1)
        info = specs[0]['info']
        self.assertEqual(info['function_id'], 'powerpoint_to_genome')
        self.assertEqual(info['git_commit_hash'], 'a01e1a20b9c504a0136c75323b00b1cd4c7f7970')
        self.assertEqual(info['module_name'], 'GenomeToPowerpointConverter')
        self.assertEqual(info['name'], 'Powerpoint to Genome')
        self.assertEqual(info['release_tag'], ['beta', 'dev'])
        self.assertIsNotNone(info['kidl'])
        self.assertIsNotNone(info['kidl']['parse'])
        self.assertEqual(specs[0]['long_description'],
                         '<b> some html here </b> <br><br> more here!')

        # test out some additional ways to get the results
        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter', 'function_id': 'powerpoint_to_genome',
             'release_tag': 'release'}]})[0]
        self.assertEqual(len(specs), 0)
        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter', 'function_id': 'powerpoint_to_genome',
             'release_tag': 'beta'}]})[0]
        self.assertEqual(len(specs), 1)

        # dev should work, and if we want it twice, then give it twice (right behavior?)
        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter', 'function_id': 'powerpoint_to_genome',
             'release_tag': 'dev'},
            {'module_name': 'GenomeTopowerpointConverter', 'function_id': 'powerpoint_to_genome',
             'release_tag': 'beta'},
        ]})[0]
        self.assertEqual(len(specs), 2)

        # release the thing
        self.catalog.request_release(self.cUtil.user_ctx(),
                                     {'module_name': 'GenomeToPowerpointConverter'})
        self.catalog.review_release_request(self.cUtil.admin_ctx(),
                                            {'module_name': 'GenomeToPowerpointConverter',
                                             'decision': 'approved'})

        # list stuff in a few ways, it should show what we have
        func_list = self.catalog.list_local_functions(self.cUtil.user_ctx(),
                                                      {'release_tag': 'dev'})[0]
        self.assertEqual(len(func_list), 2)
        func_list = self.catalog.list_local_functions(self.cUtil.user_ctx(),
                                                      {'release_tag': 'beta'})[0]
        self.assertEqual(len(func_list), 2)
        func_list = self.catalog.list_local_functions(self.cUtil.user_ctx(),
                                                      {'release_tag': 'release'})[0]
        self.assertEqual(len(func_list), 2)
        func_list = self.catalog.list_local_functions(self.cUtil.user_ctx(),
                                                      {})[0]
        self.assertEqual(len(func_list), 2)

        func_list = self.catalog.list_local_functions(self.cUtil.user_ctx(),
                                                      {'module_names': [
                                                          'GenomeTopowerpoIntConverter']})[0]
        self.assertEqual(len(func_list), 2)

        # make sure we can fetch it by commit hash
        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter', 'function_id': 'powerpoint_to_genome',
             'git_commit_hash': 'a01e1a20b9c504a0136c75323b00b1cd4c7f7970'}]})[0]

        self.assertEqual(len(specs), 1)
        info = specs[0]['info']
        self.assertEqual(info['function_id'], 'powerpoint_to_genome')
        self.assertEqual(info['git_commit_hash'], 'a01e1a20b9c504a0136c75323b00b1cd4c7f7970')
        self.assertEqual(info['module_name'], 'GenomeToPowerpointConverter')
        self.assertEqual(info['name'], 'Powerpoint to Genome')
        self.assertEqual(info['release_tag'], ['release', 'beta', 'dev'])
        self.assertIsNotNone(info['kidl'])
        self.assertIsNotNone(info['kidl']['parse'])
        self.assertEqual(specs[0]['long_description'],
                         '<b> some html here </b> <br><br> more here!')

        # handle some other cases where we expect to get nothing
        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter', 'function_id': 'powerpoint_to_genome',
             'git_commit_hash': 'not a hash'}]})[0]
        self.assertEqual(len(specs), 0)

        with self.assertRaises(ValueError) as e:
            specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
                {'module_name': 'GenomeTopowerpointConverter',
                 'function_id': 'powerpoint_to_genome', 'release_tag': 'not_a_tag'}]})[0]
        self.assertEqual(str(e.exception),
                         '"release_tag" must be one of dev | beta | release')

        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter', 'function_id': 'not a function'}]})[0]
        self.assertEqual(len(specs), 0)

        specs = self.catalog.get_local_function_details(self.cUtil.user_ctx(), {'functions': [
            {'module_name': 'GenomeTopowerpointConverter',
             'function_id': 'POWERpoint_to_genome'}]})[0]
        self.assertEqual(len(specs), 0)

    def test_local_function_module_get_errors(self):

        with self.assertRaises(ValueError) as e:
            self.catalog.get_local_function_details(self.cUtil.anonymous_ctx(),
                                                    {})
        self.assertEqual(str(e.exception),
                         'Missing required parameter field "functions"')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_local_function_details(self.cUtil.anonymous_ctx(),
                                                    {'functions': {}})
        self.assertEqual(str(e.exception),
                         'Parameter field "functions" must be a list')

        specs = self.catalog.get_local_function_details(self.cUtil.anonymous_ctx(),
                                                        {'functions': []})[0]
        self.assertEqual(len(specs), 0)

        with self.assertRaises(ValueError) as e:
            self.catalog.get_local_function_details(self.cUtil.anonymous_ctx(),
                                                    {'functions': [[]]})
        self.assertEqual(str(e.exception),
                         'Values of the "functions" list must be objects')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_local_function_details(self.cUtil.anonymous_ctx(),
                                                    {'functions': [{}]})
        self.assertEqual(str(e.exception),
                         'All functions specified must specify a "module_name"')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_local_function_details(self.cUtil.anonymous_ctx(),
                                                    {'functions': [{'module_name': {}}]})
        self.assertEqual(str(e.exception),
                         '"module_name" in function specification must be a string')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_local_function_details(self.cUtil.anonymous_ctx(),
                                                    {'functions': [{'module_name': 'blah'}]})
        self.assertEqual(str(e.exception),
                         'All functions specified must specify a "function_id"')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_local_function_details(self.cUtil.anonymous_ctx(),
                                                    {'functions': [{'module_name': 'blah',
                                                                    'function_id': []}]})
        self.assertEqual(str(e.exception),
                         '"function_id" in function specification must be a string')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_local_function_details(self.cUtil.anonymous_ctx(),
                                                    {'functions': [{'module_name': 'blah',
                                                                    'function_id': 'function',
                                                                    'release_tag': {}}]})
        self.assertEqual(str(e.exception),
                         '"release_tag" in function specification must be a string')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_local_function_details(self.cUtil.anonymous_ctx(),
                                                    {'functions': [{'module_name': 'blah',
                                                                    'function_id': 'function',
                                                                    'release_tag': 'next'}]})
        self.assertEqual(str(e.exception),
                         '"release_tag" must be one of dev | beta | release')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_local_function_details(self.cUtil.anonymous_ctx(),
                                                    {'functions': [{'module_name': 'blah',
                                                                    'function_id': 'function',
                                                                    'release_tag': 'beta',
                                                                    'git_commit_hash': {}}]})
        self.assertEqual(str(e.exception),
                         '"git_commit_hash" in function specification must be a string')

    @classmethod
    def setUpClass(cls):

        print('++++++++++++ RUNNING local_function_module_test.py +++++++++++')

        # hack for testing!! remove when docker and NMS components can be tested
        from biokbase.catalog.registrar import Registrar
        Registrar._TEST_WITHOUT_DOCKER = False

        cls.cUtil = CatalogTestUtil('.')  # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())
        # approve developers we will use
        cls.catalog.approve_developer(cls.cUtil.admin_ctx(), cls.cUtil.admin_ctx()['user_id'])
        cls.catalog.approve_developer(cls.cUtil.admin_ctx(), cls.cUtil.user_ctx()['user_id'])

        cls.nms = NarrativeMethodStore(cls.cUtil.getCatalogConfig()['nms-url'])

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()
