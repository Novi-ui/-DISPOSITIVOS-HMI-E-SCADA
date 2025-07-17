import tkinter as tk
from tkinter import messagebox, simpledialog

# Simulated PLC data
plc = {
    'motores': {
        'x': {'ligado': False, 'falha': False, 'temperatura': 30},
        'y': {'ligado': False, 'falha': False, 'temperatura': 30},
    },
    'sensores': {
        'porta_fechada': True,
        'emergencia': False,
    },
    'parametros': {
        'velocidade': 1000,
        'posicoes': [(10, 10), (50, 50)],
        'tamanho_placa': (300, 200),
    },
    'alarmes': [],
    'receitas': [
        {'nome': 'PlacaA', 'tamanho': (300, 200), 'furos': [(10, 10), (50, 50)], 'velocidade': 1000},
        {'nome': 'PlacaB', 'tamanho': (400, 200), 'furos': [(20, 20), (60, 60)], 'velocidade': 1200},
    ],
}

usuarios = {
    'operador': {'senha': '123', 'nivel': 'Utilizador'},
    'admin': {'senha': 'admin', 'nivel': 'Administrador'},
    'manut': {'senha': 'manut', 'nivel': 'Manutenção'},
    'editor': {'senha': 'edit', 'nivel': 'Editor de Parâmetros'},
}

user_session = {'usuario': None, 'nivel': None}

# Alarm logic
ALARMES_DISCRETOS = ['Porta de proteção aberta', 'Falha no motor X', 'Falha no motor Y', 'Emergência acionada']
ALARMES_ANALOGICOS = ['Superaquecimento motor X', 'Superaquecimento motor Y']


def verificar_alarmes():
    alarmes = []
    if not plc['sensores']['porta_fechada']:
        alarmes.append(ALARMES_DISCRETOS[0])
    if plc['motores']['x']['falha']:
        alarmes.append(ALARMES_DISCRETOS[1])
    if plc['motores']['y']['falha']:
        alarmes.append(ALARMES_DISCRETOS[2])
    if plc['sensores']['emergencia']:
        alarmes.append(ALARMES_DISCRETOS[3])
    if plc['motores']['x']['temperatura'] > 80:
        alarmes.append(ALARMES_ANALOGICOS[0])
    if plc['motores']['y']['temperatura'] > 80:
        alarmes.append(ALARMES_ANALOGICOS[1])
    plc['alarmes'] = alarmes

def autenticar(usuario, senha):
    if usuario in usuarios and usuarios[usuario]['senha'] == senha:
        user_session['usuario'] = usuario
        user_session['nivel'] = usuarios[usuario]['nivel']
        return True
    return False

def logout():
    user_session['usuario'] = None
    user_session['nivel'] = None

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('HMI - Máquina de Furar Placas')
        self.geometry('700x500')
        self.resizable(False, False)
        self.frames = {}
        for F in (LoginScreen, MainMenu, AlarmesScreen, ParametrosScreen, ReceitasScreen, ManutencaoScreen):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.place(relwidth=1, relheight=1)
        self.show_frame('LoginScreen')

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, 'refresh'):
            frame.refresh()

class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text='Login', font=('Arial', 24)).pack(pady=40)
        tk.Label(self, text='Usuário:').pack()
        self.user_entry = tk.Entry(self)
        self.user_entry.pack()
        tk.Label(self, text='Senha:').pack()
        self.pass_entry = tk.Entry(self, show='*')
        self.pass_entry.pack()
        tk.Button(self, text='Entrar', command=self.login).pack(pady=10)

    def login(self):
        usuario = self.user_entry.get()
        senha = self.pass_entry.get()
        if autenticar(usuario, senha):
            self.controller.show_frame('MainMenu')
        else:
            messagebox.showerror('Erro', 'Usuário ou senha inválidos')

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text='Menu Principal', font=('Arial', 20)).pack(pady=20)
        self.status_label = tk.Label(self, text='', font=('Arial', 12))
        self.status_label.pack(pady=5)
        btns = [
            ('Start', self.start),
            ('Stop', self.stop),
            ('Alarmes', lambda: controller.show_frame('AlarmesScreen')),
            ('Parâmetros', lambda: controller.show_frame('ParametrosScreen')),
            ('Receitas', lambda: controller.show_frame('ReceitasScreen')),
            ('Manutenção', lambda: controller.show_frame('ManutencaoScreen')),
            ('Logout', self.logout),
        ]
        for (txt, cmd) in btns:
            tk.Button(self, text=txt, width=20, command=cmd).pack(pady=3)

    def refresh(self):
        self.status_label.config(text=f'Usuário: {user_session["usuario"]} | Nível: {user_session["nivel"]}')

    def start(self):
        plc['motores']['x']['ligado'] = True
        plc['motores']['y']['ligado'] = True
        messagebox.showinfo('Info', 'Máquina iniciada!')

    def stop(self):
        plc['motores']['x']['ligado'] = False
        plc['motores']['y']['ligado'] = False
        messagebox.showinfo('Info', 'Máquina parada!')

    def logout(self):
        logout()
        self.controller.show_frame('LoginScreen')

class AlarmesScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text='Alarmes', font=('Arial', 20)).pack(pady=20)
        self.listbox = tk.Listbox(self, width=60, height=10)
        self.listbox.pack(pady=10)
        tk.Button(self, text='Resetar Alarmes', command=self.reset_alarms).pack(pady=5)
        tk.Button(self, text='Voltar', command=lambda: controller.show_frame('MainMenu')).pack(pady=5)

    def refresh(self):
        verificar_alarmes()
        self.listbox.delete(0, tk.END)
        for alarm in plc['alarmes']:
            self.listbox.insert(tk.END, alarm)
        if not plc['alarmes']:
            self.listbox.insert(tk.END, 'Nenhum alarme ativo.')

    def reset_alarms(self):
        # Só admin pode resetar
        if user_session['nivel'] != 'Administrador':
            messagebox.showwarning('Acesso negado', 'Apenas Administrador pode resetar alarmes.')
            return
        # Resetar falhas e sensores
        plc['motores']['x']['falha'] = False
        plc['motores']['y']['falha'] = False
        plc['sensores']['porta_fechada'] = True
        plc['sensores']['emergencia'] = False
        plc['motores']['x']['temperatura'] = 30
        plc['motores']['y']['temperatura'] = 30
        verificar_alarmes()
        self.refresh()
        messagebox.showinfo('Info', 'Alarmes resetados.')

class ParametrosScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text='Parâmetros', font=('Arial', 20)).pack(pady=20)
        self.vel_label = tk.Label(self, text='Velocidade:')
        self.vel_label.pack()
        self.vel_entry = tk.Entry(self)
        self.vel_entry.pack()
        self.pos_label = tk.Label(self, text='Posições dos furos (X, Y):')
        self.pos_label.pack()
        self.pos_entry = tk.Entry(self)
        self.pos_entry.pack()
        self.status_label = tk.Label(self, text='Status dos motores:')
        self.status_label.pack(pady=5)
        self.status_motores = tk.Label(self, text='')
        self.status_motores.pack()
        tk.Button(self, text='Salvar', command=self.salvar).pack(pady=5)
        tk.Button(self, text='Voltar', command=lambda: controller.show_frame('MainMenu')).pack(pady=5)

    def refresh(self):
        self.vel_entry.delete(0, tk.END)
        self.vel_entry.insert(0, str(plc['parametros']['velocidade']))
        self.pos_entry.delete(0, tk.END)
        self.pos_entry.insert(0, str(plc['parametros']['posicoes']))
        status = f"X: {'Ligado' if plc['motores']['x']['ligado'] else 'Desligado'}, " \
                 f"Y: {'Ligado' if plc['motores']['y']['ligado'] else 'Desligado'}"
        self.status_motores.config(text=status)

    def salvar(self):
        if user_session['nivel'] not in ['Administrador', 'Editor de Parâmetros']:
            messagebox.showwarning('Acesso negado', 'Apenas Administrador ou Editor pode alterar parâmetros.')
            return
        try:
            plc['parametros']['velocidade'] = int(self.vel_entry.get())
            posicoes = eval(self.pos_entry.get())
            if isinstance(posicoes, list):
                plc['parametros']['posicoes'] = posicoes
            else:
                raise ValueError
            messagebox.showinfo('Info', 'Parâmetros salvos!')
        except Exception:
            messagebox.showerror('Erro', 'Valores inválidos!')

class ReceitasScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text='Receitas', font=('Arial', 20)).pack(pady=20)
        self.listbox = tk.Listbox(self, width=60, height=8)
        self.listbox.pack(pady=10)
        tk.Button(self, text='Adicionar', command=self.adicionar).pack(side=tk.LEFT, padx=10)
        tk.Button(self, text='Editar', command=self.editar).pack(side=tk.LEFT, padx=10)
        tk.Button(self, text='Remover', command=self.remover).pack(side=tk.LEFT, padx=10)
        tk.Button(self, text='Voltar', command=lambda: controller.show_frame('MainMenu')).pack(side=tk.RIGHT, padx=10)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for r in plc['receitas']:
            self.listbox.insert(tk.END, f"{r['nome']} | Tamanho: {r['tamanho']} | Furos: {r['furos']} | Vel: {r['velocidade']}")

    def adicionar(self):
        if user_session['nivel'] not in ['Administrador', 'Editor de Parâmetros']:
            messagebox.showwarning('Acesso negado', 'Apenas Administrador ou Editor pode adicionar receitas.')
            return
        nome = simpledialog.askstring('Adicionar Receita', 'Nome da receita:')
        if not nome:
            return
        tamanho = simpledialog.askstring('Adicionar Receita', 'Tamanho da placa (ex: 300,200):')
        furos = simpledialog.askstring('Adicionar Receita', 'Furos (ex: [(10,10),(20,20)]):')
        velocidade = simpledialog.askinteger('Adicionar Receita', 'Velocidade:')
        try:
            tam = tuple(map(int, tamanho.split(',')))
            fur = eval(furos)
            plc['receitas'].append({'nome': nome, 'tamanho': tam, 'furos': fur, 'velocidade': velocidade})
            self.refresh()
        except Exception:
            messagebox.showerror('Erro', 'Valores inválidos!')

    def editar(self):
        idx = self.listbox.curselection()
        if not idx:
            return
        idx = idx[0]
        receita = plc['receitas'][idx]
        if user_session['nivel'] not in ['Administrador', 'Editor de Parâmetros']:
            messagebox.showwarning('Acesso negado', 'Apenas Administrador ou Editor pode editar receitas.')
            return
        nome = simpledialog.askstring('Editar Receita', 'Nome da receita:', initialvalue=receita['nome'])
        tamanho = simpledialog.askstring('Editar Receita', 'Tamanho da placa (ex: 300,200):', initialvalue=','.join(map(str, receita['tamanho'])))
        furos = simpledialog.askstring('Editar Receita', 'Furos (ex: [(10,10),(20,20)]):', initialvalue=str(receita['furos']))
        velocidade = simpledialog.askinteger('Editar Receita', 'Velocidade:', initialvalue=receita['velocidade'])
        try:
            tam = tuple(map(int, tamanho.split(',')))
            fur = eval(furos)
            receita.update({'nome': nome, 'tamanho': tam, 'furos': fur, 'velocidade': velocidade})
            self.refresh()
        except Exception:
            messagebox.showerror('Erro', 'Valores inválidos!')

    def remover(self):
        idx = self.listbox.curselection()
        if not idx:
            return
        if user_session['nivel'] not in ['Administrador', 'Editor de Parâmetros']:
            messagebox.showwarning('Acesso negado', 'Apenas Administrador ou Editor pode remover receitas.')
            return
        del plc['receitas'][idx[0]]
        self.refresh()

class ManutencaoScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text='Manutenção', font=('Arial', 20)).pack(pady=20)
        self.status_label = tk.Label(self, text='', font=('Arial', 12))
        self.status_label.pack(pady=10)
        tk.Button(self, text='Testar Motor X', command=self.testar_motor_x).pack(pady=3)
        tk.Button(self, text='Testar Motor Y', command=self.testar_motor_y).pack(pady=3)
        tk.Button(self, text='Testar Dispositivos de Segurança', command=self.testar_seguranca).pack(pady=3)
        tk.Button(self, text='Voltar', command=lambda: controller.show_frame('MainMenu')).pack(pady=10)

    def refresh(self):
        status = f"Motor X: {'Ligado' if plc['motores']['x']['ligado'] else 'Desligado'}, " \
                 f"Falha: {'Sim' if plc['motores']['x']['falha'] else 'Não'}, Temp: {plc['motores']['x']['temperatura']}°C\n" \
                 f"Motor Y: {'Ligado' if plc['motores']['y']['ligado'] else 'Desligado'}, " \
                 f"Falha: {'Sim' if plc['motores']['y']['falha'] else 'Não'}, Temp: {plc['motores']['y']['temperatura']}°C\n" \
                 f"Porta Proteção: {'Fechada' if plc['sensores']['porta_fechada'] else 'Aberta'}\n" \
                 f"Emergência: {'Ativada' if plc['sensores']['emergencia'] else 'Desativada'}"
        self.status_label.config(text=status)

    def testar_motor_x(self):
        plc['motores']['x']['falha'] = not plc['motores']['x']['falha']
        plc['motores']['x']['temperatura'] += 60 if plc['motores']['x']['falha'] else -60
        self.refresh()

    def testar_motor_y(self):
        plc['motores']['y']['falha'] = not plc['motores']['y']['falha']
        plc['motores']['y']['temperatura'] += 60 if plc['motores']['y']['falha'] else -60
        self.refresh()

    def testar_seguranca(self):
        plc['sensores']['porta_fechada'] = not plc['sensores']['porta_fechada']
        plc['sensores']['emergencia'] = not plc['sensores']['emergencia']
        self.refresh()

if __name__ == '__main__':
    app = App()
    app.mainloop()