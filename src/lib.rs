// A BRF book indexer with a C FFI API.
//
// Book paths are always UTF-8 and must not contain embedded NULs.
//
// The following book limits apply, and the behaviour when they're
// violated is undefined:
//
//  * files >=4GiB
//  * books with >=64 kibipages
//  * books with any individual page spanning >=64KiB
//  * it's assumed that this code won't have to handle libraries with
//    more than 1000 books; resource concerns:
//    * code uses a pipe per book and filehandle tables aren't endless;
//      though several thousand should be fine on a kernel not really
//      doing much else
//    * memory footprint of indices has not been measured or optimised;
//      the servo::heapsize crate should allow this, but 16 bytes per
//      page is not unlikely
//
// init() must be called first; if not, behaviour of other functions is
// undefined.
//
// init(lines_per_page : u8) -> i32:
//
//  Must be called before any other, giving the module an opportunity to
//  do whatever setup it wants.  Synchronous.  Returns -EINVAL if
//  `lines_per_page` is zero.  Returns -EBUSY if init() has already been
//  called.
//
// trigger_load(book : char *, fd : i32) -> None:
//
//  Begin the process of loading `book` (a path) asynchronously, and
//  return; when the book has loaded, reply "ok" on `fd`.  If the book
//  fails to load for any reason, reply "error" on `fd`.  Currently `fd`
//  is never used again, but future revisions might use it to supply
//  pre-processed page content.
//
// get_page_count(book) -> i32:
//
//  Returns one more than the maximum page number for `book` that will
//  be accepted by `get_page()`.  Synchronous.  If the page count for
//  `book` is not yet known (book load never triggered, or triggered but
//  unfinished, or triggered but failed), returns -ENOENT.
//
// get_page(book, pageno) -> (status: i32, firstbyte: u32, pagelength: u16):
//
//  Returns the index entry for `pageno` of `book`.  Synchronous.
//  `status` is 0 upon success.  `status` is -ENOENT and other fields
//  meaningless upon failure, with the same failure reasons as
//  get_page_count().  `status` is -EFAULT if `pageno` is >=
//  get_page_count(book).  It's then up to the caller to:
//
//    * read the page described
//    * pad the page out with blank lines if it has fewer lines than the
//      display does
//    * clip overlong lines to the display width

extern crate libc;
#[macro_use]
extern crate lazy_static;
extern crate quick_xml;

use libc::{c_char, c_void, write};
use quick_xml::events::Event;
use quick_xml::Reader;
use std::collections::{BTreeMap, HashMap};
use std::ffi::CStr;
use std::fs::File;
use std::io;
use std::io::{BufRead, BufReader};
use std::num::NonZeroU8;
use std::path::Path;
use std::sync::atomic::{AtomicU8, Ordering};
use std::sync::Mutex;
use std::thread;

// Internally, anyway.  Limits books to 2^16 pages.
type PageNumber = u16;

type UnixError = i32;

// This implicitly limits useable book files to sub-4GiB.
// Individual pages can't be longer than 64KiB.
#[derive(Hash, Eq, PartialEq, Debug, Copy, Clone)]
struct PageExtent {
    first: u32,
    length: u16,
}

// Just for FFI to return PageExtent with allowance for failure.
#[repr(C)]
pub struct PageExtentResult {
    status: i32,
    first: u32,
    length: u16,
}

// An entry for a single book.
#[derive(Hash, Eq, PartialEq, Debug)]
struct BookIndex {
    // FIXME: Unlike indexed_line_reader (which this drew inspiration
    // from) we index every single page, so a simple Vec is probably
    // both smaller and more efficient for page_index.
    page_index: BTreeMap<PageNumber, PageExtent>,
    page_count: PageNumber,
    fd: i32,
}

static DISPLAY_LINES: AtomicU8 = AtomicU8::new(0);
lazy_static! {
    // FIXME: use RwLock, since initial book loading can probably be a
    // bit parallel?
    static ref BOOKS: Mutex<HashMap<String, BookIndex>> = Mutex::new(HashMap::new());
}

#[no_mangle]
pub extern "C" fn init(num_display_lines: u8) -> UnixError {
    if num_display_lines <= 0 {
        return -libc::EINVAL;
    }
    // Since we've made it impossible to set to zero, an existing zero
    // must mean we're first.  It'd be nicer to use Once, but only in
    // nightly can you use is_completed() to detect that you're second
    // and thus complain.
    let old = DISPLAY_LINES.compare_and_swap(0, num_display_lines, Ordering::SeqCst);
    if old != 0 {
        return -libc::EBUSY;
    }
    0
}

