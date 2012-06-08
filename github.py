import os
import requests
import simplejson
import re
import getpass

from util import attrdict

class GithubV3APIError(Exception):
    def __init__(self, error_code, message, raw_response):
        Exception(self, message)
        self.error_code = error_code
        self.message = error_code
        self.raw_response = raw_response

    def __repr__(self):
        return "<GithubV3APIError %s %s>" % (self.error_code, self.message)


class GithubBaseV3Api(object):
    def __init__(self, username, password=None):
        self.username = username
        if password:
            self.password = password
        else:
            self.password = getpass.getpass()
        self.baseuri = 'https://api.github.com'

    def auth(self):
        return self.username, self.password

    def make_call(self, method, url, payload=None):
        if payload:
            enc_payload = simplejson.dumps(payload)
        else:
            enc_payload = ""

        response = requests.request(method, self.baseuri+url, data=enc_payload, auth=self.auth())
        response_body = simplejson.loads(response.text)
        #print response_body
        if response.status_code not in (200, 201):
            raise GithubV3APIError(response.status_code, response_body['message'], response_body)
        return attrdict(response_body)

class Github(GithubBaseV3Api):
    def __init__(self, username=None, password=None):
        if not username and 'GITHUB_USERNAME' in os.environ:
            username = os.environ['GITHUB_USERNAME']

        if not password and 'GITHUB_PASSWORD' in os.environ:
            password = os.environ['GITHUB_PASSWORD']
        GithubBaseV3Api.__init__(self, username, password)

    def list_pull_requests(self, user, repo, state='open'):
        return self.make_call('GET', '/repos/%s/%s/pulls' % (user, repo), {'state': state})

    def make_pull_request(self, user, repo, title, head_ref, body="", head_user=None, base='master'):
        if not head_user:
            head_user = user
        data = {
            "title": title,
            "body": body,
            "head": head_user+':'+head_ref,
            "base": base
        }
        return self.make_call('POST', '/repos/%s/%s/pulls' % (user, repo), data)

    def make_issue_comment(self, user, repo, issue_number, comment):
        data = { 'body': comment }
        return self.make_call('POST', '/repos/%s/%s/issues/%s/comments' % (user, repo, issue_number), data)

    def list_forks(self, user, repo):
        return self.make_call('GET', '/repos/%s/%s/forks' % (user, repo))

    def list_references(self, user, repo, ns=""):
        return self.make_call('GET', '/repos/%s/%s/git/refs/%s' % (user, repo, ns))

    def list_branches(self, user, repo):
        return self.list_references(user, repo, 'heads')

    def get_token(self, note="", note_url="", scopes=[]):
        data = {}

        if note:
            data['note'] = note
        if note_url:
            data['note_url'] = note_url
        if scopes:
            data['scopes'] = scopes

        return self.make_call('POST', '/authorizations', data)




