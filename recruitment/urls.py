from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt


from views import InitiateHiring, ChangeHiringState



urlpatterns = [
				url(r'^v1/initiatehiring/$', csrf_exempt(InitiateHiring.as_view())),
				url(r'^v1/changehiringstate/$', csrf_exempt(ChangeHiringState.as_view())),
			]