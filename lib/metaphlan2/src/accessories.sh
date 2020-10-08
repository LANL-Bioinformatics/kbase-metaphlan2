#!/bin/bash

REPORT=$1
OUTPATH=$2
PREFIX=$3

rootdir=$( cd $(dirname $0) ; pwd -P )
export PATH=$rootdir:$PATH;


convert_metaphlan2tabTree.pl < $REPORT > $OUTPATH/$PREFIX.out.tab_tree
mpln2krona.pl -l s -i $REPORT > $OUTPATH/$PREFIX.out.krona

ktImportText $OUTPATH/$PREFIX.out.krona -o $OUTPATH/$PREFIX.krona.html
phylo_dot_plot.pl -i $OUTPATH/$PREFIX.out.tab_tree -p $OUTPATH/$PREFIX.tree -t 'Metaphlan'

set +ex;
echo "";
echo "[END] $OUTPATH $PREFIX";
