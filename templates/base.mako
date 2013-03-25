<!DOCTYPE html>
<html>
<head>
<link type="text/css" rel="stylesheet" href="/static/css/style.css"/>
<script src="/static/js/jquery.js"></script>
<title>
    <%block name="title">
    Augmented Notes
    </%block>
  </title>
  <meta name="description" content="Augmented Notes is a tool for creating websites that facilitate interdisciplinary music and text scholarship."/>
  <%block name="extrahead">
  </%block>
</head>
<body>
  <div class="center-content">  
    <%block name="center_content">
      <div id="header">
        <%block name="header">
          <div id="header-left">
            <img src="/static/img/augnotes_badge.png" class="header-logo">
          </div>
          <div id="header-right">
            <b>
              A Tool for Producing Interdisciplinary Music and Text Scholarship
            </b>
          </div>
          <div style="clear:both"></div>
        </%block>
      </div>
      <div class="content">
        <%block name="content">
        </%block>
      </div>
      <div class="footer">
        <%block name="footer">
          <a class="license" rel="license" href="http://creativecommons.org/licenses/by/3.0/">
            <img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/3.0/88x31.png" />
          </a>
          <div style="display:inline-block">
            Developed by Joanna Swafford
            <a style="display:none"
            href="https://plus.google.com/112090517120755825501?rel=author"></a>
            &nbsp;|&nbsp;
            <a href="mailto:jes8zv@virginia.edu?Subject=Songs%20of%20the%20Victorians">
              Email</a>
            &nbsp;|&nbsp;
            <a href="http://twitter.com/annieswafford" target="_blank">
              Twitter
            </a>
          </div>
        </%block>
      </div>
    </%block>
  </div>
  </body>
</html>