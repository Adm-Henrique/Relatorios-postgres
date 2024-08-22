

### IMPORTANDO BIBLIOTECAS ###
import pandas as pd
import psycopg2
import customtkinter as ctk
from tkinter import *
from PIL import Image



#### FUNÇÃO CONSULTA SQL AUTONOMOS###
def exportar_aut():
    conn = psycopg2.connect(
        host="localhost",
        database="ALTERDATA_FESFUTEBOL",
        user="postgres",
        password="#abc123#"
    )

    global df_funcionarios

    sql_query = f''';with
    T1 as(
      select
    	i.idhistorico,
    	i.idcontribuinte,
    	a.nmsocio,
    	i.dtpagamento,
    	i.idevento,
    	i.nmevento,
    	i.vlevento,
        d.cdchamada,
    	i.nmdepartamento
      from wdp.ir{entry_empresa.get()} i
      left join wdp.cadauto a on (i.idcontribuinte = a.cdmatricula)
      left join wdp.depto d on (i.iddepartamento = d.iddepartamento)
    where dtpagamento between '{entry_dataini.get()}' and '{entry_datafinal.get()}'
      order by idhistorico, vlevento desc),
    T2 as(
      select *
      from
      T1 where character_length(nmevento) > 4 AND IDEVENTO <> '609' and idevento <> '003'),
      T3 as(
      select
      A.*,
      B.nmevento as N,
      B.vlevento as V
      from
      T2 as A left outer join T1 as B on A.idhistorico = B.idhistorico and A.Idevento <> B.Idevento),
      T4 as(
      select
    	idhistorico,
    	idcontribuinte,
    	nmsocio,
    	dtpagamento,
    	idevento,
    	nmevento,
    	vlevento,
        cdchamada,
    	nmdepartamento,
        case when N = 'INSS' then V else null end as inss,
    	case when N = 'IRRF' then V else null end as irrf from T3),
    T5 as
    (select
    	idhistorico,
    	idcontribuinte,
    	nmsocio,
    	dtpagamento,
    	idevento,
    	nmevento,
        cdchamada,
    	nmdepartamento,
    	vlevento,
    	max(inss) as inss,
    	max(irrf) as irrf
    from T4
    group by idhistorico,idcontribuinte,nmsocio,dtpagamento,idevento,nmevento,vlevento, cdchamada, nmdepartamento)

    select
    	EXTRACT(YEAR FROM dtpagamento) as ano,
    	CASE EXTRACT (MONTH from dtpagamento)
             WHEN 1 THEN 'JAN'
             WHEN 2 THEN 'FEV'
             WHEN 3 THEN 'MAR'
             WHEN 4 THEN 'ABR'
             WHEN 5 THEN 'MAI'
             WHEN 6 THEN 'JUN'
             WHEN 7 THEN 'JUL'
             WHEN 8 THEN 'AGO'
             WHEN 9 THEN 'SET'
             WHEN 10 THEN 'OUT'
             WHEN 11 THEN 'NOV'
             WHEN 12 THEN 'DEZ'
             END AS MES,
      cdchamada,
      nmdepartamento AS departamento,
    	idevento AS COD_EVENTO,
    	nmevento AS RUBRICA,
    	sum(vlevento) as vlevento_bruto,
    	sum(inss / 0.11) as Base_inss,
    	sum(inss) as inss_folha,
      sum(vlevento)*0.20 as inss_patronal,
    	sum(irrf) as irrf,
    	sum((inss) + (vlevento)*0.20) as GPS_2100
    from T5
    group by ano, mes, cdchamada, nmdepartamento, idevento, nmevento
    order by mes, idevento;'''

    df_funcionarios = pd.read_sql_query(sql_query, conn)
    df_funcionarios.to_excel('Resultados.xlsx', index=False)
    conn.close()
    entry_empresa.delete(0, END)
    entry_dataini.delete(0, END)
    entry_datafinal.delete(0, END)
    print(df_funcionarios)


#### CONSULTA SQL MOVIMENTO DE PENSAO ###
def exportar_pensao():
    conn = psycopg2.connect(
        host="localhost",
        database="ALTERDATA_PACK",
        user="postgres",
        password="#abc123#"
    )

    global df_pensao

    sql_query = f'''SELECT 	f.cdchamada,
                            f.nmfuncionario, 
                            to_char (r.dtinicial, 'dd/mm/yyyy') as dtinicial, 
                            to_char(r.dtfinal, 'dd/mm/yyyy') as dtfinal,
                            e.cdchamada AS Cod_rubrica , 
                            r.nmevento,  
                            r.vlevento
                    FROM wdp.r{entry_empresa.get()} r
                    INNER JOIN wdp.evento e ON r.idevento = e.idevento
                    INNER JOIN wdp.f00020 f ON r.idfuncionario = f.idfuncionario
                    WHERE (r.dtinicial BETWEEN '{entry_dataini.get()}' AND '{entry_datafinal.get()}') AND e.sttipoevento = 'P';'''
    df_pensao = pd.read_sql_query(sql_query, conn)
    df_pensao.to_excel('Pensao.xlsx', index=False)
    conn.close()
    entry_empresa.delete(0, END)
    entry_dataini.delete(0, END)
    entry_datafinal.delete(0, END)
    print(df_pensao)




