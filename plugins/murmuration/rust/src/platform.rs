//! Everything that differs by operating system, in one place. This step holds the Unix arms only, moved unchanged.

use std::ffi::OsString;
use std::path::PathBuf;

/// The home directory of the current user: `HOME`, then the passwd entry; `None` when there is none to expand `~` to.
pub(crate) fn home_dir() -> Option<String> {
    match std::env::var_os("HOME") {
        Some(h) => Some(h.to_string_lossy().to_string()),
        None => std::env::home_dir().map(|h| h.to_string_lossy().to_string()),
    }
}

/// The command that starts the Python interpreter.
pub(crate) fn python_cmd() -> &'static str {
    "python3"
}

/// The path whose bytes are `bytes`.
#[cfg(unix)]
pub(crate) fn path_from_bytes(bytes: Vec<u8>) -> PathBuf {
    use std::os::unix::ffi::OsStringExt;
    PathBuf::from(OsString::from_vec(bytes))
}

/// Offset east of UTC in seconds of the local zone at `epoch_s`; 0 when the C library cannot say.
#[cfg(unix)]
#[allow(unsafe_code)]
pub(crate) fn local_offset(epoch_s: i64) -> i64 {
    #[repr(C)]
    struct Tm {
        sec: i32,
        min: i32,
        hour: i32,
        mday: i32,
        mon: i32,
        year: i32,
        wday: i32,
        yday: i32,
        isdst: i32,
        gmtoff: i64,
        zone: *const u8,
    }
    extern "C" {
        fn localtime_r(t: *const i64, out: *mut Tm) -> *mut Tm;
    }
    let mut tm = Tm { sec: 0, min: 0, hour: 0, mday: 0, mon: 0, year: 0, wday: 0, yday: 0, isdst: 0, gmtoff: 0, zone: std::ptr::null() };
    // SAFETY: `tm` is a valid, writable struct with the layout of C's `struct tm` on macOS and Linux (nine ints, then a long and a pointer); `localtime_r` only writes into it.
    let ok = unsafe { !localtime_r(&epoch_s, &mut tm).is_null() };
    if ok {
        tm.gmtoff
    } else {
        0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn python_name() {
        assert_eq!(python_cmd(), "python3");
    }

    #[test]
    fn unix_path_keeps_every_byte() {
        use std::os::unix::ffi::OsStrExt;
        let p = path_from_bytes(vec![b'/', 0xff, b'a']);
        assert_eq!(p.as_os_str().as_bytes(), &[b'/', 0xff, b'a']);
    }

    #[test]
    fn local_offset_is_a_sane_zone_offset() {
        let off = local_offset(1_700_000_000);
        assert!((-14 * 3600..=14 * 3600).contains(&off));
    }
}
