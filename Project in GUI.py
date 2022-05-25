from tkinter import *
import tkinter as tk
import tkinter.ttk
from tkinter import END, Canvas, PhotoImage, ttk
import tkinter.messagebox
import sqlite3
from datetime import date
from dateutil.relativedelta import relativedelta
today = date.today()
conn = sqlite3.connect(r'Project DB.db')
c = conn.cursor()

def create_table():
    c.execute('''CREATE TABLE book(id integer PRIMARY KEY AUTOINCREMENT,
                type varchar(50) NOT NULL,
                name varchar(100) NOT NULL,
                status varchar(50) NOT NULL,
                borrow_by varchar(100) NOT NULL,
                phone_num varchar(12) NOT NULL,
                return_book varchar(50) NOT NULL)''')
    c.execute('''CREATE TABLE user(id integer PRIMARY KEY AUTOINCREMENT,
                name varchar(100) NOT NULL,
                phone_num varchar(12) NOT NULL,
                borrow_id varchar(50) NOT NULL,
                borrow_date varchar(50) NOT NULL,
                borrow_end varchar(50) NOT NULL,
                price varchar(50) NOT NULL)''')
    conn.commit()

def add_book():
    def button_command():
        type = choiceEntry.get()
        name = nameEntry.get()
        c.execute('''INSERT INTO book (type, name, status, borrow_by, phone_num, return_book) VALUES (?, ?, "Not Borrow", "None", "None", "None")''',(type, name.title()))
        conn.commit()
        tkinter.messagebox.showinfo('เสร็จสิ้น','เพิ่มหนังสือเรียบร้อย')
        add.destroy()
        refresh()

    add = tk.Tk()
    add.title('เพิ่มหนังสือ')
    add.resizable(0,0)
    add.option_add('*Font','Calibri 16')

    tk.Label(add, text='ประเภทหนังสือ').grid(row=0, column=1)
    tk.Label(add, text='ชื่อหนังสือ').grid(row=2, column=1)

    choiceEntry = tk.StringVar(add, value='เลือกประเภทของหนังสือ')
    typebook = ttk.Combobox(add, textvariable=choiceEntry)
    typebook['values'] = ('หนังสือเรียน','หนังสือนิยาย','หนังสือการ์ตูน')
    typebook.grid(row=1, column=1)
    nameEntry = tk.Entry(add)
    nameEntry.grid(row=3, column=1)
    tk.Button(add, text='เพิ่มหนังสือ', bg='green', fg='white', command=button_command).grid(row=4,column=1)
    
    add.mainloop()

def delete_book():
    idbook = idEntry.get()
    c.execute(f'''SELECT * FROM book WHERE id like "%{idbook}%"''')
    books = c.fetchall()
    if books:
        if idbook.isnumeric():
            ask = tkinter.messagebox.askyesno('ลบหนังสือ','ต้องการที่จะลบหนังสือหรือไม่')
            if ask == True:
                c.execute('''DELETE FROM book WHERE id = ?''',[idbook])
                tkinter.messagebox.showinfo('เสร็จสิ้น','ลบหนังสือเรียบร้อย')
                conn.commit()
                idEntry.delete(0, END)
                refresh()
    else:
        tkinter.messagebox.showinfo('ผิดพลาด','ID หนังสือไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง')

def search_book_name_command():
    all_book.delete(*all_book.get_children())
    namebook = nameEntry.get()

    c.execute(f'''SELECT * FROM book WHERE name like "%{namebook}%" ORDER BY name''')
    books = c.fetchall()
    if books:
        for book in books:
            all_book.insert('','end', values=(book))
    else:
        tkinter.messagebox.showinfo('ผิดพลาด','ไม่เจอรายชื่อหนังสือที่ตรงกับที่ท่านค้นหา')
        refresh()

    root.mainloop()

def search_book_type_command():  
    all_book.delete(*all_book.get_children())
    typebook = typeEntry.get()

    c.execute(f'''SELECT * FROM book WHERE type like "%{typebook}%" ORDER BY name''')
    books = c.fetchall()
    for book in books:
        all_book.insert('','end', values=(book))

    root.mainloop()

