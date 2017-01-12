from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework_jwt.utils import jwt_decode_handler
from authentication.models import Credential
from party.models import Party

import logging

class GenericCRUDView(generics.GenericAPIView):
    logging.basicConfig(filename="/var/log/api/api.log", format='%(asctime)s %(message)s')
    requireApiKey = True
    def get_queryset(self):
        queryset = super(GenericCRUDView, self).get_queryset()
        params = self.request.GET
        for key in params:
            if key in queryset.model._meta.get_all_field_names():
                value = params[key]
                filters = {key:value}
                try:
                    queryset = queryset.filter(**filters)
                except ValueError:
                    return []
        return queryset

    def get(self, request, format=None):
        serializer_class = self.get_serializer_class()
        params = request.GET
        obj = self.get_queryset()
        serializer = serializer_class(obj, many=True)
        return Response(serializer.data)

    def put(self, request, format=None):
        serializer_class = self.get_serializer_class()
        params = request.GET
        # does not allow user to update everything, too dangerous
        if not params:
            return Response({'error':'does not allow update without query parameters'})
        obj = self.get_queryset()
        ret = []
        for entry in obj:
            serializer = serializer_class(entry, data=request.data)
            if serializer.is_valid():
                serializer.save()
                ret.append(serializer.data)
        return Response(ret)

    def post(self, request, format=None):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        params = request.GET
        # does not allow user to update everything, too dangerous
        if not params:
            return Response({'error':'does not allow delete without query parameters'})
        obj = self.get_queryset()
        for entry in obj:
            entry.delete()
        return Response({'success':'delete complete'})

    def getPermission(self, request, roleList):
        token = ''
        for item in request.META.items():
            if item[0] == 'HTTP_AUTHORIZATION':
                token = item[1].split(' ')[1]
        decode = jwt_decode_handler(token)
        user_id = decode['user_id']
        partyId = None
        partyType = ''
        if Credential.objects.all().filter(user_id=user_id).exists():
            partyId = Credential.objects.get(user_id=user_id).partyId.partyId
            partyType = Party.objects.all().get(partyId=partyId).partyType

        for role in roleList:
            if partyType == role:
                return True
        return False

