YFD = {
    'Partner':{
        'partnerId':'yfd',
        'name':'YFD',
        'logoUri':'https://s3-us-west-2.amazonaws.com/pw2-logo/yfd.png',
        'termOfServiceUri':'https://www.google.com/intl/en/policies/terms/?fg=1',
        'description':'yfd partner description',
    },
    'PartnerPattern':[
        {'sourceUri':'testyfd.com', 'targetUri':'http://back-prod.testyfd.com'},
        {'sourceUri':'demoyfd.steveatgetexp.com', 'targetUri':'http://back-demoyfd.steveatgetexp.com'},
    ],
    'SubscriptionTerm':[
        {'description':'Two Month', 'period':60, 'price':100, 'groupDiscountPercentage':0},
        {'description':'Eight Months', 'period':240, 'price':400, 'groupDiscountPercentage':10},
        {'description':'Three Year', 'period':1095, 'price':1800, 'groupDiscountPercentage':20},
    ],
    'SubscriptionDescription':[
        {'header':'Default for Test Partner','descriptionType':'def'},
        {'header':'Test Individual Subscription', 'descriptionType':'individual'},
        {'header':'Test Institution Subscription', 'descriptionType':'institution'},
        {'header':'Test Commercial Subscription', 'descriptionType':'commercial'},
    ],
    'def':[
        'This is default benefit #1',
        'You will be awesome',
        'You will get a million dollars',
    ],
    'individual':[
        'All your base are belong to us',
        'For great justice',
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
        '/paid/',
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
