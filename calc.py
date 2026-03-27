import math
import numpy as np
import tkinter as tk

# Оформление и его переменные
BG_COLOR = '#1a1a1a'
FRAME_BG = '#262626'
TEXT_COLOR = '#ffff00'
HEADER_COLOR = "#99ffc0"
RESULT_CARD_BG = "#333333"
INPUT_FG = 'black'
FONT_MAIN = ('Segoe UI', 14, 'bold')
FONT_HEADER = ('Segoe UI', 14, 'bold italic')
FONT_RES_VAL = ('Consolas', 14, 'bold')

def compute_and_update():
    try:
        # Все расчетные формулы
        T = var_T.get()
        rate_val = var_p.get()
        strike_E = var_e.get()
        fwd_t = var_t.get()
        fut_k = var_k.get()

        steps = 10
        r_norm = rate_val / 100.0
        dt = T / steps
        vol = 0.1
        u = math.exp(vol * math.sqrt(dt))
        d = 1/u
        p = (math.exp(r_norm * dt) - d) / (u - d)
        q = 1 - p

        m_rates = np.zeros((steps+1, steps+1))
        m_rates[steps][0] = rate_val
        c_idx = 1
        for r in range(steps-1, -1, -1):
            m_rates[r][c_idx] = m_rates[r+1][c_idx-1] * u
            c_idx += 1
        for r in range(steps, -1, -1):
            for c in range(1, steps+1):
                if m_rates[r][c] == 0: m_rates[r][c] = m_rates[r][c-1] * d

        m_zcb = np.zeros((steps+1, steps+1))
        m_zcb[:, steps] = 100.0
        gap = 1
        for c in range(steps-1, -1, -1):
            for r in range(gap, steps+1):
                m_zcb[r][c] = ((p*m_zcb[r-1][c+1]/100 + q*m_zcb[r][c+1]/100) / (1 + m_rates[r][c]/100)) * 100
            if c > 0: gap += 1
        
        lbl_res_zcb.config(text=f"{max(0, m_zcb[10][0]):.2f}%")

        # Считаем Форвард
        t_s = int(fwd_t)
        m_z_t = np.zeros((t_s+1, t_s+1)); m_z_t[:, t_s] = 100.0
        sub = m_rates[m_rates.shape[0]-(t_s+1):, 0:(t_s+1)].copy()
        gap = 1
        for c in range(t_s-1, -1, -1):
            for r in range(gap, t_s+1):
                m_z_t[r][c] = ((p*m_z_t[r-1][c+1]/100 + q*m_z_t[r][c+1]/100) / (1 + sub[r][c]/100)) * 100
            if c > 0: gap += 1
        lbl_res_fwd.config(text=f"{(m_zcb[10][0] / m_z_t[t_s][0]) * 100:.2f}%")

        # Считае Фьючерс
        k_s = int(fut_k)
        m_f = m_zcb[m_zcb.shape[0]-(k_s+1):, 0:(k_s+1)].copy()
        gap = 1
        for c in range(k_s-1, -1, -1):
            for r in range(gap, k_s+1):
                m_f[r][c] = (p*m_f[r-1][c+1]/100 + q*m_f[r][c+1]/100) * 100
            if c > 0: gap += 1
        lbl_res_fut.config(text=f"{m_f[k_s][0]:.2f}%")

        # Считаем Опцион
        m_o = np.zeros((k_s+1, k_s+1))
        for r in range(k_s+1): m_o[r][k_s] = max(0, m_f[r][k_s] - strike_E)
        gap = 1
        for c in range(k_s-1, -1, -1):
            for r in range(gap, k_s+1):
                a, b = p*(m_o[r-1][c+1]/100), q*(m_o[r][c+1]/100)
                df = math.exp((r_norm * T)/k_s)
                m_o[r][c] = max((a+b)/df, max(0, m_f[r][c]/100 - strike_E/100)) * 100
            if c > 0: gap += 1
        lbl_res_opt.config(text=f"{m_o[k_s][0]:.2f}%")

    except Exception as e:
        print(f"Ошибка в расчетах: {e}")


# Выведем экран и в последубющем поделим его на 2 части, а то много окон это не круто
root = tk.Tk()
root.title("Stonks Predictor v0.1")
root.geometry("1000x800")
root.configure(bg=BG_COLOR)

