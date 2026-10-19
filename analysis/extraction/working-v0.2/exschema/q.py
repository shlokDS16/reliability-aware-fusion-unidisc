import sys
root = sys.argv[1]
sys.path.insert(0, root + "/analysis/screening")
import quote_check as qc
t = open(root + "/research/sources/md/fulltext-pymupdf/M00285.txt", encoding="utf-8").read()
for q in ["D3PM-absorbing 256 1.47 OA-ARDM (ours) 250 1.43 ±0.001",
          "OA-ARDM (ours) 250 1.43 ±0.001",
          "Table 1: Order Agnostic model performance (in bpc) on the text8 dataset."]:
    print(qc.quote_status(q, t), "|", q)
