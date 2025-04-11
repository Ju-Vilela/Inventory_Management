#!/usr/bin/env bash
# build.sh

# Instala dependências e coleta os arquivos estáticos
pip install -r requirements.txt
python manage.py collectstatic --noinput
