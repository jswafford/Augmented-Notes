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
	<script src="/static/js/augnotesTimeEdit.js"></script>
	<script>
		var augmented_notes_data = ${json.dumps(data)};
	</script>
	<script type="text/javascript" charset="utf-8">
	$(function() {
		window.augnotes = new AugmentedNotes(augmented_notes_data);
		var score_div = $(".score-div");
		var audio_elt = $("audio#aplayer");
		window.augnotes_ui = new AugmentedNotesUI(augnotes, score_div, audio_elt);
		window.an_time_edit = new AugNotesTimeEdit(augnotes);
		
		$(".next").click(function() {
			augnotes_ui.goToNextMeasure();
		});
		
		$(".prev").click(function() {
			augnotes_ui.goToPrevMeasure();
		});
		
		$(".startover").click(function() {
			augnotes_ui.setCurrentTime(0);
		});
		
		$(".save").click(function() {
			var measure_id = augnotes_ui.currentMeasureID();
			var current_time = augnotes_ui.currentTime();
			var measure = augnotes.getMeasure(measure_id);
			// If the measure end is <= 0, we haven't filled it in yet, so we want
			// to update this measure.

			// Likewise, if the end is NOT <= 0, but the current time is closer to
			// the end of this measure than to the beginning, we still want to
			// update this measure.

			// If the end is NOT <= 0, and the current time is closer to the
			// beginning of this measure than to the end, then we actually want to
			// change the end time of the PREVIOUS measure.
			if (measure.end >0 && (Math.abs(current_time - measure.start) < Math.abs(current_time - measure.end))) {
				measure_id = augnotes.getPrevMeasureID(measure_id);
			}
			// Now we update the measure.
			var inputs_on_page = $("input.measure_time.page" + measure_id.page_num.toString());
			var input = inputs_on_page.eq(measure_id.measure_num);
			input.val(current_time.toFixed(2));
			input.change();
		});

		function showInputsForCurrentPage() {
			var measure_id = augnotes_ui.currentMeasureID();
			an_time_edit.showInputsForPage(measure_id.page_num);
		};

		$(augnotes_ui).on("AugmentedNotesUI-page_change", function() {
			showInputsForCurrentPage();
		});
		$(augnotes_ui).on("AugmentedNotesUI-measure_change", function() {
			var measure_id = augnotes_ui.currentMeasureID();
			var inputs_on_page = $("input.measure_time.page" + measure_id.page_num.toString());
			var input = inputs_on_page.eq(measure_id.measure_num);
			$("input.current").removeClass("current");
			input.addClass("current");
		})

		$(".send_augnotes").click(function() {
			$.post("http://localhost:5000/time_edit/"+augnotes.data.dataset_name, {"data":JSON.stringify(augnotes.data)});
		})
	});
	</script>
</%block>


<%block name="content">
	<div class="instructions">
	<h1>Set the Measure Times</h1>
	<p>To set the measure times, click on the "play" button for the audio file, and click the "save" button at the end of each measure. Once all the measures have been completed, you can click the play button to make sure the box moves in time with the music.</p>
	</div>
	<div class="left_panel score-div">
		% for url in urls['pages']:
			<div class="score-page">
				<img class="score" src="${url}" width="350" alt="Scan">
			</div>
		% endfor
	</div>
	<div class="right_panel">
		<div class="audtools">
			<audio style="width:100%" controls="controls" id='aplayer'>
				<source id="ogg" src="${urls['ogg']}" type="audio/ogg"/>
				<source id="mp3" src="${urls['mp3']}" type="audio/mp3"/>
				Your browser does not support the audio tag!
			</audio>
			<div class="toolbar">
				<button class="save">save</button>
				<button class="prev">previous</button>
				<button class="next">next</button>
				<button class="startover">back to start</button>
			</div>
		</div>
		<div class="time">
			<div id="time_list">
			</div>
		</div>
		<button type="button" class="send_augnotes">Submit the times</button>
	</div>
	<div style="clear:both"></div>
</%block>