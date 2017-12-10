from tkinter import *
from Game import *
import os
from tkinter import messagebox


class Library:
    def __init__(self):
        self.fen = {}  # maps fens to variations, i.e., self.fen[(3, (1, 2, 4))] = "rnbak..."
        self.comment = {}  # maps comments to variations, i.e., self.comment[(3, (1, 2, 4))] = "rnbak..."
        self.movename = {}  # maps movename to variations
        self.filename = ""

    def add_move(self, movename, order, variation, fen, comment):
        self.fen[(order, variation)] = fen
        self.comment[(order, variation)] = comment
        self.movename[(order, variation)] = movename

    def write_to_file(self, movename, order, variation, fen, comment):
        dataline = str(order)+":"+tuple_2_str(variation)+":"+fen+":"+movename+":"+comment+"\n"
        with open('book/'+ self.filename, 'a') as infile:
            infile.write(dataline)

    def clear_library(self):
        self.fen = {}
        self.comment = {}
        self.movename = {}

class Board:
    def __init__(self):
        self.game = Game()
        self.library = Library()
        self.selected_library = ""
        self.layer_selected = {}  # associated with the selected variation in listboxes
        self.layer_selected[0] = ()
        self.layer_lastmove = [0, 0, 0, 0, 0, 0, 0, 0, 0] # the last move of the selected layer (before reach sub-layer)
        self.lbox = {}
        self.frame = {}
        self.label = {}
        self.lb_list = {}
        self.temp = {"newbranch_flag": False}  # for storing temporary variables
        self.image = {}
        self.code = {}
        self.piece_selected_flag = 0
        self.piece_selected_pos = (0, 0)
        self.gui = Tk()
        self.bt_record_state = IntVar(self.gui)
        self.cv = Canvas(self.gui, width=CV_WIDTH, height=CV_HEIGHT)
        self.cv.place(x = 0, y = 0)
        self.cv.bind("<Button-1>", self.L_Click)
        #Create_Menu(self.gui)
        self.Create_Menu()
        self.Create_Board()
        self.Create_ListBoxes()
        self.Create_Buttons()
        self.move_main = self.move_var1 = self.move_var2 = self.move_var3 = self.move_var4 = 0


    def Create_ListBoxes(self):
        frame_main = Frame(self.gui, bd = 2, relief = SUNKEN)
        frame_main.place(x = CV_WIDTH+5, y = 0)
        lbl_main = Label(frame_main, text="Main", width=7)
        lbl_main.pack(side=TOP, anchor=NW, padx=5, pady=5)
        self.lbmain = Listbox(frame_main, width = 15, height = 17)
        self.lbmain.pack()
        self.lbmain.bind("<<ListboxSelect>>", self.lbmain_click)

        for i in range(1, 5):
            self.frame[i] = Frame(self.gui, bd=2, relief=SUNKEN)
            self.frame[i].place(x=CV_WIDTH + i*100 + 5, y=0)
            self.label[i] = Label(self.frame[i], text="Layer " + str(i), width=7)
            self.label[i].pack(side=TOP, anchor=NW, padx=5, pady=5)
            self.lbox[i] = Listbox(self.frame[i], width=15, height=7)
            self.lbox[i].name = i
            self.lbox[i].pack()
            self.lbox[i].bind("<ButtonRelease-1>", self.lbox_click)

        for i in range(5, 9):
            self.frame[i] = Frame(self.gui, bd=2, relief=SUNKEN)
            self.frame[i].place(x=CV_WIDTH + (i-4) * 100 + 5, y=160)
            self.label[i] = Label(self.frame[i], text="Layer " + str(i), width=7)
            self.label[i].pack(side=TOP, anchor=NW, padx=5, pady=5)
            self.lbox[i] = Listbox(self.frame[i], width=15, height=7)
            self.lbox[i].name = i
            self.lbox[i].pack()
            self.lbox[i].bind("<ButtonRelease-1>", self.lbox_click)

        frame_lib = Frame(self.gui, bd=2, relief=SUNKEN)
        frame_lib.place(x = CV_WIDTH + 5, y = 360)
        lbl_lib = Label(frame_lib, text="Library", width=7)
        lbl_lib.pack(side=TOP, anchor=NW, padx=5, pady=5)
        self.lblib = Listbox(frame_lib, width = 35, height = 7)
        self.lblib.pack()
        library_files = os.listdir("book/")
        for file in reversed(library_files):
            self.lblib.insert(0, file)
        self.lblib.bind("<ButtonRelease-1>", self.lblib_click)


    def Create_Buttons(self):
        # BUTTONS
        self.first_button = Button(self.gui, text="|<", width=8, height=2)
        self.first_button.place(x = 2*CV_WIDTH/10, y = CV_HEIGHT + 30, anchor = CENTER)
        self.previous_button = Button(self.gui, text="<", width=8, height=2)
        self.previous_button.place(x = 4*CV_WIDTH/10, y = CV_HEIGHT + 30, anchor = CENTER)
        self.next_button = Button(self.gui, text=">", width=8, height=2)
        self.next_button.place(x = 6*CV_WIDTH/10, y = CV_HEIGHT + 30, anchor = CENTER)
        self.final_button = Button(self.gui, text=">|", width=8, height=2)
        self.final_button.place(x = 8*CV_WIDTH/10, y = CV_HEIGHT + 30, anchor = CENTER)
        self.bt_record = Checkbutton(self.gui, text="Record", variable = self.bt_record_state, command = self.bt_record_click)
        self.bt_record.place(x = CV_WIDTH, y = CV_HEIGHT + 30, anchor = CENTER)
        self.bt_delete = Button(self.gui, width=10, text="Delete Moves", command = self.bt_delete_click)
        self.bt_delete.place(x =CV_WIDTH + 450, y = 330, anchor = CENTER)
        self.bt_newbranch = Button(self.gui, width=10, text="New branch", command = self.bt_newbranch_click)
        self.bt_newbranch.place(x=CV_WIDTH + 150, y=330, anchor=CENTER)
        self.bt_refresh = Button(self.gui, width = 10, text="Refresh", command = self.refresh_display)
        self.bt_refresh.place(x=CV_WIDTH + 58, y=330, anchor=CENTER)

        self.gui.geometry('{}x{}'.format(970, 580)) # SET MAIN GUI WINDOW SIZE FIXED

    def Create_Menu(self):
        menubar = Menu(self.gui)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=donothing)
        filemenu.add_command(label="Open", command=donothing)
        filemenu.add_command(label="Save", command=donothing)
        filemenu.add_command(label="Save as...", command=donothing)
        filemenu.add_command(label="Close", command=donothing)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.gui.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Generate FEN", command=self.generate_fen_from_gui)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.gui.config(menu=menubar)


    def Create_Board(self):
        global background_image
        background_image = PhotoImage(file=r'img\board.png')
        self.cv.create_image(CV_WIDTH/2, CV_HEIGHT/2, image=background_image, tags="background")
        # vertical lines
        self.cv.create_line(OFFSET, OFFSET, OFFSET, OFFSET + DISTANCE * 9, fill="#fff", width=2)
        self.cv.create_line(OFFSET + DISTANCE * 8, OFFSET, OFFSET + DISTANCE * 8, OFFSET + DISTANCE * 9, fill="#fff", width=2)
        for x in range(OFFSET + DISTANCE, OFFSET + DISTANCE * 8, DISTANCE):
            self.cv.create_line(x, OFFSET, x, OFFSET + DISTANCE * 4, fill="#fff", width=2)
            self.cv.create_line(x, OFFSET + DISTANCE * 5, x, OFFSET + DISTANCE * 9, fill="#fff", width=2)
        # horizontal lines
        for y in range(OFFSET, CV_HEIGHT, DISTANCE):
            self.cv.create_line(OFFSET, y, CV_WIDTH - OFFSET, y, fill="#fff", width=2)
            # diagonal lines in the citadel region
            self.cv.create_line(OFFSET + 3 * DISTANCE, OFFSET, OFFSET + 5 * DISTANCE, OFFSET + 2 * DISTANCE,
                                fill="#fff", width=2)
            self.cv.create_line(OFFSET + 5 * DISTANCE, OFFSET, OFFSET + 3 * DISTANCE, OFFSET + 2 * DISTANCE,
                                fill="#fff", width=2)
            self.cv.create_line(OFFSET + 3 * DISTANCE, OFFSET + 7 * DISTANCE, OFFSET + 5 * DISTANCE,
                                OFFSET + 9 * DISTANCE, fill="#fff", width=2)
            self.cv.create_line(OFFSET + 5 * DISTANCE, OFFSET + 7 * DISTANCE, OFFSET + 3 * DISTANCE,
                                OFFSET + 9 * DISTANCE, fill="#fff", width=2)

    def __getitem__(self, index):
        return self.image[index], self.code[index]

    def __setitem__(self, index, value):
        self.image[index] = value
        self.code[index] = value

    def generate_fen_from_gui(self):
        fen_str = ""
        t = 0
        for y in range(1, 11):
            for x in range(1, 10):
                if x == 1 and y > 1:
                    fen_str = fen_str + "/"
                if self.code[(x, y)] is not None:
                    if t >= 1:
                        fen_str = fen_str + str(t)
                        t = 0
                    fen_str = fen_str + self.code[(x, y)]
                else:
                    t = t + 1
                    if x == 9 and t >= 1:
                        fen_str = fen_str + str(t)
                        t = 0
        return fen_str

    def gui_fen_parse(self, fen_str):
        x = 1
        y = 1
        for i in range(0, len(fen_str)):
            char = fen_str[i]
            if char == '/':
                x = 1
                y += 1
            elif char.isdigit():
                for j in range(0,int(char)):
                    self.image[(x, y)] = None
                    self.code[(x, y)] = None
                    x += 1
            else:
                if char.isupper():
                    color = RED
                else:
                    color = BLACK
                self.image[(x, y)] = PhotoImage(
                    file='img/' + char + str(color) + '.png')
                self.cv.create_image(get_gui_pos(x), get_gui_pos(y), image=self.image[(x, y)],
                                     tag=str(x) + "_" + str(y))
                self.code[(x, y)] = char
                x += 1

    def gui_move_piece(self, A, B): # move piece from A to B on GUI
        self.piece_selected_flag = 0
        self.cv.create_image(get_gui_pos(B[0]), get_gui_pos(B[1]), image=self.image[A],
                             tag=str(B[0]) + '_' + str(B[1]))
        self.cv.delete(str(A[0]) + "_" + str(A[1]))
        self.image[B] = self.image[A]
        self.code[B] = self.code[A]
        self.image[A] = None
        self.code[A] = None

    def L_Click(self, event):
        # Get the mouse click's position on board
        global path
        path = PhotoImage(file=r'img\select.png')
        x = round((event.x - OFFSET) / DISTANCE) + 1
        y = round((event.y - OFFSET) / DISTANCE) + 1
        if self.piece_selected_flag == 0:
            if self.code[(x, y)] is not None:
                self.cv.create_image(get_gui_pos(x), get_gui_pos(y), image=path, tag="select_img")
                self.piece_selected_flag = 1
                self.piece_selected_pos = (x, y)
            else:
                self.cv.delete('select_img')
                self.piece_selected_flag = 0
        else:
            if self.game.check_legal_move(self.piece_selected_pos, (x, y)):
                movename = self.game.get_movename(self.piece_selected_pos, (x, y))
                self.gui_move_piece(self.piece_selected_pos, (x, y))  # move piece image on GUI
                self.game.move_piece(self.piece_selected_pos, (x, y))  # move piece internally in engine
                self.piece_selected_pos = None
                if self.temp["newbranch_flag"] is True:
                    self.library.add_move(movename, self.temp["order"],
                                          self.temp["variation"], self.generate_fen_from_gui(), "")
                    self.library.write_to_file(movename, self.temp["order"],
                                            self.temp["variation"], self.generate_fen_from_gui(), "")
                    self.temp["newbranch_flag"] = False
                    self.lbmain.insert(END, movename)
                    self.lb_list[(0, self.lbmain.size() - 1)] = (self.temp["order"], self.temp["variation"])
                    self.lbox[self.temp["lbname"]].delete(END)
                    self.lbox[self.temp["lbname"]].insert(END, movename)
                    self.activate_last_main_move()


                if self.bt_record_state.get():
                    order = self.lb_list[(0, self.lbmain.size() - 1)][0]
                    variation = self.lb_list[(0, self.lbmain.size() - 1)][1]
                    if self.lbox[len(variation)+1].size() >= 1:
                        messagebox.showinfo("Next move is a branch. Create a new branch first.")
                    else:
                        self.library.add_move(movename, order+1,
                            variation, self.generate_fen_from_gui(), "")
                        self.library.write_to_file(movename, order+1,
                            variation, self.generate_fen_from_gui(), "")
                        self.lbmain.insert(END, movename)
                        self.lb_list[(0, self.lbmain.size() - 1)] = (order + 1, variation)
                        self.activate_last_main_move()
                self.cv.delete('select_img')
                self.piece_selected_flag = 0

    def update_listboxes(self):
        self.lbmain.insert(0, self.generate_fen_from_gui())

    def refresh_display(self):
        # Clear library
        self.library.clear_library()
        # Clear all listboxes
        self.lbmain.delete(0, END)
        for i in range(1, 9):
            self.lbox[i].delete(0, END)
            self.layer_lastmove[i] = 0
        # Import all moves from file to library and determine the last move of layer 0
        with open('book/' + self.library.filename, 'r') as infile:
            file = infile.read()
        moves = file.splitlines()
        for move in moves:
            self.library.add_move(get_move_name(move), get_move_order(move),
                                  get_move_variation(move), get_move_fen(move), get_move_comment(move))
        i = 0
        while self.library.fen.get((i, ())) is not None:
            i += 1
        self.layer_lastmove[0] = i - 1
        # Display moves
        self.display_main_moves()
        self.display_lbox1()

    def lblib_click(self, event):
        self.library.filename = self.lblib.get(self.lblib.curselection()[0])
        self.refresh_display()

    def lbox_click(self, event):
        i = event.widget.name
        for j in range(0, self.lbox[i].size()):  # make all previous selected entries white
            self.lbox[i].itemconfig(j, {'bg': 'white'})
        self.layer_selected[i] = self.lb_list[(i, self.lbox[i].curselection()[0])][1]
        self.lbox[i].itemconfig(self.lbox[i].curselection()[0], {'bg': 'green'})
        j = 1
        while i+j <= 4:
            self.lbox[i+j].delete(0, END)
            self.layer_lastmove[i+j] = 0
            j += 1
        # Detect the last move of the selected variation before going to a deeper layer
        stop = 1
        j = 1
        while stop == 1:
            if self.library.fen.get((self.layer_lastmove[i-1] + j, self.layer_selected[i])) is None:
                stop = 0
                self.layer_lastmove[i] = self.layer_lastmove[i-1] + j - 1
            else:
                j += 1
        # display variations in the next layer
        for j in range(1,10):
            order = self.layer_lastmove[i] + 1
            variation = self.layer_selected[i] + (j,)
            if self.library.fen.get((order, variation)) is not None:
                self.lbox[i+1].insert(END, str(order) + "(" + tuple_2_str(variation) + "). "
                    + self.library.movename[(order, variation)])
                self.lb_list[(i + 1, self.lbox[i + 1].size() - 1)] = (self.layer_lastmove[i] + 1, self.layer_selected[i] + (j,))
                j += 1
        self.display_main_moves()

    def lbmain_click(self, event):
        if len(self.lbmain.curselection())!=0:
            self.gui_fen_parse(self.library.fen[self.lb_list[(0, self.lbmain.curselection()[0])]])
            self.game.fen_parse(self.library.fen[self.lb_list[(0, self.lbmain.curselection()[0])]])
            # The reason for the if statement above is that when the first command in
            # display_main_moves() executes, it accidentally triggers the main listbox event
            # At this moment lbmain.curselection is an empty tuple.

    def display_main_moves(self):
        self.lbmain.delete(0,END)
        for i in range(0, self.layer_lastmove[0] + 1):
            self.lbmain.insert(END, str(i)+". "+self.library.movename[(i, ())])
            self.lb_list[(0, self.lbmain.size() - 1)] = (i, ())
        for layer in range(1, 5):
            if self.layer_lastmove[layer]!=0:
                for i in range(self.layer_lastmove[layer-1] + 1, self.layer_lastmove[layer] + 1):
                    self.lbmain.insert(END, str(i)+"("+tuple_2_str(self.layer_selected[layer])
                       + "). " + self.library.movename[(i, self.layer_selected[layer])])
                    self.lb_list[(0, self.lbmain.size() - 1)] = (i, self.layer_selected[layer])
                self.lbmain.itemconfig(self.layer_lastmove[layer - 1] + 1, {'bg': 'green'})
        self.activate_last_main_move()

    def display_lbox1(self):
        # Display variations for Layer 1 listbox
        self.lbox[1].delete(0, END)
        stop_j = 1
        j = 1

        for j in range(1,10):
            order = self.layer_lastmove[0]+1
            variation = (j,)
            if self.library.fen.get((order, variation)) is not None:
                self.lbox[1].insert(END, str(order) + "(" + tuple_2_str(variation) + "). "
                    + self.library.movename[(order, variation)])
                self.lb_list[(1, self.lbox[1].size() - 1)] = (order,variation)


    def bt_delete_click(self):
        order = self.lb_list[(0, self.lbmain.curselection()[0])][0]
        variation = self.lb_list[(0, self.lbmain.curselection()[0])][1]
        layer = len(variation)
        if self.lbox[layer+1].size()>0:
            result = messagebox.askquestion("Warning", "There are sub-branches after this move. "
                "Deleting this move implies deleting all subsequent branches. Do you wish to proceed?", icon='warning')
            if result == 'yes':
                bad_words = ':'+tuple_2_str(variation)
                with open("book/"+self.library.filename) as badfile, open('out.txt', 'w') as cleanfile:
                    for line in badfile:
                        if bad_words not in line:
                            cleanfile.write(line)
                        elif get_move_order(line) < order:
                            cleanfile.write(line)
                with open('out.txt') as f:
                    with open("book/"+self.library.filename, "w") as f1:
                        for line in f:
                                f1.write(line)

        else:
            result = messagebox.askquestion("Warning", "Deleting this move implies "
                            "deleting all subsequent moves. Do you wish to proceed?",
                                            icon='warning')
            if result == 'yes':
                print("yes")

    def activate_last_main_move(self):
        self.lbmain.selection_clear(0,END)
        self.lbmain.selection_set(END)
        self.lbmain.activate(END)
        self.gui_fen_parse(self.library.fen[self.lb_list[(0, self.lbmain.size() - 1)]])
        self.game.fen_parse(self.library.fen[self.lb_list[(0, self.lbmain.size() - 1)]])

    def bt_newbranch_click(self):
        if self.lbmain.curselection() == self.lbmain.size():
            layer = len(self.lb_list[(0, self.lbmain.size() - 1)][1])
            j = 1
            while self.library.fen.get((self.layer_lastmove[layer]+1,
                                        self.layer_selected[layer] + (j,))) is not None:
                j += 1
            self.lbox[layer + 1].insert(END, "New branch")
            self.temp["variation"] = self.lb_list[(0, self.lbmain.size() - 1)][1] + (j,)
            self.temp["order"] = self.lb_list[(0, self.lbmain.size() - 1)][0] + 1
            self.temp["lbname"] = layer + 1
            self.temp["newbranch_flag"] = True
            self.lb_list[(layer + 1, self.lbox[layer + 1].size() - 1)] = (self.temp["order"], self.temp["variation"])
            messagebox.showinfo("Notice", "Please make the first move of this new branch on the board")
        else:
            messagebox.showinfo("Notice", "The new branch should be created at the last move"
                                          " in the Main window. Please select the last move and try again.")


    def bt_record_click(self):
        a = 5


def get_move_order(dataline):
    order = int(dataline.split(":")[0])
    return order


def get_move_variation(dataline):
    variation_str = dataline.split(":")[1]
    if variation_str == "":
        variation = ()
    else:
        variation = tuple(map(int, variation_str.split('.')))
    return variation


def get_move_fen(dataline):
    fen = dataline.split(":")[2]
    return fen


def get_move_name(dataline):
    name = dataline.split(":")[3]
    return name


def get_move_comment(dataline):
    cm = dataline.split(":")[4]
    return cm


def tuple_2_str(tup): #
    tup_str = ""
    for i in range(0, len(tup)):
        tup_str = tup_str + str(tup[i])+"."
    tup_str = tup_str[:-1]  # remove the last dot
    return tup_str


def get_gui_pos(pos):
    gui_pos = OFFSET + (pos-1)*DISTANCE
    return gui_pos


def donothing():
   filewin = Toplevel()
   button = Button(filewin, text="Do nothing button")
   button.pack()

def about():
    messagebox.showinfo("Chinese Chess Python GUI v1.0", "Written by Kha Vo \n voanhkha@yahoo.com \n November 2017")


