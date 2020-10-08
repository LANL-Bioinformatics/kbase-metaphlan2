FROM kbase/sdkbase2:python
MAINTAINER Mark Flynn

#RUN echo ". /miniconda/etc/profile.d/conda.sh" >> ~/.bashrc && conda create -n mpenv python=3.6
#RUN conda activate mpenv
#RUN conda config --add channels defaults && \
#conda config --add channels bioconda && \
#conda config --add channels conda-forge
#RUN conda install -yc bioconda pandas metaphlan2=2.96
#RUN pip install coverage jinja2 nose
RUN mkdir -p /kb/data
COPY ./data/ /kb/data/
RUN \
curl -o conda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
rm -rf /miniconda && \
sh ./conda.sh -u -b -p /miniconda/ && \
conda config --add channels bioconda && \
conda config --add channels conda-forge && \
conda install pandas metaphlan
RUN apt update && \
    apt-get install -y build-essential wget unzip git curl autoconf autogen bioperl && \
    cd ../ && \
    git clone https://github.com/marbl/Krona && \
    cd Krona/KronaTools && \
    ./install.pl --prefix /kb/deployment && \
    mkdir taxonomy && \
    ./updateTaxonomy.sh
RUN \
conda install nose pyopenssl requests coverage jinja2 && \
pip install jsonrpcbase
USER root
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module
RUN chmod -R +x /kb/module/lib/metaphlan2/src
WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
