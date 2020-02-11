from flask import Flask,request,redirect,url_for,jsonify
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split 
from sklearn import metrics
import sqlite3 , time
from sqlalchemy import create_engine
from datetime import datetime
from flask_cors import CORS


def predict(df3,value):
    X,y = df3[1].values.reshape(-1,1),df3[2].values.reshape(-1,1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    regressor = LinearRegression()
    regressor.fit(X,y)
    y_pred = regressor.predict(X_test)
    pred = regressor.predict(value)
    return(pred)

app = Flask(__name__)
CORS(app)
@app.route('/') 
def run_data(): 
    run = request.args.get('run', default = '0', type = str)
    user_id = request.args.get('user_id', default = '0', type = str)
    print(user_id)
    user_id =user_id.replace('-','_')
    print(user_id)
    #day=request.args.get('day', default = '0', type = str)
    engine = create_engine('sqlite:///user.db', echo=False)
    df = pd.read_csv('file1.csv',index_col='day')
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='user%s' '''%user_id)
    if c.fetchone()[0]==1 : 
        #print('Table exists.')
        pass
    else :
        df.to_sql('user%s'%user_id, con=engine)
    conn.commit()
    conn.close()
    df = pd.DataFrame(engine.execute("SELECT * FROM user%s"%user_id).fetchall())
    #print(df.tail)
    #day = df.values[-1][0]+1
    day_n1=0##this is to be predicted
    day_n=float(run)##value fetched from website
    day=df.values[-1][0]
    day= str(int(day+1))
    date = datetime.fromtimestamp(time.time()+19800).strftime(format('%-m/%-d/%Y'))
    #print(day)
    if day=='150':
        day_n_1=day_n
        day_n1 = 0
        #print('prediction for next day: '+ str(day_n1))
        conn = sqlite3.connect('user.db')
        conn.execute("INSERT INTO user%s VALUES (%s,%s,%s)"%(user_id,day,day_n_1,str(day_n)));
        conn.commit()
        conn.close()
    else:
        day_n_1=df.values[-1][1]
        day_n1 = predict(df,np.array([[day_n]]).reshape(-1,1))[0][0]
        #print('prediction for next day: '+ str(day_n1))
        conn = sqlite3.connect('user.db')
        conn.execute("INSERT INTO user%s VALUES (%s,%s,%s)"%(user_id,day,day_n_1,str(day_n)));
        conn.commit()
        conn.close()
    return jsonify(
        userid=user_id,
        run=run,
        prediction = str(abs(round(float(day_n1),3))),
        day = str(int(day)-150),
        date = date
    )

 
if __name__ == "__main__":
    app.run(environ.get('PORT'))
