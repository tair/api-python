from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
import datetime

from loggingapp.models import Sessions2, PageViews2, PartySessionAffiliation, IpSessionAffiliation, IpTableForLogging
from loggingapp.serializers import sessionsSerializer, pageViewsSerializer
from party.models import Party
from partner.models import Partner

# Create your views here.

#Create and list sessions. Session queries based on start, end and partId
class SessionListCreate(generics.ListCreateAPIView):
  serializer_class = sessionsSerializer
  def get_queryset(self):
    queryset = Partner.filters(self, Sessions2.objects.all(), "sessionPartnerId") 
    startDate = self.request.QUERY_PARAMS.get('startDatetime', None)
    endDate = self.request.QUERY_PARAMS.get('endDatetime', None)
    partyId = self.request.QUERY_PARAMS.get('partyId', None)
    ipAddress = self.request.QUERY_PARAMS.get('ip', None)
    sessionId = self.request.QUERY_PARAMS.get('sessionId', None)
    if queryset:
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
      if sessionId is not None:
        queryset = queryset.filter(sessionId=sessionId)
    return queryset
      

#Create and list PageViews. Page view queries based on start, end and partyId
class PageViewListCreate(generics.ListCreateAPIView):
  serializer_class = pageViewsSerializer
  def get_queryset(self):
    allsessions = Partner.filters(self, Sessions2.objects.all(), "sessionPartnerId")
    if not allsessions:
      print "No Sessions for this partnerId"
      queryset = PageViews2.objects.none()
    else:
      queryset = PageViews2.objects.filter(pageViewSession_id__in=allsessions.values('sessionId'))
      print allsessions.values('sessionId')
      print PageViews2.objects.first().pageViewSession
      startDate = self.request.QUERY_PARAMS.get('startDatetime', None)
      endDate = self.request.QUERY_PARAMS.get('endDatetime', None)
      partyId = self.request.QUERY_PARAMS.get('partyId', None)
      ipAddress = self.request.QUERY_PARAMS.get('ip', None)
      sessionId = self.request.QUERY_PARAMS.get('sessionId', None)
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
      if sessionId is not None:
        queryset = queryset.filter(pageViewSession=sessionId)
    return queryset
  def perform_create(self, serializer):
    partnerId = self.request.QUERY_PARAMS.get('partnerId', None)
    if (self.request.QUERY_PARAMS.get('sessionId', None) is not None):
      session = self.request.QUERY_PARAMS.get('sessionId')
    elif ("pageViewSession" in self.request.data):
      session = self.request.data['pageViewSession']
    else:
      session = None
    if ("pageViewDateTime" in self.request.data) and (session is not None):
      su = Sessions2.objects.get(sessionId=session)
      su.sessionEndDateTime = self.request.data['pageViewDateTime']
      su.save()
    if ("partyId" in self.request.data) and (session is not None):
      PartySessionAffiliation(
          partySessionAffiliationParty=Party.objects.get(partyId=self.request.data['partyId']),
          partySessionAffiliationSession=Sessions2.objects.get(sessionId=session)
      ).save()
    if ("ipAddress" in self.request.data) and (session is not None):
      IpSessionAffiliation(
          ipSessionAffiliationIp=IpTableForLogging.objects.get(ipTableForLoggingIp=self.request.data['ipAddress']),
          ipSessionAffiliationSession = Sessions2.objects.get(sessionId=session)
      ).save()
    if (partnerId is not None) and (session is not None):
      if ( Sessions2.objects.get(sessionId=session).sessionPartnerId.partnerId == partnerId ):
        if serializer.is_valid():
          serializer.save()
     
def getdatetime(datetimestring):
  print datetimestring
  datetimearr = datetimestring.split(" ")
  len(datetimearr)
  datearr = datetimearr[0].split("-")
  timearr = datetimearr[1].split(":")
  return datetime.datetime(int(datearr[0]), int(datearr[1]), int(datearr[2]), int(timearr[0]), int(timearr[1]), int(timearr[2]))
