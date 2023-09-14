from tkinter import *
from sqlite3 import *
from tkinter.messagebox import *
from tkinter import ttk
from tkinter.filedialog import *
from configparser import *


mainWidth = 800
mainHeight = 540
infoWidth = 340
infoHeight = 160
redactorWidth = 496
redactorHeight = 360
loginWidth = 300
loginHeight = 180
searchWidth = 300
searchHeight = 100

fViewInfo = False
fViewSearch = False
info = "База данных 'Герои СССР'\n(c) Timokhin.V.M., Russia, 2023\n\ntimohinvaceslav4@gmail.com"
manual = "База данных Герои СССР\nПозволяет: добавлять / удалять / изменять информацию.\n" \
         "Клавиши программы:\nF1 - вызов справки по программе\nF2 - добавить в базу данных\n" \
         "F3 - удалить из базы данных\nF4 - изменить запись в базе данных\nF10 - меню программы"
helpBorder = "F1 - Помощь F2 - Добавить F3 - Удалить F4 - Изменить"
querydata = []
namelist = []
imageBuffer = None


cursor1 = connect("AmDB.db").cursor()
cursor1.execute("CREATE TABLE if not exists table1 (id INTEGER PRIMARY KEY, fio TEXT, item TEXT, image BLOB);")


def cmQuit(event=None):
    cursor1.connection.close()
    mainForm.quit()  # form1.destroy()


def selectAll():
    global querydata, namelist
    cursor1.execute("SELECT id, fio FROM table1")
    querydata = cursor1.fetchall()
    namelist = [querydata[i][1] for i in range(len(querydata))]


def search():
    global querydata, fViewSearch
    def submit(event=None):
        found = False
        FIO = inpFIO.get()
        for i in range(0, len(namelist)):
            if namelist[i] == FIO:
                found = True
                cur = memberlist.curselection()
                if len(cur) > 0:
                    memberlist.select_clear(cur)
                memberlist.select_set(i)
                listSelect()
                break
        if not found:
            showerror("Ошибка!", "Не найдено ни одной записи")
        global fViewSearch
        searchForm.destroy()
        fViewSearch = False

    def close(event=None):
        global fViewSearch
        searchForm.destroy()
        fViewSearch = False

    if not fViewSearch:
        searchForm = Toplevel()
        searchForm.focus_set()
        w = searchForm.winfo_screenwidth()
        h = searchForm.winfo_screenheight()
        x_help = (w/2) - (searchWidth/2)
        y_help = (h/2) - (searchHeight/2)
        searchForm.geometry('%dx%d+%d+%d' % (searchWidth, searchHeight, x_help, y_help - 40))
        searchForm.resizable(height=False, width=False)
        searchForm.title('Поиск')
        content = ttk.Label(searchForm, text="Введите ФИО:", padding=10)
        content.pack(anchor=NW)
        inpFIO = StringVar()
        inp = Entry(searchForm, textvariable=inpFIO, width=47)
        inp.place(x=6, y=30)
        inp.focus_set()
        searchForm.protocol('WM_DELETE_WINDOW', close)
        Button(searchForm, text='Поиск', command=submit).place(x=searchWidth-55, y=searchHeight-35)
        searchForm.bind('<Return>', submit)
        fViewSearch = True


def updateData(event=None):
    global querydata
    choosen = memberlist.curselection()
    if len(choosen) == 0:
        return
    exportData = querydata[choosen[0]]
    updateOrCreateRecord(list(exportData))


def insertData(event=None):
    updateOrCreateRecord()


