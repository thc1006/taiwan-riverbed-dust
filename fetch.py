import urllib.request, json, time, os, csv
K="4c89a32a-a214-461b-bf29-30ff32a61a8a"
B=f"https://data.moenv.gov.tw/api/v2/aqx_p_488?api_key={K}"
C=os.path.dirname(os.path.abspath(__file__))
OUT=f"{C}/data/winter.csv"; PROG=f"{C}/data/progress.txt"
KEEP=["sitename","county","datacreationdate","pm10","pm10_avg","pm2.5","windspeed","winddirec","longitude","latitude"]
CTY={"彰化縣","雲林縣","南投縣","嘉義縣","嘉義市","臺中市","臺南市","苗栗縣"}   # 濁水溪流域 + 上下風背景

os.makedirs(f"{C}/data",exist_ok=True)
done=set()
if os.path.exists(PROG):
    done={int(x) for x in open(PROG).read().split() if x.strip()}
new=not os.path.exists(OUT)
f=open(OUT,"a",newline="",encoding="utf-8"); w=csv.DictWriter(f,fieldnames=KEEP)
if new: w.writeheader()
pf=open(PROG,"a")

for off in range(300000,442000,1000):
    if off in done: continue
    for attempt in range(3):
        try:
            j=json.loads(urllib.request.urlopen(urllib.request.Request(
                B+f"&limit=1000&offset={off}&format=JSON",
                headers={"User-Agent":"Mozilla/5.0 research"}),timeout=90).read())
            r=j if isinstance(j,list) else (j.get("records") or [])
            n=0
            for x in r:
                if x.get("county") in CTY:
                    w.writerow({k:x.get(k) for k in KEEP}); n+=1
            f.flush(); pf.write(f"{off}\n"); pf.flush()
            break
        except Exception:
            if attempt==2: pf.write(f"{off}\n"); pf.flush()
            time.sleep(3*(attempt+1))
    time.sleep(0.2)
f.close(); pf.close()
print("DONE")
