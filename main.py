import random
from flask import Flask, render_template, redirect,url_for
from google.cloud import datastore
import google.oauth2.id_token
from flask import Flask, render_template, request
from google.auth.transport import requests
import datetime
from multiprocessing.sharedctypes import Value

app = Flask(__name__)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

######################### Create and Retrieve UserInfo #########################

def retrieveUserInfo(claims):
   entity_key = datastore_client.key('UserInfo', claims['email'])
   entity = datastore_client.get(entity_key)
   return entity

def createUserInfo(claims,username):
 entity_key = datastore_client.key('UserInfo', claims['email'])
 entity = datastore.Entity(key = entity_key)
 if "name" in claims.keys():
    ssName = claims["name"]
 else: 
    ssName = claims["email"]
 entity.update({
 'email': claims['email'],
 'name': ssName,
 'bio': "",
 'username': username,
 'follower_list': [],
 'following_list': [],
 'tweet_list': []
 })
 datastore_client.put(entity)

####################### Create and Retrieve Tweet ###########################

def CreateTweet(claims, tweet, username):
    id = random.getrandbits(63)
    entity_key = datastore_client.key('Tweet', id)
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'tweet': tweet,
        'time': datetime.datetime.now(),
        'username': username,
        'file': ""
    })
    datastore_client.put(entity)
    return id

def retrieveTweets(user_info):
    #make key objects out of all the keys and retrieve them
    id = user_info['tweet_list']
    entity_keys = []
    for i in range(len(id)):
        entity_keys.append(datastore_client.key('Tweet', id[i]))
    tweet_list = datastore_client.get_multi(entity_keys)
    return tweet_list

def retrieveTweetlist(user_info):
    #make key objects out of all the keys and retrieve them
    entity_id = user_info['following_list']
    entity_keys = []
    for i in range(len(entity_id)):
        entity_keys.append(datastore_client.key('UserInfo', entity_id[i]))
    following_list = datastore_client.get_multi(entity_keys)
    Tweetlist = []
    for user in following_list:
        tweets = retrieveTweets(user)
        for tweet in tweets:
            Tweetlist.append(tweet)
    tweets = retrieveTweets(user_info)
    for tweet in tweets:
        Tweetlist.append(tweet)
    Tweetlist.sort(key=lambda x: x['time'], reverse=True)
    Tweetlist = Tweetlist[0:50]
    return Tweetlist

####################### Binding Tweet to User ###########################

def addTweetToUser(user_info, id):
    entity_keys = user_info['tweet_list']
    entity_keys.append(id)
    user_info.update({
        'tweet_list': entity_keys
    })
    datastore_client.put(user_info)

####################### delete tweet ###########################

def deleteTweet(entity_id, user_info):
    entity_key = datastore_client.key('Tweet', entity_id)
    datastore_client.delete(entity_key)
    
    tweet_list = user_info['tweet_list']
    tweet_list.remove(entity_id)
    user_info.update({
        'tweet_list' : tweet_list
    })
    datastore_client.put(user_info)

################################## App Routes ######################################################################################################


#########################  app route function inorder to delete tweet #########################

@app.route('/delete/<int:id>', methods=['GET','POST'])
def delete_tweet(id):
    id_token = request.cookies.get("token")
    error_message=None
    claims=None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            deleteTweet(id, user_info)
        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for("profile"))

#########################  app route function inorder to unfollow user #########################

@app.route('/unfollow/<email>', methods=['POST'])
def unfollow(email):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    current_user = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
                
            entity_key = datastore_client.key('UserInfo', email)
            current_user = datastore_client.get(entity_key)
                
            entity_keys = user_info['following_list']
            entity_keys.remove(current_user['email'])
            user_info.update({
                'following_list': entity_keys
            })
            datastore_client.put(user_info)
            
            entity_keyss = current_user['follower_list']
            entity_keyss.remove(user_info['email'])
            current_user.update({
                'follower_list': entity_keyss
            })
            datastore_client.put(current_user) 
        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for('user_information', email=email))

#########################  app route function inorder to edit tweet #########################

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit_tweet(id):
    id_token = request.cookies.get("token")
    error_message=None
    claims=None
    tweet = None
    if request.method == 'GET':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                user_info = retrieveUserInfo(claims)
                entity_key = datastore_client.key("Tweet", id)
                tweet = datastore_client.get(entity_key)
            except ValueError as exc:
                error_message = str(exc)
        return render_template('edittweet.html', user_data=claims, error_message=error_message, user_info=user_info, tweet=tweet)
    else:
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                entity_key = datastore_client.key('Tweet', id)
                entity = datastore_client.get(entity_key)
                entity.update({
                    'tweet': request.form['tweet'],
                    'time': datetime.datetime.now(),
                    'file': ""
                })
                datastore_client.put(entity)
            except ValueError as exc:
                error_message = str(exc)
        return redirect(url_for("profile"))

#########################  app route function inorder to add tweet #########################

@app.route('/addtweet', methods=["GET","POST"])    
def Tweet():
   id_token = request.cookies.get("token")
   user_data=None
   error_message = None
   user_info = None
   tweets = None
   if request.method == "POST":
      if id_token:
         try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            id = CreateTweet(claims, request.form['tweet'], user_info['username'])
            if id != False:
              addTweetToUser(user_info, id)
         except ValueError as exc:
            error_message = str(exc)
      return redirect(url_for("profile"))
   else:
      if id_token:
         try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            tweets=retrieveTweets(user_info)
         except ValueError as exc:
            error_message = str(exc)
      return render_template('addtweet.html', user_data=claims, error_message=error_message,user_info=user_info,tweets=tweets)

