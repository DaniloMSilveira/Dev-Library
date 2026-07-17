# AWS EC2 — Infraestrutura Modular com Terraform + Ansible

Este documento descreve o projeto prático disponível em `examples/aws-ec2/`, que demonstra uma infraestrutura modular e escalável na AWS com Terraform, incluindo ambientes separados (dev/prod) e integração com Ansible.

## 📂 Estrutura do Projeto

```
examples/aws-ec2/
├── infra/                    # Módulo Terraform reutilizável (infraestrutura base)
│   ├── terraform.tf          # Configuração do provider AWS e versões
│   ├── main.tf               # Definição dos recursos (EC2, ASG, LB, etc)
│   ├── security-group.tf     # Rules de inbound/outbound
│   ├── variables.tf          # Variáveis esperadas pelo módulo
│   └── .terraform.lock.hcl   # Lock file de provadores (versioni-ado)
│
├── env/
│   ├── dev/                  # Ambiente de DESENVOLVIMENTO
│   │   ├── main.tf           # Chamada do módulo infra/ com valores dev
│   │   ├── playbook.yml      # Playbook Ansible para dev
│   │   └── hosts.yml         # Inventário Ansible (preenchido com IP público)
│   │
│   └── prod/                 # Ambiente de PRODUÇÃO
│       ├── main.tf           # Chamada do módulo infra/ com valores prod
│       ├── playbook.yml      # Playbook Ansible para prod
│       ├── ansible.sh        # Script de inicialização (user_data)
│       └── hosts.yml         # Inventário Ansible (preenchido com IP público)
│
└── infra/
    └── hosts.yml             # Inventário Ansible (referência compartilhada)
```

## 🏗️ Recursos Terraform Implementados

### Módulo `infra/`

O módulo define a infraestrutura reutilizável:

**1. Launch Template**
```terraform
aws_launch_template
```
- Define a imagem AMI, tipo de instância, chaves SSH, tags e user_data.

**2. Autoscaling Group (ASG)**
```terraform
aws_autoscaling_group
aws_autoscaling_schedule  # Scale up/down em horários específicos
```
- Escalona automaticamente as instâncias com base em políticas.
- Schedules de scale-up (seg-fri 10h) e scale-down (seg-fri 21h).
- Zonas de disponibilidade em duas regiões.

**3. Security Group**
```terraform
aws_security_group
```
- Regras de inbound/outbound (acesso total por padrão — `0.0.0.0/0`).
- Aplicável a instâncias criadas pelo ASG.

**4. Load Balancer (apenas em PROD)**
```terraform
aws_lb
aws_lb_target_group
aws_lb_listener
aws_autoscaling_policy     # Target tracking para CPU
```
- Application Load Balancer que distribui tráfego entre as instâncias do ASG.
- Listener na porta 8000.
- Política de autoscaling (target: 50% CPU).

**5. VPC e Subnets (padrão)**
```terraform
aws_default_vpc
aws_default_subnet
```
- Usa VPC padrão da AWS com subnets em múltiplas zonas de disponibilidade.

### Variáveis do Módulo

O módulo espera as seguintes variáveis (definidas em `infra/variables.tf`):

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `environment` | string | Nome do ambiente (DEV, PROD) |
| `aws_region` | string | Região AWS (ex: us-west-2) |
| `instance_type` | string | Tipo de instância (t2.micro, t2.small, etc) |
| `ssh_key` | string | Nome da chave SSH (sem extensão .pem) |
| `security_group` | string | Nome do security group |
| `asg_name` | string | Nome do autoscaling group |
| `asg_min_size` | number | Mínimo de instâncias |
| `asg_max_size` | number | Máximo de instâncias |
| `is_production` | bool | Flag para habilitar recursos de produção (LB, ASG policy) |

## 🌍 Ambientes (dev e prod)

Cada ambiente reutiliza o mesmo módulo `infra/` mas com configurações diferentes:

### DEV (`env/dev/main.tf`)

```terraform
module "aws-dev" {
  source       = "../../infra"
  environment  = "DEV"
  aws_region   = "us-west-2"
  instance_type = "t2.micro"
  ssh_key      = "iac-dev"
  security_group = "full-access-dev"
  asg_name     = "asg-dev"
  asg_min_size = 0
  asg_max_size = 1
  is_production = false
}
```

**Características:**
- 1 instância no máximo (cost-effective para testes).
- **Sem** Load Balancer.
- Schedules de autoscaling (desliga à noite, liga de manhã).

