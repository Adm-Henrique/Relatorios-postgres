
######## Importando bibliotecas ########

import pandas as pd
import psycopg2
import tkinter as tk
import customtkinter as ctk

######## Conectar-se ao banco de dados PostgreSQL ########

# conn = psycopg2.connect(
#     host="localhost",
#     database="ALTERDATA_FESFUTEBOL",
#     user="postgres",
#     password="#abc123#"
# )


######## Funções para consulta SQL ########
def exportar():
    conn = psycopg2.connect(
        host="localhost",
        database="ALTERDATA_FESFUTEBOL",
        user="postgres",
        password="#abc123#"
    )

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
    df_funcionarios.to_excel('Resultados_tk.xlsx', index=False)

    conn.close()
    print(df_funcionarios)

######### Criando Interface ########

janela = tk.Tk()
janela.title('Dados do Relatório')

# Labels:
label_empresa = tk.Label(janela, text='Empresa: ')
label_empresa.grid(row=0, column=0, padx=10, pady=10)

label_dataini = tk.Label(janela, text='Data Inicial: ')
label_dataini.grid(row=1, column=0, padx=10, pady=10)

label_datafinal= tk.Label(janela, text='Data Final: ')
label_datafinal.grid(row=2, column=0, padx=10, pady=10)

# Entry's
entry_empresa = tk.Entry(janela, text='Empresa: ', width=30)
entry_empresa.grid(row=0, column=1, padx=10, pady=10)

entry_dataini = tk.Entry(janela, text='Data Inicial: ', width=30)
entry_dataini.grid(row=1, column=1, padx=10, pady=10)

entry_datafinal= tk.Entry(janela, text='Data Final: ', width=30)
entry_datafinal.grid(row=2, column=1, padx=10, pady=10)

# Botões:
botao_consulta = tk.Button(janela, text='Exportar', command= exportar)
botao_consulta.grid(row=4, column=0, padx=10, pady=10, columnspan=5, ipadx=80)


janela.mainloop()



# # Definindo variáveis de consulta:
# empresa = input('Cod. Empresa: ')
# dataini = input('Data Inicial: ')
# datafinal = input('Data Final: ')
#
#
# # Definir a consulta SQL
# sql_query = f''';with
# T1 as(
#   select
# 	i.idhistorico,
# 	i.idcontribuinte,
# 	a.nmsocio,
# 	i.dtpagamento,
# 	i.idevento,
# 	i.nmevento,
# 	i.vlevento,
#     d.cdchamada,
# 	i.nmdepartamento
#   from wdp.ir{empresa} i
#   left join wdp.cadauto a on (i.idcontribuinte = a.cdmatricula)
#   left join wdp.depto d on (i.iddepartamento = d.iddepartamento)
# where dtpagamento between '{dataini}' and '{datafinal}'
#   order by idhistorico, vlevento desc),
# T2 as(
#   select *
#   from
#   T1 where character_length(nmevento) > 4 AND IDEVENTO <> '609' and idevento <> '003'),
#   T3 as(
#   select
#   A.*,
#   B.nmevento as N,
#   B.vlevento as V
#   from
#   T2 as A left outer join T1 as B on A.idhistorico = B.idhistorico and A.Idevento <> B.Idevento),
#   T4 as(
#   select
# 	idhistorico,
# 	idcontribuinte,
# 	nmsocio,
# 	dtpagamento,
# 	idevento,
# 	nmevento,
# 	vlevento,
#     cdchamada,
# 	nmdepartamento,
#     case when N = 'INSS' then V else null end as inss,
# 	case when N = 'IRRF' then V else null end as irrf from T3),
# T5 as
# (select
# 	idhistorico,
# 	idcontribuinte,
# 	nmsocio,
# 	dtpagamento,
# 	idevento,
# 	nmevento,
#     cdchamada,
# 	nmdepartamento,
# 	vlevento,
# 	max(inss) as inss,
# 	max(irrf) as irrf
# from T4
# group by idhistorico,idcontribuinte,nmsocio,dtpagamento,idevento,nmevento,vlevento, cdchamada, nmdepartamento)
#
# select
# 	EXTRACT(YEAR FROM dtpagamento) as ano,
# 	CASE EXTRACT (MONTH from dtpagamento)
#          WHEN 1 THEN 'JAN'
#          WHEN 2 THEN 'FEV'
#          WHEN 3 THEN 'MAR'
#          WHEN 4 THEN 'ABR'
#          WHEN 5 THEN 'MAI'
#          WHEN 6 THEN 'JUN'
#          WHEN 7 THEN 'JUL'
#          WHEN 8 THEN 'AGO'
#          WHEN 9 THEN 'SET'
#          WHEN 10 THEN 'OUT'
#          WHEN 11 THEN 'NOV'
#          WHEN 12 THEN 'DEZ'
#          END AS MES,
#   cdchamada,
#   nmdepartamento AS departamento,
# 	idevento AS COD_EVENTO,
# 	nmevento AS RUBRICA,
# 	sum(vlevento) as vlevento_bruto,
# 	sum(inss / 0.11) as Base_inss,
# 	sum(inss) as inss_folha,
#   sum(vlevento)*0.20 as inss_patronal,
# 	sum(irrf) as irrf,
# 	sum((inss) + (vlevento)*0.20) as GPS_2100
# from T5
# group by ano, mes, cdchamada, nmdepartamento, idevento, nmevento
# order by mes, idevento;'''


# # Executar a consulta e obter os resultados
# df_funcionarios = pd.read_sql_query(sql_query, conn)
#
# # Fechar a conexão com o banco de dados
# conn.close()
#
# # Exibindo o data freme da consulta
# print(df_funcionarios)
#
# # Exportar os resultados para um arquivo Excel
# df_funcionarios.to_excel('Resultados.xlsx', index=False)
#
# print(df_funcionarios)
