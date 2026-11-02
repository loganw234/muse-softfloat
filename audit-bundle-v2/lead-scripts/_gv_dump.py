
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("gv", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out = {
 "POPUP_WORDS": m.POPUP_WORDS, "POPUP_DWELL": m.POPUP_DWELL,
 "ARRIVALS": m.ARRIVALS, "T_BRIDGE": m.T_BRIDGE, "T_REPLAY": m.T_REPLAY,
 "SHIFT": m.SHIFT, "TOTAL": m.TOTAL, "T_BOX": m.T_BOX, "T_FADE": m.T_FADE,
 "GATES": [(g["id"], g["rank"], g["t0"], g["t1"]) for g in m.GATES],
 "LEGS": [list(x) for x in m.LEGS],
 "cursor_at_gates": [m.cursor_rank(g["t0"]) for g in m.GATES],
 "POPUP5": [[t, lines] for t, lines in m.POPUP5],
}
print(json.dumps(out))
