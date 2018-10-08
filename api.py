# encoding: utf-8

from flask import Flask
from flask_restful import Resource, Api, reqparse
import requests
from params import navitia_API_key as TOKEN
from params import navitia_base_url as BASE

app = Flask(__name__)
api = Api(app)

navitia_API_key = TOKEN
navitia_base_url = BASE

def admin_region_to_geocodejson(a_place):
    feature = {"type" : "Feature"}
    feature['geometry'] = {"type" : "Point", "coordinates" : [float(a_place['coord']['lon']), float(a_place['coord']['lat'])]}
    feature['properties'] = {"type" : "city"}
    feature['properties']["id"] = a_place['id']
    feature['properties']["name"] = a_place['name']
    feature['properties']["city"] = a_place['name']
    feature['properties']["label"] = a_place['label']
    feature['properties']["postcode"] = a_place.get('zip_code')
    feature['properties']["citycode"] = a_place.get('insee')
    return feature


def point_to_geocodejson(a_place):
    feature = {"type" : "Feature"}
    _type = a_place['embedded_type']
    feature['geometry'] = {"type" : "Point", "coordinates" : [float(a_place[_type]['coord']['lon']), float(a_place[_type]['coord']['lat'])]}
    feature['properties'] = {"type" : _type}
    feature['properties']["id"] = a_place['id']
    feature['properties']["name"] = a_place['name']
    feature['properties']["street"] = a_place[_type]['name']
    if "house_number" in a_place[_type]:
        feature['properties']["housenumber"] = a_place[_type]['house_number']
        feature['properties']["name"] = feature['properties']["street"]
    feature['properties']["label"] = a_place[_type]['label']
    if len(a_place[_type].get('administrative_regions', [])):
        feature['properties']["city"] = a_place[_type]['administrative_regions'][0]['name']
        feature['properties']["postcode"] = a_place[_type]['administrative_regions'][0].get('zip_code')
        feature['properties']["citycode"] = a_place[_type]['administrative_regions'][0].get('insee')

    #sometimes, we have the zipcode inside the city name ...
    hack_cut = feature['properties']["city"].split(' ')
    if len(hack_cut) > 1 :
        feature['properties']["city"] = hack_cut[0]

    #the full name contains both the street and the housenumber
    hack_cut = feature['properties']["street"].split(' ')
    if hack_cut[0].isnumeric():
        feature['properties']["street"] = feature['properties']["street"][len(hack_cut[0]) +1 :]
    return feature

class NavitiaAutocomplete(Resource):
    def get(self, coverage_name=None):
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str, help='the q you are you looking for', required=True)
        parser.add_argument('limit', type=int)
        args = parser.parse_args()
        query = args['q']

        navitia_params = {"q": query, "type[]":["address", "poi", "administrative_region"]}

        if "limit" in args :
            navitia_params['count'] = args['limit']
        if coverage_name:
            navitia_url = "{}coverage/{}/places".format(navitia_base_url, coverage_name)
        else:
            navitia_url = '{}places'.format(navitia_base_url)

        get_nav = requests.get(navitia_url, params = navitia_params, headers={'Authorization': navitia_API_key})

        navitia_places = [elem for elem in get_nav.json()["places"]]
        navitia_features = []

        for a_place in navitia_places :
            if a_place["embedded_type"] == "administrative_region":
                feature = admin_region_to_geocodejson(a_place["administrative_region"])
            else :
                feature = point_to_geocodejson(a_place)
            navitia_features.append(feature)

        geocoder_json = {
            "type" : "FeatureCollection",
            "query" : query,
            "features" : navitia_features,
            "_navitia_response" : navitia_places
        }

        return geocoder_json

api.add_resource(NavitiaAutocomplete, '/coverage/<string:coverage_name>', '/coverage/<string:coverage_name>/', '/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
