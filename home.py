from cloudant import Cloudant

from flask import Flask, render_template, request,redirect,flash,url_for
from flask_compress import Compress
import atexit
import cf_deployment_tracker
import os
import json
import requests

cf_deployment_tracker.track()

app=Flask(__name__)
Compress(app)
db_name = 'mydb'
client = None
db = None
if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

port = int(os.getenv('PORT', 8000))

def get_problems_solved(user):
	ans=set()
	url="http://codeforces.com/api/user.status?handle="+user
	req=requests.get(url)
	if req.status_code!=200:
		return None
	data=json.loads(req.text)
	if data['status'] == 'FAILED':
		return None
	for i in data['result']:
		if i['verdict']=='OK' and 'contestId' in i['problem']:
			ans.add(tuple([i['problem']['contestId'],i['problem']['index'],tuple(i['problem']['tags'])]))
	return ans

def validate(user):
	url="http://www.codeforces.com/api/user.info?handles="+user
	req=requests.get(url)
	if req.status_code!=200 and req.status_code!=400:
		return None
	data=json.loads(req.text)
	return data['status']=='OK'


@app.route('/')
def face():
	return render_template('index.htm')
@app.route('/compare',methods=['POST'])
def compare_results():
	user_1=request.form['user1']
	user_2=request.form['user2']
	user_1_good=True
	user_2_good=True
	while True:
		user_1_good=validate(user_1)
		if user_1_good!=None:
			break
	while True:
		user_2_good=validate(user_2)
		if user_2_good!=None:
			break
	if user_1_good and user_2_good:
		while True:
			probs_1=get_problems_solved(user_1)
			if probs_1 is not None:
				break
		while True:
			probs_2=get_problems_solved(user_2)
			if probs_2 is not None:
				break
		probs_both=sorted(i for i in probs_1&probs_2 if int(i[0])<100000)
		probs_only_1=sorted(i for i in probs_1-probs_2 if int(i[0])<100000)
		probs_only_2=sorted(i for i in probs_2-probs_1 if int(i[0])<100000)
		return render_template('compare.htm',both=probs_both,only1=probs_only_1,only2=probs_only_2,first=user_1,second=user_2)
	else:
		if not user_1_good:
			flash(user_1+' is an invalid handle!')
		if not user_2_good:
			flash(user_2+' is an invalid handle!')
		return redirect(url_for('face'))
@atexit.register
def shutdown():
    if client:
        client.disconnect()
app.secret_key = "Dd\x90'\xa8U\x15\x82D\x8b\x1aj\x05re\x96\xa3\xd2f\xa8\xac\x9b\xa8\x06"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)