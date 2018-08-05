import sqlite3
import tkinter as tk
from tkinter import ttk
# Sanitize input at some point because xkcd comic num 327
# View doesn't correctly refresh after deletion. Still deletes from table


def setup_table(conn):
    """
    (Connection) -> Cursor
    Main database management
    """
    table_name = "StudentInfo"
    table_columns = [["Student_ID", "INTEGER"],
                     ["Student_Name", "TEXT"],
                     ["Hours_bought", "INTEGER"],
                     ["First_class", "DATE"],  # YYYY-MM-DD
                     ["Grade", "INTEGER"],
                     ["Subject1", "TEXT"],
                     ["Subject2", "TEXT"],
                     ["Subject3", "TEXT"],
                     ["Days_of_attendance", "DATE"],
                     ["Hours_of_attendance", "TIME"],  # HH:MM:SS.SSS
                     ["Comments", "TEXT"]]

    # delete_table(conn, table_name)
    create_table(conn, table_name, table_columns)
    return conn.cursor(), table_name


def create_connection(db_name):
    """
    (str) -> Connection
    Attempt to connect to a database file, return connection if successful.
    """
    try:
        conn = sqlite3.connect(db_name)
        print("Connection Successful")
        return conn
    except Exception as e:
        print(e)


def create_table(conn, table_name, table_columns):
    """
    (Connection, str, List[List[str]]) -> None
    Make table in db file with name table_name and with columns contained in
    nested lists that contain column name and column data format. Return True
    if operation completed successfully.
    """
    try:
        # Get cursor
        c = conn.cursor()
        print("Cursor connected")
        c.execute("CREATE TABLE {n} ({c} {f} PRIMARY KEY)"
                  .format(n=table_name, c=table_columns[0][0],
                          f=table_columns[0][1]))
        print("Table Created")
        conn.commit()
        for i in range(len(table_columns) - 1):
            c.execute("ALTER TABLE {n} ADD COLUMN '{cn}' {ct}"
                      .format(n=table_name, cn=table_columns[i+1][0],
                              ct=table_columns[i+1][1]))
        print("Columns Added")
        conn.commit()
    except Exception as e:
        print(e)


def commit_and_close_connection(conn):
    """
    (connection) -> None
    Close connection to db
    """
    try:
        conn.commit()
        conn.close()
        print("Connection Commited and Closed")
    except Exception as e:
        print("Could not close connection")
        print(e)


def add_row(conn, table_name, info_list, columns, frame, add_win):
    """
    (Connection, str, List[str], List[str], Frame, Window) -> None
    Add new row to database. Return true if operation successful.
    """
    c = conn.cursor()
    id = get_new_id(conn, table_name)
    data = str(tuple([id] + info_list))
    # Assume all data is in correct order and amount from input validation
    try:
        c.execute("INSERT INTO {tn} VALUES {d}".format(tn=table_name,
                                                       d=data))
        print("Successful Addition to Table")
        conn.commit()
        fill_data(conn, table_name, columns, frame)
        add_win.destroy()
    except Exception as e:
        print(e)


def modify_row(conn, table_name, id, data, columns, frame, mod_win):
    """
    (Connection, str, str, List[List[str]], List[str], Frame, Window) -> None
    new_data is in format of {column name: new data for column}. This function
    updates value of the column at 'name' row. Return true if successful.
    """
    c = conn.cursor()
    # If there are any modifications to be made
    try:
        for i in range(len(data)):
            c.execute("UPDATE {tn} SET {c}=('{d}') WHERE Student_ID={id}"
                      .format(tn=table_name, c=data[i][0], d=data[i][1],
                              id=id))
        print("Modified 1 Element Successfully")
        conn.commit()
        fill_data(conn, table_name, columns, frame)
        mod_win.destroy()
    except Exception as e:
        print(e)


def delete_row(conn, table_name, id, columns, frame, del_win):
    """
    (Connection, str, str, List[str], Frame, window) -> bool
    Delete row from database, return True if successful.
    """
    c = conn.cursor()
    try:
        c.execute('DELETE FROM {tn} WHERE Student_ID="{i}"'
                  .format(tn=table_name, i=id))
        print("Successful Row Deletion")
        conn.commit()
        fill_data(conn, table_name, columns, frame)
        del_win.destroy()
    except Exception as e:
        print(e)


