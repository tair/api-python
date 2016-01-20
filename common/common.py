# The catch-all class to encapsulate any commonly used function that doen't (yet) deserve a dedicated class of its own.





def getIpAddress(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR') 
    if x_forwarded_for: 
        ip = x_forwarded_for.split(',')[0] 
    else: 
        ip = request.META.get('REMOTE_ADDR') 
    return ip        
