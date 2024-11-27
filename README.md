# MedBox - Sistema de Gerenciamento de Medicamentos

O MedBox é um sistema web para gerenciamento de medicamentos, controle de estoque e monitoramento de adesão ao tratamento.

## Funcionalidades

- Cadastro de medicamentos
- Configuração de alarmes
- Controle de estoque
- Monitoramento de adesão ao tratamento
- Alertas de estoque baixo
- Notificações de horários de medicação

## Requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone este repositório ou baixe os arquivos
2. Navegue até a pasta do projeto
3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Executando o Sistema

Para iniciar o servidor:

```bash
python app.py
```

O sistema estará disponível em `http://localhost:5000`

## Estrutura do Projeto

```
MedBox/
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências do projeto
└── templates/         # Templates HTML
    ├── base.html
    ├── index.html
    ├── novo_medicamento.html
    ├── novo_alarme.html
    ├── estoque.html
    └── adesao.html
```

## Uso

1. Acesse o sistema através do navegador
2. Cadastre seus medicamentos em "Novo Medicamento"
3. Configure alarmes para os medicamentos em "Novo Alarme"
4. Monitore o estoque na seção "Estoque"
5. Acompanhe a adesão ao tratamento em "Adesão"

## Próximas Implementações

- [ ] Sistema de autenticação de usuários
- [ ] API para notificações push
- [ ] Relatórios de adesão ao tratamento
- [ ] Integração com dispositivos IoT
- [ ] Backup automático dos dados
