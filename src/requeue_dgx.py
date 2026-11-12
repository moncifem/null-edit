"""Rebuild ~/nulledit/todo.txt on the DGX after the second out-of-memory stall (run there, in ~/nulledit).
Strictly serial. 31B gets a hard memory cap and files of at most 11,000 tokens. Existing lines are reused by name."""
lines = {}
for f in ("todo.bak_v8", "todo.txt", "failed.txt"):
    try:
        for l in open(f):
            if "|" in l:
                lines[l.split("|")[0].strip()] = l.rstrip("\n")
    except FileNotFoundError:
        pass
RC = "python run_conflict.py --sleep 0 --max-file-tokens 32000 --model ../data/models/{m} --tag {t} --instances ../results/conf_ids.txt --frames R"
lines["g12b_conf"] = "g12b_conf | " + RC.format(m="gemma-4-12B-it", t="g12b_conf")
lines["g26b_conf"] = "g26b_conf | " + RC.format(m="gemma-4-26B-A4B-it", t="g26b_conf")
CAP = "SCORER_MEM_FRACTION=0.8 python run_conflict.py --sleep 0 --max-file-tokens 11000 --model ../data/models/gemma-4-31B-it --tag {t} --instances ../results/test_ids.txt --limit 100 --frames {f}"
lines["g31b_test"] = "g31b_test | " + CAP.format(t="g31b_test", f="R")
lines["g31b_test_rx"] = "g31b_test_rx | " + CAP.format(t="g31b_test_rx", f="RX")
lines["g31b_conf"] = "g31b_conf | " + CAP.format(t="g31b_conf", f="R").replace("../results/test_ids.txt --limit 100", "../results/conf_ids.txt")
lines["diag_12b"] = "diag_12b | python diag_long.py --model ../data/models/gemma-4-12B-it --ref-tag g12b_test --n 2"
lines["diag_g26b"] = "diag_g26b | python diag_long.py --model ../data/models/gemma-4-26B-A4B-it --ref-tag g26b_test --n 2"
if "--max-tokens" not in lines["edit_e4b"]:
    lines["edit_e4b"] += " --max-tokens 640"
for k in ("gen_g26b_test", "gen_g31b_test"):
    lines[k] = lines[k].replace("--limit 60", "--limit 100")
lines["gen_g31b_test"] = "gen_g31b_test | SCORER_MEM_FRACTION=0.8 " + lines["gen_g31b_test"].split("|", 1)[1].strip().replace("--max-file-tokens 32000", "--max-file-tokens 11000")
order = ["g12b_conf", "g26b_conf", "g31b_test", "diag_12b", "diag_g26b", "noprefill_e4b", "g26b_test_rx", "gen_e2b_test",
         "gen_g12b_test", "gen_e4b_live", "g31b_conf", "g31b_test_rx", "gen_g26b_test", "gen_g31b_test", "edit_e4b"]
open("todo.txt.new", "w").write("\n".join(lines[o] for o in order) + "\n")
print("\n".join(lines[o][:150] for o in order))
