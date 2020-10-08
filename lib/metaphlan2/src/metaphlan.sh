#!/bin/bash

set -e;

usage(){
cat << EOF
USAGE: $0 -i <FASTQ> -o <OUTDIR> -p <PREFIX> [OPTIONS]

OPTIONS:
   -i      Input a FASTQ or FASTA file
   -o      Output directory
   -p      Output prefix
   -t      Number of threads
   -d      Database
   -f      File type
   -h      help
EOF
}
echo "running metaphlan2"
DB=$EDGE_HOME/database/metaphlan2
FASTQ=
PREFIX=
OUTPATH=
THREADS=4

while getopts "i:o:p:t:d:f:h" OPTION
do
     case $OPTION in
        i) FASTQ=$OPTARG
           ;;
        o) OUTPATH=$OPTARG
           ;;
        p) PREFIX=$OPTARG
           ;;
        t) THREADS=$OPTARG
           ;;
        d) DB=$OPTARG
           ;;
        f) TYPE=$OPTARG
           ;;
        h) usage
           exit
           ;;
     esac
done

if [[ -z "$FASTQ" || -z "$OUTPATH" || -z "$PREFIX" ]]
then
     usage;
     exit 1;
fi

#export PYTHONPATH=$EDGE_HOME/bin/python/lib
#export PATH=$EDGE_HOME/bin:$EDGE_HOME/scripts:$EDGE_HOME/scripts/microbial_profiling/script:$PATH;
#mkdir -p $OUTPATH

set -x;
#run metaphlan
echo "metaphlan --bowtie2db $DB --nproc $THREADS --input_type $TYPE $FASTQ outpath $OUTPATH prefix $PREFIX"
time metaphlan --bowtie2db ${DB} --input_type ${TYPE} ${FASTQ} ${OUTPATH}/${PREFIX}.report.txt

#parse mpln
convert_metaphlan2tabTree.pl < $OUTPATH/$PREFIX.report.txt > $OUTPATH/$PREFIX.out.tab_tree
mpln2krona.pl -l s -i $OUTPATH/$PREFIX.report.txt > $OUTPATH/$PREFIX.out.krona

ktImportText $OUTPATH/$PREFIX.out.krona -o $OUTPATH/$PREFIX.krona.html
phylo_dot_plot.pl -i $OUTPATH/$PREFIX.out.tab_tree -p $OUTPATH/$PREFIX.tree -t 'Metaphlan'

set +ex;
echo "";
echo "[END] $OUTPATH $PREFIX";