#[no_mangle]
pub extern "C" fn trigger_load(bookpath: *const c_char, bookfd: i32) {
    let bookpath = stringify(bookpath);

    thread::spawn(move || {
        let mut status = "ok";
        let display_lines = DISPLAY_LINES.load(Ordering::SeqCst);
        let display_lines = NonZeroU8::new(display_lines).expect("init() hasn't been called yet");
        let index = index_book(&bookpath, display_lines);
        if index.is_some() {
            println!("did index book");
            let index = index.unwrap();
            let page_count = index.len() as PageNumber;
            BOOKS.lock().unwrap().insert(
                bookpath,
                BookIndex {
                    page_index: index,
                    page_count: page_count,
                    fd: bookfd,
                },
            );
        } else {
            status = "error";
        }
        // Write to pipe.
        let len = status.len();
        let status = status.as_ptr() as *const c_void;
        let result = unsafe { write(bookfd, status, len) };
        // Something's already seriously wrong if a write to our own
        // pipe fails, so panic.  Better that than let the error go
        // completely unnoticed.
        if result < 0 {
            panic!("pipe write failed");
        }
    });
}


fn index_book(
    bookpath: &String,
    display_lines: NonZeroU8,
) -> Option<BTreeMap<PageNumber, PageExtent>> {
    // FIXME could/should we do path conversion in shared code?
    let path = Path::new(bookpath);
    // Ensure valid Unicode path.
    if path.to_str().is_none() {
        return None;
    }
    // File must have an extension.
    let ext = path.extension();
    if ext.is_none() {
        return None;
    }
    // Unwrap is safe because we checked Unicode-ness already.
    let ext = ext.unwrap().to_str().unwrap().to_ascii_lowercase();

    let f = File::open(bookpath);
    if f.is_err() {
        return None;
    }
    let reader = io::BufReader::new(f.unwrap());

    match ext.as_str() {
        "brf" => index_brf(reader, display_lines),
        "pef" => index_pef(reader, display_lines),
        _ => None,
    }
}

#[no_mangle]
pub extern "C" fn get_page_count(bookpath: *const c_char) -> i32 {
    let bookpath = stringify(bookpath);
    match BOOKS.lock().unwrap().get(&bookpath) {
        Some(bookindex) => {
            // Only use this for debug, it's pretty noisy.
            //println!("{}: {:?}", bookpath, bookindex);
            bookindex.page_count as i32
        }
        None => {
            println!("{} is unknown.", bookpath);
            -libc::ENOENT
        }
    }
}

#[no_mangle]
pub extern "C" fn get_page(bookpath: *const c_char, page: PageNumber) -> PageExtentResult {
    let bookpath = stringify(bookpath);
    let books = BOOKS.lock().unwrap();
    let book = books.get(&bookpath);
    if book.is_none() {
        println!("{} is unknown.", bookpath);
        return PageExtentResult {
            status: -libc::ENOENT,
            first: 0,
            length: 0,
        };
    }
    let book = book.unwrap();
    // Only use this for debug, it's pretty noisy.
    //println!("{}: {:?}", bookpath, book);
    if page >= book.page_index.len() as PageNumber {
        return PageExtentResult {
            status: -libc::EFAULT,
            first: 0,
            length: 0,
        };
    }
    let extent = book.page_index.get(&page).unwrap();
    PageExtentResult {
        status: 0,
        first: extent.first,
        length: extent.length as u16,
    }
}

const FORM_FEED: &str = "\x0C";

