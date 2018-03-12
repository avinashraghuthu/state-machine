from __future__ import unicode_literals

from django.db import models
from transitions import Machine
# Create your models here.


class StateManager(models.Manager):

	def add_state(self, name, description=None):
		obj = self.model(name=name, description=description)
		obj.save()
		return obj

	def get_state(self, name):
		try:
			state = self.get(name=name)
		except State.DoesNotExist, e:
			state = None
		return state


class State(models.Model):
	ACTIVE = 1
	INACTIVE = 0
	status_choices = ((ACTIVE, 'Active'),
					  (INACTIVE, 'Inactive'))
	name = models.CharField(max_length=255, primary_key=True)  # State name which is unique
	description = models.TextField(null=True, blank=True)  # State description
	status = models.PositiveSmallIntegerField(default=ACTIVE, choices=status_choices)

	objects = StateManager()

	def __unicode__(self):
		return str(self.name) + ' ' + str(self.status)


class StateConditionManager(models.Manager):

	def add_state_condition(self, action, source_state, destination_state):
		obj = self.model(action=action, source_state=source_state,
						 destination_state=destination_state)
		obj.save()
		return obj

	def prepare_state_condition_transitions(self, state_conditions):
		transitions = []
		for state_condition in state_conditions:
			data = dict()
			data['trigger'] = state_condition.action
			data['source'] = state_condition.source_state.name
			data['dest'] = state_condition.destination_state.name
			transitions.append(data)
		return transitions


class StateCondition(models.Model):
	action = models.CharField(max_length=255)  # Action upon which state change happen
	source_state = models.ForeignKey(State, related_name='source')
	destination_state = models.ForeignKey(State, related_name='destination')

	objects = StateConditionManager()

	def __unicode__(self):
		return str(self.action) + ' ' + str(self.source_state) + ' ' + str(self.destination_state)


class WorkflowInfoManager(models.Manager):

	def add_workflow(self, name, description, state_obj_list, state_condition_list, initial_state):
		obj = self.model(name=name, description=description, initial_state=initial_state)
		obj.save()
		obj.states = state_obj_list
		obj.state_conditions = state_condition_list


class WorkflowInfo(models.Model):
	name = models.CharField(max_length=255, primary_key=True)
	description = models.TextField(null=True, blank=True)
	states = models.ManyToManyField(State, related_name='states')
	state_conditions = models.ManyToManyField(StateCondition, related_name='state_conditions')
	initial_state = models.ForeignKey(State, related_name='initial_state')

	objects = WorkflowInfoManager()

	def __unicode__(self):
		return str(self.name) + ' ' + str(self.description)

	def initiate_workflow(self, acting_obj):
		states = list(self.states.values_list('name', flat=True))
		state_conditions = self.state_conditions.all()
		transitions = StateCondition.objects.prepare_state_condition_transitions(state_conditions)
		machine = Machine(acting_obj, states=states, transitions=transitions, initial=self.initial_state.name)
		return machine, acting_obj

	def change_state(self, action, acting_obj):
		action_str = 'acting_obj'+'.'+action+'()'
		flag = eval(action_str)
		if not flag:
			raise Exception('State Change failed')
		return acting_obj


