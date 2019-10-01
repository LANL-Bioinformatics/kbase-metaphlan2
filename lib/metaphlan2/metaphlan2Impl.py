# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
import pandas as pd

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ReadsUtilsClient import ReadsUtils
from installed_clients.DataFileUtilClient import DataFileUtil
#END_HEADER


class metaphlan2:
    '''
    Module Name:
    metaphlan2

    Module Description:
    A KBase module: metaphlan2
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    def package_folder(self, folder_path, zip_file_name, zip_file_description):
        ''' Simple utility for packaging a folder and saving to shock '''
        if folder_path == self.scratch:
            raise ValueError ("cannot package scatch itself.  folder path: "+folder_path)
        elif not folder_path.startswith(self.scratch):
            raise ValueError ("cannot package folder that is not a subfolder of scratch.  folder path: "+folder_path)
        dfu = DataFileUtil(self.callback_url)
        if not os.path.exists(folder_path):
            raise ValueError ("cannot package folder that doesn't exist: "+folder_path)
        output = dfu.file_to_shock({'file_path': folder_path,
                                    'make_handle': 0,
                                    'pack': 'zip'})
        return {'shock_id': output['shock_id'],
                'name': zip_file_name,
                'label': zip_file_description}
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.scratch = config['scratch']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_metaphlan2(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_metaphlan2
        logging.info('Downloading Reads data as a Fastq file.')
        readsUtil = ReadsUtils(self.callback_url)
        download_reads_output = readsUtil.download_reads(
            {'read_libraries': params['input_refs']})
        print(
            f"Input parameters {params['input_refs']} download_reads_output {download_reads_output}")
        fastq_files = []
        fastq_files_name = []
        for key, val in download_reads_output['files'].items():
            if 'fwd' in val['files'] and val['files']['fwd']:
                fastq_files.append(val['files']['fwd'])
                fastq_files_name.append(val['files']['fwd_name'])
            if 'rev' in val['files'] and val['files']['rev']:
                fastq_files.append(val['files']['rev'])
                fastq_files_name.append(val['files']['rev_name'])
        logging.info(f"fastq files {fastq_files}")
        fastq_files_string = ' '.join(fastq_files)
        cmd = ['metaphlan2.py', '--bowtie2db', '/data/metaphlan2/',
               '--mpa_pkl', '/data/metaphlan2/mpa_v20_m200.pkl',
               '--input_type', 'fastq']

        output_dir = os.path.join(self.scratch, 'metaphlan2_output')

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cmd.extend(['--min_alignment_len', params['min_alignment_len']]) if params['min_alignment_len'] > 0 else cmd
        cmd.append('--ignore_viruses') if params['ignore_viruses'] == 1 else cmd
        cmd.append('--ignore_bacteria') if params['ignore_bacteria'] == 1 else cmd
        cmd.append('--ignore_eukaryotes') if params['ignore_eukaryotes'] == 1 else cmd
        cmd.append('--ignore_archaea') if params['ignore_archaea'] == 1 else cmd
        cmd.extend(['--stat_q', str(params['stat_q'])])

        cmd.append(fastq_files_string)
        cmd.append(os.path.join(output_dir, 'report.txt'))
        logging.info(f'cmd {cmd}')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        logging.info(f'subprocess {p.communicate()}')

        cmd0 = ["ls", output_dir]
        logging.info(f'cmd {cmd0}')
        pls = subprocess.Popen(cmd0, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

        cmd1 = ["ls", '/kb/module/test/']
        logging.info(f'cmd {cmd1}')
        logging.info(f'subprocess {pls.communicate()}')

        pls = subprocess.Popen(cmd1, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        logging.info(f'subprocess {pls.communicate()}')

        logging.info(f"params['input_refs'] {params['input_refs']}")
        report_df = pd.read_csv(os.path.join(output_dir, 'report.txt'),
                                sep='\t')
        report_df['kingdom'] = None
        report_df['phylum'] = None
        report_df['class'] = None
        report_df['order'] = None
        report_df['family'] = None
        report_df['genus'] = None
        report_df['species'] = None
        report_df['strain'] = None

        tax_dict = {'k': 'kingdom', 'p': 'phylum', 'c': 'class', 'o': 'order',
                    'f': 'family', 'g': 'genus', 's': 'species', 't': 'strain'}
        report_df['taxonomy'] = report_df['#SampleID'].apply(
            lambda x: x.split('|')).apply(lambda x: [y.split('__') for y in x])
        for idx, row in report_df.iterrows():
            for col in row['taxonomy']:
                report_df.loc[idx, tax_dict[col[0]]] = col[1]
        report_df.drop(['taxonomy', '#SampleID'], axis=1, inplace=True)

        report_html_file = os.path.join(output_dir, 'report.html')
        report_df.to_html(report_html_file, classes='Metaphlan2_report',
                          index=False)
        html_zipped = self.package_folder(output_dir, 'report.html', 'report')

        # Step 5 - Build a Report and return
        objects_created = []
        output_files = os.listdir(output_dir)
        output_files_list = []
        for output in output_files:
            if not os.path.isdir(output):
                output_files_list.append(
                    {'path': os.path.join(output_dir, output), 'name': output})
        message = f"MetaPhlAn2 run finished on {fastq_files_string}."
        report_params = {'message': message,
                         'workspace_name': params.get('workspace_name'),
                         'objects_created': objects_created,
                         'file_links': output_files_list,
                         'html_links': [html_zipped],
                         'direct_html_link_index': 0,
                         'html_window_height': 460}
        kbase_report_client = KBaseReport(self.callback_url)
        report_output = kbase_report_client.create_extended_report(
            report_params)
        report_output['report_params'] = report_params
        logging.info(report_output)
        # Return references which will allow inline display of
        # the report in the Narrative
        output = {'report_name': report_output['name'],
                  'report_ref': report_output['ref'],
                  'report_params': report_output['report_params']}
        #END run_metaphlan2

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_metaphlan2 return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
