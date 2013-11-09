<%
import json
%>
<!DOCTYPE html>
<html>
<head>
  <title>
    Your Title Here
  </title>
  <link type="text/css" rel="stylesheet" href="./static/css/export.css" />
  <script src="./static/js/jquery.js"></script>
  <script src="./static/js/augnotes.js"></script>
  <script src="./static/js/augnotesui.js"></script>
  <script type="text/javascript" charset="utf-8">
    $(function() {
      window.augmented_notes_data = ${json.dumps(data)};
      window.augnotes = new AugmentedNotes(augmented_notes_data);
      var score_div = $(".score-div");
      var audio_elt = $(".audtools audio");
      window.augnotes_ui = new AugmentedNotesUI(augnotes, score_div, audio_elt);
    });
  </script>
</head>
<body>
  <div class="center-content">
    <div class="title">
      <h1> Your Title Here </h1>
    </div>
    <div style="clear:both"></div>
    <div class="content">
      <div class="audtools">
        <audio style="width:100%" controls="controls">
          <source id="ogg" src="${urls['ogg']}" type="audio/ogg"/>
          <source id="mp3" src="${urls['mp3']}" type="audio/mp3"/>
          Your browser does not support the audio tag!
        </audio>
      </div>
      <div>
        <div class="score-div">
          % for url in urls['pages']:
            <div class="score-page">
              <img class="score" src="${url}" width="542px" alt="Scan">
            </div>
          % endfor
        </div>
      </div>
    </div>
    <div class="footer">
      <a class="license" rel="license" href="http://creativecommons.org/licenses/by/3.0/">
        <img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/3.0/88x31.png" />
      </a>
      <a class="augnotes-badge" href="http://www.augmentednotes.com">
        <img alt="Powered by Augmented Notes" style="border-width:0" src="./static/img/augnotes_badge.png" width="88px"/>
      </a>
    </div>
  </div>
</body>
</html>