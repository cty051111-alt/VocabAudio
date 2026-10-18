"""VocabAudio — light/dark Windows-style Tkinter desktop UI.

Fully local UI; third-party dictionary voice retrieval only starts on user action.
"""
from __future__ import annotations
import os, queue, subprocess, sys, threading, tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from vocab_core import read_file, deduplicate, render_audio
from settings_store import DEFAULTS, load_settings, save_settings, data_dir

PALETTES={
 'light': {'bg':'#F4F7FB','nav':'#FFFFFF','panel':'#FFFFFF','pane':'#F9FBFD','text':'#15243A','muted':'#6A7A8D','line':'#DCE5EF','accent':'#1677F8','selection':'#E5F0FF','entry':'#FFFFFF','danger':'#C13B45','ok':'#1A9C58'},
 'dark': {'bg':'#111B27','nav':'#141F2D','panel':'#1C2939','pane':'#172433','text':'#F0F5FB','muted':'#A6B7C9','line':'#35465B','accent':'#2586FF','selection':'#253F61','entry':'#172332','danger':'#F47D83','ok':'#31C979'}
}

class App:
 def __init__(self,root):
  self.root=root;root.title('VocabAudio · 词汇发音工坊 2.0 Beta');root.geometry('1240x795');root.minsize(1050,675)
  try:
   icon=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/'assets'/'VocabAudio.ico'
   if icon.exists():root.iconbitmap(str(icon))
  except Exception:pass
  self.settings=load_settings();self.theme=self.settings['theme'];self.p=PALETTES[self.theme]
  self.q=queue.Queue();self.busy=False;self.cancel=False;self.words=[];self.rows=[]
  self.accent=tk.StringVar(value=self.settings['accent']);self.speed=tk.DoubleVar(value=float(self.settings['speed']));self.gap=tk.DoubleVar(value=float(self.settings['gap']))
  self.repeat=tk.IntVar(value=int(self.settings['repeat']));self.open_folder=tk.BooleanVar(value=self.settings['open_folder'])
  self.output_name=tk.StringVar(value='vocabulary_audio');self.input_path='';self.output_dir=str(self.settings['last_output_dir'] or Path.home()/'Downloads')
  self.status=tk.StringVar(value='就绪 · 请导入 PDF、DOCX、TXT 或 CSV 词汇表');self.count=tk.StringVar(value='已识别 0 个单词')
  self.page='home';self.root.protocol('WM_DELETE_WINDOW',self.close)
  self.make_layout();self.apply_theme();self.root.after(100,self.poll)

 def make_layout(self):
  self.shell=tk.Frame(self.root);self.shell.pack(fill='both',expand=True)
  self.sidebar=tk.Frame(self.shell,width=220);self.sidebar.pack(side='left',fill='y');self.sidebar.pack_propagate(False)
  self.brand_row=tk.Frame(self.sidebar);self.brand_row.pack(fill='x',padx=16,pady=(26,0))
  self.brand_icon=tk.Canvas(self.brand_row,width=34,height=43,highlightthickness=0,bd=0);self.brand_icon.pack(side='left',padx=(0,7))
  for i,h in enumerate([12,23,34,23,12]):
   x=4+i*6; self.brand_icon.create_line(x,21-h/2,x,21+h/2,fill='#1677F8',width=4,capstyle='round')
  self.logo=tk.Label(self.brand_row,text='VocabAudio',font=('Segoe UI',16,'bold'),anchor='w');self.logo.pack(side='left')
  self.tag=tk.Label(self.sidebar,text='词汇发音工坊   ·   BETA',font=('Microsoft YaHei UI',9),anchor='w');self.tag.pack(fill='x',padx=24,pady=(3,35))
  self.nav={}
  for key,title in [('home','⌂   首页'),('words','▤   词汇管理'),('audio','◖   音频设置'),('help','ⓘ   使用帮助'),('settings','⚙   软件设置')]:
   btn=tk.Button(self.sidebar,text=title,anchor='w',relief='flat',bd=0,font=('Microsoft YaHei UI',11),command=lambda k=key:self.navigate(k),cursor='hand2',padx=22,pady=14)
   btn.pack(fill='x',padx=12,pady=3);self.nav[key]=btn
  self.nav_spacer=tk.Frame(self.sidebar,height=20);self.nav_spacer.pack(expand=True,fill='both')
  self.uninstall_btn=tk.Button(self.sidebar,text='卸载与清理  ›',anchor='w',relief='flat',bd=0,font=('Microsoft YaHei UI',10),command=self.uninstall_dialog,padx=22,pady=16,cursor='hand2');self.uninstall_btn.pack(fill='x',padx=12,pady=(0,14))
  self.content=tk.Frame(self.shell);self.content.pack(side='left',fill='both',expand=True)
  self.header=tk.Frame(self.content,height=95);self.header.pack(fill='x',padx=28,pady=(24,10))
  self.header_title=tk.Label(self.header,text='VocabAudio  词汇发音工坊',font=('Microsoft YaHei UI',23,'bold'),anchor='w');self.header_title.pack(anchor='w')
  self.header_desc=tk.Label(self.header,text='将词汇表快速转换为可跟读、可听写的朗读音频',font=('Microsoft YaHei UI',10),anchor='w');self.header_desc.pack(anchor='w',pady=(3,0))
  self.body=tk.Frame(self.content);self.body.pack(fill='both',expand=True,padx=26,pady=(0,12))
  self.left=tk.Frame(self.body);self.left.pack(side='left',fill='both',expand=True,padx=(0,18))
  self.right=tk.Frame(self.body,width=310);self.right.pack(side='right',fill='y');self.right.pack_propagate(False)
  # Left: workflow
  self.steps=tk.Label(self.left,text='① 导入文件   ───   ② 识别单词   ───   ③ 朗读设置   ───   ④ 导出音频',font=('Microsoft YaHei UI',10,'bold'))
  self.steps.pack(fill='x',pady=(8,17))
  self.import_panel=tk.Frame(self.left,highlightthickness=1);self.import_panel.pack(fill='x',pady=(0,15))
  self.import_title=tk.Label(self.import_panel,text='导入文件',font=('Microsoft YaHei UI',13,'bold'));self.import_title.pack(anchor='w',padx=18,pady=(14,4))
  self.import_hint=tk.Label(self.import_panel,text='支持 PDF、Word (.docx)、TXT、CSV；原生 .wps 请另存为 DOCX',font=('Microsoft YaHei UI',9));self.import_hint.pack(anchor='w',padx=18)
  self.drop=tk.Frame(self.import_panel,highlightthickness=1,height=147);self.drop.pack(fill='x',padx=18,pady=(12,15));self.drop.pack_propagate(False)
  self.drop_icon=tk.Label(self.drop,text='▤',font=('Segoe UI Symbol',30));self.drop_icon.pack(pady=(8,3))
  self.drop_label=tk.Label(self.drop,text='请选择需要生成发音的词汇表',font=('Microsoft YaHei UI',10));self.drop_label.pack()
  self.choose_btn=tk.Button(self.drop,text='选择文件',font=('Microsoft YaHei UI',10,'bold'),padx=20,pady=6,relief='flat',cursor='hand2',command=self.choose);self.choose_btn.pack(pady=(9,0))
  self.preview=tk.Frame(self.left,highlightthickness=1);self.preview.pack(fill='both',expand=True)
  top=tk.Frame(self.preview);top.pack(fill='x',padx=16,pady=(12,8));self.preview_top=top
  self.preview_label=tk.Label(top,text='识别结果预览',font=('Microsoft YaHei UI',12,'bold'));self.preview_label.pack(side='left')
  self.count_label=tk.Label(top,textvariable=self.count,font=('Microsoft YaHei UI',9));self.count_label.pack(side='right')
  columns=('num','word','ipa','state')
  table_frame=tk.Frame(self.preview);table_frame.pack(fill='both',expand=True,padx=16,pady=(0,9));self.table_frame=table_frame
  self.tree=ttk.Treeview(table_frame,columns=columns,show='headings',height=8,selectmode='extended')
  for key,head,width,anchor in [('num','序号',62,'center'),('word','英文单词 / 词组',175,'w'),('ipa','发音预览',160,'w'),('state','状态',90,'center')]:
   self.tree.heading(key,text=head);self.tree.column(key,width=width,minwidth=55,anchor=anchor,stretch=(key in ('word','ipa')))
  sb=ttk.Scrollbar(table_frame,orient='vertical',command=self.tree.yview);self.tree.configure(yscrollcommand=sb.set)
  sb.pack(side='right',fill='y');self.tree.pack(side='left',fill='both',expand=True)
  self.tree.bind('<Double-1>',lambda e:self.edit_selected())
  tools=tk.Frame(self.preview);tools.pack(fill='x',padx=16,pady=(0,11));self.tools=tools
  self.edit_btn=tk.Button(tools,text='编辑列表',command=self.edit_words,relief='flat',cursor='hand2',font=('Microsoft YaHei UI',9),padx=10,pady=5);self.edit_btn.pack(side='left')
  self.clean_btn=tk.Button(tools,text='删除选中',command=self.remove_selected,relief='flat',cursor='hand2',font=('Microsoft YaHei UI',9),padx=10,pady=5);self.clean_btn.pack(side='left',padx=8)
  self.generate_line=tk.Frame(self.left);self.generate_line.pack(fill='x',pady=(15,0))
  self.gen_btn=tk.Button(self.generate_line,text='▶  开始生成音频',font=('Microsoft YaHei UI',12,'bold'),padx=32,pady=11,relief='flat',command=self.start,cursor='hand2');self.gen_btn.pack(side='left')
  self.cancel_btn=tk.Button(self.generate_line,text='取消',font=('Microsoft YaHei UI',10),relief='flat',command=self.stop_work,state='disabled',padx=12,pady=10);self.cancel_btn.pack(side='left',padx=10)
  self.status_label=tk.Label(self.left,textvariable=self.status,font=('Microsoft YaHei UI',9),anchor='w');self.status_label.pack(fill='x',pady=(10,0))
  self.progress=ttk.Progressbar(self.left,maximum=100,mode='determinate');self.progress.pack(fill='x',pady=(5,0))
  # Right: controls
  self.settings_panel=tk.Frame(self.right,highlightthickness=1);self.settings_panel.pack(fill='both',expand=True)
  self.s_title=tk.Label(self.settings_panel,text='⚙  朗读设置',font=('Microsoft YaHei UI',14,'bold'));self.s_title.pack(anchor='w',padx=19,pady=(20,13))
  self.separator=tk.Frame(self.settings_panel,height=1);self.separator.pack(fill='x',padx=18,pady=(0,18))
  self.theme_frame=tk.Frame(self.settings_panel);self.theme_frame.pack(fill='x',padx=18,pady=(0,20))
  self.theme_label=tk.Label(self.theme_frame,text='界面主题',font=('Microsoft YaHei UI',10,'bold'));self.theme_label.pack(side='left')
  self.theme_btn=tk.Button(self.theme_frame,text='☾ 深色',font=('Microsoft YaHei UI',9),relief='flat',command=self.toggle_theme,cursor='hand2',padx=12,pady=4);self.theme_btn.pack(side='right')
  self.heading_label('发音口音')
  self.accent_frame=tk.Frame(self.settings_panel);self.accent_frame.pack(fill='x',padx=18,pady=(7,24))
  self.us=tk.Radiobutton(self.accent_frame,text='美式英语',variable=self.accent,value='us',command=self.persist,indicatoron=False,font=('Microsoft YaHei UI',10),relief='flat',bd=0,pady=10)
  self.uk=tk.Radiobutton(self.accent_frame,text='英式英语',variable=self.accent,value='uk',command=self.persist,indicatoron=False,font=('Microsoft YaHei UI',10),relief='flat',bd=0,pady=10)
  self.us.pack(side='left',fill='x',expand=True);self.uk.pack(side='left',fill='x',expand=True,padx=(7,0))
  self.speed_num=self.heading_label('语速',suffix='1.0×');self.speed_scale=self.add_scale(self.speed,0.7,1.3,self.update_speed)
  self.gap_num=self.heading_label('词间停顿',suffix='0.8 秒');self.gap_scale=self.add_scale(self.gap,0.2,3.0,self.update_gap)
  self.heading_label('重复次数')
  self.repeat_box=ttk.Combobox(self.settings_panel,textvariable=self.repeat,values=[1,2,3,4,5],state='readonly',font=('Microsoft YaHei UI',10));self.repeat_box.pack(fill='x',padx=18,pady=(8,20));self.repeat_box.bind('<<ComboboxSelected>>',lambda e:self.persist())
  self.heading_label('输出文件名')
  self.name_entry=tk.Entry(self.settings_panel,textvariable=self.output_name,font=('Consolas',11),relief='flat',highlightthickness=1);self.name_entry.pack(fill='x',padx=18,pady=(8,8),ipady=9)
  self.open_check=tk.Checkbutton(self.settings_panel,text='生成后自动打开文件夹',variable=self.open_folder,command=self.persist,font=('Microsoft YaHei UI',9),anchor='w');self.open_check.pack(fill='x',padx=18,pady=(7,8))
  self.location_btn=tk.Button(self.settings_panel,text='更改输出文件夹',font=('Microsoft YaHei UI',9),command=self.choose_dir,relief='flat',cursor='hand2',pady=8);self.location_btn.pack(fill='x',padx=18,pady=(5,7))
  self.output_hint=tk.Label(self.settings_panel,text='保存到：'+self.output_dir,font=('Microsoft YaHei UI',8),wraplength=255,justify='left');self.output_hint.pack(anchor='w',padx=18)

 def heading_label(self,text,suffix=None):
  line=tk.Frame(self.settings_panel);line.pack(fill='x',padx=18,pady=(2,0));self.rows.append(line)
  label=tk.Label(line,text=text,font=('Microsoft YaHei UI',10,'bold'));label.pack(side='left')
  value=None
  if suffix:
   value=tk.Label(line,text=suffix,font=('Segoe UI',10));value.pack(side='right')
  self.rows.append(label)
  if value:self.rows.append(value)
  return value

 def add_scale(self,variable,lo,hi,command):
  slider=tk.Scale(self.settings_panel,from_=lo,to=hi,resolution=.1,orient='horizontal',showvalue=False,variable=variable,command=command,bd=0,highlightthickness=0,length=270)
  slider.pack(fill='x',padx=18,pady=(5,22));return slider
 def update_speed(self,val):
  if self.speed_num:self.speed_num.config(text=f'{float(val):.1f}×')
  self.persist()
 def update_gap(self,val):
  if self.gap_num:self.gap_num.config(text=f'{float(val):.1f} 秒')
  self.persist()
 def persist(self):
  try:save_settings({'theme':self.theme,'accent':self.accent.get(),'speed':self.speed.get(),'gap':self.gap.get(),'repeat':self.repeat.get(),'open_folder':self.open_folder.get(),'last_output_dir':self.output_dir})
  except OSError:pass
 def apply_theme(self):
  p=self.p;self.root.configure(bg=p['bg'])
  for w,c in [(self.shell,p['bg']),(self.sidebar,p['nav']),(self.brand_row,p['nav']),(self.nav_spacer,p['nav']),(self.content,p['bg']),(self.header,p['bg']),(self.body,p['bg']),(self.left,p['bg']),(self.right,p['bg']),(self.import_panel,p['panel']),(self.drop,p['pane']),(self.preview,p['panel']),(self.preview_top,p['panel']),(self.table_frame,p['panel']),(self.tools,p['panel']),(self.generate_line,p['bg']),(self.settings_panel,p['panel']),(self.separator,p['line']),(self.theme_frame,p['panel']),(self.accent_frame,p['panel'])]:w.config(bg=c)
  self.brand_icon.config(bg=p['nav'])
  for w in self.rows:
   if isinstance(w,tk.Frame):w.config(bg=p['panel'])
   else:w.config(bg=p['panel'],fg=p['text'])
  for w in (self.logo,self.header_title,self.import_title,self.preview_label,self.s_title,self.theme_label):w.config(bg=p['nav'] if w is self.logo else p['bg'] if w is self.header_title else p['panel'],fg=p['text'])
  for w in (self.tag,self.header_desc,self.import_hint,self.drop_label,self.count_label,self.status_label,self.output_hint):w.config(bg=p['nav'] if w is self.tag else p['bg'] if w in (self.header_desc,self.status_label) else p['pane'] if w is self.drop_label else p['panel'],fg=p['muted'])
  self.drop_icon.config(bg=p['pane'],fg=p['muted']);self.steps.config(bg=p['bg'],fg=p['accent'])
  for w in (self.import_panel,self.preview,self.settings_panel):w.config(highlightbackground=p['line'])
  self.drop.config(highlightbackground=p['line'])
  for k,btn in self.nav.items():btn.config(bg=p['selection'] if k==self.page else p['nav'],fg=p['accent'] if k==self.page else p['text'],activebackground=p['selection'],activeforeground=p['accent'])
  self.uninstall_btn.config(bg=p['nav'],fg=p['muted'],activebackground=p['selection'])
  for w in (self.edit_btn,self.clean_btn,self.cancel_btn,self.location_btn,self.theme_btn):w.config(bg=p['pane'],fg=p['text'],activebackground=p['selection'],activeforeground=p['accent'])
  for w in (self.choose_btn,self.gen_btn):w.config(bg=p['accent'],fg='white',activebackground='#0563CD',activeforeground='white')
  for w in (self.us,self.uk):w.config(bg=p['pane'],fg=p['text'],selectcolor=p['selection'],activebackground=p['selection'])
  for w in (self.speed_scale,self.gap_scale):w.config(bg=p['panel'],fg=p['text'],troughcolor=p['line'],activebackground=p['accent'])
  self.open_check.config(bg=p['panel'],fg=p['text'],selectcolor=p['pane'],activebackground=p['panel'])
  self.name_entry.config(bg=p['entry'],fg=p['text'],insertbackground=p['text'],highlightbackground=p['line'],highlightcolor=p['accent'])
  self.theme_btn.config(text='☼ 浅色' if self.theme=='dark' else '☾ 深色')
  st=ttk.Style(self.root);st.theme_use('clam')
  st.configure('Treeview',background=p['entry'],fieldbackground=p['entry'],foreground=p['text'],borderwidth=0,rowheight=31,font=('Segoe UI',10))
  st.configure('Treeview.Heading',background=p['pane'],foreground=p['text'],font=('Microsoft YaHei UI',9,'bold'),relief='flat')
  st.map('Treeview',background=[('selected',p['selection'])],foreground=[('selected',p['text'])])
  st.configure('TCombobox',fieldbackground=p['entry'],background=p['pane'],foreground=p['text'],padding=8)
  st.configure('TProgressbar',background=p['accent'],troughcolor=p['line'])
  self.tree.tag_configure('ok',foreground=p['ok'])

 def toggle_theme(self):
  self.theme='dark' if self.theme=='light' else 'light';self.p=PALETTES[self.theme];self.apply_theme();self.persist()
 def navigate(self,key):
  self.page=key
  for k,b in self.nav.items():b.config(bg=self.p['selection'] if k==key else self.p['nav'],fg=self.p['accent'] if k==key else self.p['text'])
  if key=='home':return
  if key=='words':self.edit_words()
  elif key=='audio':self.status.set('音频设置位于界面右侧，可调整美式／英式、速度、停顿和重复次数。')
  elif key=='help':messagebox.showinfo('使用帮助','1. 选择 PDF、DOCX、TXT 或 CSV 词汇表。\n2. 双击表格行或打开「编辑列表」校对词汇。\n3. 设置口音、语速、停顿与重复次数。\n4. 点击「开始生成音频」输出 MP3。\n\n原生 WPS 格式请另存为 DOCX；扫描 PDF 请先 OCR。\n音频需要在线词典服务，下载失败会生成清单。')
  elif key=='settings':self.settings_dialog()
 def choose(self):
  file=filedialog.askopenfilename(title='选择词汇文件',filetypes=[('词汇文件','*.pdf *.docx *.txt *.csv *.wps *.doc'),('所有文件','*.*')])
  if not file:return
  try:words,method=read_file(file)
  except Exception as e:messagebox.showerror('读取失败',str(e));return
  if not words:messagebox.showwarning('没有找到单词','未识别到词条，请检查文件是否包含可复制的英文文本，或使用「编辑列表」手动粘贴。');return
  self.input_path=file;self.words=words;self.drop_label.config(text=Path(file).name);self.refresh_table()
  self.output_name.set(Path(file).stem+'_audio');self.status.set(f'已读取 {len(words)} 个单词（{method}）。可双击词条修改。')
 def refresh_table(self):
  self.tree.delete(*self.tree.get_children())
  for i,w in enumerate(self.words,1):self.tree.insert('','end',values=(i,w,'—','✓ 已识别'),tags=('ok',))
  self.count.set(f'已识别 {len(self.words)} 个单词')
 def edit_selected(self):
  selected=self.tree.selection()
  if not selected:return
  idx=self.tree.index(selected[0]);self.edit_words(index=idx)
 def remove_selected(self):
  indexes=sorted([self.tree.index(i) for i in self.tree.selection()],reverse=True)
  for i in indexes:del self.words[i]
  self.refresh_table()
 def edit_words(self,index=None):
  window=tk.Toplevel(self.root);window.title('编辑单词列表');window.geometry('550x550');window.transient(self.root)
  p=self.p;window.configure(bg=p['panel'])
  tk.Label(window,text='每行一个单词或词组。保存时自动去重并保留顺序。',bg=p['panel'],fg=p['muted'],font=('Microsoft YaHei UI',10)).pack(anchor='w',padx=20,pady=(20,8))
  txt=tk.Text(window,wrap='none',font=('Consolas',11),undo=True,bg=p['entry'],fg=p['text'],insertbackground=p['text']);txt.pack(fill='both',expand=True,padx=20,pady=(0,12));txt.insert('1.0','\n'.join(self.words))
  if index is not None:txt.mark_set('insert',f'{index+1}.0');txt.see('insert');txt.focus_set()
  def save():
   new=deduplicate(txt.get('1.0','end').splitlines());self.words=new;self.refresh_table();self.status.set(f'已更新，共 {len(new)} 个单词。');window.destroy()
  tk.Button(window,text='保存列表',bg=p['accent'],fg='white',relief='flat',font=('Microsoft YaHei UI',11,'bold'),command=save,padx=20,pady=8).pack(pady=(0,18))
 def choose_dir(self):
  folder=filedialog.askdirectory(title='选择导出文件夹',initialdir=self.output_dir)
  if folder:self.output_dir=folder;self.output_hint.config(text='保存到：'+folder);self.persist()
 def start(self):
  if self.busy:return
  words=deduplicate(self.words)
  if not words:messagebox.showwarning('没有单词','请先导入词汇表，或在词汇管理里粘贴单词。');return
  base=self.output_name.get().strip()
  if not base or any(c in base for c in '\\/:*?"<>|'):messagebox.showwarning('文件名错误','请输入合法的 Windows 文件名，不要包含特殊符号。');return
  try:
   directory=Path(self.output_dir);directory.mkdir(parents=True,exist_ok=True)
   target=directory/(base+'.mp3')
  except OSError as e:messagebox.showerror('输出错误',str(e));return
  if target.exists() and not messagebox.askyesno('确认覆盖','目标 MP3 已存在，确定覆盖吗？'):return
  self.busy=True;self.cancel=False;self.gen_btn.config(state='disabled');self.cancel_btn.config(state='normal');self.progress['value']=0
  accent=self.accent.get();gap=int(self.gap.get()*1000);speed=self.speed.get();repeat=max(1,int(self.repeat.get()))
  self.status.set(f'准备下载 {len(words)} 个词语的发音……');self.persist()
  def worker():
   try:
    # Repeat user-requested words in sequence; repetitions are kept, but legacy renderer de-duplicates.
    # Therefore audio repeats are handled by a repeat-aware extension to vocab_core.
    good,failed=render_audio(words,str(target),accent=accent,gap_ms=gap,pace=speed,repeat=repeat,progress=lambda i,n,w,s:self.q.put(('progress',i,n,w,s)),is_cancelled=lambda:self.cancel)
    self.q.put(('done',str(target),good,failed))
   except Exception as e:self.q.put(('error',str(e)))
  threading.Thread(target=worker,daemon=True).start()
 def stop_work(self):self.cancel=True;self.status.set('正在取消：完成当前下载后停止。')
 def poll(self):
  try:
   while True:
    item=self.q.get_nowait()
    if item[0]=='progress':
     _,i,n,w,s=item;self.progress['value']=int(i*100/n);self.status.set(f'{i}/{n} · {w} · {s}')
    elif item[0]=='error':
     self.finish();self.status.set(item[1]);messagebox.showerror('生成失败',item[1])
    elif item[0]=='done':
     _,target,good,failed=item;self.finish();self.progress['value']=100
     if failed:
      report=Path(target).with_suffix('.失败词表.txt');report.write_text('\n'.join(f'{w}: {e}' for w,e in failed),encoding='utf-8-sig')
      messagebox.showwarning('部分完成',f'成功 {len(good)} 个，失败 {len(failed)} 个。\n请检查：{report}\n失败的词没有包含在音频中。')
     else:messagebox.showinfo('生成完成',f'已生成 {len(good)} 个词的音频。\n{target}')
     self.status.set('已导出：'+target)
     if self.open_folder.get() and os.name=='nt':os.startfile(str(Path(target).parent))
  except queue.Empty:pass
  self.root.after(100,self.poll)
 def finish(self):self.busy=False;self.gen_btn.config(state='normal');self.cancel_btn.config(state='disabled')
 def settings_dialog(self):
  messagebox.showinfo('软件设置',f'版本：2.0 Beta\n当前主题：{"深色" if self.theme=="dark" else "浅色"}\n应用设置存放于：\n{data_dir()}\n\n源文件和输出 MP3 均由用户自行管理，不会被自动删除。')
 def uninstall_dialog(self):
  if self.busy:messagebox.showwarning('正在生成','请先取消音频生成再卸载。');return
  if not messagebox.askyesno('卸载与清理','将启动安全卸载助手。\n\n只会清理 VocabAudio 安装目录及程序自己的设置和缓存。\n不会删除你的 PDF、Word、个人 Python 环境或导出的 MP3。\n\n是否继续？'):return
  helper=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/'uninstall_helper.py'
  # Only launch helper from source checkout; frozen distribution uses shipped Uninstall.bat.
  if getattr(sys,'frozen',False):
   messagebox.showinfo('卸载方式','请先关闭程序，然后双击程序文件夹中的 Uninstall_VocabAudio.bat。\n它会明确显示删除范围，确认后再清理。');return
  messagebox.showinfo('卸载方式','请先关闭程序，再双击文件夹中的 Uninstall_VocabAudio.bat。\n不会删除你自己安装的 Python。')
 def close(self):
  if self.busy and not messagebox.askyesno('结束任务','正在生成音频，确定取消并退出吗？'):return
  self.cancel=True;self.persist();self.root.destroy()

def self_test():
 import requests, docx, pymupdf
 from vocab_core import ffmpeg_executable, youdao_url
 assert deduplicate(['acquire','adopt','acquire'])==['acquire','adopt']
 assert 'type=2' in youdao_url('acquire','us')
 f=Path(ffmpeg_executable());assert f.exists()
 result=subprocess.run([str(f),'-version'],capture_output=True,timeout=30,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 assert result.returncode==0
 if sys.stdout is not None: print('VocabAudio v2 self-test: PASS',flush=True)
 if '--self-test-report' in sys.argv:
  report=Path(sys.argv[sys.argv.index('--self-test-report')+1])
  report.write_text('VocabAudio v2 self-test: PASS',encoding='utf-8')
 return 0

if __name__=='__main__':
 if '--self-test' in sys.argv:sys.exit(self_test())
 root=tk.Tk();App(root);root.mainloop()
