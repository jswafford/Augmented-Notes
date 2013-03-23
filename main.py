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

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

class MainHandler(webapp2.RequestHandler):
  def get(self):
    upload_url = blobstore.create_upload_url('/upload')
    self.response.out.write(open("main.html").read() % upload_url )

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    mp3_infos = self.get_uploads('mp3')
    ogg_infos = self.get_uploads('ogg')
    page_infos = self.get_uploads('page')
    mei_infos = self.get_uploads('mei')

    if mp3_infos:
	    self.response.out.write("<a href='/serve/%s'>mp3</a><br/>" % mp3_infos[0].key())
    if ogg_infos:
	    self.response.out.write("<a href='/serve/%s'>ogg</a><br/>" % ogg_infos[0].key())
    if page_infos:
	    self.response.out.write("<a href='/serve/%s'>page</a><br/>" % page_infos[0].key())
    if mei_infos:
	    self.response.out.write("<a href='/serve/%s'>mei</a><br/>" % mei_infos[0].key())

    # self.response.out.write(open("time_edit.html").read())
    # self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/upload', UploadHandler),
                               ('/serve/([^/]+)?', ServeHandler),
                               ],
                              debug=True)
# http://stackoverflow.com/questions/583791/is-it-possible-to-generate-and-return-a-zip-file-with-app-engine