def get_new_id(conn, table_name):
    """
    (Connectionm, str) -> str
    Return a new ID for the table by adding 1 to current max id
    """
    try:
        id_vals = get_all_ids(conn, table_name)
        id_vals = [int(id) for id in id_vals]
        print(id_vals)
        max_id = max(id_vals) if len(id_vals) > 0 else 0
        new_id = max_id + 1
        print(new_id)
        return str(new_id)
    except Exception as e:
        print("Could not connect to database to get new id")
        print(e)


def get_row_from_id(conn, table_name, id):
    """
    (Connection, str, str) -> List[str]
    Get all data from a certain row from id
    """
    c = conn.cursor()
    print(c)
    c.execute("SELECT * FROM {tn} WHERE Student_ID={id}"
              .format(tn=table_name, id=id))
    row_info = [str(val) for val in c.fetchall()[0]]
    print(row_info)
    return row_info


def get_all_ids(conn, table_name):
    """
    (Connection, str) -> List[str]
    Return list of all id's in the database
    """
    try:
        c = conn.cursor()
        c.execute("SELECT Student_ID FROM {tn}".format(tn=table_name))
        ids = c.fetchall()
        id_vals = [str(tup[0]) for tup in ids]
        print(id_vals)
        return id_vals
    except Exception as e:
        print("Something went wrong with getting to db")
        print(e)


def get_column_names(conn, table_name):
    """
    (connection, str) -> List[str]
    Get all columns in the database
    """
    c = conn.cursor()
    c.execute("PRAGMA TABLE_INFO({tn})".format(tn=table_name))
    columns = [tup[1] for tup in c.fetchall()]
    return columns


def fill_data(conn, table_name, columns, frame):
    """
    (Connection, str, List[str], Frame) -> None
    Fill frame with database info
    """
    font = ("Calibri Light", 8)
    ids = get_all_ids(conn, table_name)
    rows = []
    print(ids)
    # frame.grid_forget()
    for id in ids:
        rows.append(get_row_from_id(conn, table_name, id))
    print(rows)
    for i in range(len(rows)):  # rows
        for j in range(len(rows[i])):  # Columns
            data = tk.Label(master=frame, text=rows[i][j], font=font)
            data.grid(row=i+1, column=j+1, padx=4, pady=2)


