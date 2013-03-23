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

from mako.lookup import TemplateLookup

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

templates = TemplateLookup(directories=['templates'])

class MainHandler(webapp2.RequestHandler):
  def get(self):
    upload_url = blobstore.create_upload_url('/upload')
    empty = bool(self.request.get('empty'))
    template = templates.get_template("main.mako")
    self.response.out.write(template.render(upload_url = upload_url, empty=empty))

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def get(self):
    return self.post()

  def post(self):
    defaults = dict(
      mp3 = '/static/tmp/music.mp3',
      ogg = '/static/tmp/music.ogg',
      page = '/static/tmp/1.jpg',
      mei = '/static/tmp/data.js',
    )
    keys = ['mp3', 'ogg', 'page', 'mei']
    urls = {}
    for key in keys:
      info = self.get_uploads(key)
      if info:
        urls[key] = "/serve/%s"%info[0].key()
      else:
        urls[key] = defaults[key]
        # self.redirect("/?empty=1")
    if not self.get_uploads("mei"):
      data = '{"pages": [{"measure_ends": [2.4, 4.57, 6.68, 9.11, 10.47, 11.77, 14.23, 16.6, 18.8, 21.12, 23.5, 26, 28.3], "measure_bounds": [[110, 152, 240, 171], [350, 152, 172, 171], [522, 152, 170, 171], [47, 308, 220, 162], [267, 308, 116, 162], [383, 308, 111, 162], [494, 308, 191, 162], [48, 472, 237, 230], [286, 472, 190, 230], [477, 472, 209, 230], [48, 701, 242, 222], [291, 701, 199, 222], [491, 701, 194, 222]]}, {"measure_ends": [30.4, 32.8, 36.4, 38.9, 41.1, 43.7, 46.2, 48.3, 50.6, 52.9, 55.5, 58.3], "measure_bounds": [[30, 32, 258, 232], [288, 32, 182, 232], [472, 32, 198, 232], [29, 264, 216, 214], [246, 264, 187, 214], [433, 264, 237, 214], [27, 480, 249, 219], [278, 480, 191, 219], [470, 480, 201, 219], [31, 715, 243, 219], [274, 715, 208, 219], [483, 715, 189, 219]]}, {"measure_ends": [61.2, 63.7, 65.9, 68.5, 71, 74, 78.3, 81.1, 85.2, 89.8, 92.1, 94.4, 96.8, 99.4], "measure_bounds": [[51, 48, 254, 218], [304, 48, 207, 218], [508, 48, 191, 218], [52, 265, 217, 218], [268, 265, 218, 218], [484, 265, 212, 218], [50, 487, 234, 218], [282, 487, 112, 218], [395, 487, 137, 218], [532, 487, 161, 218], [49, 714, 225, 224], [274, 714, 135, 224], [410, 714, 151, 224], [561, 714, 131, 224]]}, {"measure_ends": [101.8, 104.2, 106.3, 108.6, 111, 113.5, 116.1, 119.6, 122.1, 124.5, 127, 129.5, 132.1], "measure_bounds": [[22, 50, 254, 218], [276, 50, 186, 218], [462, 50, 203, 218], [27, 274, 244, 218], [270, 274, 204, 218], [473, 275, 195, 218], [31, 496, 273, 232], [303, 496, 178, 231], [482, 496, 191, 231], [36, 737, 209, 210], [246, 737, 141, 210], [388, 737, 150, 210], [536, 737, 140, 210]]}, {"measure_ends": [135.5, 138.6, 141.4, 144.5, 147.6, 149.9, 153.7, 156.8, 159.7, 162.9, 167.9, 173.1], "measure_bounds": [[35, 32, 250, 238], [285, 32, 197, 238], [482, 32, 197, 238], [33, 276, 238, 212], [272, 276, 207, 212], [478, 276, 198, 212], [32, 498, 248, 216], [279, 498, 192, 216], [470, 498, 203, 216], [31, 719, 226, 216], [257, 719, 195, 216], [451, 719, 219, 216]]}, {"measure_ends": [177.3, 182.3, 185.2, 187.7, 190.6, 193.5, 196.2, 199.1, 201, 203.1, 205.1, 207.1, 208.9], "measure_bounds": [[38, 23, 168, 228], [206, 23, 125, 228], [332, 23, 179, 228], [511, 23, 175, 228], [36, 266, 247, 203], [283, 266, 179, 203], [462, 266, 225, 203], [38, 484, 246, 216], [283, 484, 206, 216], [488, 484, 201, 216], [41, 705, 243, 216], [283, 705, 195, 216], [479, 705, 211, 216]]}, {"measure_ends": [211.1, 213.1, 215.3, 217.7, 219.9, 221.7, 223.7, 225.6, 227.7, 230.6, 233.7, 236.8, 239.2, 241.1, 243.1, 246], "measure_bounds": [[43, 29, 206, 228], [249, 29, 147, 228], [394, 29, 74, 228], [468, 29, 52, 228], [520, 29, 169, 228], [47, 269, 244, 203], [291, 269, 185, 203], [477, 269, 212, 203], [48, 496, 225, 207], [271, 496, 158, 207], [428, 496, 118, 207], [546, 496, 144, 207], [49, 724, 208, 216], [257, 724, 151, 216], [409, 724, 159, 216], [569, 724, 123, 216]]}], "dataset_name": "balfe", "title": "Come Into the Garden Maud"}'
    else:
      blob_info = self.get_uploads("mei")[0]
      data = blobstore.BlobReader(blob_info.key()).read()

    # for key in keys:
      # self.response.out.write("<a href='%s'>%s</a><br/>" % (urls[key], key))
    template = templates.get_template("time_edit.mako")
    self.response.out.write(template.render(data=data, urls=urls))
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