




def is_admin(user):
    '''return true if the user belongs to the admin group, false otherwise'''
    return(user.groups.filter(name='admin').exists())
