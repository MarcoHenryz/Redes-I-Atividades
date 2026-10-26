import json, random, os

OUT = "/home/marcoach/Work/Redes-I-Atividades/trabalho-virtualizacao-nuvem-container/Figuras"
os.makedirs(OUT, exist_ok=True)
rnd = random.Random(7)

INK   = "#1e1e1e"
BLUE  = "#a5d8ff"; BLUE_S  = "#1971c2"
YEL   = "#ffec99"; YEL_S   = "#f08c00"
GREY  = "#e9ecef"; GREY_S  = "#868e96"
GREEN = "#b2f2bb"; GREEN_S = "#2f9e44"
VIOL  = "#d0bfff"; VIOL_S  = "#6741d9"
NONE  = "transparent"

def base(t, x, y, w, h, **kw):
    e = {
        "type": t, "id": "%s-%d" % (t[:3], rnd.randrange(10**9)),
        "x": x, "y": y, "width": w, "height": h, "angle": 0,
        "strokeColor": INK, "backgroundColor": NONE, "fillStyle": "solid",
        "strokeWidth": 2, "strokeStyle": "solid", "roughness": 1, "opacity": 100,
        "groupIds": [], "frameId": None, "roundness": {"type": 3},
        "seed": rnd.randrange(10**9), "version": 1, "versionNonce": rnd.randrange(10**9),
        "isDeleted": False, "boundElements": [], "updated": 1, "link": None, "locked": False,
    }
    e.update(kw); return e

def rect(x, y, w, h, fill=NONE, stroke=INK, round_=True, sw=2, style="solid"):
    return base("rectangle", x, y, w, h, backgroundColor=fill, strokeColor=stroke,
                strokeWidth=sw, strokeStyle=style,
                roundness={"type": 3} if round_ else None)

def text(x, y, s, size=16, w=None, align="center", color=INK, family=1, bold_box=None):
    lines = s.split("\n")
    h = int(size * 1.25 * len(lines))
    w = w if w is not None else int(max(len(l) for l in lines) * size * 0.58)
    return base("text", x, y, w, h, text=s, originalText=s, fontSize=size, fontFamily=family,
                textAlign=align, verticalAlign="top", containerId=None, lineHeight=1.25,
                baseline=int(size * 0.9), strokeColor=color, roundness=None)

def centered(cx, cy, s, size=16, w=260, color=INK):
    """texto centrado em (cx, cy)"""
    lines = s.split("\n")
    h = int(size * 1.25 * len(lines))
    return text(cx - w / 2, cy - h / 2, s, size=size, w=w, align="center", color=color)

def line(pts, stroke=INK, style="solid", sw=2, arrow=False):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = xs[0], ys[0]
    return base("arrow" if arrow else "line", x0, y0, max(xs) - min(xs), max(ys) - min(ys),
                points=[[p[0] - x0, p[1] - y0] for p in pts],
                strokeColor=stroke, strokeStyle=style, strokeWidth=sw, roundness={"type": 2},
                lastCommittedPoint=None, startBinding=None, endBinding=None,
                startArrowhead=None, endArrowhead="arrow" if arrow else None)

def scene(elements, name):
    doc = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
           "elements": elements,
           "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
           "files": {}}
    p = os.path.join(OUT, name + ".excalidraw")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return p

# ===========================================================================
# FIGURA 2 — escopo de controle
# ===========================================================================
el = []
ROWS = [("Aplicação", 0), ("Middleware", 1), ("Sistema\noperacional", 2), ("Hardware e\nhipervisor", 3)]
COLS = ["IaaS", "PaaS", "SaaS"]
# estado: C = consumidor gerencia, U = consumidor usa / provedor mantém, P = provedor (oculta)
MATRIX = {  # (col, row) -> estado
    ("IaaS", 0): "C", ("IaaS", 1): "C", ("IaaS", 2): "C", ("IaaS", 3): "P",
    ("PaaS", 0): "C", ("PaaS", 1): "U", ("PaaS", 2): "P", ("PaaS", 3): "P",
    ("SaaS", 0): "U", ("SaaS", 1): "P", ("SaaS", 2): "P", ("SaaS", 3): "P",
}
FILL = {"C": (BLUE, BLUE_S), "U": (YEL, YEL_S), "P": (GREY, GREY_S)}

