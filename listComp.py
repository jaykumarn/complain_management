from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import showinfo, showwarning
from db import DBConnect

class ListComp:
    def __init__(self):
        self._dbconnect = DBConnect()
        self._root = Toplevel()
        self._root.title('List of Complaints')
        self._root.geometry('900x500')
        
        btn_frame = Frame(self._root)
        btn_frame.pack(fill=X, padx=5, pady=5)
        Button(btn_frame, text='Refresh', command=self._load_data).pack(side=RIGHT)
        
        container = Frame(self._root)
        container.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self._tv = Treeview(container, columns=('Name', 'Gender', 'Comment', 'DateTime', 'Status'))
        self._tv.heading('#0', text='ID')
        self._tv.heading('Name', text='Name')
        self._tv.heading('Gender', text='Gender')
        self._tv.heading('Comment', text='Comment')
        self._tv.heading('DateTime', text='Date/Time')
        self._tv.heading('Status', text='Status')
        
        self._tv.column('#0', width=50)
        self._tv.column('Name', width=100)
        self._tv.column('Gender', width=60)
        self._tv.column('Comment', width=300)
        self._tv.column('DateTime', width=130)
        self._tv.column('Status', width=80)
        
        scrollbar = Scrollbar(container, orient=VERTICAL, command=self._tv.yview)
        self._tv.configure(yscrollcommand=scrollbar.set)
        
        self._tv.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self._tv.bind('<Double-1>', self._on_double_click)
        
        self._load_data()

    def _load_data(self):
        for item in self._tv.get_children():
            self._tv.delete(item)
        
        cursor = self._dbconnect.ListRequest()
        for row in cursor:
            created_at = row['CreatedAt'] if row['CreatedAt'] else ''
            status = row['Status'] if row['Status'] else 'Pending'
            self._tv.insert('', 'end', text=row['ID'],
                           values=(row['Name'], row['Gender'], row['Comment'], created_at, status))

    def _on_double_click(self, event):
        selected = self._tv.selection()
        if not selected:
            return
        item = selected[0]
        comp_id = self._tv.item(item, 'text')
        ResolutionForm(self._dbconnect, comp_id, self._load_data)


class ResolutionForm:
    def __init__(self, dbconnect, comp_id, refresh_callback):
        self._dbconnect = dbconnect
        self._comp_id = comp_id
        self._refresh_callback = refresh_callback
        
        complaint = self._dbconnect.GetComplaint(comp_id)
        if not complaint:
            showwarning('Error', 'Complaint not found')
            return
        
        self._win = Toplevel()
        self._win.title(f'Resolve Complaint #{comp_id}')
        self._win.geometry('550x550')
        
        canvas = Canvas(self._win)
        scrollbar = Scrollbar(self._win, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas)
        
        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Complaint Details
        info_frame = LabelFrame(scrollable_frame, text='Complaint Details')
        info_frame.pack(fill=X, padx=10, pady=5)
        
        Label(info_frame, text=f"Name: {complaint['Name']}").pack(anchor=W, padx=5)
        Label(info_frame, text=f"Gender: {complaint['Gender']}").pack(anchor=W, padx=5)
        Label(info_frame, text=f"Date: {complaint['CreatedAt'] or 'N/A'}").pack(anchor=W, padx=5)
        
        Label(info_frame, text="Comment:").pack(anchor=W, padx=5)
        comment_text = Text(info_frame, height=3, width=60, state=NORMAL)
        comment_text.insert('1.0', complaint['Comment'] or '')
        comment_text.config(state=DISABLED)
        comment_text.pack(padx=5, pady=5)
        
        # Response History
        history_frame = LabelFrame(scrollable_frame, text='Response History')
        history_frame.pack(fill=X, padx=10, pady=5)
        
        history = self._dbconnect.GetResponseHistory(comp_id)
        if history:
            for resp in history:
                resp_frame = Frame(history_frame, relief=GROOVE, borderwidth=1)
                resp_frame.pack(fill=X, padx=5, pady=3)
                
                header = Frame(resp_frame)
                header.pack(fill=X)
                Label(header, text=resp['CreatedAt'], font=('Arial', 9, 'bold')).pack(side=LEFT, padx=5)
                Label(header, text=f"[{resp['Status']}]", font=('Arial', 9)).pack(side=LEFT)
                
                resp_text = Text(resp_frame, height=2, width=55, state=NORMAL, wrap=WORD)
                resp_text.insert('1.0', resp['Response'] or '')
                resp_text.config(state=DISABLED, bg='#f0f0f0')
                resp_text.pack(padx=5, pady=2)
        else:
            Label(history_frame, text='No response history yet.', foreground='gray').pack(pady=10)
        
        # New Response Form
        resolve_frame = LabelFrame(scrollable_frame, text='Add Response')
        resolve_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        Label(resolve_frame, text='Status:').pack(anchor=W, padx=5, pady=2)
        self._status_var = StringVar()
        current_status = complaint['Status'] if complaint['Status'] else 'Pending'
        self._status_var.set(current_status)
        
        status_frame = Frame(resolve_frame)
        status_frame.pack(anchor=W, padx=5)
        Radiobutton(status_frame, text='Pending', value='Pending', variable=self._status_var).pack(side=LEFT)
        Radiobutton(status_frame, text='In Progress', value='In Progress', variable=self._status_var).pack(side=LEFT)
        Radiobutton(status_frame, text='Resolved', value='Resolved', variable=self._status_var).pack(side=LEFT)
        Radiobutton(status_frame, text='Rejected', value='Rejected', variable=self._status_var).pack(side=LEFT)
        
        Label(resolve_frame, text='Response:').pack(anchor=W, padx=5, pady=2)
        self._resolution_text = Text(resolve_frame, height=4, width=60)
        self._resolution_text.pack(padx=5, pady=5)
        
        btn_frame = Frame(scrollable_frame)
        btn_frame.pack(fill=X, padx=10, pady=10)
        Button(btn_frame, text='Submit Response', command=self._save).pack(side=RIGHT, padx=5)
        Button(btn_frame, text='Cancel', command=self._win.destroy).pack(side=RIGHT)

    def _save(self):
        resolution = self._resolution_text.get('1.0', 'end').strip()
        status = self._status_var.get()
        if not resolution:
            showwarning('Warning', 'Please enter a response')
            return
        self._dbconnect.Resolve(self._comp_id, resolution, status)
        showinfo('Success', 'Response saved successfully')
        self._win.destroy()
        self._refresh_callback()
