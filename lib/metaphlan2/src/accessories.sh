#!/bin/bash

REPORT=$1
OUTPATH=$2
PREFIX=$3

rootdir=$( cd $(dirname $0) ; pwd -P )
export PATH=$rootdir:$PATH;
#generate out.list
convert_krakenRep2list.pl < $REPORT > $OUTPATH/$PREFIX.out.list
convert_krakenRep2tabTree.pl < $REPORT > $OUTPATH/$PREFIX.out.tab_tree

# Make Krona plot
ktImportText  $OUTPATH/$PREFIX.out.tab_tree -o $OUTPATH/$PREFIX.krona.html

#generate Tree Dendrogram
phylo_dot_plot.pl -i $OUTPATH/$PREFIX.out.tab_tree -p $OUTPATH/$PREFIX.tree -t 'Kraken2'

set +xe;
echo "";
echo "[END] $OUTPATH $PREFIX";