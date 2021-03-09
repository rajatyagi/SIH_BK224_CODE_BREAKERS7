from flask import Flask, render_template, redirect, request, url_for , send_file
import numpy as np
import pandas as pd
import csv
from pycaret.regression import *

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/', methods = ['POST']) 
def result():
    if request.method == 'POST':
        to_predict_list = request.form.to_dict()
        sih_model = load_model('model')
        
        sd_v,sd_i,sd_t,sd_w,sd_age,a_v,a_i,a_t,a_w,a_age,a_pf,a_e = 14.450315,1.184078,14.724061,11.850687,3,425.041214,10.004947,55.033790,99.990990,5,0.65,80.63        
        
        def warnings(pv1,pi1,t1,pf1,e):
            outstr = ""
            if pv1 > a_v + 1.2*sd_v : outstr += "High voltage ,"
            if t1 > a_t + 1.2*sd_t : outstr += "Overheating ,"
            if pv1*pi1*pf1*e/100 > 1.5*a_v*a_i*a_pf*a_e/100 : outstr += "Overloading ,"
            if len(outstr)==0 : outstr += "No Warnings"
            return outstr
                       
        def suggestions(pi1,t1,pf1,e):
            if  e >= 85.56 and t1 < 60:
                return "The asset is running efficiently any changes may make the asset less reliable. \n"
            elif e >= 85.56 and t1 >= 60:
                return "Asset cooling to" + str(t1*0.8) + "'C will give better efficiency. \n"
            else :
                if t1 < 60 and (pi1 != 8 or pf1 != 0.5):
                    return "Efficiency can be increased by decreasing current to " + str(round((max(pi1*0.95,8)),4)) + " Amps or \n\tcorrecting the power factor to " + str(round(max(pf1*0.9,0.5),3)) + ". \n"
                elif t1 >= 60 and (pi1 != 8 or pf1 != 0.5 or t1 != 60):
                    return "Efficiency can be increased by decreasing current to " + str(round((max(pi1*0.95,8)),4)) + " Amps, \n\tcorrecting the power factor to " + str(round(max(pf1*0.9,0.5),3)) + " or \n\treducing the temperature to " + str(round(t1*0.8,2)) + " 'C. \n"
                else : return "The asset is running efficiently any changes may make the asset less reliable. \n"
            
        def relia(pv1, pi1, t1, a1, w1):                
            reliabilty = 5
            if pv1 > a_v + 1.2*sd_v:
                reliabilty -=1
            if pi1 > a_i + 1.2*sd_i:
                reliabilty -=1
            if t1 > a_t + 1.2*sd_t:
                reliabilty -=1
            if w1 > a_w + 1.2*sd_w:
                reliabilty -=1
            if a1 > a_age + sd_age:
                reliabilty -=1

            if reliabilty == 5:
                return 'Highly Reliable'
            if reliabilty == 3 or reliabilty == 4:
                return 'Moderately Reliable'
            if reliabilty == 1 or reliabilty == 2:
                return 'Less Reliable'
            if reliabilty == 0:
                return 'Not Reliable'
        
        pv1 = to_predict_list['voltage']
        pi1 = to_predict_list['current']
        po1 = to_predict_list['poles']
        f1 = to_predict_list['frequency']
        pf1 = to_predict_list['cosq']
        t1 = to_predict_list['temperature']
        l1 = to_predict_list['load']
        w1 = to_predict_list['angvel']
        a1 = to_predict_list['age']
        
        if len(pv1)==0:
           pv1 = 425.041214
        if len(pi1)==0:
            pi1 = 10.004947
        if len(po1)==0:
            po1 = 3
        if len(f1)==0:
            f1 = 50
        if len(pf1)==0:
            pf1 = 0.650188
        if len(t1)==0:
            t1 = 55
        if len(l1)==0:
            l1 = 85
        if len(w1)==0:
            w1 = 100
        if len(a1)==0:
            a1 = 5
        
        v = pv1
        i = pi1
        f = f1
        pf = pf1
        t = t1
        l = l1
        av = w1
        a = a1
        p = po1

        pv1 = float(pv1)
        pi1 = float(pi1)
        po1 = float(po1)
        f1 = float(f1)
        pf1 = float(pf1)
        t1 = float(t1)
        l1 = float(l1)
        w1 = float(w1)
        a1 = float(a1)

       
        
        pv,pi,po,f,pf,t,l,w,a= [pv1],[pi1],[po1],[f1],[pf1],[t1],[l1],[w1],[a1]
        df = pd.DataFrame(list(zip(pv,pi,po,f,pf,t,l,w,a)),columns = ['3 Phase Voltage in Volts','3 Phase Current in Amps','Poles','Frequency in Hz','Power Factor','Temperature in Celcius','% Load','Angular Velocity in rad/sec','Motor Age in Yrs'])
       
        pred_new = predict_model(sih_model,data=df)
        r = relia(pred_new['3 Phase Voltage in Volts'][0],pred_new['3 Phase Current in Amps'][0],pred_new['Temperature in Celcius'][0],pred_new['Motor Age in Yrs'][0],pred_new['Angular Velocity in rad/sec'][0])
        e = pred_new['Label'][0]
        c = 0
        ctr = round(50 - (3500/e),0)
        if ctr < 0 : ctr = 0
        c = abs(ctr)

        efficiency =str(e)+" %"
        reliability = r
        age =str(int(c))+" Years"
        warnings = warnings(pred_new['3 Phase Voltage in Volts'][0],pred_new['3 Phase Current in Amps'][0],pred_new['Temperature in Celcius'][0],pred_new['Power Factor'][0],e)
        suggestions = suggestions(pred_new['3 Phase Current in Amps'][0],pred_new['Temperature in Celcius'][0],pred_new['Power Factor'][0],e)

        
    return render_template("index.html", efficiency = efficiency, reliability = reliability, age = age, warnings = warnings, suggestions = suggestions, v = v,i = i, f = f, pf = pf, t = t, l = l, av = av, a = a, p = p)

