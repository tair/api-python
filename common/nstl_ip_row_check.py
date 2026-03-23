# Shared NSTL Excel row validation (size, private, overlap, exact match).
# Used by scripts/NSTLLoadIPCheck.py and scripts/NSTLLoadIPRange.py (Python 2).

import numbers

try:
    basestring
except NameError:
    basestring = str

from netaddr import IPAddress

from common.common import (
    exact_match_exists,
    get_overlapping_ranges,
    ip2long,
    isIpRangePrivate,
    validateIpRangeSize,
)


def normalize_excel_serial_id(serial_id):
    """
    Match party serialId (CharField) after pandas/openpyxl infers float (e.g. 12345.0).
    """
    if serial_id is None or serial_id == '':
        return ''
    try:
        if serial_id != serial_id:
            return ''
    except TypeError:
        pass
    if isinstance(serial_id, float):
        i = int(serial_id)
        if serial_id == i:
            return str(i)
        return str(serial_id)
    if isinstance(serial_id, numbers.Integral) and not isinstance(serial_id, bool):
        return str(serial_id)
    s = str(serial_id).strip()
    try:
        f = float(s)
        if f == int(f):
            return str(int(f))
    except (TypeError, ValueError, OverflowError):
        pass
    return s


def ip_check_error_row(serial_id, cn_name, en_name, start, end, error, ip_range_id=''):
    """Seven columns for errdf; keep ip range id empty when not a DB row."""
    return [serial_id, cn_name, en_name, start, end, error, ip_range_id]


def _coerce_ip_cell(val):
    """Normalize Excel cell to a stripped string (handles float/int from pandas/openpyxl)."""
    if val is None:
        return ''
    try:
        if isinstance(val, float) and val != val:
            return ''
    except Exception:
        pass
    if isinstance(val, basestring):
        return val.strip()
    return str(val).strip()


def validate_nstl_row_for_load(serial_id, cn_name, en_name, start, end, IpRange):
    """
    Same rules as NSTLLoadIPCheck: row is OK to load only if it passes all checks
    and does not overlap existing active ranges (except exact match, which is blocked).

    Returns (ok_to_load, err_rows, to_ignore_add, to_expire_add, start_norm, end_norm).
    start_norm/end_norm are coerced strings (for DB load when ok_to_load is True).
    err_rows is a list of 7-tuples/lists for the error DataFrame.
    to_ignore_add / to_expire_add are sets of str(ipRangeId) for checker reporting.
    """
    to_ignore_add = set()
    to_expire_add = set()
    err_rows = []

    start = _coerce_ip_cell(start)
    end = _coerce_ip_cell(end)
    if start and not end:
        end = start
    if end and not start:
        start = end
    if not start or not end:
        err_rows.append(ip_check_error_row(serial_id, cn_name, en_name, start, end, 'ip range invalid'))
        return False, err_rows, to_ignore_add, to_expire_add, start, end

    if not validateIpRangeSize(start, end):
        err_rows.append(ip_check_error_row(serial_id, cn_name, en_name, start, end, 'ip range too large'))
        return False, err_rows, to_ignore_add, to_expire_add, start, end

    if isIpRangePrivate(start, end):
        err_rows.append(ip_check_error_row(serial_id, cn_name, en_name, start, end, 'ip range private'))
        return False, err_rows, to_ignore_add, to_expire_add, start, end

    if start.startswith('255') or end.startswith('255'):
        err_rows.append(ip_check_error_row(serial_id, cn_name, en_name, start, end, 'ip range invalid'))
        return False, err_rows, to_ignore_add, to_expire_add, start, end

    try:
        IPAddress(start)
        IPAddress(end)
    except Exception:
        err_rows.append(ip_check_error_row(serial_id, cn_name, en_name, start, end, 'ip range invalid'))
        return False, err_rows, to_ignore_add, to_expire_add, start, end

    if exact_match_exists(start, end, IpRange):
        existing = get_overlapping_ranges(start, end, IpRange)
        try:
            s_long = ip2long(start)
            e_long = ip2long(end)
        except Exception:
            s_long, e_long = None, None
        for ipRange in existing:
            if s_long is not None and ipRange.startLong == s_long and ipRange.endLong == e_long:
                err_rows.append(ip_check_error_row(serial_id, cn_name, en_name, start, end, 'ip range exists'))
                err_rows.append(ip_check_error_row(
                    ipRange.partyId.serialId if ipRange.partyId.serialId else '', '', ipRange.partyId.name,
                    ipRange.start, ipRange.end, 'ip range exists', ipRange.ipRangeId))
                to_ignore_add.add(str(ipRange.ipRangeId))
        if not err_rows:
            err_rows.append(ip_check_error_row(
                serial_id, cn_name, en_name, start, end, 'ip range exists'))
        return False, err_rows, to_ignore_add, to_expire_add, start, end

    overlapping = get_overlapping_ranges(start, end, IpRange)
    overlap = False
    for ipRange in overlapping:
        range_serial = str(ipRange.partyId.serialId) if ipRange.partyId.serialId else ''
        range_names = ipRange.partyId.name
        range_ids_str = str(ipRange.ipRangeId)
        start_val = IPAddress(start)
        end_val = IPAddress(end)
        range_start = IPAddress(ipRange.start)
        range_end = IPAddress(ipRange.end)
        same_inst = serial_id == range_serial

        if start_val >= range_start and end_val <= range_end:
            overlap = True
            err_rows.append(ip_check_error_row(serial_id, cn_name, en_name, start, end, 'ip range contained'))
            err_rows.append(ip_check_error_row(range_serial, '', range_names, ipRange.start, ipRange.end, 'ip range contained', range_ids_str))
            to_ignore_add.add(str(ipRange.ipRangeId))
        elif start_val <= range_start and end_val >= range_end:
            overlap = True
            if same_inst:
                err_rows.append(ip_check_error_row(serial_id, cn_name, en_name, start, end, 'ip range contain existing in same institution'))
                err_rows.append(ip_check_error_row(range_serial, '', range_names, ipRange.start, ipRange.end, 'ip range contain existing in same institution', range_ids_str))
            else:
                err_rows.append(ip_check_error_row(serial_id, cn_name, en_name, start, end, 'ip range contain existing in different institution'))
                err_rows.append(ip_check_error_row(range_serial, '', range_names, ipRange.start, ipRange.end, 'ip range contain existing in different institution', range_ids_str))
            to_expire_add.add(str(ipRange.ipRangeId))
        else:
            overlap = True
            if same_inst:
                err_rows.append(ip_check_error_row(serial_id, cn_name, en_name, start, end, 'ip range overlap in same institution'))
                err_rows.append(ip_check_error_row(range_serial, '', range_names, ipRange.start, ipRange.end, 'ip range overlap in same institution', range_ids_str))
            else:
                err_rows.append(ip_check_error_row(serial_id, cn_name, en_name, start, end, 'ip range overlap in different institution'))
                err_rows.append(ip_check_error_row(range_serial, '', range_names, ipRange.start, ipRange.end, 'ip range overlap in different institution', range_ids_str))
            to_expire_add.add(str(ipRange.ipRangeId))

    if overlap:
        return False, err_rows, to_ignore_add, to_expire_add, start, end

    return True, [], to_ignore_add, to_expire_add, start, end
