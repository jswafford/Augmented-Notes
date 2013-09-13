<%inherit file="base.mako"/>

<%!
  import json
%>

<%block name="title">
  Select Measure Times
</%block>

<%block name="extrahead">
  <script src="/static/js/augnotes.js"></script>
  <script src="/static/js/augnotesui.js"></script>
  <script>
    var augmented_notes_data = ${json.dumps(data)};
  </script>

  <style type='text/css'>

  .box.selected {
    border-color: red;
    cursor: move;
  }

  button {
    width: 90%;
    margin-left: auto;
    margin-right: auto;
    display: block;
    margin-top: 15px;
    font-size: 100%;
    border: 1px solid black;
    background: white;
    border-radius: 10px;
  }
  .num {
    background:rgba(0,0,0,.5);
    color:white;
    width:20px;
    text-align:center;
  }
  </style>
<script>
function number_boxes() {
  $(".score-page:visible .box").each(function(num) {
    $(this).find(".num").text(num+1);
  })
}

</script>
<script type='text/javascript'>
$(window).load(function(){
  var startx, starty;
  var offsetx, offsety;
  var newbox;
  var mode = 'edit';

  function selected_boxes() {
    return $(".score-page:visible .box.selected");
  }

  function selected_box() {
    return selected_boxes().eq(0);
  }

  function visible_boxes() {
    return $(".score-page:visible .box");
  }

  function select_box(box) {
    selected_boxes().removeClass("selected");
    $(box).addClass("selected");
    btns_on_selected.attr("disabled", false);
  }

  function renumber_selected() {
    var response = prompt("What should the new number be?");
    if (!response)
      return;
    var new_num = parseInt(response)-1;
    if (isNaN(new_num)) {
      alert("I don't understand the number '"+response+"'");
      return;
    }
    var box = selected_box();
    box.css("display", "none");
    box.appendTo($("body"));
    var boxes = visible_boxes();
    if (new_num >= boxes.length) {
      $(".score-page:visible .box-container").append(box);
    } else {
      if (new_num < 0) new_num = 0;
      box.insertBefore(boxes.eq(new_num));
    }
    box.css("display", "block");
    number_boxes();
  }
  $("#renumber_selected").click(renumber_selected);

  function set_mode(new_mode) {
    mode = new_mode;
  }

  function set_box(x, y) {

    var miny = Math.min(starty, y);
    var maxy = Math.max(starty, y);
    var minx = Math.min(startx, x);
    var maxx = Math.max(startx, x);
    newbox.css("top", miny-offsety);
    newbox.css("left", minx-offsetx);
    newbox.css("width", maxx - minx);
    newbox.css("height", maxy - miny);
  }

  function push_boxes_to_augnotes() {
    $(".score-page").each(function(page_num) {
      var score_page = $(this);
      var width_scale = score_page.data("width_scale");
      var height_scale = score_page.data("height_scale");
      var page_data = augnotes.data.pages[page_num];
      page_data.measure_bounds = [];
      score_page.find(".box").each(function(measure_num) {
        var box = $(this);
        var left = Math.round(box.position().left / width_scale);
        var top = Math.round(box.position().top / height_scale);
        var width = Math.round(box.width() / width_scale);
        var height = Math.round(box.height() / height_scale);
        console.log(left, top, width, height, width_scale, height_scale);
        page_data.measure_bounds[measure_num] = [left, top, width, height];
      });
      var nmeasures = page_data.measure_bounds.length;
      var tmp = page_data.measure_ends;
      page_data.measure_ends = []
      for (var i = 0; i < nmeasures; i++) {
        if (i < tmp.length)
          page_data.measure_ends[i] = tmp[i];
        else
          page_data.measure_ends[i] = null;
      }
      console.log("Page", page_num);
    });
  }
  window.push_boxes_to_augnotes = push_boxes_to_augnotes;
  $(".send_augnotes").click(function() {
    push_boxes_to_augnotes();
    console.log("SUBMIT!");
    var form = $("#augnotes_submission");
    var input = form.find('input[name="data"]');
    input.val(JSON.stringify(augnotes.data));
    // form.submit();
  })

  var nextpg = $("#next_page");
  var prevpg = $("#prev_page");
  var delbtn = $("#delete_box_btn");
  var btns_on_selected = $("#delete_box_btn, #renumber_selected");

nextpg.click(function() {
    augnotes_ui.goToNextPage();
    number_boxes();
    if (augnotes_ui.curr_page == augnotes.pages.length - 1) {
        nextpg.attr('disabled', true);
      } else {
        nextpg.attr('disabled', false);
      }
    if (augnotes_ui.curr_page == 0) {
        prevpg.attr('disabled', true);
      } else {
        prevpg.attr('disabled', false);
      }
  })

prevpg.click(function() {
    augnotes_ui.goToPrevPage();
    number_boxes();
    if (augnotes_ui.curr_page == augnotes.pages.length - 1) {
        nextpg.attr('disabled', true);
      } else {
        nextpg.attr('disabled', false);
      }
    if (augnotes_ui.curr_page == 0) {
        prevpg.attr('disabled', true);
      } else {
        prevpg.attr('disabled', false);
      }
  })

  $("#new_box_btn").click(function() {
    if (mode === 'create') {
      set_mode('edit');
      $(this).text("Add boxes");
      $(".box").resizable("option", "disabled", false );
      $(".box").draggable("option", "disabled", false );
    } else {
      set_mode('create');
      $(this).text("Done adding boxes");
      $(".box").resizable("option", "disabled", true );
      $(".box").draggable("option", "disabled", true );
    }
  })

  delbtn.click(function() {
    selected_boxes().remove();
    number_boxes();
    btns_on_selected.attr('disabled', true);
  })

  $(".score-page").mousedown(function (event) {
    if (mode === 'create') {
      startx = event.pageX;
      starty = event.pageY;
      offsetx = $(this).find(".box-container").position().left;
      offsety = $(this).find(".box-container").position().top;
      newbox = $("<div class='box'><div class='num'></div></div>");
      if (selected_boxes().length)
        (selected_boxes().eq(0)).after(newbox);
      else
        $(this).find(".box-container").append(newbox);
      number_boxes();
      select_box(newbox);
      set_box(event.pageX, event.pageY);
      set_mode('drawing');
      event.preventDefault();
      return false;
    }
  })

  $("div.score-div").on("mousedown", ".box", function(event) {
    if (mode === 'edit' && ! $(this).hasClass("selected")) {
      btns_on_selected.attr("disabled", false);
      select_box(this);
      set_mode('edit');
    }
  })

  $(document).mouseup(function (event) {
    if (mode === 'drawing') {
      set_box(event.pageX, event.pageY);
      newbox.resizable({handles: "all"}).draggable({});
      newbox.resizable("option", "disabled", true );
      newbox.draggable("option", "disabled", true );
      set_mode('create');
      event.preventDefault();
      return false;
    }
  }).mousemove(function (event) {
    if (mode === 'drawing') {
      set_box(event.pageX, event.pageY);
      event.preventDefault();
      return false;
    }
  });
});
</script>
  <script type="text/javascript" charset="utf-8">
  $(function() {
    window.augnotes = new AugmentedNotes(augmented_notes_data);
    var score_div = $(".score-div");
    var audio_elt = $(".audtools audio");
    window.augnotes_ui = new AugmentedNotesUI(augnotes, score_div, audio_elt);
    $(augnotes_ui).on("AugmentedNotesUI-page-loaded", function(event, page_num) {
      $(".score-div .score-page").eq(page_num).find(".box").resizable({handles: "all"}).draggable({}).each(function() {
          $(this).append("<div class='num'></div>");
        });
      number_boxes();
    });
  });
