from django.shortcuts import render
from django.views.generic import View
from StateMachine.responses import init_response, send_200, send_400 ,send_201
from recruitment.models import Job, Candidate, Hiring
from workflow.models import WorkflowInfo
from constants import (STR_CANDIDATE_NOT_EXISTS, STR_JOB_NOT_EXISTS,
					   STR_HIRING_INTIATED)
from workflow.constants import (STR_WORKFLOW_NOT_EXISTS)
# Create your views here.


class InitiateHiring(View):

	def __init__(self):
		self.response = init_response()

	# @decorator_4xx([]) # to authenticate the user for api
	def post(self, request, *args, **kwargs):
		req_data = request.POST
		job_id = req_data['job_id']
		candidate_id = req_data['candidate_id']
		workflow_name = req_data['workflow_name']
		try:
			job = Job.objects.get(pk=job_id)
			candidate = Candidate.objects.get(pk=candidate_id)
			workflow = WorkflowInfo.objects.get(name=workflow_name)
			hiring_obj, current_state = Hiring.objects.initiate_hiring(job, candidate, workflow)
			self.response['res_str'] = STR_HIRING_INTIATED % current_state
			self.response['res_data'] = hiring_obj.serializer()
			return send_201(self.response)
		except Job.DoesNotExist, e:
			self.response['res_str'] = STR_JOB_NOT_EXISTS
		except Candidate.DoesNotExist,e:
			self.response['res_str'] = STR_CANDIDATE_NOT_EXISTS
		except WorkflowInfo.DoesNotExist, e:
			self.response['res_str'] = STR_WORKFLOW_NOT_EXISTS
		return send_400(self.response)


class ChangeHiringState(View):

	def __init__(self):
		self.response = init_response()

	# @decorator_4xx([]) # to authenticate the user for api
	def post(self, request, *args, **kwargs):
		req_data = request.POST
		hiring_id = req_data['hiring_id']
		action = req_data['action']
		try:
			hiring_obj = Hiring.objects.get(pk=hiring_id)
			state_obj, machine_obj = hiring_obj.get_state_machine_obj()
			workflow = hiring_obj.workflow
			acting_obj = workflow.change_state(action, state_obj)
			hiring_obj.dump_state_machine_obj(machine_obj, acting_obj)
			return send_200(self.response)
		except Job.DoesNotExist, e:
			self.response['res_str'] = STR_JOB_NOT_EXISTS
		except Candidate.DoesNotExist,e:
			self.response['res_str'] = STR_CANDIDATE_NOT_EXISTS
		except WorkflowInfo.DoesNotExist, e:
			self.response['res_str'] = STR_WORKFLOW_NOT_EXISTS
		except Exception, e:
			self.response['res_str'] = str(e)
		return send_400(self.response)