<%inherit file="base.mako"/>

<%block name="extrahead">
<script>
$(function() {
  var template = $(".score-upload").eq(0).clone();
  console.log("template is:", template)
  template.find("label").text("");
  $(".add-score-upload").click(function() {
    console.log("Detected click!")
    $(".score-upload-list").append(template.clone());
  })
})
</script>
</%block>


<%block name="content">
  <div class="instructions">
    <h1>Welcome to Augmented Notes</h1>
    <p>
      To get started making your own website, upload an mp3 and ogg version of your audio file, an MEI file, and the image files of your score, then follow the directions. At the end, Augmented Notes will output a zip file with everything you need to have your own website that highlights each measure of a score in time with an audio file.
    </p>
    <div class="error"
      %if not empty:
        style="display:none"
      %endif
      >
      Please upload files for all categories.
    </div>
    <form action="${upload_url}" method="POST" enctype="multipart/form-data">
      <label class="upload-label" for="mp3">Upload MP3:</label>
      <input type="file" name="mp3" id="mp3">
      <br/>
      <br/>
      <label class="upload-label" for="ogg">Upload OGG:</label>
      <input type="file" name="ogg" id="ogg">
      <br/>
      <br/>
      <label class="upload-label" for="mei">Upload MEI:</label>
      <input type="file" name="mei" id="mei">
      <br/>
      <br/>
      <div class="score-upload-list">
        <div class="score-upload">
          <label class="upload-label">Upload Score:</label>
          <input type="file" name="page">
          <br/>
        </div>
      </div>
      <label class="upload-label"></label>
      <a class="add-score-upload">+ Add another page</a>
      <br/>
      <input type="submit" name="submit" value="Submit"><br/>
    </form>
  </div>
</%block>