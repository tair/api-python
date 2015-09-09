TAIR = {
    'Partner':{
        'partnerId':'tair',
        'name':'TAIR',
        'logoUri':'https://s3-us-west-2.amazonaws.com/pw2-logo/logo2.gif',
        'termOfServiceUri':'https://www.arabidopsis.org/doc/about/tair_terms_of_use/417',
    },
    'PartnerPattern':[
        {'sourceUri':'demotair.steveatgetexp.com', 'targetUri':'http://back-prod.arabidopsis.org'},
        {'sourceUri':'gbrowseaws.arabidopsis.org', 'targetUri':'http://back-gbrowse-prod.arabidopsis.org'},
        {'sourceUri':'seqvieweraws.arabidopsis.org', 'targetUri':'http://back-seqviewer-prod.arabidopsis.org'},
    ],
    'SubscriptionTerm':[
        {'description':'1 month', 'period':30, 'price':9.80, 'groupDiscountPercentage':10},
        {'description':'1 year', 'period':365, 'price':98, 'groupDiscountPercentage':10},
        {'description':'2 years', 'period':730, 'price':196, 'groupDiscountPercentage':10},
    ],
    'SubscriptionDescription':[
        {'header':'Subscription Benefit','descriptionType':'def'},
        {'header':'Individual Subscription Benefit', 'descriptionType':'individual'},
        {'header':'Institution Subscription Benefit', 'descriptionType':'institution'},
        {'header':'Commercial Subscription Benefit', 'descriptionType':'commercial'},
    ],
    'def':[
        'Unlimited access to the TAIR pages',
        'Up-to-date, manually curated data from the literature',
        'Custom datasets on request',
        'Downloadable, current genome-wide datasets',
    ],
    'individual':[
        'Access for a single research',
        'Each lab member requires their own individual subscription',
        'Discounts available when two or more individuals subscribe together',
    ],
    'institution':[
        'Unlimited access for all researchers, students and staff at your institution',
        'Cost is typically covered by your library',
        'Access is granted automatically by IP address',
    ],
    'commercial':[
        'Used by most top agroscience companies',
        'Subscription options for entire companies or individual commercial uses',
        'License terms appropriate for commercial uses',
    ],
    'PaidPattern':[
        '/servlets/TairObject\?((id=\d+\&type=assignment)|(type=assignment\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=gene)|(type=gene\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=assemblyunit)|(type=assemblyunit\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=marker)|(type=marker\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=locus)|(type=locus\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=contig)|(type=contig\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=cloneend)|(type=cloneend\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=polyallele)|(type=polyallele\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=restrictionenzyme)|(type=restrictionenzyme\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=sequence)|(type=sequence\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=species_variant)|(type=species_variant\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=host_strain)|(type=host_strain\&id=\d+))',
        '/servlets/TairObject\?((id=\d+\&type=keyword)|(type=keyword\&id=\d+))',
        '/servlets/Search.*type=annotation',
        '/servlets/tools/',
        '/servlets/mapper',
        '/biocyc/index.jsp',
        '/tools/nbrowse.jsp',
        '/tools/igb/91',
        '/Blast/',
        '/wublast/',
        '/fasta/',
        '/ChromosomeMap/',
        '/portals/masc/',
        '/portals/mutants/',
        '/portals/proteome/',
        '/portals/metabolome/',
        '/download/index-auto.jsp/?(!?dir=/download_files/Protocols)',
        '/submit/ExternalLinkSubmission.jsp',
        '/submit/genefamily_submission.jsp',
        '/submit/gene_annotation.submission.jsp',
        '/submit/marker_submission.jsp',
        '/submit/pathway_submission.jsp',
        '/submit/phenotype_submission.jsp',
        '/submit/protocol_submission.jsp',
        '/submit/submit_2010.jsp',
        '/news/newsgroup.jsp',
        '/news/newsletter_archive.jsp',
        '/news/events.jsp',
        '/news/jobs.jsp',
    ],
    'LimitValue':[
        3,
        5,
    ],
    'TestUser':[
    ],
}