#### CRIANDO INTERFACE GRÁFICA PRINCIPAL ###
Reports = ctk.CTk()
Reports.geometry("700x700")
Reports.resizable(width=False, height=False)
Reports.title('Reports Alterdata')
#janela.iconify() #fecha a janela/aplicação
#janela.deiconify #abre a janela/aplicação
Reports._set_appearance_mode('system') #Tema da aplicação
frame1 = ctk.CTkFrame(master=Reports, width=680, height=300).place(x=10, y=390)

imglogoprincipal = ctk.CTkImage(dark_image=Image.open("H:\Python\Relatorios-postgres\logo_alterdata_software-04.png"),
                                light_image=Image.open("H:\Python\Relatorios-postgres\logo_alterdata_software-04.png"),
                                size=(450,250))
ctk.CTkLabel(Reports, text=None, image=imglogoprincipal).place(x=130, y=80)

def Jan_Report_aut():
    Report_aut = ctk.CTkToplevel(Reports)
    Report_aut.title('Mov. Autônomos')
    Report_aut.geometry('330x220')
    Report_aut.resizable(width=False, height=False)
   

    global entry_empresa
    global entry_dataini
    global entry_datafinal

    label_empresa = ctk.CTkLabel(master=Report_aut, text='Empresa: ')
    label_empresa.grid(row=0, column=0, padx=10, pady=10)

    label_dataini = ctk.CTkLabel(master=Report_aut, text='Data Inicial: ')
    label_dataini.grid(row=1, column=0, padx=10, pady=10)

    label_datafinal = ctk.CTkLabel(master=Report_aut, text='Data Final: ')
    label_datafinal.grid(row=2, column=0, padx=10, pady=10)

    entry_empresa = ctk.CTkEntry(master=Report_aut, width= 200, placeholder_text='Código...', fg_color='#575757')
    entry_empresa.grid(row=0, column=1, padx=10, pady=10)

    entry_dataini = ctk.CTkEntry(master=Report_aut, width=200, placeholder_text='Data inicial...', fg_color='#575757')
    entry_dataini.grid(row=1, column=1, padx=10, pady=10)

    entry_datafinal = ctk.CTkEntry(master=Report_aut, width=200, placeholder_text='Data final...', fg_color='#575757')
    entry_datafinal.grid(row=2, column=1, padx=10, pady=10)

    botao_exportar = ctk.CTkButton(master=Report_aut, text='Exportar .xlsx', command=exportar_aut)
    botao_exportar.grid(row=4, column=0, padx=10, pady=10, columnspan=5, ipadx=80)

    Report_aut.transient()
    Report_aut.grab_set()
    Reports.wait_window(Report_aut)
    pass

def Jan_Report_pensao():
    Report_pensao = ctk.CTkToplevel(Reports)
    Report_pensao.title('Movimento de Pensão')
    Report_pensao.geometry('330x220')
    Report_pensao.resizable(width=False, height=False)

    global entry_empresa
    global entry_dataini
    global entry_datafinal

    label_empresa = ctk.CTkLabel(master=Report_pensao, text='Empresa: ')
    label_empresa.grid(row=0, column=0, padx=10, pady=10)

    label_dataini = ctk.CTkLabel(master=Report_pensao, text='Data Inicial: ')
    label_dataini.grid(row=1, column=0, padx=10, pady=10)

    label_datafinal = ctk.CTkLabel(master=Report_pensao, text='Data Final: ')
    label_datafinal.grid(row=2, column=0, padx=10, pady=10)

    entry_empresa = ctk.CTkEntry(master=Report_pensao, width= 200, placeholder_text='Código...', fg_color='#575757')
    entry_empresa.grid(row=0, column=1, padx=10, pady=10)

    entry_dataini = ctk.CTkEntry(master=Report_pensao, width=200, placeholder_text='Data inicial...', fg_color='#575757')
    entry_dataini.grid(row=1, column=1, padx=10, pady=10)

    entry_datafinal = ctk.CTkEntry(master=Report_pensao, width=200, placeholder_text='Data final...', fg_color='#575757')
    entry_datafinal.grid(row=2, column=1, padx=10, pady=10)

    botao_exportar = ctk.CTkButton(master=Report_pensao, text='Exportar .xlsx', command=exportar_pensao)
    botao_exportar.grid(row=4, column=0, padx=10, pady=10, columnspan=5, ipadx=80)

    Report_pensao.transient()
    Report_pensao.grab_set()
    Reports.wait_window(Report_pensao)
    pass

botao_Jan_Report_aut = ctk.CTkButton(master=Reports, text='Mov. Autônomos', command=Jan_Report_aut).place(x=300, y=500)
botao_Jan_Report_pensao = ctk.CTkButton(master=Reports, text='EV. PENSÃO', command=Jan_Report_pensao).place(x=300, y=550)


Reports.mainloop()

