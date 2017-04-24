function AugNotesTimeEdit(augnotes) {
	// Loops over measures and pages
	for (var page_num = 0; page_num < augnotes.num_pages; page_num += 1) {
		var page = augnotes.pages[page_num];
		for (var mnum=0; mnum < page.measure_ends.length; mnum += 1) {
		// Creates input for setting timestamps
			var input = $('<input type="text">');
			input.val(page.measure_ends[mnum]);
			input.addClass("measure_time").addClass("page"+page_num);
			input.attr("name", "p"+page_num+"m"+mnum);
			// Need to store this in data so that we can get it in our
			// function - we can't just use the one here because it will
			// have changed by the time the function is called (and keep overwriting the last measure).
			input.data("input-num", [page_num, mnum]);
			// Saves timestamps (measure_ends) when they change
			input.change(function() {
				var nums = $(this).data("input-num");
				var page_num = nums[0];
				var measure_num = nums[1];
				var value = parseFloat($(this).val());
				if (isNaN(value)) {
					// Parsing failed
					$(this).addClass("error");
					augnotes.pages[page_num].measure_ends[measure_num] = null;
				} else {
					$(this).removeClass("error");
					augnotes.pages[page_num].measure_ends[measure_num] = value;
				}
			})
			$("#time_list").append(input);
		}
	}
}
//Shows inputs only for current page
AugNotesTimeEdit.prototype.showInputsForPage = function(page_num) {
	$(".measure_time").not(".page"+page_num.toString()).hide();
	$(".measure_time.page"+page_num.toString()).show();
}