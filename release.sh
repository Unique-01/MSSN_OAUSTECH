#!/usr/bin/env sh



flask db init
flask db migrate -m "migration"
flask db upgrade
flask create-admin-user
