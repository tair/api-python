#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from subscription.models import Party, Payment, Subscription, SubscriptionIpRange, SubscriptionTerm
from subscription.serializers import PartySerializer, PaymentSerializer, SubscriptionSerializer, SubscriptionIpRangeSerializer, SubscriptionTermSerializer

from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import generics


# top level: /subscriptions/

# Basic CRUD operation for Parties, Payments, IpRanges, Terms, Subscriptions
# /parties/
class PartiesList(generics.ListCreateAPIView):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

# /parties/<primary_key>
class PartiesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

# /payments/
class PaymentsList(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# /payments/<primary_key>/
class PaymentsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# /ipranges/
class IpRangesList(generics.ListCreateAPIView):
    queryset = SubscriptionIpRange.objects.all()
    serializer_class = SubscriptionIpRangeSerializer

# /ipranges/<primary_key>/
class IpRangesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionIpRange.objects.all()
    serializer_class = SubscriptionIpRangeSerializer

# /terms/
class TermsList(generics.ListCreateAPIView):
    queryset = SubscriptionTerm.objects.all()
    serializer_class = SubscriptionTermSerializer

# /terms/<primary_key>/
class TermsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionTerm.objects.all()
    serializer_class = SubscriptionTermSerializer

# /subscriptions/
class SubscriptionsList(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

# /subscriptions/<primary_key>/
class SubscriptionsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

#------------------- End of Basic CRUD operations --------------


# Specific queries

# /subscriptions/active/
class SubscriptionsActive(APIView):
    availableQuerySet = {
        'partyid',
        'ip',
    }

    def get(self, request, format=None):
        querySet = self.availableQuerySet.intersection(set(request.query_params))
        obj = None
        for key in querySet:
            value = request.GET.get(key)
            if key == 'partyid':
                obj = Subscription.getActiveById(value)
            elif key == 'ip':
                obj = Subscription.getActiveByIp(value)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if obj == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscriptionSerializer(obj, many=True)
        return Response(serializer.data)

# /subscriptions/<primary key>/payments
class SubscriptionsPayments(APIView):
    def get(self, request, pk, format=None):
        obj = Payment.objects.filter(partyId=pk)
        serializer = PaymentSerializer(obj, many=True)
        return Response(serializer.data)

# /subscriptions/<primary key>/prices
class SubscriptionsPrices(APIView):
    def get(self, request, pk, format=None):
        obj = SubscriptionTerm.getByPartyId(pk)
        serializer = SubscriptionTermSerializer(obj, many=True)
        return Response(serializer.data)

# /terms/query/
class TermsQuery(APIView):
    availableQuerySet = {
        'price',
        'period',
        'auto_renew',
        'group_discount_percentage',
    }
    def get(self, request, format=None):
        querySet = self.availableQuerySet.intersection(set(request.query_params))
        dataObj = []
        for key in querySet:
            value = request.GET.get(key)
            if key == 'price':
                dataObj = dataObj.filter(price=value)
            elif key == 'period':
                dataObj = dataObj.filter(period=value)
            elif key == 'auto_renew':
                dataObj = dataObj.filter(autoRenew=value)
            elif key == 'group_discount_percentage':
                dataObj = dataObj.filter(groupDiscountPercentage=value)
        serializer = SubscriptionTermSerializer(dataObj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
