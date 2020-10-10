# -*- coding: utf-8 -*-
import os
import time
import logging
import subprocess
import unittest
from pprint import pprint
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

    def getWsClient(self):
        return self.__class__.wsClient

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_params(self):
    #     Prepare test objects in workspace if needed using
    #     self.getWsClient().save_objects({'workspace': self.getWsName(),
    #                                      'objects': []})
    #
    #     Run your method by
    #     ret = self.getImpl().your_method(self.getContext(), parameters...)
    #
    #     Check returned data with
    #     self.assertEqual(ret[...], ...) or other unittest methods
        input_refs = ['22956/22/1']
        input_genomes = ["79/16/1"]

        # input_refs = ['22956/101/1']  # SRS019033.fastq_reads
        input_assembly = ["79/16/1"]  # Shewanella_oneidensis_MR-1_assembly
        test_fastq_reads = ['22956/22/1']  # test.fastq_reads
        two_reads_set = ['22956/25/1']  # two_se_reads_set (v1) test.fastq_reads (v1) rhodo.art.q50.SE.reads.fastq (v2)
        three_reads_set = ['22956/71/1']  # test.fastq_reads (v1) HMP Even (v1) HMP Odd (v1)
        five_reads_set = ['22956/66/1']
        test_reads_set = ['22956/23/1']  # reads set with single read (test_reads_set)
        hmp_reads_set = ['22956/59/1']
        input_paired_refs = ['22956/8/1', '22956/7/1']

        result = self.serviceImpl.run_metaphlan2(self.ctx,
                                                 {'workspace_name': self.wsName,
                                                  'input_refs': input_refs,
                                                  'tax_level': 'k',
                                                  'min_cu_len': 1000,
                                                  'min_alignment_len': 0,
                                                  'ignore_viruses': 0,
                                                  'ignore_bacteria': 0,
                                                  'ignore_eukaryotes': 0,
                                                  'ignore_archaea': 0, 'stat_q': 0.1})[0]
        logging.info(f"report_ref {result}")
        logging.info(f"report_ref {result['report_ref']}")
        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)
        report = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']
        logging.info(f'print report {report}')
        pprint(report)
        self.assertIn('direct_html', report)
        self.assertIn('file_links', report)
        self.assertIn('html_links', report)
        self.assertIn('objects_created', report)
        self.assertIn('text_message', report)

        result = self.serviceImpl.run_metaphlan2(self.ctx, {'workspace_name': self.wsName,
                                                            'input_refs': two_reads_set,
                                                            'tax_level': 'k',
                                                            'min_cu_len': 1000,
                                                            'min_alignment_len': 0,
                                                            'ignore_viruses': 0,
                                                            'ignore_bacteria': 0,
                                                            'ignore_eukaryotes': 0,
                                                            'ignore_archaea': 0,
                                                            'stat_q': 0.1
                                                            })[0]
        logging.info(f"report_ref {result}")
        logging.info(f"report_ref {result['report_ref']}")
        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)
        report = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']
        logging.info(f'print report {report}')
        pprint(report)
        self.assertIn('direct_html', report)
        self.assertIn('file_links', report)
        self.assertIn('html_links', report)
        self.assertIn('objects_created', report)
        self.assertIn('text_message', report)

        result = self.serviceImpl.run_metaphlan2(self.ctx, {'workspace_name': self.wsName,
                                                            'input_refs': three_reads_set,
                                                            'tax_level': 'k',
                                                            'min_cu_len': 1000,
                                                            'min_alignment_len': 0,
                                                            'ignore_viruses': 0,
                                                            'ignore_bacteria': 0,
                                                            'ignore_eukaryotes': 0,
                                                            'ignore_archaea': 0,
                                                            'stat_q': 0.1
                                                            })[0]
        logging.info(f"report_ref {result}")
        logging.info(f"report_ref {result['report_ref']}")
        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)
        report = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']
        logging.info(f'print report {report}')
        pprint(report)
        self.assertIn('direct_html', report)
        self.assertIn('file_links', report)
        self.assertIn('html_links', report)
        self.assertIn('objects_created', report)
        self.assertIn('text_message', report)
        #
        # input_refs = ['22956/3/1']
        # ret = self.serviceImpl.run_metaphlan2(self.ctx,
        #                                       {'workspace_name': self.wsName,
        #                                        'input_genomes': input_genomes,
        #                                        'tax_level': 'k',
        #                                        'min_cu_len': 1000,
        #                                        'min_alignment_len': 0,
        #                                        'ignore_viruses': 0,
        #                                        'ignore_bacteria': 0,
        #                                        'ignore_eukaryotes': 0,
        #                                        'ignore_archaea': 0, 'stat_q': 0.1})
        # print(f'ret {ret[0]}')
        # self.assertIn('MetaPhlAn2 run finished',
        #               ret[0]['report_params']['message'])
    def test_metaphlan2(self):

        self.assertTrue(os.path.exists(
            '/data/metaphlan2/mpa_v20_m200.1.bt2'))
        self.assertTrue(os.path.exists(
            '/data/metaphlan2/mpa_v20_m200.pkl'))
        logging.info(os.listdir('/data/metaphlan2/'))
        cmd0 = ['rm', '/kb/module/work/test_data/test.fastq.bowtie2out.txt']
        logging.info(f'cmd {cmd0}')
        p = subprocess.Popen(cmd0, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        logging.info(p.communicate())

        cmd = ['metaphlan2.py', '--bowtie2db', '/data/metaphlan2/',
               '--input_type', 'fastq',
               '/kb/module/work/test_data/test.fastq',
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