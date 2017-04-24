#!/usr/bin/env python

import os, os.path
import urllib
import webapp2
import sys
import glob
import zipfile
import cStringIO
import json
import requests

# For local testing only, the local runner seems to miss lxml
sys.path.append("/Users/dplepage/.virtualenvs/augnotes/lib/python2.7/site-packages/")
sys.path.append("/Users/jswafford/.virtualenvs/AugNotes/lib/python2.7/site-packages/")
import lxml

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from mako.lookup import TemplateLookup

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

def get_or_create_example():
  example_key = db.Key.from_path("Song", "EXAMPLE")
  example = db.get(example_key)
  if not example:
    upload_url = blobstore.create_upload_url('/upload')
    images = list(sorted(glob.glob("example_data/pages/*.jpg")))
    files = [
      ('mp3', ('music.mp3', open('example_data/music.mp3', 'rb'), 'audio/mp3')),
      ('ogg', ('music.ogg', open('example_data/music.ogg', 'rb'), 'audio/ogg')),
    ]
    files.extend([
      ('page', (os.path.basename(f), open(f, 'rb'), 'image/jpeg')) for f in images])
    r = requests.post(upload_url, files=files, allow_redirects=False)
    key = int(r.headers['location'].split("/box_edit/")[1])
    tmp = Song.get_by_id(key)
    example = Song(key_name="EXAMPLE", mp3=tmp.mp3, ogg=tmp.ogg, page_list=tmp.page_list, json=tmp.json)
    example.put()
    tmp.delete()
  return example

def make_example(include_data=False):
  example = get_or_create_example()
  if include_data:
    json_string = open("example_data/data.js").read()
  else:
    json_string = example.json
  song = Song(mp3=example.mp3, ogg=example.ogg, page_list=example.page_list, json=json_string)
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
  json = db.TextProperty(required=False)
  page_list = db.ListProperty(blobstore.BlobKey, required=True)


#  ====================
#  = Login Management =
#  ====================

def is_admin(user):
  allowed_emails = ['jswaffor@gmail.com', 'jes8zv@virginia.edu', 'dplepage@gmail.com']
  return user is not None and user.email() in allowed_emails

def check_login(handler):
  return
  # if handler.request.host.startswith("localhost"):
  #   return
  user = users.get_current_user()
  if not is_admin(user):
    handler.redirect('http://anglophileinacademia.blogspot.com/2013/01/a-progress-update-and-important.html')

class SignInHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
    else:
      self.redirect('/')

class SongInfo(object):
  def __init__(self, song, example=None):
    self.song = song
    self.example = example
    self.mp3 = blobstore.BlobInfo.get(song.mp3.key())
    self.ogg = blobstore.BlobInfo.get(song.ogg.key())
    self.from_example = self.like_example = self.is_example = False
    if example:
      if self.song.key().name() == self.example.song.key().name():
        self.is_example = True
      else:
        self.from_example = self.mp3.key() == example.mp3.key()
        self.like_example = self.mp3.md5_hash == example.mp3.md5_hash
        self.like_example &= self.ogg.md5_hash == example.ogg.md5_hash
    if self.mp3 is None or self.ogg is None:
      self.deleted = True
      self.pages = []
      self.total_size = 0
      self.npages = 0
      return
    self.pages = [blobstore.BlobInfo.get(k) for k in song.page_list]
    self.total_size = self.mp3.size + self.ogg.size
    self.total_size += sum(p.size for p in self.pages)
    self.npages = len(self.pages)

class ListSongsHandler(webapp2.RequestHandler):
  def get(self):
    if not is_admin(users.get_current_user()):
      self.redirect(users.create_login_url(self.request.uri))
      return
    example = SongInfo(get_or_create_example())
    page = int(self.request.get("page", 1))
    nitems = int(self.request.get("nitems", 20))
    offset = (page-1)*nitems
    total_items = offset + Song.all().count(offset=offset, limit=600)
    if total_items == offset+600:
      total_items = None
    songs = Song.all().run(offset=offset, limit=nitems)
    template = templates.get_template("list.mako")

    self.response.out.write(template.render(
      total_items=total_items,
      offset=offset,
      nitems=nitems,
      songs=[SongInfo(s, example) for s in songs],
      example=example))

def delete_song(song, example):
  if not is_admin(users.get_current_user()):
    raise Exception()
  if song.key().name() == 'EXAMPLE':
    raise Exception()
  blobs = [song.mp3.key(), song.ogg.key()] + song.page_list
  do_not_delete = [example.mp3.key(), example.ogg.key()] + example.page_list
  blobs = set(blobs)-set(do_not_delete)
  song.delete()
  blobstore.delete(blobs)

class DeleteHandler(webapp2.RequestHandler):
  def post(self, song_id):
    if not is_admin(users.get_current_user()):
      self.redirect(users.create_login_url(self.request.uri))
      return
    song = Song.get_by_id(int(song_id))
    example = get_or_create_example()
    delete_song(song, example)
    return self.redirect("/songs")


class DeleteManyHandler(webapp2.RequestHandler):
  def post(self):
    example = get_or_create_example()
    for song_id in self.request.POST.getall("ids"):
      song = Song.get_by_id(int(song_id))
      delete_song(song, example)
    return self.redirect("/songs")


class MainHandler(webapp2.RequestHandler):
  def get(self):
    check_login(self)
    try:
      upload_url = blobstore.create_upload_url('/upload')
    except:
      upload_url = None
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
    z.writestr("export/static/img/augnotes_badge.png", open("export_assets/augnotes_badge.png").read())
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
    self.response.headers['Content-Disposition'] = "attachment; filename=your_website.zip"
    self.response.out.write(output.getvalue())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    check_login(self)
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/delete_many', DeleteManyHandler),
    ('/songs', ListSongsHandler),
    ('/delete/([^/]+)', DeleteHandler),
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
