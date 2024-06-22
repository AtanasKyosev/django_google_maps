from datetime import datetime

from django.views import View
from django.views.generic import ListView

import googlemaps
from django.conf import settings

from project_content.forms import DistanceForm
from project_content.models import Locations, Distances
from django.shortcuts import render, redirect


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


class DistanceView(View):
    template_name = "project_content/distance.html"

    def get(self, request):
        form = DistanceForm
        distances = Distances.objects.all()
        context = {
            'form': form,
            'distances': distances
        }

        return render(request, self.template_name, context)

    def post(self, request):
        form = DistanceForm(request.POST)
        if form.is_valid():
            from_location = form.cleaned_data['from_location']

            from_location_info = Locations.objects.get(name=from_location)

            from_adress_string = ("ul. " + str(from_location.adress) + " " +
                                  str(from_location.number) + ", " +
                                  str(from_location_info.zipcode) + ", " +
                                  str(from_location_info.city) + ", " +
                                  str(from_location_info.country)
                                  )

            to_location = form.cleaned_data['to_location']

            to_location_info = Locations.objects.get(name=to_location)

            to_adress_string = ("ul. " + str(to_location.adress) + " " +
                                str(to_location.number) + ", " +
                                str(to_location_info.zipcode) + ", " +
                                str(to_location_info.city) + ", " +
                                str(to_location_info.country)
                                )

            mode = form.cleaned_data['mode']
            now = datetime.now()

            gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
            calculate = gmaps.distance_matrix(
                from_adress_string,
                to_adress_string,
                mode=mode,
                departure_time=now
            )

            duration_seconds = calculate['rows'][0]['elements'][0]['duration']['value']
            duration_minutes = duration_seconds / 60

            distance_meters = calculate['rows'][0]['elements'][0]['distance']['value']
            distance_kilometers = distance_meters / 1000

            if 'duration_in_traffic' in calculate['rows'][0]['elements'][0]:
                duration_in_traffic_seconds = calculate['rows'][0]['elements'][0]['duration_in_traffic']['value']
                duration_in_traffic_minutes = duration_in_traffic_seconds / 60
            else:
                duration_in_traffic_minutes = None

            obj = Distances(
                from_location=Locations.objects.get(name=from_location),
                to_location=Locations.objects.get(name=to_location),
                mode=mode,
                distance_km=distance_kilometers,
                duration_mins=duration_minutes,
                duration_traffic_mins=duration_in_traffic_minutes
            )

            obj.save()

        else:
            print(form.errors)

        return redirect('my_distance_view')