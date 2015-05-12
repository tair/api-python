import requests
import json
import sys, getopt

class PyTestGenerics:
    @staticmethod
    def initPyTest():
        try:
            opts, args = getopt.getopt(sys.argv[1:], "h:" , ["host="])
        except getopt.GetoptError:
            print "Usage: python -m metering.pyTests --host <hostname>\n\rExample hostname: 'http://pb.steveatgetexp.com:8080/'"
            sys.exit(1)
        serverUrl = ""
        for opt, arg in opts:
            if opt=='--host' or opt=='-h':
                serverUrl = arg
        if serverUrl=="":
            print "hostname is required"
            sys.exit(1)
        return serverUrl


    @staticmethod
    def forceGet(model, pkName, pk):
        try:
            filters = {pkName:pk}
            return model.objects.get(**filters)
        except:
            return None

    @staticmethod
    def forceDelete(model, pkName,pk):
        try:
            filters = {pkName:pk}
            model.objects.get(**filters).delete()
        except:
            pass

    @staticmethod
    def forcePost(model, pkName, data):
        u = model(**data)
        u.save()
        return u.__dict__[pkName]

    @staticmethod
    def genericTestCreate(test):
        sample = test.sample
        req = requests.post(sample.url, data=sample.data)
        test.assertEqual(req.status_code, 201)
        test.assertIsNotNone(PyTestGenerics.forceGet(sample.model,sample.pkName,req.json()[sample.pkName]))
        PyTestGenerics.forceDelete(sample.model,sample.pkName,req.json()[sample.pkName])

    @staticmethod
    def genericTestGetAll(test):
        sample = test.sample
        pk = sample.forcePost(sample.data)
        url = sample.url
        if hasattr(sample,'partnerId'):
            url += '?partnerId=%s' % sample.partnerId
        req = requests.get(url)
        test.assertEqual(req.status_code, 200)
        PyTestGenerics.forceDelete(sample.model,sample.pkName,pk)

    @staticmethod
    def genericTestUpdate(test):
        sample = test.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + str(pk) + '/'
        if hasattr(sample, 'partnerId'):
            url += '?partnerId=%s' % sample.partnerId
        req = requests.put(url, data=sample.updateData)
        if sample.pkName in sample.updateData:
            pk = sample.updateData[sample.pkName]
        test.assertEqual(req.status_code, 200)
        PyTestGenerics.forceDelete(sample.model,sample.pkName,pk)

    @staticmethod
    def genericTestDelete(test):
        sample = test.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + str(pk) + '/'
        if hasattr(sample, 'partnerId'):
            url += '?partnerId=%s' % sample.partnerId
        req = requests.delete(url)
        test.assertIsNone(PyTestGenerics.forceGet(sample.model,sample.pkName,pk))

    @staticmethod
    def genericTestGet(test):
        sample = test.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + str(pk) + '/'
        if hasattr(sample, 'partnerId'):
            url += '?partnerId=%s' % sample.partnerId
        req = requests.get(url)
        test.assertEqual(req.status_code, 200)
        PyTestGenerics.forceDelete(sample.model,sample.pkName,pk)
