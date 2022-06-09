#################
### LIBRARIES ###
#################
# For sending GET requests from the API
import requests
# For saving access tokens and for file management when creating and adding to the dataset
import os
# For dealing with json responses we receive from the API
import json
# For displaying the data after
import pandas as pd
# For saving the response data in CSV format
import csv
# For parsing the dates received from twitter in readable formats
import datetime
import dateutil.parser
import unicodedata
#To add wait time between requests
import time
import ast


#################
### CONSTANTS ###
#################

DATA_DIRECTORY = "data/"
BEARER_TOKEN_PATH = "bearer_token.txt"


#################
### FUNCTIONS ###
#################

def auth():
    return os.getenv('TOKEN')

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def create_url(keyword, start_date, end_date, max_results = 10):
    
    search_url = "https://api.twitter.com/2/tweets/search/all" 

    
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,referenced_tweets.id,referenced_tweets.id.author_id,entities.mentions.username,attachments.poll_ids,attachments.media_keys,in_reply_to_user_id,geo.place_id',
                    
                    'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text',
                    'media.fields': 'duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width,alt_text',
                    'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    return (search_url, query_params)  

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def append_csv_url(json_response, fileName, username):
    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    user_username=[]
    erors=[]

    resp =json_response['includes']

    for i in resp['users']:
        usernames= i.get('username',"None")
        user_username.append(usernames)

    cc=0
    for tweet in json_response['data']:
        


        if('conversation_id' in tweet):
            conversation_id = tweet['conversation_id']
        else:
            conversation_id= ''
        
        
        conversation_url1 = f"https://twitter.com/{user_username[min(cc, len(user_username)-1)]}/status/{conversation_id}"
                # 9. attachments

        # Assemble all data in a list
        appli= [username, conversation_url1]#, erors[cc]]
        # Append the result to the CSV file
        csvWriter.writerow(appli)
        cc +=1

    # When done, close the CSV file
    csvFile.close()


def append_csv_app(json_response, fileName, username):
    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    media_url=[]
    count_media=0
    user_username=[]

    resp =json_response['includes']
    
    if 'media' in resp:
        for i in resp['media']:       
            mur= i.get('url', "None")
            print(mur)
            media_url.append(mur) 
    for i in resp['users']:
        usernames= i.get('username',"None")
        user_username.append(usernames)

    #Loop through each tweet
    cc=0

    for tweet in json_response['data']:
        
        # We will create a variable for each since some of the keys might not exist for some tweets
        # So we will account for that

        # 6. Tweet metrics
        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']

        # 8. Tweet text
        text = tweet['text']

        if('conversation_id' in tweet):
            conversation_id = tweet['conversation_id']
        else:
            conversation_id= ''

        conversation_url = f"https://twitter.com/{username}/status/{conversation_id}"
        # Catch this error, which actually shouldn't matter since the status is always the same
        conversation_url1 = f"https://twitter.com/{user_username[min(cc, len(user_username)-1)]}/status/{conversation_id}"

                # 9. attachments
        if ('attachments' in tweet): 
            attachments =tweet['attachments']
            m_url=media_url[count_media]
            count_media +=1
            print(count_media)
        else:
            attachments = " "
            m_url= " "
        ################Agregando Users information
         
        # Assemble all data in a list
        appli= [username, like_count, quote_count, reply_count, retweet_count, text,  conversation_url1, m_url]
        # Append the result to the CSV file
        csvWriter.writerow(appli)
        cc +=1

    # When done, close the CSV file
    csvFile.close()

######################################


