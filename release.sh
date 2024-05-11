#!/usr/bin/env sh


flask db init
flask db migrate
flask db upgrade
flask create-admin-user