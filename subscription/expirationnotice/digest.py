from django.utils.html import escape

BODY_STYLE = ('margin: 0; padding: 16px 16px 24px; color: #222222; '
              'font-family: Helvetica, Arial, sans-serif; font-size: 14px;')
TABLE_STYLE = 'border-collapse: collapse;'
TH_STYLE = ('padding: 0 24px 4px 0; text-align: left; font-weight: bold; '
            'white-space: nowrap; border-bottom: 1px solid #999999;')
TD_STYLE = ('padding: 4px 24px 4px 0; text-align: left; '
            'vertical-align: top; border-bottom: 1px solid #dddddd;')
DATE_STYLE = TD_STYLE + ' white-space: nowrap;'

COLUMNS = ('Ends', 'Institution', 'Started')


def render(subscriptions):
    return '<html><body style="%s"><table style="%s">%s%s</table></body></html>' % (
        BODY_STYLE,
        TABLE_STYLE,
        _column_headings(),
        ''.join(_row(subscription) for subscription in subscriptions),
    )


def _column_headings():
    return '<tr>%s</tr>' % ''.join(
        '<th style="%s">%s</th>' % (TH_STYLE, column) for column in COLUMNS
    )


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
