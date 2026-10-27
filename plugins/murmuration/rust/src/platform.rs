//! Everything that differs by operating system, in one place.
//!
//! The decision of what to do on each OS lives in pure functions that take their inputs (`home_from`, `python_for`), so they are
//! tested on every host. The `#[cfg]` wrappers only read the environment or call the C library. No Windows arm may return a value
//! that allows what Unix would deny: a failure falls back to offset 0, no home (the path stays unexpanded), a path that cannot be
//! opened, or a failed spawn, as the Unix error paths do.

use std::ffi::OsString;
use std::path::PathBuf;

/// The OS family a decision is made for.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Os {
    Unix,
    Windows,
}

/// The family this binary was compiled for.
const OS: Os = if cfg!(windows) { Os::Windows } else { Os::Unix };

/// The home directory named by the environment variables, as text.
///
/// Unix reads `HOME` only (an empty value is kept, as `os.path.expanduser` keeps it); the caller falls back to the passwd entry.
/// Windows reads `USERPROFILE`, then `HOME`; an empty value counts as absent, so the path stays unexpanded.
pub(crate) fn home_from(home: Option<OsString>, userprofile: Option<OsString>, os: Os) -> Option<String> {
    let chosen = match os {
        Os::Unix => home,
        Os::Windows => userprofile.filter(|v| !v.is_empty()).or_else(|| home.filter(|v| !v.is_empty())),
    };
    chosen.map(|h| h.to_string_lossy().to_string())
}

/// The interpreter the Python fallback is spawned with.
pub(crate) fn python_for(os: Os) -> &'static str {
    match os {
        Os::Unix => "python3",
        Os::Windows => "python",
    }
}

/// The family this binary was compiled for, as the guard's default flavour of paths and program names.
pub(crate) const fn host() -> Os {
    OS
}

/// The home directory the environment names, read as `os` reads it (no passwd or shell-folder fallback): what the guard's Windows reading of `~` uses on any host.
pub(crate) fn home_for(os: Os) -> Option<String> {
    home_from(std::env::var_os("HOME"), std::env::var_os("USERPROFILE"), os)
}

/// The home directory of the current user, or `None` when there is none to expand `~` to.
pub(crate) fn home_dir() -> Option<String> {
    let found = home_from(std::env::var_os("HOME"), std::env::var_os("USERPROFILE"), OS);
    found.or_else(|| std::env::home_dir().map(|h| h.to_string_lossy().to_string()))
}

/// The command that starts the Python interpreter on this OS.
pub(crate) fn python_cmd() -> &'static str {
    python_for(OS)
}

/// The path whose bytes are `bytes`.
#[cfg(unix)]
pub(crate) fn path_from_bytes(bytes: Vec<u8>) -> PathBuf {
    use std::os::unix::ffi::OsStringExt;
    PathBuf::from(OsString::from_vec(bytes))
}

/// The path whose bytes are `bytes`; bytes that are not UTF-8 give an empty path, which cannot be opened (never an allow).
#[cfg(windows)]
pub(crate) fn path_from_bytes(bytes: Vec<u8>) -> PathBuf {
    String::from_utf8(bytes).map_or_else(|_| PathBuf::new(), PathBuf::from)
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

/// Offset east of UTC in seconds of the local zone at `epoch_s`; 0 when the C runtime cannot say.
///
/// The MSVC CRT has no `tm_gmtoff`: the local broken-down time read back as if it were UTC (`_mkgmtime64`) differs from `epoch_s` by the offset.
#[cfg(windows)]
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
    }
    extern "C" {
        fn _localtime64_s(out: *mut Tm, t: *const i64) -> i32;
        fn _mkgmtime64(tm: *mut Tm) -> i64;
    }
    let mut tm = Tm { sec: 0, min: 0, hour: 0, mday: 0, mon: 0, year: 0, wday: 0, yday: 0, isdst: 0 };
    // SAFETY: `tm` is a valid, writable struct with the layout of the CRT's `struct tm` (nine ints); `_localtime64_s` only writes into it and reads `epoch_s`.
    let status = unsafe { _localtime64_s(&mut tm, &epoch_s) };
    if status != 0 {
        return 0;
    }
    // SAFETY: `tm` was filled by `_localtime64_s` above; `_mkgmtime64` reads it and may normalise its fields.
    let as_utc = unsafe { _mkgmtime64(&mut tm) };
    if as_utc == -1 {
        0
    } else {
        as_utc - epoch_s
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn os(s: &str) -> Option<OsString> {
        Some(OsString::from(s))
    }

    #[test]
    fn unix_reads_home_only() {
        assert_eq!(home_from(os("/h"), os("C:\\u"), Os::Unix), Some("/h".to_string()));
        assert_eq!(home_from(None, os("C:\\u"), Os::Unix), None);
        assert_eq!(home_from(None, None, Os::Unix), None);
    }

    #[test]
    fn unix_keeps_an_empty_home() {
        assert_eq!(home_from(os(""), os("C:\\u"), Os::Unix), Some(String::new()));
    }

    #[test]
    fn windows_prefers_userprofile_then_home() {
        assert_eq!(home_from(os("/h"), os("C:\\u"), Os::Windows), Some("C:\\u".to_string()));
        assert_eq!(home_from(os("/h"), None, Os::Windows), Some("/h".to_string()));
        assert_eq!(home_from(None, os("C:\\u"), Os::Windows), Some("C:\\u".to_string()));
    }

    #[test]
    fn windows_treats_empty_and_absent_as_no_home() {
        assert_eq!(home_from(None, None, Os::Windows), None);
        assert_eq!(home_from(os(""), os(""), Os::Windows), None);
        assert_eq!(home_from(os("/h"), os(""), Os::Windows), Some("/h".to_string()));
        assert_eq!(home_from(os(""), None, Os::Windows), None);
    }

    #[test]
    fn python_names() {
        assert_eq!(python_for(Os::Unix), "python3");
        assert_eq!(python_for(Os::Windows), "python");
    }

    #[test]
    fn host_family_matches_its_wrappers() {
        assert_eq!(python_cmd(), python_for(OS));
        assert_eq!(OS == Os::Windows, cfg!(windows));
    }

    #[cfg(unix)]
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
