from flask import Flask,render_template,request,flash,redirect,url_for
from flask_mysqldb import MySQL
import secrets
from flask import Flask, Response
import reportlab
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
# from flask import Response
# from io import BytesIO
# import pyautogui as pagsales
app=Flask(__name__)
app.secret_key="success"
app.config['MYSQL_HOST']='localhost'
app.config["MYSQL_USER"]='root'
app.config["MYSQL_PASSWORD"]='1234'
app.config["MYSQL_DB"]="aerele"

mysql=MySQL(app)

@app.route("/",methods=["POST","GET"])

def home():
    if request.method=="POST":
        user=request.form["username"]
        passw=request.form["password"]
        #Main Branch Page
        if user=="global" and passw=="g":
            cur=mysql.connection.cursor()
            cur.execute("select * from items")
            list=cur.fetchall()
            return render_template("global.html",value=list)
        #Namma Kadai Admin Page
        elif user=="NammaKadai" and passw=="admin":
            cur=mysql.connection.cursor()
            cur.execute("select * from items")
            list=cur.fetchall()
            cur.execute("select * from purchase")
            list1=cur.fetchall()
            cur.execute("select balance from cash where id=1")
            list2=cur.fetchall()[0][0]
            cur.execute("select * from sales")
            list3=cur.fetchall()
            cur.execute("select sum(profit) from sales")
            lll=cur.fetchall()[0][0]
            return render_template("admin.html",value=list,values=list1,v=list2,v1=list3,p=lll)
        else:
            #user page
            cur=mysql.connection.cursor()
            cur.execute("select * from user where username=%s and password=%s",(user,passw))
            l=cur.fetchall()
            cur.execute("select * from purchase")
            list=cur.fetchall()
            if l:
                #user available
                cur.execute("select * from temp")
                userneed=cur.fetchall()
                return render_template("user.html",value=list,name=l[0][0],value1=userneed)
            else:
                #user not available 
                return render_template("register.html");
    return render_template("login.html")

