from django.shortcuts import render
from django.views.generic import View
from StateMachine.responses import init_response, send_200, send_400 ,send_201
from models import Job, Candidate, Hiring, Company
from workflow.models import WorkflowInfo
from constants import (STR_CANDIDATE_NOT_EXISTS, STR_JOB_NOT_EXISTS,
					   STR_HIRING_INTIATED, STR_INVALID_GENDER, STR_INVALID_EMAIL,
					   STR_INVALID_MOB, STR_INVALID_SALARY, STR_INVALID_EXP,
					   STR_HIRING_STATE_CHANGE_SUCCESS, STR_CANDIDATE_ADDED_SUCCESS,
					   STR_COMPANY_ADDED_SUCCESS, STR_JOB_ADDED_SUCCESS, STR_JOB_FETCHED,
					   STR_HIRING_DETAILS_FETCHED)
from workflow.constants import (STR_WORKFLOW_NOT_EXISTS)
from exceptions import (InvalidEmailId, InvalidMobileNumber, InvalidGender,
						InvalidExperience, InvalidSalary)
import re
from decimal import Decimal
# Create your views here.


class InitiateHiring(View):
	""" Used to initiate the hiring process"""

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

	""" Used for changing the state of candidate in hiring process """

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
			self.response['res_str'] = STR_HIRING_STATE_CHANGE_SUCCESS
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


class AddCandidate(View):

	""" Add candidate to database"""

	def __init__(self):
		self.response = init_response()

	def _validate_email(self, email):
		email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
		if not re.match(email_regex, email):
			raise InvalidEmailId('Invalid Email id')

	def _validate_mobile_number(self, mobile_number):
		if not len(mobile_number) == 10 or \
				not mobile_number.isdigit():
			raise InvalidMobileNumber('Invalid Mobile Number')

	def _validate_gender(self, gender):
		if gender not in [Candidate.MALE, Candidate.FEMALE, Candidate.OTHER]:
			raise InvalidGender('Invalid Gender')

	def _validate(self, mobile_number, email_id, gender):
		self._validate_mobile_number(mobile_number)
		self._validate_email(email_id)
		self._validate_gender(gender)


	# @decorator_4xx([]) # to authenticate the user for api
	def post(self, request, *args, **kwargs):
		req_data = request.POST
		name = req_data['name']
		mobile_number = req_data['mobile_number']
		email_id = req_data['email_id']
		gender = req_data['gender']
		qualification = req_data['qualification']
		try:
			self._validate(mobile_number, email_id, gender)
			candidate = Candidate.objects.add_candidate(name, mobile_number, email_id, gender, qualification)
			self.response['res_data'] = candidate.serializer()
			self.response['res_str'] = STR_CANDIDATE_ADDED_SUCCESS
			return send_201(self.response)
		except InvalidMobileNumber, e:
			self.response['res_str'] = STR_INVALID_MOB
		except InvalidEmailId, e:
			self.response['res_str'] = STR_INVALID_EMAIL
		except InvalidGender, e:
			self.response['res_str'] = STR_INVALID_GENDER
		except Exception, e:
			self.response['res_str'] = str(e)
		return send_400(self.response)


class AddCompany(View):

	"""Add company to database """

	def __init__(self):
		self.response = init_response()

	# @decorator_4xx([]) # to authenticate the user for api
	def post(self, request, *args, **kwargs):
		req_data = request.POST
		name = req_data['name']
		description = req_data.get('description')
		address = req_data.get('address')
		company = Company.objects.add_company(name, description, address)
		self.response['res_data'] = company.serializer()
		self.response['res_str'] = STR_COMPANY_ADDED_SUCCESS
		return send_201(self.response)


class AddJob(View):

	""" Add a new job """

	def __init__(self):
		self.response = init_response()

	def _validate_experience_req(self, experience_req):
		try:
			experience_req = int(experience_req)
			if experience_req > 100:
				raise InvalidExperience('Invalid Experience')
		except ValueError, e:
			raise InvalidExperience('Invalid Experience')
		return experience_req

	def validate_salary(self, salary):
		try:
			amount = Decimal(salary)
		except Exception as ex:
			raise InvalidSalary('Invalid salary')
		return amount

	def _validate(self, experience_req, salary):
		exp_req = self._validate_experience_req(experience_req)
		salary_amt = self.validate_salary(salary)
		return exp_req, salary_amt

	# @decorator_4xx([]) # to authenticate the user for api
	def post(self, request, *args, **kwargs):
		req_data = request.POST
		job_role = req_data['job_role']
		description = req_data.get('description')
		experience_req = req_data['experience_req']
		salary = req_data['salary']
		company_id = req_data['company_id']
		try:
			exp_req, salary_amt = self._validate(experience_req, salary)
			job = Job.objects.create_job(job_role, company_id,  description, exp_req, salary_amt)
			self.response['res_data'] = job.serializer()
			self.response['res_str'] = STR_JOB_ADDED_SUCCESS
			return send_201(self.response)
		except InvalidSalary, e:
			self.response['res_str'] = STR_INVALID_SALARY
		except InvalidExperience, e:
			self.response['res_str'] = STR_INVALID_EXP
		except Exception, e:
			self.response['res_str'] = str(e)
		return send_400(self.response)


class GetJobByRole(View):

	""" Get the jobs  bases on the job role"""

	def __init__(self):
		self.response = init_response()

	# @decorator_4xx([]) # to authenticate the user for api
	def get(self, request, *args, **kwargs):
		req_data = request.GET
		job_role = req_data['job_role']
		try:
			job_list = Job.objects.filter(job_role__icontains=job_role)
			data = []
			for job in job_list:
				data.append(job.serializer())
			self.response['res_data'] = data
			self.response['res_str'] = STR_JOB_FETCHED
			return send_200(self.response)
		except InvalidSalary, e:
			self.response['res_str'] = STR_INVALID_SALARY
		except InvalidExperience, e:
			self.response['res_str'] = STR_INVALID_EXP
		except Exception, e:
			self.response['res_str'] = str(e)
		return send_400(self.response)


class GetHiringDetails(View):

	""" Get hiring details of the current state in workflow"""

	def __init__(self):
		self.response = init_response()

	# @decorator_4xx([]) # to authenticate the user for api
	def get(self, request, *args, **kwargs):
		req_data = request.GET
		state_name = req_data['state']
		try:
			hiring_candidate_list = Hiring.objects.filter(current_state__name=state_name)
			data = []
			for hiring_candidate in hiring_candidate_list:
				data.append(hiring_candidate.serializer())
			self.response['res_data'] = data
			self.response['res_str'] = STR_HIRING_DETAILS_FETCHED
			return send_200(self.response)
		except InvalidSalary, e:
			self.response['res_str'] = STR_INVALID_SALARY
		except InvalidExperience, e:
			self.response['res_str'] = STR_INVALID_EXP
		except Exception, e:
			self.response['res_str'] = str(e)
		return send_400(self.response)

