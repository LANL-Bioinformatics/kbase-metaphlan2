FROM kbase/sdkbase2:python
MAINTAINER Mark Flynn
RUN mkdir -p /kb/data
COPY ./data/ /kb/data/
RUN conda install -yc bioconda pandas metaphlan2 && \
    pip install coverage && \
    conda clean -ya
#    conda install -yc biobakery graphlan && \
#  Entry
RUN apt update && \
    apt-get install -y build-essential wget unzip git curl autoconf autogen bioperl libssl-dev&& \
    cd ../ && \
    git clone https://github.com/marbl/Krona && \
    cd Krona/KronaTools && \
    ./install.pl --prefix /kb/deployment && \
    mkdir taxonomy && \
    ./updateTaxonomy.sh && \
    apt-get autoremove -y && apt-get clean

USER root
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module
RUN chmod -R +x /kb/module/lib/metaphlan2/src/
RUN cp /kb/module/lib/metaphlan2/src/metaphlan2.py /miniconda/bin/
WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
