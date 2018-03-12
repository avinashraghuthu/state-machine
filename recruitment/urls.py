from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt


from views import (InitiateHiring, ChangeHiringState, AddCandidate, AddCompany,
					AddJob, GetJobByRole, GetHiringDetails)



urlpatterns = [
				url(r'^v1/initiatehiring/$', csrf_exempt(InitiateHiring.as_view())),
				url(r'^v1/changehiringstate/$', csrf_exempt(ChangeHiringState.as_view())),
				url(r'^v1/addcandidate/$', csrf_exempt(AddCandidate.as_view())),
				url(r'^v1/addcompany/$', csrf_exempt(AddCompany.as_view())),
				url(r'^v1/addjob/$', csrf_exempt(AddJob.as_view())),
				url(r'^v1/getjobbyrole/$', csrf_exempt(GetJobByRole.as_view())),
				url(r'^v1/gethiringdetails/$', csrf_exempt(GetHiringDetails.as_view())),

			]