FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update


# -----------------------------------------
RUN conda install -c bioconda numpy scipy metaphlan2 graphlan export2graphlan && \
    conda clean -ya

#  'axisbg' in 'artist.py' has changed to 'facecolor' from matplotlib v2.2.3
RUN /opt/conda/bin/pip uninstall -y matplotlib && /opt/conda/bin/pip install matplotlib==2.1.0

#  Entry

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
