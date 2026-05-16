output "vm_external_ip" {
  description = "Публичный IP виртуальной машины"
  value       = yandex_compute_instance.vm.network_interface[0].nat_ip_address
}

output "vm_internal_ip" {
  description = "Внутренний IP ВМ в VPC"
  value       = yandex_compute_instance.vm.network_interface[0].ip_address
}

output "ssh_command" {
  description = "Команда для подключения по SSH (копировать и выполнить)"
  value       = "ssh ubuntu@${yandex_compute_instance.vm.network_interface[0].nat_ip_address}"
}

output "registry_id" {
  description = "ID Container Registry — нужен для тегирования и публикации образов"
  value       = yandex_container_registry.main.id
}

output "registry_path" {
  description = "Базовый путь Container Registry для docker push/pull"
  value       = "cr.yandex/${yandex_container_registry.main.id}"
}

output "app_url" {
  description = "URL веб-приложения (после ручного запуска docker-compose на ВМ)"
  value       = "http://${yandex_compute_instance.vm.network_interface[0].nat_ip_address}:8080"
}

output "api_url" {
  description = "URL API"
  value       = "http://${yandex_compute_instance.vm.network_interface[0].nat_ip_address}:8000"
}
