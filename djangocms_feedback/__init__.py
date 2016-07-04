from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_string
from django.conf import settings

from .views import AjaxFeedbackView 


class FeedbackFormsManager(object):
	_objects = []
	_feedback_types=getattr(settings, 'DJANGOCMS_FEEDBACK_TYPES', ())

	@classmethod
	def objects(cls):
		if not len(cls._feedback_types) == cls._objects:
			cls._objects = []
			for ft in cls._feedback_types:
				cls.Object(ft)
		return cls._objects

	class Object(object):
		
		def __init__(self, ft):
			self._slug = ft.get('slug')
			self._label = ft.get('label')
			self._view_class = ft.get('view_class','')
			self._form_class = ft.get('form_class','')
			FeedbackFormsManager._objects.append(self)

		@property
		def label(self):
			return self._label
		@property
		def slug(self):
			return self._slug

		@property
		def view_class(self):
			if type(self._view_class) is str:
				if not self._view_class:
					self._view_class = AjaxFeedbackView
				else:
					self._view_class = import_string(self._view_class) 
			return self._view_class


		@property
		def form_class(self):
			if type(self._form_class) is str:
				if not self._form_class:
					self._form_class = self.view_class.form_class
				else:
					self._form_class = import_string(self._form_class) 
			return self._form_class

		@property
		def view(self):
			if getattr(self.view_class, 'form_class', None):
				return self.view_class.as_view(form_class=self.form_class)
			return self.view_class.as_view()

