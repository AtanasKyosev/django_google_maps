from django.views import View
from django.views.generic import ListView

import googlemaps
from django.conf import settings

from project_content.models import Locations
from django.shortcuts import render


class HomeView(ListView):
    template_name = "project_content/home.html"
    context_object_name = 'mydata'
    model = Locations
    success_url = "/"


class GeocodingView(View):
    template_name = "project_content/geocoding.html"

    def get(self, request, pk):
        location = Locations.objects.get(pk=pk)
        search_query = ''

        if location.lng and location.lat and location.place_id is not None:
            lat = location.lat
            lng = location.lng
            place_id = location.place_id
            label = "from my database"

        elif location.adress and location.number and location.country and location.zipcode and location.city is not None:
            adress_string = ("ul. " + str(location.adress) + " " +
                             str(location.number) + ", " +
                             str(location.zipcode) + ", " +
                             str(location.city) + ", " +
                             str(location.country)
                             )
            search_query = adress_string
            gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
            result = gmaps.geocode(adress_string)[0]

            lat = result.get('geometry', {}).get('location', {}).get('lat', None)
            lng = result.get('geometry', {}).get('location', {}).get('lng', None)
            place_id = result.get('place_id', {})
            label = "from my api call"

            location.lat = lat
            location.lng = lng
            location.place_id = place_id
            location.save()

        else:
            result = ""
            lat = ""
            lng = ""
            place_id = ""
            label = "no call made"

        context = {
            'adress_string': search_query,
            'location': location,
            'lat': lat,
            'lng': lng,
            'place_id': place_id,
            'label': label
        }

        return render(request, self.template_name, context)
