//! Everything that differs by operating system, in one place.
//!
//! The decision of what to do on each OS lives in pure functions that take their inputs (`python_for`), so they are tested on
//! every host. The `#[cfg]` wrappers only call the C library; a failure falls back to offset 0, as the Unix error path does.

/// The OS family a decision is made for.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Os {
    Unix,
    Windows,
}

/// The family this binary was compiled for.
pub(crate) const OS: Os = if cfg!(windows) { Os::Windows } else { Os::Unix };

/// The interpreter the Python fallback is spawned with.
///
/// `python3` on Windows too: the Python rows of `hooks.json` (SessionStart's install among them) start `python3`, so a
/// machine the plugin runs on has one, while `python` may be missing or only the Microsoft Store stub.
pub(crate) fn python_for(os: Os) -> &'static str {
    match os {
        Os::Unix | Os::Windows => "python3",
    }
}

/// The command that starts the Python interpreter on this OS.
pub(crate) fn python_cmd() -> &'static str {
    python_for(OS)
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

    #[test]
    fn python_names() {
        assert_eq!(python_for(Os::Unix), "python3");
        assert_eq!(python_for(Os::Windows), "python3");
    }

    #[test]
    fn host_family_matches_its_wrappers() {
        assert_eq!(python_cmd(), python_for(OS));
        assert_eq!(OS == Os::Windows, cfg!(windows));
    }

    #[test]
    fn local_offset_is_a_sane_zone_offset() {
        let off = local_offset(1_700_000_000);
        assert!((-14 * 3600..=14 * 3600).contains(&off));
    }
}
