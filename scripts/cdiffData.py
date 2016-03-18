CDIFF = {
    'Partner':{
        'partnerId':'cdiff',
        'name':'CDIFF',
        'logoUri':'https://s3-us-west-2.amazonaws.com/pw2-logo/BioCyc.gif',
        'termOfServiceUri':'https://www.google.com/intl/en/policies/terms/?fg=1',
        'description':'cdiff partner description',
    },
    'PartnerPattern':[
        {'sourceUri':'stevecdiff.steveatgetexp.com', 'targetUri':'http://cdifficile.biocyc.org'},
    ],
    'SubscriptionTerm':[
        {'description':'Two Month', 'period':60, 'price':100, 'groupDiscountPercentage':0},
        {'description':'Eight Months', 'period':240, 'price':400, 'groupDiscountPercentage':10},
        {'description':'Three Year', 'period':1095, 'price':1800, 'groupDiscountPercentage':20},
    ],
    'SubscriptionDescription':[
        {'header':'Default for CDIFF','descriptionType':'def'},
        {'header':'CDIFF Individual Subscription', 'descriptionType':'individual'},
        {'header':'CDIFF Institution Subscription', 'descriptionType':'institution'},
        {'header':'CDIFF Commercial Subscription', 'descriptionType':'commercial'},
    ],
    'def':[
        'This is default benefit #1',
        'You will be awesome',
        'This is default benefit #2',
    ],
    'individual':[
        'All your base are belong to us',
        'For great justice',
        'CDIFF individual benefit #3',
    ],
    'institution':[
        'This is institution benefit #1',
        'Test',
    ],
    'commercial':[
        'This is test commercial benefit',
        'You get 50% discount',
        'Cats are awesome!',
    ],
    'PaidPattern':[
        '/comp-genomics',
    ],
    'LimitValue':[
        5,
        10,
        15,
    ],
    'TestUser':[
        {'username':'stevetest', 'password':'stevepass', 'email':'steve@getexp.com', 'institution':'getexp', 'userIdentifier':'steve'},
        {'username':'azeemtest', 'password':'azeempass', 'email':'azeem@getexp.com', 'institution':'getexp', 'userIdentifier':'azeem'},
    ],
}
