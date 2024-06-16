# Gerador de Etiquetas Inteligentes para Hospitais

## Descrição

Este script em Python foi desenvolvido para substituir o modelo atual de geração de etiquetas em hospitais, que usa um número fixo de etiquetas (por exemplo, 10, 12, 14... etiquetas por paciente). Esse método pode resultar em desperdício de material se o paciente precisar de pouca medicação ou, ao contrário, pode exigir a impressão de mais etiquetas. Minha ferramenta analisa os prontuários e gera etiquetas personalizadas, considerando horários, turnos e classes de medicamentos, otimizando a quantidade de etiquetas impressas de acordo com a necessidade de cada paciente.

![Apresentação](imagens/apresentação.png)

# Funcionalidades 

- **Análise de Prontuários:** Lê os prontuários dos pacientes para determinar a quantidade essencial de etiquetas.

- **Classificação:** Organiza as etiquetas de acordo com os horários, tipos de medicamentos (normais ou psicotropicos) e turnos.

- **Personalização:** Permite que o usuário determine intervalos de tempo à considerar na análise e, se necessario, desconsidere medicamentos especificos

<!--GIF Coleta-->

## Requisitos

- Python 3.12.3
- Bibliotecas: pandas, numpy, reportlab, webbrowser, streamlit.
<!-- 
## Instalação


# Usando a Ferramenta

# Contribuição

-->
# Licença

Este arquivo está licenciado sob a CC BY-NC-SA 4.0. Veja o arquivo [LINCENSEmd](LICENSE.md) para mais detalhes.