@app.route("/page2")
def page2():
	return render_template("page2.html")

@app.route("/page2", methods = ['POST','GET'])
def data():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            uploaded_file.save(uploaded_file.filename)
        
        return redirect(url_for('page2'))
        
        test = pd.read_csv(uploaded_file.filename)
        
        sih_model = load_model('model')
        
        def relia(pv1, pi1, t1, a1, w1):
            sd_v,sd_i,sd_t,sd_w,sd_age,a_v,a_i,a_t,a_w,a_age = 14.450315,1.184078,14.724061,11.850687,3,425.041214,10.004947,55.033790,99.990990,5        
            reliabilty = 5
            if pv1 > a_v + 1.2*sd_v:
                reliabilty -=1
            if pi1 > a_i + 1.2*sd_i:
                reliabilty -=1
            if t1 > a_t + 1.2*sd_t:
                reliabilty -=1
            if w1 > a_w + 1.2*sd_w:
                reliabilty -=1
            if a1 > a_age + sd_age:
                reliabilty -=1

            if reliabilty == 5:
                return 'Highly Reliable'
            if reliabilty == 3 or reliabilty == 4:
                return 'Moderately Reliable'
            if reliabilty == 1 or reliabilty == 2:
                return 'Less Reliable'
            if reliabilty == 0:
                return 'Not Reliable'

        pred_new = predict_model(sih_model,data=test)
        trained = test

        r,c=[],[]

        for i in range(pred_new.count()[1]):
            r.append(relia(pred_new['3 Phase Voltage in Volts'][i],pred_new['3 Phase Current in Amps'][i],pred_new['Temperature in Celcius'][i],pred_new['Motor Age in Yrs'][i],pred_new['Angular Velocity in rad/sec'][i]))
            e1 = pred_new['Label'][i]
            ctr = round(50 - (3500/e1),0)
            if ctr < 0 : ctr = 0
            c.append(abs(ctr))

        trained['Reliability_Check'] = r
        trained['Life Cycle in Yrs_Check'] = c
        trained['Predicted Effeciency_Check'] = pred_new['Label']

        test.to_csv('./predicted_data.csv',index=False)
        path = "predicted_data.csv"
        return send_file(path, as_attachment=True)
        

        result = "Model Successfully Trained"
            # return render_template("page2.html", "Model Successfully Trained")
    return render_template("page2.html", result = result)


@app.route("/photos")
def photos():
	return render_template("photos.html")

@app.route("/train")
def train():
	return render_template("train.html")

@app.route("/train", methods = ['POST'])

def train_data():
	if request.method == 'POST':
		uploaded_file = request.files['file']
		if uploaded_file.filename != '':
			uploaded_file.save(uploaded_file.filename)
		data_set = pd.read_csv(uploaded_file.filename)
		exp1 = setup(data_set, target = 'Efficiency in %',
	             ignore_features=['% Load','Reliability','Life Cycle in Yrs'],
	             numeric_features=['Motor Age in Yrs','Frequency in Hz'],
	             categorical_features=['Poles'], normalize=True,silent=True)
		xgboost_gpu = create_model('xgboost',tree_method = 'gpu_hist', gpu_id = 0,fold=20)


		pred_new = predict_model(xgboost_gpu)

		def relia(pv1, pi1, t1, a1, w1): 
		    
		    sd_v,sd_i,sd_t,sd_w,sd_age,a_v,a_i,a_t,a_w,a_age = 14.450315,1.184078,14.724061,11.850687,3,425.041214,10.004947,55.033790,99.990990,5        
		    
		    reliabilty = 5
		    if pv1 > a_v + 1.2*sd_v:
		        reliabilty -=1
		    if pi1 > a_i + 1.2*sd_i:
		        reliabilty -=1
		    if t1 > a_t + 1.2*sd_t:
		        reliabilty -=1
		    if w1 > a_w + 1.2*sd_w:
		        reliabilty -=1
		    if a1 > a_age + sd_age:
		        reliabilty -=1

		    if reliabilty == 5:
		        return 'Highly Reliable'
		    if reliabilty == 3 or reliabilty == 4:
		        return 'Moderately Reliable'
		    if reliabilty == 1 or reliabilty == 2:
		        return 'Less Reliable'
		    if reliabilty == 0:
		        return 'Not Reliable'

		r,c=[],[]

		for i in range(pred_new.count()[1]):
		    r.append(relia(pred_new['3 Phase Voltage in Volts'][i],pred_new['3 Phase Current in Amps'][i],pred_new['Temperature in Celcius'][i],pred_new['Motor Age in Yrs'][i],pred_new['Angular Velocity in rad/sec'][i]))
		    e1 = pred_new['Label'][i]
		    ctr = round(50 - (3500/e1),0)
		    if ctr < 0 : ctr = 0
		    c.append(abs(ctr))

		pred_new['Reliability'] = r
		pred_new['Life Cycle in Yrs'] = c

		pred_new.head()
		lr_final = finalize_model(xgboost_gpu)
		save_model(xgboost_gpu, './model')

	return render_template("train.html")




if __name__ == '__main__':
	#app.debug = True
	app.run(debug = True)
