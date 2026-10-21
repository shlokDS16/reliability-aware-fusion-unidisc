# Stage A: worked examples and falsifier

F1_G (EA vs EB) on the 7 drawn records: 0.2413793103448276; on the 5 worked examples: None
Falsifier (F1_G drawn below 0.6): True
Contamination test (drawn more than 0.15 below worked examples): None
Red-team MA2 test: {"M-sign": 1.0, "budget_across_arms": 1.0, "credited_ablation": 1.0, "fails": false}
Red-team MJ3 test: {"G4 M-anchorG": 1.0, "G4 M-pool": 1.0, "G4 M-class": 1.0, "any_above_0.93": true}
Sign coverage (MJ1): {"KA1(a) printed arrow": 0, "lookup": 65, "EC": 0, "pending EC": 138, "unsigned": 0}; routed share 0.6798029556650246; final-null share 0.6798029556650246

Each extractor against the worked-example lists:
"not computed: --we not given (we-expected.jsonl is precondition A11)"
