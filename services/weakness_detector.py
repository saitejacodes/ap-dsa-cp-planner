def detect_weaknesses(cf_stats,lc_stats):
    combined={}
    for tag,stats in cf_stats.items():
        if tag not in combined:
            combined[tag]={"attempted":0,"solved":0}
        combined[tag]["attempted"]+=stats["attempted"]
        combined[tag]["solved"]+=stats["solved"]
    for tag,stats in lc_stats.items():
        if tag not in combined:
            combined[tag]={"attempted":0,"solved":0}
        combined[tag]["solved"]+=stats["solved"]
        combined[tag]["attempted"]+=stats["attempted"]
    analysis=[]
    for tag,stats in combined.items():
        attempts=stats["attempted"]
        solves=stats["solved"]
        if attempts==0:
            analysis.append({"tag":tag,"status":"UNTOUCHED","rate":0,"evidence":"0 attempts"})
        else:
            rate=float(solves)/float(attempts)
            if rate<0.4:
                analysis.append({"tag":tag,"status":"WEAK","rate":rate,"evidence":f"{rate*100:.1f}% success"})
            elif rate>0.7:
                analysis.append({"tag":tag,"status":"STRONG","rate":rate,"evidence":f"{rate*100:.1f}% success"})
            else:
                analysis.append({"tag":tag,"status":"AVERAGE","rate":rate,"evidence":f"{rate*100:.1f}% success"})
    analysis.sort(key=lambda x:x["rate"])
    return analysis

