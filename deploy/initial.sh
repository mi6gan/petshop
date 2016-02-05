#!/bin/sh
python manage.py migrate --noinput
python manage.py flush --noinput
python manage.py loadfixtures
python manage.py loadcategories
python manage.py fakeproducts --count 1000
python manage.py oscar_populate_countries
cd petshop/static
npm install
node_modules/grunt-cli/bin/grunt
cd ../../
./manage.py collectstatic --noinput