def borrow_book():
    def borrow_windows():

        def borrow_command():
            idbook = idBorrow.get()
            name = nameBorrow.get()
            phone = phonBorrow.get()
            return_day = dayBorrow.get()
            next = (today + relativedelta(days=int(return_day)))
            c.execute(f'''SELECT * FROM book WHERE id ="{idbook}"''')
            borrow = c.fetchone()
            if borrow:
                c.execute(f'''UPDATE book SET borrow_by ="{name.title()}" WHERE id ="{idbook}"''')
                c.execute(f'''UPDATE book SET return_book ="{next}" WHERE id ="{idbook}"''')
                c.execute(f'''UPDATE book SET phone_num ="{phone}" WHERE id ="{idbook}"''')
                c.execute(f'''UPDATE book SET status ="Borrow" WHERE id ="{idbook}"''')
                c.execute('''INSERT INTO user (name, phone_num, borrow_id, borrow_date, borrow_end, price) VALUES (?, ?, ?, ?, ?, ?)''',(name.title(), phone, idbook, today, next, result))
                conn.commit()
                tkinter.messagebox.showinfo('เสร็จสิ้น','ทำการยืมหนังสือเรียบร้อย\nขอบคุณที่ใช้บริการค่ะ')
                root.destroy()
                borrowWin.destroy()
                refresh()
        
        borrowWin = tk.Tk()
        borrowWin.title('ยืมหนังสือ')
        borrowWin.resizable(0,0)
        borrowWin.option_add('*Font','Calibri 16')

        idbook = idBorrow.get()
        c.execute(f'''SELECT * FROM book WHERE id ="{idbook}"''')
        book = c.fetchone()
        num = dayBorrow.get()
        result = int(num)*7
        tk.Label(borrowWin, text='หนังสือที่ท่านต้องการยืมคือ').grid(row=1, column=1)
        tk.Label(borrowWin, text=(book[2])).grid(row=2, column=1)
        tk.Label(borrowWin, text='จำนวน {} วัน'.format(num)).grid(row=3, column=1)
        tk.Label(borrowWin, text='รวมค่าบริการ {} บาท'.format(result)).grid(row=4, column=1)
        tk.Button(borrowWin, text='ยืนยัน', bg='green', fg='white', command=borrow_command).grid(row=5, column=1)
        borrowWin.mainloop()
        
    def check():
        phon = phonBorrow.get()
        day = dayBorrow.get()
        id = idBorrow.get()
        name = nameBorrow.get()
        c.execute(f'''SELECT * FROM book WHERE id ="{id}" AND status like "Not Borrow"''')
        borrow = c.fetchone()
        if borrow:
            if phon.isnumeric() and len(phon) == 10 and day.isnumeric() and 0 < int(day) <= 14 and id.isnumeric() and name.replace(' ','').isalpha():
                borrow_windows()
            else:
                tkinter.messagebox.showinfo('ผิดพลาด','ท่านกรอกข้อมูลบางส่วนผิดพลาดกรุณาตรวจสอบอีกครั้ง')
        else:
            tkinter.messagebox.showinfo('ผิดพลาด','ID หนังสือไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง')

    root = tk.Tk()
    root.option_add('*Font','Calibri 16')
    all_book = tkinter.ttk.Treeview(root)
    all_book.grid(row=1,column=1)
    root.title('ยืมหนังสือ')
    root.resizable(0,0)

    c.execute('''SELECT * FROM book WHERE status like "Not Borrow" ORDER BY name ''')
    books = c.fetchall()

    tk.Label(root, text = ('หนังสือที่สามารถยืมได้')).grid(row=0,column=1)
    all_book['show'] = 'headings'
    all_book['columns'] = ('id','type','name')

    all_book.heading('id', text = 'ID หนังสือ')
    all_book.heading('type', text = 'ประเภท')
    all_book.heading('name', text = 'ชื่อ')

    all_book.column('id', width = 60)
    all_book.column('type', width = 80)
    all_book.column('name', width = 150)

    for book in books:
        all_book.insert('','end', values=(book[0],book[1],book[2]))
        
    tk.Label(root, text='กรอกเลข ID หนังสือที่ต้องการจะยืม').grid(row=2, column=1)
    tk.Label(root, text='กรอกชื่อผู้ยืม (กรอกภาษาอังกฤษ)').grid(row=4, column=1)
    tk.Label(root, text='กรอกเบอร์โทรผู้ยืม').grid(row=6, column=1)
    tk.Label(root, text='กรอกจำนวนวันที่ต้องการจะยืม (สามารถยืมได้ไม่เกิน 14 วัน)').grid(row=8, column=1)
    tk.Label(root, text='ค่าบริการในการยืม 7 บาท/วัน').grid(row=12, column=1)
    idBorrow = tk.Entry(root)
    idBorrow.grid(row=3,column=1)
    nameBorrow = tk.Entry(root)
    nameBorrow.grid(row=5,column=1)
    phonBorrow = tk.Entry(root)
    phonBorrow.grid(row=7,column=1)
    dayBorrow = tk.Entry(root)
    dayBorrow.grid(row=10,column=1)
    tk.Button(root, text='ตกลง', bg='green', fg='white', command=check).grid(row=11,column=1)
    
    root.mainloop()