LX, LW = 40, 150          # coluna de rótulos
CW, CGAP = 210, 22        # largura/gap das colunas
RH, RGAP = 76, 14         # altura/gap das linhas
TOP = 120

def colx(i): return LX + LW + 30 + i * (CW + CGAP)
def rowy(j): return TOP + j * (RH + RGAP)

# cabeçalhos das colunas
for i, c in enumerate(COLS):
    el.append(centered(colx(i) + CW / 2, TOP - 42, c, size=28, w=CW))
# rótulos das linhas
for name, j in ROWS:
    el.append(centered(LX + LW / 2, rowy(j) + RH / 2, name, size=18, w=LW))
# células
CELL_TXT = {"C": "gerencia\ne mantém", "U": "usa\n(provedor mantém)", "P": "oculta"}
for i, c in enumerate(COLS):
    for name, j in ROWS:
        st = MATRIX[(c, j)]
        f, s = FILL[st]
        el.append(rect(colx(i), rowy(j), CW, RH, fill=f, stroke=s))
        txt = CELL_TXT[st] if j < 3 else "provedor"
        el.append(centered(colx(i) + CW / 2, rowy(j) + RH / 2, txt, size=14, w=CW - 16,
                           color="#495057"))
# fronteira de controle por coluna (linha tracejada no topo do bloco do consumidor)
FRONT = {"IaaS": rowy(2) + RH + RGAP / 2, "PaaS": rowy(0) + RH + RGAP / 2, "SaaS": rowy(0) - RGAP / 2}
for i, c in enumerate(COLS):
    y = FRONT[c]
    el.append(line([(colx(i) - 12, y), (colx(i) + CW + 12, y)], stroke=VIOL_S, style="dashed", sw=3))
el.append(text(colx(2) + CW + 26, FRONT["SaaS"] - 14, "fronteira de controle\ndo consumidor",
               size=14, w=190, align="left", color=VIOL_S))

# legenda
LY = rowy(3) + RH + 56
for k, (st, lab) in enumerate([("C", "consumidor instala, gerencia e mantém"),
                               ("U", "consumidor usa; provedor mantém"),
                               ("P", "oculta do consumidor / provedor")]):
    f, s = FILL[st]
    el.append(rect(LX, LY + k * 38, 34, 24, fill=f, stroke=s))
    el.append(text(LX + 46, LY + k * 38 + 2, lab, size=15, w=430, align="left", color="#495057"))
el.append(text(LX, LY + 3 * 38 + 14, "Adaptado de NIST SP 500-292, Figura 8, p. 9",
               size=13, w=430, align="left", color="#868e96"))

print(scene(el, "fig-escopo-controle"))

# ===========================================================================
# FIGURA 3 — camadas de orquestração
# ===========================================================================
el = []
X, W = 260, 820
# faixas
S_Y, S_H = 90, 150
R_Y, R_H = 290, 400
P_Y, P_H = 740, 190

el.append(rect(X, S_Y, W, S_H, fill=NONE, stroke=GREEN_S, sw=3))
el.append(text(X + 16, S_Y + 12, "Camada de serviço", size=20, w=320, align="left", color=GREEN_S))
for i, (m, d) in enumerate([("IaaS", "recursos\nfundamentais"),
                            ("PaaS", "plataforma e\nruntime"),
                            ("SaaS", "aplicação do\nprovedor")]):
    bx = X + 40 + i * 260
    el.append(rect(bx, S_Y + 54, 230, 76, fill=GREEN, stroke=GREEN_S))
    el.append(centered(bx + 115, S_Y + 78, m, size=18, w=210))
    el.append(centered(bx + 115, S_Y + 106, d, size=13, w=210, color="#495057"))

el.append(rect(X, R_Y, W, R_H, fill=NONE, stroke=VIOL_S, sw=3))
el.append(text(X + 16, R_Y + 12, "Camada de abstração e controle de recursos", size=20,
               w=560, align="left", color=VIOL_S))
