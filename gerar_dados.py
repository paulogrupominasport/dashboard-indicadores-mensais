import pandas as pd, datetime as dt, json
from collections import defaultdict
import sys, os
XL = sys.argv[1] if len(sys.argv)>1 else os.environ.get("XLSX_PATH","base.xlsx")
def S(n): return pd.read_excel(XL, sheet_name=n, dtype=object)

def ym(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return None
    if isinstance(v,(dt.datetime,dt.date,pd.Timestamp)): return (int(v.year),int(v.month))
    if isinstance(v,(int,float)):
        try:
            d=dt.datetime(1899,12,30)+dt.timedelta(days=float(v)); return (d.year,d.month)
        except: return None
    s=str(v).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S","%Y-%m-%d","%d/%m/%Y %H:%M:%S","%d/%m/%Y %H:%M","%d/%m/%Y"):
        try: d=dt.datetime.strptime(s[:19],fmt); return (d.year,d.month)
        except: pass
    return None
def num(v):
    try:
        if v is None or (isinstance(v,float) and pd.isna(v)): return 0.0
        return float(v)
    except: return 0.0
def cancel(v): return str(v).strip().lower().startswith('s')
def tit(s):
    s=str(s).strip()
    return ' '.join(w.capitalize() if not w.isupper() or len(w)>3 else w.capitalize() for w in s.split())

# ---------- USER NORMALIZATION ----------
import unicodedata
def _norm(s):
    b=''.join(c for c in unicodedata.normalize('NFKD',str(s)) if not unicodedata.combining(c))
    return ' '.join(b.lower().replace('.',' ').split())
# canônico = primeiro nome (com acento correto); cobre variações, caixa, e nomes "grudados"
CANON={'ana':'Ana Paula','anapaula':'Ana Paula','anapaulanunes':'Ana Paula',
 'beatriz':'Beatriz','beatrizribeiro':'Beatriz',
 'helder':'Helder','heldercamilodeoliveira':'Helder',
 'isabela':'Isabela',
 'joice':'Joice','joicerodriguesdeandrade':'Joice',
 'juceni':'Juceni','jucenimilack':'Juceni',
 'paulo':'Paulo','paulosilva':'Paulo','pauloameno':'Paulo',
 'patricia':'Patrícia','patriciadiniz':'Patrícia',
 'rafael':'Rafael',
 'viviane':'Viviane','vivianevitalinadefreitas':'Viviane',
 'fabiana':'Fabiana','fabianarodrigues':'Fabiana',
 'henrique':'Henrique','henriquesilva':'Henrique','henriquerodriguessilva':'Henrique',
 'hugo':'Hugo','hugopaula':'Hugo','hugopaulasilva':'Hugo',
 'heverton':'Heverton','felipe':'Felipe','luciana':'Luciana',
 'guilherme':'Guilherme','guilhermelucas':'Guilherme'}
def nuser(raw):
    s=str(raw).strip()
    if not s or s.lower() in ('nan','none'): return None
    base=_norm(s)
    if base=='proativo': return None
    nospace=base.replace(' ','')
    if nospace in CANON: return CANON[nospace]
    toks=base.split()
    if not toks: return None
    if toks[0] in ('ana','anapaula') or toks[:2]==['ana','paula']: return 'Ana Paula'
    if toks[0] in CANON: return CANON[toks[0]]
    return toks[0].capitalize()

# ---------- LOAD ----------
de=S('Documentos Emitidos'); dl=S('Documentos Lançados'); ped=S('Pedidos ')
cc=S('Carta Correção'); cad=S('Cadastros'); oc=S('Ordens Compra'); qr=S('Qrcodes'); vp=S('Vale Pedágio')
ag1=S('Agendamento T-mult'); ag2=S('Agendamento Imbituba'); ag3=S('Agendamento Proativo')

WINDOW=lambda a,m:(a==2026 and 1<=m<=12)  # months present in dashboard universe

# ========== VISAO (indicadores + produtividade) ==========
IND=['NF-e Emitidas','Documentos Lançados','Agendamentos','Vale Pedágios Emitidos','QR Codes Emitidos',
     'NF-e Canceladas','CC-e Geradas','Ordens Compra Emitidas','Pedidos Gerados','Cadastros Realizados']
UIND=['NF-e Emitidas','Documentos Lançados','Vale Pedágios Emitidos','QR Codes Emitidos','NF-e Canceladas','CC-e Geradas']
cards=defaultdict(lambda: defaultdict(int))
users=defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # (ym)->user->ind->count

def feed(df,datecol,ind,filt=None,usercol=None,per_user=False):
    for _,r in df.iterrows():
        if filt and not filt(r): continue
        k=ym(r.get(datecol))
        if not k or not WINDOW(*k): continue
        cards[k][ind]+=1
        if per_user and usercol:
            u=nuser(r.get(usercol))
            if u: users[k][u][ind]+=1

feed(de,'Data_Emissão','NF-e Emitidas',lambda r:not cancel(r.get('Cancelada')),'Usuário',True)
feed(de,'Data_Emissão','NF-e Canceladas',lambda r:cancel(r.get('Cancelada')),'Usuário',True)
feed(dl,'Data_Digitação','Documentos Lançados',None,'Usuário',True)
feed(vp,'Dt.Emissão','Vale Pedágios Emitidos',None,'Usuario',True)
feed(qr,'Período Início','QR Codes Emitidos',None,'Usuário',True)
feed(cc,'Data/Hora','CC-e Geradas',None,'Usuário',True)
feed(oc,'Data Lançamento','Ordens Compra Emitidas')
feed(cad,'Data_Ativa','Cadastros Realizados')
feed(ped,'Data do Pedido','Pedidos Gerados')
# Agendamentos = soma das 3 agendas
for d,col in [(ag1,'Entrada do Pátio'),(ag2,'Data Hora Programada'),(ag3,'Data Prevista de Chegada')]:
    for _,r in d.iterrows():
        k=ym(r.get(col))
        if k and WINDOW(*k): cards[k]['Agendamentos']+=1

months={}
for k in sorted(cards):
    a,m=k; key=f"{a}-{m:02d}"
    if sum(cards[k].values())<200: continue
    c={i:cards[k].get(i,0) for i in IND}
    ulist=[]
    for u,vals in users[k].items():
        v={i:vals.get(i,0) for i in UIND}
        tot=sum(v.values())
        if tot>0: ulist.append({"u":u,"total":tot,"vals":{i:v[i] for i in UIND if v[i]>0} if False else v})
    ulist.sort(key=lambda x:-x['total'])
    # prune zero-vals for compactness like original (keep only nonzero in vals)
    for u in ulist: u['vals']={i:c2 for i,c2 in u['vals'].items() if c2>0}
    months[key]={"ano":a,"mes":m,"cards":c,"total":sum(c.values()),"users":ulist}

ULBL={'NF-e Emitidas':'NF-e','Documentos Lançados':'Doc.Lanç.','Vale Pedágios Emitidos':'Vale Ped.','QR Codes Emitidos':'QR Code','NF-e Canceladas':'Cancel.','CC-e Geradas':'CC-e'}
CLBL={i:i for i in IND}
VISAO={"months":months,"cards":IND,"uind":UIND,"ulbl":ULBL,"clbl":CLBL}

# ========== DATA (financeiro) ==========
EXP_SET={101,102,106,123}              # expedições (Emitidos) — regra original
COMPRAS_SET={101,102,501}              # compras (Lançados) — regra original
SERV_SET={352,353,932,949}             # serviços de transporte / outra prestação
SERV_EXCL={352,353,932,949}            # excluídos das compras
FILIAL_MAP={1:'Minas Gusa',2:'Filial Imbituba',3:'Filial Criciúma',6:'Filial Fundão',7:'Filial 7',8:'Filial 8',9:'Filial 9'}
import re as _re
def normUnit(s):
    s=str(s or '').strip()
    u=s.upper().replace('FILIAL ','').strip()
    m={'MINAS GUSA':'Minas Gusa','IMBITUBA':'Filial Imbituba','CRICIUMA':'Filial Criciúma','CRICIÚMA':'Filial Criciúma','FUNDÃO':'Filial Fundão','FUNDAO':'Filial Fundão'}
    if u in m: return m[u]
    return ' '.join(w.capitalize() for w in s.split()) if s else 'Não Informada'
def uni_compras(code):
    try: return FILIAL_MAP.get(int(code)) or normUnit(code)
    except: return normUnit(code)
def fin(df, datecol, cfopcol, unicol, allowed, prodcol, unifn=None):
    agg=defaultdict(lambda:[0.0,0.0,0])  # (ano,mes,uni,cfop)->[valor,qtd,docs]
    prod=defaultdict(lambda:[0.0,0.0])
    for _,r in df.iterrows():
        if cancel(r.get('Cancelada')): continue
        c=r.get(cfopcol)
        if pd.isna(c): continue
        cint=int(c)
        if isinstance(allowed,tuple) and allowed[0]=='EXCEPT':
            if cint in allowed[1]: continue
        elif cint not in allowed: continue
        k=ym(r.get(datecol))
        if not k or not WINDOW(*k): continue
        raw=r.get(unicol)
        uni=unifn(raw) if unifn else (normUnit(raw) if (raw is not None and str(raw).strip()) else 'Não Informada')
        cf=cint; val=num(r.get('Valor_Total')); qt=num(r.get('Quantidade'))
        a=agg[(k[0],k[1],uni,cf)]; a[0]+=val; a[1]+=qt; a[2]+=1
        pn=str(r.get(prodcol) or '').strip()
        if pn: p=prod[pn]; p[0]+=val; p[1]+=qt
    rows=[{"ano":a,"mes":m,"unidade":u,"cfop":cf,"valor":round(v[0],2),"qtd":round(v[1],2),"docs":v[2]}
          for (a,m,u,cf),v in sorted(agg.items())]
    top=sorted(({"produto":p,"valor":round(v[0],2),"qtd":round(v[1],2)} for p,v in prod.items()),key=lambda x:-x['valor'])
    return rows,top

expedicoes,topExp=fin(de,'Data_Emissão','CFOp_Código','Descrição',EXP_SET,'Pseudônimo')
compras,topCom   =fin(dl,'Data_Emissão','CFoP_Código','Código',('EXCEPT',SERV_EXCL),'Pseudônimo.1',unifn=uni_compras)
servicos,topServ =fin(de,'Data_Emissão','CFOp_Código','Descrição',SERV_SET,'Pseudônimo')

# ========== SOBRAS ==========
sob=pd.read_excel(XL,'Sobras',header=None,dtype=object)
sobras=[]
for i in range(len(sob)):
    row=sob.iloc[i].tolist()
    k=ym(row[0]) if row else None
    if k and WINDOW(*k) and row[1] and str(row[1]).strip():  # data row with navio
        sobras.append({"mes":k[1],"ano":k[0],"navio":str(row[1]).strip(),
            "entrada":round(num(row[2]),2),"cliente":str(row[3]).strip() if row[3] else "",
            "volume":round(num(row[4]),2),"sobra":round(num(row[5]),2),
            "venda_volume":round(num(row[8]),2) if len(row)>8 else 0})

# ========== ESTOQUE (completo por mês) + PREVISTO x REALIZADO ==========
import math
MES_FULL={'JANEIRO':1,'FEVEREIRO':2,'MARÇO':3,'ABRIL':4,'MAIO':5,'JUNHO':6,'JULHO':7,'AGOSTO':8,'SETEMBRO':9,'OUTUBRO':10,'NOVEMBRO':11,'DEZEMBRO':12}
INV_MES={v:k for k,v in MES_FULL.items()}
def _cell(x):
    if x is None: return None
    if isinstance(x,float) and math.isnan(x): return None
    if isinstance(x,bool): return x
    if isinstance(x,int): return x
    if isinstance(x,float): return round(x,2)
    s=str(x).strip()
    if s=='' or s.lower()=='nan': return None
    try:
        f=float(s.replace(',','.')) if (s.count(',')==1 and s.count('.')==0) else float(s)
        return round(f,2)
    except: return s
def _blocks(df):
    starts=[]
    for i in range(len(df)):
        v=str(df.iloc[i,0]).strip().upper() if pd.notna(df.iloc[i,0]) else ''
        if v in MES_FULL: starts.append((i,MES_FULL[v]))
    out={}
    for k,(r,m) in enumerate(starts):
        end=starts[k+1][0] if k+1<len(starts) else len(df)
        rows=[]
        for i in range(r,end):
            row=[_cell(x) for x in df.iloc[i].tolist()]
            if any(c is not None and c!='' for c in row): rows.append(row)
        out[str(m)]={"label":INV_MES[m],"rows":rows}
    return out
est=pd.read_excel(XL,'Estoque',header=None,dtype=object)
estoque=_blocks(est)
_xl=pd.ExcelFile(XL)
_prn=[s for s in _xl.sheet_names if 'previsto' in s.lower().replace(' ','') or 'realizado' in s.lower()]
prevReal=_blocks(pd.read_excel(XL,_prn[0],header=None,dtype=object)) if _prn else {}

anos=sorted({r['ano'] for r in (compras+expedicoes+servicos)})
unidades=sorted({r['unidade'] for r in (compras+expedicoes+servicos)})
DATA={"meta":{"geradoEm":dt.date.today().isoformat(),"fonte":os.environ.get("FONTE_LABEL","Planilha online (Google)")},
 "compras":compras,"expedicoes":expedicoes,"servicos":servicos,
 "topProdCompras":topCom[:8],"topProdExped":topExp[:8],"topProdServ":topServ[:4],
 "sobras":sobras,"estoque":estoque,"prevReal":prevReal,"anos":anos,"unidades":unidades}

out={"DATA":DATA,"VISAO":VISAO}
OUTPATH=os.environ.get("OUT_PATH","dados.json")
json.dump(out,open(OUTPATH,"w"),ensure_ascii=False)
print("OK ->",OUTPATH)
print("estoque meses:",{k:len(v["rows"]) for k,v in estoque.items()})
print("prevReal meses:",{k:len(v["rows"]) for k,v in prevReal.items()})
print("recs compras/exped/serv:",len(compras),len(expedicoes),len(servicos))
print("VISAO meses:",list(VISAO["months"].keys()))