def append_to_csv(json_response, fileName, username):

    #A counter variable
    counter = 0
    cc=0
    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    media_url=[]
    res_app=[]
    count_media=0
    user_username=[]

    resp =json_response['includes']

    if 'media' in resp:
        for i in resp['media']:        
            mur= i.get('url', "None")
            print(mur)
            media_url.append(mur) 
    
    for i in resp['users']:
        usernames= i.get('username',"None")
        user_username.append(usernames)

    #Loop through each tweet
    for tweet in json_response['data']:

        # 1. Author ID
        author_id = tweet['author_id']
       
        # 2. Time created
        created_at = dateutil.parser.parse(tweet['created_at'])

        # 3. Geolocation
        if ('geo' in tweet):   
            geo = tweet['geo']['place_id']
        else:
            geo = " "

        # 4. Tweet ID
        tweet_id = tweet['id']

        # 5. Language
        lang = tweet['lang']

        # 6. Tweet metrics
        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']

        # 7. source
        source = tweet['source']

        # 8. Tweet text
        text = tweet['text']

        # 9. attachments
        if ('attachments' in tweet): 
            attachments =tweet['attachments']#
            m_url=media_url[count_media]
            count_media +=1
            print(count_media)
        else:
            attachments = " "
            m_url= " "

        #10 possibly_sensitive
        if ('possibly_sensitive' in tweet): 
            possibly_sensitive= tweet['possibly_sensitive']
        else:
            possibly_sensitive = 'False'

        if('context_annotations' in tweet):
            context_annotations= tweet['context_annotations']
        else:
            context_annotations= ''

        if('conversation_id' in tweet):
            conversation_id = tweet['conversation_id']
        else:
            conversation_id= ''


        if('entities' in tweet):
            entities = tweet['entities']
        else:
            entities= ''


        if('in_reply_to_user_id' in tweet):
            in_reply_to_user_id= tweet['in_reply_to_user_id']
        else:
            in_reply_to_user_id= ''     


        if('referenced_tweets' in tweet):
            referenced_tweets= tweet['referenced_tweets']
        else:
            referenced_tweets= ''  


        if('reply_settings' in tweet):
            reply_settings= tweet['reply_settings']
        else:
            reply_settings= ''     

        
        conversation_url= f"https://twitter.com/{user_username[min(cc, len(user_username)-1)]}/status/{conversation_id}"
        ################Agregando Users information
   
        
        # Assemble all data in a list

        res = [attachments, author_id, context_annotations, conversation_id, created_at, entities, geo, tweet_id, in_reply_to_user_id, lang, possibly_sensitive,referenced_tweets, reply_settings, source, like_count, quote_count, reply_count, retweet_count, text, conversation_url,  username, m_url]#,, profile_image] #, profile_image_url]#, user_id,user_name,user_username,user_description, user_retweet_count, user_reply_count,user_like_count, user_quote_count]
        appli= [username, like_count, quote_count, reply_count, retweet_count, text, conversation_url, m_url]
        # Append the result to the CSV file
        csvWriter.writerow(res)
        counter += 1
        
    # When done, close the CSV file
    csvFile.close()
    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", counter) 

def main():
    #Inputs for tweets

    os.environ['TOKEN'] = open(BEARER_TOKEN_PATH, "r").readline()
    
    ##############
    ##############
    ############## Variable for candidates' accounts

    username_list = []
    with open('initial_counts.csv', newline='') as handlesCSV:
        reader = csv.DictReader(handlesCSV)
        for row in reader:
            username_list.append(row)


    # username = ['JoshHarder','realannapaulina']#, 'hiral4congress','ThomTillis','RepJahanaHayes', 'Meg4Congress','PauletteEJordan']
    
    fileURL= DATA_DIRECTORY + 'Mentions_URL.csv'
    # If the CSV is empty or doesn't exist, create one
    if (os.path.exists(fileURL) == False) or (os.stat(fileURL).st_size == 0):
        # Read in the headers from the template
        csvTemplate=open(DATA_DIRECTORY + "template/Mentions_Template.csv", "r").readline()
        csvF_URL=open(fileURL,"a+", newline="", encoding='utf-8')
        urlWriter = csv.writer(csvF_URL)
        urlWriter.writerow(['Candidate', 'Conversation_URL'])
        csvF_URL.close()

    for row in username_list:
        name = row['candidate']
        tweet_count = int(row['tweet count'])

        ######################
        ######################
        ######################Variable for the filter
        keyword = '(from:'+name+' OR @'+name+') -is:retweet' ############This line is the filter
        file_name= DATA_DIRECTORY + name +'_1profileNRT.csv'
        file_json= DATA_DIRECTORY + name +'_1profileNRT.json'
        file2_json= DATA_DIRECTORY + name +'_4app.csv'
       
        bearer_token = auth()
        headers = create_headers(bearer_token)

