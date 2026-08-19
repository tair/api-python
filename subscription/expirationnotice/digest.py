from collections import namedtuple

from common.utils.dateUtils import relativedelta_sort_key

Due = namedtuple('Due', ['lead_time', 'expiring'])


def render(due):
    return '\n\n'.join(_section(group) for group in _soonest_first(due)) + '\n'


def _soonest_first(due):
    return sorted(due, key=lambda group: relativedelta_sort_key(group.lead_time))


def _section(group):
    heading = _heading(group.lead_time)
    lines = [heading, '-' * len(heading)]
    for expiring in group.expiring:
        lines.append(_line(expiring))
    return '\n'.join(lines)


def _heading(lead_time):
    return 'Expiring within %s' % _in_words(lead_time)


def _in_words(lead_time):
    count, unit = _largest_whole_unit(lead_time)
    if count == 1:
        return 'a %s' % unit
    return '%d %ss' % (count, unit)


def _largest_whole_unit(lead_time):
    if lead_time.years and not lead_time.months:
        return lead_time.years, 'year'
    months = lead_time.years * 12 + lead_time.months
    if months:
        return months, 'month'
    if lead_time.days and lead_time.days % 7 == 0:
        return lead_time.days // 7, 'week'
    if lead_time.days:
        return lead_time.days, 'day'
    raise ValueError('no wording for %r' % lead_time)


def _line(expiring):
    return '  %s  %s  (%s, %s)' % (
        expiring.end_date.strftime('%Y-%m-%d'),
        expiring.name,
        expiring.partner_id,
        expiring.party_type,
    )
