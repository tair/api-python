def render(subscriptions, bounds):
    return '\n\n'.join(
        _section(horizon, within)
        for horizon, within in _group_by_horizon(subscriptions, bounds)
    ) + '\n'


def _group_by_horizon(subscriptions, bounds):
    sections = []
    remaining = subscriptions
    for horizon, cutoff in bounds:
        within = [s for s in remaining if s.end_date <= cutoff]
        remaining = [s for s in remaining if s.end_date > cutoff]
        if within:
            sections.append((horizon, within))
    return sections


def _section(horizon, subscriptions):
    heading = _heading(horizon)
    lines = [heading, '-' * len(heading)]
    for subscription in subscriptions:
        lines.append(_line(subscription))
    return '\n'.join(lines)


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


def _line(subscription):
    parenthetical = [subscription.party_type]
    if subscription.start_date is not None:
        parenthetical.append('started %s'
                             % subscription.start_date.strftime('%Y-%m-%d'))
    return '  %s  %s  (%s)' % (
        subscription.end_date.strftime('%Y-%m-%d'),
        subscription.name,
        ', '.join(parenthetical),
    )
