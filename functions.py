"""
Functions for building recommender from #nowplaying database
===

"""

import random

def getUtilityMatrix(infile):
    """
    Builds utility matrix of user-artist interactions

    Takes mapreduced file of user,(artist,count)*n tuples
    and returns dictionary
    of user-artist interactions, indexed by user, with the
    last two keys holding the twitter user ids and artist
    strings, respectively.
    Took about 8 hours to process on personal computer
    for full database (mapreduced file ~400 MB, pickle
    outfile ~XX). Can also take in subset of data.
    This algorithm ignores the playcounts of each artist 
    per user and just captures whether a user listened
    to an artist at least once, but the count data could be
    used for a more sophisticated algorithm.
    
    If specified, writes data to file
    """
    artlen = 0
    data = {}
    data['users'] = []
    data['artists'] = []
    
    o = open(infile, 'r', encoding = 'utf-8')
    
    """separates list of strings into list of lists, where the structure 
    of each list is [userid,artist1,count1,artist2,count2,...,artistn,countn]
    """
    userstrs = [l for l in o]
    userlists = [s.split(',') for s in userstrs]
    
    o.close()
    
    """loops through each line, which represents one user and each artist 
    they tweeted with #nowplaying
    """
    for i in range(len(userlists)):
        data['users'].append(userlists[i][0])
        dataline = []
        
        """loops through each artist the user listened to"""
        for j in range(1,len(userlists[i]),2):
            
            """tries to find the user's listed artist in the list of artists.
            The artist search and the list of artists is created simultaneously
            """
            found = False
            for k in range(artlen):
                """if the artist is found in the list of artist, the index of that
                artist in the user list is stored in a list for that user,
                and the search ends with a 'break'
                """
                if userlists[i][j] == data['artists'][k]:
                    dataline.append(k)
                    found = True
                    break
            """after the artist list is checked and the user's artist isn't found
            that artist is added as a new artist to the artist list and it's index
            is stored in the user's list
            """
            if not found:
                data['artists'].append(userlists[i][j])
                dataline.append(artlen)
                artlen += 1
        """after creating the artist index list for each user, the list is stored 
        in a dictionary, with the user's index as the key
        """
        data[i] = sorted(dataline)
        """for benchmarking progress on large files"""
        if len(userlists) > 10000 and i % 1000 == 0:
            print("Completed %s / %s" % (i, len(userlists)))
     
    return(data)

def getRecommendationList(data, uid, k, artists, justids = False):
    """
    Returns a ranked list of new artists to try
    
    Takes in a utility matrix of user-artist interactions,
    a test user id, and k-nearest neighbors.
    Calculates Jaccard's coeffients to measure
    similarity between the test user and all other
    users
    Ranks artists based on the k closest users 
    who listened to each artist
    """
    
    """loop through each user who is not the test user
    and calculate a jaccard coefficient for that user"""
    jaccard = []
    for i in [i for i in range(0,len(data)) if i != uid]:
        intersection = len(set(data[uid]).intersection(data[i]))
        union = len(data[uid]) + len(data[i]) - intersection
        jaccard.append((i,intersection/union))
    sortscores = sorted(jaccard, key=lambda x: x[1], reverse=True)
    if k > len(sortscores):
        k = len(sortscores)
        print('k set to max: %s' % (k))
    
    """get the k nearest neighbors for the test user"""
    knn = sortscores[:k]
    newartindex = [i for i in range(len(artists)) if i not in data[uid]]
    
    """gets list of all artists not listened to by test user"""
    firstlist = []
    for i in range(k):
        firstlist.append([i for i in data[knn[i][0]] if i not in data[uid]])
    sums = []
    
    """both algorithms below sum up the jaccard scores
    of the knn who listened to each artist. The summed
    scores are sorted, and the highest scored artists
    are returned in a ranked list. One features just
    the artist index int, and the other lists the 
    string artist name and the summed jaccard scores"""
    if justids:
        for i in newartindex:
            nsum = 0
            for j in range(k):
                if i in firstlist[j]:
                    nsum += knn[j][1]
            sums.append((i, nsum))
        sortedsums = sorted(sums, key = lambda tup: tup[1], reverse=True)
        idlist = [x[0] for x in sortedsums]
        return(idlist)
    else:
        for i in newartindex:
            nsum = 0
            for j in range(k):
                if i in firstlist[j]:
                    nsum += knn[j][1]
            sums.append((artists[i], nsum))
        recom = sorted(sums, key = lambda tup: tup[1], reverse=True)
        return(recom)
    
def printresults(n, rclist):
    """
    prints n results from a list returned from getRecommendationList
    """
    if n > len(rclist):
        n = len(rclist)
    print("Top %s results:" % (n))
    for i in range(n):
        print("%s) %s" % (i+1,rclist[i][0]))
        
def userRecommendations(data, uid, k, artists, n):
    """
    puts getRecommendationList and printresults into one function
    """
    recom = getRecommendationList(data, uid, k, artists)
    printresults(n, recom)
    
def getYourRecommendations(data, k, artists, n):
    """
    UI for allowing user to enter in n musical artists and get
    n new recommendations back
    """
    print("Enter %s bands or musicians to get %s recommendations." % (n,n))
    inartists = []
    
    """checks if inputted artist is in the #nowplaying database"""
    for i in range(n):
        insystem = False
        while not insystem:
            inartists.append(input('Artist %s: ' % (i+1)))
            insystem = (inartists[i] in artists)
            if not insystem:
                inartists.remove(inartists[i])
                print('Artist not in the system. Try another.')
    
    """makes a new data list from indices of inputted artists"""
    newdata = [artists.index(a) for a in inartists]
    
    """adds the inputted user to the end of the utility matrix"""
    newindex = len(data)
    data[newindex] = newdata
    
    """gets recommendationlist and prints it"""
    userRecommendations(data, newindex, k, artists, n)
    
    """removes the new user"""
    del data[newindex]

def testSystem(data, k, artists, n):
    """
    Returns a precision score for the recommendation engine
    
    
    Designed to get the precision of this recommendation
    system, particularly getYourRecommendatrions UI, for a 
    given k-nearest neighbors and n input/output artists.
    Precision is defined as the number of recommended artists
    that interest the user.
    """

    """finds a random user and see if they have at least
    n*2 user-artist events. n*2 are needed to get recommendations
    on n artists and see if the rest match the recommendations
    """
    found = False
    userlen = len(data)
    while not found:
        testuid = random.randint(0,userlen - 1)
        if len(data[testuid]) >= 2*n:
            found = True
    originaldata = data[testuid]
    
    """samples n artists from whole dataline"""
    trainingset = random.sample(originaldata, n)
    
    """makes testset from artists not selected"""
    testset = [i for i in originaldata if i not in trainingset]
    
    """replaces artists in user's dict column with smaller,
    sampled list"""
    data[testuid] = trainingset
    
    """gets artists recommendations and returns original artist list"""
    fullrecomidlist = getRecommendationList(data, testuid, k, artists, justids = True)
    data[testuid] = originaldata
    
    """calculates and returns p based on how many recommended artists
    are found in the user's listening history but were sampled out for
    the test recommendation and divides it by the number of recommendations.
    Basically, percentage of recommendations that user had previously
    listened to."""
    nidlist = fullrecomidlist[0:n]
    p = sum([1 for i in nidlist if i in testset])/n
    return(p)