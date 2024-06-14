import pandas as pd
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os
import webbrowser

#Coleta de dados
diretorioScript = os.path.dirname(__file__)
caminhoParquet = os.path.join(diretorioScript, '../database/banco-de-dados.parquet')
dfProntuarios = pd.read_parquet(caminhoParquet)

#Funcao para aplicar filtro de horarios
@st.cache_resource()
def aplicarFiltros(dfIn,horarioInicial, horarioFinal, excluirMedicamentos):

   maskHorario = (dfIn['horario'] >= horarioInicial) & (dfIn['horario'] <= horarioFinal)
   maskMedicamentos = ~dfIn['medicacao'].isin(excluirMedicamentos)

   dfOut = dfIn[maskHorario & maskMedicamentos]

   dfOut = dfOut.drop_duplicates(subset=['nome', 'classe', 'horario'])

   return dfOut

#Funcao para identificar o turno da medicacao
def determinarTurno(horario):
    if horario.hour >= 20 or horario.hour < 2:
        return 'T1'
    elif horario.hour >= 2 and horario.hour < 8:
        return 'T2'
    elif horario.hour >= 8 and horario.hour < 14:
        return 'T3'
    else:
        return 'T4'

#Formatacao do horario
def converterHorario(horario):
    return horario.strftime('%H:%M') + 'H'

#Geracao das etiquetas
def gerarPDF(dataframe, nomeArquivo):

    #Dimensoes da pagina
    largura_pagina, altura_pagina = 100*mm, 35*mm

    c = canvas.Canvas(nomeArquivo, pagesize=(largura_pagina, altura_pagina))

    #tamanho das fontes
    tamanhosFonte = {
        'nome': 5.5*mm,
        'identificacoes': 4.2*mm,
        'turno': 4*mm,
        'horario': 3.5*mm 
    }
    
    #Margem horizontal
    margemX = 3*mm

    #Impressao dos dados
    for _, row in dataframe.iterrows():
        
        c.setLineWidth(2)

        c.setFont("Helvetica-Bold",tamanhosFonte['nome'])
        c.drawString(margemX, altura_pagina - 7*mm, str(row['nome']))
        
        c.setFont("Helvetica",tamanhosFonte['identificacoes'])
        c.drawString(margemX, altura_pagina - 13*mm, f'Atendimento: {row['atendimento']}')

        c.setFont("Helvetica",tamanhosFonte['identificacoes'])
        c.drawString(margemX, altura_pagina - 19*mm, f'Nascimento: {row['dataNascimento']}')

        c.setFont("Helvetica",tamanhosFonte['identificacoes'])
        c.drawString(margemX, altura_pagina - 25*mm, f'Sexo: {row['sexo']}')

        c.setFont("Helvetica",tamanhosFonte['identificacoes'])
        c.drawString(margemX, altura_pagina - 31*mm, f'Mãe: {row['maePaciente']}')

        if row['classe'] == 'psicotropico':
            c.saveState()

            c.setFont("Helvetica-Bold", 3*mm)
            c.rotate(90)
            c.drawString(12*mm, -74.5*mm,'psico')

            c.restoreState()

            c.roundRect(76*mm, 5*mm, 18*mm, 20*mm, 5*mm, stroke=1, fill=0)
            c.setLineWidth(1)
        elif row['classe'] == 'normal':
            c.circle(85*mm, altura_pagina - (20*mm), 10*mm, stroke=1, fill=0)
            c.setLineWidth(1)
            
        c.setFont("Helvetica-Bold",tamanhosFonte['turno'])
        c.drawString(83*mm, altura_pagina - (18*mm), str(row['turno']))

        c.line(78*mm, 15*mm, 92*mm, 15*mm)

        c.setFont("Helvetica-Bold",tamanhosFonte['horario'])
        c.drawString(79*mm, altura_pagina - (25*mm), str(row['horario']))
      
        c.showPage()

    c.save()

st.title('Gerador de etiquetas')

horarioInicial = st.time_input('Horario Inicial', value=pd.to_datetime('00:00:00').time())
horarioFinal = st.time_input('Horario Final', value=pd.to_datetime('23:59:59').time())
inputExcluirMedicamentos = st.text_input("Medicamentos a desconsiderar (separados por vírgulas)", "")

dfFormatado = dfProntuarios.copy()

if st.button("Executar"):
    excluirMedicamentos = [med.strip() for med in inputExcluirMedicamentos.split(',')]

    dfFiltrado = aplicarFiltros(dfProntuarios, horarioInicial, horarioFinal, excluirMedicamentos)

    #Adciona informacoes que serao impressas com visuais mais agradaveis
    dfFormatado = dfFiltrado.copy()
    dfFormatado['turno'] = dfFormatado['horario'].apply(determinarTurno)
    dfFormatado.loc[:, 'sexo'] = dfFormatado['sexo'].replace({'F': 'Feminino', 'M': 'Masculino'})
    dfFormatado.loc[:, 'horario'] = dfFormatado['horario'].apply(converterHorario)

    caminhoPDF = os.path.join(diretorioScript, 'etiquetas.pdf')
    gerarPDF(dfFormatado, caminhoPDF)

    st.success('Etiquetas geradas com sucesso!')
    st.write("As etiquetas foram geradas e salvas no arquivo 'etiquetas.pdf'.")

    webbrowser.open_new_tab(caminhoPDF)