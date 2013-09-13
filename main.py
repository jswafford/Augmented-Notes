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
import glob
import zipfile
import cStringIO
import json
# For local testing only, the local runner seems to miss lxml
sys.path.append("/usr/local/lib/python2.7/site-packages/")
sys.path.append("/Users/dplepage/.virtualenvs/augnotes/lib/python2.7/site-packages/")
import lxml

from google.appengine.ext import db
from google.appengine.api import users

from mako.lookup import TemplateLookup

from google.appengine.api import files
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from parse_mei import parse_mei

templates = TemplateLookup(directories=['templates'])


#  ===========================
#  = Example Data Generators =
#  ===========================

def make_empty_data(npages):
  '''Generate empty data for an augmented score with npages pages.'''
  return {"pages": [
    {"measure_ends": [], "measure_bounds": []} for _ in range(npages)
  ]}


def add_file_as_blob(filename, mime_type):
  blob_name = files.blobstore.create(mime_type='image/jpeg',
    _blobinfo_uploaded_filename=filename.split("/")[-1])
  with files.open(blob_name, 'a') as f:
    f.write(open(filename).read())
  files.finalize(blob_name)
  return files.blobstore.get_blob_key(blob_name)


def make_example(include_data=False):
  mp3 = add_file_as_blob('example_data/music.mp3', 'audio/mp3')
  ogg = add_file_as_blob('example_data/music.ogg', 'audio/ogg')
  images = list(sorted(glob.glob("example_data/pages/*.jpg")))
  page_list = [add_file_as_blob(img_name, 'image/jpeg') for img_name in images]
  if include_data:
    json_string = open("example_data/data.js").read()
  else:
    json_string = json.dumps(make_empty_data(len(page_list)))
  song = Song(mp3=mp3, ogg=ogg, page_list=page_list, json=json_string)
  song.put()
  return song

class ExampleHandler(webapp2.RequestHandler):
  def get(self):
    song = make_example(include_data=False)
    self.redirect("/box_edit/{0}".format(song.key().id()))

class DataExampleHandler(webapp2.RequestHandler):
  def get(self):
    song = make_example(include_data=True)
    self.redirect("/time_edit/{0}".format(song.key().id()))

#  ==============
#  = Song Model =
#  ==============

class Song(db.Model):
  mp3 = blobstore.BlobReferenceProperty(required=True)
  ogg = blobstore.BlobReferenceProperty(required=True)
  mei = blobstore.BlobReferenceProperty(required=False)
  json = db.TextProperty(required=True)
  page_list = db.ListProperty(blobstore.BlobKey, required=True)


#  ====================
#  = Login Management =
#  ====================

def valid_user(user):
  allowed_emails = ['jswaffor@gmail.com', 'jes8zv@virginia.edu', 'dplepage@gmail.com']
  return user is not None and user.email() in allowed_emails

def check_login(handler):
  return
  # if handler.request.host.startswith("localhost"):
  #   return
  user = users.get_current_user()
  if not valid_user(user):
    handler.redirect('http://anglophileinacademia.blogspot.com/2013/01/a-progress-update-and-important.html')

class SignInHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
    else:
      self.redirect('/')


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
    if not mp3_list or not ogg_list or not page_list:
      self.redirect("/?empty=1")
      return
    mp3 = mp3_list[0].key()
    ogg = ogg_list[0].key()
    page_list = [page.key() for page in page_list]
    if mei_list:
      mei = mei_list[0].key()
      json_data = parse_mei(blobstore.BlobReader(mei).read())
    else:
      mei = None
      json_data = make_empty_data(len(page_list))
    song = Song(
      mp3=mp3,
      ogg=ogg,
      mei=mei,
      json=json.dumps(json_data),
      page_list=page_list,
    )
    song.put()
    self.redirect("/box_edit/{0}".format(song.key().id()))


def serve_url(key):
  return '/serve/{0}'.format(key)


class SongEditHandler(webapp2.RequestHandler):
  template_name = None
  next_url = None

  def get_song_or_404(self, song_id):
    try:
      song_id = int(song_id)
    except ValueError:
      self.abort(404)
    song = Song.get_by_id(song_id)
    if song is None:
      self.abort(404)
    return song

  def get(self, song_id):
    check_login(self)
    song = self.get_song_or_404(song_id)
    urls = {}
    urls['mp3'] = serve_url(song.mp3.key())
    urls['ogg'] = serve_url(song.ogg.key())
    urls['pages'] = [serve_url(key) for key in song.page_list]
    data = json.loads(song.json)
    template = templates.get_template(self.template_name)
    self.response.out.write(template.render(data=data, urls=urls, song_id=song_id))

  def post(self, song_id):
    check_login(self)
    song = self.get_song_or_404(song_id)
    song.json = self.request.get('data')
    song.put()
    self.redirect(self.next_url.format(song.key().id()))


class BoxEditHandler(SongEditHandler):
  template_name = 'box_edit.mako'
  next_url = '/time_edit/{0}'


class TimeEditHandler(SongEditHandler):
  template_name = 'time_edit.mako'
  next_url = '/zip/{0}'


class ZipFileHandler(webapp2.RequestHandler):
  def get(self, song_id):
    check_login(self)
    try:
      song_id = int(song_id)
    except ValueError:
      self.error(404)
      return
    song = Song.get_by_id(song_id)
    output = cStringIO.StringIO()
    z = zipfile.ZipFile(output,'w')
    z.writestr("export/data/music.mp3", blobstore.BlobReader(song.mp3).read())
    z.writestr("export/data/music.ogg", blobstore.BlobReader(song.ogg).read())
    z.writestr("export/static/js/augnotes.js", open("export_assets/augnotes.js").read())
    z.writestr("export/static/js/augnotesui.js", open("export_assets/augnotesui.js").read())
    z.writestr("export/static/js/jquery.js", open("export_assets/jquery.js").read())
    z.writestr("export/static/css/export.css", open("export_assets/export.css").read())
    page_urls = []
    for page in song.page_list:
      page_info = blobstore.BlobInfo.get(page)
      fname = "export/data/pages/{0}".format(page_info.filename)
      page_urls.append("./data/pages/{0}".format(page_info.filename))
      z.writestr(fname, blobstore.BlobReader(page).read())
    urls = {}
    urls['mp3'] = "./data/music.mp3"
    urls['ogg'] = "./data/music.ogg"
    urls['pages'] = page_urls
    data = json.loads(song.json)
    template = templates.get_template("export/archive.mako")
    page_src = template.render(data=data, urls=urls, song_id=song_id)
    z.writestr("export/archive.html", page_src)
    z.close()

    self.response.headers["Content-Type"] = "multipart/x-zip"
    self.response.headers['Content-Disposition'] = "attachment; filename=test.zip"
    self.response.out.write(output.getvalue())

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
    ('/box_edit/([^/]+)', BoxEditHandler),
    ('/zip/([^/]+)', ZipFileHandler),
    ('/example', ExampleHandler),
    ('/example_with_data', DataExampleHandler),
  ],
  debug=True)
