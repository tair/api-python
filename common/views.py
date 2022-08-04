from rest_framework.response import Response
from rest_framework import generics, status
from django.db import models

class GenericCRUDView(generics.GenericAPIView):
    requireApiKey = True
    def get_queryset(self):
        queryset = super(GenericCRUDView, self).get_queryset()
        params = self.request.GET
        for key in params:
            # fully backward compatiable version on get_fields method can be found here:
            # https://docs.djangoproject.com/en/1.10/ref/models/meta/#migrating-from-the-old-api
            try:
                f = queryset.model._meta.get_field(key)
                value = params[key]
                filters = {key:value}
                try:
                    queryset = queryset.filter(**filters)
                except ValueError:
                    return []
            except models.FieldDoesNotExist:
                # do nothing, continue to check next key
                continue
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
        errorRes = []
        serializerList = []
        valid = True
        for entry in obj:
            serializer = serializer_class(entry, data=request.data)
            if not serializer.is_valid():
                valid = False
                errorRes.append(serializer.errors)
            else:
                serializerList.append(serializer)

        if not valid:
            return Response(errorRes, status=status.HTTP_400_BAD_REQUEST)

        successRes = []

        for serializer in serializerList:
            serializer.save()
            successRes.append(serializer.data)

        return Response(successRes)

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
