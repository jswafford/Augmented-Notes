'''
This parses MEI files and outputs box data.
Usage: python parse_mei.py <mei_file> <dataset_name>
'''
from pyquery import PyQuery as pq

xml_id = "{http://www.w3.org/XML/1998/namespace}id"

def extract_box_pos(mei):
    '''Return a list of pages, where each page is a list of measure bounds.'''
    page_data = []
    d = pq(mei).remove_namespaces()
    fac = d('facsimile')
    pages = fac('surface')
    for page in pages.items():
        zones = page('zone')
        measures = []
        for zone in zones.items():
            data = zone.attr("data")
            if data and d("#"+data)[0].tag == 'measure':
                measures.append(zone)
                continue
            if d('measure[facs="{0}"]'.format(zone.attr(xml_id))):
                measures.append(zone)
                continue
        measure_bounds = []
        for m in measures:
            ulx, uly, lrx, lry = [int(m.attr(x)) for x in ['ulx', 'uly', 'lrx', 'lry']]
            measure_bounds.append([ulx, uly, lrx-ulx, lry-uly])
        page_data.append(measure_bounds)
    return page_data

def parse_mei(mei_text):
    boxes = extract_box_pos(mei_text)
    d = pq(mei_text).remove_namespaces()
    title = d("title").eq(0).text()
    pages = []
    for page_of_boxes in boxes:
        pages.append(dict(measure_bounds = page_of_boxes, measure_ends=[None]*len(page_of_boxes)))
    data = dict(
        title = title,
        pages = pages)
    return data
    
def import_mei(filename):
    '''Given an MEI file, output augnotes JSON data.'''
    return parse_mei(open(filename).read())


def test_extract_box_pos():
    mei = open("sample_data/flat/source.mei").read()
    data = extract_box_pos(mei)
    assert len(data) == 7, 'Length of data is: {0}'.format(len(data))
    page0 = data[0]
    nmeasures = len(page0)
    assert nmeasures == 13, '{0} measure bounds on first page'.format(nmeasures)
    first_bounds = page0[0]
    assert first_bounds == [88, 162, 357-88, 318-162], 'First bounds are {0}'.format(first_bounds)

if __name__ == '__main__':
    import sys
    import os
    import json
    import glob
    filename = sys.argv[1]
    if os.path.isdir(filename):
        names = glob.glob(filename+"/exist/db/contents/sources/edirom_source_*.xml")
        if len(names) != 1:
            raise Exception("Cannot get mei file from {0}".format(filename))
        filename = names[0]
    print json.dumps(import_mei(filename))
