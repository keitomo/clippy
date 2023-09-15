import tkinter as tk
from tkinter import ttk
'''
ModifiedEntryクラス
元のEntryクラスと同様にふるまう
中のテキストが更新されると、"<<TextModified>>"イベントが発生する。
'''
class ModifiedEntry(ttk.Entry):
    def __init__(self, *args, **kwargs):
        # Entry自体の初期化は元のクラスと同様。
        ttk.Entry.__init__(self , *args, **kwargs)
        self.sv = kwargs["textvariable"] if "textvariable" in kwargs.keys()  else tk.StringVar()
        # traceメソッドでStringVarの中身を監視。変更があったらvar_changedをコールバック
        self.sv.trace('w',self.var_changed)
        # EntryとStringVarを紐づけ。
        self.configure(textvariable = self.sv)

    # argsにはtrace発生元のVarの_nameが入っている
    # argsのnameと内包StringVarの_nameが一致したらイベントを発生させる。
    def var_changed(self, *args):
        if args[0] == self.sv._name:
            s = self.sv.get()
            self.event_generate("<<TextModified>>")