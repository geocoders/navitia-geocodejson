# navitia places in geocodejson format

Run queries against navitia places API with support of [geocodejson spec](https://github.com/geocoders/geocodejson-spec).

## Intalling

Python3 is needed.
To install the requirements :

    pip install -r requirements.txt

Then duplicate the default_params folder and rename to params :

    cp -R default_params/ params/

Put your navitia api key in the params/__init__.py

## Running

    python api.py

Then, you can geocode some stuff :

        curl 'http://localhost:5000/coverage/fr-idf?q=rue%20de%20la%20procession&limit=2'

Or use [geocoder-tester](https://github.com/geocoders/geocoder-tester) :

        py.test --api-url http://localhost:5000/coverage/fr-idf/ --max-run 10
