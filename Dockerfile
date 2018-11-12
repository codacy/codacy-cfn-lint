FROM python:3.7-alpine

LABEL cfn.version="0.8.3" release.date="2018.11.12"

ADD docs/ /docs
ADD entrypoint.py /

RUN adduser -u 2004 -D docker &&\
  pip install cfn-lint==0.8.3 &&\
  rm -rvf /root/.cache &&\
  chown -Rv docker:docker /docs entrypoint.py

ENTRYPOINT ["/entrypoint.py"]
