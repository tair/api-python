# The catch-all container for any commonly used classes/functions that don't (yet) deserve dedicated containers of their own.
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from netaddr import IPAddress, IPRange, IPNetwork

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

# validate ip range based on a series of conditions
def validateIpRange(start, end):
    if isIpRangePrivate(start, end):
        raise serializers.ValidationError({'IP Range': _('IP range contains private IP: %s - %s' % (start, end))})
    if not validateIpRangeSize(start, end):
        raise serializers.ValidationError({'IP Range': _('IP range too large: %s - %s' % (start, end))})

# check if the ip range is private
def isIpRangePrivate(start, end):
    if IPAddress(start).is_private() or IPAddress(end).is_private():
        return True
    ipRange = IPRange(start, end)
    if ipRange.__getstate__()[2] == 4:
        for cidr in IPV4_PRIVATE:

            if ipRange.__contains__(cidr):
                return True
    if ipRange.__getstate__()[2] == 6:
        for cidr in IPV6_PRIVATE:
            if ipRange.__contains__(cidr):
                return True
    return False

IPV4_PRIVATE = (
    IPNetwork('10.0.0.0/8'),  # Class A private network local communication (RFC 1918)
    IPNetwork('100.64.0.0/10'),  # Carrier grade NAT (RFC 6598)
    IPNetwork('172.16.0.0/12'),  # Private network - local communication (RFC 1918)
    IPNetwork('192.0.0.0/24'),  # IANA IPv4 Special Purpose Address Registry (RFC 5736)
    IPNetwork('192.168.0.0/16'),  # Class B private network local communication (RFC 1918)
    IPNetwork('198.18.0.0/15'),  # Testing of inter-network communications between subnets (RFC 2544)
    IPRange('239.0.0.0', '239.255.255.255'),  # Administrative Multicast
)

IPV6_PRIVATE = (
    IPNetwork('fc00::/7'),  # Unique Local Addresses (ULA)
    IPNetwork('fec0::/10'),  # Site Local Addresses (deprecated - RFC 3879)
)

# check if the ip range is over the limit
def validateIpRangeSize(start, end):
    ipRange = IPRange(start, end)
    if ipRange.__getstate__()[2] == 4:
        return True if ipRange.size <= 65536 else False
    if ipRange.__getstate__()[2] == 6:
        return True if ipRange.size <= 324518553658426726783156020576256 else False
