import json

from config.config import is_dev_server
from models.users import RunkeeperUserModel
from lib.apis.runkeeperapi import RunkeeperAPI

import webapp2
from google.appengine.api import memcache



"""
Acts like a proxy with caching
"""
class RunkeeperMetricsHandler(webapp2.RequestHandler):

    # @todo implement this better with auth scopes...
    disallowed_calls = [
        'team',
        'diabetes',
        # 'background_activities',
        # 'fitness_activities',
        'nutrition',
        'profile',
        # 'records',
        # 'general_measurements',
        # 'settings',
        # 'weight',
        # 'change_log',
        'strength_training_activities',
        # 'sleep',
    ]

    def get(self, user_id, call, id_=None):

        # If its not allowed gto
        if not is_dev_server() and call in self.disallowed_calls:
            self.response.out.write('Call not allowed')
            return

        # Get the user from DB
        runkeeper_user_model = RunkeeperUserModel.get_by_id(user_id)
        if not runkeeper_user_model:
            self.response.out.write('No user found')
            return

        # Get the API
        runkeeper_api = RunkeeperAPI(
            access_token=runkeeper_user_model.access_token,
            access_token_type=runkeeper_user_model.access_token_type,
            debug=True
        )

        # Get the user from Runkeeper
        runkeeper_user = runkeeper_api.get_user()

        # Check if the call is listed
        if not hasattr(runkeeper_user, call):
            self.response.out.write('Unknown call')
            return

        # Check if we can get from the cache
        response = memcache.get(self.get_cache_key(user_id, call, id_))
        if not response:
            # If not found call and write to cache
            response = getattr(runkeeper_user, call)()
            memcache.add(self.get_cache_key(user_id, call, id_), response, 36000)

        # Run the call and echo it
        self.response.out.write(json.dumps(response))

    def get_cache_key(self, user_id, call, id_=None):
        return str(user_id) + str(call) + (id_ if id_ else '')