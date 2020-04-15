FROM node:13.12.0-alpine AS angular
RUN mkdir /app
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json /app/
RUN npm install
COPY frontend /app
RUN npm run build -- --output-path=/app/angular-app/dist/

FROM alpine:3.11
MAINTAINER Branko Milosavljevic <mbranko@uns.ac.rs>
RUN set -x \
    && deps=' \
    uwsgi \
    python3 \
    uwsgi-python3 \
    uwsgi-router_static \
    mariadb-dev \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    libffi-dev \
    graphviz-dev \
    libmagic \
    ' \
        && apk --no-cache add --update $deps

RUN pip3 install -U pip
COPY backend/requirements.txt /app/requirements.txt
RUN pip3 install --upgrade pip setuptools
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r /app/requirements.txt
COPY backend /app
COPY --from=angular /app/angular-app/dist /app/frontend/dist
RUN chmod +x /app/run_prod.sh
WORKDIR /app
RUN mkdir /private
ARG django_settings=prod
ENV DJANGO_SETTINGS=$django_settings
RUN python3 /app/manage.py collectstatic --noinput 
RUN rm -rf /app/webshop.log
EXPOSE 8000
CMD ["/app/run_prod.sh"]
