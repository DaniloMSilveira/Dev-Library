# Terraform / Ansible - Guia Geral

## 🎯 Conceitos Principais

### Terraform
**Ferramenta de provisionamento de infraestrutura (IaC declarativa)**
- Garante que os recursos (VMs, redes, load balancers) existam com o estado desejado
- Mantém um `state` para rastrear recursos gerenciados
- Aplica mudanças comparando desired state com current state (`plan`/`apply`)

### Ansible
**Ferramenta de automação de configuração e orquestração**
- Ideal para configurar software, copiar arquivos e aplicar mudanças contínuas
- Sem necessidade de recriação de infraestrutura
- Modelo agentless (comunica via SSH)

### 🤝 Integração

**Regra prática**: usar **Terraform para criar recursos infra** (instâncias, VPCs, security groups) e **Ansible para provisionar/configurar serviços** dentro dessas instâncias.

---

## 📁 Principais Arquivos

### Terraform

| Arquivo | Descrição |
|---------|-----------|
| **`terraform.tf`** | Bloco `terraform` com configurações dos provedores cloud e suas versões |
| **`main.tf`** | Definição do provedor, variáveis e recursos a serem criados |
| **`variables.tf`** | Declaração de variáveis esperadas |
| **`outputs.tf`** | Valores que o Terraform retorna após aplicação (opcional) |

### 🔎 Componentes Básicos do Terraform

#### ✅ Resource
Um `resource` descreve um recurso que o Terraform irá criar/gerenciar.

```hcl
resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "example-vpc" }
}
```

#### ✅ Module
Um `module` organiza infraestrutura em blocos reutilizáveis (pode ser local ou remoto).

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name   = "app-vpc"
  cidr   = "10.0.0.0/16"
}
```

#### ✅ Variable
`variable` define um parâmetro configurável para um módulo.

```hcl
variable "environment" {
  type        = string
  description = "Nome do ambiente (dev / prod)"
}
```

Use em outro arquivo:

```hcl
environment = "prod"
```

#### ✅ Output
`output` expõe valores após o `terraform apply`, útil para ver informações ou passar para outros módulos.

```hcl
output "vpc_id" {
  value = module.vpc.vpc_id
}
```

### Ansible

| Arquivo | Descrição |
|---------|-----------|
| **`inventory.yml`** | Define hosts/servidores (estático ou dinâmico). Pode ser `hosts.yml`, `inventory.ini`, etc |
| **`playbook.yml`** | Define as tarefas a executar nos hosts (instalação, configuração, deployment) |
| **`roles/`** | Estrutura reutilizável de tasks, handlers e templates (optional para projetos maiores) |

---

## 📚 Comandos Terraform

```bash
# Inicialização
terraform init              # Inicializa workspace, baixa providers

# Validação
terraform fmt              # Formata arquivos .tf seguindo convenções
terraform validate         # Valida sintaxe e consistência

# Planejamento e Aplicação
terraform plan             # Mostra mudanças que serão aplicadas (dry-run)
terraform apply            # Aplica as configurações (cria/atualiza recursos)

# Inspeção e Limpeza
terraform state list       # Lista recursos gerenciados
terraform state show <resource>  # Detalhes de um recurso específico
terraform show             # Exibe todos os recursos aplicados
terraform destroy          # Destrói todos os recursos gerenciados
```

---

## 🔧 Comandos Ansible

```bash
# Validação de conectividade
ansible -i <inventory> all -m ping     # Verifica SSH nos hosts do inventário
ansible -i <inventory> all -a "uptime" # Executa comando ad-hoc

# Execução de Playbooks
ansible-playbook -i <inventory> <playbook.yml>                    # Executa playbook padrão
ansible-playbook -i <inventory> <playbook.yml> -u ubuntu          # Com usuário específico
ansible-playbook -i <inventory> <playbook.yml> --private-key ~/key.pem  # Com chave privada
```

---

## 🔄 Workflow Típico

```
1. Definir infraestrutura em Terraform
         ↓
2. terraform init && terraform plan && terraform apply
         ↓
3. Obter dados dos recursos criados (IPs, DNS, etc)
         ↓
4. Atualizar inventário Ansible com hosts criados
         ↓
5. Validar conectividade: ansible -i inventory all -m ping
         ↓
6. Executar provisioning: ansible-playbook -i inventory playbook.yml
         ↓
7. Validar aplicação em execução
```

---

## 💡 Dicas Rápidas

- **Terraform State**: arquivo `.tfstate` contém estado atual — nunca commite no Git (ignore com `.gitignore`)
- **Providers**: sempre especifique versões (`~> 5.0`) para evitar breaking changes
- **SSH Keys**: certifique-se de que as chaves privadas estão acessíveis e com permissões corretas (`chmod 600`)
- **Idempotência**: Ansible é idempotente — execute um playbook múltiplas vezes com segurança