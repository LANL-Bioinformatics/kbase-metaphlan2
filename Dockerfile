FROM kbase/sdkbase2:python
MAINTAINER Mark Flynn

#FROM genomicpariscentre/bowtie2
# -----------------------------------------
#FROM biobakery/metaphlan2:2.7.7
#RUN pip --default-timeout=180 install --upgrade pip && \
#    conda config --set remote_read_timeout_secs 300 && \
#    conda config --add channels bioconda && \
#    conda update -y conda && \

RUN pip install pandas && \
    apt update && \
    apt-get install -y build-essential wget unzip git curl autoconf autogen libssl-dev
# download conda
# add build user
RUN useradd -ms /bin/bash build

# switch to build user
USER build
ENV HOME /home/build
WORKDIR /home/build/
RUN wget -c https://repo.anaconda.com/miniconda/Miniconda2-4.6.14-Linux-x86_64.sh -O $HOME/miniconda.sh
#RUN wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O $HOME/miniconda.sh
RUN chmod 0755 $HOME/miniconda.sh
RUN ["/bin/bash", "-c", "$HOME/miniconda.sh -b -p $HOME/conda"]
#RUN /bin/bash -c $HOME/miniconda.sh -b -p $HOME/conda -y
ENV PATH="$HOME/conda/bin:$PATH"
RUN rm $HOME/miniconda.sh

# update conda
RUN conda update conda
RUN conda install -y -c bioconda numpy scipy metaphlan2 graphlan export2graphlan && \
    conda clean -ya
#  Entry

USER root
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
