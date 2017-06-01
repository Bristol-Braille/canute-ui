import logging
import os
import xml.dom.minidom as minidom
from . import utility


log = logging.getLogger(__name__)


def convert_brf(width, height, brf_file, native_file, remove=True):
    '''
    converts a brf format braille book to native.

    :param brf: filename of the pef file
    :param native_file: filename of the destination file
    '''
    log.info("converting brf %s" % brf_file)

    def pad_line(converted):
        converted.extend([0] * (width - len(converted)))

    # do the conversion from brf to pin numbers
    book = []
    with open(brf_file) as fh:
        for line in fh.readlines():
            converted = []
            for char in line:
                try:
                    converted.append(utility.alpha_to_pin_num(char))
                except utility.LinefeedConversionException:
                    if len(converted):
                        pad_line(converted)
                        book.append(converted)
                        converted = []
                except utility.FormfeedConversionException:
                    if len(converted):
                        pad_line(converted)
                        book.append(converted)
                        converted = []

                    # pad up to the next page
                    while len(book) % height != 0:
                        book.append([0] * width)

            if len(converted):
                pad_line(converted)
                book.append(converted)

    log.info("brf loaded with %d lines" % len(book))
    log.info("writing to [%s]" % native_file)
    with open(native_file, 'w') as fh:
        for index, line in enumerate(book):
            if len(line) > width:
                log.warning(
                   'length of row %d is %d which is greater than %d,'
                   + ' truncating'
                   % (index, len(line), width)
                )
            fh.write(bytearray(line[:width]))

    if remove:
        log.info("removing old brf file")
        os.remove(brf_file)


def convert_pef(width, height, pef_file, native_file, remove=True):
    '''
    converts a pef format braille book (XML) to native.
    This format uses unicode of braille and uses the
    `unicode_to_pin_num()` function for the conversion to our own numbered
    braille pictures.

    :param pef_file: filename of the pef file
    :param native_file: filename of the destination file
    '''
    log.info("converting pef %s" % pef_file)
    try:
        xml_doc = minidom.parse(pef_file)
    except:
        log.error("could not convert %s" % pef_file)
        if remove:
            os.remove(pef_file)
        return

    pages = xml_doc.getElementsByTagName('page')
    log.debug("got %d pages" % len(pages))
    lines = []

    def pad_page(page):
        num_rows = len(page.getElementsByTagName('row'))
        for i in range(height - num_rows):
            blank_row = xml_doc.createElement("row")
            txt = xml_doc.createTextNode("")
            blank_row.appendChild(txt)
            page.appendChild(blank_row)

    # rows do the conversion from unicode to pin numbers
    for page in pages:
        # pad missing rows
        pad_page(page)
        for row in page.getElementsByTagName('row'):
            try:
                data = row.childNodes[0].data.rstrip()
                line = []
                for uni_char in data:
                    pin_num = utility.unicode_to_pin_num(uni_char)
                    line.append(pin_num)
            except IndexError:
                # empty row element
                line = [0] * width

            # ensure right length
            missing_cells = width - len(line)
            line.extend([0] * missing_cells)

            lines.append(line)

    log.info("pef loaded with %d lines" % len(lines))
    log.info("writing to [%s]" % native_file)
    with open(native_file, 'w') as fh:
        for index, line in enumerate(lines):
            if len(line) > width:
                log.warning(
                   'length of row %d is %d which is greater than %d,'
                   + ' truncating'
                   % (index, len(line), width)
                )
            fh.write(bytearray(line[:width]))

    if remove:
        log.info("removing old pef file")
        os.remove(pef_file)
