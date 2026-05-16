variable "cloud_id" {
  type        = string
  description = "ID облака Yandex Cloud. Узнать: yc config get cloud-id"
}

variable "folder_id" {
  type        = string
  description = "ID каталога, в котором создаются ресурсы. Узнать: yc config get folder-id"
}

variable "sa_key_file" {
  type        = string
  description = "Путь к JSON-ключу service account'а terraform-sa"
  default     = "~/.config/yandex-cloud/terraform-key.json"
}

variable "ssh_public_key_file" {
  type        = string
  description = "Путь к публичному SSH-ключу для входа на ВМ"
  default     = "~/.ssh/id_rsa.pub"
}
