<%inherit file="base.mako"/>
<%block name="header">
</%block>

<%block name="content">
<div class="instructions">
    <h1>Welcome to Augmented Notes</h1>
  <p>To get started making your own website, upload an mp3 and ogg version of your audio file, an MEI file, and the image files of your score, then follow the directions.  At the end, Augmented Notes will output a zip file with everything you need to have your own website that highlights each measure of a score in time with an audio file.</p>
    <div
      class="error"
      %if not empty:
        style="display:none"
      %endif
      >
      Please upload files for all categories.
    </div>
    <form action="${upload_url}" method="POST" enctype="multipart/form-data">
      Upload MP3: <input type="file" name="mp3"><br/><br/>
      Upload OGG: <input type="file" name="ogg"><br/><br/>
      Upload MEI: <input type="file" name="mei"><br/><br/>
      Upload Score: <input type="file" name="page"><br/><br/>
      <input type="submit" name="submit" value="Submit"><br/>
    </form>
    </div>
    </%block>