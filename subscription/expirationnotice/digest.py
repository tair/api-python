from django.utils.html import escape

BODY_STYLE = ('margin: 0; padding: 16px 16px 24px; color: #222222; '
              'font-family: Helvetica, Arial, sans-serif; font-size: 14px;')
TABLE_STYLE = 'border-collapse: collapse;'
TH_STYLE = ('padding: 0 24px 4px 0; text-align: left; font-weight: bold; '
            'white-space: nowrap; border-bottom: 1px solid #999999;')
HEADING_STYLE = ('padding: 18px 24px 4px 0; text-align: left; '
                 'font-weight: bold; white-space: nowrap;')
TD_STYLE = ('padding: 4px 24px 4px 0; text-align: left; '
            'vertical-align: top; border-bottom: 1px solid #dddddd;')
DATE_STYLE = TD_STYLE + ' white-space: nowrap;'

COLUMNS = ('Ends', 'Institution', 'Started')


def render(subscriptions, bounds):
    # One table across every section, so the columns line up down the whole
    # message rather than being re-measured per section.
    return '<html><body style="%s"><table style="%s">%s%s</table></body></html>' % (
        BODY_STYLE,
        TABLE_STYLE,
        _column_headings(),
        ''.join(_section(horizon, within)
                for horizon, within in _group_by_horizon(subscriptions, bounds)),
    )


def _group_by_horizon(subscriptions, bounds):
    sections = []
    remaining = subscriptions
    for horizon, cutoff in bounds:
        within = [s for s in remaining if s.end_date <= cutoff]
        remaining = [s for s in remaining if s.end_date > cutoff]
        if within:
            sections.append((horizon, within))
    return sections


def _column_headings():
    return '<tr>%s</tr>' % ''.join(
        '<th style="%s">%s</th>' % (TH_STYLE, column) for column in COLUMNS
    )


def _section(horizon, subscriptions):
    return '%s%s' % (
        _heading_row(horizon),
        ''.join(_row(subscription) for subscription in subscriptions),
    )


def _heading_row(horizon):
    return '<tr><th colspan="%d" style="%s">%s</th></tr>' % (
        len(COLUMNS), HEADING_STYLE, escape(_heading(horizon)),
    )


def _heading(horizon):
    return 'Expiring within %s' % _in_words(horizon)


def _in_words(horizon):
    count, unit = _largest_whole_unit(horizon)
    if count == 1:
        return 'a %s' % unit
    return '%d %ss' % (count, unit)


def _largest_whole_unit(horizon):
    if horizon.years and not horizon.months:
        return horizon.years, 'year'
    months = horizon.years * 12 + horizon.months
    if months:
        return months, 'month'
    if horizon.days and horizon.days % 7 == 0:
        return horizon.days // 7, 'week'
    if horizon.days:
        return horizon.days, 'day'
    raise ValueError('no wording for %r' % horizon)


def _row(subscription):
    cells = (
        (DATE_STYLE, _date(subscription.end_date)),
        (TD_STYLE, subscription.name),
        (DATE_STYLE, _date(subscription.start_date)),
    )
    return '<tr>%s</tr>' % ''.join(
        '<td style="%s">%s</td>' % (style, escape(value)) for style, value in cells
    )


def _date(moment):
    if moment is None:
        return ''
    return moment.strftime('%Y-%m-%d')