def return_book():
    def return_command():
        idbook = idReturn.get()
        c.execute(f'''SELECT id FROM book WHERE id ="{idbook}" AND status like"Borrow"''')
        returnbook = c.fetchone()
        if returnbook:
            if idbook.isnumeric():
                c.execute(f'''UPDATE book SET borrow_by ="None" WHERE id ="{idbook}"''')
                c.execute(f'''UPDATE book SET return_book ="None" WHERE id ="{idbook}"''')
                c.execute(f'''UPDATE book SET phone_num ="None" WHERE id ="{idbook}"''')
                c.execute(f'''UPDATE book SET status ="Not Borrow" WHERE id ="{idbook}"''')
                c.execute('''DELETE FROM user WHERE borrow_id = ?''',[idbook])
                conn.commit()
                tkinter.messagebox.showinfo('เสร็จสิ้น','ทำการคืนหนังสือเรียบร้อย')
                root.destroy()
                refresh()
        else:
            tkinter.messagebox.showinfo('ผิดพลาด','ID หนังสือไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง')

    root = tk.Tk()
    root.option_add('*Font','Calibri 16')
    all_book = tkinter.ttk.Treeview(root)
    all_book.grid(row=1,column=1)
    root.title('คืนหนังสือ')
    root.resizable(0,0)

    c.execute('''SELECT * FROM book WHERE status like "Borrow"''')
    books = c.fetchall()

    tk.Label(root, text = ('หนังสือที่โดยยืม')).grid(row=0,column=1)
    all_book['show'] = 'headings'
    all_book['columns'] = ('id','type','name','borrow','phone','return')

    all_book.heading('id', text = 'ID หนังสือ')
    all_book.heading('type', text = 'ประเภท')
    all_book.heading('name', text = 'ชื่อ')
    all_book.heading('borrow', text = 'ผู้ยืม')
    all_book.heading('phone', text = 'เบอร์ติดต่อผู้ยืม')
    all_book.heading('return', text = 'วันที่ต้องคืน')

    all_book.column('id', width = 60)
    all_book.column('type', width = 80)
    all_book.column('name', width = 150)
    all_book.column('borrow', width = 150)
    all_book.column('phone', width = 80)
    all_book.column('return', width = 100)

    for book in books:
        all_book.insert('','end', values=(book[0],book[1],book[2],book[4],book[5],book[6]))

    tk.Label(root, text='กรอกเลข ID หนังสือที่ต้องการจะคืน').grid(row=2, column=1)
    idReturn = tk.Entry(root)
    idReturn.grid(row=3, column=1)
    tk.Button(root, text='ตกลง', bg='green', fg='white' , command=return_command).grid(row=4, column=1)
    root.mainloop()

