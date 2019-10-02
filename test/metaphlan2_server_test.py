# -*- coding: utf-8 -*-
import os
import time
import logging
import subprocess
import unittest
from configparser import ConfigParser

from metaphlan2.metaphlan2Impl import metaphlan2
from metaphlan2.metaphlan2Server import MethodContext
from metaphlan2.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class metaphlan2Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('metaphlan2'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'metaphlan2',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = metaphlan2(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_metaphlan2_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_params(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        input_refs = ['22956/3/1']
        ret = self.serviceImpl.run_metaphlan2(self.ctx, {'workspace_name': self.wsName,
                                                         'input_ref': input_refs,
                                                         'tax_level': 'k',
                                                         'min_cu_len': 1000,
                                                         'min_alignment_len': 0,
                                                         'ignore_viruses': 0,
                                                         'ignore_bacteria': 0,
                                                         'ignore_eukaryotes': 0,
                                                         'ignore_archaea': 0,
                                                         'stat_q': 0.1
                                                         })
        print(f'ret {ret[0]}')
        self.assertIn('MetaPhlAn2 run finished', ret[0]['report_params']['message'])

    def test_metaphlan2(self):
        cmd0 = ['rm', '/kb/module/work/test_data/test.fastq.bowtie2out.txt']
        logging.info(f'cmd {cmd0}')
        p = subprocess.Popen(cmd0, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        logging.info(p.communicate())

        cmd = ['metaphlan2.py', '--bowtie2db', '/data/metaphlan2/',
               '--mpa_pkl', '/data/metaphlan2/mpa_v20_m200.pkl',
               '--input_type', 'fastq', '--min_cu_len', '1000',
               '--min_alignment_len', '0', '/kb/module/work/test_data/test.fastq',
               '/kb/module/work/test_data/metaphlan2_report.txt']
        logging.info(f'cmd {cmd}')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        logging.info(p.communicate())

        self.assertTrue(os.path.exists('/kb/module/work/test_data/metaphlan2_report.txt'))
        with open('/kb/module/work/test_data/metaphlan2_report.txt', 'r') as fp:
            logging.info('print summary')
            lines = fp.readlines()
            for line in lines:
                logging.info(line.split('\t')[-1].strip())
            self.assertEqual(lines[-1].split()[0],
                             'k__Viruses|p__Viruses_noname|c__Viruses_noname|o__Mononegavirales|f__Filoviridae|g__Ebolavirus|s__Zaire_ebolavirus|t__PRJNA14703')