#########################  app route function inorder to follow user #########################

@app.route('/follow/<email>', methods=['POST'])
def follow(email):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    current_user = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
                
            entity_key = datastore_client.key('UserInfo', email)
            current_user = datastore_client.get(entity_key)
                
            entity_keys = user_info['following_list']
            entity_keys.append(current_user['email'])
            user_info.update({
                'following_list': entity_keys
            })
            datastore_client.put(user_info)
            
            entity_keyss = current_user['follower_list']
            entity_keyss.append(user_info['email'])
            current_user.update({
                'follower_list': entity_keyss
            })
            datastore_client.put(current_user)            
        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for('user_information', email=email))





#########################  app route function inorder to display user info #########################


@app.route('/user/<email>', methods=['GET','POST'])
def user_information(email):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    current_user = None
    tweets = None
    if request.method == 'GET':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                user_info = retrieveUserInfo(claims)
            
                entity_key = datastore_client.key('UserInfo', email)
                current_user = datastore_client.get(entity_key)
            
                tweets = retrieveTweets(retrieveUserInfo(current_user))
                tweets.sort(key=lambda x: x['time'], reverse=True)
                tweets = tweets[0:50]
            except ValueError as exc:
                error_message = str(exc)
        return render_template('usertweetfollower.html', user_data=claims, error_message=error_message, user_info=user_info,current_user=current_user, tweets=tweets)




#########################  app route function inorder tosearch tweet and user #########################


@app.route('/search', methods=['GET','POST'])
def search():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    users = []
    tweets = []
    
    if request.method == 'GET':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                user_info = retrieveUserInfo(claims)
                tweets = retrieveTweets(user_info)
                
            except ValueError as exc:
                error_message = str(exc)
        return render_template('search.html', user_data=claims, error_message=error_message, user_info=user_info, tweets=tweets)
    else :
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                user_info = retrieveUserInfo(claims)
                
                search=request.form['search']
                query = datastore_client.query(kind= "UserInfo")
                results = list(query.fetch())

                for user in results:
                    if request.form['search'].lower() in user['username'].lower():
                        users.append(user)
                users = list(users)
                
                query = datastore_client.query(kind= "Tweet")
                results = list(query.fetch())
            
                for tweet in results:
                    if request.form['search'].lower() in tweet['tweet'].lower():
                        tweets.append(tweet)
                tweets = list(tweets)
                
            except ValueError as exc:
                error_message = str(exc)
        return render_template('searchresult.html', user_data=claims, error_message=error_message, user_info=user_info, users=users, tweets=tweets,search=search)



#########################  app route function inorder to edit profile #########################


@app.route('/editprofile', methods=['GET','POST'])
def editprofile():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    tweets = None
    if request.method == 'GET':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                user_info = retrieveUserInfo(claims)
                tweets = retrieveTweets(user_info)
                
            except ValueError as exc:
                error_message = str(exc)
        return render_template('editprofile.html', user_data=claims, error_message=error_message, user_info=user_info, tweets=tweets)
    else:
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                entity_key = datastore_client.key('UserInfo', claims['email'])
                entity = datastore_client.get(entity_key)
                entity.update({
                    'name': request.form['name'],
                    'bio': request.form['bio']
                })
                datastore_client.put(entity) 
                user_info = retrieveUserInfo(claims)
                tweets = retrieveTweets(user_info)
            except ValueError as exc:
                error_message = str(exc)
        return render_template('profile.html', user_data=claims, error_message=error_message, user_info=user_info, tweets=tweets)



#########################  app route function inorder to add username #########################


@app.route('/username', methods=['GET','POST'])
def username():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    if request.method == 'GET':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            except ValueError as exc:
                error_message = str(exc)
        return render_template('username.html')
    else: 
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                createUserInfo(claims, request.form['username'])
                user_info = retrieveUserInfo(claims)
            except ValueError as exc:
                error_message = str(exc)
        return redirect(url_for('profile'))

#########################  app route function inorder to display profile with tweets #########################


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    tweets = None
    if request.method == 'GET':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                user_info = retrieveUserInfo(claims)
                tweets = retrieveTweetlist(user_info)
            except ValueError as exc:
                error_message = str(exc)
        return render_template('profile.html', user_data=claims, error_message=error_message, user_info=user_info, tweets=tweets)


#########################  app route function inorder to root to index #########################

@app.route('/')
def root():
   id_token = request.cookies.get("token")
   error_message = None
   claims = None
   user_info = None
   Tweet = None
   Tweetlist = None
   if id_token:
    try:
     claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
     user_info = retrieveUserInfo(claims)
     if user_info == None:
                  return redirect(url_for("username"))
     Tweet=retrieveTweets(user_info)
     Tweetlist = retrieveTweetlist(user_info)
    except ValueError as exc:
            error_message = str(exc)
   return render_template('index.html', user_data=claims, error_message=error_message, user_info=user_info,Tweet=Tweet,Tweetlist=Tweetlist)  

if __name__ == '__main__':
   app.run(host='127.0.0.1', port=8080, debug=True)