def updateOrCreateRecord(data=None):
    global imageBuffer
    imageBuffer = None
    selected = memberlist.curselection()

    def confirm():
        name = entryFIO.get()
        text = textData.get(1.0,END)
        if data:
            query = "UPDATE table1 SET FIO = ?, item = ?, image = ? WHERE id=?;"
            par = (name, text, imageBuffer, data[0])
            cursor1.execute(query, par)
            cursor1.connection.commit()
            memberlist.delete(selected)
            memberlist.insert(selected, name)
            selectAll()
            memberlist.select_set(selected)
            listSelect()
        else:
            query = "INSERT INTO table1(FIO, item, image) VALUES (?,?,?)"
            par = (name, text, imageBuffer)
            cursor1.execute(query, par)
            cursor1.connection.commit()
            memberlist.insert(END, name)
            selectAll()
            memberlist.select_set(END)
            listSelect()

        RefreshData.destroy()


    def selectImage():
        global imageBuffer
        path = askopenfilename(title = "Выбор изображения", filetypes = [("png files","*.png")])
        if path:
            try:
                Img = PhotoImage(file=path, format='png')
                with open(path, "rb") as F:
                    imageBuffer = F.read()
                    F.close()
                Miniature = Img.subsample(8,8)
                Icon.create_image(0,0, image=Miniature, anchor=NW, tag="icon")
                Icon.image = Miniature
            except Exception:
                #прозволяет избежать ошибки из-за корявого имени файла
                showerror("Ошибка!", "Не удалось открыть выбранный файл. Проверьте имя файла")

    RefreshData = Toplevel()
    RefreshData.resizable(height=False, width=False)
    RefreshData.geometry()
    w = RefreshData.winfo_screenwidth()
    h = RefreshData.winfo_screenheight()
    x_ref = (w / 2) - (redactorWidth / 2)
    y_ref = (h / 2) - (redactorHeight / 2)
    RefreshData.geometry('%dx%d+%d+%d' % (redactorWidth, redactorHeight, x_ref, y_ref - 40))
    RefreshData.title('Редактор')
    RefreshData.grab_set()
    RefreshData.focus_set()
    nameSpace = Label(RefreshData, text='Фамилия Имя Отчество:')
    nameSpace.place(x=5, y=5)
    entryFIO = Entry(RefreshData, width=45)
    entryFIO.place(x=5, y=25)
    textSpace = Label(RefreshData, text='Текст статьи:')
    textSpace.place(x=5, y=50)
    textData = Text(RefreshData, width=60, height=10)
    textData.place(x=5, y=70)

    Icon = Canvas(RefreshData, height=100, width=100)

    if data:
        imageBlobQuery = f"SELECT image FROM table1 WHERE id={data[0]}"
        cursor1.execute(imageBlobQuery)
        dataImgText = cursor1.fetchall()
        imageBuffer = dataImgText[0][0]

        curMiniature = None if not imageBuffer else PhotoImage(data=imageBuffer, format='png').subsample(8,8)
        Icon.create_image(0,0,image=curMiniature, anchor=NW)
        Icon.image = curMiniature
        entryFIO.insert(0, data[1])
        textData.insert(END, selectedText.get(1.0, END))

    Icon.place(x=150, y=250)
    imageSpace = Label(RefreshData, text='Изображение:')
    imageSpace.place(x=5, y=250)
    Button(RefreshData, text='Сохранить', command=confirm).place(x=redactorWidth-76, y=redactorHeight-32)
    Button(RefreshData, text='Выбрать изображение', command=selectImage).place(x=5, y=redactorHeight-80)


def deleteData(event=None):
    global querydata
    choosen = memberlist.curselection()
    if len(choosen) == 0:
        return
    else:
        recordId = querydata[choosen[0]][0]
        delAccept = askyesno(title="Удаление записи", message="Вы действительно хотите удалить запись?")
        if delAccept:
            cursor1.execute(f"DELETE FROM table1 WHERE id={recordId};")
            cursor1.connection.commit()
            memberlist.delete(choosen)
            mainCanvas.delete("all")
            selectedText.place_forget()
            showinfo(title="Удаление записи", message="Запись успешно удалена!")
            selectAll()
        else:
            memberlist.select_set(choosen)


def listSelect(event=None):
    choosenIndex = memberlist.curselection()
    if len(choosenIndex) == 0:
        return
    choosenIndex = choosenIndex[0]
    imageBlobQuery = f"SELECT image, item FROM table1 WHERE id={querydata[choosenIndex][0]}"
    cursor1.execute(imageBlobQuery)
    dataImgText = cursor1.fetchall()
    image = dataImgText[0][0]
    selectedImage = None if not image else PhotoImage(data=image, format='png').subsample(2,2)
    mainCanvas.create_image(0, 0, image=selectedImage, anchor=NW)
    mainCanvas.image = selectedImage
    mainCanvas.place(x=200, y=10, width=380, height=400)
    selectedText.delete(1.0, END)
    selectedText.insert(END, dataImgText[0][1])
    selectedText.place(x=590, y=10, width=200, height=450)


def helpWin(event=None):
    global fViewInfo

    def close():
        global fViewInfo
        helpForm.destroy()
        fViewInfo = False

    if not fViewInfo:
        helpForm = Toplevel()
        helpForm.focus_set()
        w = helpForm.winfo_screenwidth()
        h = helpForm.winfo_screenheight()
        x_help = (w/2) - (infoWidth/2)
        y_help = (h/2) - (infoHeight/2)
        helpForm.geometry('%dx%d+%d+%d' % (infoWidth, infoHeight, x_help, y_help - 40))
        helpForm.resizable(height=False, width=False)
        helpForm.title('Справка')
        content = ttk.Label(helpForm, text=manual, padding=10)
        content.pack(anchor="nw")
        helpForm.protocol('WM_DELETE_WINDOW', close)
        Button(helpForm, text='Закрыть', command=close).place(x=infoWidth-70, y=infoHeight-40)
        fViewInfo = True