### PROD (`env/prod/main.tf`)

```terraform
module "aws-prod" {
  source       = "../../infra"
  environment  = "PROD"
  aws_region   = "us-west-2"
  instance_type = "t2.micro"
  ssh_key      = "iac-prod"
  security_group = "full-access-prod"
  asg_name     = "asg-prod"
  asg_min_size = 1
  asg_max_size = 5
  is_production = true
}
```

**Características:**
- Mínimo 1 instância, máximo 5.
- **Com** Application Load Balancer (porta 8000).
- Autoscaling baseado em CPU (target 50%).
- Sempre ligado (sem schedules de desligamento).

## 🚀 Workflow Completo

### 1. Preparar as Chaves SSH

Certifique-se de que você tem as chaves SSH criadas em sua máquina local e registradas na AWS:

```bash
# Exemplo: criar uma chave para dev
aws ec2 create-key-pair --key-name iac-dev --query 'KeyMaterial' --output text > ~/.ssh/iac-dev.pem
chmod 600 ~/.ssh/iac-dev.pem
```

> **Nota**: As chaves públicas (`.pub`) já estão no repositório apenas como referência. As chaves privadas devem ser geradas localmente.

### 2. Inicializar Terraform

```bash
cd examples/aws-ec2/infra
terraform init
terraform fmt      # Formata o código
terraform validate # Valida a sintaxe
```

### 3. Planejar e Aplicar (DEV)

```bash
cd ../env/dev
terraform init
terraform plan
terraform apply
```

**Saída**: Instância(s) EC2 criada(s) com Load Balancer (se prod).

### 4. Obter IP Público

```bash
terraform output      # Visualiza outputs (se definidos)
# ou
terraform show | grep public_ip
```

### 5. Atualizar Inventário Ansible

```bash
# Editar infra/hosts.yml (ou env/dev/hosts.yml)
[terraform-ansible]
<IP_PÚBLICO_DA_INSTÂNCIA>
```

### 6. Testar Conectividade SSH e Executar Ansible

```bash
# De dentro de env/dev/ ou env/prod/
ssh -i ~/.ssh/iac-dev.pem ubuntu@<IP>

# Teste de ping com Ansible
ansible -i hosts.yml all -m ping

# Aplicar playbook
ansible-playbook -i hosts.yml playbook.yml -u ubuntu --private-key ~/.ssh/iac-dev.pem
```

### 7. Visualizar Recursos (opcional)

```bash
terraform state list     # Lista recursos gerenciados
terraform show           # Detalhes de todos os recursos
terraform state show 'aws_autoscaling_group.app_server_asg'  # Recurso específico
```

### 8. Destruir Infraestrutura (quando terminar)

```bash
cd examples/aws-ec2/env/dev  # ou /prod
terraform destroy
```

## 📝 Exemplos de Playbooks Ansible

### dev/playbook.yml

```yaml
- hosts: terraform-ansible
  become: yes
  tasks:
    - name: criar arquivo index
      copy:
        dest: /home/ubuntu/index.html
        content: "<h1>Terraform - DEV Ansible</h1>"

    - name: iniciar servidor web com busybox
      shell: nohup busybox httpd -f -p 8000 &
```

### prod/playbook.yml

Semelhante ao DEV, mas pode incluir tarefas adicionais como:
- Instalação de Docker, SSL, monitoramento, etc.

> **Nota**: O arquivo `prod/ansible.sh` é referenciado como `user_data` pelo Terraform; é executado automaticamente quando a instância é inicializada.

## 🔧 Dicas e Boas Práticas

1. **State Management**:
   - Arquivos `*.tfstate` são ignorados pelo `.gitignore` (contêm dados sensíveis).
   - Para equipes, considere usar remote state (S3 + DynamoDB).

2. **Chaves SSH**:
   - Nunca commite chaves privadas. Use local E ignore no `.gitignore`.
   - Público (`.pub`) pode ficar como referência (não crítico).

3. **Recursos de Produção**:
   - Sempre use `terraform plan` antes de `apply` para revisar mudanças.
   - Versione seu `terraform.lock.hcl` para garantir builds consistentes.

4. **Limpeza de Planos**:
   - Se criou `plan.tfplan`, remova-o com `rm plan.tfplan` após aplicar.

5. **Debugging**:
   - Use `terraform console` para testar expressões Terraform.
   - Use `TF_LOG=DEBUG terraform apply` para logs detalhados.


