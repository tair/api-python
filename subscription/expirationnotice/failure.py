def render(run_date, trace):
    return 'The expiring-subscription notifier failed on %s.\n\n%s' % (
        run_date.strftime('%Y-%m-%d %H:%M:%S'),
        trace,
    )