</script>
</%block>


<%block name="content">
    <div class="instructions">
  <h1>Lay out the boxes</h1>
  <p>
    Draw a box around each measure of the score. To create boxes, hit "Add boxes", then click, drag, and release on the image. Click "Done adding boxes" to edit boxes you've already made - drag the sides or corners of a box to resize it, or drag in the middle to move it.  To delete a box, select it and click the "Delete Box" button.  To change a measure number, select that box click on the "Renumber selected Box" button. Use the "Previous Page" and "Next Page" buttons to move throughout the score.
  </p>
  <p>
    When you have created all the boxes, click on the button labeled "Save and Continue" to continue to the 'Time Edit' Page."
  </p>
  </div>
  <div class="left_panel score-div">
    % for url in urls['pages']:
      <div class="score-page">
        <img class="score" src="${url}" width="559" alt="Scan">
      </div>
    % endfor
  </div>
  <div class="right_panel" style="width:100px;">
    <div class="audtools" style="display:none">
      <audio style="width:100%" controls="controls">
        <source id="ogg" src="${urls['ogg']}" type="audio/ogg"/>
        <source id="mp3" src="${urls['mp3']}" type="audio/mp3"/>
        Your browser does not support the audio tag!
      </audio>
    </div>
    <button class="button" id="new_box_btn">Add Boxes</button>
    <button class="button" id="renumber_selected">Renumber selected box</button>
    <button class="button" id="delete_box_btn" disabled="true">Delete selected box</button>
    <button class="button" id="next_page">Next Page</button>
    <button class="button" id="prev_page" disabled="true">Previous Page</button>
     <button class="send_augnotes button" type="button">Save and Continue</button>
  </div>
  <div style="clear:both"></div>
  <form id="augnotes_submission" style="display:none" action="/box_edit/${song_id}" method="POST">
    <input type='hidden' name="data"/>
  </form>
</%block>
