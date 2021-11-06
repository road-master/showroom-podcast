FROM mstmelody/python-ffmpeg:20210822032000 as production
COPY showroompodcast LICENSE Pipfile pyproject.toml README.md setup.cfg setup.py /workspace/
# see: https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV PIPENV_VENV_IN_PROJECT=1
RUN pip --no-cache-dir install pipenv==2021.5.29 \
 && pipenv install --deploy --skip-lock \
 && pipenv run python -m pip install --editable . \
 && pip uninstall -y pipenv virtualenv-clone virtualenv
COPY . /workspace
VOLUME ["/workspace/output"]
ENTRYPOINT [ ".venv/bin/showroom-podcast" ]

FROM production as development
RUN pip --no-cache-dir install pipenv==2021.5.29 \
 && pipenv install --deploy --dev
ENTRYPOINT [ "pipenv", "run" ]
CMD ["pytest"]