def edit_book():
    def edit_command():
        idbook = idEdit.get()
        newtype = choiceEntry.get()
        newname = nameEdit.get()
        c.execute(f'''SELECT * FROM book WHERE id ="{idbook}"''')
        edit = c.fetchone()
        if edit:
            if idbook.isnumeric() and newname:
                c.execute(f'''UPDATE book SET type ="{newtype}" WHERE id ="{idbook}"''')
                c.execute(f'''UPDATE book SET name ="{newname.title()}" WHERE id ="{idbook}"''')
                conn.commit()
                tkinter.messagebox.showinfo('เสร็จสิ้น','แก้ไขข้อมูลหนังสือเรียบร้อย')
                root.destroy()
                refresh()
            else:
                tkinter.messagebox.showinfo('ผิดพลาด','กรุณากรอกข้อมูลให้ครบ')
        else:
            tkinter.messagebox.showinfo('ผิดพลาด','ID หนังสือไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง')

    root = tk.Tk()
    root.option_add('*Font','Calibri 16')
    all_book = tkinter.ttk.Treeview(root)
    all_book.grid(row=1,column=1)
    root.title('แก้ไขข้อมูลหนังสือ')
    root.resizable(0,0)

    c.execute('''SELECT * FROM book ORDER BY name''')
    books = c.fetchall()

    tk.Label(root, text = ('หนังสือทั้งหมด')).grid(row=0,column=1)
    all_book['show'] = 'headings'
    all_book['columns'] = ('id','type','name','status')

    all_book.heading('id', text = 'ID หนังสือ')
    all_book.heading('type', text = 'ประเภท')
    all_book.heading('name', text = 'ชื่อ')
    all_book.heading('status', text = 'สถานะ')

    all_book.column('id', width = 60)
    all_book.column('type', width = 80)
    all_book.column('name', width = 150)
    all_book.column('status', width = 80)

    for book in books:
        all_book.insert('','end', values=(book[0], book[1], book[2], book[3]))

    tk.Label(root, text='กรอกเลข ID หนังสือที่ต้องการแก้ไข').grid(row=2, column=1)
    tk.Label(root, text='แก้ไขประเภทหนังสือเป็น').grid(row=4, column=1)
    tk.Label(root, text='แก้ไขชื่อหนังสือเป็น').grid(row=6, column=1)
    idEdit = tk.Entry(root)
    idEdit.grid(row=3, column=1)
    choiceEntry = tk.StringVar(root, value='เลือกประเภทของหนังสือ')
    typebook = ttk.Combobox(root, textvariable=choiceEntry)
    typebook['values'] = ('หนังสือเรียน','หนังสือนิยาย','หนังสือการ์ตูน')
    typebook.grid(row=5, column=1)
    nameEdit = tk.Entry(root)
    nameEdit.grid(row=7, column=1)
    tk.Button(root, text='แก้ไข', bg='green', fg='white', command=edit_command).grid(row=8, column=1)

    root.mainloop()

def user_show():
    root = tk.Tk()
    root.option_add('*Font','Calibri 16')
    all_user = tkinter.ttk.Treeview(root)
    all_user.grid(row=1,column=1)
    root.title('ผู้ยืม')
    root.resizable(0,0)

    c.execute('''SELECT * FROM user ORDER BY name''')
    users = c.fetchall()
    if users:
        tk.Label(root, text = ('ผู้ยืมทั้งหมด')).grid(row=0,column=1)
        all_user['show'] = 'headings'
        all_user['columns'] = ('name','phone','borrow','date','return','price')

        all_user.heading('name', text = 'ชื่อ')
        all_user.heading('phone', text = 'เบอร์ติดต่อ')
        all_user.heading('borrow', text = 'ID หนังสือที่ยืม')
        all_user.heading('date', text = 'วันที่ยืม')
        all_user.heading('return', text = 'วันที่ต้องคืน')
        all_user.heading('price', text = 'ราคาค่ายืม')

        all_user.column('name', width = 150)
        all_user.column('phone', width = 120)
        all_user.column('borrow', width = 100)
        all_user.column('date', width = 100)
        all_user.column('return', width = 100)
        all_user.column('price', width = 80)

        for user in users:
            all_user.insert('','end', values=(user[1],user[2],user[3],user[4],user[5],user[6]))

