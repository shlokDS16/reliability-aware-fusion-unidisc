# Stage A: worked examples and falsifier

F1_G (EA vs EB) on the 7 drawn records: 0.2938775510204082; on the 5 worked examples: None
Falsifier (F1_G drawn below 0.6): True
Contamination test (drawn more than 0.15 below worked examples): None
Red-team MA2 test: {"M-sign": 0.9868421052631579, "budget_across_arms": 0.8888888888888888, "credited_ablation": 1.0, "fails": false}
Red-team MJ3 test: {"G4 M-anchorG": 0.9444444444444444, "G4 M-pool": 0.9166666666666666, "G4 M-class": 0.6388888888888888, "any_above_0.93": true}
Sign coverage (MJ1): {"KA1(a) printed arrow": 67, "lookup": 237, "EC": 0, "pending EC": 773, "unsigned": 0}; routed share 0.7177344475394615; final-null share 0.7177344475394615

Each extractor against the worked-example lists:
"not computed: --we not given (we-expected.jsonl is precondition A11)"
