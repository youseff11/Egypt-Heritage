def user_profile_context(request):
    """Make user profile (avatar) available in all templates"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            return {'user_profile': profile}
        except Exception:
            return {'user_profile': None}
    return {'user_profile': None}
