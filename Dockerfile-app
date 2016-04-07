FROM python:2.7
# things we like
RUN apt-get update && apt-get install -y \
      git \
      vim
# set up volume we will share our codebase with
VOLUME /baleen
WORKDIR /baleen
# add baleen package to our python path
RUN echo $(pwd) > /usr/local/lib/python2.7/site-packages/baleen.pth
# install requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
# until we get the baleen daemon set, just sleep for now
CMD /bin/sleep Inf
