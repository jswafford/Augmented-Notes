<!DOCTYPE html>
<html>
<head>
<link type="text/css" rel="stylesheet" href="/static/css/style.css"/>
<script src="/static/js/jquery.js"></script>
<script src="/static/js/jquery-ui.js"></script>
  <link rel="stylesheet" type="text/css" href="http://code.jquery.com/ui/1.9.2/themes/base/jquery-ui.css">
<title>
    <%block name="title">
    Augmented Notes
    </%block>
  </title>
  <meta name="description" content="Augmented Notes is a tool for creating websites that facilitate interdisciplinary music and text scholarship."/>
  <%block name="extrahead">
  </%block>
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-44029101-1', 'augmentednotes.com');
  ga('send', 'pageview');

</script>
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