# The catch-all container for any commonly used classes/functions that don't (yet) deserve dedicated containers of their own.


# Determine IP address of the host from which the given request has been received.
#
def getRemoteIpAddress(request):
 
    # If the request comes through an HTTP proxy, use the first of the IP addresses specified in the XFF header.     
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR') 
    if x_forwarded_for: 
        ip = x_forwarded_for.split(',')[0] 
    else: 
        ip = request.META.get('REMOTE_ADDR') 
    return ip        