fn index_brf(
    mut br: BufReader<File>,
    display_lines: NonZeroU8,
) -> Option<BTreeMap<PageNumber, PageExtent>> {
    let mut lines_in_cur_page = 0; // 0 means current page has no content yet
    let mut line = String::new();

    let mut cur_page = PageExtent {
        first: 0,
        length: 0,
    };
    let mut map = BTreeMap::new();

    loop {
        line.clear();
        let size = br.read_line(&mut line);
        if !size.is_ok() {
            // Read error; return None so that we make no entry for this
            // book.
            return None;
        }
        let mut size = size.unwrap();
        if size == 0 {
            // We hit EOF.
            if lines_in_cur_page > 0 {
                let total_pages = map.len() as PageNumber;
                map.insert(total_pages, cur_page.clone());
            }
            return Some(map);
        }
        //println!("line {} is {} chars", lines_in_cur_page, size);

        // BufRead doesn't have lookahead and has a fixed idea of lines, making
        // this slightly difficult to reason about: one of the two ways to end
        // a page, encountering a form feed, can't be detected until you see
        // the beginning of the next line.  So we've already grabbed a line and
        // have to decide whether the previous line was the last in its page or
        // not.
        if (line.starts_with(FORM_FEED) && lines_in_cur_page > 0)
            || lines_in_cur_page == display_lines.get()
        {
            // Either we've seen the page terminator or we've seen a new
            // line that will fill the page.  Tie off the existing page
            // *without* newly read line.
            let cur_page_num = map.len() as PageNumber;
            map.insert(cur_page_num, cur_page.clone());
            cur_page.first += cur_page.length as u32;
            cur_page.length = 0;
            lines_in_cur_page = 0;
            // Assumptions about FFs, based on a search of all BRFs in our
            // available library:
            //  * FFs only ever follow line endings; i.e.:
            //    * may end a file, but can't begin one
            //    * never embedded within a line
            //    * there's only ever zero or one after a line ending
            if line.starts_with(FORM_FEED) {
                // Don't include FF in the next page.
                cur_page.first += 1;
                size -= 1;
            }
        }
        cur_page.length += size as u16;
        lines_in_cur_page += 1;
    }
}

// We follow the original algorithm from the Python for pagination:
//  * hoover all rows up into a pageless list
//  * paginate by book height
//  * pad the final page
// That unfortunately means that a PageExtent can span XML pages.
// What we return is the extent from the '<' of the first <row> to the
// '>' of the last, and then lumber the caller with discarding:
//  * the initial <row>
//  * anything between </row> and <row> (even <page> or </page>)
//  * the final </row>
// Maybe this horror will go away if we move to rust-cpython.
//
// Even more horrid: quick_xml doesn't give us any handle on the entire
// original tag so we have to assume XML doesn't use whitespace inside
// tags, and then do shonky maths on assumed tag lengths.
//
fn index_pef(
    br: BufReader<File>,
    display_lines: NonZeroU8,
) -> Option<BTreeMap<PageNumber, PageExtent>> {
    let mut reader = Reader::from_reader(br);

    let mut lines_in_cur_page = 0;
    let mut buf = Vec::new();
    let mut done = false;

    let mut cur_page = PageExtent {
        first: 0,
        length: 0,
    };
    let mut map = BTreeMap::new();

    while !done {
        match reader.read_event(&mut buf) {
            Ok(Event::Start(ref e)) => {
                match e.name() {
                    b"row" => {
                        if lines_in_cur_page == 0 {
                            cur_page.first = (reader.buffer_position() - "<row>".len()) as u32;
                        }
                    }
                    _ => (),
                }
            }
            Ok(Event::End(ref e)) => {
                match e.name() {
                    b"row" => {
                        lines_in_cur_page += 1;
                        if lines_in_cur_page == display_lines.get() {
                            cur_page.length =
                                (reader.buffer_position() as u32 - cur_page.first) as u16;
                            lines_in_cur_page = 0;
                        }
                    }
                    _ => (),
                }
            }
            Ok(Event::Empty(e)) => match e.name() {
                b"row" => {
                    lines_in_cur_page += 1;
                    if lines_in_cur_page == display_lines.get() {
                        cur_page.length = (reader.buffer_position() as u32 - cur_page.first) as u16;
                        lines_in_cur_page = 0;
                    }
                }
                _ => (),
            },
            Ok(Event::Eof) => {
                cur_page.length = (reader.buffer_position() as u32 - cur_page.first) as u16;
                done = true;
            }
            Err(_) => return None,
            _ => (),
        }
        if cur_page.length != 0 {
            let total_pages = map.len() as PageNumber;
            map.insert(total_pages, cur_page.clone());
            cur_page.first += cur_page.length as u32;
            cur_page.length = 0;
        }

        // Apparently this minimises memory usage.
        buf.clear();
    }
    Some(map)
}

fn stringify(bookpath: *const c_char) -> String {
    let c_str = unsafe {
        assert!(!bookpath.is_null());
        CStr::from_ptr(bookpath)
    };
    c_str.to_str().unwrap().to_string()
}