def add_entry_window(conn, table_name, columns, frame):
    """
    (connection, str, List[str], frame) -> None
    Window to take input for addition to db
    """
    add_win = tk.Tk()
    add_win.title("Update Record")
    width = 350
    height = 320

    # Center window on screen
    x = (add_win.winfo_screenwidth() // 2) - (width // 2)
    y = (add_win.winfo_screenheight() // 2) - (height // 2)
    add_win.geometry("{w}x{h}+{x}+{y}".format(w=width, h=height, x=x, y=y))
    add_win.resizable(height=False, width=False)

    font = ("Calibri Light", 12)
    entries = []
    for i in range(1, len(columns)):
        label = tk.Label(master=add_win, text=columns[i], font=font)
        entry = tk.Entry(master=add_win, font=font)
        entries.append(entry)
        label.grid(row=i, column=0)
        entry.grid(row=i, column=1)

    submit = tk.Button(master=add_win, text="Submit", font=font,
                       command=lambda:
                       add_entry_button(conn, table_name, entries, columns,
                                        frame, add_win))
    cancel = tk.Button(master=add_win, text="Cancel", font=font,
                       command=lambda: close_window(add_win))
    submit.grid(row=len(columns) + 1, column=0)
    cancel.grid(row=len(columns) + 1, column=1)
    add_win.attributes('-topmost', 'true')
    add_win.mainloop()


def add_entry_button(conn, table_name, entries, columns, frame, add_win):
    """
    (Connection, str, List[Entry], List[str], Frame, window) -> None
    Collect data for addition and format appropriately
    """
    info = []
    for entry in entries:
        info.append(str(entry.get()))
    print(info)
    add_row(conn, table_name, info, columns, frame, add_win)


def close_window(window):
    """
    (window) -> None
    Destroy window (button function)
    """
    window.destroy()


def ask_for_id_mod(conn, table_name, columns, frame):
    """
    (Connection, str, List[str], Frame) -> None
    Window to get id for modification
    """
    conf_win = tk.Tk()
    conf_win.title("Update Record")
    width = 275
    height = 300
    font = ("Calibri Light", 12)

    # Center window on screen
    x = (conf_win.winfo_screenwidth() // 2) - (width // 2)
    y = (conf_win.winfo_screenheight() // 2) - (height // 2)
    conf_win.geometry("{w}x{h}+{x}+{y}".format(w=width, h=height, x=x, y=y))
    conf_win.resizable(height=False, width=False)
    prompt = tk.Label(master=conf_win, text="Select ID to Modify", font=font)
    prompt.grid(row=0, column=1)

    ids = get_all_ids(conn, table_name)
    print(ids)
    listbox = tk.Listbox(master=conf_win, font=font, selectmode=tk.SINGLE)
    listbox.grid(row=1, column=1)
    for id in ids:
        listbox.insert(tk.END, str(id))

    select = tk.Button(master=conf_win, text="Select", font=font,
                       command=lambda: mod_window(conn, table_name, listbox,
                                                  columns, frame, conf_win))
    cancel = tk.Button(master=conf_win, text="Cancel", font=font,
                       command=lambda: close_window(conf_win))
    select.grid(row=2, column=0)
    cancel.grid(row=2, column=2)
    conf_win.attributes('-topmost', 'true')
    conf_win.mainloop()


def mod_window(conn, table_name, listbox, columns, frame, window):
    """
    (Connection, str, Listbox, List[str], Frame, Window) -> None
    Window to collect information to modify an entry
    """
    mod_win = tk.Tk()
    mod_win.title("Update Record")
    width = 320
    height = 350
    font = ("Calibri Light", 12)

    # Center window on screen
    x = (mod_win.winfo_screenwidth() // 2) - (width // 2)
    y = (mod_win.winfo_screenheight() // 2) - (height // 2)
    mod_win.geometry("{w}x{h}+{x}+{y}".format(w=width, h=height, x=x, y=y))
    mod_win.resizable(height=False, width=False)

    id = listbox.get(listbox.curselection())
    window.destroy()
    row = get_row_from_id(conn, table_name, id)
    entries = []
    for i in range(1, len(columns)):
        label = tk.Label(master=mod_win, text=columns[i], font=font)
        entry = tk.Entry(master=mod_win, font=font)
        entry.insert(tk.END, row[i])
        entries.append(entry)
        label.grid(row=i, column=0)
        entry.grid(row=i, column=1)

    submit = tk.Button(master=mod_win, text="Submit", font=font,
                       command=lambda:
                       mod_entry_button(conn, table_name, id, entries, columns,
                                        frame, mod_win))
    cancel = tk.Button(master=mod_win, text="Cancel", font=font,
                       command=lambda: close_window(mod_win))
    submit.grid(row=len(columns) + 1, column=0)
    cancel.grid(row=len(columns) + 1, column=1)

    mod_win.attributes('-topmost', 'true')
    mod_win.mainloop()


def mod_entry_button(conn, table_name, id, entries, columns, frame, mod_win):
    """
    (Connection, str, str, List[Entry], List[str], Frame, Window) -> None
    On submission of modification form, format data appropriately and call mod
    function
    """
    data = []
    currow = get_row_from_id(conn, table_name, id)
    for i in range(len(entries)):
        if entries[i] != currow[i+1]:
            data.append([str(columns[i+1]), str(entries[i].get())])

    modify_row(conn, table_name, id, data, columns, frame, mod_win)


def ask_for_id_del(conn, table_name, columns, frame):
    """
    (Connection, str, List[str], Frame) -> None
    Get id for deletion
    """
    conf_win = tk.Tk()
    conf_win.title("Update Record")
    width = 275
    height = 300
    font = ("Calibri Light", 12)

    # Center window on screen
    x = (conf_win.winfo_screenwidth() // 2) - (width // 2)
    y = (conf_win.winfo_screenheight() // 2) - (height // 2)
    conf_win.geometry("{w}x{h}+{x}+{y}".format(w=width, h=height, x=x, y=y))
    conf_win.resizable(height=False, width=False)
    prompt = tk.Label(master=conf_win, text="Select ID to Delete", font=font)
    prompt.grid(row=0, column=1)

    ids = get_all_ids(conn, table_name)
    listbox = tk.Listbox(master=conf_win, font=font, selectmode=tk.SINGLE)
    listbox.grid(row=1, column=1)
    for id in ids:
        listbox.insert(tk.END, str(id))

    select = tk.Button(master=conf_win, text="Select", font=font,
                       command=lambda: del_call(conn, table_name, listbox,
                                                columns, frame, conf_win))
    cancel = tk.Button(master=conf_win, text="Cancel", font=font,
                       command=lambda: close_window(conf_win))
    select.grid(row=2, column=0)
    cancel.grid(row=2, column=2)
    conf_win.attributes('-topmost', 'true')
    conf_win.mainloop()


def del_call(conn, table_name, listbox, columns, frame, window):
    """
    (Connection, str, Listbox, List[str], Frame, Window) -> None
    Determine id of row to be deleted, call delete function
    """
    id = listbox.get(listbox.curselection())
    delete_row(conn, table_name, id, columns, frame, window)


if __name__ == "__main__":
    # Define initials of database
    db = "students.db"
    conn = create_connection(db)
    c, table_name = setup_table(conn)
    print(conn)
    columns = get_column_names(conn, table_name)
    print(columns)
    all_ids = get_all_ids(conn, table_name)
    print(all_ids)

    # Define main window properties
    window = tk.Tk()
    window.title("Student Database GUI")
    width = 1280
    height = 720

    # Center window on screen
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry("{w}x{h}+{x}+{y}".format(w=width, h=height, x=x, y=y))
    window.resizable(height=False, width=False)

    # Define organization frames
    top_frame = tk.Frame(window, width=1280, height=70)
    top_frame.grid(row=0, column=0)
    db_frame = tk.Frame(window, width=1280, height=650, padx=50, pady=5)
    db_frame.grid(row=1, column=0)

    # Fonts
    fl20 = ("Calibri Light", 20)
    fl12 = ("Calibri Light", 12)
    fb20 = ("Calibri Light", 20, "bold")
    fb10 = ("Calibri Light", 13, "bold")
    fl10 = ("Calibri Light", 12)

    # Table title
    table_title_label = tk.Label(master=top_frame,
                                 text="Table Name: '" + table_name + "'",
                                 font=fb20)
    table_title_label.grid(row=0, column=6)

    # Define Buttons
    add_button = tk.Button(master=top_frame, text="Add a Record",
                           default="active", font=fl12, height=1, width=15)
    add_button.grid(row=1, column=3, pady=10, padx=25)
    add_button.config(command=lambda:
                      add_entry_window(conn, table_name, columns, db_frame))

    remove_button = tk.Button(master=top_frame, text="Remove a Record",
                              font=fl12, height=1, width=15)
    remove_button.grid(row=1, column=5, pady=10, padx=25)
    remove_button.config(command=lambda:
                         ask_for_id_del(conn, table_name, columns, db_frame))

    modify_button = tk.Button(master=top_frame, text="Modify Record",
                              font=fl12, height=1, width=15)
    modify_button.grid(row=1, column=7, pady=10, padx=25)
    modify_button.config(command=lambda:
                         ask_for_id_mod(conn, table_name, columns, db_frame))

    # Show initial Contents
    display_columns = [column.replace("_", " ") for column in columns]
    for i in range(len(display_columns)):
        head = tk.Label(master=db_frame, text=display_columns[i],
                        font=fb10)
        head.grid(row=0, column=i+1, padx=2, pady=2)
    fill_data(conn, table_name, columns, db_frame)

    window.mainloop()
