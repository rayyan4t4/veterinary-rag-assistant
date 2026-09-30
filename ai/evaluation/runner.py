import json
from pathlib import Path

def load_jsonl(path: str):
    required={"question","relevant_document_ids"}; rows=[]
    for line_no,line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(),1):
        row=json.loads(line)
        if not required.issubset(row): raise ValueError(f"Line {line_no} lacks required fields")
        rows.append(row)
    return rows

def retrieval_metrics(expected: set[str], ranked: list[str], k: int):
    top=ranked[:k]; hits=[x for x in top if x in expected]
    first=next((i for i,x in enumerate(ranked,1) if x in expected),None)
    return {"precision_at_k":len(hits)/k,"recall_at_k":len(set(hits))/len(expected) if expected else 0,"hit_rate":float(bool(hits)),"mrr":1/first if first else 0}
