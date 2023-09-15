"""
The MIT License
Copyright (c) 2022 keitomo

以下に定める条件に従い、本ソフトウェアおよび関連文書のファイル（以下「ソフトウェア」）の複製を取得するすべての人に対し、
ソフトウェアを無制限に扱うことを無償で許可します。
これには、ソフトウェアの複製を使用、複写、変更、結合、掲載、頒布、サブライセンス、および/または販売する権利、
およびソフトウェアを提供する相手に同じことを許可する権利も無制限に含まれます。

上記の著作権表示および本許諾表示を、ソフトウェアのすべての複製または重要な部分に記載するものとします。

ソフトウェアは「現状のまま」で、明示であるか暗黙であるかを問わず、何らの保証もなく提供されます。
ここでいう保証とは、商品性、特定の目的への適合性、および権利非侵害についての保証も含みますが、それに限定されるものではありません。
作者または著作権者は、契約行為、不法行為、またはそれ以外であろうと、ソフトウェアに起因または関連し、
あるいはソフトウェアの使用またはその他の扱いによって生じる一切の請求、損害、その他の義務について何らの責任も負わないものとします。
"""
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
import ffmpeg
import re,os,glob
from PIL import Image, ImageDraw, ImageFont
import shutil
from functools import partial
from modified import *
import threading

clips=[]
os.environ["Path"]="./Library/"
renderFlag=False
threads=[]

class Clip:
    """Clip class
        動画とテキストを保持するクラス
    """
    def __init__(self,video=None,text="None"):
        """Clipの初期化

        Args:
            video (str, optional): 動画のパス. Defaults to None.
            text (str): クリップのテキスト. Defaults to "None".
        """
        self._video=video
        self._text=text

    def __repr__(self) -> str:
        return self._video

    def changeText(self,text):
        """Clipのテキスト変更

        Args:
            text (str): 変更後のテキスト
        """
        self._text=text

    def changevideo(self,video):
        """Clipの動画のパスの変更

        Args:
            video (str): 変更後の動画のパス
        """
        self._video=video

    def text(self):
        """Clipのテキストを返す

        Returns:
            str: Clipのテキスト
        """
        return self._text

    def video(self):
        """Clipの動画のパスを返す

        Returns:
            str: Clipの動画のパス
        """
        return self._video

class Clippy:

    @staticmethod
    def concatVideo(videoList,outFile="output"):
        """videoList内の動画をつなぎ合わせて,outFileに出力

        Args:
            videoList (list): つなぎ合わせる動画のリスト
            outFile (str, optional): 動画の出力先のパス. Defaults to "output".
        """
        if re.findall('mp4$', outFile)==[]:
            outFile=outFile+".mp4"
        with open("tmp.txt","w", encoding='utf-8') as f:
            lines = [f"file '{line}'" for line in videoList]
            f.write("\n".join(lines))
        ffmpeg.input("tmp.txt", f="concat", safe=0).output(outFile, vcodec="h264",acodec="aac",pix_fmt='yuv420p').run(overwrite_output=True)
        os.remove("tmp.txt")

    @staticmethod
    def createVideo(img,audio=None,outFile="hoge",time=3):
        """imgとaudioを結合させてtime秒の動画をoutFileに出力

        Args:
            img (str): 結合する画像のパス
            audio (str, optional): 結合する音声のパス. Defaults to None.
            outFile (str, optional): 動画の出力先のパス. Defaults to "hoge".
            time (int, optional): 作成する動画の時間. Defaults to 3.

        Returns:
            str: 作成した動画のパス
        """
        if re.findall('mp4$', outFile)==[]:
            outFile=outFile+".mp4"
        instVideo=ffmpeg.input(filename=img,loop=1,t=time,r=30)
        if audio!=None and audio!="":
            instAudio=ffmpeg.input(audio,t=time)
            stream = ffmpeg.output(instVideo,instAudio,outFile,vcodec="h264",acodec="aac",pix_fmt='yuv420p',ar=48000)
        else:
            stream = ffmpeg.output(instVideo,outFile,vcodec="h264",acodec="aac",pix_fmt='yuv420p',ar=48000)
        ffmpeg.run(stream,overwrite_output=True)
        return outFile

    @staticmethod
    def reEncode(file):
        """動画の再エンコード

        Args:
            file (str): 再エンコードする動画のパス
        """
        shutil.move("./VideoTmp/"+file,"./VideoTmp/"+"old_"+file)
        ffmpeg.input("./VideoTmp/"+"old_"+file).output("./VideoTmp/"+file,vcodec="h264",acodec="aac",pix_fmt='yuv420p',ar=48000).run()

    @staticmethod
    def createImg(img=None,text="Sample",font="./Library/LightNovelPOPv2.otf",fontSize=100,outFile="test.png"):
        """imgにtextを合成した画像を作成し,outFileに出力

        Args:
            img (str, optional): 合成する画像. Defaults to None.
            text (str, optional): 合成するテキスト. Defaults to "Sample".
            font (str, optional): テキストのフォント. Defaults to "./Library/LightNovelPOPv2.otf".
            fontSize (int, optional): フォントのサイズ. Defaults to 100.
            outFile (str, optional): 画像の出力先. Defaults to "test.png".

        Returns:
            str: 作成した画像のパス
        """
        if re.findall('png$', outFile)==[]:
            outFile=outFile+".png"
        mainIm=Image.new("RGB",(1920,1080),"blue")
        im=Image.new("RGB",(1920,1080),"blue")
        if img!=None and img!="":
            im=Image.open(img)
        imgSize=im.size
        mainIm.paste(im,(int(960-imgSize[0]/2),int(540-imgSize[1]/2)))
        draw=ImageDraw.Draw(mainIm)
        font_=ImageFont.truetype(font,fontSize)
        textSize=font_.getsize(text)
        draw.text((int(960-textSize[0]/2), int(540-textSize[1]/2)), text, font=font_,fill='white',stroke_width=4,stroke_fill='black')
        mainIm.save(outFile)
        return outFile

    @staticmethod
    def render(bg,se,outFile):
        """動画をレンダリングする

        Args:
            bg (_type_): 背景画像のパス
            se (_type_): 効果音のパス
            outFile(str): 動画の出力先のパス
        """
        videoList=[]
        if se=="":
            se="./Library/silent.mp3"
        for i,c in enumerate(clips):
            img=Clippy.createImg(img=bg,text=c.text(),outFile="./VideoTmp/"+c.text())
            video=Clippy.createVideo(img,se,outFile="./VideoTmp/"+str(i)+"_"+c.text())
            os.remove(img)
            videoList.append(video)
            Clippy.reEncode(c.video())
            videoList.append("./VideoTmp/"+c.video())
        Clippy.concatVideo(videoList,outFile)

