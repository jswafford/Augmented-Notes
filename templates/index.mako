<%inherit file="base.mako"/>

<%block name="extrahead">
<script>
$(function() {
  var template = $(".score-upload").eq(0).clone();
  template.find("label").text("");
  $(".add-score-upload").click(function() {
    var new_block = template.clone();
    $(".score-upload-list").append(new_block);
    new_block.find("input").click();
  })
})
</script>
</%block>


<%block name="content">
  <div class="instructions">
    <h1>Welcome to Augmented Notes</h1>
    <p>
      Augmented Notes integrates scores and audio files to produce interactive
      multimedia websites in which measures of the score are highlighted in time
      with music.
    </p><p>
      You can see it in action
       <a href="http://www.songsofthevictorians.com/balfe/archive.html">here</a>
       as part of the digital archive in <a href="http://www.songsofthevictorians.com/">Songs of the Victorians</a>.
    </p>
    % if upload_url:
      <p>
        To get started making your own website, upload mp3 and ogg versions of your audio file, images of the pages of your score, and, if you have one, an MEI file containing measure boundaries, then hit submit below. Augmented Notes will help you mark the measures on the score and assign them times, and will output a zip file of everything you need to have your own website.
      </p>
      <p>
        Want to try Augmented Notes, but don't have the right files? Click <a href="/example">here</a> to try it with Bach's Prelude No. 1 in C major (BWV 846) <a href="http://en.wikipedia.org/wiki/File:Johann_Sebastian_Bach_-_The_Well-tempered_Clavier_-_Book_1_-_02Epre_cmaj.ogg">performed by Martha Goldstein!</a>
      </p>
      <div class="empty-error"
        %if not empty:
          style="display:none"
        %endif
        >
        Please provide an MP3, an OGG, and score images.
      </div>
      <form action="${upload_url}" method="POST" enctype="multipart/form-data">
        <label class="upload-label" for="mp3">Upload MP3:</label>
        <input type="file" name="mp3" id="mp3">
        <br/>
        <br/>
        <label class="upload-label" for="ogg">Upload OGG:</label>
        <input type="file" name="ogg" id="ogg">
        <br/>
        <span style="font-size:80%; color:#666">
        (If you don't have an OGG, you can create one <a href="http://audio.online-convert.com/convert-to-ogg">here</a>)
        </span>
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
        <label class="upload-label" for="mei">Upload MEI (optional):</label>
        <input type="file" name="mei" id="mei">
        <br/>
        <br/>
        <input type="submit" name="submit" value="Submit"><br/>
      </form>
    % else:
      <p>
        We're doing some maintenance right now, so uploading is disabled, but we'll be back soon!
      </p>
      <p>
        In the meantime, you can <a href="/example">CLICK HERE FOR THE SANDBOX </a> to try Augmented Notes with Bach's Prelude No. 1 in C major (BWV 846) <a href="http://en.wikipedia.org/wiki/File:Johann_Sebastian_Bach_-_The_Well-tempered_Clavier_-_Book_1_-_02Epre_cmaj.ogg">performed by Martha Goldstein.</a>
      </p>
    % endif
  </div>
</%block>