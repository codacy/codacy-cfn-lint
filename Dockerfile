FROM python:3.7-alpine

LABEL cfn.version="0.24.6" release.date="2019.10.26"

ADD docs/ /docs
ADD entrypoint.py /

RUN adduser -u 2004 -D docker &&\
  pip install cfn-lint==0.24.6 &&\
  rm -rvf /root/.cache &&\
  chown -Rv docker:docker /docs entrypoint.py

ENTRYPOINT ["/entrypoint.py"]
