import os
import pandas as pd
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox
from tkinter.ttk import Combobox, Treeview

class BatteryCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Autonoia")
        self.root.geometry("600x400")  # Define o tamanho da janela principal

        # Labels and Entries
        self.create_label_entry("Potência do UPS (kVA)", 0, "potencia_ups")
        self.create_label_entry("Fator de Potência do UPS", 1, "fator_potencia_ups")
        self.create_label_entry("Fator de Potência do Inversor", 2, "fator_potencia_inversor")
        self.create_label_entry("Quantidade de Baterias", 3, "quantidade_baterias")
        self.create_label_entry("Número de Bancos de Bateria", 4, "numero_bancos_bateria")

        # Spinners
        self.autonomia_var = StringVar(value='5min')  # Define valor inicial
        self.tensao_corte_var = StringVar(value='1.7')  # Define valor inicial

        self.create_combobox("Selecione a autonomia", ['5min', '10min', '15min', '20min', '30min', '45min', '1h', '2h', '3h', '4h', '5h', '6h', '8h', '10h', '20h'], 5, self.autonomia_var)
        self.create_combobox("Selecione a tensão de corte", ['1.6', '1.65', '1.67', '1.7', '1.75', '1.8', '1.85', '1.9'], 6, self.tensao_corte_var)

        # Calculate Button
        calc_button = Button(self.root, text="Calcular", command=self.calcular)
        calc_button.grid(row=7, column=1)

    def create_label_entry(self, text, row, var_name):
        label = Label(self.root, text=text)
        label.grid(row=row, column=0, pady=5)

        entry = Entry(self.root)
        entry.grid(row=row, column=1, pady=5)
        setattr(self, var_name, entry)

    def create_combobox(self, text, values, row, var):
        label = Label(self.root, text=text)
        label.grid(row=row, column=0, pady=5)

        combobox = Combobox(self.root, textvariable=var, values=values)
        combobox.grid(row=row, column=1, pady=5)

    def calcular(self):
        try:
            # Collecting Input Data
            potencia_ups = float(self.potencia_ups.get())
            fator_potencia_ups = float(self.fator_potencia_ups.get())
            fator_potencia_inversor = float(self.fator_potencia_inversor.get())
            quantidade_baterias = int(self.quantidade_baterias.get())
            numero_bancos_bateria = int(self.numero_bancos_bateria.get())
            autonomia = self.autonomia_var.get()
            tensao_corte = self.tensao_corte_var.get()

            # Calculating Watt per Cell
            watt_per_cell = (potencia_ups * 1000 * fator_potencia_ups / fator_potencia_inversor) / (quantidade_baterias * numero_bancos_bateria)
            resultado_calculo = watt_per_cell / 6

            # Loading and Filtering Excel Data

            tabela_baterias = pd.read_excel('BateriasDados.xlsx')
            tabela_baterias['F,V'] = tabela_baterias['F,V'].fillna('').astype(str).str.replace(',', '.').astype(float)

            autonomia_col = autonomia.replace('min', '') + 'min' if 'min' in autonomia else autonomia.replace('h', '') + 'h'
            filtro_autonomia = tabela_baterias[autonomia_col] >= resultado_calculo
            filtro_fv = tabela_baterias['F,V'] == float(tensao_corte)
            filtro_final = filtro_autonomia & filtro_fv

            tabela_selecionada = tabela_baterias.loc[filtro_final, ['Código', 'F,V', autonomia_col]]

            # Display Results
            if not tabela_selecionada.empty:
                self.abrir_janela_resultados(tabela_selecionada, resultado_calculo)
            else:
                self.mostrar_erro("Nenhuma bateria encontrada para a autonomia selecionada.")
        except Exception as e:
            self.mostrar_erro(str(e))

    def abrir_janela_resultados(self, tabela_baterias, resultado_calculo):
        results_window = Tk()
        results_window.title("Baterias Compativeis")
        results_window.geometry("1000x600")  # Define o tamanho da janela de resultados

        # Result Calculation Label
        resultado_label = Label(results_window, text=f"Resultado do Cálculo: {resultado_calculo:.2f} WPC")
        resultado_label.pack(pady=10)

        # Treeview for Table
        tree = Treeview(results_window, columns=("Código", "F,V", self.autonomia_var.get()), show="headings")
        tree.heading("Código", text="Código")
        tree.heading("F,V", text="F,V")
        tree.heading(self.autonomia_var.get(), text=self.autonomia_var.get())

        for _, row in tabela_baterias.iterrows():
            tree.insert("", "end", values=(row['Código'], row['F,V'], row[self.autonomia_var.get()]))

        tree.pack(fill="both", expand=True)

    def mostrar_erro(self, mensagem):
        messagebox.showerror("Erro", mensagem)

if __name__ == '__main__':
    root = Tk()
    app = BatteryCalculatorApp(root)
    root.mainloop()
