import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog, simpledialog
from devices import DATA, PROFILES, settings, persist, save
from engine import Engine
from sdk_setup import setup, installed
from bridge import launch, screenshot, package_id

class Desktop:
    def __init__(self, root):
        self.root = root
        self.config = settings()
        self.engine = Engine(self.config)
        self.events = queue.Queue()
        self.busy = False
        root.title("AEMULUS")
        root.configure(bg="#15191f")
        root.minsize(700, 520)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10), foreground="#e8edf5", background="#202630")
        style.configure("TButton", padding=(10, 7))
        style.map("TButton", background=[("active", "#35577d")])
        style.configure("TCombobox", fieldbackground="#303945", foreground="#131820")
        panel = tk.Frame(root, background="#15191f", padx=26, pady=22)
        panel.pack(fill="both", expand=True)
        logo = tk.Canvas(panel, width=60, height=40, bg="#15191f", highlightthickness=0)
        logo.grid(row=0,column=0,sticky="w")
        logo.create_polygon(2,4, 29,15, 38,8, 47,10, 57,16, 46,16, 39,29, 21,36, 27,26, 13,21,
                            fill="#88bdff")
        tk.Label(panel,text="AEMULUS",bg="#15191f",fg="white",font=("Segoe UI",23,"bold")).grid(row=0,column=1,sticky="w")
        self.device = ttk.Combobox(panel, values=[p.title for p in PROFILES], state="readonly")
        self.device.current(0)
        self.device.grid(row=1,column=0,columnspan=4,sticky="ew",pady=(18,8))
        self.device.bind("<<ComboboxSelected>>", lambda _: self.refresh())
        def row(index, actions):
            for col,(label,fn) in enumerate(actions):
                ttk.Button(panel,text=label,command=fn).grid(row=index,column=col,sticky="ew",padx=2,pady=3)
                panel.columnconfigure(col,weight=1)
        ttk.Button(panel, text="Skonfiguruj Android automatycznie", command=self.auto_setup).grid(row=2,column=0,columnspan=4,sticky="ew",pady=(4,9))
        row(3,[("Utwórz urządzenie",lambda:self.session("create")),("Start",lambda:self.session("start")),
               ("Stop",lambda:self.session("stop")),("Status",self.refresh)])
        row(4,[("Instaluj APK",self.install),("Uruchom aplikację",self.open_app),
               ("Home",lambda:self.key("3")),("Back",lambda:self.key("4"))])
        row(5,[("Zrzut PNG",lambda:self.export(True)),("Logcat",lambda:self.export(False)),
               ("Domyślny launcher",lambda:self.android("shell","am","start","-a","android.settings.HOME_SETTINGS")),
               ("Ustawienia",self.preferences)])
        self.recent = ttk.Combobox(panel,values=self.config["recent"])
        self.recent.set(next(iter(self.config["recent"]), "dev.universalcarlauncher.app"))
        self.recent.grid(row=6,column=0,columnspan=3,sticky="ew",pady=8)
        ttk.Button(panel,text="Odinstaluj pakiet",command=self.remove).grid(row=6,column=3,sticky="ew")
        self.status = tk.StringVar(value="Wybierz profil, a następnie Start.")
        tk.Label(panel,textvariable=self.status,bg="#15191f",fg="#90bdff",anchor="w").grid(row=7,column=0,columnspan=4,sticky="ew")
        self.log = tk.Text(panel,height=9,bg="#101318",fg="#dee6ef",wrap="word",relief="flat",padx=10,pady=10)
        self.log.grid(row=8,column=0,columnspan=4,sticky="nsew",pady=8)
        panel.rowconfigure(8,weight=1)
        root.after(100,self.poll)

    def work(self, title, fn, done=None):
        if self.busy:
            messagebox.showinfo("AEMULUS","Trwa poprzednia operacja.")
            return
        self.busy = True
        self.device.configure(state="disabled")
        self.status.set(title+"…")
        def worker():
            try:
                self.events.put((True,fn(),done))
            except Exception as error:
                self.events.put((False,str(error),None))
        threading.Thread(target=worker,daemon=True).start()

    def poll(self):
        try:
            ok, result, done = self.events.get_nowait()
            if ok is None:
                self.log.insert("end", str(result) + "\n")
                self.log.see("end")
                self.root.after(120,self.poll)
                return
            self.busy = False
            self.device.configure(state="readonly")
            self.status.set("Zakończono" if ok else "Błąd")
            if isinstance(result,bytes):
                result = result.decode(errors="replace")
            self.log.insert("end",(str(result or "OK").strip() or "OK")+"\n")
            self.log.see("end")
            if done:
                done()
        except queue.Empty:
            pass
        self.root.after(120,self.poll)

    def selected(self):
        return PROFILES[self.device.current()]

    def call(self):
        engine, profile = self.engine, self.selected()
        return lambda *args, **kw: engine.target(profile,*args,**kw)

    def session(self, action):
        p, e = self.selected(), self.engine
        def run():
            if action=="create" and p.name in e.sessions():
                raise ValueError("Zatrzymaj urządzenie przed konfiguracją.")
            return getattr(e,action)(p)
        self.work(p.title+" · "+action,run)

    def refresh(self):
        p,e = self.selected(),self.engine
        def status():
            serial = e.sessions().get(p.name)
            if serial:
                boot = e.target(p,"shell","getprop","sys.boot_completed").strip()
                info = e.target(p,"shell","cat","/proc/meminfo").decode().splitlines()[:3]
                return f"{p.title} · {serial} · "+("gotowy" if boot==b"1" else "rozruch")+"\n"+"\n".join(info)
            state = "zatrzymane" if (e.home/(p.name+".ini")).exists() else "jeszcze nieutworzone"
            return p.title+" · "+state
        self.work("Odczyt statusu",status)

    def android(self,*args):
        call = self.call()
        self.work("ADB",lambda:call(*args))

    def key(self,code):
        self.android("shell","input","keyevent",code)

    def install(self):
        path = filedialog.askopenfilename(filetypes=[("Android APK","*.apk")])
        if path:
            call = self.call()
            self.work("Instalacja APK",lambda:call("install","-r",path,timeout=180))

    def open_app(self):
        pkg, call = self.recent.get().strip(), self.call()
        def remember():
            self.config["recent"] = ([pkg]+[p for p in self.config["recent"] if p!=pkg])[:12]
            persist(self.config)
            self.recent.configure(values=self.config["recent"])
        self.work("Uruchamianie",lambda:launch(call,pkg),remember)

    def remove(self):
        pkg = self.recent.get().strip()
        if messagebox.askyesno("Odinstalowanie",f"Usunąć {pkg} i jego dane z wybranego urządzenia?"):
            call = self.call()
            self.work("Odinstalowanie",lambda:call("uninstall",package_id(pkg)))

    def export(self,png):
        ext = ".png" if png else ".txt"
        dest = filedialog.asksaveasfilename(defaultextension=ext,filetypes=[(ext,"*"+ext)])
        if dest:
            call = self.call()
            pkg = self.recent.get().strip()
            def capture():
                if png:
                    screenshot(call,Path(dest))
                else:
                    pid = call("shell","pidof","-s",package_id(pkg)).decode().strip()
                    if not pid.isdecimal():
                        raise ValueError("Uruchom aplikację przed zapisem logu.")
                    save(Path(dest),call("logcat","-d","-t","2000","--pid="+pid))
                return dest
            self.work("Zapisywanie",capture)

    def auto_setup(self):
        if self.busy:
            return
        sdk = self.config["sdk"]
        if installed(sdk):
            messagebox.showinfo("AEMULUS", "Android SDK jest juz skonfigurowany.")
            return
        if not messagebox.askyesno("AEMULUS - Android SDK",
                "Program pobierze oficjalne komponenty Android SDK od Google. "
                "Wymagane jest kilka GB wolnego miejsca. "
                "Czy zapoznales sie z licencjami Android SDK i zgadzasz sie je zaakceptowac?"):
            return
        def report(message):
            self.events.put((None, message, None))
        self.work("Konfiguracja Android SDK", lambda: setup(sdk, report, accept_licenses=True))

    def preferences(self):
        if self.busy:
            return
        path = filedialog.askdirectory(title="Katalog Android SDK",initialdir=self.config["sdk"])
        if not path:
            return
        ram = simpledialog.askinteger("RAM","Pamięć gościa (MiB)",initialvalue=self.config["ram"],minvalue=1536,maxvalue=8192)
        if ram is None:
            return
        cores = simpledialog.askinteger("CPU","Liczba rdzeni",initialvalue=self.config["cores"],minvalue=1,maxvalue=8)
        if cores is None:
            return
        self.config.update(sdk=path,ram=ram,cores=cores)
        persist(self.config)
        self.engine = Engine(self.config)
        self.status.set(f"Zapisano · {ram} MiB · {cores} vCPU")

if __name__ == "__main__":
    root = tk.Tk()
    Desktop(root)
    root.mainloop()
