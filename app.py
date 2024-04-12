from flask import Flask,render_template,request,redirect,flash
from flask_mysqldb import MySQL

app=Flask(__name__)
app.config['SECRET_KEY'] = 'kavil'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='root'
app.config['MYSQL_DB']='warehouse'

mysql=MySQL(app)

@app.route('/',methods=['GET','POST'])
def Global():
    if request.method=="POST":
        user =request.form['un']
        key=request.form['pw']
        cur=mysql.connection.cursor()
        cur.execute("select*from login where Username=%s",(user,))
        ex=cur.fetchone()
        if user=="admin" and key=="admin@121":
            # cur.execute("INSERT INTO login_details(Username,password)values(%s,%s)",(user,key))
            # mysql.connection.commit()
            return redirect('/gadmin')
        else:
            if user==ex[1] and key==ex[2]:
                return redirect('/product')
    return render_template("index.html")

@app.route('/signup',methods=['GET','POST'])
def signup():
    nme=request.form['name']
    username=request.form['us']
    password=request.form['pass']
    cur=mysql.connection.cursor()
    query = "select * from login where Name=%s"
    cur.execute(query,(nme,))
    ex=cur.fetchall()
    if not ex:
        cur.execute("insert into login(Name,Username,Password)values(%s,%s,%s)",(nme,username,password))
        mysql.connection.commit()
        return redirect('/')    
@app.route('/gadmin',methods=['GET','POST'])
def select():
    cur=mysql.connection.cursor()
    cur.execute("select*from Item")
    value=cur.fetchall()
    #cur.close()
    return render_template("global_admin.html",data=value)

@app.route('/insert',methods=['GET', 'POST'])
def insert():
    Id =request.form['id']
    pname=request.form['pn']
    pprice=request.form['pa']
    cur=mysql.connection.cursor()
    cur.execute("INSERT INTO Item(Item_id,Item_name,Item_price)values(%s, %s, %s)",(int(Id),pname,int(pprice)))
    mysql.connection.commit()
    return redirect('/gadmin')

@app.route('/delete/<int:Item_id>', methods=['GET','POST','DELETE'])
def delete(Item_id):
    cur=mysql.connection.cursor()
    cur.execute("DELETE FROM Item WHERE Item_id=%s",(Item_id,))
    mysql.connection.commit()
    return redirect('/gadmin')

@app.route('/product')
def view():
    cur=mysql.connection.cursor()
    cur.execute("select*from Item")
    value=cur.fetchall()
    
    cur.execute("select*from stock")
    ex=cur.fetchall()
    
    cur.execute("select*from purchase")
    ps=cur.fetchall()
    
    cur.execute("select*from sales")
    ss=cur.fetchall()
    
    cur.execute("select*from company")
    cp=cur.fetchone()
    
    return render_template("order.html",data=value,value=ex,buy=ps,sale=ss,com=cp)

#Add a Product in Stock

@app.route('/add/<int:Item_id>', methods=['GET', 'POST'])
def add(Item_id):
    qty=request.form["quantity"]
    if qty > "0":
        total=request.form["total_display"]
        cur=mysql.connection.cursor()
        cur.execute("select Item_name,Item_price from Item where Item_id=%s",(Item_id,))
        value=cur.fetchall()
        mysql.connection.commit()
        first=value[0][0]
        second=value[0][1]
        cur.execute("select*from stock where Item_id=%s",(Item_id,))
        ex=cur.fetchall()
        cur.execute("select*from company")
        cash=cur.fetchone()
        no=cash[0]
        ca=cash[2]-int(total)
    
        if not ex:
            cur.execute("INSERT INTO stock(Item_id,Item_name,Item_price,count,total_amount)VALUES(%s,%s,%s,%s,%s)",(Item_id,first,int(second),int(qty),int(total)))
            mysql.connection.commit()
        
            cur.execute("INSERT INTO purchase (Item_id, qty, rate, amount) VALUES (%s, %s, %s, %s)",(Item_id,int(qty),int(total),int(ca)))
            mysql.connection.commit()
        
            cur.execute("UPDATE company set cash_balance=%s where company_id=%s",(int(ca),int(no)))
            mysql.connection.commit()
        else:
        
            cur.execute("UPDATE stock set count=count+%s,total_amount=total_amount+%s where Item_id=%s",(int(qty),int(total),Item_id,))
            mysql.connection.commit()
        
            cur.execute("INSERT INTO purchase (Item_id, qty, rate, amount) VALUES (%s, %s, %s, %s)",(Item_id,int(qty),int(total),int(ca)))
            mysql.connection.commit()
        
            cur.execute("UPDATE company set cash_balance=%s where company_id=%s",(int(ca),int(no)))
            mysql.connection.commit()
        return redirect('/product')
    else:
        return redirect('/product')
#Remove a stock

@app.route('/remove/<int:Product_Id>', methods=['GET','POST', 'DELETE'])
def remove(Product_Id):
    cur = mysql.connection.cursor()
    print(Product_Id)
    cur.execute("DELETE FROM stock WHERE Item_id=%s", (Product_Id,))
    mysql.connection.commit()
    return redirect('/product')

#sale a product
@app.route('/sale/<int:Product_id>',methods=['GET','POST'])
def sale(Product_id):
    count=request.form["count"]
    if count > "0":
        total=request.form["display"]
        cur=mysql.connection.cursor()
        cur.execute("select*from stock where Item_id=%s",(Product_id,))
        ex=cur.fetchone()
        # value=ex[3]-int(count)
        
        amount=ex[4]-(int(total)-2)
        cur.execute("select*from company")
        cash=cur.fetchone()
        no=cash[0]
        ca=cash[2]+int(total)
        
        cur.execute("UPDATE stock set count=count-%s,total_amount=total_amount-%s where Item_id=%s",(int(count),int(amount),Product_id,))
        mysql.connection.commit()
    
        cur.execute("INSERT INTO sales (Item_id, quantity, rate, amount) VALUES(%s,%s,%s,%s)",(Product_id,int(count),int(total),int(ca)))
        mysql.connection.commit()
    
        cur.execute("UPDATE company set cash_balance=cash_balance+%s where company_id=%s",(int(total),int(no)))
        mysql.connection.commit()
    
        return redirect('/product')
    else:
        return redirect('/product')
        
if __name__=="__main__":
    app.run(debug=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    