from flask import Flask, render_template, request,redirect
import json
import requests

app=Flask(__name__)

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
		if i['verdict']=='OK':
			ans.add(str(i['problem']['contestId'])+i['problem']['index'])
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
	return render_template('index.htm',mybool=True)
@app.route('/compare',methods=['POST'])
def compare_results():
	user_1=request.form['user1']
	print(user_1)
	while True:
		x=validate(user_1)
		print(x)
		if x==True:
			break
		if x==False:
			return render_template('index.htm',mybool=False)
	user_2=request.form['user2']
	print(user_2)
	while True:
		x=validate(user_2)
		print(x)
		if x==True:
			break
		if x==False:
			return render_template('index.htm',mybool=False)
	while True:
		probs_1=get_problems_solved(user_1)
		if probs_1 is not None:
			break
	while True:
		probs_2=get_problems_solved(user_2)
		if probs_2 is not None:
			break
	print(len(probs_1))
	print(len(probs_2))
	probs_both=sorted(probs_1&probs_2)
	probs_only_1=sorted(probs_1-probs_2)
	probs_only_2=sorted(probs_2-probs_1)
	return render_template('compare.htm',both=probs_both,only1=probs_only_1,only2=probs_only_2)

app.run(debug=True)