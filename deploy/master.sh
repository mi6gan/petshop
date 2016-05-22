#!/bin/sh
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py fixproducts -v 3
#python manage.py flush --noinput
#python manage.py oscar_populate_countries
#python manage.py loadfixtures -v 3
#python manage.py loadproducts petshop/fixtures/products.csv --clear -v 3
#python manage.py loadphotos -v 3 /pet-zakupki.ru/products/ --clear
#cp -R petshop/fixtures/media/petshop ./media/
cd petshop/static
npm install
node_modules/grunt-cli/bin/grunt
cd ../../
./manage.py collectstatic --noinput