# recorte VM
el.append(rect(X + 36, R_Y + 56, 350, 220, fill=NONE, stroke=GREY_S, style="dashed"))
el.append(centered(X + 211, R_Y + 76, "Virtualização completa", size=15, w=330, color="#495057"))
for i in range(3):
    vx = X + 52 + i * 110
    el.append(rect(vx, R_Y + 96, 96, 92, fill=BLUE, stroke=BLUE_S))
    el.append(centered(vx + 48, R_Y + 120, "app", size=14, w=88))
    el.append(centered(vx + 48, R_Y + 158, "SO\nhóspede", size=13, w=88, color="#495057"))
el.append(rect(X + 52, R_Y + 200, 318, 56, fill=VIOL, stroke=VIOL_S))
el.append(centered(X + 211, R_Y + 228, "Hipervisor", size=18, w=300))
# recorte contêiner
el.append(rect(X + 430, R_Y + 56, 350, 220, fill=NONE, stroke=GREY_S, style="dashed"))
el.append(centered(X + 605, R_Y + 76, "Virtualização em nível de SO", size=15, w=340, color="#495057"))
for i in range(3):
    cx = X + 446 + i * 110
    el.append(rect(cx, R_Y + 96, 96, 92, fill=YEL, stroke=YEL_S))
    el.append(centered(cx + 48, R_Y + 134, "app em\ncontêiner", size=13, w=88))
el.append(rect(X + 446, R_Y + 200, 318, 56, fill=VIOL, stroke=VIOL_S))
el.append(centered(X + 605, R_Y + 228, "Kernel compartilhado + runtime", size=15, w=310))
# faixa de controle
el.append(rect(X + 36, R_Y + 300, 744, 72, fill="#f8f0fc", stroke=VIOL_S))
el.append(centered(X + 408, R_Y + 322, "Controle", size=17, w=700))
el.append(centered(X + 408, R_Y + 350,
                   "alocação de recursos  ·  controle de acesso  ·  monitoramento de uso",
                   size=14, w=720, color="#495057"))

el.append(rect(X, P_Y, W, P_H, fill=NONE, stroke=GREY_S, sw=3))
el.append(text(X + 16, P_Y + 12, "Camada de recursos físicos", size=20, w=400,
               align="left", color="#495057"))
for i, t in enumerate(["Servidores\nCPU e memória", "Rede\nswitches e enlaces",
                       "Armazenamento", "Instalação\nHVAC e energia"]):
    bx = X + 30 + i * 196
    el.append(rect(bx, P_Y + 58, 176, 100, fill=GREY, stroke=GREY_S))
    el.append(centered(bx + 88, P_Y + 108, t, size=14, w=164))

# dependências e consumidor
el.append(line([(X + W / 2, S_Y + S_H + 8), (X + W / 2, R_Y - 8)], arrow=True, stroke=INK))
el.append(line([(X + W / 2, R_Y + R_H + 8), (X + W / 2, P_Y - 8)], arrow=True, stroke=INK))
el.append(text(X + W / 2 + 14, S_Y + S_H + 12, "depende de", size=13, w=130, align="left",
               color="#868e96"))
el.append(text(X + W / 2 + 14, R_Y + R_H + 12, "depende de", size=13, w=130, align="left",
               color="#868e96"))
el.append(rect(40, S_Y + 40, 170, 86, fill=NONE, stroke=INK))
el.append(centered(125, S_Y + 83, "Cloud\nConsumer", size=18, w=160))
el.append(line([(212, S_Y + 83), (X - 10, S_Y + 83)], arrow=True))
el.append(line([(125, S_Y + 130), (125, P_Y + 95), (X - 10, P_Y + 95)],
               arrow=True, style="dashed", stroke="#c92a2a"))
el.append(text(60, P_Y + 108, "sem acesso direto", size=14, w=200, align="left", color="#c92a2a"))
el.append(text(X, P_Y + P_H + 26, "Adaptado de NIST SP 500-292, §3.2 e Figura 15, p. 12-13",
               size=13, w=520, align="left", color="#868e96"))

print(scene(el, "fig-camadas-orquestracao"))
