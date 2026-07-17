# AWS EKS — Exemplo com Terraform

Este exemplo demonstra como provisionar um cluster Kubernetes (EKS) na AWS usando Terraform, incluindo:

- Criação de **VPC + subnets públicas/privadas** (módulo `terraform-aws-modules/vpc/aws`)
- Criação de **cluster EKS** com **managed node group**
- Provisionamento de **repositório ECR** para imagens Docker
- Deployment de recursos Kubernetes (`Deployment` + `Service LoadBalancer`) via provider `kubernetes`
- Uso de **backend S3** para armazenar o state (em `env/prod`)

---

## 📁 Estrutura do Projeto

```
examples/aws-eks/
├── infra/                # Infraestrutura compartilhada (módulo local)
│   ├── provider.tf       # Providers (AWS + Kubernetes) + data sources EKS
│   ├── vpc.tf            # VPC + subnets (module terraform-aws-modules/vpc/aws)
│   ├── ecr.tf            # Repositório ECR
│   ├── eks.tf            # Cluster EKS + managed node group
│   ├── kubernetes.tf     # Recursos Kubernetes (Deployment + Service LB)
│   ├── security-group.tf # Security Group para acesso SSH ao cluster
│   └── variables.tf      # Variáveis esperadas pelo módulo
│
└── env/
    └── prod/            # Ambiente de desenvolvimento
        ├── backend.tf    # Backend S3 para armazenar o state
        └── main.tf       # Chamada do módulo infra/ com valores de desenvolvimento
    └── prod/            # Ambiente de produção
        ├── backend.tf    # Backend S3 para armazenar o state
        └── main.tf       # Chamada do módulo infra/ com valores de produção
```

---

## ⚙️ Pré-requisitos

- [Terraform](https://www.terraform.io/downloads) (versão >= 0.14)
- Conta AWS com credenciais configuradas (via `aws configure` ou variáveis de ambiente)
- Permissões para criar: VPC, subnets, EKS, IAM, EC2, ECR, Security Groups, S3 (state)

> 💡 O cluster EKS criado neste exemplo faz uso do provider `kubernetes` para provisionar recursos dentro do cluster. O Terraform irá aguardar até que o cluster esteja pronto antes de aplicar os recursos Kubernetes.

---

## ▶️ Como Usar

### 1) Configurar o ambiente

```bash
cd examples/aws-eks/env/dev
```


### 2) Inicializar o backend e providers

```bash
terraform init
```

### 3) Planejar

```bash
terraform plan
```

### 4) Aplicar

```bash
terraform apply
```

### 5) Verificar outputs

```bash
terraform output
```

### 6) Destruir (limpeza)

```bash
terraform destroy
```

---

## 🧠 Como este exemplo está organizado

### ✅ `infra/provider.tf`

- Configura o provider AWS (`us-west-2`) e a versão mínima do Terraform.
- Usa `data.aws_eks_cluster` + `data.aws_eks_cluster_auth` para conectar o provider `kubernetes` ao cluster criado.

### ✅ `infra/vpc.tf`

- Cria a VPC e subnets (públicas + privadas) usando o módulo oficial `terraform-aws-modules/vpc/aws`.

### ✅ `infra/ecr.tf`

- Cria um repositório ECR (`aws_ecr_repository`) com o nome passado via variável `repository`.

### ✅ `infra/eks.tf`

- Cria o cluster EKS (`terraform-aws-modules/eks/aws`) com a versão `1.21`.
- Habilita **endpoint privado** (`cluster_endpoint_private_access = true`).
- Provisiona um **managed node group** (`eks_managed_node_groups`) com instâncias `t2.micro`.

### ✅ `infra/kubernetes.tf`

- Cria um `kubernetes_deployment` para uma aplicação Django (imagem Docker hardcoded).
- Cria um `kubernetes_service` do tipo `LoadBalancer` para expor a aplicação.
- Expõe o URL do LoadBalancer via output Terraform.

### ✅ `infra/security-group.tf`

- Cria um Security Group `ssh_cluster` para permitir acesso SSH (porta 22) a partir de qualquer lugar.