def appInfo():
    showinfo(title="О программе", message=info)


def logIn():
    config = ConfigParser()
    config.read("AmDB.ini")
    login = config['main']['user']
    password = config['main']['keyuser']

    def checkPass(event=None):
        if login == inpLogin.get() and password == inpPassword.get():
            authorisationForm.destroy()
        else:
            entryLogin.delete(0, END)
            entryPassword.delete(0, END)
            showerror("Ошибка!","Ошибка входа! Неверный логин или пароль!")

    authorisationForm = Tk()
    authorisationForm.resizable(width=False, height=False)
    x = (authorisationForm.winfo_screenwidth() / 2) - (loginWidth / 2)
    y = (authorisationForm.winfo_screenheight() / 2) - (loginHeight / 2)
    authorisationForm.geometry('%dx%d+%d+%d' % (loginWidth, loginHeight, x, y - 40))

    icon = PhotoImage(file = "AmDB_Icon.png", format='png')
    authorisationForm.iconphoto(False, icon)

    authorisationForm.title("Войти")
    inpLogin = StringVar()
    inpPassword = StringVar()
    getLogin = Label(authorisationForm, text='Введите логин:')
    getLogin.place(x=loginWidth/2-48, y=5)
    entryLogin = Entry(authorisationForm, textvariable=inpLogin)
    entryLogin.place(x=loginWidth/2-62,y=30)
    entryLogin.focus_set()

    getPass = Label(authorisationForm, text='Введите пароль:')
    getPass.place(x=loginWidth/2-50, y=60)

    entryPassword = Entry(authorisationForm, show='*', textvariable=inpPassword)
    entryPassword.place(x=loginWidth/2-62, y=85)
    Button(authorisationForm, text="Вход", width=10, command=checkPass).place(x=loginWidth/2-40,y=loginHeight - 40)
    authorisationForm.protocol('WM_DELETE_WINDOW', exit)
    authorisationForm.bind('<Return>', checkPass)
    authorisationForm.mainloop()

logIn()

mainForm = Tk()
mainForm.title("Герои СССР")
mainForm.resizable(height=False, width=False)

screen_width = mainForm.winfo_screenwidth()
screen_height = mainForm.winfo_screenheight()

x = (screen_width/2) - (mainWidth/2)
y = (screen_height/2) - (mainHeight/2)

mainForm.geometry('%dx%d+%d+%d' % (mainWidth, mainHeight, x, y - 40))

mainmenu = Menu()
mainForm.config(menu=mainmenu)

menu1 = Menu(tearoff=False)
menu1.add_command(label='Найти...', command=search)
menu1.add_separator()
menu1.add_command(label='Добавить', command=insertData, accelerator='F2')
menu1.add_command(label='Удалить', command=deleteData, accelerator='F3')
menu1.add_command(label='Изменить', command=updateData, accelerator='F4')
menu1.add_separator()
menu1.add_command(label='Выход', command=cmQuit, accelerator='Ctrl+X')
mainmenu.add_cascade(label='Фонд', menu=menu1)

menu2 = Menu(tearoff=False)
menu2.add_command(label='Содержание', command=helpWin)
menu2.add_separator()
menu2.add_command(label='О программе', command=appInfo)
mainmenu.add_cascade(label='Справка', menu=menu2)

InfoBorderCanvas = Canvas(bg='#68217a')
InfoBorderCanvas.create_text(160, 10, text=helpBorder, fill='white')
InfoBorderCanvas.place(x=-5, y=mainHeight - 19, width=mainWidth+10, height=22)

mainForm.bind('<Control-Key-x>', cmQuit)
mainForm.bind('<Key-F2>', insertData)
mainForm.bind('<Key-F3>', deleteData)
mainForm.bind('<Key-F4>', updateData)
mainForm.bind('<Key-F1>', helpWin)

mainCanvas = Canvas()
selectedText = Text()
selectedText.place(x=590, y=10, width=200, height=450)
selectedText.place_forget()
selectedText.bind("<Key>", lambda e: "break")

selectAll()
memberlist = Listbox(mainForm, width=30, height=28, listvariable=Variable(value=namelist), exportselection=0)
memberlist.place(x=5, y=10)
memberlist.bind('<<ListboxSelect>>', listSelect)
memberlist.bind('<FocusOut>', lambda e: memberlist.selection_clear(0, END))


mainForm.mainloop()