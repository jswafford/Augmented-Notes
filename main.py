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
import zipfile
import cStringIO
import json

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
  mei = blobstore.BlobReferenceProperty(required=False)
  json = db.TextProperty(required=True)
  page_list = db.ListProperty(blobstore.BlobKey, required=True)

def make_example():
  from google.appengine.api import files
  file_name = files.blobstore.create(mime_type='audio/mp3')
  with files.open(file_name, 'a') as f:
    f.write(open("example_data/music.mp3").read())
  files.finalize(file_name)
  mp3 = files.blobstore.get_blob_key(file_name)
  file_name = files.blobstore.create(mime_type='audio/ogg')
  with files.open(file_name, 'a') as f:
    f.write(open("example_data/music.ogg").read())
  files.finalize(file_name)
  ogg = files.blobstore.get_blob_key(file_name)
  json_string = open("example_data/data.js").read()
  import glob
  page_list = []
  for img_name in glob.glob("example_data/pages/*.jpg"):
    file_name = files.blobstore.create(mime_type='image/jpeg',
      _blobinfo_uploaded_filename=img_name.split("/")[-1])
    with files.open(file_name, 'a') as f:
      f.write(open(img_name).read())
    files.finalize(file_name)
    page_list.append(files.blobstore.get_blob_key(file_name))
  song = Song(mp3=mp3, ogg=ogg, page_list=page_list, json=json_string, uid="example")
  song.put()
  return song

def valid_user(user):
  allowed_emails = ['jswaffor@gmail.com', 'jes8zv@virginia.edu', 'dplepage@gmail.com']
  return user is not None and user.email() in allowed_emails

def check_login(handler):
  if handler.request.host.startswith("localhost"):
    return
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
    json_data = parse_mei(blobstore.BlobReader(mei).read())
    page_list = [page.key() for page in page_list]
    song = Song(
      mp3=mp3,
      ogg=ogg,
      mei=mei,
      json=json.dumps(json_data),
      page_list=page_list, 
      uid="foo"
    )
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
    urls['pages'] = [serve(key) for key in song.page_list]
    data = json.loads(song.json)
    template = templates.get_template("time_edit.mako")
    self.response.out.write(template.render(data=data, urls=urls, song_id=song_id))

  def post(self, song_id):
    check_login(self)
    try:
      song_id = int(song_id)
    except ValueError:
      self.error(404)
      return
    song = Song.get_by_id(song_id)
    song.json = self.request.get('data')
    song.put()
    self.response.out.write("ok");

class PreviewHandler(webapp2.RequestHandler):
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
    urls['pages'] = [serve(key) for key in song.page_list]
    data = json.loads(song.json)
    template = templates.get_template("export/archive.mako")
    self.response.out.write(template.render(data=data, urls=urls, song_id=song_id))


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

class ExampleHandler(webapp2.RequestHandler):
  def get(self):
    song = make_example()
    self.redirect("/time_edit/{0}".format(song.key().id()))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/upload', UploadHandler),
    ('/login', SignInHandler),
    ('/serve/([^/]+)', ServeHandler),
    ('/time_edit/([^/]+)', TimeEditHandler),
    ('/preview/([^/]+)', PreviewHandler),
    ('/zip/([^/]+)', ZipFileHandler),
    ('/example', ExampleHandler)
  ],
  debug=True)

# Dear future us: Read this! It's about zip files.
# http://stackoverflow.com/questions/583791/is-it-possible-to-generate-and-return-a-zip-file-with-app-engine