# Вводим временные параметры и рыночные показатели
var_T = tk.DoubleVar(value=10.0)
var_t = tk.DoubleVar(value=4.0)
var_k = tk.DoubleVar(value=6.0)
var_p = tk.DoubleVar(value=5.0)
var_e = tk.DoubleVar(value=80.0)

# ЛЕВАЯ ПАНЕлб
left_panel = tk.Frame(root, bg=BG_COLOR)
left_panel.pack(side="left", fill="both", expand=True, padx=20)

# Временные параметры
f_time = tk.LabelFrame(left_panel, text=" ВРЕМЕННЫЕ ПАРАМЕТРЫ ", font=FONT_HEADER, bg=FRAME_BG, fg=HEADER_COLOR, pady=10, labelanchor='n')
f_time.pack(fill="x", pady=20)

params_data = [("Срок T (лет):", var_T), ("Форвард (t):", var_t), ("Фьючерс (k):", var_k)]
for t, v in params_data:
    r = tk.Frame(f_time, bg=FRAME_BG)
    r.pack(fill="x", padx=15, pady=5)
    tk.Label(r, text=t, font=FONT_MAIN, bg=FRAME_BG, fg=TEXT_COLOR).pack(side="left")
    tk.Spinbox(r, from_=0, to=100, textvariable=v, font=FONT_MAIN, width=6, bg='#f0f0f0', fg=INPUT_FG).pack(side="right")

# Рыночные показатели
f_market = tk.LabelFrame(left_panel, text=" РЫНОЧНЫЕ ПОКАЗАТЕЛИ ", font=FONT_HEADER, bg=FRAME_BG, fg=HEADER_COLOR, pady=10, labelanchor='n')
f_market.pack(fill="x", pady=20)

m_params_data = [("Ставка (%):", var_p, 0.5), ("Страйк (E):", var_e, 1.0)]
for t, v, s in m_params_data:
    r = tk.Frame(f_market, bg=FRAME_BG)
    r.pack(fill="x", padx=15, pady=5)
    tk.Label(r, text=t, font=FONT_MAIN, bg=FRAME_BG, fg=TEXT_COLOR).pack(side="left")
    tk.Spinbox(r, from_=0, to=200, increment=s, textvariable=v, font=FONT_MAIN, width=6, bg='#f0f0f0', fg=INPUT_FG).pack(side="right")

# Красная (зеленая) кнопка Трампа
btn = tk.Button(left_panel, text="ПОСЧИТАТЬ ДЕНБГИ", 
                font=('Segoe UI', 16, 'bold'), 
                bg="#42B438", fg='black',
                relief='flat', command=compute_and_update)
# Тут кнопку менять, если вдруг вам не понравится (хотел сделать красную, изучаю питон, бегу, спешу, падаю.. но пытаюсь.)
btn.pack(pady=30, fill="x", ipady=140)

# ПРАВАЯ ПАНЕЛЬ
right_panel = tk.LabelFrame(root, text=" ПОЛУЧЕННЫЙ РЕЗУЛЬТАТ ", font=FONT_HEADER, bg=BG_COLOR, fg=HEADER_COLOR, labelanchor='n')
right_panel.pack(side="right", fill="both", expand=True, padx=20, pady=20)

def create_res_row(parent, label_text):
    row = tk.Frame(parent, bg=BG_COLOR); row.pack(fill="x", padx=20, pady=40)
    tk.Label(row, text=label_text, font=FONT_MAIN, bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w")
    val_lbl = tk.Label(row, text="---", font=FONT_RES_VAL, bg=RESULT_CARD_BG, fg=HEADER_COLOR, pady=10, width=15, relief="solid", borderwidth=1)
    val_lbl.pack(pady=5)
    return val_lbl

lbl_res_zcb = create_res_row(right_panel, "Цена облигации ZCB₁₀:")
lbl_res_fwd = create_res_row(right_panel, "Форвардная цена (t):")
lbl_res_fut = create_res_row(right_panel, "Фьючерсная цена (k):")
lbl_res_opt = create_res_row(right_panel, "Стоимость Call-опциона:")

root.mainloop()