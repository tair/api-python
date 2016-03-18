update PartnerPattern
set sourceUri = 'demotair.arabidopsis.org', targetUri = 'http://back-test.arabidopsis.org'
where partnerPatternId = 1;

update PartnerPattern
set sourceUri = 'testgb.arabidopsis.org', targetUri = 'http://back-gbrowse-test.arabidopsis.org'
where partnerPatternId = 2;

update PartnerPattern
set sourceUri = 'testsv.arabidopsis.org', targetUri = 'http://back-seqviewer-test.arabidopsis.org'
where partnerPatternId = 3;

delete from PartnerPattern where partnerPatternId = 4;

update UriPattern
   set pattern = 'testgb\.arabidopsis\.org/cgi-bin/(?!gb2/gbrowse_img)'
where patternId = 104;

update UriPattern
   set pattern = 'testsv\.arabidopsis\.org'
where patternId = 105;

update Partner 
set homeUri = 'https://demotair.arabidopsis.org' 
where partnerId = 'tair';

update Partner 
set termOfServiceUri = 'https://demotair.arabidopsis.org/doc/about/tair_terms_of_use/417' 
where partnerId = 'tair';

update Partner 
set description = 'Genome database for the reference plant Arabidopsis thaliana' 
where partnerId = 'tair';

update Partner 
set homeUri = 'https://demotair.arabidopsis.org' 
where partnerId = 'phoenix';

update Partner 
set termOfServiceUri = 'https://demotair.arabidopsis.org/doc/about/tair_terms_of_use/417' 
where partnerId = 'phoenix';

update Partner 
set description = 'phoenix partner description' 
where partnerId = 'phoenix'

INSERT INTO phoenix_api.Partner (partnerId, name, logoUri, termOfServiceUri, homeUri) 
VALUES ('biocyc', 'BioCyc', 'https://s3-us-west-2.amazonaws.com/pw2-logo/BioCyc.gif', 'http://biocyc.org/disclaimer.shtml', 'http://www.biocyc.org/');

INSERT INTO phoenix_api.PartnerPattern (sourceUri, targetUri, partnerId) 
VALUES ('stevecdiff.steveatgetexp.com', 'http://www.biocyc.org/', 'biocyc');

