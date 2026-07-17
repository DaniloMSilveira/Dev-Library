# Estudos - Terraform

Este repositório é um guia de estudos para aprender infraestrutura como código (IaC) utilizando as principais tecnologias da stack do Terraform. Inclui documentações teóricas e exemplos práticos para facilitar o aprendizado.

## 📋 Índice

- [Estrutura do Projeto](#-estrutura-do-projeto-📁)
- [Pré-requisitos](#-pré-requisitos-⚙️)
- [Como Usar](#-como-usar-▶️)
- [Navegabilidade](#-navegabilidade)

## 🧭 Navegabilidade

- **Documentações**: acesse `docs/` ou clique nos arquivos listados abaixo.
- **Exemplos**: navegue até `examples/` e escolha a pasta desejada (por exemplo `aws-ec2`).
- Use o comando `ls` no terminal para visualizar o conteúdo de qualquer diretório.


## 📁 Estrutura do Projeto 

- **`docs/`**: Documentações em Markdown sobre comandos principais do Terraform, integração com Ansible e exemplos práticos.
  - [terraform-ansible.md](docs/terraform-ansible.md)
  - [aws-ec2.md](docs/aws-ec2.md)
- **`examples/`**: Exemplos práticos de configurações Terraform.
  - [aws-ec2/](examples/aws-ec2)


## ⚙️ Pré-requisitos 

- [Terraform](https://www.terraform.io/downloads) (versão >= 1.2)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- Conta no provedor da Cloud com credenciais configuradas (via CLI ou variáveis de ambiente)

## ▶️ Como Usar 

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/terraform.git
   cd terraform
   ```

2. **Navegue para um exemplo** (ex.: AWS EC2):
   ```bash
   cd examples/aws-ec2
   ```

3. **Configure variáveis** (se necessário, crie arquivos `.tfvars` para ambientes dev/prod).

4. **Execute os comandos Terraform**:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

5. **Limpeza**: Remova recursos com `terraform destroy`.
