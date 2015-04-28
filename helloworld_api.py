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

class Profile(ndb.Model):
    nickname = ndb.StringProperty()
    email = ndb.StringProperty()

class ProfileForm(messages.Message):
    email = messages.StringField(1)
    nick = messages.StringField(2)


STORED_GREETINGS = GreetingCollection(items=[
    GreetingForm(message='Good morning World!'),
    GreetingForm(message='Good night World!'),
])


@endpoints.api(name='helloworld', version='v1')
class HelloWorldApi(remote.Service):

    def _getProfileFromUser(self):
        """Get current user and return profile in DB"""
        user = endpoints.get_current_user()
        p_key = ndb.Key(Profile, user.email())
        p = p_key.get()

        if not p:
            p = Profile(
                key = p_key,
                nickname = user.nickname(),
                email = user.email()
            )        
            p.put()
        return p 

    def _copyProfileToForm(self, profile):
        """Put profile from DB in to protorpc form"""
        pf = ProfileForm()
        pf.nick = profile.nickname
        pf.email = profile.email
        return pf



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
        """Add greeting with user's profile as parent"""
        profile = self._getProfileFromUser()
        p_key = ndb.Key(Profile, profile.email)
        g = Greeting(message=request.message, parent=p_key)
        g.put()		
        return request

    @endpoints.method(message_types.VoidMessage, ProfileForm)
    def returnPofile(self, unused_request):
        """Return a user's profile"""
        profile = self._getProfileFromUser()
        return self._copyProfileToForm(profile)

APPLICATION = endpoints.api_server([HelloWorldApi])

