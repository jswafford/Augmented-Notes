// Defines measure with start time, end time, x, y, width, and height
function Measure(start, end, rect) {
	this.start = start;
	this.end = end;
	this.x = rect[0];
	this.y = rect[1];
	this.w = rect[2];
	this.h = rect[3];
}

// Defines MeasureID class, with page_num and measure_num
function MeasureID(page_num, measure_num) {
	this.page_num = page_num;
	this.measure_num = measure_num;
}

// Defines AugmentedNotes class that stores data for a given dataset,
// including name, number of pages, and all the measure data for pages
// data - the entire saved dataset
// pages - the list of measure numbers, times, and box positions for each page
// num_pages - the number of pages
// This class knows all of the data but doesn't do any of the UI stuff (no rendering).
function AugmentedNotes(data) {
	this.data = data;
	this.pages = data.pages;
	this.num_pages = this.pages.length
}

// Returns pageNum clamped to number of pages in dataset
AugmentedNotes.prototype.clampPageNum = function(num) {
	if (num < 0)
		return 0;
	if (num >= this.pages.length)
		return this.pages.length-1;
	return num;
}

// Returns the number of measures for a given page number
AugmentedNotes.prototype.getNumMeasures = function(page_num) {
	return this.pages[page_num].measure_ends.length;
}

// Returns MeasureID for previous measure given a MeasureID
AugmentedNotes.prototype.getPrevMeasureID = function(measure_id) {
	if (measure_id.measure_num > 0) {
		// If the measure number is > 0, then just move back one measure on
		// the same page.
		return new MeasureID(measure_id.page_num, measure_id.measure_num-1);
	} else if (measure_id.page_num > 0) {
		// If measure number is 0, but page number is > 0, return last measure
		// of previous page
		var last_measure_of_new_page = this.getNumMeasures(measure_id.page_num-1)-1;
		return new MeasureID(measure_id.page_num-1, last_measure_of_new_page);
	} else {
		// If measure number and page number are both 0, we can't go
		// backwards. Stay at the beginning.
		return new MeasureID(0, 0);
	}
}

// Returns MeasureID for next measure given a MeasureID
AugmentedNotes.prototype.getNextMeasureID = function(measure_id) {
	if (measure_id.measure_num != this.getNumMeasures(measure_id.page_num)-1) {
		// If the measure number isn't the last on the page, then keep the page
		// num the same and add one to the measure num.
		return new MeasureID(measure_id.page_num, measure_id.measure_num+1);
	} else if (measure_id.page_num != this.num_pages-1) {
		// If the measure number IS last on the page, but we're not on the last page,
		// add one to the page num and set the measure num to 0.
		return new MeasureID(measure_id.page_num+1, 0);
	} else {
		// If we're on the the last measure of the last page, stay put.
		return new MeasureID(measure_id.page_num, measure_id.measure_num);
	}
}

// Returns a measure object for a given MeasureID
AugmentedNotes.prototype.getMeasure = function(measure_id) {
	var page_num = measure_id.page_num;
	var measure_num = measure_id.measure_num;
	var rect = this.pages[page_num].measure_bounds[measure_num];
	var end = this.pages[page_num].measure_ends[measure_num];
	if (measure_num === 0 && page_num === 0) {
		var start = 0;
	} else {
		var prev_id = this.getPrevMeasureID(measure_id);
		var start = this.pages[prev_id.page_num].measure_ends[prev_id.measure_num];
	}
	return new Measure(start, end, rect);
}
//Returns MeasureID for given time
AugmentedNotes.prototype.measureIDAtTime = function(time) {
	for (var page_num = 0; page_num < this.num_pages; page_num += 1) {
		var page = this.pages[page_num];
		for (var measure_num = 0; measure_num < page.measure_ends.length; measure_num += 1) {
			var m_time = page.measure_ends[measure_num];
			if (m_time === null || time < m_time)
				return new MeasureID(page_num, measure_num);
		}
	}
	// Return MeasureID for last measure of last page
	var last_index = this.num_pages-1;
	var last_page = this.pages[last_index]
	return new MeasureID(last_index, last_page.measure_ends.length-1);
}