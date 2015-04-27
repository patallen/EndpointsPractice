import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types
from protorpc import remote


package = 'Hello'

class GreetingForm(messages.Message):
	message = messages.StringField(1)

class GreetingCollection(messages.Message):
	items = messages.MessageField(GreetingForm, 1, repeated=True)

class Greeting(ndb.Model):
	message = ndb.StringProperty()

STORED_GREETINGS = GreetingCollection(items=[
	GreetingForm(message='Good morning World!'),
	GreetingForm(message='Good night World!'),
])

@endpoints.api(name='helloworld', version='v1')
class HelloWorldApi(remote.Service):


	@endpoints.method(message_types.VoidMessage, GreetingCollection,
					  path='hellogreeting', http_method='GET',
					  name='greetings.listGreetings')
	def greetings_list(self, unused_request):
		return STORED_GREETINGS

	RESOURCE_ID = endpoints.ResourceContainer(
		message_types.VoidMessage,
		id=messages.IntegerField(2, variant=messages.Variant.INT32, required=True))


	@endpoints.method(RESOURCE_ID, GreetingForm, 
					  path='hellogreeting/{id}', http_method='GET',
					  name='greetings.getGreeting')
	def greeting(self, request):
		try:
			return STORED_GREETINGS.items[request.id]
		except:
			return endpoints.NotFoundException('Greeting %s not found.' % request.id)


	@endpoints.method(GreetingForm, GreetingForm,
					  path='hellogreeting', http_method='POST',
					  name='greeting.addGreeting')
	def addGreeting(self, request):
		g = Greeting(message=request.message)
		g.put()		
		return request

APPLICATION = endpoints.api_server([HelloWorldApi])

