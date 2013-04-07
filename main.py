#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import urllib
import webapp2
import sys
sys.path.append("/usr/local/lib/python2.7/site-packages/")
import lxml

from google.appengine.ext import db
from google.appengine.api import users

from mako.lookup import TemplateLookup

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from parse_mei import parse_mei

templates = TemplateLookup(directories=['templates'])

class Song(db.Model):
  mp3 = blobstore.BlobReferenceProperty(required=True)
  ogg = blobstore.BlobReferenceProperty(required=True)
  mei = blobstore.BlobReferenceProperty(required=True)
  page_list = db.ListProperty(blobstore.BlobKey, required=True)

def make_balfe():
  from google.appengine.api import files
  file_name = files.blobstore.create(mime_type='audio/mp3')
  with files.open(file_name, 'a') as f:
    f.write(open("tmp/music.mp3").read())
  files.finalize(file_name)
  mp3 = files.blobstore.get_blob_key(file_name)
  file_name = files.blobstore.create(mime_type='audio/ogg')
  with files.open(file_name, 'a') as f:
    f.write(open("tmp/music.ogg").read())
  files.finalize(file_name)
  ogg = files.blobstore.get_blob_key(file_name)
  file_name = files.blobstore.create(mime_type='text/javascript')
  with files.open(file_name, 'a') as f:
    f.write(open("tmp/data.js").read())
  files.finalize(file_name)
  mei = files.blobstore.get_blob_key(file_name)
  import glob
  page_list = []
  for img_name in glob.glob("tmp/*.jpg"):
    file_name = files.blobstore.create(mime_type='image/jpeg')
    with files.open(file_name, 'a') as f:
      f.write(open(img_name).read())
    files.finalize(file_name)
    page_list.append(files.blobstore.get_blob_key(file_name))
  page_list = page_list
  balfe_song = Song(mp3=mp3, ogg=ogg, page_list=page_list, mei=mei, uid="balfe_test")
  song.put()
  return song

def valid_user(user):
  allowed_emails = ['jswaffor@gmail.com', 'jes8zv@virginia.edu', 'dplepage@gmail.com']
  return user is not None and user.email() in allowed_emails

def check_login(handler):
  user = users.get_current_user()
  if not valid_user(user):
    handler.redirect('http://anglophileinacademia.blogspot.com/2013/01/a-progress-update-and-important.html')

class MainHandler(webapp2.RequestHandler):
  def get(self):
    check_login(self)
    upload_url = blobstore.create_upload_url('/upload')
    empty = bool(self.request.get('empty'))
    template = templates.get_template("index.mako")
    self.response.out.write(template.render(upload_url = upload_url, empty=empty))

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    check_login(self)
    mp3_list = self.get_uploads('mp3')
    ogg_list = self.get_uploads('ogg')
    mei_list = self.get_uploads('mei')
    page_list = self.get_uploads('page')
    if not mp3_list or not ogg_list or not mei_list or not page_list:
      self.redirect("/?empty=1")
      return
    mp3 = mp3_list[0].key()
    ogg = ogg_list[0].key()
    mei = mei_list[0].key()
    page_list = [page.key() for page in page_list]
    song = Song(mp3=mp3, ogg=ogg, mei=mei, page_list=page_list, uid="foo")
    song.put()
    self.redirect("/time_edit/{0}".format(song.key().id()))

def serve(key):
  return '/serve/{0}'.format(key)

class SignInHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
    else:
      self.redirect("/")

class TimeEditHandler(webapp2.RequestHandler):
  def get(self, song_id):
    check_login(self)
    try:
      song_id = int(song_id)
    except ValueError:
      self.error(404)
      return
    song = Song.get_by_id(song_id)
    urls = {}
    urls['mp3'] = serve(song.mp3.key())
    urls['ogg'] = serve(song.ogg.key())
    urls['mei'] = serve(song.mei.key())
    urls['pages'] = [serve(key) for key in song.page_list]
    mei = blobstore.BlobReader(song.mei).read()
    data = parse_mei(mei)
    template = templates.get_template("time_edit.mako")
    self.response.out.write(template.render(data=data, urls=urls))

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    check_login(self)
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/upload', UploadHandler),
    ('/login', SignInHandler),
    ('/serve/([^/]+)', ServeHandler),
    ('/time_edit/([^/]+)', TimeEditHandler),
  ],
  debug=True)

# Dear future us: Read this! It's about zip files.
# http://stackoverflow.com/questions/583791/is-it-possible-to-generate-and-return-a-zip-file-with-app-engine