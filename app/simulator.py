"""Deterministic, clearly fictional nationwide counting demo. Never represents actual elections."""
from __future__ import annotations
import hashlib, random, re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

REGIONS = [
 ('서울','서울특별시',48),('부산','부산광역시',18),('대구','대구광역시',12),('인천','인천광역시',14),
 ('광주','광주광역시',8),('대전','대전광역시',8),('울산','울산광역시',6),('세종','세종특별자치시',2),
 ('경기','경기도',60),('강원','강원특별자치도',9),('충북','충청북도',9),('충남','충청남도',11),
 ('전북','전북특별자치도',10),('전남','전라남도',10),('경북','경상북도',13),('경남','경상남도',14),('제주','제주특별자치도',2)
]
# 254 *fictional* district slots, NOT current official constituency allocation.
assert sum(x[2] for x in REGIONS)==254
CANDIDATES=['모의 후보 A','모의 후보 B','모의 후보 C']
NOT_FOUND='제공된 근거로는 확인할 수 없습니다.'


def clock():
    return datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')


def stable_seed(text):
    return int(hashlib.sha256(text.encode()).hexdigest()[:12],16)


def generate(seed=20261111):
    districts=[]
    for region,full,count in REGIONS:
        for i in range(1,count+1):
            district_id=f'{region}-{i:03}'
            rng=random.Random(stable_seed(f'{seed}:{district_id}'))
            eligible=rng.randrange(63000,187000,100)
            turnout=rng.uniform(.57,.77)
            target=int(eligible*turnout)
            weights=[rng.uniform(.23,.54),rng.uniform(.23,.54),rng.uniform(.06,.18)]
            weight_sum=sum(weights)
            weights=[v/weight_sum for v in weights]
            progress=rng.uniform(.04,.38)
            counted=int(target*progress)
            votes=[int(counted*weights[0]),int(counted*weights[1])]
            votes.append(counted-sum(votes))
            districts.append({'id':district_id,'region':region,'region_full':full,
                 'name':f'{region} 모의 {i:02d}선거구','eligible':eligible,
                 'target_votes':target,'counted':counted,'votes':votes,
                 'weights':weights,'progress':counted/target,'revision':0})
    return districts


def evolve(districts,seed,step):
    changes=[]
    for d in districts:
        rng=random.Random(stable_seed(f'{seed}:{step}:{d["id"]}'))
        if d['counted']>=d['target_votes'] or rng.random()<.13:continue
        remaining=d['target_votes']-d['counted']
        delta=min(remaining,max(1,int(d['target_votes']*rng.uniform(.002,.013))))
        fluctuating=[max(.015,w+rng.uniform(-.045,.045)) for w in d['weights']]
        s=sum(fluctuating)
        fractions=[x/s for x in fluctuating]
        add=[int(delta*fractions[0]),int(delta*fractions[1])]
        add.append(delta-sum(add))
        d['votes']=[v+a for v,a in zip(d['votes'],add)]
        d['counted']+=delta
        d['progress']=round(d['counted']/d['target_votes'],6)
        d['revision']+=1
        changes.append({'id':d['id'],'added':delta})
    return changes


def aggregate(districts,region=None):
    chosen=[d for d in districts if region is None or d['region']==region]
    counted=sum(d['counted'] for d in chosen)
    targets=sum(d['target_votes'] for d in chosen)
    eligible=sum(d['eligible'] for d in chosen)
    votes=[sum(d['votes'][i] for d in chosen) for i in range(3)]
    assert sum(votes)==counted
    winner=sorted(range(3),key=lambda i:(-votes[i],i))
    return {'counted':counted,'target_votes':targets,'eligible':eligible,'progress_pct':round(counted/targets*100,2) if targets else 0,
      'turnout_simulated_pct':round(targets/eligible*100,1) if eligible else 0,'votes':votes,
      'percentages':[round(v/counted*100,2) if counted else 0 for v in votes],
      'leader':CANDIDATES[winner[0]] if counted else '집계 전','lead_votes':votes[winner[0]]-votes[winner[1]] if counted else 0,
      'districts':len(chosen)}


def snapshot(districts,step,seed):
    return {'mode':'SIMULATION_ONLY','banner':'교육용 모의 개표 · 실제 선거와 무관',
        'source':'내장된 난수 생성기 (공식 선거 데이터 아님)','updated_at':clock(),'step':step,'seed':seed,
        'candidates':CANDIDATES,'national':aggregate(districts),
        'regions':[{'id':r,'full_name':full,**aggregate(districts,r)} for r,full,_ in REGIONS],
        'districts':[{'id':d['id'],'region':d['region'],'name':d['name'],'counted':d['counted'],
           'target_votes':d['target_votes'],'progress_pct':round(d['progress']*100,2),
           'votes':d['votes'],'percentages':[round(v/d['counted']*100,2) if d['counted'] else 0 for v in d['votes']],
           'eligible':d['eligible']} for d in districts]}

