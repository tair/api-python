#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from subscription.models import Party, Payment, Subscription, SubscriptionIpRange, SubscriptionTerm
from subscription.serializers import PartySerializer, PaymentSerializer, SubscriptionSerializer, SubscriptionIpRangeSerializer, SubscriptionTermSerializer

from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView

# top level: /subscriptions/

# /parties/
class Parties(APIView):
    def get(self, request, format=None):
        dataObj = Party.objects.all()
        serializer = PartySerializer(dataObj, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PartySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /payments/
class Payments(APIView):
    def get(self, request, format=None):
        dataObj = Payment.objects.all()
        serializer = PaymentSerializer(dataObj, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /payments/<primary_key>/
class PaymentsDetail(APIView):
    def get(self, request, pk, format=None):
        obj = Payment.objects.get(partyId=pk)
        serializer = PaymentSerializer(obj, many=True)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = Payment.objects.get(partyId=pk)
        serializer = PaymentSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = Payment.objects.get(partyId=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# /ipranges/
class IpRanges(APIView):
    def get(self, request, format=None):
        obj = SubscriptionIpRange.objects.all()
        serializer = SubscriptionIpRangeSerializer(obj, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SubscriptionIpRangeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /ipranges/<primary_key>/
class IpRangesDetail(APIView):

    def get(self, request, pk, format=None):
        obj = SubscriptionIpRange.objects.get(subscriptionIpRangeId=pk)
        serializer = SubscriptionIpRangeSerializer(dataObj, many=True)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = SubscriptionIpRange.objects.get(subscriptionIpRangeId=pk)
        serializer = SubscriptionIpRangeSerializer(dataObj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = SubscriptionIpRange.objects.get(subscriptionIpRangeId=pk)
        dataObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# /subscriptions/
class Subscriptions(APIView):
    availableQuerySet = {
        'ip',
    }

    def get(self, request, format=None):
        querySet = self.availableQuerySet.intersection(set(request.query_params))
        dataObj = None
        for key in querySet:
            value = request.GET.get(key)
            if key == 'ip':
                dataObj = Subscription.getByIp(value)

        if dataObj == None:
            #/subscriptions/ without query parameter returns all subscriptions
            dataObj = Subscription.objects.all()

        serializer = SubscriptionSerializer(dataObj, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /subscriptions/<primary_key>/
class SubscriptionsDetail(APIView):

    def get(self, request, pk, format=None):
        obj = Subscription.objects.get(partyId=pk)
        serializer = SubscriptionSerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = Subscription.objects.get(partyId=pk)
        serializer = SubscriptionSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = Subscription.objects.get(partyId=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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


# /terms/
class Terms(APIView):
    availableQuerySet = {
        'price',
        'period',
        'auto_renew',
        'group_discount_percentage',
    }
    def get(self, request, format=None):
        querySet = self.availableQuerySet.intersection(set(request.query_params))
        dataObj = SubscriptionTerm.objects.all()
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

    def post(self, request, format=None):
        serializer = SubscriptionTermSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /terms/<primary_key>/
class TermsDetail(APIView):

    def get(self, request, pk, format=None):
        obj = SubscriptionTerm.objects.get(subscriptionTermId=pk)
        serializer = SubscriptionTermSerializer([obj], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        obj = SubscriptionTerm.objects.get(subscriptionTermId=pk)
        serializer = SubscriptionTermSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = SubscriptionTerm.objects.get(subscriptionTermId=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
