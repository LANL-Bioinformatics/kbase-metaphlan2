FROM kbase/sdkbase2:python
MAINTAINER Mark Flynn

RUN conda install -yc bioconda pandas metaphlan2 && \
    pip install coverage
#    conda install -yc biobakery graphlan && \
#    conda clean -ya
#  Entry
RUN apt update && \
    apt-get install -y build-essential wget unzip git curl autoconf autogen bioperl libssl-dev&& \
    cd ../ && \
    git clone https://github.com/marbl/Krona && \
    cd Krona/KronaTools && \
    ./install.pl --prefix /kb/deployment && \
    mkdir taxonomy && \
    ./updateTaxonomy.sh

USER root
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module
RUN chmod +x /kb/module/lib/metaphlan2/src/accessories.sh
WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
