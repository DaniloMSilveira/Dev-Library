resource "kubernetes_deployment" "django_api" {
  metadata {
    name = "django-api"
    labels = {
      nome = "django-api"
    }
  }

  spec {
    replicas = var.replicas

    selector {
      match_labels = {
        nome = "django-api"
      }
    }

    template {
      metadata {
        labels = {
          nome = "django-api"
        }
      }

      spec {
        container {
          image = "${var.repository_url}/${var.repository}:${var.k8s_image_tag}"
          name  = "django-api"

          resources {
            limits = {
              cpu    = var.cpu_limit
              memory = var.memory_limit
            }
            requests = {
              cpu    = var.cpu_request
              memory = var.memory_request
            }
          }

          liveness_probe {
            http_get {
              path = "/probe"
              port = 8000
            }

            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "LoadBalancer" {
  metadata {
    name = "load-balancer-django-api"
  }
  spec {
    selector = {
      nome = "django-api"
    }
    port {
      port = 8000
      target_port = 8000
    }
    type = "LoadBalancer"
  }
}

data "kubernetes_service" "dns" {
    metadata {
      name = "load-balancer-django-api"
    }
}

output "URL" {
  value = data.kubernetes_service.dns.status
}