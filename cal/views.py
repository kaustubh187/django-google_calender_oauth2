from django.shortcuts import redirect
from django.http import JsonResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import googleapiclient.discovery


#Prompts user for his/her credentials
def GoogleCalendarInitView(request):
    
    #Flow object will handle auth process
    flow = Flow.from_client_secrets_file(
        'config/abc.json',
        #Defining the scopes
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        #Redirect uri after permission granted
        redirect_uri='http://localhost:8000/rest/v1/calendar/redirect/'
    )
    #Storing refresh and access token
    authorization_url, state = flow.authorization_url(access_type='offline')

    #Storing the state value in sessions
    request.session['oauth_state'] = state

    #Finally redirected to auth url
    return redirect(authorization_url)

def GoogleCalendarRedirectView(request):
    state = request.session.pop('oauth_state', '')
    
    flow = Flow.from_client_secrets_file(
        'config/abc.json',
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        redirect_uri='http://localhost:8000/rest/v1/calendar/redirect/',
        state=state
    )

    # Get the authorization response URL
    authorization_response = request.build_absolute_uri()


    # Exchange authorization code for tokens
    flow.fetch_token(authorization_response=authorization_response)
    
    credentials = flow.credentials
    access_token = credentials.token
    ref_token = credentials.refresh_token
    client_id = credentials.client_id
    client_secret = credentials.client_secret

    
    credentials_info = {
        'refresh_token': ref_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'token': access_token,
        'token_uri': 'https://accounts.google.com/o/oauth2/token',
        'scopes': ['https://www.googleapis.com/auth/calendar.readonly'],
    }
    # Create credentials object using credentials_info
    credentials = Credentials.from_authorized_user_info(credentials_info)

    # Build the Google Calendar service
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    #Retrieve the list of events from the user's primary calendar
    events_result = service.events().list(calendarId='primary').execute()
    events = events_result.get('items', [])


    return JsonResponse(events, safe=False)

    
