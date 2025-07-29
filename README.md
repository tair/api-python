# api-python

This is a RESTful API designed to provide all the services required to support Phoenix subscriptions and partners. The API is written in Python using Django framework.

To run migrations:
Go to running docker container:
docker exec -it b04e97f15b73 /bin/bash
cd /var/www/api-python

python manage.py makemigrations subscription

Confluence Links:
Subscription -> controls.py
https://phoenixbioinformatics.atlassian.net/wiki/x/C4D9Ig
