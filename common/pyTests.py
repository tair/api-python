import requests
import json
import sys, getopt

class GenericCRUDTest(object):
    def setUp(self):
        # TODO: insert ApiKey model creation here
        pass

    def test_for_create(self):
        sample = self.sample
        req = requests.post(sample.url, data=sample.data)
        self.assertEqual(req.status_code, 201)
        self.assertIsNotNone(PyTestGenerics.forceGet(sample.model,sample.pkName,req.json()[sample.pkName]))
        PyTestGenerics.forceDelete(sample.model,sample.pkName,req.json()[sample.pkName])

    def test_for_get_all(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url
        if hasattr(sample,'partnerId'):
            url += '?partnerId=%s' % sample.partnerId
        req = requests.get(url)
        self.assertEqual(req.status_code, 200)
        PyTestGenerics.forceDelete(sample.model,sample.pkName,pk)

    def test_for_update(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + '?%s=%s' % (sample.pkName, str(pk))
        if hasattr(sample, 'partnerId'):
            url += '&partnerId=%s' % sample.partnerId
        req = requests.put(url, data=sample.updateData)
        if sample.pkName in sample.updateData:
            pk = sample.updateData[sample.pkName]
        self.assertEqual(req.status_code, 200)
        PyTestGenerics.forceDelete(sample.model,sample.pkName,pk)

    def test_for_delete(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + '?%s=%s' % (sample.pkName, str(pk))
        if hasattr(sample, 'partnerId'):
            url += '&partnerId=%s' % sample.partnerId
        req = requests.delete(url)
        self.assertIsNone(PyTestGenerics.forceGet(sample.model,sample.pkName,pk))

    def test_for_get(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + '?%s=%s' % (sample.pkName, str(pk))
        if hasattr(sample, 'partnerId'):
            url += '&partnerId=%s' % sample.partnerId
        req = requests.get(url)
        self.assertEqual(req.status_code, 200)
        PyTestGenerics.forceDelete(sample.model,sample.pkName,pk)

    def tearDown(self):
        # TODO: insert ApiKey model deletion here
        pass

class GenericTest(object):
    def setUp(self):
        # TODO: insert ApiKey model creation here
        pass

    def tearDown(self):
        # TODO: insert ApiKey model deletion here
        pass

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
