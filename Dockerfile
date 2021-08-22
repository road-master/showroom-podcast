FROM mstmelody/python-ffmpeg:20210822032000 as production
# COPY ./Pipfile ./Pipfile.lock /workspace/
COPY showroompodcast LICENSE Pipfile Pipfile.lock pyproject.toml README.md setup.cfg setup.py /workspace/
ENV PIPENV_VENV_IN_PROJECT=1
RUN pip --no-cache-dir install pipenv \
#  && pipenv install --deploy --system \
 && pipenv install --deploy --dev \
 && pip uninstall -y pipenv virtualenv-clone virtualenv
COPY . /workspace
VOLUME ["/workspace/output"]
ENTRYPOINT [ ".venv/bin/showroom-podcast" ]

FROM production as development
# see: https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV PIPENV_VENV_IN_PROJECT=1
RUN pip --no-cache-dir install pipenv \
 && pipenv install --deploy --dev
ENTRYPOINT [ "pipenv", "run" ]
CMD ["pytest"]
