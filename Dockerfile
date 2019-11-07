FROM python:3.7-alpine

LABEL cfn.version="0.24.8" release.date="2019.11.2"

RUN adduser -u 2004 -D docker &&\
  pip install cfn-lint==0.24.8 &&\
  rm -rvf /root/.cache

ADD docs/ /docs
ADD entrypoint.py /

RUN chown -Rv docker:docker /docs entrypoint.py

ENTRYPOINT ["/entrypoint.py"]