#Report generation
@app.route('/generate_pdf_report',methods=["POST","GET"])
def generate_pdf_report():
    # Retrieve data from the table (replace this with your actual query)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM sales")
    table_data = cursor.fetchall()
    cursor.close()

    # Create a BytesIO object to hold PDF content
    pdf_buffer = BytesIO()

    # Create a PDF document
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    elements = []

    
    table = Table(table_data)
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.1, 0.3, 0.5)),
        ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),
        ('GRID', (0, 0), (-1, -1), 1, (0.5, 0.5, 0.5)), 
    ]))

    elements.append(table)

    doc.build(elements)

    # Seek to the beginning of the buffer before reading
    pdf_buffer.seek(0)

    # Create a Flask Response with the PDF content
    response = Response(pdf_buffer.read(), content_type='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename="sales_report.pdf"'

    return response

#report generation
@app.route("/logout",methods=["POST","GET"])
def logout():
    if request.method=="POST":
        cur=mysql.connection.cursor()
        cur.execute("truncate table temp")
        cur.connection.commit()
        return redirect("/")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        namee=request.form["username"]
        passw=request.form["password"]
        cur=mysql.connection.cursor()
        cur.execute("select * from user where username=%s",(namee,))
        ll=cur.fetchall()
        if ll:
            #if user already available
            return render_template("register.html",msg="User Exist")
        cur.execute("Insert into user (username,password) values(%s,%s)",(namee,passw))
        cur.connection.commit()
        return redirect("/")    

@app.route("/addproduct",methods=["POST","GET"])
def addproduct():
    if request.method=="POST":
        id=request.form["id"]
        count=request.form["count"]
        product=request.form["product"]
        price=request.form["price"]
        cur=mysql.connection.cursor()
        cur.execute("select * from items where id=%s",(id))
        msg=cur.fetchall()
        if msg or int(count)<0 or int(price) < 0 :
            #if product already exist in the id(Main Branch page)
            cur.execute("select * from items")
            list=cur.fetchall()
            return render_template("global.html",value=list,msg="aaa")
        #No products available on that id    
        cur.execute("Insert into items(id,product,price,count) values (%s,%s,%s,%s)",(int(id),product,int(price),int(count)))
        cur.connection.commit()
        cur.execute("select * from items")
        list=cur.fetchall()
        return render_template("global.html",value=list) 
    return render_template("global.html")

@app.route("/remove",methods=["GET","POST","DELETE"])
def remove():
    id=request.form["id"]
    cur=mysql.connection.cursor()
    cur.execute("select * from items where id=%s",(id))
    mm=cur.fetchall()
    if mm:
        cur.execute("DELETE FROM items WHERE id=%s",(id))
        cur.connection.commit()
        cur.execute("select * from items")
        list=cur.fetchall()
        return render_template("global.html",value=list)
    else:
        cur.execute("select * from items")
        list=cur.fetchall()
        return render_template("global.html",value=list,msg="aaa")

@app.route("/update",methods=["GET","POST","DELETE"])
def update():
    id=request.form["id"]
    count=request.form["count"]
    cur=mysql.connection.cursor()
    cur.execute("select * from items where id=%s",(id))
    mm=cur.fetchall()
    if mm and int(count)>0:
        cur.execute("UPDATE items SET count = %s WHERE id= %s ",(count,id))
        cur.connection.commit()
        cur.execute("select * from items")
        list=cur.fetchall()
        return render_template("global.html",value=list)
    else:
        cur.execute("select * from items")
        list=cur.fetchall()
        return render_template("global.html",value=list,msg="aaa")

@app.route("/add",methods=["GET","POST"])
def add():
    id=request.form["id"]
    count=int(request.form["count"])
    cur=mysql.connection.cursor()
    cur.execute("select * from items where id=%s",(id))
    m=cur.fetchall()
    if m and int(count) > 0:
        cur.execute("select price from items where id=%s",(id))
        rate=int(cur.fetchall()[0][0])
        cur.execute("select balance from cash where id=1")
        balance=int(cur.fetchall()[0][0])
        cur.execute("select count from items where id=%s",(id))
        qty=int(cur.fetchall()[0][0])
        if qty<count:
            cur.execute("select * from purchase")
            list=cur.fetchall()
            cur.execute("select * from items")
            list1=cur.fetchall()
            cur.execute("select balance from cash where id=1")
            list2=cur.fetchall()[0][0]
            cur.execute("select * from sales")
            list3=cur.fetchall()
            cur.execute("select sum(profit) from sales")
            lll=cur.fetchall()[0][0]
            msg="We don't that much of products"
            return render_template("admin.html",values=list,value=list1,v=str(list2),v1=list3,p=lll,msg=msg)
        if int(rate)*int(count) <= int(balance) and qty>=count:
            flash("Data Inserted","error")
            x=balance-rate*count
            y=rate*count
            cur.execute("UPDATE cash SET balance = %s WHERE id= %s ",(x,1))
            cur.connection.commit()
            cur.execute("select product from items where id=%s",(id))
            product=cur.fetchall()[0][0]
            cur.execute("select * from purchase where id=%s",(id))
            ex=cur.fetchall()
            if not ex:
                cur.execute("Insert into purchase (id,product,price,count,amount) values (%s,%s,%s,%s,%s)",(id,product,rate,count,y))
                cur.connection.commit()
            else:
                cur.execute("select count from purchase where id=%s",(id))
                c=cur.fetchall()[0][0]
                c=c+count
                cur.execute("select amount from purchase where id=%s",(id))
                t=cur.fetchall()[0][0]
                t=t+y
                cur.execute("update purchase set count=%s where id=%s",(c,id))    
                cur.connection.commit()
                cur.execute("update purchase set amount=%s where id=%s",(t,id))    
                cur.connection.commit()
        
            cur.execute("select count from items where id=%s",(id))
            initialcount=cur.fetchall()[0][0]
            initialcount=initialcount-count
            cur.execute("update items set count=%s where id=%s",(initialcount,id))
            cur.connection.commit()
            if initialcount<=0:
                cur.execute("delete from items where id=%s",(id))
                cur.connection.commit()
            cur.execute("select * from purchase")
            list=cur.fetchall()
            cur.execute("select * from items")
            list1=cur.fetchall()
            cur.execute("select balance from cash where id=1")
            list2=cur.fetchall()[0][0]
            cur.execute("select * from sales")
            list3=cur.fetchall()
            cur.execute("select sum(profit) from sales")
            lll=cur.fetchall()[0][0]
            return render_template("admin.html",values=list,value=list1,v=str(list2),v1=list3,p=lll)
    else:
        cur.execute("select * from purchase")
        list=cur.fetchall()
        cur.execute("select * from items")
        list1=cur.fetchall()
        cur.execute("select balance from cash where id=1")
        list2=cur.fetchall()[0][0]
        cur.execute("select * from sales")
        list3=cur.fetchall()
        cur.execute("select sum(profit) from sales")
        lll=cur.fetchall()[0][0]
        msg="No products like that"
        return render_template("admin.html",values=list,value=list1,v=str(list2),v1=list3,p=lll,msg=msg)
    
@app.route("/buy/<name>",methods=["GET","POST"])
def buy(name):
    id=request.form["id"]
    count=request.form["count"]
    cur=mysql.connection.cursor()
    cur.execute("select * from purchase where id=%s",(id))
    data=cur.fetchall()
    if data and int(count)>0:
        product=data[0][1]
        costprice= data[0][2]
        qty=data[0][3]
        if int(qty)<int(count):
            cur.execute("select * from purchase")
            list=cur.fetchall()
            cur.execute("select * from temp")
            list2=cur.fetchall()
            msg="No products"
            return render_template("user.html",name=name,value=list,value1=list2,msg=msg)    
        soldprice=costprice+3
        profit=(int(soldprice)*int(count))-(int(costprice)*int(count))
        cur.execute("insert into sales (user,item,costprice,soldprice,profit,quantity) values (%s,%s,%s,%s,%s,%s)",(name,product,costprice,soldprice,int(profit),count))
        cur.connection.commit()
        amt=(int(soldprice)*int(count))
        cur.execute("select * from temp where id=%s",(id))
        l=cur.fetchall()
        if not l:
            cur.execute("insert into temp (id,product,price,quantity,amount) values(%s,%s,%s,%s,%s)",(id,product,soldprice,count,amt))
            cur.connection.commit()
        else:
            q=int(l[0][3])+int(count)
            p=int(l[0][4])+(int(soldprice)*int(count))
            cur.execute("update temp set amount=%s where id=%s",(p,id))
            cur.connection.commit()
            cur.execute("update temp set quantity=%s where id=%s",(q,id))
            cur.connection.commit()    
        qty=int(qty)-int(count)
        if qty>0:
            cur.execute("update purchase set count=%s where id=%s",(qty,id))
            cur.connection.commit()
        else:
            cur.execute("delete from purchase where id=%s",(id))
            cur.connection.commit()    
        cur.execute("select balance from cash where id=1")
        bal=cur.fetchall()[0][0]
        bal=int(bal)+(int(soldprice)*int(count))
        cur.execute("update cash set balance=%s where id=%s",(bal,1))
        cur.connection.commit()
        cur.execute("select * from purchase")
        list=cur.fetchall()
        cur.execute("select * from temp")
        list2=cur.fetchall()
        return render_template("user.html",name=name,value=list,value1=list2)
    else:
        cur.execute("select * from purchase")
        list=cur.fetchall()
        cur.execute("select * from temp")
        list2=cur.fetchall()
        msg="No products"
        return render_template("user.html",name=name,value=list,value1=list2,msg=msg)

if __name__== "__main__":
    app.run(debug=True)