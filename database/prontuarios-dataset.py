import pandas as pd
import numpy as np
import random as rd
from datetime import time
import os

diretorioScript = os.path.dirname(__file__)

#Base de dados disponivel em: https://www.kaggle.com/datasets/cankatsrc/medical-records-dataset
caminhoMedicalRecords = os.path.join(diretorioScript, '../database/medical-records.csv')
dfPacientes = pd.read_csv(caminhoMedicalRecords)

#Base de dados disponivel em: https://www.kaggle.com/datasets/rupindersinghrana/gender-by-name
caminhoNameDataset = os.path.join(diretorioScript, '../database/name_gender_dataset.csv')
dfMaePaciente = pd.read_csv(caminhoNameDataset, usecols=['Name', 'Gender']).iloc[:1000]
dfMaePaciente = dfMaePaciente[dfMaePaciente['Gender'] == 'F'][['Name']].reset_index(drop=True)

#Intervalo de Pacientes
dfPacientes = dfPacientes.iloc[:500]

#Elimina colunas desnecessarias e as reordena
dfPacientes.drop(['patient_id', 'medical_conditions', 'medications', 'allergies', 'last_appointment_date'], axis=1, inplace=True)
dfPacientes.rename(columns={'name':'nome', 'date_of_birth':'dataNascimento', 'gender':'sexo'}, inplace=True)

dfPacientes = dfPacientes[['nome', 'sexo', 'dataNascimento']]

#Lista com letras de A a Z
letrasAZ = [chr(i) for i in range(65, 91)]

listaMedicamentos= []
listaClassificacao = []

#Definicao de medicação e sua classificacao
for letra in letrasAZ:
    probabilidadeNormal = 0.7
    if rd.random() < probabilidadeNormal:
        classe = 'normal'
    else:
        classe = 'psicotropico'

    listaMedicamentos.append(f'Medicamento{letra}')
    listaClassificacao.append(classe)

#Cria DF com nome e classe das medicacoes
dfMedicamentos = pd.DataFrame({'medicacao':listaMedicamentos, 'classe': listaClassificacao}).reset_index(drop=True)

#Gera um numero aleatorio de medicacao para cada paciente
lista = np.random.randint(1,10, size=len(dfPacientes))

#Expansao da DF para garantir que cada medicacao tenha uma linha propria
dfExpandidoPaciente = dfPacientes.loc[dfPacientes.index.repeat(lista)].reset_index(drop=True)

#Gera um medicamento aleatorio para cada linha da DF expandida e atribui a classificacao correspondente
dfExpandidoPaciente['medicacao'] = np.random.choice(listaMedicamentos, size=len(dfExpandidoPaciente))
dfPacientesMedicamentos = dfExpandidoPaciente.merge(dfMedicamentos, how = 'left', on = 'medicacao')

# Converte e formata datas para o formato DD-MM-AAAA
def converterData(df):
    df['dataNascimento'] = pd.to_datetime(df['dataNascimento'])
    
    df['dataNascimento'] = df['dataNascimento'].dt.strftime('%d-%m-%Y')
    return df

# Chama funcao para converter datas
dfPacientesMedicamentos = converterData(dfPacientesMedicamentos)

#Gera um horario aleatorio para cada linha da DF
dfPacientesMedicamentos['horario'] = [time(hour=h) for h in np.random.choice(range(0,24,2), len(dfPacientesMedicamentos))]

#Simula um numero de atendimento para cada paciente
nomesPacientes = dfPacientesMedicamentos['nome'].unique()
numeroAtendimento = {nome: np.random.randint(10000000, 99999999) for nome in nomesPacientes}
dfPacientesMedicamentos['atendimento'] = dfPacientesMedicamentos['nome'].map(numeroAtendimento)

#Simula o nome das maes de cada paciente
nomeMaes = dfMaePaciente['Name'].to_list()
maePaciente = {nome: np.random.choice(nomeMaes) + ' ' + np.random.choice(nomeMaes) for nome in nomesPacientes}
dfPacientesMedicamentos['maePaciente'] = dfPacientesMedicamentos['nome'].map(maePaciente)

#Simula a enfermaria onde o paciente esta
enfermarias = ['UTI A', 'UTI B', 'UTI C', 'Internação 1', 'Internação 2', 'Internação 3', 'Internação 4']
enfermariaPaciente = {nome: np.random.choice(enfermarias) for nome in nomesPacientes}
dfPacientesMedicamentos['enfermaria'] = dfPacientesMedicamentos['nome'].map(enfermariaPaciente)

caminhoParquet = os.path.join(diretorioScript, 'banco-de-dados.parquet')
dfPacientesMedicamentos.to_parquet(caminhoParquet)