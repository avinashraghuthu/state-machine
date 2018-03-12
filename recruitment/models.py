from __future__ import unicode_literals

from django.db import models
from StateMachine.utils import generate_unique_id
import dill as pickle
from workflow.models import WorkflowInfo, State
# Create your models here.


class BaseModel(models.Model):
	created_on = models.DateTimeField(auto_now_add=True, db_index=True)
	updated_on = models.DateTimeField(auto_now=True, db_index=True)
	is_deleted = models.BooleanField(default=False)

	class Meta:
		abstract = True


class CompanyManager(models.Manager):

	def add_company(self, name, description=None, address=None):
		company_id = generate_unique_id('COMP')
		obj = self.model(company_id=company_id, name=name, description=description, address=address)
		obj.save()
		return obj


class Company(BaseModel):
	company_id = models.CharField(max_length=255, primary_key=True)  # Uniquely identify the company which can be referred
	name = models.CharField(max_length=255)
	description = models.TextField(null=True, blank=True)
	address = models.TextField(null=True, blank=True)

	objects = CompanyManager()

	def __unicode__(self):
		return str(self.name) + ' ' + str(self.description)

	def serializer(self):
		data = dict()
		data['company_id'] = self.company_id
		data['name'] = self.name
		data['description'] = self.description
		return data


class JobManager(models.Manager):

	def create_job(self, job_role, company_id,  description, experience_req, salary):
		job_id = generate_unique_id('JOB')
		obj = self.model(job_id=job_id, job_role=job_role, company_id=company_id, description=description,
						 experience_req=experience_req, salary=salary)
		obj.save()
		return obj


class Job(BaseModel):
	job_id = models.CharField(max_length=255, primary_key=True)  # Uniquely identify the job which can be referred
	job_role = models.CharField(max_length=255)  # Role of job like SDE, SDE2
	description = models.TextField(null=True, blank=True)  # Job description
	experience_req = models.IntegerField(default=0)  # In years
	salary = models.DecimalField(decimal_places=2, default=0.00, max_digits=20)
	company = models.ForeignKey(Company)

	objects = JobManager()

	def __unicode__(self):
		return str(self.job_role) + ' ' + str(self.company)

	def serializer(self):
		data = dict()
		data['job_id'] = self.job_id
		data['job_role'] = self.job_role
		data['description'] = self.description
		data['experience_req'] = self.experience_req
		data['salary'] = self.salary
		data['company'] = self.company
		return data


class CandidateManager(models.Manager):

	def add_candidate(self, name, mobile_number, email_id, gender, qualification):
		candidate_id = generate_unique_id('CAD')
		obj = self.model(candidate_id=candidate_id, name=name, mobile_number=mobile_number,
							email_id=email_id, gender=gender, qualification=qualification)
		obj.save()
		return obj


class Candidate(BaseModel):
	MALE = 'M'
	FEMALE = 'F'
	OTHER = 'O'
	GENDER = (
		(MALE, 'Male'),
		(FEMALE, 'Female'),
		(OTHER, 'Other'),
	)

	candidate_id = models.CharField(max_length=255, primary_key=True)  # Uniquely identify the candidate
	name = models.CharField(max_length=255)
	mobile_number = models.CharField(max_length=255, db_index=True)
	email_id = models.EmailField(max_length=255, db_index=True)
	gender = models.CharField(max_length=16, choices=GENDER)
	qualification = models.CharField(max_length=255)  # Education qualification like B.Tech

	objects = CandidateManager()

	def __unicode__(self):
		return str(self.name) + ' ' + str(self.mobile_number)

	def serializer(self):
		data = dict()
		data['candidate_id'] = self.candidate_id
		data['name'] = self.name
		data['mobile_number'] = self.mobile_number
		data['email_id'] = self.email_id
		data['qualification'] = self.qualification
		return data


class HiringManager(models.Manager):

	def add_hiring_entry(self, job, candidate, workflow, state_obj, machine_obj, current_state):
		hiring_id = generate_unique_id('HIR')
		state_obj_dump = pickle.dumps(state_obj).encode("base64").strip()
		machine_obj_dump = pickle.dumps(machine_obj).encode("base64").strip()
		obj = self.model(hiring_id=hiring_id, candidate=candidate, job=job, workflow=workflow,
						 state_obj_dump=state_obj_dump, machine_obj_dump=machine_obj_dump,
						 current_state=current_state)
		obj.save()
		return obj

	def initiate_hiring(self, job, candidate, workflow):
		machine, acting_obj = workflow.initiate_workflow(candidate)
		hiring_obj = self.add_hiring_entry(job, candidate, workflow, acting_obj, machine, workflow.initial_state)
		return hiring_obj, acting_obj.state


class Hiring(BaseModel):
	hiring_id = models.CharField(max_length=255, primary_key=True)  # Uniquely identify the hiring entry
	candidate = models.ForeignKey(Candidate)
	job = models.ForeignKey(Job)
	state_obj_dump = models.TextField(null=True, blank=True)
	machine_obj_dump = models.TextField(null=True, blank=True)
	workflow = models.ForeignKey(WorkflowInfo)  # Specifies the workflow that is followed
	current_state = models.ForeignKey(State)  # Specifies the current state of hiring candidate

	objects = HiringManager()

	def __unicode__(self):
		return str(self.candidate) + ' ' + str(self.job)

	def serializer(self):
		data = dict()
		data['hiring_id'] = self.hiring_id
		data['candidate'] = self.candidate.serializer()
		data['job'] = self.job.serializer()
		data['workflow'] = self.workflow.name
		data['current_state'] = self.current_state.name
		return data

	def dump_state_machine_obj(self, machine_obj, state_obj):
		self.state_obj_dump = pickle.dumps(state_obj).encode("base64").strip()
		self.machine_obj_dump = pickle.dumps(machine_obj).encode("base64").strip()
		self.current_state = State.objects.get_state(state_obj.state)
		self.save()

	def get_state_machine_obj(self):
		state_obj = pickle.loads(self.state_obj_dump.decode("base64"))
		machine_obj = pickle.loads(self.machine_obj_dump.decode("base64"))
		return state_obj, machine_obj
