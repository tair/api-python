from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
import datetime

from loggingapp.models import Sessions2, PageViews2, PartySessionAffiliation, IpSessionAffiliation, IpTableForLogging
from loggingapp.serializers import sessionsSerializer, pageViewsSerializer
from subscription.models import Party
# Create your views here.

#Create a session
class SessionCreate(generics.CreateAPIView):
  queryset = Sessions2.objects.all()
  serializer_class = sessionsSerializer

#Session queries based on start, end and partId
class SessionList(generics.ListAPIView):
  serializer_class = sessionsSerializer
  def get_queryset(self):
    queryset = Sessions2.objects.all()
    startDate = self.request.QUERY_PARAMS.get('startDatetime', None)
    endDate = self.request.QUERY_PARAMS.get('endDatetime', None)
    partyId = self.request.QUERY_PARAMS.get('partyId', None)
    ipAddress = self.request.QUERY_PARAMS.get('ip', None)
    #TODO: Use Django Q objects to try all 6 cases - 1010, 0110, 1001, 0101, 100, 001
    #NOTE: In above 1s represent either start/end date that user provides and 0s are start and end date of session
    if startDate is not None: 
      start = getdatetime(startDate)
      queryset = queryset.filter(sessionStartDateTime__gte=start)
    if endDate is not None:
      end = getdatetime(endDate)
      queryset = queryset.filter(sessionStartDateTime__lte=end)
    if partyId is not None:
      psobjs = PartySessionAffiliation.objects.filter(partySessionAffiliationParty=partyId)
      queryset = queryset.filter(sessionId__in=psobjs.values('partySessionAffiliationSession'))
    if ipAddress is not None:
      ipobjs = IpTableForLogging.objects.filter(ipTableIp=ipAddress)
      ipsobjs = IpSessionAffiliation.objects.filter(ipSessionAffiliationIp_id__in=ipobjs.values('ipTableId'))
      queryset = queryset.filter(sessionId__in=ipsobjs.values('ipSessionAffiliationSession'))
    return queryset

#Add page view to session
class PageViewCreate(generics.CreateAPIView):
  queryset = PageViews2.objects.all()
  serializer_class = pageViewsSerializer
  def perform_create(self, serializer):
    if ("pageViewDateTime" in self.request.data) and ("pageViewSession" in self.request.data):
      su = Sessions2.objects.get(sessionId=self.request.data['pageViewSession'])
      su.sessionEndDateTime = self.request.data['pageViewDateTime']
      su.save()
    if ("partyId" in self.request.data) and ("pageViewSession" in self.request.data):
      PartySessionAffiliation( 
          partySessionAffiliationParty=Party.objects.get(partyId=self.request.data['partyId']),
          partySessionAffiliationSession=Sessions2.objects.get(sessionId=self.request.data['pageViewSession'])
      ).save()
    #TODO: Check and create new IP row
    if ("ipAddress" in self.request.data) and ("pageViewSession" in self.request.data):
      IpSessionAffiliation(
          ipSessionAffiliationIp=IpTableForLogging.objects.get(ipTableForLoggingIp=self.request.data['ipAddress']),
          ipSessionAffiliationSession = Sessions2.objects.get(sessionId=self.request.data['pageViewSession'])
      ).save()
    if serializer.is_valid():
      serializer.save()
     
#Page view queries based on start, end and partyId
class PageViewList(generics.ListAPIView):
  serializer_class = pageViewsSerializer
  def get_queryset(self):
    queryset = PageViews2.objects.all()
    startDate = self.request.QUERY_PARAMS.get('startDatetime', None)
    endDate = self.request.QUERY_PARAMS.get('endDatetime', None)
    partyId = self.request.QUERY_PARAMS.get('partyId', None)
    ipAddress = self.request.QUERY_PARAMS.get('ip', None)
    if startDate is not None:
      start = getdatetime(startDate)
      queryset = queryset.filter(pageViewDateTime__gte=start)
    if endDate is not None:
      end = getdatetime(endDate)
      queryset = queryset.filter(pageViewDateTime__lte=end)
    if partyId is not None:
      psobjs = PartySessionAffiliation.objects.filter(partySessionAffiliationParty=partyId)
      sobjs = Sessions2.objects.filter(sessionId__in=psobjs.values('partySessionAffiliationSession'))
      queryset = queryset.filter(pageViewSession__in=sobjs.values('sessionId'))
    if ipAddress is not None:
      ipobjs = IpTableForLogging.objects.filter(ipTableIp=ipAddress)
      ipsobjs = IpSessionAffiliation.objects.filter(ipSessionAffiliationIp_id__in=ipobjs.values('ipTableId'))
      sobjs = Sessions2.objects.filter(sessionId__in=ipsobjs.values('ipSessionAffiliationSession'))
      queryset = queryset.filter(pageViewSession__in=sobjs.values('sessionId'))
    return queryset
     
def getdatetime(datetimestring):
  print datetimestring
  datetimearr = datetimestring.split(" ")
  len(datetimearr)
  datearr = datetimearr[0].split("-")
  timearr = datetimearr[1].split(":")
  return datetime.datetime(int(datearr[0]), int(datearr[1]), int(datearr[2]), int(timearr[0]), int(timearr[1]), int(timearr[2]))
