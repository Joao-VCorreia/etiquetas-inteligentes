import pandas as pd
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime, timedelta, time
import os
import webbrowser

#Coleta de dados
diretorioScript = os.path.dirname(__file__)
caminhoParquet = os.path.join(diretorioScript, '../database/banco-de-dados.parquet')
dfProntuarios = pd.read_parquet(caminhoParquet)

#Ordena os horarios de maneira crescente
dfProntuarios = dfProntuarios.groupby('nome', group_keys=False).apply(lambda x: x.sort_values('horario'))

#Funcao para aplicar filtro de horarios
@st.cache_resource()
def aplicarFiltros(dfIn, horarioInicial, horarioFinal, excluirMedicamentos):
    # Se o horário final é menor que o inicial, significa que passou da meia-noite
    if horarioFinal < horarioInicial:
        # Máscara de horário para considerar a transição de dias
        maskHorario = ((dfIn['horario'] >= horarioInicial) & (dfIn['horario'] <= time(23, 59, 59))) | \
                      ((dfIn['horario'] >= time(0, 0)) & (dfIn['horario'] <= horarioFinal))
    else:
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
    largura_pagina, altura_pagina = 100*mm, 35*mm
    margemX = 3*mm

    c = canvas.Canvas(nomeArquivo, pagesize=(largura_pagina, altura_pagina))

    for _, row in dataframe.iterrows():
        c.setLineWidth(2)
        c.setFont("Helvetica-Bold", 5.5*mm)
        c.drawString(margemX, altura_pagina - 7*mm, str(row['nome']))
        c.setFont("Helvetica", 4*mm)
        c.drawString(margemX, altura_pagina - 12*mm, f"Atendimento: {row['atendimento']}")
        c.drawString(margemX, altura_pagina - 17*mm, f"Enfermaria: {row['enfermaria']}")
        c.drawString(margemX, altura_pagina - 22*mm, f"Nascimento: {row['dataNascimento']}")
        c.drawString(margemX, altura_pagina - 27*mm, f"Sexo: {row['sexo']}")
        c.drawString(margemX, altura_pagina - 32*mm, f"Mãe: {row['maePaciente']}")

        if row['classe'] == 'psicotropico':
            c.saveState()
            c.setFont("Helvetica-Bold", 3*mm)
            c.rotate(90)
            c.drawString(12*mm, -74.5*mm, 'psico')
            c.restoreState()
            c.roundRect(76*mm, 5*mm, 18*mm, 20*mm, 5*mm, stroke=1, fill=0)
        elif row['classe'] == 'normal':
            c.circle(85*mm, altura_pagina - 20*mm, 10*mm, stroke=1, fill=0)

        c.setFont("Helvetica-Bold", 4*mm)
        c.drawString(83*mm, altura_pagina - 18*mm, str(row['turno']))
        c.line(78*mm, 15*mm, 92*mm, 15*mm)
        c.setFont("Helvetica-Bold", 3.5*mm)
        c.drawString(79*mm, altura_pagina - 25*mm, str(row['horario']))
        c.showPage()

    c.save()
    
st.title('Gerador de etiquetas')

#Dicionario com intervalo de Turnos
turnos = {
    'T1 - 20:00 às 01:59': (time(20, 0), time(1, 59, 59)),
    'T2 - 02:00 às 07:59': (time(2, 0), time(7, 59, 59)),
    'T3 - 08:00 às 13:59': (time(8, 0), time(13, 59, 59)),
    'T4 - 14:00 às 19:59': (time(14, 0), time(19, 59, 59))
}

# Preferencia de selecao
opcaoTurno = st.radio("Escolha o turno ou defina um horário específico:", ('Turno', 'Horário Específico'))

# Se o usuário escolher turno, ele pode selecionar um dos turnos pré-definidos
if opcaoTurno == 'Turno':
    turnoSelecionado = st.selectbox("Selecione o turno:", list(turnos.keys()))
    horarioInicial, horarioFinal = turnos[turnoSelecionado]
else:
    # Se o usuário escolher horário específico, ele pode definir os horários inicial e final
    horarioInicial = st.time_input('Horario Inicial', value=pd.to_datetime('00:00:00').time())
    horarioFinal = st.time_input('Horario Final', value=pd.to_datetime('23:59:59').time())

#lista de medicamentos a desconsiderar
inputExcluirMedicamentos = st.text_input("Medicamentos a desconsiderar (separados por vírgulas)", "")

if st.button("Executar"):
    excluirMedicamentos = [med.strip() for med in inputExcluirMedicamentos.split(',')]

    dfFiltrado = aplicarFiltros(dfProntuarios, horarioInicial, horarioFinal, excluirMedicamentos)

    #Adciona informacoes que serao impressas com visuais mais agradaveis
    dfFormatado = dfFiltrado.copy()
    dfFormatado['turno'] = dfFormatado['horario'].apply(determinarTurno)
    dfFormatado.loc[:, 'sexo'] = dfFormatado['sexo'].replace({'F': 'Feminino', 'M': 'Masculino'})
    dfFormatado.loc[:, 'horario'] = dfFormatado['horario'].apply(converterHorario)

    #gerando e salvando etiquetas
    caminhoPDF = os.path.join(diretorioScript, 'etiquetas.pdf')
    gerarPDF(dfFormatado, caminhoPDF)

    st.success('Etiquetas geradas com sucesso!')

    #Abrindo arquivo em uma nova pagina
    webbrowser.open_new_tab(caminhoPDF)
