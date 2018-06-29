from flask import g,Flask,render_template, redirect, request, session, url_for, jsonify
import facebook
import tweepy
app = Flask(__name__)


#-----------Twitter-----------------------
CONSUMER_KEY = 'xrcjEJAAffVtZRzLyA8YWh2eh'
CONSUMER_SECRET = 'sYE5qFDtHHD8MLzCVzg8jXLkfDMBVuD1FQeIvL0QPDshGjwXaZ'
ACCESS_TOKEN = '1005106327180513280-0v99YasghntR4oEIAyjLSlbsTkgbIq'
ACCESS_TOKEN_SECRET = 'd0G4kRClwe6WYukBguQykvt7IadJK3eCFTiaBuVrFAQcS'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = None

@app.route('/twitter',methods=['POST','GET'])
def twitter():
	return render_template('twitter.html', name = None)

@app.route('/twitter_login',methods=['POST','GET'])
def twitter_login():
	#api.update_status(status = "Hey, I'm tweeting with Tweepy!") #Crear Tweet
	global api
	api = tweepy.API(auth)
	user = api.me()
	return render_template('twitter.html', name = user.name)

@app.route('/twitter_logOut',methods=['POST','GET'])
def twitter_logOut():
	global api
	api = None
	return render_template('twitter.html', name = None)

@app.route('/load_tweets',methods=['POST','GET'])
def load_tweets():
	if api is None:
		return render_template('twitter.html', name = None)
	else:
		public_tweets = api.home_timeline()
		return render_template('twitter.html', tweets= public_tweets, name = api.me().name)

@app.route('/created_tweets',methods=['POST','GET'])
def created_tweets():
	if api is None:
		return render_template('twitter.html', name = None)
	else:
		tweetText = request.form['texto']
		api.update_status(status = tweetText) #Crear Tweet
		return render_template('twitter.html', creado = 1, name = api.me().name)

###################Facebook
@app.route('/facebook',methods=['POST','GET'])
def facebook_index():
	return render_template('fb.html')


@app.route('/friends',methods=['POST'])
def friends():
	graph = facebook.GraphAPI(access_token=request.form["token"])
	friends = graph.get_connections(id=request.form["uid"], connection_name='friends')
	return jsonify(friends = friends)	


@app.route('/')
def index():
	return render_template('indexfbytw.html')

if __name__ == "__main__":
	app.run()
