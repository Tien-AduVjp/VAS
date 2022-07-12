def bypass_karma_check_and_execute(user, karma_required, method, args=[], kwarg={}):
    """ Temporary add the missing karma to cache to pass the karma check,
        then execute method, and finally invalidate the cache.
    """
    user = user.sudo()
    user.env.cache.update(user, user._fields.get('karma'), [karma_required])
    res = method(*args, **kwarg)
    user.invalidate_cache(['karma'], user.ids)
    return res
