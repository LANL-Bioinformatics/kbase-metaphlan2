# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
import pandas as pd

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ReadsUtilsClient import ReadsUtils
from installed_clients.AssemblyUtilClient import AssemblyUtil
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
    VERSION = "0.0.2"
    GIT_URL = "git@github.com:LANL-Bioinformatics/kbase-metaphlan2.git"
    GIT_COMMIT_HASH = "b57f631656b3413a298682cc9bd6f71a80529f19"

    #BEGIN_CLASS_HEADER
    def _generate_DataTable(self, infile, outfile):
        f =  open(infile, "r")
        wf = open(outfile,"w")

        header = f.readline().strip()
        headerlist = [ x.strip() for x in header.split('\t')]

        wf.write("<head>\n")
        wf.write("<link rel='stylesheet' type='text/css' href='https://cdn.datatables.net/1.10.19/css/jquery.dataTables.css'>\n")
        wf.write("<script type='text/javascript' charset='utf8' src='https://code.jquery.com/jquery-3.3.1.js'></script>\n")
        wf.write("<script type='text/javascript' charset='utf8' src='https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js'></script>\n")
        wf.write("</head>\n")
        wf.write("<body>\n")
        wf.write("""<script>
        $(document).ready(function() {
            $('#gottcha2_result_table').DataTable();
        } );
        </script>""")
        wf.write("<table id='gottcha2_result_table' class='display' style=''>\n")
        wf.write('<thead><tr>' + ''.join("<th>{0}</th>".format(t) for t in headerlist) + '</tr></thead>\n')
        wf.write("<tbody>\n")
        for line in f:
            if not line.strip():continue
            wf.write("<tr>\n")
            temp = [ x.strip() for x in line.split('\t')]
            wf.write(''.join("<td>{0}</td>".format(t) for t in temp))
            wf.write("</tr>\n")
        wf.write("</tbody>\n")
        wf.write("</table>")
        wf.write("</body>\n")

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

        # Check parameters
        logging.info(f'params {params}')
        # Check for presence of input file types in params
        input_genomes = 'input_genomes' in params and len(
            params['input_genomes']) > 0 and None not in params[
                            'input_genomes']
        input_refs = 'input_ref' in params and len(
            params['input_ref']) > 0 and None not in params['input_ref']

        # for name in ['workspace_name', 'db_type']:
        #     if name not in params:
        #         raise ValueError(
        #             'Parameter "' + name + '" is required but missing')
        if not input_genomes and not input_refs:
            raise ValueError(
                'You must enter either an input genome or input reads')

        if input_refs and input_genomes:
            raise ValueError(
                'You must enter either an input genome or input reads, '
                'but not both')

        if input_genomes and (not isinstance(params['input_genomes'][0], str)):
            raise ValueError('Pass in a valid input genome string')

        if input_refs and (
                not isinstance(params['input_ref'], list) or not len(
                params['input_ref'])):
            raise ValueError('Pass in a list of input references')
            # Start with base cmd and add parameters based on user input

        cmd = ['metaphlan2.py', '--bowtie2db', '/data/metaphlan2/mpa_v20_m200',
               '--mpa_pkl', '/data/metaphlan2/mpa_v20_m200.pkl']

        if input_genomes:
            assembly_util = AssemblyUtil(self.callback_url)
            fasta_file_obj = assembly_util.get_assembly_as_fasta(
                {'ref': params['input_genomes'][0]})
            logging.info(fasta_file_obj)
            fasta_file = fasta_file_obj['path']

            cmd.extend(['--input_type', 'fasta', fasta_file])

        if input_refs:
            logging.info('Downloading Reads data as a Fastq file.')
            logging.info(f"Input parameters {params.items()}")
            readsUtil = ReadsUtils(self.callback_url)
            download_reads_output = readsUtil.download_reads(
                {'read_libraries': params['input_ref']})
            print(
                f"Input refs {params['input_ref']} download_reads_output {download_reads_output}")
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
            cmd.extend(['--input_type', 'fastq', fastq_files_string])

        output_dir = os.path.join(self.scratch, 'metaphlan2_output')

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # insert into second to last position, before input file(s)
        cmd.insert(-1, '--min_alignment_len') if params['min_alignment_len'] > 0 else cmd
        cmd.insert(-1, str(params['min_alignment_len'])) if params[
                                                           'min_alignment_len'] > 0 else cmd
        cmd.insert(-1, '--ignore_viruses') if params['ignore_viruses'] == 1 else cmd
        cmd.insert(-1, '--ignore_bacteria') if params['ignore_bacteria'] == 1 else cmd
        cmd.insert(-1, '--ignore_eukaryotes') if params['ignore_eukaryotes'] == 1 else cmd
        cmd.insert(-1, '--ignore_archaea') if params['ignore_archaea'] == 1 else cmd
        cmd.insert(-1, '--stat_q')
        cmd.insert(-1, str(params['stat_q']))
        cmd.insert(-1, '--min_cu_len')
        cmd.insert(-1, str(params['min_cu_len']))

        # append output file
        cmd.extend(['--bowtie2out', os.path.join(output_dir, 'report.txt')])
        cmd00 = ["ls", '-la', '/data/metaphlan2/']
        logging.info(f'cmd00 {cmd00}')
        pls = subprocess.Popen(cmd00, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        logging.info(f'subprocess {pls.communicate()}')

        # run pipeline
        logging.info(f'cmd {" ".join(cmd)}')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        logging.info(f'subprocess {p.communicate()}')

        cmd = ['/kb/module/lib/metaphlan2/src/accessories.sh', os.path.join(output_dir, 'report.txt'), output_dir, 'metaphlan2']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        logging.info(f'subprocess {p.communicate()}')

        # get output file and convert to format for report
        # logging.info(f"params['input_ref'] {params['input_ref']}")
        report_df = pd.read_csv(os.path.join(output_dir, 'report.txt'),
                                sep='\t')
        taxa_list = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus',
                    'species', 'strain', 'unclassified']
        abbrev_list = ['k', 'p', 'c', 'o', 'f', 'g', 's', 't', 'unclassified']

        for taxa in taxa_list:
            report_df[taxa] = None
        tax_dict = dict(zip(abbrev_list, taxa_list))

        # split dunderscores to get tax level and name
        report_df['taxonomy'] = report_df['#SampleID'].apply(
            lambda x: x.split('|')).apply(lambda x: [y.split('__') for y in x])

        for idx, row in report_df.iterrows():
            for col in row['taxonomy']:
                try:
                    report_df.loc[idx, tax_dict[col[0]]] = col[1]
                except IndexError:
                    report_df.loc[idx, tax_dict[col[0]]] = col[0]

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
        message = f"MetaPhlAn2 run finished."
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
