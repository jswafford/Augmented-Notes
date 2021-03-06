//http://stackoverflow.com/questions/4851395/how-to-get-the-height-of-a-hidden-image
function getImageDimensions(el, onReady) {
    var src = typeof el.attr === 'function' ? el.attr('src') : el.src !== undefined ? el.src : el;

    var image = new Image();
    image.onload = function(){
        if(typeof(onReady) == 'function') {
            onReady({
                width: image.width,
                height: image.height
            });
        }
    };
    image.src = src;
}

function AugmentedNotesUI(augnotes, score_div, audio_elt) {
    this.augnotes = augnotes;
    this.audio_elt = audio_elt;
    this.score_div = $(score_div);
    this.current_measure_id = new MeasureID(null,null);
    this.show_page(0);
    this.apply_boxes();
    var self = this;
    this.audio_elt.on("timeupdate", function() {
        self.highlightCurrentTime(this.currentTime);
    })
}

AugmentedNotesUI.prototype.apply_boxes = function() {
    var self = this;
    this.score_div.find(".score-page").each(function(page_num) {
        var score_page = $(this);
        var wrapper = $('<div style="position:relative"></div>');
        score_page.prepend(wrapper);
        var image_elt = $(this).find("img.score")
        getImageDimensions(image_elt.attr("src"), function(data) {
            var original_image_w = data.width;
            var original_image_h = data.height;
            var imgw = image_elt.width()*1.0;
            var imgh = image_elt.height()*1.0;
            //scales coordinates for box image
            var width_scale = imgw/original_image_w;
            var height_scale = imgh/original_image_h;
            // width or height might be 0 because of hidden images.
            // We require that at least one be fixed on the image.
            if (height_scale === 0) // height not specified
                height_scale = width_scale;
            else if (width_scale === 0) // width not specified
                width_scale = height_scale;
            for (var i = 0; i < self.augnotes.getNumMeasures(page_num); i++) {
                var measure_id = new MeasureID(page_num, i);
                var measure = self.augnotes.getMeasure(measure_id);
                var box = $('<div class="box"></div>');
                box.css({
                    display: "none",
                    left: measure.x*width_scale + "px",
                    top: measure.y*height_scale + "px",
                    width: measure.w*width_scale + "px",
                    height: measure.h*height_scale + "px"
                });
                wrapper.append(box);
            }
            // TODO ideally should do this once after all boxes are done.
            self.highlightCurrentTime();
        })
    })
}

AugmentedNotesUI.prototype.highlightMeasure = function(measure_id) {
    var old_id = this.current_measure_id;
    this.show_page(measure_id.page_num);
    this.score_div.find(".score-page:visible").find(".box").hide().eq(measure_id.measure_num).show();
    this.current_measure_id = measure_id;
    if (old_id.measure_num !== this.current_measure_id.measure_num) {
        $(this).trigger("AugmentedNotesUI-measure_change");
    }
    if (old_id.page_num !== this.current_measure_id.page_num) {
        $(this).trigger("AugmentedNotesUI-page_change");
    }
}

AugmentedNotesUI.prototype.highlightTime = function(time) {
    var measure_id = this.augnotes.measureIDAtTime(time)
    this.highlightMeasure(measure_id)
}

AugmentedNotesUI.prototype.highlightCurrentTime = function() {
    this.highlightTime(this.currentTime())
}

AugmentedNotesUI.prototype.show_page = function(num) {
    var page_num = this.augnotes.clampPageNum(num);
    if (page_num === this.curr_page)
        return;
    var pages = this.score_div.find(".score-page");
    pages.filter(":visible").hide();
    pages.eq(page_num).show();
    this.curr_page = page_num;
}

AugmentedNotesUI.prototype.currentMeasureID = function() {
    var currentTime = this.currentTime();
    return this.augnotes.measureIDAtTime(currentTime);
}

AugmentedNotesUI.prototype.currentPageNum = function() {
    return this.currentMeasureID().page_num;
}

AugmentedNotesUI.prototype.currentMeasureNum = function() {
    return this.currentMeasureID().measure_num;
}

AugmentedNotesUI.prototype.currentTime = function() {
    return this.audio_elt[0].currentTime;
}

AugmentedNotesUI.prototype.setCurrentTime = function(time) {
    this.audio_elt[0].currentTime = time;
    this.highlightCurrentTime();
}

AugmentedNotesUI.prototype.goToNextMeasure = function() {
    var page_num = this.currentPageNum();
    var m_num = this.currentMeasureNum();
    var end_time = this.augnotes.getMeasure(this.currentMeasureID()).end;
    this.setCurrentTime(end_time+.001);
}

AugmentedNotesUI.prototype.goToPrevMeasure = function() {
    var page_num = this.currentPageNum();
    var m_num = this.currentMeasureNum();
    var measure_id = this.currentMeasureID();
    if (m_num === 0 && page_num === 0) {
        var start_time = 0;
    } else {
        var prev_id = this.augnotes.getPrevMeasureID(measure_id);
        var start_time = this.augnotes.getMeasure(prev_id).start;
    }
    this.setCurrentTime(start_time+.001);
}

AugmentedNotesUI.prototype.pause = function() {
    this.audio_elt[0].pause();
}

AugmentedNotesUI.prototype.play = function() {
    this.audio_elt[0].play();
}
