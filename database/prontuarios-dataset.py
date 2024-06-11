import pandas as pd
import numpy as np
import random as rd
from datetime import time

dfPacientes = pd.read_csv("medical-records.csv")

dfPacientes = dfPacientes.iloc[:500]

dfPacientes.drop(['patient_id', 'medical_conditions', 'medications', 'allergies'], axis=1, inplace=True)
dfPacientes.rename(columns={'name':'nome', 'date_of_birth':'dataNascimento', 'gender':'sexo', 'last_appointment_date': 'ultimaConsulta'}, inplace=True)

dfPacientes['sexo'].replace({'F': 'Feminino', 'M': 'Masculino'}, inplace=True)

dfPacientes = dfPacientes[['nome', 'sexo', 'dataNascimento', 'ultimaConsulta']]

letrasAZ = [chr(i) for i in range(65, 91)]
listaMedicamentos= []
listaClassificacao = []

for letra in letrasAZ:
    probabilidadeNormal = 0.7
    if rd.random() < probabilidadeNormal:
        classe = 'normal'
    else:
        classe = 'psicotropico'

    listaMedicamentos.append(f'Medicamento{letra}')
    listaClassificacao.append(classe)


dfMedicamentos = pd.DataFrame({'medicacao':listaMedicamentos, 'classe': listaClassificacao}).reset_index(drop=True)

lista = np.random.randint(1,10, size=len(dfPacientes))
dfExpandidoPaciente = dfPacientes.loc[dfPacientes.index.repeat(lista)].reset_index(drop=True)

dfExpandidoPaciente['medicacao'] = np.random.choice(listaMedicamentos, size=len(dfExpandidoPaciente))

dfPacientesMedicamentos = dfExpandidoPaciente.merge(dfMedicamentos, how = 'left', on = 'medicacao')

dfPacientesMedicamentos['horario'] = [time(hour=h) for h in np.random.choice(range(0,24,2), len(dfPacientesMedicamentos))]

nomesPacientes = dfPacientesMedicamentos['nome'].unique()
numeroAtendimento = {nome: np.random.randint(10000000, 99999999) for nome in nomesPacientes}

dfPacientesMedicamentos['atendimento'] = dfPacientesMedicamentos['nome'].map(numeroAtendimento)

dfPacientesMedicamentos.to_parquet('banco-de-dados.parquet')