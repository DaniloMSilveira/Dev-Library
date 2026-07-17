# AWS ECS — Exemplo com Terraform

Este exemplo mostra como criar a infraestrutura base para uma aplicação em AWS usando Terraform. O foco está em:

- Provisionar uma **VPC** com subnets públicas/privadas (módulo `terraform-aws-modules/vpc/aws`)
- Criar um **repositório ECR** para armazenar imagens Docker
- Definir **security groups** para comunicação entre ALB/serviço
- Usar **backend remoto (S3)** para armazenar o estado do Terraform

> **Nota**: este exemplo cria recursos ECS (cluster, task, service) usando Fargate.

---

## 📁 Estrutura do Projeto

```
examples/aws-ecs/
├── infra/            # Infraestrutura compartilhada (módulo local)
│   ├── provider.tf   # Provider AWS e versão do Terraform
│   ├── vpc.tf        # Módulo VPC (terraform-aws-modules/vpc/aws)
│   ├── ecr.tf        # Repositório ECR
│   ├── iam.tf        # IAM roles/policies para ECS e ECR
│   ├── ecs.tf        # Cluster ECS + Task + Service (Fargate)
│   ├── alb.tf        # Load Balancer + Target Group
│   ├── security-group.tf  # SGs para ALB + ECS
│   └── variables.tf  # Variáveis esperadas pelo módulo
│
└── env/
    ├── dev/         # Ambiente de desenvolvimento
    │   ├── backend.tf  # Backend S3 (key: dev/terraform.tfstate)
    │   └── main.tf     # Chamada do módulo local (infra/)
    └── prod/        # Ambiente de produção
        ├── backend.tf  # Backend S3 (key: prod/terraform.tfstate)
        └── main.tf     # Chamada do módulo local (infra/)
```

---

## ⚙️ Pré-requisitos

- [Terraform](https://www.terraform.io/downloads) (versão >= 0.14)
- Conta AWS com credenciais configuradas (via `aws configure` ou variáveis de ambiente)
- Permissões para criar: VPC, subnets, ECR, ECS, ECR, IAM, Security Groups, S3 (para state)

---

## ▶️ Como Usar

1. **Acesse o ambiente**:

```bash
cd examples/aws-ecs/env/dev
```

2. **Inicialize o Terraform**:

```bash
terraform init
```

3. **Planeje a aplicação**:

```bash
terraform plan
```

4. **Aplique**:

```bash
terraform apply
```

5. **Ver outputs** (quando disponíveis):

```bash
terraform output
```

6. **Limpeza**:

```bash
terraform destroy
```

---

## 🧠 Análise dos arquivos (exemplo completo)

### ✅ `infra/provider.tf`
Define **provider AWS** (`us-west-2`) e versão mínima do Terraform.

### ✅ `infra/vpc.tf`
Usa o módulo oficial `terraform-aws-modules/vpc/aws` para criar:
- VPC com CIDR `10.0.0.0/16`
- 3 subnets públicas + 3 subnets privadas
- NAT Gateway para acesso a internet a partir das subnets privadas

### ✅ `infra/ecr.tf`
Define um repositório ECR (`aws_ecr_repository`) para hospedar imagens Docker.

### ✅ `infra/iam.tf`
Cria um role + policy para o ECS/Fargate poder:
- Buscar imagens no ECR
- Enviar logs ao CloudWatch

### ✅ `infra/ecs.tf`
Cria:
- Cluster ECS (módulo `terraform-aws-modules/ecs/aws`)
- Task Definition (Fargate) com container rodando imagem `
  <repository_url>/<environment>:v1`
- Service (Fargate) com **desired_count = 3**
- Conexão do service com o ALB (target group `aws_lb_target_group.target`)

### ✅ `infra/alb.tf`
Cria:
- Application Load Balancer (ALB) em subnets públicas
- Target Group (`ip` type) com porta 8000
- Listener HTTP na porta 8000
- Output `IP` com o DNS do ALB

### ✅ `infra/security-group.tf`
Cria dois Security Groups:
- `alb_security_group`: permite acesso HTTP (porta 8000) de qualquer lugar
- `private_security_group`: permite tráfego interno do ALB para o ECS

### ✅ `env/prod/backend.tf`
Configura backend S3 (`terraform-state` bucket) com chave `prod/terraform.tfstate`.

### ✅ `env/prod/main.tf`
Chama o módulo local `infra/` e expõe um output:
- `output "IP_alb"` (usa `module.prod.IP`, que referencia o DNS do ALB)

### ✅ `env/dev/main.tf`
Chama o mesmo módulo local (`infra/`) com valores de `dev`:
- Menor `ecs_container_count` (1) para custo reduzido
- `ecs_container_cpu`/`ecs_container_memory` definidos para instância mais leve
