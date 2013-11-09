function AugNotesTimeEdit(augnotes) {
	for (var page_num = 0; page_num < augnotes.num_pages; page_num += 1) {
		var page = augnotes.pages[page_num];
		for (var mnum=0; mnum < page.measure_ends.length; mnum += 1) {
			// page.measure_ends[mnum] = null;
			var input = $('<input type="text">');
			input.val(page.measure_ends[mnum]);
			input.addClass("measure_time").addClass("page"+page_num);
			input.attr("name", "p"+page_num+"m"+mnum);
			// Need to store this in data so that we can get it in our
			// function - we can't just use the one here because it will
			// have changed by the time the function is called.
			input.data("input-num", [page_num, mnum]);
			input.change(function() {
				var nums = $(this).data("input-num");
				var page_num = nums[0];
				var measure_num = nums[1];
				var value = parseFloat($(this).val());
				if (isNaN(value)) {
					// Parsing failed
					$(this).addClass("error");
				} else {
					$(this).removeClass("error");
					augnotes.pages[page_num].measure_ends[measure_num] = value;
				}
			})
			// var li = $('<li></li>');
			// li.append(input);
			$("#time_list").append(input);
		}
	}
}

AugNotesTimeEdit.prototype.showInputsForPage = function(page_num) {
	$(".measure_time").not(".page"+page_num.toString()).hide();
	$(".measure_time.page"+page_num.toString()).show();
}