def main():

    def on_closing():
        if renderFlag:
            messagebox.showerror("書き出し中","書き出しが終わるまでしばらくお待ちください")
        while(renderFlag):
            root.mainloop()
        try:
            shutil.rmtree("./VideoTmp/")
            root.destroy()
        except:
            pass

    def video_button():
        if renderFlag:
            return
        fTyp = [("動画","*.mp4")]
        iDir = os.getcwd()
        filepath = filedialog.askopenfilename(filetypes = fTyp, initialdir = iDir)
        if not os.path.exists("./VideoTmp"):
            os.mkdir("VideoTmp")
        if filepath!="":
            filename = os.path.split(filepath)[1]
            shutil.copy(filepath,"./VideoTmp/"+filename)
            c=Clip(video=filename)
            videoList.insert(tk.END,c)
            clips.append(c)

    def bulk_button():
        if renderFlag:
            return
        iDir = os.getcwd()
        filepath = filedialog.askdirectory(initialdir = iDir)
        if not os.path.exists("./VideoTmp"):
            os.mkdir("VideoTmp")
        if filepath!="":
            videos=glob.glob(filepath+"/*.mp4")
            for v in videos:
                filename = os.path.split(v)[1]
                shutil.copy(v,"./VideoTmp/"+filename)
                c=Clip(video=filename)
                videoList.insert(tk.END,c)
                clips.append(c)

    def bg_button(filepath_entry):
        if renderFlag:
            return
        fTyp = [("png","*.png"),("jpg","*.jpg"),("すべて","*")]
        iDir = os.getcwd()
        filepath = filedialog.askopenfilename(filetypes = fTyp, initialdir = iDir)
        if filepath!="":
            filepath_entry.delete(0,tk.END)
            filepath_entry.insert(tk.END,filepath)

    def se_button(filepath_entry):
        if renderFlag:
            return
        fTyp = [("効果音","*.mp3"),("すべて","*")]
        iDir = os.getcwd()
        filepath = filedialog.askopenfilename(filetypes = fTyp, initialdir = iDir)
        if filepath!="":
            filepath_entry.delete(0,tk.END)
            filepath_entry.insert(tk.END,filepath)

    def show_selected(event):
        try:
            selectNum.set(videoList.curselection()[0])   #選択項目のindex取得
            title.set(clips[selectNum.get()].text())
            titleText.grid(row=5,column=1,sticky=tk.W,padx=10)
            titleEntry.grid(row=6,column=1,columnspan=2)
        except IndexError:
            pass
        except Exception as e:
            print(e)

    def change_text(event):
        if renderFlag:
            return
        clips[selectNum.get()].changeText(title.get())

    def render(bg,se,filename):
        global renderFlag
        renderFlag=True
        pBar.start()
        Clippy.render(bg,se,filename)
        messagebox.showinfo("CLiPPy", "書き出しが終わりました！")
        renderFlag=False
        pBar.stop()
        pText.grid_remove()
        pBar.grid_remove()
        threads.pop(0)

    def render_button():
        if renderFlag:
            return
        if clips==[]:
            messagebox.showerror('エラー', '動画が読み込まれていません')
            return
        pText.grid(row=12,column=1,sticky=tk.W)
        pBar.grid(row=13,column=1,columnspan=2)
        filename = filedialog.asksaveasfilename(
            title = "動画を保存",
            filetypes = [("mp4", ".mp4")],
            initialdir = "./"
        )
        if filename=="":
            return
        bg=bgEntry.get()
        se=seEntry.get()
        t=threading.Thread(target=partial(render,bg,se,filename))
        t.start()
        threads.append(t)

    def sort_video(event):
        if renderFlag:
            return
        before=videoList.curselection()[0]
        after=videoList.nearest(event.y)
        clip=videoList.get(before)
        c=clips[before]
        videoList.delete(before)
        del clips[before]
        videoList.insert(after,clip)
        clips.insert(after,c)

    def delete_video():
        if renderFlag:
            return
        n=selectNum.get()
        try:
            videoList.delete(n)
            del clips[n]
        except:
            pass
        if clips==[]:
            titleText.grid_remove()
            titleEntry.grid_remove()


    root = tk.Tk()
    root.title("CLiPPy! v0.2")
    root.geometry("520x350")
    root.resizable(False,False)
    root.iconbitmap('./Library/favicon.ico')
    root.protocol("WM_DELETE_WINDOW", on_closing)

    appName=ttk.Label(root,text="CLiPPy!")
    appName.grid(sticky=tk.W)

    frame = ttk.Frame(root)
    frame.grid()

    videoText = ttk.Label(frame, text="動画ファイル")
    videoText.grid(row=0,column=0)
    expVideoText = ttk.Label(frame, text="結合したい動画を読み込む(mp4のみ)")
    expVideoText.grid(row=0,column=1,sticky=tk.W)
    videoRead = ttk.Button(frame,text=u'読込', command=video_button)
    videoRead.grid(row=0,column=3)

    bulkRead = ttk.Button(frame,text=u'一括読込', command=bulk_button)
    bulkRead.grid(row=1,column=3)

    bgText = ttk.Label(frame, text="背景画像")
    bgText.grid(row=2,column=0)

    bgPath = tk.StringVar()
    bgEntry = ttk.Entry(frame, textvariable=bgPath, width=50)
    bgEntry.grid(row=2,column=1,columnspan=2)

    bgRead = ttk.Button(frame, text=u'読込', command=partial(bg_button,bgEntry))
    bgRead.grid(row=2,column=3)

    seText = ttk.Label(frame, text="効果音")
    seText.grid(row=3,column=0)

    sePath = tk.StringVar()
    seEntry = ttk.Entry(frame, textvariable=sePath, width=50)
    seEntry.grid(row=3,column=1,columnspan=2)

    seRead = ttk.Button(frame, text=u'読込', command=partial(se_button,seEntry))
    seRead.grid(row=3,column=3)

    videoText = ttk.Label(frame, text="読込動画一覧")
    videoText.grid(row=4,column=0,pady=10)

    clipList=tk.StringVar(value=[])
    videoList = tk.Listbox(frame,activestyle=tk.DOTBOX,selectmode="SINGLE",listvariable=clipList)
    videoList.grid(row=5,column=0,padx=3,rowspan=10)
    videoList.bind("<<ListboxSelect>>",show_selected)
    videoList.bind("<ButtonRelease-1>",sort_video)

    selectNum = tk.IntVar()

    titleText = ttk.Label(frame, text="クリップテキスト")

    title = tk.StringVar()
    titleEntry = ModifiedEntry(frame, textvariable=title, width=40)
    titleEntry.bind('<<TextModified>>', change_text)

    renderButton=ttk.Button(frame,text=u"作成",command=render_button)
    renderButton.grid(row=16,column=2)

    deleteButton=ttk.Button(frame,text=u"消去",command=delete_video)
    deleteButton.grid(row=16,column=0)

    pText = ttk.Label(frame,text="動画作成中")
    pBar = ttk.Progressbar(frame,mode='indeterminate',length=200)

    root.mainloop()

if __name__=="__main__":
    main()
