from django.shortcuts import render
from django.http import StreamingHttpResponse
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
import datetime
import csv

from rest_framework import status

from loggingapp.models import PageView
from loggingapp.serializers import PageViewSerializer
from common.views import GenericCRUDView
from party.models import Party
from partner.models import Partner

from django.db.models import Count, Min, Max

from netaddr import IPAddress

# Create your views here.

# top level uri: /session-logs/

# /page-views/
class PageViewCRUD(GenericCRUDView):
  queryset = PageView.objects.all()
  serializer_class = PageViewSerializer

  def get(self, request, format=None):
    params = request.GET
    obj = self.get_queryset()
    if 'startDate' in params:
      obj = obj.filter(pageViewDate__gte=params['startDate'])
    if 'endDate' in params:
      obj = obj.filter(pageViewDate__lte=params['endDate'])
    serializer = self.serializer_class(obj, many=True)
    return Response(serializer.data)

  def post(self,request, format=None):
    serializer = self.serializer_class(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, format=None):
    return Response({'message':'delete is not enabled for Page View'}, status=status.HTTP_400_BAD_REQUEST)

  def update(self, request):
    return Response({'message':'update is not enabled for Page View'}, status=status.HTTP_400_BAD_REQUEST)

# /sessions/counts/
class SessionCountView(generics.GenericAPIView):

  def get(self, request, format=None):
    startDate = request.GET.get('startDate')
    endDate = request.GET.get('endDate')
    ip = request.GET.get('ip')
    partyId = request.GET.get('partyId')

    filters = {}
    if startDate:
      filters['pageViewDate__gte']=startDate
    if endDate:
      filters['pageViewDate__lte']=endDate
    if ip:
      filters['ip']=ip
    if partyId:
      filters['partyId']=partyId

    distinctSessions = PageView.objects.values('sessionId').distinct().filter(**filters)
    return Response({'count':len(distinctSessions)})

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

def page_view_to_csv(request):
    """A view that streams a large CSV file."""
    pageViews = PageView.objects.all()

    params = request.GET
    if all(field in params for field in ['startDate', 'endDate', 'startIp', 'endIp', 'ipPref']):
        startDate = params['startDate']
        endDate = params['endDate']
        startIp = params['startIp']
        endIp = params['endIp']
        ipPref = params['ipPref']
    else:
        return Response({'error':'required fields: startDate, endDate, startIp, endIp, ipPref'}, status=status.HTTP_400_BAD_REQUEST)

    if startDate:
        pageViews = pageViews.filter(pageViewDate__gte=startDate)
    if endDate:
        pageViews = pageViews.filter(pageViewDate__lte=endDate)
    if startIp:
        startIp = IPAddress(startIp)
        pageViews = pageViews.filter(ip__gte=startIp)
    if endIp:
        endIp = IPAddress(endIp)
        pageViews = pageViews.filter(ip__lte=endIp)
    if ipPref:
        pageViews = pageViews.filter(ip__startswith=ipPref)

    pageViews = pageViews.values_list()

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(pageView) for pageView in pageViews),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    return response