def refresh():
    all_book.delete(*all_book.get_children())

    c.execute('''SELECT * FROM book ORDER BY name''')
    books = c.fetchall()
    for book in books:
        all_book.insert('','end', values=(book))

root = tk.Tk()
root.title('Bookshelf')
root.geometry('1280x720')
root.resizable(0,0)
root.option_add('*Font','Calibri 16')

canvas = Canvas(root, width=1280, height=720)
canvas.place(x=0 ,y=0, relheight=1, relwidth=1)
img1 = PhotoImage(file='C:\\Users\\Administrator\\Desktop\\Python\\books-642676_1280.png')
canvas.create_image(0, 0, anchor=NW, image=img1)
canvas.create_text(800, 75, text='หนังสือทั้งหมด', font=('TP Kubua',32))
canvas.create_text(225, 250, text='กรอกเลข ID หนังสือที่ต้องการลบ', font=('TP Kubua',20))
canvas.create_text(600, 567, text='ค้นหาหนังสือจากชื่อ', font=('TP Kubua',22))
canvas.create_text(583, 647, text='ค้นหาหนังสือจากประเภท', font=('TP Kubua',22))

tk.Button(root, text='เพิ่มหนังสือ', fg='black', bg='#ADDCF4', command=add_book).place(x=163,y=140) 
tk.Button(root, text='ลบหนังสือ', fg='white', bg='#FF7373',command=delete_book).place(x=163,y=310)
tk.Button(root, text='ค้นหา', fg='white', command=search_book_name_command, bg='#E89064').place(x=1000,y=540)
tk.Button(root, text='ค้นหา', fg='white', command=search_book_type_command, bg='#E89064').place(x=1000,y=620)
tk.Button(root, text='ยืมหนังสือ', bg='#FAEA84', command=borrow_book).place(x=82,y=390)
tk.Button(root, text='คืนหนังสือ', bg='#FAEA84', command=return_book).place(x=250,y=390)
tk.Button(root, text='แก้ไขข้อมูลหนังสือ', command=edit_book).place(x=250,y=650)
tk.Button(root, text='แสดงผู้ยืมทั้งหมด', command=user_show).place(x=132,y=490)
tk.Button(root, text='รีเฟรช ↻', font='Calibri 12', fg='white' , bg='#E89064', command=refresh).place(x=1080,y=60)
tk.Button(root, text='ออกจากโปรแกรม', fg='white', bg='#FF7373', command=exit).place(x=20,y=650)
nameEntry = tk.Entry(root)
nameEntry.place(x=720,y=550)
idEntry = tk.Entry(root)
idEntry.place(x=105,y=270)

choiceEntry = tk.StringVar(root, value='เลือกประเภทของหนังสือ')
typeEntry = ttk.Combobox(root, textvariable=choiceEntry)
typeEntry['values'] = ('หนังสือเรียน','หนังสือนิยาย','หนังสือการ์ตูน')
typeEntry.place(x=712,y=630)

all_book = tkinter.ttk.Treeview(root, height=20)
all_book.place(x=450,y=100)
c.execute('''SELECT * FROM book ORDER BY name''')
books = c.fetchall()

all_book['show'] = 'headings'
all_book['columns'] = ('id','type','name','status','borrow','phone','return')

all_book.heading('id', text = 'ID หนังสือ')
all_book.heading('type', text = 'ประเภท')
all_book.heading('name', text = 'ชื่อ')
all_book.heading('status', text = 'สถานะ')
all_book.heading('borrow', text = 'ผู้ยืม')
all_book.heading('phone', text = 'เบอร์ติดต่อผู้ยืม')
all_book.heading('return', text = 'วันที่ต้องคืน')

all_book.column('id', width = 60)
all_book.column('type', width = 80)
all_book.column('name', width = 150)
all_book.column('status', width = 80)
all_book.column('borrow', width = 150)
all_book.column('phone', width = 80)
all_book.column('return', width = 100)

for book in books:
    all_book.insert('','end', values=(book))

root.mainloop()