#####################
#####################
#####################Variable for time-windows. start_list and end_list must have the same number of elements
        start_time_date=[datetime.datetime(2020, 10, 4, 15, 21, 0, 0, datetime.timezone.utc),
            datetime.datetime(2020, 10, 11, 22, 50, 0, 0, datetime.timezone.utc),
            datetime.datetime(2020, 10, 15, 14, 30, 0, 0, datetime.timezone.utc),
            datetime.datetime(2020, 10, 16, 13, 8, 0, 0, datetime.timezone.utc),
            datetime.datetime(2020, 10, 18, 22, 11, 0, 0, datetime.timezone.utc),
            datetime.datetime(2020, 11, 1, 14, 35, 0, 0, datetime.timezone.utc),
            datetime.datetime(2020, 11, 5, 19, 41, 0, 0, datetime.timezone.utc),
            datetime.datetime(2020, 11, 8, 11, 32, 0, 0, datetime.timezone.utc),
            datetime.datetime(2020, 11, 9, 23, 12, 0, 0, datetime.timezone.utc),
            datetime.datetime(2020, 11, 20, 21, 44, 0, 0, datetime.timezone.utc)]
        
        hour_count = 0
        if tweet_count >= 1000:
            hour_count = 1
        elif tweet_count >= 100:
            hour_count = 4
        elif tweet_count >= 10:
            hour_count = 48
        else:
            hour_count = 168

        hour_count= 16
        end_time_date = [timestamp + datetime.timedelta(hours = hour_count) for timestamp in start_time_date] 

        start_list = [t.strftime('%Y-%m-%dT%H:%M:%S.000Z') for t in start_time_date]
        end_list = [t.strftime('%Y-%m-%dT%H:%M:%S.000Z') for t in end_time_date]
        
        
        max_results = 99
        
        #Total number of tweets we collected from the loop
        total_tweets = 0

        # Create file
        
        csvFile = open(file_name, "a", newline="", encoding='utf-8')
        csvWriter = csv.writer(csvFile)
        #Create headers for the data you want to save, in this example, we only want save these columns in our dataset
                            
        csvWriter.writerow(['attachments','author id', 'context_annotations', 'conversation_id','created_at', 'entities','geo', 'tweet_id','in_reply_to_user_id','lang','possibly_sensitive', 'referenced_tweets', 'reply_settings','source', 'like_count', 'quote_count', 'reply_count','retweet_count', 'tweet', 'conversation_url ', 'name','media_url'])
        csvFile.close()

        csvFile = open(file2_json, "a", newline="", encoding='utf-8')
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(['username', 'like_count', 'quote_count', 'reply_count', 'retweet_count', 'text', 'conversation_url', 'm_url'])
        csvFile.close()



        for i in range(0,len(start_list)):

            # Inputs
            count = 0 # Counting tweets per time period
            
            flag = True
            next_token = None
            tweets_list=pd.DataFrame()
    
            # Check if flag is true
            while flag:
                startRequest = time.time()
            
                print("-------------------")
                print("Token: ", next_token)
                print(name)
                url = create_url(keyword, start_list[i],end_list[i], max_results)
                json_response = connect_to_endpoint(url[0], headers, url[1], next_token)
                
                result_count = json_response['meta']['result_count']

                if 'next_token' in json_response['meta']:
                # Save the token to use for next call
                    next_token = json_response['meta']['next_token']
                    print("Next Token: ", next_token)
                    if result_count is not None and result_count > 0 and next_token is not None:
                        print("Start Date: ", start_list[i])
                   
                        append_to_csv(json_response, file_name, name)
                        append_csv_app(json_response, file2_json, name)
                        append_csv_url(json_response, fileURL, name)
                        
                        s=json.dumps(json_response, indent=4)
                        f=open(file_json,"w")
                        f.write(s)
                        count += result_count
                        total_tweets += result_count
                        print("Total # of Tweets added: ", total_tweets)
                        print("-------------------")

                                    
                # If no next token exists
                else:
                    if result_count is not None and result_count > 0:
                        print("-------------------")
                        print("Start Date: ", start_list[i])
                        
                        append_to_csv(json_response, file_name, name)
                        append_csv_app(json_response, file2_json, name)
                        append_csv_url(json_response, fileURL, name)
                        s=json.dumps(json_response, indent=4)
                        f=open(file_json,"w")
                        f.write(s)
                        count += result_count
                        total_tweets += result_count
                        print("Total # of Tweets added: ", total_tweets)
                        print("-------------------")
                    
                    flag = False
                    next_token = None
                endRequest = time.time()
                print(endRequest - startRequest)
                if (endRequest - startRequest < 3):
                    time.sleep(3.2 - (endRequest - startRequest))
                    
        print("Total number of results: ", total_tweets)


if __name__ == "__main__":
    main()